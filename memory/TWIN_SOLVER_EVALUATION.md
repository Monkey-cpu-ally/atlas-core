# Digital Twin Solver Evaluation — OpenFOAM / FEniCS
_Engineering memo · 2026-06-18 · author: ATLAS Core_

## Verdict

| Solver | Verdict | Why |
|---|---|---|
| **OpenFOAM**  | ❌ Do not bundle into ATLAS containers | Hard system dependency (`paraview-data` ~ 1.4 GB, `openmpi`, custom kernel mounts). Boots cleanly only inside a privileged Docker image OR on bare Linux with `apt install openfoam2312`. Run-time per CFD case is 10 min → 4 hours. Will starve the FastAPI event loop and exceed Kubernetes per-pod memory caps. |
| **FEniCSx** (`dolfinx`) | ❌ Do not bundle directly | Requires `mpi4py` + `petsc4py` + `slepc4py` + `pyvista` (PETSc alone is 300 MB compiled). Same Kubernetes & runtime concerns as OpenFOAM. |
| **External solver service** (recommended) | ✅ Adopt | Decouple solver execution from the ATLAS API pod. ATLAS submits jobs over HTTP, the solver pod (or LAN workstation) processes asynchronously, ATLAS polls/streams results back into `twin_simulations` collection. |
| **Lightweight in-process solvers** | ✅ Adopt | `scipy.integrate.solve_ivp` for ODE-shaped problems (battery thermals, motor dynamics). `pychrono` (rigid-body multibody) is small and pip-installable. Good fit when the architect wants something better than the current heuristic engines but doesn't need finite-element fidelity. |

## Rationale

### Container & runtime constraints

ATLAS runs as a single Kubernetes pod with these effective limits:
- 9.8 GB disk total (currently ~3 GB used)
- ~2 GB RAM budget for the FastAPI process
- No `sudo`, no privileged Docker, no GPU drivers
- 120 s foreground bash timeout, so a long solver run blocks the API

Installing OpenFOAM requires:

```
apt install openfoam2312        # 2.1 GB + 700 MB binaries
                                # also pulls openmpi, paraview-data
```

This blows the disk budget and would still fail because the
`hyperthreading` and kernel-AIO requirements aren't met inside a
multi-tenant pod.

`fenicsx` is more pip-friendly but pulls `petsc4py` (300 MB compiled),
`slepc4py`, `mpi4py`, `pyvista` (visualisation), each of which fails
the cgroup memory limit during build.

### Where physics fidelity actually matters

Re-reading the architect's intent in `/app/memory/PRD.md` and the
existing twin simulator (6 engines: BLUEPRINT / ASSEMBLY / RESOURCE /
FAILURE / TIMELINE / COST), the gap is **not** "we need Navier-Stokes
for our twins". The gap is:

1. **ODE-level dynamics** for battery thermal runaway, motor
   torque-vs-RPM, plant biology growth curves.
2. **Multibody kinematics** for robotic arms / rovers (pre-flight
   pathing verification).
3. **Environmental compatibility** (e.g. "drone tuned for 9.81 m/s²
   gravity put in a lunar environment doc → flag mismatch").

Cases 1 + 2 are solvable with `scipy` + `pychrono`. Case 3 is solved
by the new `TwinEnvironment` registry + `bind_twin` compatibility
checker shipped in Phase D2.

### Concrete next step (when fidelity is actually demanded)

Spin up an **external solver pod** on the same LAN with these contents:

```
solver-pod/
  Dockerfile               # `apt install openfoam2312` + `pip install fenics-dolfinx`
  worker.py                # consumes ATLAS jobs from `/api/twins/solver/jobs`
  cases/                   # OpenFOAM case templates per twin category
```

ATLAS already has the contract pieces it needs:

- `digital_twin.run_and_persist_simulation` writes results into
  `twin_simulations` regardless of who computed them.
- `SimulationResult` carries `findings/warnings/failures/metrics` —
  the same shape an OpenFOAM post-processor can emit.
- The new `TwinEnvironment` doc gives the solver the ambient
  conditions it needs (gravity, temperature, density).

A future endpoint `POST /api/twins/solver/jobs` would push a job to the
external worker; `GET /api/twins/solver/jobs/{id}` would poll. No
in-process solver, no Kubernetes budget overrun.

## Action items

| # | Action | Owner | Status |
|---|---|---|---|
| 1 | Implement `TwinEnvironment` registry + AABB obstacles + compatibility checker | ATLAS Core | ✅ DONE (Phase D2) |
| 2 | Seed 5 realistic environments (lab/outdoor/aerial/aquatic/lunar) | ATLAS Core | ✅ DONE (Phase D2) |
| 3 | Wire `bind_twin` / `unbind` endpoints | ATLAS Core | ✅ DONE (Phase D2) |
| 4 | Add `scipy.integrate.solve_ivp`-based ODE engine to `twin_simulator` (battery thermal, motor torque, biology growth) | ATLAS Core | 🟡 Future, when first concrete case lands |
| 5 | External solver pod (OpenFOAM / FEniCS) | Architect | 🔴 Hold — only build when a twin actually needs CFD/FEM |
| 6 | UI: HUD panel for environments + twin binding | Frontend | 🔴 Hold — after audit cycle |

## TL;DR

> OpenFOAM and FEniCS are excellent solvers — but they belong on
> their own pod, not bundled into the ATLAS API container. For
> 90 % of the foreseeable use-cases the new `TwinEnvironment`
> registry + the existing six heuristic engines + a future
> `scipy.integrate.solve_ivp`-based ODE engine cover the load.
> When a twin truly needs CFD/FEM, the contract to stream results
> back into `twin_simulations` from an external worker is already
> in place.
