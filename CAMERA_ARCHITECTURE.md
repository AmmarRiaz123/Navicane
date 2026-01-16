# Camera System Architecture

## The Constraint

This Raspberry Pi system has a **hard hardware/OS limitation**:

**ONLY rpicam-* CLI commands work for camera access.**

### What DOES Work ✅

- `rpicam-hello` - Camera preview
- `rpicam-still` - Still image capture
- `rpicam-vid` - Video recording
- `rpicam-raw` - RAW image capture

### What DOES NOT Work ❌

- **Picamera2** - Python library hangs or fails
- **cv2.VideoCapture(0)** - Cannot open camera device
- **libcamera Python bindings** - Not functional
- **GStreamer libcamera** - Does not work
- **Direct /dev/video access** - Fails

## Why This Happens

Possible causes:
1. Specific Raspberry Pi OS build
2. libcamera version incompatibility with Python bindings
3. Kernel/driver mismatch
4. Hardware abstraction layer issues

**This is NOT a bug to fix** - it's a system constraint to work within.

## Our Solution

### Architecture

