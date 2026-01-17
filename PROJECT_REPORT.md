# Navicane (Smart Cane) — Technical Project Report

## 1) Executive Summary

Navicane is a Raspberry Pi–based assistive navigation system designed to improve near-field awareness for a visually impaired user. It combines:

- **Ultrasonic ranging** (for distance measurement)
- **Haptic feedback** (vibration intensity and cadence scale with distance)
- **Camera-based object detection** (what the obstacle likely is)
- **Speech output** (announces only when sufficiently close and meaningful)

The system is engineered as **non-blocking**, using independent loops/threads so that sensors + vibration continue even if camera/speech temporarily fail.

---

## 2) System Goals and Constraints

### Goals
| Goal | Description |
|---|---|
| Real-time obstacle awareness | Fast distance sensing and immediate haptic response |
| Low cognitive load | Speech is gated and rate-limited (no “constant chatter”) |
| Robustness | Degrades gracefully if camera/audio unavailable |
| Boot-to-run automation | Runs as a background service (systemd) |

### Hard Constraints
- Camera access on your setup works via **rpicam CLI** tools (**rpicam-still / rpicam-hello / rpicam-vid**), not OpenCV `VideoCapture`.
- Bluetooth audio tends to be **session dependent** (manual terminal runs work earlier than systemd boot runs unless timing/session is handled).

---

## 3) Hardware Overview

### Primary Hardware
| Component | Qty | Notes |
|---|---:|---|
| Raspberry Pi | 1 | Raspberry Pi OS 64-bit |
| Pi Camera Module | 1 | Accessed via rpicam-* CLI |
| HC-SR04 Ultrasonic Sensor | 1 | Mounted on **left** side |
| Vibration Motor + driver | 1 | Requires transistor + diode |
| Audio output | 1 | Bluetooth headphones/speaker |

### GPIO Assignment (current config)
| Function | GPIO | Source |
|---|---:|---|
| Ultrasonic Trigger | 23 | `ULTRASONIC_SENSORS['left']['trigger']` |
| Ultrasonic Echo | 24 | `ULTRASONIC_SENSORS['left']['echo']` |
| Vibration Motor | 17 | `VIBRATION_MOTORS['center']` |

**Electrical safety note**: HC-SR04 echo is 5V logic; Raspberry Pi GPIO is 3.3V tolerant. Use a voltage divider on ECHO.

---

## 4) Software Architecture

### Module-Level Breakdown
| File | Responsibility | Key Outputs |
|---|---|---|
| `main.py` | Orchestrates concurrency, integrates subsystems | Non-blocking loops |
| `ultrasonic.py` | Reads distance from HC-SR04 (left sensor) | Distance in cm |
| `vibration.py` | Converts distance → haptic intensity/pulse | PWM vibration |
| `camera.py` | Captures image via rpicam-still, runs OpenCV DNN model | Detected objects |
| `speech.py` | TTS announcements with cooldown and non-overlap | Spoken warnings |
| `config.py` | Single source of tuning parameters | Runtime constants |
| `utils.py` | Logging + utility primitives | Logger, rate limiter |

### Runtime Flow (high-level)
1. **Ultrasonic loop** reads distance continuously.
2. **Vibration controller** maps distance to intensity + pulse rate.
3. **Camera loop** runs only when ultrasonic distance is within `CAMERA_TRIGGER_DISTANCE`.
4. **Speech** triggers only when distance is within `SPEECH_TRIGGER_DISTANCE` AND camera has a high-confidence “ahead” detection.

### Non-Blocking Design
- “Fast path” (ultrasonic → vibration) must never be blocked by camera or speech.
- Speech uses background threads and a “don’t overlap” rule so it cannot deadlock the camera loop.

---

## 5) Object Detection Pipeline

### Model
- Current configuration uses **YOLOv4-tiny (Darknet)** loaded via OpenCV DNN:
  - weights: `~/models/yolov4-tiny.weights`
  - cfg: `~/models/yolov4-tiny.cfg`
  - class names: `~/models/coco.names`

### Capture Method
- Image capture occurs by spawning `rpicam-still`, saving a JPEG to a temp path, then reading it via OpenCV (`cv2.imread`).

### Filtering Strategy
1. Ignore detections below `CONFIDENCE_THRESHOLD`.
2. Ignore detections not in `PRIORITY_OBJECTS`.
3. Compute whether detection is “ahead” using the image horizontal center window:
   - `CENTER_REGION_START` → `CENTER_REGION_END`

---

## 6) Speech Strategy

Speech is intentionally constrained to avoid overwhelming the user.

### Triggering Rules (intended behavior)
| Condition | Result |
|---|---|
| Distance ≥ `CAMERA_TRIGGER_DISTANCE` | Camera detection loop may skip to save CPU |
| Distance < `CAMERA_TRIGGER_DISTANCE` | Camera detection runs periodically |
| Distance ≥ `SPEECH_TRIGGER_DISTANCE` | No announcements (silent monitoring) |
| Distance < `SPEECH_TRIGGER_DISTANCE` AND “ahead” object detected | Speak object label |
| Critical range (e.g., < 30 cm if implemented) | “Warning …” prefix + priority |

### De-conflicting speech
- Speech must **not talk over itself**
- Speech must **not spam repeat**: cooldown via `SPEECH_COOLDOWN`

---

## 7) Haptic Feedback Strategy

The vibration controller uses *zones* with distinct urgency patterns.

### Vibration Zones (current configuration)
| Zone | Range (cm) | Intensity Behavior | Pulse Rate |
|---|---|---|---:|
| critical | 0–30 | constant strong | 0 (constant) |
| danger | 30–60 | strong fast pulses | 5 Hz |
| warning | 60–100 | medium pulses | 2 Hz |
| caution | 100–150 | light pulses | 1 Hz |
| clear | 150–400 | off | 0 |

This creates a gradient: closer object → stronger + faster haptics.

---

## 8) Configuration Reference (config.py)

This table reflects the *intent* and *impact* of each key parameter.

### Ultrasonic / Obstacle Logic
| Key | Current | Impact |
|---|---:|---|
| `ULTRASONIC_SENSORS['left']` | trigger=23, echo=24 | Hardware wiring |
| `DISTANCE_THRESHOLD` | 60 cm | Affects “obstacle close” logic (if used directly) |
| `SENSOR_TIMEOUT` | 0.1 s | Timeout for echo waits; too low → many None readings |

### Vibration
| Key | Current | Impact |
|---|---:|---|
| `VIBRATION_MOTORS['center']` | GPIO 17 | Motor control pin |
| `VIBRATION_RANGES` | zones | Defines distance bands |
| `VIBRATION_PULSE_RATES` | per zone | How “urgent” haptics feel |

### Camera
| Key | Current | Impact |
|---|---:|---|
| `CAMERA_WIDTH`, `CAMERA_HEIGHT` | 640×480 | Higher = more CPU + better detection detail |
| `RPICAM_CAPTURE_INTERVAL` | 2.0 s | Capture pacing (if used by camera loop) |
| `RPICAM_TIMEOUT` | 5 s | Capture command timeout |
| `CAMERA_MAX_RETRY_ATTEMPTS` | 5 | Robustness during service startup |
| `CAMERA_RETRY_DELAY` | 2 s | Retry pacing if camera fails early |

### Detection / Vision
| Key | Current | Impact |
|---|---:|---|
| `MODEL_PATH` | YOLO weights | Must exist and be readable |
| `PROTOTXT_PATH` | YOLO cfg | Must exist and match weights |
| `CONFIDENCE_THRESHOLD` | 0.50 | Higher → fewer/cleaner detections; lower → more false positives |
| `PRIORITY_OBJECTS` | 9 classes | Limits what can be spoken |
| `CENTER_REGION_START/END` | 0.25 / 0.75 | Wider window → more “ahead” hits (more speech), narrower → fewer |

### Speech / Timing
| Key | Current | Impact |
|---|---:|---|
| `SPEECH_TRIGGER_DISTANCE` | 80 cm | Speak only when closer than this |
| `SPEECH_COOLDOWN` | 5.0 s | Longer = less repetition |
| `TTS_SPEED` | 170 | Higher = faster speech |
| `TTS_VOLUME` | 200 | eSpeak amplitude (still depends on system volume/output routing) |

### Loop Timing
| Key | Current | Impact |
|---|---:|---|
| `ULTRASONIC_LOOP_DELAY` | 0.05 s | 20 Hz haptics responsiveness |
| `CAMERA_LOOP_DELAY` | 1.0 s | Detection frequency (CPU + speech frequency driver) |

---

## 9) Deployment: Running on Boot (systemd)

### Why “works in terminal but not on boot” happens
Common causes:
- Bluetooth audio connects but sink isn’t default yet (PulseAudio/BlueZ timing).
- Service starts before user audio session is ready.
- Environment differs: `XDG_RUNTIME_DIR`, DBus session address, Pulse socket availability.

### Recommended service expectations
- Service should run indefinitely (`Restart=always`) and never stop unless explicitly stopped.
- Camera failures at boot should **not** crash the entire system. The system should run “haptics-only” until camera becomes available.

---

## 10) Logging and Observability

### Logging targets
- Primary log file: `smart_cane.log` in your working directory (depends on where service runs).
- systemd journal: `journalctl -u smart-cane -f`

### Typical “good” log signals
- “Smart cane starting”
- Ultrasonic loop started
- Camera loop started
- “Smart cane ready”
- Periodic detections and speech announcements

---

## 11) Testing Matrix

### Component Tests
| Test | Command | Pass Criteria |
|---|---|---|
| Ultrasonic | `python3 ultrasonic.py` | Stable distance readings |
| Vibration | `python3 vibration.py` | Intensity/pulses change |
| Camera | `python3 camera.py` | Saves image / produces detections |
| Speech | `python3 speech.py` | Sound is audible |
| Integration | `python3 test_full_integration.py` | Detect + speak under distance gating |

### Service Tests
| Test | Command | Pass Criteria |
|---|---|---|
| Start service | `sudo systemctl start smart-cane` | Stays active |
| Boot test | reboot | “starting/ready” spoken + keeps running |
| Journal | `journalctl -u smart-cane -n 200` | No rapid crash loops |

---

## 12) Troubleshooting Guide (common failures)

### A) Camera works in terminal, fails on boot
Likely timing/permissions. Fix patterns:
- Increase service startup delay (ExecStartPre sleep).
- Make camera init non-fatal and retry in runtime.
- Ensure `libcamera-apps` installed and rpicam tools available in PATH.

### B) Bluetooth connects but no audio on boot
Likely session/sink selection:
- Ensure service has correct audio env (`XDG_RUNTIME_DIR`, DBus).
- Prefer a *user systemd service* (per-user session) for Bluetooth audio stability.
- Delay speech until default sink is present.

### C) Wrong detections / too chatty
- Increase `CONFIDENCE_THRESHOLD` (0.5 → 0.6).
- Reduce `PRIORITY_OBJECTS`.
- Narrow `CENTER_REGION_START/END`.
- Increase `SPEECH_COOLDOWN`.

### D) CPU too high
- Increase `CAMERA_LOOP_DELAY` (1.0 → 2.0+).
- Lower resolution (640×480 → 320×240).
- Reduce camera trigger distance or only run detection when ultrasonic indicates near obstacles.

---

## 13) Safety and Operational Notes

- This is an assistive prototype and must be tested in controlled environments.
- Always use appropriate mobility aids.
- Ensure secure wiring and proper power supply to prevent resets.

---

## 14) Appendix: Suggested “Tuning Profiles”

### Profile A: Quiet and conservative (less speech)
- `CONFIDENCE_THRESHOLD = 0.6`
- `SPEECH_TRIGGER_DISTANCE = 60`
- `SPEECH_COOLDOWN = 6`
- `CENTER_REGION_START/END = 0.3 / 0.7`
- `CAMERA_LOOP_DELAY = 2.0`

### Profile B: More awareness (more detections, some risk of false positives)
- `CONFIDENCE_THRESHOLD = 0.45`
- `SPEECH_TRIGGER_DISTANCE = 100`
- `SPEECH_COOLDOWN = 3`
- `CENTER_REGION_START/END = 0.2 / 0.8`
- `CAMERA_LOOP_DELAY = 1.0`

---

## 15) “What to include in a final submission”
- Wiring diagram + pin map
- Final `config.py` values used in demo
- Demo video showing distance → vibration gradient and close-range speech
- Systemd unit file used for boot run
- Troubleshooting log excerpts for major issues resolved
