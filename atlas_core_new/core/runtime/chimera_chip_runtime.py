"""
Chimera Digital Chip Runtime (Software-Defined SoC for Your AIs)
----------------------------------------------------------------
Goal: Improve AI responsiveness + reliability + safety by running them on a "digital chip" runtime:
- 3-lane scheduler: LIVE / WORK / BACKGROUND
- Unified memory manager with quotas + priority
- Safety/Immune Watch: halt, quarantine, rollback (snapshots)
- Module interface standard + example modules (Ajani/Minerva/Hermes-style)
- Audit log for sensitive I/O

This does NOT copy any proprietary silicon. It's a new architecture using general principles.

Run:
  python chimera_chip_runtime.py
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import time
import uuid
import json
import copy


# -----------------------------
# Lanes (console-style budgets)
# -----------------------------
class Lane(str, Enum):
    LIVE = "live"            # UI, conversation, safety checks (low latency)
    WORK = "work"            # heavy compute (vision, generation, inference)
    BACKGROUND = "background"  # indexing, backups, training, compression


# -----------------------------
# Simple chip-like resources
# -----------------------------
@dataclass
class Budget:
    """Budgets are per tick. Keep LIVE snappy."""
    ms_per_tick_live: int = 12
    ms_per_tick_work: int = 18
    ms_per_tick_background: int = 8

    # Global caps (modeled)
    max_tasks_in_flight: int = 64
    max_total_mem_kb: int = 256_000  # "unified memory" size (model)
    max_io_ops_per_tick: int = 8     # rate limit


@dataclass
class TaskSpec:
    """A task is a packet of work routed to a module."""
    lane: Lane
    name: str
    module: str
    payload: Dict[str, Any] = field(default_factory=dict)

    # "chip-like" constraints (modeled)
    est_cost_ms: int = 3
    mem_kb: int = 128
    io_ops: int = 0

    # permissions for sensitive surfaces (modeled tokens/consent)
    needs_consent: bool = False
    time_token: Optional[str] = None  # simple token string
    audit_tag: Optional[str] = None

    # internal
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_ts: float = field(default_factory=time.time)


@dataclass
class TaskResult:
    task_id: str
    ok: bool
    output: Any = None
    error: Optional[str] = None
    elapsed_ms: int = 0


# -----------------------------
# Unified Memory (Apple-like concept, not implementation)
# -----------------------------
@dataclass
class MemoryBlock:
    block_id: str
    owner: str
    kb: int
    label: str
    created_ts: float = field(default_factory=time.time)
    data: Any = None


class UnifiedMemory:
    def __init__(self, max_total_kb: int):
        self.max_total_kb = max_total_kb
        self.blocks: Dict[str, MemoryBlock] = {}
        self.total_kb = 0

        # simple per-owner quotas (tune to taste)
        self.owner_quota_kb: Dict[str, int] = {
            "CROWN-CORE": int(max_total_kb * 0.25),
            "SPEAR-CORE": int(max_total_kb * 0.35),
            "TEMPLE-CACHE": int(max_total_kb * 0.25),
            "ARCHIVE-VAULT": int(max_total_kb * 0.15),
        }
        self.owner_usage_kb: Dict[str, int] = {}

    def _usage(self, owner: str) -> int:
        return self.owner_usage_kb.get(owner, 0)

    def alloc(self, owner: str, kb: int, label: str, data: Any = None) -> str:
        quota = self.owner_quota_kb.get(owner, self.max_total_kb)
        if self._usage(owner) + kb > quota:
            raise MemoryError(f"Owner quota exceeded: owner={owner}, req={kb}KB, usage={self._usage(owner)}KB, quota={quota}KB")
        if self.total_kb + kb > self.max_total_kb:
            raise MemoryError(f"Unified memory exceeded: req={kb}KB, total={self.total_kb}KB, max={self.max_total_kb}KB")

        block_id = str(uuid.uuid4())
        self.blocks[block_id] = MemoryBlock(block_id=block_id, owner=owner, kb=kb, label=label, data=data)
        self.total_kb += kb
        self.owner_usage_kb[owner] = self._usage(owner) + kb
        return block_id

    def free(self, block_id: str) -> None:
        b = self.blocks.pop(block_id, None)
        if not b:
            return
        self.total_kb -= b.kb
        self.owner_usage_kb[b.owner] = max(0, self._usage(b.owner) - b.kb)

    def snapshot(self) -> Dict[str, Any]:
        # For rollback: keep metadata, not huge payloads.
        return {
            "max_total_kb": self.max_total_kb,
            "total_kb": self.total_kb,
            "owner_usage_kb": copy.deepcopy(self.owner_usage_kb),
            "blocks_meta": {
                bid: {"owner": b.owner, "kb": b.kb, "label": b.label, "created_ts": b.created_ts}
                for bid, b in self.blocks.items()
            }
        }


# -----------------------------
# Audit log + permission fabric
# -----------------------------
@dataclass
class AuditEvent:
    ts: float
    task_id: str
    module: str
    tag: str
    details: Dict[str, Any] = field(default_factory=dict)


class PermissionFabric:
    """Simple modeled permission gate for sensitive tasks."""
    def __init__(self):
        self.consent_grants: Dict[str, bool] = {}  # e.g., {"camera": True}
        self.valid_tokens: Dict[str, float] = {}   # token -> expiry timestamp

    def set_consent(self, surface: str, granted: bool) -> None:
        self.consent_grants[surface] = granted

    def mint_token(self, ttl_sec: int = 60) -> str:
        token = str(uuid.uuid4())
        self.valid_tokens[token] = time.time() + ttl_sec
        return token

    def verify(self, needs_consent: bool, consent_surface: Optional[str], token: Optional[str]) -> Tuple[bool, str]:
        if needs_consent:
            if not consent_surface:
                return False, "missing consent surface"
            if not self.consent_grants.get(consent_surface, False):
                return False, f"consent not granted for: {consent_surface}"

        if token:
            exp = self.valid_tokens.get(token, 0.0)
            if time.time() > exp:
                return False, "token expired or invalid"

        return True, "ok"


# -----------------------------
# Module interface ("organs")
# -----------------------------
class ModuleState(str, Enum):
    OK = "ok"
    QUARANTINED = "quarantined"
    HALTED = "halted"


class ChimeraModule:
    """Standard interface all modules must implement."""
    name: str
    role: str  # "cpu", "accelerator", "cache", "io", "safety", "vault"

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.state = ModuleState.OK
        self.internal: Dict[str, Any] = {}  # safe internal state

    def health(self) -> Dict[str, Any]:
        return {"state": self.state.value, "role": self.role}

    def snapshot(self) -> Dict[str, Any]:
        # Snapshot must be small, deterministic
        return {"state": self.state.value, "internal": copy.deepcopy(self.internal)}

    def restore(self, snap: Dict[str, Any]) -> None:
        self.state = ModuleState(snap.get("state", "ok"))
        self.internal = copy.deepcopy(snap.get("internal", {}))

    def handle(self, task: TaskSpec, ctx: "ChipContext") -> Any:
        raise NotImplementedError


@dataclass
class ChipContext:
    memory: UnifiedMemory
    perms: PermissionFabric
    audit: List[AuditEvent]
    immutable_constitution: Dict[str, Any]
    # "global wires"
    safety_halt: bool = False


# -----------------------------
# IMMUNE-WATCH (Safety MCU)
# -----------------------------
class ImmuneWatch(ChimeraModule):
    def __init__(self):
        super().__init__("IMMUNE-WATCH", role="safety")
        self.internal = {
            "halt_reason": None,
            "quarantine": set(),
            "snapshots": {},  # module_name -> snapshot dict
            "rollback_count": 0,
            "max_rollbacks": 12,
        }

    def observe_and_enforce(self, modules: Dict[str, ChimeraModule], ctx: ChipContext) -> None:
        """Runs every tick. Enforces non-negotiable safety rules."""
        if self.state != ModuleState.OK:
            ctx.safety_halt = True
            self.internal["halt_reason"] = "immune_watch_not_ok"
            return

        # If we've exceeded rollback attempts, halt the whole system (safe failure)
        if self.internal["rollback_count"] > self.internal["max_rollbacks"]:
            ctx.safety_halt = True
            self.internal["halt_reason"] = "rollback_limit_exceeded"
            return

        # Quarantine enforcement
        for mn in list(self.internal["quarantine"]):
            if mn in modules:
                modules[mn].state = ModuleState.QUARANTINED

    def snapshot_all(self, modules: Dict[str, ChimeraModule], ctx: ChipContext) -> None:
        # Take snapshots of module states + memory meta
        snaps = {mn: m.snapshot() for mn, m in modules.items()}
        snaps["_unified_memory"] = ctx.memory.snapshot()
        self.internal["snapshots"] = snaps

    def rollback_module(self, module_name: str, modules: Dict[str, ChimeraModule], ctx: ChipContext) -> None:
        snaps = self.internal.get("snapshots", {})
        if module_name not in snaps:
            return
        modules[module_name].restore(snaps[module_name])
        self.internal["rollback_count"] += 1

    def quarantine(self, module_name: str, reason: str) -> None:
        self.internal["quarantine"].add(module_name)
        self.internal["halt_reason"] = f"quarantine:{module_name}:{reason}"

    def halt_everything(self, reason: str, ctx: ChipContext) -> None:
        ctx.safety_halt = True
        self.internal["halt_reason"] = reason

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        # IMMUNE-WATCH doesn't do normal tasks; it enforces policy.
        return {"ok": True, "note": "policy_enforced"}


# -----------------------------
# Example modules (Ajani/Minerva/Hermes style roles)
# -----------------------------
class CrownCore(ChimeraModule):
    """Decision CPU: low latency orchestration, planning, dialogue."""
    def __init__(self):
        super().__init__("CROWN-CORE", role="cpu")
        self.internal = {"ticks": 0, "last_intent": None}

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        if self.state != ModuleState.OK:
            raise RuntimeError("crown_core_not_ok")

        self.internal["ticks"] += 1
        if task.name == "decide_route":
            intent = task.payload.get("intent", "unknown")
            self.internal["last_intent"] = intent
            # A simple router suggestion (real system can be smarter)
            if intent in ("chat", "ui", "safety_check"):
                return {"lane": Lane.LIVE.value, "module": "CROWN-CORE"}
            if intent in ("vision", "heavy_reasoning", "generate"):
                return {"lane": Lane.WORK.value, "module": "SPEAR-CORE"}
            return {"lane": Lane.BACKGROUND.value, "module": "CROWN-CORE"}

        if task.name == "respond":
            # simulate low-latency response
            text = task.payload.get("text", "")
            return {"response": f"[Ajani/Crown] {text}".strip()}

        return {"ok": True, "note": f"crown handled {task.name}"}


class SpearCore(ChimeraModule):
    """Parallel accelerator: heavy compute (ML inference / generation / search)."""
    def __init__(self):
        super().__init__("SPEAR-CORE", role="accelerator")
        self.internal = {"jobs": 0}

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        if self.state != ModuleState.OK:
            raise RuntimeError("spear_core_not_ok")

        self.internal["jobs"] += 1
        if task.name == "infer":
            # pretend we did heavy math; allocate a result block in unified memory
            kb = max(64, task.mem_kb)
            block_id = ctx.memory.alloc(owner="SPEAR-CORE", kb=kb, label="inference_result", data={"score": 0.93})
            return {"result_block": block_id, "score": 0.93}

        if task.name == "generate":
            prompt = task.payload.get("prompt", "")
            # allocate larger working memory
            block_id = ctx.memory.alloc(owner="SPEAR-CORE", kb=task.mem_kb, label="gen_output", data={"text": f"Generated: {prompt[:80]}"})
            return {"output_block": block_id}

        return {"ok": True, "note": f"spear handled {task.name}"}


class TempleCache(ChimeraModule):
    """Working memory/cache: fast scratch for cross-module reuse."""
    def __init__(self):
        super().__init__("TEMPLE-CACHE", role="cache")
        self.internal = {"hits": 0, "misses": 0, "map": {}}

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        if self.state != ModuleState.OK:
            raise RuntimeError("temple_cache_not_ok")

        if task.name == "put":
            key = task.payload["key"]
            val = task.payload["value"]
            self.internal["map"][key] = val
            return {"ok": True}

        if task.name == "get":
            key = task.payload["key"]
            if key in self.internal["map"]:
                self.internal["hits"] += 1
                return {"hit": True, "value": self.internal["map"][key]}
            self.internal["misses"] += 1
            return {"hit": False}

        return {"ok": True, "note": f"cache handled {task.name}"}


class ArchiveVault(ChimeraModule):
    """Long memory + identity vault: versioned, signed updates only (modeled)."""
    def __init__(self):
        super().__init__("ARCHIVE-VAULT", role="vault")
        self.internal = {
            "identity_version": "1.0",
            "personality_hash": "locked",
            "versions": [],
            "sealed": True,
        }

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        if self.state != ModuleState.OK:
            raise RuntimeError("archive_vault_not_ok")

        if task.name == "read_identity":
            return {"identity_version": self.internal["identity_version"], "sealed": self.internal["sealed"]}

        if task.name == "propose_update":
            # proposals can be stored, but not applied without human authorization
            proposal = task.payload.get("proposal", {})
            self.internal["versions"].append({"ts": time.time(), "proposal": proposal})
            return {"stored": True, "note": "proposal stored; not applied (human key required)"}

        return {"ok": True, "note": f"vault handled {task.name}"}


class NerveBus(ChimeraModule):
    """Permissioned IO: no raw access, must have consent + token + audit."""
    def __init__(self):
        super().__init__("NERVE-BUS", role="io")
        self.internal = {"io_ops": 0}

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        if self.state != ModuleState.OK:
            raise RuntimeError("nerve_bus_not_ok")

        # enforce modeled permission checks
        consent_surface = task.payload.get("surface")
        ok, msg = ctx.perms.verify(task.needs_consent, consent_surface, task.time_token)

        if not ok:
            raise PermissionError(f"io_permission_denied:{msg}")

        # Audit
        tag = task.audit_tag or "io_event"
        ctx.audit.append(AuditEvent(ts=time.time(), task_id=task.task_id, module=self.name, tag=tag, details={"surface": consent_surface, "name": task.name}))
        self.internal["io_ops"] += 1

        # Return simulated IO result
        if task.name == "read_sensor":
            return {"surface": consent_surface, "value": 42}
        if task.name == "write_file":
            return {"ok": True, "bytes": task.payload.get("bytes", 0)}

        return {"ok": True, "note": "io_complete"}


class HeartPower(ChimeraModule):
    """Power/clock governance: modeled DVFS + thermal rules."""
    def __init__(self):
        super().__init__("HEART-POWER", role="power_clock")
        self.internal = {"mode": "balanced", "temp_c": 42, "throttle": False}

    def handle(self, task: TaskSpec, ctx: ChipContext) -> Any:
        if self.state != ModuleState.OK:
            raise RuntimeError("heart_power_not_ok")

        if task.name == "set_mode":
            mode = task.payload.get("mode", "balanced")
            if mode not in ("eco", "balanced", "performance"):
                return {"ok": False, "error": "bad_mode"}
            self.internal["mode"] = mode
            return {"ok": True, "mode": mode}

        if task.name == "tick_thermal":
            # simplistic temperature model
            load = task.payload.get("load", 0.2)
            self.internal["temp_c"] = min(95, int(self.internal["temp_c"] + 10 * load - 2))
            self.internal["throttle"] = self.internal["temp_c"] >= 80
            return {"temp_c": self.internal["temp_c"], "throttle": self.internal["throttle"]}

        return {"ok": True}


# -----------------------------
# Scheduler + Router (the "Chimera Chip")
# -----------------------------
class ChimeraScheduler:
    def __init__(self, budget: Budget):
        self.budget = budget
        self.queues: Dict[Lane, List[TaskSpec]] = {Lane.LIVE: [], Lane.WORK: [], Lane.BACKGROUND: []}
        self.in_flight: Dict[str, TaskSpec] = {}
        self.stats = {"ticks": 0, "completed": 0, "dropped": 0, "halted": 0}

    def submit(self, task: TaskSpec) -> bool:
        if len(self.in_flight) >= self.budget.max_tasks_in_flight:
            self.stats["dropped"] += 1
            return False
        self.queues[task.lane].append(task)
        self.in_flight[task.task_id] = task
        return True

    def pop_next(self, lane: Lane) -> Optional[TaskSpec]:
        q = self.queues[lane]
        if not q:
            return None
        # FIFO for predictability (console vibe)
        return q.pop(0)

    def _lane_budget_ms(self, lane: Lane) -> int:
        if lane == Lane.LIVE:
            return self.budget.ms_per_tick_live
        if lane == Lane.WORK:
            return self.budget.ms_per_tick_work
        return self.budget.ms_per_tick_background

    def tick(self, chip: "ChimeraChip") -> List[TaskResult]:
        """One scheduler tick. Always serves LIVE first."""
        self.stats["ticks"] += 1
        if chip.ctx.safety_halt:
            self.stats["halted"] += 1
            return []

        results: List[TaskResult] = []
        # Lane priority: LIVE -> WORK -> BACKGROUND
        for lane in (Lane.LIVE, Lane.WORK, Lane.BACKGROUND):
            lane_budget = self._lane_budget_ms(lane)
            start_lane = time.time()

            while True:
                if chip.ctx.safety_halt:
                    self.stats["halted"] += 1
                    return results

                elapsed_lane = int((time.time() - start_lane) * 1000)
                if elapsed_lane >= lane_budget:
                    break

                task = self.pop_next(lane)
                if not task:
                    break

                # rate-limit IO ops per tick (chip-wide)
                if task.io_ops > 0 and chip.io_ops_this_tick + task.io_ops > self.budget.max_io_ops_per_tick:
                    # push back to same lane to preserve order
                    self.queues[lane].insert(0, task)
                    break

                # execute
                res = chip.execute(task)
                results.append(res)

                # remove from inflight
                self.in_flight.pop(task.task_id, None)
                self.stats["completed"] += 1

        return results


class ChimeraChip:
    """
    The "digital chip" runtime:
    - Houses modules (organs)
    - Runs scheduler ticks
    - Enforces safety via IMMUNE-WATCH
    """
    def __init__(self, budget: Budget):
        self.budget = budget
        self.memory = UnifiedMemory(max_total_kb=budget.max_total_mem_kb)
        self.perms = PermissionFabric()
        self.audit: List[AuditEvent] = []

        # Constitution = immutable blueprint rules. Keep it read-only.
        self.constitution = {
            "human_key_required_for_identity_update": True,
            "permissioned_io_only": True,
            "no_raw_access": True,
            "rollback_limit": 12,
        }

        self.ctx = ChipContext(
            memory=self.memory,
            perms=self.perms,
            audit=self.audit,
            immutable_constitution=copy.deepcopy(self.constitution),
            safety_halt=False,
        )

        self.modules: Dict[str, ChimeraModule] = {
            "IMMUNE-WATCH": ImmuneWatch(),
            "CROWN-CORE": CrownCore(),
            "SPEAR-CORE": SpearCore(),
            "TEMPLE-CACHE": TempleCache(),
            "ARCHIVE-VAULT": ArchiveVault(),
            "NERVE-BUS": NerveBus(),
            "HEART-POWER": HeartPower(),
        }

        self.scheduler = ChimeraScheduler(budget=budget)
        self.io_ops_this_tick = 0

        # prime snapshots
        self.immune().snapshot_all(self.modules, self.ctx)
        self.immune().internal["max_rollbacks"] = self.constitution["rollback_limit"]

    def immune(self) -> ImmuneWatch:
        return self.modules["IMMUNE-WATCH"]  # type: ignore

    def health_report(self) -> Dict[str, Any]:
        return {mn: m.health() for mn, m in self.modules.items()}

    def route(self, intent: str) -> TaskSpec:
        """Ask CROWN-CORE where to route work (simple demonstration)."""
        decision = TaskSpec(lane=Lane.LIVE, name="decide_route", module="CROWN-CORE", payload={"intent": intent}, est_cost_ms=2)
        res = self.execute(decision)
        if not res.ok:
            return TaskSpec(lane=Lane.LIVE, name="respond", module="CROWN-CORE", payload={"text": "Routing failed; safe fallback."})

        lane = Lane(res.output["lane"])
        module = res.output["module"]
        return TaskSpec(lane=lane, name="respond", module=module, payload={"text": f"Intent routed to {module} on lane {lane.value}."})

    def execute(self, task: TaskSpec) -> TaskResult:
        """Execute one task with safety + rollback logic."""
        if self.ctx.safety_halt:
            return TaskResult(task_id=task.task_id, ok=False, error="system_halted", elapsed_ms=0)

        t0 = time.time()
        self.io_ops_this_tick += task.io_ops

        # IMMUNE-WATCH enforcement each task (fast policy checks)
        self.immune().observe_and_enforce(self.modules, self.ctx)
        if self.ctx.safety_halt:
            return TaskResult(task_id=task.task_id, ok=False, error=f"halted:{self.immune().internal.get('halt_reason')}", elapsed_ms=0)

        # Quarantined module cannot run
        mod = self.modules.get(task.module)
        if not mod:
            return TaskResult(task_id=task.task_id, ok=False, error=f"unknown_module:{task.module}", elapsed_ms=0)
        if mod.state == ModuleState.QUARANTINED:
            return TaskResult(task_id=task.task_id, ok=False, error=f"module_quarantined:{task.module}", elapsed_ms=0)

        # Try execute; on failure -> rollback module and/or quarantine
        try:
            # enforce "permissioned IO only" constitution
            if mod.role == "io" and self.ctx.immutable_constitution.get("permissioned_io_only", True):
                if not task.needs_consent:
                    raise PermissionError("io_tasks_must_require_consent_in_this_model")

            out = mod.handle(task, self.ctx)

            elapsed = int((time.time() - t0) * 1000)
            return TaskResult(task_id=task.task_id, ok=True, output=out, elapsed_ms=elapsed)

        except PermissionError as e:
            # Permission violations are serious: quarantine IO module briefly
            self.immune().quarantine(task.module, reason=str(e))
            # snapshot + rollback to last safe state
            self.immune().rollback_module(task.module, self.modules, self.ctx)
            elapsed = int((time.time() - t0) * 1000)
            return TaskResult(task_id=task.task_id, ok=False, error=f"permission_error:{e}", elapsed_ms=elapsed)

        except MemoryError as e:
            # Memory pressure: rollback SPEAR or CACHE as needed, then continue
            self.immune().rollback_module(task.module, self.modules, self.ctx)
            elapsed = int((time.time() - t0) * 1000)
            return TaskResult(task_id=task.task_id, ok=False, error=f"memory_error:{e}", elapsed_ms=elapsed)

        except Exception as e:
            # Generic failures: rollback, then quarantine if repeated
            self.immune().rollback_module(task.module, self.modules, self.ctx)
            # if too many rollbacks, halt system
            if self.immune().internal["rollback_count"] > self.immune().internal["max_rollbacks"]:
                self.immune().halt_everything("too_many_failures", self.ctx)
            elapsed = int((time.time() - t0) * 1000)
            return TaskResult(task_id=task.task_id, ok=False, error=f"error:{type(e).__name__}:{e}", elapsed_ms=elapsed)

    def tick(self) -> List[TaskResult]:
        """One runtime tick: reset IO ops, take snapshot, run scheduled tasks."""
        self.io_ops_this_tick = 0

        # thermal tick modeled
        thermal = TaskSpec(lane=Lane.LIVE, name="tick_thermal", module="HEART-POWER", payload={"load": 0.25}, est_cost_ms=1)
        _ = self.execute(thermal)

        # snapshot at start of tick for rollback reference
        self.immune().snapshot_all(self.modules, self.ctx)

        # enforce policy once per tick
        self.immune().observe_and_enforce(self.modules, self.ctx)
        if self.ctx.safety_halt:
            return []

        return self.scheduler.tick(self)

    def export_state(self) -> Dict[str, Any]:
        return {
            "health": self.health_report(),
            "scheduler": self.scheduler.stats,
            "immune": copy.deepcopy(self.immune().internal),
            "memory": self.memory.snapshot(),
            "audit_tail": [asdict(a) for a in self.audit[-10:]],
        }


# -----------------------------
# Demo: "Chimera chip improves AI feel"
# -----------------------------
def demo():
    chip = ChimeraChip(budget=Budget())

    # Grant consent for a modeled surface and mint a token
    chip.perms.set_consent("camera", True)
    token = chip.perms.mint_token(ttl_sec=30)

    # Submit tasks: LIVE chat, WORK generation, IO sensor read (permissioned), BACKGROUND vault proposal
    chip.scheduler.submit(TaskSpec(
        lane=Lane.LIVE, name="respond", module="CROWN-CORE",
        payload={"text": "Low-latency response: no lag."}, est_cost_ms=2, mem_kb=64
    ))

    chip.scheduler.submit(TaskSpec(
        lane=Lane.WORK, name="generate", module="SPEAR-CORE",
        payload={"prompt": "Design a safe regenerative AI chip architecture."},
        est_cost_ms=12, mem_kb=2048
    ))

    chip.scheduler.submit(TaskSpec(
        lane=Lane.LIVE, name="read_sensor", module="NERVE-BUS",
        payload={"surface": "camera"}, est_cost_ms=3, mem_kb=128,
        io_ops=1, needs_consent=True, time_token=token, audit_tag="camera_read"
    ))

    chip.scheduler.submit(TaskSpec(
        lane=Lane.BACKGROUND, name="propose_update", module="ARCHIVE-VAULT",
        payload={"proposal": {"personality_tuning": "minor", "note": "Store only. Human key required."}},
        est_cost_ms=4, mem_kb=128
    ))

    # Run a few ticks
    for i in range(3):
        results = chip.tick()
        print(f"\n=== TICK {i} ===")
        for r in results:
            print(json.dumps(asdict(r), indent=2, default=str))

        print("\nSTATE (tail):")
        print(json.dumps(chip.export_state(), indent=2, default=str))

    # Try a forbidden IO task (no consent flag) to demonstrate immune quarantine
    print("\n=== FORBIDDEN IO TEST ===")
    bad = TaskSpec(
        lane=Lane.LIVE, name="read_sensor", module="NERVE-BUS",
        payload={"surface": "camera"},
        io_ops=1, needs_consent=False, time_token=None, audit_tag="raw_attempt"
    )
    res = chip.execute(bad)
    print(json.dumps(asdict(res), indent=2, default=str))
    print("\nSTATE AFTER VIOLATION:")
    print(json.dumps(chip.export_state(), indent=2, default=str))


if __name__ == "__main__":
    demo()
