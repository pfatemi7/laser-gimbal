#!/usr/bin/env python3
"""
Simple Working Hand Tracker - Focuses on core functionality.
"""

import cv2
import mediapipe as mp
import serial
import time
import os

class SimpleWorkingHandTracker:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.4
        )
        
        # Servo angle mapping
        self.angle_min = 10
        self.angle_max = 170
        
        # Serial communication
        self.ser = None
        
        # Camera
        self.cap = None
        
        # Performance
        self.last_angle = 90
        self.angle_threshold = 3
        self.last_send_time = 0
        self.send_interval = 0.1
        
    def find_arduino_port(self):
        """Auto-detect Arduino serial port."""
        arduino_port = os.getenv('ARDUINO_PORT')
        if arduino_port:
            return arduino_port
        
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            port_name = port.device
            if '/dev/ttyACM' in port_name:
                return port_name
        
        return None
    
    def connect_serial(self):
        """Connect to Arduino via serial."""
        port = self.find_arduino_port()
        if not port:
            print("No Arduino port found!")
            return False
        
        try:
            self.ser = serial.Serial(port, 115200, timeout=1)
            time.sleep(1)
            print(f"Connected to Arduino on {port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            return False
    
    def send_angle(self, angle):
        """Send angle command to Arduino."""
        current_time = time.time()
        
        if current_time - self.last_send_time < self.send_interval:
            return
            
        if self.ser and self.ser.is_open:
            try:
                angle = max(0, min(180, int(angle)))
                command = f"{angle}\n"
                self.ser.write(command.encode())
                self.ser.flush()
                self.last_send_time = current_time
                print(f"Hand position: {angle}°")
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")
    
    def hand_x_to_angle(self, x):
        """Convert normalized hand X position to servo angle."""
        angle = self.angle_min + (self.angle_max - self.angle_min) * x
        return angle
    
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
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        print("Camera initialized successfully!")
        
        # Connect to Arduino
        if not self.connect_serial():
            print("Warning: Could not connect to Arduino. Running in demo mode.")
            return
        
        print("Hand tracking started!")
        print("Move your hand in front of the camera to control the servo.")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process with MediaPipe
                results = self.hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    # Get hand position
                    hand_landmarks = results.multi_hand_landmarks[0]
                    wrist = hand_landmarks.landmark[0]
                    hand_x = wrist.x
                    
                    # Convert to servo angle
                    new_angle = self.hand_x_to_angle(hand_x)
                    
                    # Send angle if change is significant
                    angle_diff = abs(new_angle - self.last_angle)
                    if angle_diff > self.angle_threshold:
                        self.send_angle(new_angle)
                        self.last_angle = new_angle
                else:
                    # No hand detected - center servo
                    if self.last_angle != 90:
                        self.send_angle(90)
                        self.last_angle = 90
                
                # Small delay
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nStopping hand tracker...")
        except Exception as e:
            print(f"Error during tracking: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        if self.ser and self.ser.is_open:
            self.ser.close()
        print("Resources cleaned up")

def main():
    """Main entry point."""
    print("Simple Working Hand Servo Tracker")
    print("==================================")
    
    try:
        tracker = SimpleWorkingHandTracker()
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
