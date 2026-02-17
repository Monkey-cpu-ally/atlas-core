from __future__ import annotations

import time
import json
import hmac
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable, Literal
from uuid import uuid4

# ============================================================
# Sword & Shield Protocol v1
# - Shield: policy + detection + isolation controls
# - Sword: safe response actions (no hack-back)
# ============================================================

Zone = Literal["core_memory", "tools_io", "render_forge", "connectors", "ui", "unknown"]
Severity = Literal["low", "medium", "high", "critical"]
RiskClass = Literal["low", "medium", "high", "critical"]
Lane = Literal["FAST", "SAFE", "HEAVY"]
WarriorMode = Literal["guardian", "warrior"]


def utc_ms() -> int:
    return int(time.time() * 1000)


def stable_hash(obj: Any) -> str:
    s = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(s).hexdigest()


# -----------------------------
# Zone Contracts
# -----------------------------
@dataclass
class ZoneContract:
    zone: str
    allowed_actions: List[str]
    base_risk: Dict[str, int]


class ZoneContractRegistry:
    def __init__(self):
        self.contracts: Dict[str, ZoneContract] = {}

    def register(self, contract: ZoneContract):
        self.contracts[contract.zone] = contract

    def get(self, zone: str) -> ZoneContract:
        return self.contracts.get(zone) or ZoneContract(
            zone="unknown",
            allowed_actions=[],
            base_risk={}
        )


class RiskScorer:
    def __init__(self, contracts: ZoneContractRegistry):
        self.contracts = contracts

    def score(self, zone: str, action: str, context: Optional[Dict[str, Any]] = None) -> int:
        context = context or {}
        base = context.get("base_risk_override")
        if isinstance(base, int):
            return max(0, min(100, base))
        contract = self.contracts.get(zone)
        return contract.base_risk.get(action, 40)


def default_zone_contracts() -> ZoneContractRegistry:
    registry = ZoneContractRegistry()
    registry.register(ZoneContract(
        zone="core_memory",
        allowed_actions=["snapshot_forensics"],
        base_risk={"snapshot_forensics": 25}
    ))
    registry.register(ZoneContract(
        zone="render_forge",
        allowed_actions=["snapshot_forensics", "isolate_zone"],
        base_risk={"snapshot_forensics": 25, "isolate_zone": 45}
    ))
    registry.register(ZoneContract(
        zone="tools_io",
        allowed_actions=["snapshot_forensics", "isolate_zone", "tools_call"],
        base_risk={"snapshot_forensics": 25, "isolate_zone": 55, "tools_call": 30}
    ))
    registry.register(ZoneContract(
        zone="connectors",
        allowed_actions=["snapshot_forensics", "isolate_zone", "freeze_connector"],
        base_risk={"snapshot_forensics": 25, "isolate_zone": 65, "freeze_connector": 75}
    ))
    registry.register(ZoneContract(
        zone="ui",
        allowed_actions=["snapshot_forensics"],
        base_risk={"snapshot_forensics": 20}
    ))
    return registry


# -----------------------------
# Cache (fast path accelerator)
# -----------------------------
@dataclass
class CacheEntry:
    value: Any
    created_ms: int
    ttl_ms: int


class TinyCache:
    def __init__(self, max_items: int = 500):
        self.max_items = max_items
        self.store: Dict[str, CacheEntry] = {}

    def get(self, key: str) -> Optional[Any]:
        ent = self.store.get(key)
        if not ent:
            return None
        if utc_ms() - ent.created_ms > ent.ttl_ms:
            self.store.pop(key, None)
            return None
        return ent.value

    def set(self, key: str, value: Any, ttl_ms: int = 60_000) -> None:
        if len(self.store) >= self.max_items:
            oldest_key = min(self.store.items(), key=lambda kv: kv[1].created_ms)[0]
            self.store.pop(oldest_key, None)
        self.store[key] = CacheEntry(value=value, created_ms=utc_ms(), ttl_ms=ttl_ms)


# -----------------------------
# Metrics
# -----------------------------
@dataclass
class Metric:
    name: str
    lane: Lane
    zone: Zone
    ms: int
    cached: bool
    ok: bool
    meta: Dict[str, Any] = field(default_factory=dict)


class Metrics:
    def __init__(self):
        self.events: List[Metric] = []

    def log(self, m: Metric) -> None:
        self.events.append(m)

    def summary(self) -> Dict[str, Any]:
        if not self.events:
            return {"count": 0}
        total = len(self.events)
        avg = sum(e.ms for e in self.events) / total
        by_lane: Dict[str, List[int]] = {}
        for e in self.events:
            by_lane.setdefault(e.lane, []).append(e.ms)
        lane_stats = {k: {"count": len(v), "avg_ms": sum(v) / len(v)} for k, v in by_lane.items()}
        return {"count": total, "avg_ms": avg, "lane": lane_stats}


# -----------------------------
# Tamper-evident audit chain
# -----------------------------
@dataclass
class AuditEvent:
    ts_ms: int
    event_id: str
    actor: str              # human | hermes | ajani | minerva | system
    action: str
    zone: Zone
    severity: Severity
    details: Dict[str, Any]
    prev_hash: str
    hash: str


class AuditChain:
    """
    Append-only, hash-chained audit log.
    Store events wherever you want (file/db); this keeps integrity in-memory.
    """
    def __init__(self, secret_key: bytes):
        self._key = secret_key
        self._events: List[AuditEvent] = []
        self._prev_hash = "GENESIS"

    def append(self, actor: str, action: str, zone: Zone, severity: Severity, details: Dict[str, Any]) -> AuditEvent:
        payload = {
            "ts_ms": utc_ms(),
            "event_id": f"evt_{uuid4().hex}",
            "actor": actor,
            "action": action,
            "zone": zone,
            "severity": severity,
            "details": details,
            "prev_hash": self._prev_hash,
        }
        msg = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = hmac.new(self._key, msg, hashlib.sha256).hexdigest()

        evt = AuditEvent(
            ts_ms=payload["ts_ms"],
            event_id=payload["event_id"],
            actor=actor,
            action=action,
            zone=zone,
            severity=severity,
            details=details,
            prev_hash=payload["prev_hash"],
            hash=digest,
        )
        self._events.append(evt)
        self._prev_hash = digest
        return evt

    def export(self) -> List[Dict[str, Any]]:
        return [e.__dict__ for e in self._events]


# -----------------------------
# Capability tokens (simple)
# -----------------------------
@dataclass
class CapabilityToken:
    token_id: str
    issued_to: str
    caps: List[str]
    exp_ms: int
    max_risk: int = 40  # 0..100

    def is_valid(self) -> bool:
        return utc_ms() < self.exp_ms


class TokenVault:
    def __init__(self):
        self._tokens: Dict[str, CapabilityToken] = {}

    def issue(self, issued_to: str, caps: List[str], ttl_ms: int, max_risk: int = 40) -> str:
        tok_id = f"tok_{uuid4().hex}"
        tok = CapabilityToken(tok_id, issued_to, caps, utc_ms() + ttl_ms, max_risk=max_risk)
        self._tokens[tok_id] = tok
        return tok_id

    def verify(self, tok_id: str) -> CapabilityToken:
        tok = self._tokens.get(tok_id)
        if not tok:
            raise PermissionError("Token not found.")
        if not tok.is_valid():
            raise PermissionError("Token expired.")
        return tok

    def revoke(self, tok_id: str) -> None:
        self._tokens.pop(tok_id, None)


# -----------------------------
# Policy Engine (Shield)
# -----------------------------
@dataclass
class PolicyDecision:
    allow: bool
    reason: str
    risk_score: int  # 0..100
    required_approval: Literal["none", "hermes", "human+hermes"] = "none"


class PolicyEngine:
    """
    Central place to enforce rules so Hermes stays Hermes but safer.
    """
    def __init__(self, human_required_over: int = 50):
        self.human_required_over = human_required_over

    def decide(
        self,
        actor: str,
        action: str,
        zone: Zone,
        risk_score: int,
        token: Optional[CapabilityToken],
    ) -> PolicyDecision:
        # Default-deny for unknown zone actions
        if zone == "unknown":
            return PolicyDecision(False, "Unknown zone", 90, "human+hermes")

        # Token required for tool IO / connectors
        if zone in ("tools_io", "connectors") and token is None:
            return PolicyDecision(False, "Missing token for IO/connectors", 85, "human+hermes")

        # Risk gating
        if token is not None and risk_score > token.max_risk:
            return PolicyDecision(False, f"Risk {risk_score} exceeds token max {token.max_risk}", risk_score, "human+hermes")

        # High-risk actions always need human+hermes approval
        if risk_score >= self.human_required_over:
            return PolicyDecision(True, "Allowed with dual approval", risk_score, "human+hermes")

        # Medium needs Hermes approval
        if risk_score >= 35:
            return PolicyDecision(True, "Allowed with Hermes approval", risk_score, "hermes")

        return PolicyDecision(True, "Allowed", risk_score, "none")


# -----------------------------
# Detection (Shield)
# -----------------------------
@dataclass
class Signal:
    name: str
    zone: Zone
    severity: Severity
    score: int
    details: Dict[str, Any] = field(default_factory=dict)


class Detector:
    def evaluate(self, ctx: Dict[str, Any]) -> List[Signal]:
        return []


class RateAnomalyDetector(Detector):
    """
    Simple behavioral detector: too many actions in a time window.
    """
    def __init__(self, max_per_minute: int = 120):
        self.max_per_minute = max_per_minute

    def evaluate(self, ctx: Dict[str, Any]) -> List[Signal]:
        recent = ctx.get("recent_action_count_60s", 0)
        if recent > self.max_per_minute:
            return [Signal(
                name="rate_anomaly",
                zone=ctx.get("zone", "unknown"),
                severity="high",
                score=75,
                details={"recent_action_count_60s": recent, "max_per_minute": self.max_per_minute}
            )]
        return []


# -----------------------------
# Response (Sword)
# -----------------------------
@dataclass
class ResponseAction:
    name: str
    zone: Zone
    risk_score: int
    params: Dict[str, Any] = field(default_factory=dict)


class ResponseEngine:
    """
    SAFE defensive actions only.
    In your real build, these actions will call your actual system controls.
    """
    def __init__(self):
        self.zone_state: Dict[Zone, str] = {
            "core_memory": "normal",
            "tools_io": "normal",
            "render_forge": "normal",
            "connectors": "normal",
            "ui": "normal",
            "unknown": "restricted",
        }

    def execute(self, action: ResponseAction) -> Dict[str, Any]:
        if action.name == "isolate_zone":
            self.zone_state[action.zone] = "isolated"
            return {"ok": True, "zone": action.zone, "state": "isolated"}

        if action.name == "revoke_token":
            # token revocation handled by TokenVault externally
            return {"ok": True, "note": "Use TokenVault.revoke(token_id)"}

        if action.name == "freeze_connector":
            self.zone_state["connectors"] = "isolated"
            return {"ok": True, "zone": "connectors", "state": "isolated"}

        if action.name == "snapshot_forensics":
            # stub: you would package logs, recent actions, configs
            return {"ok": True, "bundle_id": f"forensic_{uuid4().hex}"}

        return {"ok": False, "error": "Unknown action"}


# -----------------------------
# The Organ: Sword & Shield
# -----------------------------
class SwordShieldOrgan:
    def __init__(
        self,
        audit: AuditChain,
        tokens: TokenVault,
        policy: PolicyEngine,
        response: ResponseEngine,
        contracts: Optional[ZoneContractRegistry] = None,
        mode: WarriorMode = "guardian",
    ):
        self.audit = audit
        self.tokens = tokens
        self.policy = policy
        self.response = response
        self.contracts = contracts or default_zone_contracts()
        self.risk = RiskScorer(self.contracts)
        self.detectors: List[Detector] = [RateAnomalyDetector()]
        self.mode: WarriorMode = mode
        self.strike_count: Dict[Zone, int] = {}

    def evaluate_signals(self, ctx: Dict[str, Any]) -> List[Signal]:
        signals: List[Signal] = []
        for d in self.detectors:
            signals.extend(d.evaluate(ctx))
        return signals

    def record_strike(self, zone: Zone) -> int:
        self.strike_count[zone] = self.strike_count.get(zone, 0) + 1
        return self.strike_count[zone]

    def clear_strikes(self, zone: Zone) -> None:
        self.strike_count[zone] = 0

    def propose_defense(self, signals: List[Signal]) -> List[ResponseAction]:
        actions: List[ResponseAction] = []
        for s in signals:
            if s.severity not in ("high", "critical"):
                continue

            strikes = self.record_strike(s.zone)

            if self.mode == "guardian":
                actions.append(ResponseAction(
                    name="isolate_zone",
                    zone=s.zone,
                    risk_score=45,
                    params={"reason": s.name}
                ))
                actions.append(ResponseAction(
                    name="snapshot_forensics",
                    zone=s.zone,
                    risk_score=30,
                    params={"trigger": s.name}
                ))

            elif self.mode == "warrior":
                actions.append(ResponseAction(
                    name="snapshot_forensics",
                    zone=s.zone,
                    risk_score=30,
                    params={"trigger": s.name}
                ))

                if strikes >= 1:
                    actions.append(ResponseAction(
                        name="isolate_zone",
                        zone=s.zone,
                        risk_score=45,
                        params={"reason": s.name, "strikes": strikes}
                    ))

                if s.zone == "connectors" or s.zone == "tools_io":
                    if strikes >= 2 or (s.severity == "critical" and s.score >= 85):
                        actions.append(ResponseAction(
                            name="freeze_connector",
                            zone="connectors",
                            risk_score=75,
                            params={"trigger": s.name, "strikes": strikes}
                        ))

        return actions

    def request_action(
        self,
        actor: str,
        action: str,
        zone: Zone,
        risk_score: Optional[int] = None,
        token_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        approvals: Optional[Dict[str, bool]] = None,
    ) -> Dict[str, Any]:
        details = details or {}
        approvals = approvals or {}

        contract = self.contracts.get(zone)
        if action not in contract.allowed_actions and action != "tools_call":
            return {"ok": False, "blocked": True, "reason": f"Action '{action}' not allowed in zone '{zone}'"}

        if risk_score is None:
            risk_score = self.risk.score(zone, action, details)

        token = None
        if token_id:
            token = self.tokens.verify(token_id)

        decision = self.policy.decide(actor, action, zone, risk_score, token)

        self.audit.append(
            actor="system",
            action="policy_decision",
            zone=zone,
            severity="medium" if decision.allow else "high",
            details={"request_actor": actor, "action": action, "risk": risk_score, "decision": decision.__dict__}
        )

        if not decision.allow:
            return {"ok": False, "blocked": True, "reason": decision.reason, "decision": decision.__dict__}

        # Enforce approvals
        if decision.required_approval == "hermes" and not approvals.get("hermes", False):
            return {"ok": False, "blocked": True, "reason": "Hermes approval required", "decision": decision.__dict__}

        if decision.required_approval == "human+hermes":
            if not approvals.get("human", False) or not approvals.get("hermes", False):
                return {"ok": False, "blocked": True, "reason": "Human + Hermes approval required", "decision": decision.__dict__}

        # Execute defensive actions only (Sword)
        # Map high-level request to safe response ops
        if action == "isolate_zone":
            result = self.response.execute(ResponseAction("isolate_zone", zone, risk_score, details))
        elif action == "freeze_connector":
            result = self.response.execute(ResponseAction("freeze_connector", zone, risk_score, details))
        elif action == "snapshot_forensics":
            result = self.response.execute(ResponseAction("snapshot_forensics", zone, risk_score, details))
        elif action == "tools_call":
            result = {"ok": True, "action": "tools_call", "zone": zone, "approved": True}
        else:
            return {"ok": False, "blocked": True, "reason": "Unsupported action in Sword protocol"}

        self.audit.append(actor=actor, action=action, zone=zone, severity="low", details={"result": result, **details})
        return {"ok": True, "result": result, "decision": decision.__dict__}


# -----------------------------
# Task Request/Response
# -----------------------------
@dataclass
class TaskRequest:
    name: str
    zone: Zone
    lane: Lane
    payload: Dict[str, Any]
    max_ms: int = 600
    cache_ttl_ms: int = 30_000
    allow_cache: bool = True
    risk_score: int = 20
    token_id: Optional[str] = None
    approvals: Dict[str, bool] = field(default_factory=dict)


@dataclass
class TaskResponse:
    ok: bool
    result: Any
    lane: Lane
    ms: int
    cached: bool = False
    note: str = ""


# -----------------------------
# Hermes Router (3-Lane)
# -----------------------------
class HermesRouter:
    """
    FAST: local micro-engine functions (instant)
    SAFE: guarded tool calls (through Sword&Shield)
    HEAVY: big model / big render / cloud
    """
    def __init__(
        self,
        cache: TinyCache,
        metrics: Metrics,
        sword_shield: Optional[SwordShieldOrgan] = None,
        fast_handlers: Optional[Dict[str, Callable[[Dict[str, Any]], Any]]] = None,
        safe_handlers: Optional[Dict[str, Callable[[Dict[str, Any]], Any]]] = None,
        heavy_handlers: Optional[Dict[str, Callable[[Dict[str, Any]], Any]]] = None,
    ):
        self.cache = cache
        self.metrics = metrics
        self.sword_shield = sword_shield
        self.fast_handlers = fast_handlers or {}
        self.safe_handlers = safe_handlers or {}
        self.heavy_handlers = heavy_handlers or {}

    def run(self, req: TaskRequest) -> TaskResponse:
        start = utc_ms()
        cache_key = stable_hash({"name": req.name, "lane": req.lane, "payload": req.payload})

        if req.allow_cache:
            cached_val = self.cache.get(cache_key)
            if cached_val is not None:
                ms = utc_ms() - start
                self.metrics.log(Metric(req.name, req.lane, req.zone, ms, True, True))
                return TaskResponse(True, cached_val, req.lane, ms, cached=True, note="cache-hit")

        try:
            if req.lane == "FAST":
                fn = self.fast_handlers.get(req.name)
                if not fn:
                    raise ValueError(f"No FAST handler for {req.name}")
                out = fn(req.payload)

            elif req.lane == "SAFE":
                if self.sword_shield is not None:
                    gate = self.sword_shield.request_action(
                        actor="hermes",
                        action="tools_call",
                        zone=req.zone,
                        risk_score=req.risk_score,
                        token_id=req.token_id,
                        approvals=req.approvals,
                        details={"task": req.name}
                    )
                    if not gate.get("ok"):
                        ms = utc_ms() - start
                        self.metrics.log(Metric(req.name, req.lane, req.zone, ms, False, False, {"blocked": gate}))
                        return TaskResponse(False, gate, req.lane, ms, cached=False, note="blocked-by-shield")

                fn = self.safe_handlers.get(req.name)
                if not fn:
                    raise ValueError(f"No SAFE handler for {req.name}")
                out = fn(req.payload)

            else:  # HEAVY
                fn = self.heavy_handlers.get(req.name)
                if not fn:
                    raise ValueError(f"No HEAVY handler for {req.name}")
                out = fn(req.payload)

            ms = utc_ms() - start
            ok = True

            if ms > req.max_ms and req.lane == "FAST":
                note = f"budget-exceeded({ms}ms>{req.max_ms}ms)"
            else:
                note = "ok"

            if req.allow_cache:
                self.cache.set(cache_key, out, ttl_ms=req.cache_ttl_ms)

            self.metrics.log(Metric(req.name, req.lane, req.zone, ms, False, ok, {"note": note}))
            return TaskResponse(ok, out, req.lane, ms, cached=False, note=note)

        except Exception as e:
            ms = utc_ms() - start
            self.metrics.log(Metric(req.name, req.lane, req.zone, ms, False, False, {"error": str(e)}))
            return TaskResponse(False, {"error": str(e)}, req.lane, ms, cached=False, note="error")


# -----------------------------
# FAST micro-engine examples
# -----------------------------
def fast_outline(payload: Dict[str, Any]) -> Dict[str, Any]:
    topic = payload.get("topic", "unknown")
    depth = int(payload.get("depth", 3))
    return {
        "topic": topic,
        "outline": [f"{i+1}. {topic} — key point" for i in range(depth)],
        "next": "Pick a point to expand."
    }


def fast_style_guard(payload: Dict[str, Any]) -> Dict[str, Any]:
    text = payload.get("text", "")
    rules = [
        "Short sentences. Direct. No fluff.",
        "State action + reason.",
        "If uncertain, say so plainly."
    ]
    return {"rules": rules, "text": text}


# ============================================================
# Example boot (you'd wire this into Hermes)
# ============================================================
if __name__ == "__main__":
    audit = AuditChain(secret_key=b"hermes_sword_shield_dev")
    tokens = TokenVault()
    policy = PolicyEngine(human_required_over=50)
    response = ResponseEngine()

    organ = SwordShieldOrgan(audit, tokens, policy, response, mode="warrior")

    tok_id = tokens.issue("forge", caps=["tools_io", "render_forge"], ttl_ms=60_000, max_risk=40)

    ctx = {"recent_action_count_60s": 999, "zone": "tools_io"}
    signals = organ.evaluate_signals(ctx)
    print("signals:", [s.__dict__ for s in signals])

    actions = organ.propose_defense(signals)
    print("proposed (warrior mode):", [a.__dict__ for a in actions])

    out = organ.request_action(
        actor="hermes",
        action="isolate_zone",
        zone="tools_io",
        risk_score=45,
        token_id=tok_id,
        approvals={"hermes": True, "human": True},
        details={"trigger": "rate_anomaly"}
    )
    print("action result:", out)

    print("\n--- HermesRouter Demo ---")
    cache = TinyCache()
    metrics = Metrics()
    router = HermesRouter(
        cache=cache,
        metrics=metrics,
        sword_shield=None,
        fast_handlers={
            "outline": fast_outline,
            "style_guard": fast_style_guard,
        }
    )

    r1 = router.run(TaskRequest(name="outline", zone="ui", lane="FAST", payload={"topic": "Dragon-Scale", "depth": 5}))
    r2 = router.run(TaskRequest(name="outline", zone="ui", lane="FAST", payload={"topic": "Dragon-Scale", "depth": 5}))
    print("r1:", r1)
    print("r2 (cached):", r2)
    print("metrics:", metrics.summary())
