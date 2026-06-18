"""ATLAS ESP32 Node Simulator
==========================

Pure-Python sim that mimics the reference Arduino firmware in
`/app/hardware/esp32/atlas_node/atlas_node.ino`. Useful for:

  * End-to-end tests when no real hardware is plugged in
  * CI verification of the robot pipeline
  * Architect demos of the HUD without an ESP32 on the desk

Usage:
    python /app/hardware/esp32/sim/atlas_node_sim.py \\
        --device-id $DEVICE_ID \\
        --backend http://localhost:8001 \\
        --interval 5

The simulator implements the same handlers as the firmware:
    ping · read_telemetry · actuate(led) · motion(duty_a/b) ·
    emergency_stop · clear_safe_state

It POSTs a synthetic-but-realistic telemetry payload every `--interval`
seconds and polls the inbox every 2 s, applying any commands it finds.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from typing import Any, Dict

import httpx


class AtlasNode:
    def __init__(self, backend: str, device_id: str, interval: float = 5.0):
        self.backend = backend.rstrip("/")
        self.device_id = device_id
        self.interval = interval

        self.boot_ms = int(time.time() * 1000)
        self.safe_state = False
        self.led_on = False
        self.motor_a = 0
        self.motor_b = 0
        self.sensor_baseline = random.uniform(1500, 2200)

    # --- helpers -----------------------------------------------------
    def _now_ms(self) -> int:
        return int(time.time() * 1000) - self.boot_ms

    def _read_sensor(self) -> int:
        # Drift + small noise around baseline so the anomaly detector
        # eventually has something interesting to see.
        return int(self.sensor_baseline + random.uniform(-40, 40))

    def _telemetry_payload(self) -> Dict[str, Any]:
        return {
            "payload": {
                "sensor_raw": self._read_sensor(),
                "uptime_ms":  self._now_ms(),
                "safe_state": self.safe_state,
                "led_on":     self.led_on,
                "motor_a":    self.motor_a,
                "motor_b":    self.motor_b,
                "wifi_rssi":  random.randint(-72, -55),
                "heap_free":  random.randint(180_000, 240_000),
            },
            "source": "http_sim",
        }

    # --- HTTP --------------------------------------------------------
    def push_telemetry(self) -> None:
        url = f"{self.backend}/api/robot/devices/{self.device_id}/telemetry"
        try:
            r = httpx.post(url, json=self._telemetry_payload(), timeout=8.0)
            print(f"[telemetry] {r.status_code}", flush=True)
        except Exception as exc:    # noqa: BLE001
            print(f"[telemetry] FAIL: {exc}", flush=True)

    def poll_inbox(self) -> None:
        url = f"{self.backend}/api/robot/devices/{self.device_id}/commands/inbox"
        try:
            r = httpx.get(url, timeout=8.0)
            if r.status_code != 200:
                print(f"[inbox] http {r.status_code}", flush=True)
                return
            for cmd in r.json().get("items", []):
                self.apply_command(cmd)
        except Exception as exc:    # noqa: BLE001
            print(f"[inbox] FAIL: {exc}", flush=True)

    # --- command handlers --------------------------------------------
    def apply_command(self, cmd: Dict[str, Any]) -> None:
        kind = cmd.get("kind") or ""
        cmd_id = cmd.get("id") or ""
        pl = cmd.get("payload") or {}
        print(f"[cmd] {kind} · id={cmd_id} payload={json.dumps(pl)}", flush=True)

        if kind == "ping":
            return
        if kind == "read_telemetry":
            self.push_telemetry()
            return
        if kind == "emergency_stop":
            self.safe_state = True
            self.motor_a = 0
            self.motor_b = 0
            self.led_on = False
            print("[cmd] EMERGENCY STOP — safe state", flush=True)
            return
        if kind == "clear_safe_state":
            self.safe_state = False
            print("[cmd] clear_safe_state — online", flush=True)
            return
        if self.safe_state:
            print(f"[cmd] {kind} ignored — in safe_state", flush=True)
            return
        if kind == "actuate":
            if "led" in pl:
                self.led_on = bool(pl["led"])
            return
        if kind == "motion":
            self.motor_a = max(0, min(255, int(pl.get("duty_a", 0))))
            self.motor_b = max(0, min(255, int(pl.get("duty_b", 0))))
            return
        print(f"[cmd] unhandled kind={kind}", flush=True)

    # --- main loop ---------------------------------------------------
    def run(self) -> None:
        print(
            f"ATLAS Node SIM · device_id={self.device_id} · backend={self.backend} "
            f"· interval={self.interval}s", flush=True,
        )
        last_tel = 0.0
        last_inbox = 0.0
        try:
            while True:
                now = time.time()
                if now - last_tel >= self.interval:
                    last_tel = now
                    self.push_telemetry()
                if now - last_inbox >= 2.0:
                    last_inbox = now
                    self.poll_inbox()
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n[sim] shutdown requested.", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="ATLAS ESP32 simulator")
    ap.add_argument("--backend", default="http://localhost:8001")
    ap.add_argument("--device-id", required=True)
    ap.add_argument("--interval", type=float, default=5.0)
    args = ap.parse_args()
    AtlasNode(args.backend, args.device_id, args.interval).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
