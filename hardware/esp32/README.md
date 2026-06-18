# ATLAS · ESP32 Hardware Bridge — Quickstart

> Real ESP32 node talking to the ATLAS backend.
> HTTP poll out of the box, MQTT push when you want to scale.

## Prerequisites

| | |
|---|---|
| Board | Any ESP32 dev module (ESP-WROOM-32 / DevKitC / WEMOS LOLIN32 …) |
| IDE | Arduino IDE 2.x **or** PlatformIO |
| Lib | `ArduinoJson` ≥ 6.21 (`Tools → Manage Libraries`) |
| Network | LAN connectivity to the ATLAS backend host |
| Optional | Mosquitto / EMQX broker if you want MQTT push (HTTP poll works without) |

## Hardware wiring (default sketch)

| GPIO | Purpose |
|---|---|
| `2`  | Onboard LED — used by `actuate { led: true }` commands |
| `13` | Motor channel A (PWM) — used by `motion { duty_a: 0-255 }` |
| `14` | Motor channel B (PWM) — used by `motion { duty_b: 0-255 }` |
| `25` | Analog sensor input — reported as `payload.sensor_raw` |

If your board uses different pins, edit the `PIN_*` constants in
`atlas_node/atlas_node.ino`.

## 1 · Register the device with ATLAS

```bash
ATLAS=http://192.168.1.100:8001
curl -X POST $ATLAS/api/robot/devices \
  -H 'X-Atlas-Role: owner' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "atlas-node-01",
    "kind": "esp32",
    "tags": ["lab","prototype"],
    "hardware_profile": {
      "cpu":"ESP32",
      "ram_mb":512,
      "sensors":["analog_in"],
      "actuators":["led","pwm_a","pwm_b"]
    }
  }'
```

The response body includes:

- `id` — copy this into `DEVICE_ID` in the sketch
- `mtls.cert_pem`, `mtls.key_pem`, `mtls.ca_pem` — store these somewhere
  safe; the private key is shown **once** and only once.

## 2 · Flash the firmware

1. Open `/app/hardware/esp32/atlas_node/atlas_node.ino` in Arduino IDE.
2. Edit the top of the file:
   ```cpp
   WIFI_SSID      = "your_ssid";
   WIFI_PASSWORD  = "your_password";
   ATLAS_BASE_URL = "http://192.168.1.100:8001";   // the backend
   DEVICE_ID      = "abcdef0123…"                  // from step 1
   ```
3. `Tools → Board → ESP32 Dev Module`.
4. `Tools → Partition Scheme → Default 4MB with spiffs`.
5. `Sketch → Upload` (115200 baud).

Open the Serial Monitor (115200) — you should see:

```
ATLAS Node booting …
[wifi] connecting to your_ssid
.....
[wifi] connected · IP 192.168.1.42
[telemetry] 200
[inbox] http 200
```

## 3 · Verify on the ATLAS backend

```bash
# Device should be ONLINE within a few seconds:
curl $ATLAS/api/robot/devices/$DEVICE_ID | jq '.status,.last_seen'

# Telemetry history:
curl $ATLAS/api/robot/devices/$DEVICE_ID/telemetry?limit=3 | jq .
```

## 4 · Send a command from ATLAS

```bash
# Blink the onboard LED on:
curl -X POST $ATLAS/api/robot/devices/$DEVICE_ID/command \
  -H 'X-Atlas-Role: owner' \
  -H 'Content-Type: application/json' \
  -d '{"kind":"actuate","payload":{"led":true}}'

# Drive a motor at 60% on channel A:
curl -X POST $ATLAS/api/robot/devices/$DEVICE_ID/command \
  -H 'X-Atlas-Role: owner' \
  -H 'Content-Type: application/json' \
  -d '{"kind":"motion","payload":{"duty_a":153,"duty_b":0}}'

# Emergency stop:
curl -X POST $ATLAS/api/robot/devices/$DEVICE_ID/emergency-stop \
  -H 'X-Atlas-Role: owner'
```

The Serial Monitor on the ESP32 prints `[cmd] actuate · id=…` etc.

## 5 · (Optional) Enable MQTT push

By default the firmware uses HTTP poll — works on any network, no broker.
For lower latency and many devices, run an MQTT broker on the same LAN
and set on the **backend**:

```bash
# backend/.env
MQTT_BROKER_HOST=192.168.1.5
MQTT_BROKER_PORT=1883
MQTT_TOPIC_PREFIX=atlas
MQTT_USERNAME=atlas
MQTT_PASSWORD=secret
```

Restart the backend.  Check status:

```bash
curl $ATLAS/api/robot/mqtt/status | jq .
# { "enabled": true, "connected": true, … }
```

ATLAS will now **publish** every executed command to
`atlas/devices/<id>/cmd`. It also **subscribes** to
`atlas/devices/+/telemetry` so devices can publish telemetry over MQTT
(faster than HTTP POST and supports retained messages for last-known
state).

> Adding MQTT support to the firmware is left as a follow-up — the
> reference sketch ships with HTTP poll because it works in 100% of
> network conditions without extra dependencies.

## 6 · mTLS (optional but recommended)

The backend mints a per-device cert pack on registration:

- `cert_pem` + `key_pem` — paste into the device (SPIFFS or hard-coded for
  prototype work)
- `ca_pem` — same, so the device verifies the backend's TLS cert when you
  flip `ATLAS_USE_TLS = true`

When `MTLS_ENFORCE=true` is set on the backend, telemetry + inbox calls
require the device certificate. Until then it's logged but accepted.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `[wifi] FAILED` | Wrong SSID/password, or no DHCP — Serial output will say `WL_DISCONNECTED` |
| `[telemetry] -1` | Backend unreachable — verify `ATLAS_BASE_URL` and that the host is on the same LAN |
| `[inbox] http 404` | `DEVICE_ID` typo — confirm with `curl $ATLAS/api/robot/devices` |
| Device shows `safe_state` and won't move | Send `clear_safe_state` (owner-only) with the device's exact `name` as `confirm` body field |
| Commands queue but never execute | Check `/api/robot/devices/{id}/commands?limit=5` — pipeline runs simulate→validate→execute, every step is logged in `pipeline_log` |
| MQTT shows `mqtt_dormant` | `MQTT_BROKER_HOST` env var not set — that's intentional dormancy, HTTP poll still works |

## File layout

```
/app/hardware/esp32/
  README.md                  ← this file
  atlas_node/
    atlas_node.ino           ← reference firmware sketch (HTTP poll)
```
