"""
Twin simulator — Phase 5.

Six lightweight, pure-Python simulation engines. No physics solver: each
engine inspects the twin's spec, applies domain rules, and returns a
SimulationResult with findings/warnings/failures/metrics. The architect
gets a fast, deterministic, explainable assessment that the council can
then deliberate on.

Engine list:
  BLUEPRINT — structural completeness: required fields, dependency sanity,
              no cycles, all dependency endpoints exist.
  ASSEMBLY  — topo-sort assembly order; total estimated time from
              component lead_time_days; identifies blocking components.
  RESOURCE  — bill of materials, energy budget vs. supply.
  FAILURE   — single-points-of-failure (no redundancy), unsourced energy,
              critical missing sensors.
  TIMELINE  — critical-path estimate (longest dep chain × lead times).
  COST      — Σ(quantity · cost_per_unit) + 20% labour heuristic.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any, Dict, List, Set, Tuple

from models.twin_models import (
    DigitalTwin,
    SimulationKind,
    SimulationResult,
    TwinCategory,
)

# Categories that *require* at least one sensor input to be considered complete.
_CATEGORIES_NEEDING_SENSORS: Set[TwinCategory] = {
    TwinCategory.ROBOT,
    TwinCategory.VEHICLE,
    TwinCategory.MANUFACTURING_SYSTEM,
    TwinCategory.POWER_SYSTEM,
}


def simulate(twin: DigitalTwin, kind: SimulationKind) -> SimulationResult:
    """Dispatch to the right engine and wrap the bookkeeping fields."""
    dispatch = {
        SimulationKind.BLUEPRINT: _sim_blueprint,
        SimulationKind.ASSEMBLY:  _sim_assembly,
        SimulationKind.RESOURCE:  _sim_resource,
        SimulationKind.FAILURE:   _sim_failure,
        SimulationKind.TIMELINE:  _sim_timeline,
        SimulationKind.COST:      _sim_cost,
        SimulationKind.THERMAL:   _sim_thermal,
    }
    engine = dispatch[kind]
    findings, warnings, failures, metrics, extras = engine(twin)
    score = _score(failures, warnings, metrics)
    return SimulationResult(
        twin_id=twin.id,
        revision=twin.state.revision,
        kind=kind,
        ok=(not failures),
        score=score,
        findings=findings,
        warnings=warnings,
        failures=failures,
        metrics=metrics,
        timeline=extras.get("timeline"),
        bom=extras.get("bom"),
    )


# --- Engine: BLUEPRINT -----------------------------------------------------
def _sim_blueprint(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    findings, warnings, failures = [], [], []
    metrics: Dict[str, Any] = {}

    state = twin.state
    component_ids = {c.id for c in state.components}
    metrics["component_count"] = len(state.components)
    metrics["dependency_count"] = len(state.dependencies)

    if not state.components:
        failures.append("No components defined — blueprint is empty.")
    else:
        findings.append(f"{len(state.components)} components, {len(state.dependencies)} dependencies.")

    # Dependency endpoints must exist.
    bad_refs = [
        f"{d.from_component}→{d.to_component}"
        for d in state.dependencies
        if d.from_component not in component_ids or d.to_component not in component_ids
    ]
    if bad_refs:
        failures.append("Dependencies reference unknown components: " + ", ".join(bad_refs[:5]))

    # No cycles.
    if _has_cycle(state.dependencies):
        failures.append("Circular dependency detected — assembly cannot be ordered.")
    else:
        findings.append("Dependency graph is acyclic.")

    # Category-specific requirements.
    if twin.category in _CATEGORIES_NEEDING_SENSORS and not state.sensor_inputs:
        warnings.append(
            f"{twin.category.value} typically requires sensor inputs — none defined."
        )

    if not state.dimensions:
        warnings.append("Dimensions not specified — downstream sims will use defaults.")
    if not state.energy:
        warnings.append("Energy profile not specified — RESOURCE sim will be limited.")

    return findings, warnings, failures, metrics, {}


# --- Engine: ASSEMBLY ------------------------------------------------------
def _sim_assembly(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    findings, warnings, failures = [], [], []
    metrics: Dict[str, Any] = {}
    state = twin.state
    if not state.components:
        failures.append("No components to assemble.")
        return findings, warnings, failures, metrics, {}

    order = _topological_order(state)
    if order is None:
        failures.append("Cyclic dependencies — no assembly order exists.")
        return findings, warnings, failures, metrics, {}

    name_by_id = {c.id: c.name for c in state.components}
    lead_by_id = {c.id: float(c.lead_time_days or 0.0) for c in state.components}
    steps: List[Dict[str, Any]] = []
    total_serial_days = 0.0
    for step_idx, cid in enumerate(order, start=1):
        days = lead_by_id.get(cid, 0.0)
        steps.append({
            "step": step_idx,
            "component_id": cid,
            "component": name_by_id.get(cid, cid),
            "lead_time_days": days,
        })
        total_serial_days += days
    metrics["assembly_steps"] = len(steps)
    metrics["total_serial_lead_days"] = round(total_serial_days, 2)
    findings.append(
        f"Assembly ordered in {len(steps)} steps; serial lead time ≈ {total_serial_days:.1f} days."
    )
    # Components with zero/unknown lead are likely under-specified.
    unknown_lead = [name_by_id[s["component_id"]] for s in steps if s["lead_time_days"] <= 0]
    if unknown_lead:
        warnings.append(
            f"{len(unknown_lead)} component(s) have no lead_time_days: "
            + ", ".join(unknown_lead[:5])
        )
    return findings, warnings, failures, metrics, {"timeline": steps}


# --- Engine: RESOURCE ------------------------------------------------------
def _sim_resource(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    findings, warnings, failures = [], [], []
    metrics: Dict[str, Any] = {}
    state = twin.state
    if not state.components:
        failures.append("No components — nothing to source.")
        return findings, warnings, failures, metrics, {}

    bom: List[Dict[str, Any]] = []
    total_mass = 0.0
    for c in state.components:
        bom.append({
            "component": c.name,
            "material": c.material or "—",
            "quantity": c.quantity,
            "unit": c.unit,
            "mass_kg": (c.mass_kg or 0.0) * c.quantity,
        })
        total_mass += (c.mass_kg or 0.0) * c.quantity

    metrics["total_mass_kg"] = round(total_mass, 3)
    metrics["material_count"] = len({c.material for c in state.components if c.material})
    metrics["bom_line_count"] = len(bom)

    findings.append(
        f"BOM has {len(bom)} lines · {metrics['material_count']} distinct materials · "
        f"total mass ≈ {total_mass:.2f} kg."
    )

    if state.energy:
        avg = state.energy.average_w or 0.0
        daily = state.energy.daily_wh or (avg * 24.0)
        metrics["energy_daily_wh"] = round(daily, 2)
        if state.energy.source:
            findings.append(
                f"Energy: avg={avg} W · daily≈{daily:.0f} Wh · source='{state.energy.source}'."
            )
        else:
            warnings.append("Energy source not specified — supply assumed.")
    else:
        warnings.append("No energy profile; assume grid-tied for now.")

    return findings, warnings, failures, metrics, {"bom": bom}


# --- Engine: FAILURE -------------------------------------------------------
def _sim_failure(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    findings, warnings, failures = [], [], []
    metrics: Dict[str, Any] = {}
    state = twin.state
    if not state.components:
        failures.append("No components — cannot assess failure modes.")
        return findings, warnings, failures, metrics, {}

    # In-degree count: a component on which many others depend is high-stakes.
    in_deg: Dict[str, int] = defaultdict(int)
    out_deg: Dict[str, int] = defaultdict(int)
    for d in state.dependencies:
        in_deg[d.to_component] += 1
        out_deg[d.from_component] += 1

    # SPOF rule: a component that POWERS / MOUNTS / FEEDS many others is
    # high-stakes if it fails. In our dep graph the arrow points from the
    # provider to the consumer (e.g. battery→motor means battery powers
    # motor), so a high *out-degree* indicates a high-fan-out single point
    # of failure.
    name_by_id = {c.id: c.name for c in state.components}
    spofs = [name_by_id[cid] for cid, deg in out_deg.items() if deg >= 2]
    if spofs:
        warnings.append(
            f"{len(spofs)} potential single-points-of-failure (fan-out ≥ 2 dependents): "
            + ", ".join(spofs[:6])
        )
        metrics["spof_count"] = len(spofs)
    else:
        findings.append("No high-fan-out single-points-of-failure detected.")
        metrics["spof_count"] = 0

    if twin.category in _CATEGORIES_NEEDING_SENSORS and not state.sensor_inputs:
        failures.append("Mission-critical category has zero sensor inputs — no fault detection possible.")

    if state.energy and (state.energy.peak_w or 0) > (state.energy.average_w or 0) * 3:
        warnings.append(
            "Peak power > 3× average — thermal/transient failure risk if PSU undersized."
        )

    # Components with no dependents and no outputs may be dead-weight.
    orphans = [
        name_by_id[c.id] for c in state.components
        if in_deg.get(c.id, 0) == 0 and out_deg.get(c.id, 0) == 0 and len(state.components) > 1
    ]
    if orphans:
        warnings.append(
            f"{len(orphans)} orphan component(s) with no dependencies in either direction: "
            + ", ".join(orphans[:5])
        )

    return findings, warnings, failures, metrics, {}


# --- Engine: TIMELINE ------------------------------------------------------
def _sim_timeline(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    findings, warnings, failures = [], [], []
    metrics: Dict[str, Any] = {}
    state = twin.state
    if not state.components:
        failures.append("No components — no timeline.")
        return findings, warnings, failures, metrics, {}

    order = _topological_order(state)
    if order is None:
        failures.append("Cyclic dependencies — no critical path.")
        return findings, warnings, failures, metrics, {}

    lead_by_id = {c.id: float(c.lead_time_days or 0.0) for c in state.components}
    name_by_id = {c.id: c.name for c in state.components}
    preds: Dict[str, List[str]] = defaultdict(list)
    for d in state.dependencies:
        preds[d.to_component].append(d.from_component)

    # Earliest-finish time per node — longest-path DP over the dep DAG.
    eft: Dict[str, float] = {}
    for cid in order:
        max_pred = max((eft[p] for p in preds[cid] if p in eft), default=0.0)
        eft[cid] = max_pred + lead_by_id.get(cid, 0.0)
    critical_finish = max(eft.values(), default=0.0)
    metrics["critical_path_days"] = round(critical_finish, 2)

    # Reconstruct the critical path (any one path with the max finish).
    timeline: List[Dict[str, Any]] = []
    cur = max(eft, key=eft.get) if eft else None
    chain: List[str] = []
    while cur is not None:
        chain.append(cur)
        candidates = [p for p in preds[cur] if eft.get(p, -1) == eft[cur] - lead_by_id.get(cur, 0.0)]
        cur = candidates[0] if candidates else None
    for i, cid in enumerate(reversed(chain), start=1):
        timeline.append({
            "step": i,
            "component_id": cid,
            "component": name_by_id.get(cid, cid),
            "lead_time_days": lead_by_id.get(cid, 0.0),
            "earliest_finish_day": round(eft.get(cid, 0.0), 2),
            "on_critical_path": True,
        })
    findings.append(
        f"Critical path: {len(timeline)} components, total ≈ {critical_finish:.1f} days."
    )
    return findings, warnings, failures, metrics, {"timeline": timeline}


# --- Engine: COST ----------------------------------------------------------
LABOUR_OVERHEAD = 0.20    # 20% of materials cost as labour heuristic


def _sim_cost(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    findings, warnings, failures = [], [], []
    metrics: Dict[str, Any] = {}
    state = twin.state
    if not state.components:
        failures.append("No components — cannot estimate cost.")
        return findings, warnings, failures, metrics, {}

    materials_cost = 0.0
    priced = unpriced = 0
    bom: List[Dict[str, Any]] = []
    for c in state.components:
        if c.cost_per_unit is None:
            unpriced += 1
            line_cost = 0.0
        else:
            priced += 1
            line_cost = c.quantity * c.cost_per_unit
            materials_cost += line_cost
        bom.append({
            "component": c.name,
            "quantity": c.quantity,
            "cost_per_unit": c.cost_per_unit,
            "line_cost": round(line_cost, 2),
        })

    labour = materials_cost * LABOUR_OVERHEAD
    total = materials_cost + labour
    metrics.update({
        "materials_cost": round(materials_cost, 2),
        "labour_estimate": round(labour, 2),
        "total_estimate": round(total, 2),
        "components_priced": priced,
        "components_unpriced": unpriced,
    })
    findings.append(
        f"Materials ≈ {materials_cost:.2f}; labour ≈ {labour:.2f}; "
        f"TOTAL ≈ {total:.2f} ({priced} priced / {unpriced} unpriced)."
    )
    if unpriced:
        warnings.append(
            f"{unpriced} component(s) have no cost_per_unit — estimate is a lower bound."
        )
    return findings, warnings, failures, metrics, {"bom": bom}


# --- Internals -------------------------------------------------------------
def _topological_order(state) -> List[str] | None:
    in_deg: Dict[str, int] = defaultdict(int)
    succ: Dict[str, List[str]] = defaultdict(list)
    nodes: Set[str] = {c.id for c in state.components}
    for d in state.dependencies:
        if d.from_component in nodes and d.to_component in nodes:
            succ[d.from_component].append(d.to_component)
            in_deg[d.to_component] += 1
    q = deque([n for n in nodes if in_deg[n] == 0])
    order: List[str] = []
    while q:
        n = q.popleft()
        order.append(n)
        for m in succ[n]:
            in_deg[m] -= 1
            if in_deg[m] == 0:
                q.append(m)
    if len(order) != len(nodes):
        return None
    return order


def _has_cycle(deps) -> bool:
    # Build a temporary node set from the deps themselves.
    nodes: Set[str] = set()
    succ: Dict[str, List[str]] = defaultdict(list)
    in_deg: Dict[str, int] = defaultdict(int)
    for d in deps:
        nodes.add(d.from_component)
        nodes.add(d.to_component)
        succ[d.from_component].append(d.to_component)
        in_deg[d.to_component] += 1
    if not nodes:
        return False
    q = deque([n for n in nodes if in_deg[n] == 0])
    visited = 0
    while q:
        n = q.popleft()
        visited += 1
        for m in succ[n]:
            in_deg[m] -= 1
            if in_deg[m] == 0:
                q.append(m)
    return visited != len(nodes)


def _score(failures: List[str], warnings: List[str], metrics: Dict[str, Any]) -> float:
    """Compress findings into a 0..1 quality score:
       1 = no warnings, no failures; each failure −0.4, each warning −0.10."""
    s = 1.0 - 0.4 * len(failures) - 0.10 * len(warnings)
    return max(0.0, min(1.0, round(s, 3)))


# --- Engine: THERMAL (scipy.integrate.solve_ivp ODE) -----------------------
def _sim_thermal(twin: DigitalTwin) -> Tuple[List[str], List[str], List[str], Dict, Dict]:
    """Lumped-mass thermal simulation for power-cell / battery twins.

    State: temperature T(t) of the cell core, single lumped node.
    ODE:   dT/dt = (I²·R_int + Q_self) / (m·Cp) - h·A·(T - T_amb) / (m·Cp)

    Inputs (read from twin.state.integrations.thermal, with safe defaults):
        I_amps          discharge current     (default 2.0)
        R_int_ohm       internal resistance   (default 0.04 — typical Li-ion 18650 cell)
        m_kg            cell mass             (default 0.046 — 18650)
        Cp_j_kg_k       specific heat         (default 900  — Li-ion average)
        h_w_m2_k        convective coefficient (default 15 — natural air)
        A_m2            surface area          (default 0.0042 — 18650)
        T_amb_c         ambient temperature   (default 25)
        T_init_c        starting cell temp    (default 25)
        Q_self_w        side-reaction heat    (default 0.0  — non-zero for Li-S, SS)
        chemistry       'li_ion' | 'solid_state' | 'lis'
        thermal_runaway_threshold_c   (default 80 for li_ion, 100 for solid_state)
        duration_s      (default 1800 — 30 min)
    """
    import numpy as _np
    try:
        from scipy.integrate import solve_ivp
    except ImportError:
        return ([], [], ["scipy not installed — THERMAL sim unavailable"], {}, {})

    findings: List[str] = []
    warnings: List[str] = []
    failures: List[str] = []

    integrations = (twin.state.integrations or {}) if hasattr(twin.state, "integrations") else {}
    cfg = dict(integrations.get("thermal") or {})

    chem = cfg.get("chemistry", "li_ion")
    defaults_by_chem = {
        "li_ion":      {"R_int_ohm": 0.04,  "Cp_j_kg_k": 900,  "Q_self_w": 0.0,
                        "thermal_runaway_threshold_c": 80.0},
        "solid_state": {"R_int_ohm": 0.025, "Cp_j_kg_k": 850,  "Q_self_w": 0.0,
                        "thermal_runaway_threshold_c": 100.0},
        "lis":         {"R_int_ohm": 0.07,  "Cp_j_kg_k": 950,  "Q_self_w": 0.05,
                        "thermal_runaway_threshold_c": 90.0},
    }
    chem_def = defaults_by_chem.get(chem, defaults_by_chem["li_ion"])

    p = {
        "I_amps":   float(cfg.get("I_amps", 2.0)),
        "R_int":    float(cfg.get("R_int_ohm", chem_def["R_int_ohm"])),
        "m_kg":     float(cfg.get("m_kg", 0.046)),
        "Cp":       float(cfg.get("Cp_j_kg_k", chem_def["Cp_j_kg_k"])),
        "h":        float(cfg.get("h_w_m2_k", 15.0)),
        "A":        float(cfg.get("A_m2", 0.0042)),
        "T_amb":    float(cfg.get("T_amb_c", 25.0)),
        "T_init":   float(cfg.get("T_init_c", 25.0)),
        "Q_self":   float(cfg.get("Q_self_w", chem_def["Q_self_w"])),
        "runaway":  float(cfg.get("thermal_runaway_threshold_c",
                                  chem_def["thermal_runaway_threshold_c"])),
    }
    duration = float(cfg.get("duration_s", 1800.0))

    # Heat capacity total
    C = p["m_kg"] * p["Cp"]
    if C <= 0:
        failures.append("invalid thermal mass × Cp — must be > 0")
        return findings, warnings, failures, {}, {}

    # ODE: dT/dt = (I²·R + Q_self - h·A·(T - T_amb)) / C
    Q_joule = p["I_amps"] ** 2 * p["R_int"]                 # W
    def rhs(_t: float, T_arr: _np.ndarray) -> _np.ndarray:
        T = T_arr[0]
        dTdt = (Q_joule + p["Q_self"] - p["h"] * p["A"] * (T - p["T_amb"])) / C
        return [dTdt]

    # Integrate
    t_span = (0.0, duration)
    sol = solve_ivp(
        rhs, t_span, [p["T_init"]],
        max_step=max(1.0, duration / 200.0),
        dense_output=False, rtol=1e-4, atol=1e-3,
    )
    if not sol.success:
        failures.append(f"ODE solver failed: {sol.message}")
        return findings, warnings, failures, {}, {}

    T_traj = sol.y[0]
    T_final = float(T_traj[-1])
    T_max = float(T_traj.max())
    t_at_max = float(sol.t[int(T_traj.argmax())])
    T_steady_state = p["T_amb"] + (Q_joule + p["Q_self"]) / (p["h"] * p["A"])

    metrics = {
        "chemistry": chem,
        "duration_s": duration,
        "joule_heat_w": round(Q_joule, 3),
        "side_reaction_w": p["Q_self"],
        "convective_loss_max_w": round(p["h"] * p["A"] * (T_max - p["T_amb"]), 3),
        "T_init_c": p["T_init"],
        "T_amb_c": p["T_amb"],
        "T_final_c": round(T_final, 2),
        "T_max_c": round(T_max, 2),
        "t_at_max_s": round(t_at_max, 1),
        "T_steady_state_c": round(T_steady_state, 2),
        "thermal_runaway_threshold_c": p["runaway"],
        "headroom_to_runaway_c": round(p["runaway"] - T_max, 2),
        "ode_points": int(sol.t.size),
    }

    if T_max >= p["runaway"]:
        failures.append(
            f"THERMAL RUNAWAY · T_max {T_max:.1f} °C ≥ threshold {p['runaway']} °C "
            f"at t={t_at_max:.0f}s (chemistry={chem})"
        )
    elif T_max >= p["runaway"] - 10:
        warnings.append(
            f"Thermal headroom low · T_max {T_max:.1f} °C, threshold {p['runaway']} °C — "
            "consider larger heatsink or lower duty cycle."
        )
    if T_steady_state > 60:
        warnings.append(
            f"Steady-state {T_steady_state:.0f} °C is high — long missions at this load "
            "will degrade cycle life."
        )

    findings.append(
        f"ODE-integrated thermal sim · chemistry={chem} · {duration:.0f}s · "
        f"T_init={p['T_init']}°C → T_max={T_max:.1f}°C → T_final={T_final:.1f}°C"
    )

    # Compact timeline sample (10 evenly-spaced points)
    n = T_traj.size
    if n > 10:
        idx = _np.linspace(0, n - 1, 10).astype(int)
    else:
        idx = list(range(n))
    timeline = [
        {"t_s": round(float(sol.t[i]), 1), "T_c": round(float(T_traj[i]), 2)}
        for i in idx
    ]

    return findings, warnings, failures, metrics, {"timeline": timeline}
