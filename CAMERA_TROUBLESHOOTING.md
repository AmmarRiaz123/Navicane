# Camera Troubleshooting Guide for Raspberry Pi

## Your Current Issue

```bash
vcgencmd get_camera
supported=0 detected=0, libcamera interfaces=0
```

This means the camera is **not detected** by the Raspberry Pi.

---

## Step-by-Step Fix

### Step 1: Check Physical Connection

1. **Power off** the Raspberry Pi completely:
   ```bash
   sudo shutdown -h now
   ```

2. **Disconnect power** from the Pi

3. **Check camera ribbon cable**:
   - Open the CSI port clip (pull up gently)
   - Remove the ribbon cable
   - Check for damage or bent pins
   - Re-insert the cable firmly:
     - **Blue side** faces the USB ports
     - **Silver contacts** face the HDMI ports
   - Push down the clip to lock

4. **Reconnect power** and boot up

---

### Step 2: Enable Camera in raspi-config

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **Legacy Camera** → **Enable**
- Also try: **Interface Options** → **Camera** → **Enable**

Then reboot:
```bash
sudo reboot
```

---

### Step 3: Install Camera Firmware/Software

Depending on your Raspberry Pi OS version, install the appropriate packages:

#### For libcamera (Bullseye and newer):

```bash
sudo apt update
sudo apt install -y libcamera-apps libcamera-dev
```

#### For legacy camera stack (older systems):

```bash
sudo apt update
sudo apt install -y libraspberrypi-bin libraspberrypi-dev
```

---

### Step 4: Update Firmware

```bash
sudo apt update
sudo apt full-upgrade -y
sudo rpi-update
sudo reboot
```

---

### Step 5: Check /boot/config.txt

Edit the boot configuration:

```bash
sudo nano /boot/config.txt
```

**For legacy camera (OV5647 v1.3):**

Add or uncomment these lines:
```ini
start_x=1
gpu_mem=128
```

And make sure this line is **commented out** (add # in front):
```ini
# camera_auto_detect=1
```

**Save** (Ctrl+O, Enter) and **Exit** (Ctrl+X), then reboot:
```bash
sudo reboot
```

---

### Step 6: Verify Detection

After reboot, check again:

```bash
vcgencmd get_camera
```

Should show:
