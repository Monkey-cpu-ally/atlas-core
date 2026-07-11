# ATLAS Vision Systems

Modular robotics perception foundation for **Hermes** (perception
persona) and **The Weaver** (build planner). Delivered in Iter-30.

Everything in this document maps 1:1 to a file in the repo. Nothing
here requires OpenCV, PyTorch, physical hardware, or paid API access —
detectors, trackers, pose estimators, and inspection pipelines are
pure-Python + numpy and produce deterministic outputs from a seed.

## File map

| File | Purpose |
|------|---------|
| `backend/models/vision_models.py` | Pydantic v2 request/response + persistence models: `Camera`, `Sensor`, `CameraCalibration`, `HandEyeCalibration`, `Frame`, `Detection`, `BoundingBox`, `Track`, `TrackSample`, `Pose`, `InspectionResult`, `InspectionDefect`, `TwinLink`. |
| `backend/services/vision.py`      | Service layer split into 10 clearly-labelled sections: Mongo, Registry, Calibration, Ingestion, Detection, Tracking, Pose, Inspection, Fusion, Twin link. |
| `backend/routes/vision.py`        | FastAPI router mounted at `/api/vision/*`. |
| `backend/tests/test_iter30_vision_systems.py` | 25 unit + integration tests (pipeline covers ingest → detect → track → pose → inspect → fuse → twin-link). |
| `backend/server.py`               | One `include_router(vision_router)` line added — nothing else touched. |

## MongoDB collections created

| Collection             | Model              | Notes                                   |
|------------------------|--------------------|-----------------------------------------|
| `vision_cameras`       | `Camera`           | intrinsic + hand-eye calibration flags |
| `vision_sensors`       | `Sensor`           | depth / imu / force / lidar / thermal / nir_bridge |
| `vision_calibrations`  | `CameraCalibration`| upsert-per-device (idempotent)         |
| `vision_hand_eye`      | `HandEyeCalibration`| 4x4 SE(3), residual_mm                |
| `vision_frames`        | `Frame`            | width/height/channels/checksum         |
| `vision_detections`    | `Detection`        | one row per bbox                       |
| `vision_tracks`        | `Track`            | temporal chain of detections (IoU)     |
| `vision_poses`         | `Pose`             | 6-DoF translation + quaternion         |
| `vision_inspections`   | `InspectionResult` | industrial + PCB                       |
| `vision_twin_links`    | `TwinLink`         | camera/sensor/inspection ↔ twin_id     |

## API surface (all `/api/vision/*`)

**Health & registry**
- `GET  /health`
- `GET  /devices?kind=camera|sensor`
- `POST /devices/camera`, `POST /devices/sensor`
- `GET/DELETE /devices/{device_id}`

**Calibration**
- `POST /calibration/intrinsic`, `GET /calibration/intrinsic/{device_id}`
- `POST /calibration/hand-eye`,  `GET /calibration/hand-eye/{device_id}`

**Ingestion**
- `POST /ingest/frame` (synthetic → deterministic pixels from seed; raw/png/jpg → payload_b64)
- `GET  /frames/{frame_id}`
- `GET  /frames?device_id=&limit=`

**Detection · Tracking · Pose**
- `POST /detect`            (detectors: `synthetic_grid`, `synthetic_center`, `twin_hint`)
- `GET  /detections/{frame_id}`
- `POST /track`             (IoU-based linking)
- `GET  /tracks/{track_id}`
- `POST /pose`              (methods: `synthetic`, `pnp_stub`)
- `GET  /poses/{frame_id}`

**Inspection**
- `POST /inspection/industrial`   (defect-severity thresholds)
- `POST /inspection/pcb`          (min_components + component_confidence)
- `GET  /inspection/{result_id}`
- `GET  /inspections?device_id=&limit=`

**Fusion**
- `POST /fusion`   (strategies: `nms`, `union`)

**Digital Twin link**
- `POST /twin-link` (idempotent upsert)
- `GET  /twin-link/{twin_id}`

## Interfaces (drop-in replacements)

The service layer exposes explicit "interface" functions so a real
implementation can slot in later without changing the routes:

- `synthetic_grid_detector`, `synthetic_center_detector`, `twin_hint_detector`
  → swap with a YOLO/DETR call.
- `estimate_pose(method=pnp_stub)`
  → swap with `cv2.solvePnP` once OpenCV is available in the pod.
- `run_industrial_inspection`, `run_pcb_inspection`
  → hook a defect model (e.g. PatchCore, PADIM) via the same signature.
- `fuse_detections`
  → swap NMS for Kalman-fused MOT.

## Digital Twin coupling

- Cameras/Sensors carry an optional `twin_id`.
- `POST /twin-link` writes a bidirectional link doc AND mirrors the
  `twin_id` back onto the camera/sensor row.
- The `twin_hint` detector reads the linked twin's
  `manifest.labels` and emits one detection per label — this is how
  The Weaver drives simulated perception during build planning.

## Sensor fusion readiness

Fusion consumes detections from any set of frames (multi-frame OR
multi-camera). Two strategies today: `nms` (default) and `union`.
Both return a full detection list, ready to feed pose estimation or
tracking.

## Safety / test posture

- No real camera drivers, no OpenCV imports, no torch — the service
  code is fine on any CPU-only pod.
- Synthetic frames are deterministic (numpy PRNG seeded per request).
- All 25 iter-30 tests use localhost and clean up their own state.
- Zero paid-API calls: no OpenAI, no ElevenLabs.

## What's intentionally NOT here (yet)

- OpenCV / camera driver bindings — will land when the architect confirms
  the pod's system libs.
- Real object detector weights (YOLO/DETR) — needs GPU or on-device NNAPI.
- WebRTC video streaming — separate iteration (frame-by-frame POST covers
  the current build-planning + inspection needs).
- SLAM / metric map — not in scope until multi-camera hand-eye lands.

See `backend/tests/test_iter30_vision_systems.py` for the current 25
tests and their assertions; each maps to a specific capability listed
in `/api/vision/health`.
