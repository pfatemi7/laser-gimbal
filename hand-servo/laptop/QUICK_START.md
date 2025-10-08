# Quick Start Guide

## Setup and Run Visual Servo Tracker

### 1. Navigate to the correct directory
```bash
cd /home/parham/Desktop/CamServo/hand-servo/laptop
```

### 2. Activate the virtual environment
```bash
source .venv/bin/activate
```

### 3. Run the visual servo tracker

#### Option A: Auto-detect external camera (recommended)
```bash
python3 visual_servo_tracker.py
```

#### Option B: Use specific camera
```bash
# Use camera index 1
python3 visual_servo_tracker.py --camera-index 1

# Use camera path /dev/video1
python3 visual_servo_tracker.py --camera-path /dev/video1
```

#### Option C: Interactive launcher
```bash
python3 run_visual_servo.py
```

#### Option D: Test without Arduino
```bash
python3 test_visual_servo.py
```

### 4. Adjust control parameters (optional)
```bash
# More responsive control
python3 visual_servo_tracker.py --kp 0.8

# Add integral control for better accuracy
python3 visual_servo_tracker.py --kp 0.5 --ki 0.1 --enable-integral

# Less responsive control
python3 visual_servo_tracker.py --kp 0.2
```

## What You'll See

- **Green circle**: Your hand position
- **White crosshair**: Center of the frame
- **Red arrow**: Error direction and magnitude
- **Text display**: Target angles, error values, hand coordinates
- **Real-time updates**: System adjusts to keep your hand centered

## Controls

- **Move your hand**: The system will try to keep it centered
- **Press ESC**: Exit the program
- **No hand detected**: System maintains last target angles

## Troubleshooting

### Camera Issues
- If camera not found, try different camera index: `--camera-index 0` or `--camera-index 1`
- Check camera permissions and that no other app is using the camera

### Arduino Connection
- Make sure Arduino is connected via USB
- Check that the correct Arduino code is uploaded
- The system will run in "demo mode" if Arduino is not connected

### Performance
- Adjust `--kp` parameter for responsiveness (0.1 = slow, 1.0 = fast)
- Use `--enable-integral` for better steady-state accuracy
- Reduce frame rate if system is slow

## Files Created

- `visual_servo_tracker.py` - Main visual servo tracker
- `run_visual_servo.py` - Interactive launcher
- `test_visual_servo.py` - Test without Arduino
- `setup.sh` - Setup script for dependencies
- `.venv/` - Virtual environment with dependencies
