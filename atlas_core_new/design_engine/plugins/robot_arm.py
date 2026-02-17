import random
from typing import Dict, Any, List
from .base import DesignPlugin


class RobotArmPlugin(DesignPlugin):
    key = "robot_arm"
    display_name = "6-DOF Robotic Arm (Workshop Build)"

    def default_constraints(self) -> Dict[str, Any]:
        return {
            "reach_m": 0.8,
            "payload_kg": 3.0,
            "bus_voltage_v": 48,
            "max_power_w": 800,
            "max_cost_usd": 1200,
            "max_weight_kg": 35,
            "control": "Stepper/Servo + MCU"
        }

    def generate_variant(self, idx: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        reach = float(constraints.get("reach_m", 0.8))
        payload = float(constraints.get("payload_kg", 3.0))
        _vmax = float(constraints.get("bus_voltage_v", 48))
        pmax = float(constraints.get("max_power_w", 800))

        drive = random.choice(["Servos", "Steppers", "Hybrid (servo joints + stepper base)"])
        frame = random.choice(["Aluminum extrusion", "Steel plate", "Aluminum + 3D printed brackets"])
        gear = random.choice(["Harmonic drive (proxy)", "Planetary gear", "Belt reduction"])

        torque_proxy = payload * 9.81 * reach * random.uniform(1.2, 2.2)

        cost = random.uniform(450, 2200)
        weight = random.uniform(18, 55)
        if "Steel" in frame:
            weight *= 1.15
        if "Harmonic" in gear:
            cost *= 1.25

        perf = 78 + (8 if "Servo" in drive else 0) + (6 if "Harmonic" in gear else 0) - min(20, (torque_proxy / 60) * 10) + random.uniform(-6, 6)
        safety = 82 + random.uniform(-6, 6)
        manufacturability = 72 + (6 if "extrusion" in frame.lower() else 0) + random.uniform(-8, 8)
        complexity = 45 + (12 if "Hybrid" in drive else 0) + (10 if "Harmonic" in gear else 0)

        estimated_power = min(pmax * 1.3, (torque_proxy * 12) + random.uniform(50, 250))
        if estimated_power > pmax:
            safety -= 8
            perf -= 6
            complexity += 6

        return {
            "name": f"RobotArm Variant {idx+1}",
            "architecture": f"{drive} | {frame} | {gear}",
            "derived": {
                "torque_proxy_nm": round(torque_proxy, 1),
                "estimated_power_w": round(estimated_power, 0),
                "reach_m": reach,
                "payload_kg": payload
            },
            "performance": round(max(0, min(100, perf)), 2),
            "safety": round(max(0, min(100, safety)), 2),
            "manufacturability": round(max(0, min(100, manufacturability)), 2),
            "cost": round(max(50, cost), 2),
            "weight": round(max(1, weight), 2),
            "complexity": round(max(0, min(100, complexity)), 2),
            "notes": "Proxy estimates. Next step: joint torque sizing per axis + motor/gear selection + limit switches."
        }

    def acceptance_tests(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            "Repeatability test: return-to-point error <= 2mm (starter goal)",
            "Payload test: hold payload at max reach for 30s without stall",
            "E-stop test: immediate motor power cut + brake behavior safe",
            "Thermal test: motors/drivers below rated temp at duty cycle",
            "Limit switch test: hard stop prevention works every time"
        ]

    def parts_list(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            "6 joint actuators (steppers/servos) + drivers",
            "Frame material (extrusion/plate) + fasteners",
            "Gear reductions (planetary/belt/harmonic proxy)",
            "Controller (MCU) + optional SBC",
            "Power supply + bus wiring + fuses",
            "Limit switches + emergency stop",
            "End effector mount (modular tool head)"
        ]
