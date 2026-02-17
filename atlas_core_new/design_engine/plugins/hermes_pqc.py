import random
from typing import Dict, Any, List
from .base import DesignPlugin


class HermesPQCPlugin(DesignPlugin):
    key = "hermes_pqc"
    display_name = "Hermes PQC Bridge (Post-Quantum Migration)"

    def default_constraints(self) -> Dict[str, Any]:
        return {
            "deployment": "Mobile + API",
            "max_handshake_ms": 400,
            "max_message_overhead_kb": 8,
            "max_cost_usd": 0,
            "max_weight_kg": 0,
            "mode": "Hybrid (Classical + PQC)"
        }

    def generate_variant(self, idx: int, constraints: Dict[str, Any]) -> Dict[str, Any]:
        mode = constraints.get("mode", "Hybrid (Classical + PQC)")
        scheme = random.choice(["KEM+lattice", "KEM+hash", "Signature+lattice", "Hybrid KEM+Signature"])

        base_latency = random.uniform(120, 650)
        overhead_kb = random.uniform(2, 18)

        max_ms = float(constraints.get("max_handshake_ms", 400))
        max_kb = float(constraints.get("max_message_overhead_kb", 8))

        latency_score = 100 - min(100, (base_latency / max_ms) * 60)
        size_score = 100 - min(100, (overhead_kb / max_kb) * 60)

        performance = 50 + (latency_score * 0.3) + (size_score * 0.3) + random.uniform(-5, 5)
        safety = 90 + (5 if "Hybrid" in scheme or "Hybrid" in mode else 0) + random.uniform(-4, 4)
        manufacturability = 80 - (10 if "Hybrid" in scheme else 0) + random.uniform(-6, 6)
        complexity = 40 + (18 if "Hybrid" in scheme else 0) + random.uniform(-4, 4)

        return {
            "name": f"PQC Variant {idx+1}",
            "architecture": f"{mode} | {scheme}",
            "derived": {
                "estimated_handshake_ms": round(base_latency, 1),
                "estimated_overhead_kb": round(overhead_kb, 1),
            },
            "performance": round(max(0, min(100, performance)), 2),
            "safety": round(max(0, min(100, safety)), 2),
            "manufacturability": round(max(0, min(100, manufacturability)), 2),
            "cost": 0.0,
            "weight": 0.0,
            "complexity": round(max(0, min(100, complexity)), 2),
            "notes": "Proxy estimates. Next step: choose real PQC primitives + implement test vectors + threat model."
        }

    def acceptance_tests(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            "MITM test: handshake fails under attacker proxy",
            "Replay test: message replay rejected",
            "Key rotation: rotate every N messages without breaking session",
            "Latency: handshake under max_handshake_ms on mid-range phone",
            "Audit: event logs for keys and sessions"
        ]

    def parts_list(self, constraints: Dict[str, Any]) -> List[str]:
        return [
            "Crypto abstraction layer (swap algorithms)",
            "Hybrid handshake module",
            "Key vault (OS keystore wrapper)",
            "Threat model document + test harness",
            "Fuzz tests + integration tests"
        ]
