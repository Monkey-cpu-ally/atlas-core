# ATLAS ESP32 Reference Firmware

A single-file Arduino sketch that mirrors the architect's wire protocol:

```
ESP32 ─── POST /api/robot/devices/{id}/telemetry  ──> ATLAS (every 5 s)
ESP32 ─── GET  /api/robot/devices/{id}/commands/inbox ──> ATLAS (every 3 s)
                                                          │
                                                          └── handle: ping · read_telemetry
                                                                       configure · actuate · motion
                                                                       emergency_stop · clear_safe_state
                                                                       firmware_update
```

## Files

| File | Role |
| --- | --- |
| `atlas_device.ino` | Single-file Arduino sketch (ESP32 core ≥ 2.0). Drop into Arduino IDE / PlatformIO. |
| `README.md` | This guide. |

## Quickstart

1. **Register the device on ATLAS:**
   ```bash
   curl -X POST https://atlas.local/api/robot/devices \
     -H "Content-Type: application/json" \
     -H "X-Atlas-Role: owner" \
     -d '{"name":"POSEIDON-BUOY","kind":"esp32",
          "hardware_profile":{"sensors":["water_temperature","ph","turbidity"]},
          "tags":["water","stationary"]}'
   ```
   The response includes a one-shot `mtls` block with `cert_pem`, `key_pem`,
   `ca_pem` and the device's `id`. **Save these now** — the private key is
   never shown again.

2. **Edit `atlas_device.ino`:**
   - `WIFI_SSID` / `WIFI_PASSWORD`
   - `ATLAS_BASE_URL` (e.g. `https://192.168.1.42:8001`)
   - `DEVICE_ID` (the UUID from step 1, **not** the friendly name)
   - `DEVICE_NAME` (cosmetic — serial log only)
   - **Optional** mTLS: paste `DEVICE_CERT`, `DEVICE_KEY`, `ATLAS_CA` and
     swap the `WiFiClient` block for `WiFiClientSecure` (see the comment in
     the sketch). Enforcement on the server is gated by `MTLS_ENFORCE=true`.

3. **Build & flash** — Arduino IDE: select your ESP32 board, `Sketch → Upload`.

4. **Watch the Serial Monitor (115200 baud):**
   ```
   [atlas] POSEIDON-BUOY waking · device_id=abc123
   [wifi] connecting....
   [wifi] ok · ip=192.168.1.51
   [atlas] cmd 8ce4… · ping
   [atlas] pong
   ```

## Architect's safety contract

| Server command | Device behaviour |
| --- | --- |
| `ping` | Logs `pong`, no side effect. |
| `read_telemetry` | Immediate `push_telemetry()`. |
| `configure` | Stub — apply the payload patch in `handle_command` for your build. |
| `actuate` / `motion` | Calls `actuate(payload)` ONLY if `safe_state == false`. |
| `emergency_stop` | Sets `safe_state = true`, calls `actuate_safe()` (move every actuator to its known-safe position). |
| `clear_safe_state` | Sets `safe_state = false`. Server already requires owner-role + name-confirm before emitting this. |
| `firmware_update` | Stub. In production, download a signed `.bin`, call `Update.begin/.write/.end()`. |

**Belt-and-braces:** the device refuses every `actuate` / `motion` / `firmware_update`
while `safe_state == true`, even if the server somehow lets one through. The
flag is local-authoritative until `clear_safe_state` arrives.

## Optional MQTT (Phase 8c)

Compile with `-DATLAS_ENABLE_MQTT` and set `MQTT_HOST` / `MQTT_PORT` in the
sketch. The device will additionally subscribe to:

```
<MQTT_TOPIC_PREFIX>/devices/<DEVICE_ID>/cmd
```

and route incoming JSON messages through the same `handle_command()` that
the HTTP poll uses. Telemetry stays on HTTP in v1 (one push path is enough).
When `MQTT_BROKER_HOST` is set on the server, every executed command is
published to that topic — the ESP32 acts on it instantly instead of waiting
for the next poll tick.

## Optional mTLS (Phase 8f)

The server's `/api/robot/devices` endpoint mints one cert pack per device.
Drop the three PEM strings into the constants at the top of the sketch:

```c
static const char* DEVICE_CERT = "-----BEGIN CERTIFICATE-----\n…\n";
static const char* DEVICE_KEY  = "-----BEGIN PRIVATE KEY-----\n…\n";
static const char* ATLAS_CA    = "-----BEGIN CERTIFICATE-----\n…\n";
```

Then in `http_post_json` / `http_get`, replace the implicit `WiFiClient`
with `WiFiClientSecure` and call `setCACert(ATLAS_CA)` + `setCertificate
(DEVICE_CERT)` + `setPrivateKey(DEVICE_KEY)` before each request. The
server will require this when `MTLS_ENFORCE=true`; otherwise the cert is
ignored and HTTP-poll continues to work — handy for incremental rollout.

## Multiple device types from one sketch

`read_sensors()` and `actuate()` are the only physical-world hooks. To turn
this into AETHER-STATION or SOIL-WATCH, swap the sensor reads (commented
examples are in the sketch) and the actuator pin map. Everything else —
the auth header, the command pipeline, the safe-state contract — stays
identical.

## Known limitations (v1)

- HTTP-poll only by default. Set `-DATLAS_ENABLE_MQTT` and configure
  `MQTT_HOST` for push delivery.
- No persistent state across reboots: `safe_state` resets to `false` on
  every boot. If the architect wants the safe flag to survive power-cycle,
  persist it via `Preferences` (NVS) and re-load in `setup()`.
- `firmware_update` is a stub — real OTA requires a signed `.bin` channel
  (Phase 8 roadmap).
- The sketch trusts the `ATLAS_BASE_URL` you point it at. With mTLS off and
  HTTPS off, the link is plaintext — fine for local LAN, **not** fine for
  internet deployment.
