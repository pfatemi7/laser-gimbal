# Hand Servo Follower

A computer vision project that uses a laptop webcam to detect hand position and controls an Arduino-driven servo motor to follow the hand movement in real-time.

## Features

- **Real-time hand tracking** using MediaPipe and OpenCV
- **Dual-axis control** with pan and tilt servos
- **Smooth servo movement** with exponential moving average smoothing
- **Jitter reduction** with configurable deadband
- **Safety features** including watchdog timer and center return
- **Auto-detection** of Arduino serial port
- **Visual feedback** with hand tracking overlay

## Hardware Requirements

### Arduino Side
- Arduino Uno
- Two micro servo motors (tested with ElectriFly ES80)
- USB cable for programming and communication
- Optional: External 5V power supply (≥2A) for servos if experiencing jitter

### Laptop Side
- Webcam (built-in or USB)
- Python 3.9+
- USB port for Arduino connection

## Wiring

### Servo Connections
```
Pan Servo (Pin 9):
Servo Wire    →    Arduino Uno
Red (Power)   →    5V
Brown/Black   →    GND  
Orange/White  →    Digital Pin 9

Tilt Servo (Pin 10):
Servo Wire    →    Arduino Uno
Red (Power)   →    5V
Brown/Black   →    GND  
Orange/White  →    Digital Pin 10
```

### Power Considerations
- **For testing**: Arduino's 5V pin can power two micro servos (light load)
- **For production**: Use external 5V supply (≥2A) for servos and connect grounds
- **If experiencing jitter**: External power supply is recommended

### USB Connection
- Connect Arduino to laptop via USB cable
- This provides both programming interface and serial communication
- Common ground is automatically established

## Software Installation

### 1. Arduino IDE Setup
1. Download and install [Arduino IDE](https://www.arduino.cc/en/software)
2. Open `arduino/HandServoFollower/HandServoFollower.ino`
3. Select your Arduino Uno board and correct COM port
4. Upload the code to your Arduino

### 2. Python Environment Setup

#### Create Virtual Environment
```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install opencv-python mediapipe pyserial numpy
```

## Usage

### 1. Hardware Setup
1. Wire the servo to Arduino as described above
2. Connect Arduino to laptop via USB
3. Power on Arduino (servo should center at 90°)

### 2. Run the Hand Tracker
```bash
cd laptop
python hand_tracker.py
```

### 3. Operation
- Position your hand in front of the camera
- The servos will follow your hand movement
- **Pan control**: Left edge of frame → ~170° servo position, Right edge → ~10°
- **Tilt control**: Top of frame → 0°, Bottom of frame → 90°
- Press **ESC** to exit

### 4. Port Selection (Optional)
If auto-detection fails, specify the Arduino port:
```bash
# Linux
export ARDUINO_PORT=/dev/ttyACM0
python hand_tracker.py

# Windows
set ARDUINO_PORT=COM3
python hand_tracker.py

# macOS
export ARDUINO_PORT=/dev/tty.usbmodem14101
python hand_tracker.py
```

## Configuration

### Arduino Settings
- **Pan Servo Pin**: Digital Pin 9
- **Tilt Servo Pin**: Digital Pin 10
- **Baud Rate**: 115200
- **Smoothing**: Exponential moving average (α = 0.33)
- **Deadband**: ±2° to reduce jitter
- **Watchdog**: 1 second timeout returns to center

### Python Settings
- **Camera Resolution**: 640x480
- **Frame Rate**: 30 FPS
- **Pan Angle Range**: 10° to 170° (avoids servo endpoints)
- **Tilt Angle Range**: 0° to 90° (top to bottom of frame)
- **Hand Detection**: Single hand, high confidence

## Testing

### Arduino Test Mode
Uncomment `#define TEST_SWEEP` in the Arduino code to enable automatic servo sweeping for bench testing without the laptop.

### Troubleshooting

#### Servo Not Moving
1. Check wiring connections
2. Verify Arduino is receiving serial data (check Serial Monitor)
3. Try external power supply for servo
4. Check servo is not damaged

#### Hand Not Detected
1. Ensure good lighting
2. Keep hand in frame
3. Try different hand positions
4. Check camera permissions

#### Serial Communication Issues
1. Verify correct COM port
2. Check USB cable connection
3. Try different USB port
4. Restart Arduino IDE

#### Jittery Movement
1. Use external 5V power supply for servo
2. Add capacitors to servo power lines
3. Increase deadband in Arduino code
4. Reduce frame rate in Python code

## File Structure
```
hand-servo/
├── arduino/
│   ├── HandServoFollower/
│   │   └── HandServoFollower.ino    # Dual-axis Arduino code
│   └── SimpleServo/
│       └── SimpleServo.ino         # Single servo Arduino code
├── laptop/
│   ├── hand_tracker.py             # Main dual-axis hand tracker
│   ├── hand_tracker_working_simple.py  # Single servo hand tracker
│   └── test_dual_servo.py          # Test script for dual-axis
├── clear_port.sh                   # Utility script to clear serial port
└── README.md
```

## Technical Details

### Serial Protocol
- **Format**: "PAN,TILT\n" (e.g., "120,45\n") or "PAN\n" for backward compatibility
- **Pan Range**: 0-180 degrees
- **Tilt Range**: 0-90 degrees
- **Rate**: ~15-30 commands per second

### Angle Mapping
- **Pan**: Hand X position (0-1) → Servo angle (10-170°)
- **Tilt**: Hand Y position (0-1) → Servo angle (0-90°)
- Avoids servo endpoints for safety
- Smooth interpolation between positions

### Safety Features
- **Startup**: Servos center at pan=90°, tilt=45°
- **Watchdog**: Returns to center if no commands for 1 second
- **Bounds**: Pan clamped to 0-180°, tilt clamped to 0-90°
- **Smoothing**: Prevents sudden movements

## Troubleshooting Common Issues

### "No Arduino port found"
- Check USB connection
- Try different USB port
- Install Arduino drivers
- Set ARDUINO_PORT environment variable

### "Could not open camera"
- Check camera permissions
- Close other applications using camera
- Try different camera (if multiple available)

### Servo moves erratically
- Use external power supply
- Check for loose connections
- Reduce servo load
- Add smoothing capacitors

## License

This project is open source. Feel free to modify and distribute.

## Tilt Axis Added

### Tilt Wiring
- **D10** → tilt servo signal
- Tilt angle limited to **0–90°**
- **Mapping**: top of frame ⇒ 0°, bottom ⇒ 90°
- Laptop now sends **"PAN,TILT\n"**. Example: 120,35

### Dual-Axis Control
- **Pan servo** (Pin 9): Controls left-right movement (0-180°)
- **Tilt servo** (Pin 10): Controls up-down movement (0-90°)
- **Backward compatibility**: Still accepts "PAN\n" format for pan-only control
- **Center positions**: Pan=90°, Tilt=45° when no hand detected

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
