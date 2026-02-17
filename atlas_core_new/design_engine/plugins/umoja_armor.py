import random
from typing import Dict, Any, List
from .base import DesignPlugin


class UmojaArmorPlugin(DesignPlugin):
    key = "umoja_armor"
    display_name = "Umoja STF Armor Panel"

    def default_constraints(self) -> Dict[str, Any]:
        return {
            "panel_mm": [300, 400],
            "thickness_mm": 10,
            "max_weight_kg": 1.5,
            "max_cost_usd": 250,
            "stf_fill_ratio": 0.6,
            "fiber": "Aramid",
            "shell": "Cordura 500D",
            "pouch": "TPU heat-seal",
        }

    def generate_variant(self, idx: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        panel = constraints.get("panel_mm", [300, 400])
        if isinstance(panel, list) and len(panel) >= 2:
            w_mm, h_mm = panel[0], panel[1]
        else:
            w_mm, h_mm = 300, 400
        t_mm = float(constraints.get("thickness_mm", 10))
        fill = float(constraints.get("stf_fill_ratio", 0.6))

        quilting = random.choice(["4-cell", "8-cell", "12-cell", "diamond"])
        fiber_layers = random.choice([1, 2, 3])
        pouch_count = random.choice([2, 4, 6, 8])

        area_m2 = (w_mm / 1000) * (h_mm / 1000)
        fiber_weight = area_m2 * (0.18 * fiber_layers)
        stf_weight = area_m2 * (t_mm / 1000) * (1.2 * fill)
        shell_weight = area_m2 * 0.12
        weight = fiber_weight + stf_weight + shell_weight

        cost = 40 + (30 * fiber_layers) + (12 * pouch_count) + (20 * area_m2 * 10) + random.uniform(-15, 25)

        quilting_bonus = {"4-cell": 4, "8-cell": 7, "12-cell": 10, "diamond": 9}[quilting]
        performance = 70 + quilting_bonus + (6 * fiber_layers) + (10 * fill) - (pouch_count * 1.5) + random.uniform(-6, 6)
        safety = 88 - (pouch_count * 1.2) + random.uniform(-5, 5)
        manufacturability = 80 - (pouch_count * 1.0) + random.uniform(-8, 8)
        complexity = 30 + (pouch_count * 4) + (fiber_layers * 5)

        return {
            "name": f"Armor Variant {idx+1}",
            "architecture": f"{fiber_layers}x {constraints.get('fiber', 'Aramid')} + STF pouches ({pouch_count}) + {quilting} quilting",
            "derived": {
                "estimated_weight_kg": round(weight, 2),
                "panel_area_m2": round(area_m2, 3),
                "thickness_mm": t_mm,
                "pouch_count": pouch_count
            },
            "performance": round(max(0, min(100, performance)), 2),
            "safety": round(max(0, min(100, safety)), 2),
            "manufacturability": round(max(0, min(100, manufacturability)), 2),
            "cost": round(max(10, cost), 2),
            "weight": round(max(0.1, weight), 2),
            "complexity": round(max(0, min(100, complexity)), 2),
            "notes": "Proxy estimates. Next step: define STF pouch sealing method + drop test protocol."
        }

    def acceptance_tests(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            "Flex test: bend radius <= 100mm without cracking",
            "Drop test: 5kg from 1m x10 with no leaks",
            "Leak check: 24hr compression + visual inspection",
            "Abrasion test: 1000 rub cycles on shell",
            "Edge stitch test: seam does not tear under pull"
        ]

    def parts_list(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            f"Outer shell fabric: {constraints.get('shell', 'Cordura 500D')}",
            f"Fiber layer: {constraints.get('fiber', 'Aramid')} cloth",
            f"STF pouch film: {constraints.get('pouch', 'TPU heat-seal')}",
            "STF fill (simulation/proxy spec unless lab partner)",
            "Spacer mesh / comfort foam",
            "Thread (heavy duty) + edge binding tape",
            "Heat sealer (for TPU) or equivalent sealing method"
        ]
