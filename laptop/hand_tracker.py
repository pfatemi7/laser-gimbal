#!/usr/bin/env python3
"""
Hand Servo Tracker - Pan and Tilt Control
Controls both pan and tilt servos based on hand position.
"""

import cv2
import mediapipe as mp
import serial
import time
import os
import sys

# Fix display issues
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['DISPLAY'] = os.environ.get('DISPLAY', ':0')

class HandTracker:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.4
        )
        
        # Pan servo angle mapping (X position)
        self.pan_min = 10
        self.pan_max = 170
        
        # Tilt servo angle mapping (Y position)
        self.tilt_min = 0
        self.tilt_max = 90
        self.INVERT_TILT = False  # Set True if mechanics need flipping
        
        # Serial communication
        self.ser = None
        
        # Camera
        self.cap = None
        
        # Performance
        self.last_pan_angle = 90
        self.last_tilt_angle = 45
        self.angle_threshold = 3
        self.last_send_time = 0
        self.send_interval = 0.1
        
        # Anti-freeze optimizations
        self.no_hand_count = 0
        self.max_no_hand_frames = 5
        self.frame_skip_count = 0
        self.frame_skip_interval = 2
        
    def find_arduino_port(self):
        """Auto-detect Arduino serial port."""
        arduino_port = os.getenv('ARDUINO_PORT')
        if arduino_port:
            print(f"Using Arduino port from environment: {arduino_port}")
            return arduino_port
        
        arduino_patterns = [
            '/dev/ttyACM',  # Linux
            '/dev/tty.usbmodem',  # macOS
            '/dev/tty.usbserial',  # macOS
            'COM'  # Windows
        ]
        
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_name = port.device
            for pattern in arduino_patterns:
                if pattern in port_name:
                    print(f"Found Arduino port: {port_name}")
                    return port_name
        
        print("No Arduino port found.")
        return None
    
    def connect_serial(self):
        """Connect to Arduino via serial."""
        port = self.find_arduino_port()
        if not port:
            return False
        
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(1)
            print(f"Connected to Arduino on {port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            return False
    
    def send_angles(self, pan_angle, tilt_angle):
        """Send pan and tilt angles to Arduino."""
        current_time = time.time()
        
        if current_time - self.last_send_time < self.send_interval:
            return
            
        if self.ser and self.ser.is_open:
            try:
                # Clamp angles to valid ranges
                pan_angle = max(0, min(180, int(pan_angle)))
                tilt_angle = max(0, min(90, int(tilt_angle)))
                
                # Send both angles as "PAN,TILT\n"
                command = f"{pan_angle},{tilt_angle}\n"
                self.ser.write(command.encode())
                self.ser.flush()
                self.last_send_time = current_time
                print(f"Sent angles: Pan={pan_angle}°, Tilt={tilt_angle}°")
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")
    
    def hand_x_to_pan_angle(self, x):
        """Convert normalized hand X position to pan servo angle."""
        return self.pan_min + (self.pan_max - self.pan_min) * x
    
    def hand_y_to_tilt_angle(self, y):
        """Convert normalized hand Y position to tilt servo angle."""
        if self.INVERT_TILT:
            return self.tilt_min + (self.tilt_max - self.tilt_min) * (1 - y)
        else:
            return self.tilt_min + (self.tilt_max - self.tilt_min) * y
    
    def draw_hand_info(self, frame, hand_x, hand_y, pan_angle, tilt_angle):
        """Draw hand position and angle information on frame."""
        h, w, _ = frame.shape
        
        # Draw hand center
        center_x = int(hand_x * w)
        center_y = int(hand_y * h)
        cv2.circle(frame, (center_x, center_y), 8, (0, 255, 0), -1)
        
        # Draw vertical line for pan
        cv2.line(frame, (center_x, 0), (center_x, h), (0, 255, 0), 2)
        
        # Draw horizontal line for tilt
        cv2.line(frame, (0, center_y), (w, center_y), (0, 255, 0), 2)
        
        # Draw angle text
        cv2.putText(frame, f"Pan: {int(pan_angle)}°", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Tilt: {int(tilt_angle)}°", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Hand X: {hand_x:.3f}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Hand Y: {hand_y:.3f}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    def run(self):
        """Main tracking loop."""
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return
        
        # Optimize camera settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 20)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Test camera
        print("Testing camera...")
        ret, test_frame = self.cap.read()
        if not ret:
            print("Error: Could not read from camera")
            self.cap.release()
            return
        print("Camera test successful!")
        
        # Connect to Arduino
        if not self.connect_serial():
            print("Warning: Could not connect to Arduino. Running in demo mode.")
        
        print("Hand tracking started.")
        print("Press ESC to exit. Make sure your hand is visible in the camera frame.")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.hands.process(rgb_frame)
                
                current_pan_angle = self.last_pan_angle
                current_tilt_angle = self.last_tilt_angle
                hand_detected = False
                
                if results.multi_hand_landmarks:
                    hand_detected = True
                    self.no_hand_count = 0
                    
                    # Get hand position
                    hand_landmarks = results.multi_hand_landmarks[0]
                    wrist = hand_landmarks.landmark[0]
                    hand_x = wrist.x
                    hand_y = wrist.y
                    
                    # Convert to servo angles
                    new_pan_angle = self.hand_x_to_pan_angle(hand_x)
                    new_tilt_angle = self.hand_y_to_tilt_angle(hand_y)
                    
                    current_pan_angle = new_pan_angle
                    current_tilt_angle = new_tilt_angle
                    
                    # Send angles if change is significant
                    pan_diff = abs(current_pan_angle - self.last_pan_angle)
                    tilt_diff = abs(current_tilt_angle - self.last_tilt_angle)
                    
                    if pan_diff > self.angle_threshold or tilt_diff > self.angle_threshold:
                        self.send_angles(current_pan_angle, current_tilt_angle)
                        self.last_pan_angle = current_pan_angle
                        self.last_tilt_angle = current_tilt_angle
                    
                    # Draw hand landmarks
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    # Draw hand info
                    self.draw_hand_info(frame, hand_x, hand_y, current_pan_angle, current_tilt_angle)
                    
                else:
                    # No hand detected
                    self.no_hand_count += 1
                    
                    # Send center position when no hand detected
                    if self.no_hand_count == 1:
                        print("No hand detected - centering servos")
                        self.send_angles(90, 45)  # Center pan, mid tilt
                        self.last_pan_angle = 90
                        self.last_tilt_angle = 45
                    
                    # Draw no hand message
                    cv2.putText(frame, "No hand detected", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(frame, f"Last pan: {int(self.last_pan_angle)}°", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, f"Last tilt: {int(self.last_tilt_angle)}°", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Show frame
                try:
                    cv2.imshow('Hand Servo Tracker - Press ESC to exit', frame)
                except cv2.error as e:
                    print(f"Display error: {e}")
                    print("Try running with --headless option")
                    break
                
                # Check for key presses
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    print("Quit requested by user")
                    break
                
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error during tracking: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("Resources cleaned up")

def main():
    """Main entry point."""
    print("Hand Servo Tracker - Pan and Tilt Control")
    print("==========================================")
    
    try:
        tracker = HandTracker()
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()