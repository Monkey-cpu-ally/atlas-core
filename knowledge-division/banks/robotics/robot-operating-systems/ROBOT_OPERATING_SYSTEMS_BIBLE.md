# ATLAS Robot Operating Systems Bible

**Primary AI:** Hermes  
**Supporting AIs:** Ajani, Minerva, ATLAS Council  
**Primary platforms:** The Weaver, humanoid systems, mobile robots, inspection cells, field robots

## Mission

Define the software foundation that connects AtlasOS, robot hardware, perception, planning, control, simulation, Digital Twins, and engineering records. The robot operating layer must remain modular, observable, testable, recoverable, and safe under partial failure.

## 1. System Boundary

ATLAS uses two cooperating layers:

- **AtlasOS:** missions, projects, Council coordination, Knowledge Bank, Digital Twins, research, user interfaces, governance, and long-term engineering records.
- **Robot runtime:** deterministic device communication, sensor streams, transforms, planning, control, execution, diagnostics, and hardware abstraction.

AtlasOS decides what work should happen. The robot runtime handles how verified robot processes execute it.

Neither layer should secretly absorb the responsibilities of the other.

## 2. Runtime Architecture

A robot runtime is organized into:

1. Hardware drivers
2. Device abstractions
3. Message transport
4. State publication
5. Coordinate transforms
6. Perception nodes
7. Planning nodes
8. Control nodes
9. Safety supervision
10. Mission bridge
11. Logging and replay
12. Digital Twin synchronization

Each component has one primary responsibility and a documented interface.

## 3. ROS 2 and Alternative Runtimes

ROS 2 may serve as the first reference middleware because it supports distributed nodes, topics, services, actions, lifecycle management, transforms, recording, simulation integration, and hardware abstractions.

ATLAS must not hardcode its entire architecture to one middleware. Core domain models and service contracts should remain reusable with:

- ROS 2
- Direct real-time control processes
- Industrial fieldbus systems
- Embedded microcontroller networks
- Simulation-only runtimes
- Future ATLAS-native transport layers

Middleware is an implementation tool, not the engineering constitution.

## 4. Nodes and Services

A node should own one clear capability, such as:

- Camera driver
- Joint-state publisher
- Robot-state estimator
- Vision detector
- Motion planner
- Trajectory controller
- Tool manager
- Safety monitor
- Digital Twin bridge

Nodes must expose health, version, configuration, dependencies, and fault state.

Large monolithic nodes are discouraged because they become difficult to test, restart, replace, and certify.

## 5. Communication Patterns

Use the communication pattern that matches the work:

- **Topics:** continuous streams such as images, joint states, transforms, and telemetry.
- **Services:** short request-response operations such as configuration lookup or calibration queries.
- **Actions:** long-running operations such as navigation, manipulation, inspection, or tool changes.
- **Events:** important state transitions, faults, safety changes, and mission milestones.

Interfaces should specify message schema, units, coordinate frames, timing, quality-of-service expectations, version, and failure behavior.

## 6. Quality of Service

Communication reliability requirements differ by data type.

Examples:

- Camera streams may favor timely delivery over preserving every frame.
- Safety events require reliable delivery and independent safeguards.
- Configuration updates require durability and version checks.
- Joint control commands require bounded latency and deterministic handling.
- Diagnostic logs may tolerate delayed delivery but must preserve ordering and timestamps.

Quality-of-service settings are engineering decisions and must be documented rather than left at arbitrary defaults.

## 7. Lifecycle Management

Managed components should support explicit states:

- Unconfigured
- Inactive
- Active
- Degraded
- Error
- Finalized

A component should not become active until dependencies, calibration, configuration, and safety conditions are verified.

Lifecycle transitions must be logged and testable.

## 8. Hardware Abstraction

Hardware drivers should be isolated behind stable interfaces.

Supported device classes may include:

- Motors and drives
- Encoders
- Cameras
- LiDAR
- Force/torque sensors
- IMUs
- Tool changers
- Grippers
- PLCs
- Safety controllers
- Battery and power systems

Hardware replacement should require a new driver or adapter rather than rewriting planning and mission software.

## 9. Real-Time Boundaries

Not every process needs real-time execution.

Real-time or near-real-time responsibilities may include:

- Motor current loops
- Joint control
- Emergency response
- Force control
- High-speed synchronization
- Safety-rated monitoring

Non-real-time responsibilities may include:

- Mission planning
- Documentation
- Knowledge retrieval
- Report generation
- Long-term analytics

Real-time control must not depend on cloud latency, large language model responses, or non-deterministic network services.

## 10. Coordinate Transforms and Time

The runtime must maintain a consistent transform tree across:

- World
- Map
- Robot base
- Links
- End effectors
- Tools
- Sensors
- Workpieces

Transforms require timestamps, frame IDs, validation, and revision control.

Time synchronization across computers, sensors, controllers, and recordings is required for reliable fusion and replay.

## 11. AtlasOS Mission Bridge

The mission bridge connects high-level AtlasOS missions to robot-runtime actions.

It should:

- Validate mission authorization
- Resolve the target robot and Digital Twin
- Check runtime capabilities
- Submit action goals
- Stream progress
- Report faults
- Preserve evidence
- Support pause, cancel, and safe abort
- Update the project record

AtlasOS must receive truthful execution state rather than optimistic status messages.

## 12. Digital Twin Bridge

The robot runtime synchronizes:

- Hardware configuration
- Active software versions
- Calibration revisions
- Tool identity
- Runtime state
- Faults
- Maintenance signals
- Executed trajectories
- Inspection evidence

The Digital Twin should distinguish commanded state, estimated state, and measured state.

## 13. Diagnostics and Observability

Every critical component should publish:

- Health state
- Uptime
- Configuration version
- Dependency state
- Processing latency
- Message rate
- Resource use
- Recent warnings
- Active faults

Logs must use consistent timestamps, severity levels, subsystem IDs, robot IDs, and mission IDs.

## 14. Recording and Replay

The runtime should support recording and replay of:

- Sensor streams
- Commands
- Joint states
- Transforms
- Planner outputs
- Controller feedback
- Safety events
- Faults
- Mission events

Replay supports debugging, simulation, regression testing, incident review, and model validation.

## 15. Security

The runtime should enforce:

- Authenticated devices
- Authorized commands
- Network segmentation
- Encrypted external communication where appropriate
- Signed or verified software artifacts
- Protected configuration
- Audit logging
- Least-privilege service accounts

Safety-critical control networks should remain isolated from unnecessary internet exposure.

## 16. Failure Containment

One failed node should not collapse the entire robot.

The runtime should support:

- Component restart
- Dependency timeout
- Circuit breakers
- Degraded modes
- Redundant sensors where justified
- Controlled shutdown
- Safe stop
- Fault isolation

The system must define what remains available after each major dependency fails.

## 17. Simulation Integration

The same interfaces used by physical robots should support simulated devices where practical.

Simulation should cover:

- Robot models
- Sensors
- Environments
- Collisions
- Actuators
- Fault injection
- Network delay
- Sensor noise
- Multi-robot coordination

Simulation results inform engineering decisions but do not replace physical verification.

## 18. Package and Repository Structure

A recommended organization is:

```text
robotics/
├── interfaces/
├── descriptions/
├── drivers/
├── perception/
├── planning/
├── control/
├── safety/
├── simulation/
├── mission_bridge/
├── digital_twin_bridge/
├── diagnostics/
├── launch/
├── config/
└── tests/
```

Packages should declare ownership, version, dependencies, supported robots, test status, and safety relevance.

## 19. Minimum Implementation Contract

The first ATLAS robot-runtime release should demonstrate:

- One simulated robot description
- Joint-state publication
- Transform publication
- Lifecycle-managed components
- One perception node
- One planning node
- One controller interface
- Mission submission from AtlasOS
- Pause and cancel
- Runtime diagnostics
- Recording and replay
- Digital Twin updates
- Automated tests

## 20. Verification Requirements

Acceptance requires:

- Clean startup and shutdown
- Dependency failures detected
- Lifecycle transitions tested
- Message schemas validated
- Units and frames verified
- Mission cancel and safe abort tested
- Simulated hardware replaceable through adapters
- Logs linked to mission and robot IDs
- Replay reproduces test behavior
- CI runs without physical hardware

## Laboratory Program

1. Launch a simulated two-joint robot.
2. Publish joint states and transforms.
3. Activate and deactivate lifecycle components.
4. Execute a simulated motion action.
5. Disconnect a dependency and verify degraded behavior.
6. Record and replay the mission.
7. Synchronize the result to a Digital Twin.

## Hermes Runtime Rules

- **ROS-1:** Middleware is replaceable; engineering contracts are permanent.
- **ROS-2:** Real-time control must remain independent of non-deterministic AI services.
- **ROS-3:** Every active component must expose health and failure state.
- **ROS-4:** Hardware belongs behind stable abstractions.
- **ROS-5:** A distributed robot must remain understandable when part of the network fails.
