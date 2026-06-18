/**
 * ATLAS · POSEIDON-BUOY reference firmware
 * ----------------------------------------
 * Target:    ESP32 (Arduino core ≥ 2.0.x) — works on any ESP32-DevKit, S2, S3, C3
 * Sensors:   plug your real sensors into `read_sensors()`. The skeleton ships
 *            with placeholder reads so you can flash & verify the full pipeline
 *            without hardware first.
 *
 * Wire protocol (matches /app/backend/routes/robot.py):
 *   uplink   : POST   /api/robot/devices/{id}/telemetry       (every TELEMETRY_INTERVAL_MS)
 *   downlink : GET    /api/robot/devices/{id}/commands/inbox  (every POLL_INTERVAL_MS)
 *              → array of executed commands; this firmware acts on each one
 *
 * Safety contract (architect spec):
 *   - The local SAFE_STATE flag is the device's authority. If `safe_state == true`,
 *     the device refuses every ACTUATE / MOTION / FIRMWARE_UPDATE command on its
 *     own — even if the server sends one through. Belt-and-braces; the server
 *     also blocks at the /command endpoint.
 *   - EMERGENCY_STOP from the server immediately sets safe_state = true and
 *     drops actuators to a known-safe position (defined in `actuate_safe()`).
 *   - CLEAR_SAFE_STATE from the server clears the flag. Owner-only on the
 *     server side; trust the server's role gate.
 *
 * Optional MQTT path:
 *   If `MQTT_HOST` is defined (non-empty), the firmware subscribes to
 *     "<MQTT_TOPIC_PREFIX>/devices/<id>/cmd"
 *   and acts on pushed commands without waiting for the next HTTP poll.
 *   HTTP-poll stays enabled either way as a fallback — matches the server's
 *   "MQTT bridge is dormant, REST surface unchanged" guarantee.
 *
 * mTLS (Phase 8f):
 *   The server's /api/robot/devices endpoint mints a per-device cert pack on
 *   registration. Paste the PEM strings into the constants below (DEVICE_CERT,
 *   DEVICE_KEY, ATLAS_CA) and switch the WiFiClientSecure block on. With
 *   MTLS_ENFORCE=false on the server, including the cert is harmless; with
 *   MTLS_ENFORCE=true the server will require it on telemetry + inbox.
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// === User configuration ===================================================
static const char* WIFI_SSID     = "YOUR-SSID";
static const char* WIFI_PASSWORD = "YOUR-PASSWORD";

// Copy these from /app/backend/.env (or wherever Atlas is deployed) and the
// device registration response (POST /api/robot/devices). DEVICE_ID is the
// `id` field returned by the server — NOT the friendly name.
static const char* ATLAS_BASE_URL = "https://atlas.local"; // e.g. https://192.168.1.42:8001
static const char* DEVICE_ID      = "REPLACE-WITH-DEVICE-ID";
static const char* DEVICE_NAME    = "POSEIDON-BUOY";

// === Optional MQTT (Phase 8c) =============================================
// Leave MQTT_HOST = "" to stay on the HTTP-poll fallback.
static const char* MQTT_HOST          = "";
static const uint16_t MQTT_PORT       = 1883;
static const char* MQTT_TOPIC_PREFIX  = "atlas";
static const char* MQTT_USERNAME      = "";
static const char* MQTT_PASSWORD      = "";

// === Timings ==============================================================
static const uint32_t TELEMETRY_INTERVAL_MS = 5000;   // every 5s
static const uint32_t POLL_INTERVAL_MS      = 3000;   // every 3s
static const uint32_t HTTP_TIMEOUT_MS       = 4000;

// === Device state =========================================================
struct AtlasState {
  bool safe_state = false;
  uint32_t last_telemetry_ms = 0;
  uint32_t last_poll_ms      = 0;
  String last_command_id;
  String last_command_kind;
} S;

// === mTLS (paste your /devices registration response here) ================
// With these set, swap WiFiClient → WiFiClientSecure below.
static const char* DEVICE_CERT = nullptr;   // -----BEGIN CERTIFICATE-----\n...
static const char* DEVICE_KEY  = nullptr;   // -----BEGIN PRIVATE KEY-----\n...
static const char* ATLAS_CA    = nullptr;   // -----BEGIN CERTIFICATE-----\n...

// ==========================================================================
// Sensor plumbing — replace with your real reads
// ==========================================================================
static void read_sensors(JsonDocument& doc) {
  // POSEIDON-BUOY example: water temperature, pH, turbidity
  doc["water_temperature"] = 17.0 + (millis() % 1000) / 1000.0;
  doc["ph"]                = 8.0  + ((millis() / 7) % 100) / 200.0;
  doc["turbidity"]         = 3.0  + ((millis() / 11) % 100) / 50.0;

  // AETHER-STATION example (uncomment for air-quality build):
  // doc["co2"]         = read_scd40_co2();
  // doc["pm2_5"]       = read_sps30_pm25();
  // doc["temperature"] = read_bme280_temp();

  // SOIL-WATCH example:
  // doc["soil_moisture"]    = analogRead(34);
  // doc["soil_temperature"] = read_ds18b20();
  // doc["nutrient_level"]   = read_ec_probe();
}

// Drive your actuators here. Called on ACTUATE commands when safe_state==false.
static void actuate(const JsonObject& payload) {
  Serial.printf("[atlas] actuate: target=%s value=%s\n",
                payload["target"].as<const char*>(),
                payload["value"].as<const char*>());
  // e.g. digitalWrite(VALVE_PIN, payload["value"].as<int>());
}

// Move every actuator to its known-safe position. Called on EMERGENCY_STOP.
static void actuate_safe() {
  Serial.println("[atlas] !! actuators -> safe position");
  // e.g. digitalWrite(VALVE_PIN, LOW);
  //      digitalWrite(PUMP_PIN, LOW);
}

// ==========================================================================
// Wi-Fi
// ==========================================================================
static void wifi_connect() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[wifi] connecting");
  uint32_t deadline = millis() + 20000;
  while (WiFi.status() != WL_CONNECTED && millis() < deadline) {
    delay(250); Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[wifi] ok · ip=%s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("[wifi] FAILED");
  }
}

// ==========================================================================
// HTTP helpers
// ==========================================================================
static int http_post_json(const String& path, const String& body, String& reply) {
  HTTPClient http;
  String url = String(ATLAS_BASE_URL) + path;
  http.begin(url);
  http.setTimeout(HTTP_TIMEOUT_MS);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(body);
  reply = (code > 0) ? http.getString() : String();
  http.end();
  return code;
}

static int http_get(const String& path, String& reply) {
  HTTPClient http;
  String url = String(ATLAS_BASE_URL) + path;
  http.begin(url);
  http.setTimeout(HTTP_TIMEOUT_MS);
  int code = http.GET();
  reply = (code > 0) ? http.getString() : String();
  http.end();
  return code;
}

// ==========================================================================
// Telemetry push
// ==========================================================================
static void push_telemetry() {
  StaticJsonDocument<512> doc;
  JsonObject payload = doc.createNestedObject("payload");
  read_sensors(payload);
  doc["source"] = "esp32";
  String body; serializeJson(doc, body);

  String reply;
  int code = http_post_json(
    String("/api/robot/devices/") + DEVICE_ID + "/telemetry", body, reply);
  if (code != 200) {
    Serial.printf("[atlas] telemetry POST %d: %s\n", code, reply.c_str());
  }
}

// ==========================================================================
// Command handler
// ==========================================================================
static void handle_command(JsonObject cmd) {
  String id   = cmd["id"]   | "";
  String kind = cmd["kind"] | "";
  if (id == S.last_command_id) return;   // already handled
  S.last_command_id   = id;
  S.last_command_kind = kind;

  Serial.printf("[atlas] cmd %s · %s\n", id.c_str(), kind.c_str());

  if (kind == "emergency_stop") {
    S.safe_state = true;
    actuate_safe();
    return;
  }
  if (kind == "clear_safe_state") {
    S.safe_state = false;
    Serial.println("[atlas] safe_state cleared by owner");
    return;
  }
  if (kind == "ping") {
    Serial.println("[atlas] pong");
    return;
  }
  if (kind == "read_telemetry") {
    push_telemetry();
    return;
  }
  if (kind == "configure") {
    // payload contains the configuration patch — apply as appropriate
    Serial.println("[atlas] configure (no-op in reference firmware)");
    return;
  }

  // Owner-only kinds: actuate / motion / firmware_update.
  // The server ALSO blocks these when role != owner — local check is
  // a defence-in-depth backup that lets the device refuse instantly
  // if it knows it's in SAFE_STATE.
  if (S.safe_state) {
    Serial.printf("[atlas] REFUSED '%s' — device in SAFE_STATE\n", kind.c_str());
    return;
  }
  if (kind == "actuate" || kind == "motion") {
    JsonObject payload = cmd["payload"].as<JsonObject>();
    actuate(payload);
    return;
  }
  if (kind == "firmware_update") {
    // Out of scope for v1; in production this would download a .bin
    // signed by ATLAS_CA and call Update.begin/.write/.end().
    Serial.println("[atlas] firmware_update: stub");
    return;
  }
  Serial.printf("[atlas] unknown command kind: %s\n", kind.c_str());
}

// ==========================================================================
// HTTP-poll inbox
// ==========================================================================
static void poll_inbox() {
  String reply;
  int code = http_get(
    String("/api/robot/devices/") + DEVICE_ID + "/commands/inbox", reply);
  if (code != 200) {
    Serial.printf("[atlas] inbox GET %d\n", code);
    return;
  }
  StaticJsonDocument<4096> doc;
  DeserializationError err = deserializeJson(doc, reply);
  if (err) {
    Serial.printf("[atlas] inbox json: %s\n", err.c_str());
    return;
  }
  JsonArray items = doc["items"].as<JsonArray>();
  for (JsonObject cmd : items) {
    handle_command(cmd);
  }
}

// ==========================================================================
// Optional MQTT path — wired through PubSubClient for brevity.
// Pulls cmd messages from <prefix>/devices/<id>/cmd and routes them to
// handle_command(). Telemetry stays on HTTP for v1 to keep both paths
// loosely coupled.
// ==========================================================================
#if defined(ATLAS_ENABLE_MQTT)
#include <PubSubClient.h>
WiFiClient mqtt_wifi;
PubSubClient mqtt(mqtt_wifi);

static void mqtt_cb(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<2048> doc;
  if (deserializeJson(doc, payload, length)) return;
  JsonObject cmd = doc.as<JsonObject>();
  handle_command(cmd);
}

static void mqtt_ensure() {
  if (!*MQTT_HOST) return;
  if (mqtt.connected()) return;
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(mqtt_cb);
  String cid = String("atlas-") + DEVICE_ID;
  bool ok = (*MQTT_USERNAME)
    ? mqtt.connect(cid.c_str(), MQTT_USERNAME, MQTT_PASSWORD)
    : mqtt.connect(cid.c_str());
  if (ok) {
    String topic = String(MQTT_TOPIC_PREFIX) + "/devices/" + DEVICE_ID + "/cmd";
    mqtt.subscribe(topic.c_str(), 1);
    Serial.printf("[mqtt] subscribed %s\n", topic.c_str());
  }
}
#endif

// ==========================================================================
// Arduino lifecycle
// ==========================================================================
void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.printf("\n[atlas] %s waking · device_id=%s\n", DEVICE_NAME, DEVICE_ID);
  wifi_connect();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    delay(2000);
    wifi_connect();
    return;
  }

#if defined(ATLAS_ENABLE_MQTT)
  if (*MQTT_HOST) { mqtt_ensure(); mqtt.loop(); }
#endif

  uint32_t now = millis();
  if (now - S.last_telemetry_ms >= TELEMETRY_INTERVAL_MS) {
    S.last_telemetry_ms = now;
    push_telemetry();
  }
  if (now - S.last_poll_ms >= POLL_INTERVAL_MS) {
    S.last_poll_ms = now;
    poll_inbox();
  }
  delay(50);
}
