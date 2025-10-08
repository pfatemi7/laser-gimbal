# Performance Guide for Visual Servo Tracker

## 🚀 **Optimized Version Available**

Use the optimized version for better performance:
```bash
python3 visual_servo_optimized.py --camera-index 2 --kp 1.5
```

## 🔧 **Performance Optimizations**

### **1. Reduced Resource Usage**
- **Lower resolution**: 480x360 instead of 640x480
- **Lower FPS**: 15 FPS instead of 30 FPS
- **Frame skipping**: Processes every 3rd frame
- **Reduced update rate**: 10Hz instead of 20Hz
- **Minimal camera buffer**: Buffer size = 1

### **2. Optimized MediaPipe Settings**
- **Higher confidence thresholds**: Less re-detection
- **Single hand tracking**: Reduced processing
- **Optimized detection settings**

### **3. Reduced Debug Output**
- **Minimal console output**: Only essential messages
- **Optional debug mode**: Press 'D' to toggle
- **Reduced serial communication**: Larger angle thresholds

## 📊 **System Requirements**

### **Minimum Requirements**
- **CPU**: 2+ cores, 2GHz+
- **RAM**: 4GB+ available
- **Camera**: USB 2.0+ (external recommended)

### **Recommended Settings**
- **CPU**: 4+ cores, 2.5GHz+
- **RAM**: 8GB+ available
- **Camera**: USB 3.0 external camera
- **External power**: For servos (5V, ≥2A)

## 🛠️ **Troubleshooting Performance Issues**

### **If System Hangs or Freezes**

1. **Check system resources**:
   ```bash
   # Monitor resources while running
   python3 monitor_resources.py
   ```

2. **Use optimized version**:
   ```bash
   python3 visual_servo_optimized.py --camera-index 2 --kp 1.0
   ```

3. **Reduce gain for smoother operation**:
   ```bash
   # Less responsive but more stable
   python3 visual_servo_optimized.py --camera-index 2 --kp 0.8
   ```

4. **Close other applications**:
   - Close browser tabs
   - Close other camera applications
   - Close resource-intensive programs

### **If Servos Move Too Much**

1. **Reduce proportional gain**:
   ```bash
   python3 visual_servo_optimized.py --camera-index 2 --kp 0.5
   ```

2. **Use debug mode to monitor**:
   ```bash
   python3 visual_servo_optimized.py --camera-index 2 --kp 1.0 --debug
   ```

### **If Camera Issues**

1. **Check camera availability**:
   ```bash
   ls -la /dev/video*
   v4l2-ctl --list-devices
   ```

2. **Try different camera**:
   ```bash
   # Built-in camera
   python3 visual_servo_optimized.py --camera-index 0 --kp 1.5
   
   # External camera
   python3 visual_servo_optimized.py --camera-index 2 --kp 1.5
   ```

## ⚡ **Performance Tips**

### **1. System Optimization**
- **Close unnecessary applications**
- **Use external USB camera** (better performance)
- **Ensure good lighting** (reduces processing)
- **Keep hand in frame** (reduces re-detection)

### **2. Camera Settings**
- **Use external camera**: Better performance than built-in
- **Good lighting**: Reduces processing load
- **Stable mounting**: Reduces camera shake

### **3. Servo Settings**
- **External power supply**: Prevents voltage drops
- **Smooth movements**: Use lower gain values
- **Proper wiring**: Reduces electrical noise

## 📈 **Performance Monitoring**

### **Monitor System Resources**
```bash
# Real-time monitoring
python3 monitor_resources.py

# Quick system check
top -bn1 | head -20
```

### **Check Camera Performance**
```bash
# Test camera access
python3 -c "
import cv2
for i in range(4):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f'Camera {i}: Working - {frame.shape}')
        cap.release()
"
```

## 🎯 **Recommended Settings by Use Case**

### **High Performance (Smooth Operation)**
```bash
python3 visual_servo_optimized.py --camera-index 2 --kp 1.0
```

### **Responsive (Fast Tracking)**
```bash
python3 visual_servo_optimized.py --camera-index 2 --kp 2.0
```

### **Demo Mode (Minimal Resources)**
```bash
python3 visual_servo_optimized.py --camera-index 2 --kp 0.5
```

### **Debug Mode (Troubleshooting)**
```bash
python3 visual_servo_optimized.py --camera-index 2 --kp 1.5 --debug
```

## 🔍 **Common Issues and Solutions**

### **Issue: System Hangs**
- **Solution**: Use optimized version, close other apps
- **Command**: `python3 visual_servo_optimized.py --camera-index 2 --kp 1.0`

### **Issue: Servos Move Too Much**
- **Solution**: Reduce gain value
- **Command**: `python3 visual_servo_optimized.py --camera-index 2 --kp 0.5`

### **Issue: Poor Performance**
- **Solution**: Use external camera, good lighting
- **Command**: `python3 visual_servo_optimized.py --camera-index 2 --kp 1.0`

### **Issue: Camera Not Found**
- **Solution**: Check camera connections, try different index
- **Command**: `python3 visual_servo_optimized.py --camera-index 0 --kp 1.5`

## 📝 **Quick Commands**

```bash
# Start optimized tracker
python3 visual_servo_optimized.py --camera-index 2 --kp 1.5

# Monitor resources
python3 monitor_resources.py

# Test camera
python3 -c "import cv2; cap = cv2.VideoCapture(2); print('Working' if cap.isOpened() else 'Failed'); cap.release()"
```
