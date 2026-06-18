/*
 * ATLAS Node — reference ESP32 firmware
 *
 * Pairs with the ATLAS backend Phase 7/8 robot stack. Provides:
 *   - WiFi + (optional) TLS to the ATLAS backend
 *   - Telemetry uplink:  POST /api/robot/devices/{id}/telemetry  every 5 s
 *   - Command downlink:  GET  /api/robot/devices/{id}/commands/inbox  every 2 s
 *   - Built-in handlers: ping, read_telemetry, actuate (LED), motion (PWM motor)
 *   - Emergency-stop honoured: when status returns to safe_state, all PWM = 0
 *
 * Pins (default; override in config below)
 *   GPIO 2  — onboard LED, also actuate target
 *   GPIO 25 — DHT-ish analog sensor (or any 0-3.3V source)
 *   GPIO 13 — motor PWM A
 *   GPIO 14 — motor PWM B
 *
 * Required Arduino libraries
 *   - WiFi.h           (built-in)
 *   - HTTPClient.h     (built-in)
 *   - ArduinoJson      (Benoit Blanchon, >=6.21)
 *
 * Build target: ESP32 Dev Module · 4 MB Flash · Arduino IDE 2.x or PlatformIO
 *
 * Wiring & flashing instructions: see /app/hardware/esp32/README.md
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// =============================================================================
// CONFIG — override before flashing
// =============================================================================
static const char* WIFI_SSID     = "YOUR_WIFI_SSID";
static const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Backend base URL. Use http:// for LAN, https:// for production (then set
// ATLAS_USE_TLS = true and paste the CA from /api/robot/mtls/ca below).
static const char* ATLAS_BASE_URL = "http://192.168.1.100:8001";
static const bool  ATLAS_USE_TLS  = false;

// Device identity — register via:
//   curl -X POST $ATLAS/api/robot/devices  -H 'X-Atlas-Role: owner'  \
//        -H 'Content-Type: application/json'  \
//        -d '{"name":"atlas-node-01","kind":"esp32"}'
// The response includes the `id` and a one-time mTLS cert pack.
static const char* DEVICE_ID    = "PASTE_DEVICE_ID_FROM_REGISTRATION";

// Owner token (passed as X-Atlas-Role header). Devices ALWAYS report
// telemetry without auth; this token is only used if the firmware itself
// issues elevated commands back to the backend (rare).
static const char* OWNER_ROLE_HEADER = "guest";

// Telemetry/poll cadence
static const uint32_t TELEMETRY_INTERVAL_MS = 5000;
static const uint32_t INBOX_POLL_INTERVAL_MS = 2000;

// GPIO map
static const uint8_t  PIN_LED        = 2;
static const uint8_t  PIN_SENSOR     = 25;
static const uint8_t  PIN_MOTOR_A    = 13;
static const uint8_t  PIN_MOTOR_B    = 14;
static const uint8_t  PWM_CHANNEL_A  = 0;
static const uint8_t  PWM_CHANNEL_B  = 1;
static const uint16_t PWM_FREQUENCY  = 5000;
static const uint8_t  PWM_RESOLUTION = 8;        // 8-bit (0-255)

// =============================================================================
// STATE
// =============================================================================
static uint32_t last_telemetry_ms = 0;
static uint32_t last_inbox_ms     = 0;
static bool     safe_state        = false;       // set by emergency_stop

// =============================================================================
// HELPERS
// =============================================================================
static void wifi_connect() {
  Serial.printf("[wifi] connecting to %s\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  uint32_t deadline = millis() + 30000;
  while (WiFi.status() != WL_CONNECTED && millis() < deadline) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[wifi] connected · IP %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("[wifi] FAILED — will retry in loop()");
  }
}

static String url_for(const char* path) {
  return String(ATLAS_BASE_URL) + path;
}

static void push_telemetry() {
  if (WiFi.status() != WL_CONNECTED) return;
  StaticJsonDocument<256> doc;
  doc["payload"]["sensor_raw"]   = analogRead(PIN_SENSOR);
  doc["payload"]["uptime_ms"]    = millis();
  doc["payload"]["safe_state"]   = safe_state;
  doc["payload"]["heap_free"]    = ESP.getFreeHeap();
  doc["payload"]["wifi_rssi"]    = WiFi.RSSI();
  doc["source"]                  = "http";
  String body;
  serializeJson(doc, body);

  HTTPClient http;
  String url = url_for("/api/robot/devices/") + DEVICE_ID + "/telemetry";
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  int rc = http.POST(body);
  if (rc > 0) {
    Serial.printf("[telemetry] %d\n", rc);
  } else {
    Serial.printf("[telemetry] failed: %s\n", http.errorToString(rc).c_str());
  }
  http.end();
}

static void apply_command(const JsonObject& cmd) {
  const char* kind   = cmd["kind"]   | "";
  const char* cmd_id = cmd["id"]     | "";
  JsonObject  pl     = cmd["payload"].as<JsonObject>();
  Serial.printf("[cmd] %s · id=%s\n", kind, cmd_id);

  if (!strcmp(kind, "ping")) {
    // No-op acknowledgement — telemetry tick will report we're alive.
    return;
  }
  if (!strcmp(kind, "read_telemetry")) {
    push_telemetry();    // force an immediate reading
    return;
  }
  if (!strcmp(kind, "emergency_stop")) {
    safe_state = true;
    ledcWrite(PWM_CHANNEL_A, 0);
    ledcWrite(PWM_CHANNEL_B, 0);
    digitalWrite(PIN_LED, LOW);
    Serial.println("[cmd] EMERGENCY STOP — entering safe state");
    return;
  }
  if (!strcmp(kind, "clear_safe_state")) {
    safe_state = false;
    Serial.println("[cmd] clear_safe_state — back online");
    return;
  }
  // Below commands ignored in safe_state.
  if (safe_state) {
    Serial.printf("[cmd] %s ignored — device in safe_state\n", kind);
    return;
  }
  if (!strcmp(kind, "actuate")) {
    // payload: { "led": true|false }
    if (pl.containsKey("led")) {
      digitalWrite(PIN_LED, pl["led"].as<bool>() ? HIGH : LOW);
    }
    return;
  }
  if (!strcmp(kind, "motion")) {
    // payload: { "duty_a": 0-255, "duty_b": 0-255 }
    int da = pl["duty_a"] | 0;
    int db = pl["duty_b"] | 0;
    if (da < 0) da = 0; if (da > 255) da = 255;
    if (db < 0) db = 0; if (db > 255) db = 255;
    ledcWrite(PWM_CHANNEL_A, da);
    ledcWrite(PWM_CHANNEL_B, db);
    return;
  }
  Serial.printf("[cmd] unhandled kind=%s\n", kind);
}

static void poll_inbox() {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  String url = url_for("/api/robot/devices/") + DEVICE_ID + "/commands/inbox";
  http.begin(url);
  int rc = http.GET();
  if (rc != 200) {
    if (rc != -1) Serial.printf("[inbox] http %d\n", rc);
    http.end();
    return;
  }
  String body = http.getString();
  http.end();

  DynamicJsonDocument doc(8192);
  DeserializationError err = deserializeJson(doc, body);
  if (err) {
    Serial.printf("[inbox] json: %s\n", err.c_str());
    return;
  }
  JsonArray items = doc["items"].as<JsonArray>();
  for (JsonObject cmd : items) {
    apply_command(cmd);
  }
}

// =============================================================================
// SETUP + LOOP
// =============================================================================
void setup() {
  Serial.begin(115200);
  delay(150);
  Serial.println();
  Serial.println("ATLAS Node booting …");

  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  ledcSetup(PWM_CHANNEL_A, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_B, PWM_FREQUENCY, PWM_RESOLUTION);
  ledcAttachPin(PIN_MOTOR_A, PWM_CHANNEL_A);
  ledcAttachPin(PIN_MOTOR_B, PWM_CHANNEL_B);
  ledcWrite(PWM_CHANNEL_A, 0);
  ledcWrite(PWM_CHANNEL_B, 0);

  wifi_connect();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    wifi_connect();
    delay(2000);
    return;
  }
  uint32_t now = millis();
  if (now - last_telemetry_ms >= TELEMETRY_INTERVAL_MS) {
    last_telemetry_ms = now;
    push_telemetry();
  }
  if (now - last_inbox_ms >= INBOX_POLL_INTERVAL_MS) {
    last_inbox_ms = now;
    poll_inbox();
  }
  delay(50);
}
