import random
from typing import Dict, Any, List
from .base import DesignPlugin


class HydraCorePowerPlugin(DesignPlugin):
    key = "hydracore_power"
    display_name = "Hydra-Core Universal Power Spine"

    def default_constraints(self) -> Dict[str, Any]:
        return {
            "bus_voltage_v": 24,
            "target_power_w": 500,
            "max_cost_usd": 400,
            "max_weight_kg": 3.0,
            "chemistry": "Li-ion (NMC)",
            "thermal_limit_c": 70,
            "ip_rating": "IP54",
        }

    def generate_variant(self, idx: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        vbus = float(constraints.get("bus_voltage_v", 24))
        pwr = float(constraints.get("target_power_w", 500))

        arch = random.choice(["Swappable Pack", "Pack + Supercap Burst", "Dual-Pack Redundant", "Hot-Swap Rail"])
        current_a = pwr / max(vbus, 1.0)

        base_cost = random.uniform(120, 650)
        base_weight = random.uniform(0.8, 5.0)

        redundancy_bonus = 10 if "Dual" in arch else 0
        current_penalty = min(40, current_a * 0.6)

        performance = 80 + redundancy_bonus - current_penalty + random.uniform(-8, 8)
        safety = 85 - min(25, (current_a / 30) * 10) + random.uniform(-6, 6)
        manufacturability = 75 + random.uniform(-10, 10)
        complexity = 35 + (10 if "Supercap" in arch else 0) + (12 if "Hot-Swap" in arch else 0)

        return {
            "name": f"Power Variant {idx+1}",
            "architecture": arch,
            "derived": {
                "estimated_current_a": round(current_a, 2),
                "bus_voltage_v": vbus,
                "target_power_w": pwr,
            },
            "performance": round(max(0, min(100, performance)), 2),
            "safety": round(max(0, min(100, safety)), 2),
            "manufacturability": round(max(0, min(100, manufacturability)), 2),
            "cost": round(max(10, base_cost), 2),
            "weight": round(max(0.1, base_weight), 2),
            "complexity": round(max(0, min(100, complexity)), 2),
            "notes": "Proxy estimates. Next step: choose cell format, BMS rating, fuse sizing, and thermal path."
        }

    def acceptance_tests(self, constraints: Dict[str, Any]) -> List[str]:
        vbus = constraints.get("bus_voltage_v", 24)
        return [
            f"Load test: maintain {vbus}V bus within +/-5% at target power for 10 minutes",
            "Thermal test: hottest component stays below thermal_limit_c",
            "Short protection: fuse/BMS trips safely under fault",
            "Connector cycle test: 500 insertions without failure",
            "Drop test: 1m drop x5 with no enclosure cracks"
        ]

    def parts_list(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            "Battery pack (cell holders + cells OR prebuilt pack)",
            "BMS (overcurrent/overvoltage/undervoltage/temp)",
            "Main fuse + spare fuses",
            "DC bus connector set (locking)",
            "Wiring harness (rated for expected current)",
            "Enclosure (ABS/Aluminum) + strain reliefs",
            "Thermal pads + heat spreader plate (optional)",
        ]
