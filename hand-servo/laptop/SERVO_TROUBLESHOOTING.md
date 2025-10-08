# Servo Troubleshooting Guide

## ✅ Communication Test Results
The Arduino communication is working perfectly:
- Commands are being sent correctly
- Arduino is responding with confirmations
- Serial communication is stable

## 🔧 Hardware Checklist

### 1. Servo Connections
Check that servos are connected to the correct pins:
```
Pan Servo (Pin 9):
- Red wire → 5V
- Black/Brown wire → GND
- Orange/Yellow wire → Pin 9

Tilt Servo (Pin 10):
- Red wire → 5V
- Black/Brown wire → GND
- Orange/Yellow wire → Pin 10
```

### 2. Power Supply
- **Arduino 5V pin**: Can power 1-2 micro servos for testing
- **External 5V supply**: Recommended for production (≥2A)
- **Common ground**: Ensure all grounds are connected

### 3. Servo Testing
Test each servo individually:
```bash
# Test pan servo only
echo "120" | python3 -c "
import serial, time
ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write('120\n'.encode())
time.sleep(2)
ser.write('90\n'.encode())
ser.close()
"

# Test tilt servo only  
echo "60" | python3 -c "
import serial, time
ser = serial.Serial('/dev/ttyACM0', 115200)
ser.write('90,60\n'.encode())
time.sleep(2)
ser.write('90,45\n'.encode())
ser.close()
"
```

## 🔍 Debugging Steps

### Step 1: Check Servo Movement
Run the debug script and watch for physical movement:
```bash
cd /home/parham/Desktop/CamServo/hand-servo/laptop
source .venv/bin/activate
echo "1" | python3 debug_servo.py
```

**Expected**: Servos should move through different positions visibly.

### Step 2: Test Individual Servos
```bash
# Test pan servo (should move left-right)
python3 -c "
import serial, time
ser = serial.Serial('/dev/ttyACM0', 115200)
print('Testing pan servo...')
ser.write('60\n'.encode())  # Left
time.sleep(2)
ser.write('120\n'.encode()) # Right  
time.sleep(2)
ser.write('90\n'.encode())  # Center
ser.close()
"

# Test tilt servo (should move up-down)
python3 -c "
import serial, time
ser = serial.Serial('/dev/ttyACM0', 115200)
print('Testing tilt servo...')
ser.write('90,30\n'.encode')  # Up
time.sleep(2)
ser.write('90,60\n'.encode')  # Down
time.sleep(2)
ser.write('90,45\n'.encode')  # Center
ser.close()
"
```

### Step 3: Check Arduino Code
Verify the correct Arduino code is uploaded:
- Should be `HandServoFollower.ino` (dual-axis)
- Not `SimpleServo.ino` (single-axis)

### Step 4: Power Issues
If servos don't move:
1. **Try external power supply** (5V, ≥2A)
2. **Check servo connections** (loose wires)
3. **Test with multimeter** (5V at servo power pins)
4. **Try different servos** (if available)

## 🚨 Common Issues

### Servos Not Moving
- **Cause**: Insufficient power, loose connections, damaged servos
- **Solution**: External power supply, check connections, test with different servos

### Jittery Movement  
- **Cause**: Power supply noise, loose connections
- **Solution**: Add capacitors, use external power, check connections

### One Servo Not Working
- **Cause**: Loose connection, damaged servo, wrong pin
- **Solution**: Check wiring, test with multimeter, try different servo

### Servos Move But Not Smoothly
- **Cause**: Power supply issues, mechanical binding
- **Solution**: External power, check servo mounting, lubricate if needed

## 📋 Quick Test Sequence

1. **Upload correct Arduino code** (`HandServoFollower.ino`)
2. **Check servo connections** (pins 9 and 10)
3. **Test with external power** (5V, ≥2A)
4. **Run debug script** and watch for movement
5. **Test individual servos** with simple commands
6. **Check servo specifications** (voltage, current requirements)

## 🔧 Visual Servo Tracker Settings

If servos are working but visual servo tracker seems slow:
```bash
# More responsive control
python3 visual_servo_tracker.py --kp 0.8

# Less frequent updates
python3 visual_servo_tracker.py --camera-index 2
```

## 📞 Next Steps

If servos still don't move after checking all connections and power:
1. **Test with different servos** (if available)
2. **Check servo specifications** (voltage/current requirements)
3. **Try external power supply** (5V, ≥2A)
4. **Verify Arduino code** is correct version
5. **Check for mechanical binding** in servo movement
