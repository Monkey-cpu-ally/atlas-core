# ATLAS Robotics Vision Systems Bible

**Primary AI:** Hermes  
**Supporting AIs:** Minerva, Ajani, ATLAS Council  
**Primary platforms:** The Weaver, humanoid systems, Green Robots, inspection cells

## Mission

Build a modular perception layer that allows ATLAS robots to observe, measure, inspect, localize, track, and explain what they perceive. Vision outputs must remain traceable to the originating device, frame, calibration, model version, confidence score, and Digital Twin record.

## 1. Perception Architecture

The perception stack is divided into six layers:

1. Device layer — cameras and sensors.
2. Calibration layer — intrinsic, extrinsic, timing, and hand-eye calibration.
3. Ingestion layer — frames, streams, video clips, timestamps, and metadata.
4. Perception layer — detection, segmentation, tracking, pose, depth, and measurement.
5. Inspection layer — rules, tolerances, defect classification, and pass/fail decisions.
6. Traceability layer — replay, Digital Twin updates, Knowledge Bank records, and audit history.

No model output becomes an engineering decision without its source data and confidence record.

## 2. VisionDevice Standard

Every imaging or ranging device shall use one shared abstraction.

A `VisionDevice` record should include:
- Stable device ID
- Device type
- Manufacturer and model
- Serial number
- Robot or cell assignment
- Network or physical interface
- Resolution and frame rate
- Lens or field-of-view information
- Calibration status and revision
- Operational state
- Last health check
- Digital Twin ID
- Supported capabilities

Supported device families may include RGB, stereo, depth, thermal, infrared, event cameras, LiDAR, radar, and future sensor types.

The API must operate on device capabilities rather than hardcoded camera brands.

## 3. Calibration

Calibration records are versioned engineering assets.

Required calibration types:
- Camera intrinsic calibration
- Lens distortion correction
- Stereo calibration
- Camera-to-camera extrinsics
- Camera-to-robot hand-eye calibration
- Camera-to-world calibration
- Depth scale calibration
- Time synchronization

Each record stores the method, reference target, date, operator or service, quality metrics, accepted tolerances, and superseded revision.

A robot must not perform precision measurement with expired, missing, or failed calibration.

## 4. Frame and Stream Ingestion

Every frame should carry:
- Frame ID
- Device ID
- Capture timestamp
- Sequence number
- Resolution
- Encoding
- Exposure data when available
- Calibration revision
- Robot pose or cell pose when available
- Storage reference
- Integrity checksum where practical

Video ingestion should use configurable limits for duration, frame rate, resolution, and total size. Limits belong in AtlasOS settings rather than being hardcoded into routes.

## 5. Core Perception Services

The first implementation should provide stable interfaces for:
- Object detection
- Classification
- Multi-object tracking
- Segmentation
- 2D and 3D pose estimation
- Depth and point-cloud processing
- Optical flow
- Dimensional measurement
- Barcode and QR reading
- OCR
- Anomaly and defect detection

A service may begin with simulated or deterministic test implementations, but the interface, metadata, and test contract must match future production models.

## 6. Industrial Inspection

Inspection pipelines should support:
- Surface scratches and dents
- Cracks and corrosion
- Weld condition
- Fastener presence and seating
- Connector seating
- Cable routing
- Missing or reversed components
- Bent PCB pins
- Solder-joint quality
- Assembly orientation
- Dimensional tolerances
- Label and identifier verification

Each inspection result stores:
- Inspection ID
- Part or assembly ID
- Device and frame references
- Pipeline and model version
- Measurements
- Detected defects
- Confidence
- Decision
- Human-review requirement
- Digital Twin update status

Decision classes:
- Pass
- Fail
- Rework
- Scrap
- Uncertain
- Human review required

## 7. Tracking and Pose

Tracking must preserve identity across frames and report uncertainty, missed detections, and identity changes.

Pose outputs should define the coordinate frame used, units, orientation convention, covariance or confidence, and timestamp.

Hand-eye tasks require explicit transforms between:
- Camera frame
- Robot base
- End effector
- Tool center point
- Workcell or world frame

Undefined coordinate frames are treated as invalid engineering data.

## 8. Sensor Fusion Readiness

The vision layer must be ready to combine data from cameras, LiDAR, radar, IMUs, encoders, force/torque sensors, and Digital Twins.

Fusion inputs require:
- Common timestamps
- Coordinate-frame definitions
- Calibration revisions
- Data quality metrics
- Source identity
- Uncertainty estimates

The first release may not perform full fusion, but it must not create interfaces that make fusion difficult later.

## 9. Replay and Black-Box Recording

ATLAS should support a replay endpoint for post-mission analysis.

Suggested route:

`GET /api/vision/replay?device_id=<id>&from=<timestamp>&to=<timestamp>`

A replay package may include compressed timelines of frames, detections, tracks, poses, inspections, warnings, calibration revisions, and relevant robot states.

Replay records support debugging, incident review, quality investigations, model comparison, and training-data curation. Retention, privacy, and storage limits must be configurable.

## 10. Digital Twin and Knowledge Bank Integration

Every important inspection should update the related Digital Twin with:
- Timestamp
- Device and calibration revision
- Model version
- Measurements
- Decision
- Evidence references
- Corrective action when needed

Validated failures and corrective actions should become Knowledge Bank lessons. Uncertain or unreviewed model outputs must remain separated from verified engineering knowledge.

## 11. Safety and Reliability

The vision system shall fail safely when:
- A device disconnects
- Frames stop arriving
- Calibration is invalid
- Time synchronization fails
- Confidence falls below the required threshold
- Data is corrupted
- Coordinate transforms are missing
- The active model is incompatible with the pipeline

Safety-critical actions require independent safeguards. Vision alone must not be the only protection against crushing, collision, or hazardous motion.

## 12. Minimum API Contract

The initial service should expose:
- `GET /api/vision/health`
- `GET /api/vision/devices`
- `POST /api/vision/devices`
- `POST /api/vision/calibrations`
- `POST /api/vision/ingest/frame`
- `POST /api/vision/ingest/video`
- `POST /api/vision/detect`
- `POST /api/vision/track`
- `POST /api/vision/pose`
- `POST /api/vision/inspect`
- `GET /api/vision/inspections`
- `GET /api/vision/replay`

Route names may be adapted to the existing backend, but equivalent capabilities and test coverage are required.

## 13. Verification Requirements

The implementation is accepted only when it demonstrates:
- Device registration and retrieval
- Calibration revision tracking
- Deterministic frame ingestion
- Detection result persistence
- Tracking identity across test frames
- Pose records with explicit coordinate frames
- Inspection decisions with evidence links
- Replay filtering by device and time range
- Health checks for dependencies
- No paid external API calls during tests
- Unit and integration tests passing in CI

## Laboratory Program

1. Calibrate a simulated RGB camera.
2. Detect and count fasteners on a workbench image.
3. Track parts moving across a simulated conveyor.
4. Estimate the pose of a known fixture.
5. Inspect a simulated PCB for missing components.
6. Produce a complete Digital Twin inspection record.
7. Replay the mission timeline and explain each decision.

## Hermes Vision Rules

- **VS-1:** A detection without source, time, calibration, and confidence is not engineering evidence.
- **VS-2:** Uncertainty must be recorded, not hidden.
- **VS-3:** Precision work requires valid coordinate frames and calibration.
- **VS-4:** Vision informs safe operation; it does not replace independent safety systems.
- **VS-5:** Every inspection should improve traceability and future reliability.
