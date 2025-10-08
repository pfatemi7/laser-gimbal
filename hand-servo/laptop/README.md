# Visual Servo Hand Tracker

A real-time visual servo system that tracks your index finger and controls pan/tilt servos to keep it centered in the camera frame.

## 🎯 Features

- **Index finger tracking** - Precise control using finger tip
- **Real-time visual servoing** - Smooth servo movement
- **Center line display** - Visual feedback for targeting
- **External camera support** - Works with USB cameras
- **Arduino integration** - Controls dual servos via serial

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd /home/parham/Desktop/CamServo/hand-servo/laptop
./setup.sh
source .venv/bin/activate
```

### 2. Upload Arduino Code
Upload `SimpleServoTest.ino` to your Arduino (pins 9=pan, 10=tilt).

### 3. Run the Tracker
```bash
python3 balanced_dual_tracker.py --camera-index 2 --kp 1.0
```

## 📁 Files

- **`balanced_dual_tracker.py`** - Main visual servo tracker
- **`run_visual_servo.py`** - Interactive launcher
- **`setup.sh`** - Environment setup script
- **`QUICK_START.md`** - Detailed setup guide
- **`SERVO_TROUBLESHOOTING.md`** - Hardware troubleshooting

## 🎮 Usage

1. **Point your index finger** at the center of the screen
2. **Move your finger** to control the servos
3. **Red circle** shows what's being tracked
4. **Yellow lines** show the target center
5. **Press ESC** to exit

## ⚙️ Options

```bash
# Use different camera
python3 balanced_dual_tracker.py --camera-index 0 --kp 1.0

# Adjust responsiveness
python3 balanced_dual_tracker.py --camera-index 2 --kp 0.5  # Gentle
python3 balanced_dual_tracker.py --camera-index 2 --kp 2.0  # Responsive
```

## 🔧 Hardware Requirements

- **Arduino Uno** with `SimpleServoTest.ino` uploaded
- **Two servos** connected to pins 9 (pan) and 10 (tilt)
- **5V power supply** for servos (≥2A recommended)
- **USB camera** (external recommended)

## 📊 System Status

✅ **Working perfectly!**
- Index finger tracking
- Real-time servo control
- Visual feedback
- Center line display
