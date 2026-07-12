# ATLAS Motion Planning and Control Bible

**Primary AI:** Hermes  
**Supporting AIs:** Ajani, Minerva, ATLAS Council  
**Primary platforms:** The Weaver, humanoid systems, mobile robots, precision manipulators

## Mission

Define how ATLAS robots convert goals into safe, stable, efficient, and verifiable motion. Every motion command must be traceable from mission intent through planning, control, execution, feedback, and recovery.

## 1. Motion Architecture

The motion stack is divided into:

1. Mission intent
2. Task planning
3. Motion planning
4. Trajectory generation
5. Control
6. Actuation
7. Sensor feedback
8. Safety supervision
9. Recovery and logging

No planning layer may bypass safety supervision.

## 2. Coordinate Frames

Every motion record must identify:
- World frame
- Robot base frame
- Joint frames
- End-effector frame
- Tool center point
- Workpiece frame
- Sensor frames

Frame transforms must be versioned, timestamped, and validated. Undefined or stale transforms invalidate precision tasks.

## 3. Robot Models

Each robot model should define:
- Joint type and limits
- Link geometry
- Mass and inertia
- Velocity limits
- Acceleration limits
- Jerk limits
- Torque or force limits
- Collision geometry
- Tool payload
- Actuator characteristics
- Sensor availability

The Digital Twin is the authoritative configuration source for planning.

## 4. Kinematics

The system should support:
- Forward kinematics
- Inverse kinematics
- Jacobian analysis
- Singularity detection
- Reachability analysis
- Workspace mapping
- Redundancy resolution

Inverse-kinematics results must be checked against joint limits, collisions, singularities, and task constraints before execution.

## 5. Motion Planning

Planning methods may include:
- Joint-space planning
- Cartesian planning
- Sampling-based planning
- Search-based planning
- Optimization-based planning
- Constraint-aware planning
- Multi-arm coordination

Plans are evaluated for collision risk, clearance, duration, energy, smoothness, tool orientation, payload stability, and recovery options.

## 6. Trajectory Generation

A valid trajectory defines:
- Start and goal state
- Position profile
- Velocity profile
- Acceleration profile
- Jerk limits
- Timing
- Synchronization points
- Tolerances
- Abort conditions

Trajectories should be smooth enough to protect mechanisms, payloads, tools, and nearby people.

## 7. Control Systems

The control layer may include:
- Position control
- Velocity control
- Torque control
- Force control
- Impedance control
- Admittance control
- Hybrid force-position control
- Model-predictive control

The selected controller must match the robot, task, sensor quality, environment, and risk level.

## 8. Feedback and State Estimation

Feedback may include:
- Joint encoders
- Motor current
- Force/torque sensors
- IMUs
- Vision
- Tactile sensing
- Temperature
- Vibration
- External tracking

State estimates must report confidence and timestamp. Missing or contradictory feedback should trigger degraded operation or controlled stop.

## 9. Collision Avoidance

Collision checking covers:
- Self-collision
- Robot-to-tool collision
- Robot-to-fixture collision
- Robot-to-part collision
- Robot-to-robot collision
- Robot-to-human proximity
- Dynamic obstacles

Safety-critical collision prevention requires independent safeguards beyond the primary planner.

## 10. Multi-Arm Coordination

The Weaver requires shared-space coordination with:
- Workspace reservation
- Task ownership
- Tool awareness
- Temporal synchronization
- Deadlock prevention
- Dynamic replanning
- Safe fallback positions

One arm must never assume another arm completed a movement without verified state confirmation.

## 11. Mobile and Whole-Body Motion

For mobile robots and humanoids, planning should consider:
- Center of mass
- Support polygon
- Ground contact
- Terrain
- Foot placement
- Wheel or track constraints
- Balance recovery
- Manipulation while moving

Stable motion takes priority over speed.

## 12. Fault Detection and Recovery

Recoverable motion faults may include:
- Path obstruction
- Tracking error
- Joint limit approach
- Tool slip
- Lost localization
- Sensor dropout
- Actuator overheating
- Excess force

Recovery actions may include pause, retreat, replan, reduce speed, release load, return to safe pose, or request human review.

## 13. Safety States

Required motion states include:
- Disabled
- Homing
- Ready
- Executing
- Paused
- Degraded
- Recovering
- Safe stop
- Emergency stop
- Maintenance lockout

Transitions must be explicit, logged, and testable.

## 14. Minimum Software Contract

The initial implementation should provide interfaces for:
- Robot model registration
- Joint-state ingestion
- Forward and inverse kinematics
- Collision-scene updates
- Plan creation
- Trajectory validation
- Execution commands
- Pause, resume, and cancel
- Motion status
- Fault reporting
- Replay of executed trajectories

Suggested routes:
- `GET /api/motion/health`
- `GET /api/motion/robots`
- `POST /api/motion/robots`
- `POST /api/motion/kinematics/forward`
- `POST /api/motion/kinematics/inverse`
- `POST /api/motion/plans`
- `POST /api/motion/trajectories/validate`
- `POST /api/motion/executions`
- `POST /api/motion/executions/{id}/pause`
- `POST /api/motion/executions/{id}/cancel`
- `GET /api/motion/executions/{id}`
- `GET /api/motion/replay`

## 15. Verification Requirements

Acceptance requires:
- Joint limits enforced
- Invalid transforms rejected
- Collision checks demonstrated
- Trajectory limits validated
- Pause and cancel tested
- Fault recovery tested
- Multi-arm conflicts detected
- Deterministic simulation tests
- No physical hardware required for CI
- Complete execution logs

## Laboratory Program

1. Validate a two-joint arm model.
2. Solve forward and inverse kinematics.
3. Plan around a static obstacle.
4. Generate a jerk-limited trajectory.
5. Detect a simulated tracking error.
6. Coordinate two arms in a shared workspace.
7. Replay a complete motion mission.

## Hermes Motion Rules

- **MC-1:** A reachable goal is not automatically a safe goal.
- **MC-2:** Every trajectory must respect physical and operational limits.
- **MC-3:** Feedback overrides optimistic assumptions.
- **MC-4:** Recovery behavior is part of the design, not an afterthought.
- **MC-5:** Stable, explainable motion is more valuable than impressive motion.
