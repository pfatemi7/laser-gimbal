#!/usr/bin/env python3
"""
Balanced Dual Servo Tracker - Good performance with HandServoFollower.ino
Balanced between performance and functionality
"""

import cv2
import mediapipe as mp
import time
import argparse
import os
import serial
import serial.tools.list_ports

# Fix display issues
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['DISPLAY'] = os.environ.get('DISPLAY', ':0')

class BalancedDualTracker:
    def __init__(self, camera_index=None, camera_path=None, kp=0.5):
        # Balanced MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,  # Balanced confidence
            min_tracking_confidence=0.5    # Balanced tracking
        )
        
        self.camera_index = camera_index
        self.camera_path = camera_path
        self.cap = None
        self.ser = None
        
        # Control parameters
        self.kp = kp
        self.pan_angle = 90
        self.tilt_angle = 45
        
        # Performance settings
        self.frame_skip = 2  # Process every 2nd frame
        self.frame_count = 0
        self.last_update = 0
        self.update_interval = 0.1  # Update every 100ms (10Hz)
        
        print("Balanced Dual Servo Tracker")
        print("===========================")
        print(f"Camera index: {self.camera_index}")
        print(f"Camera path: {self.camera_path}")
        print(f"Proportional gain: {self.kp}")
        print(f"Update rate: {1/self.update_interval:.1f} Hz")

    def find_camera_source(self):
        """Find camera source."""
        if self.camera_path:
            return self.camera_path
        elif self.camera_index is not None:
            return self.camera_index
        else:
            # Try external camera first
            for i in range(3):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cap.release()
                    if i != 0:  # Prefer non-zero index
                        return i
            return 0

    def initialize_camera(self):
        """Initialize camera with balanced settings."""
        source = self.find_camera_source()
        self.cap = cv2.VideoCapture(source)
        
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Balanced camera settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Larger resolution
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 20)            # Good FPS
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)       # Minimal buffer
        
        print(f"Camera initialized: {source}")
        return True

    def connect_serial(self):
        """Connect to Arduino."""
        try:
            # Try common Arduino ports
            arduino_ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyUSB0', '/dev/ttyUSB1']
            
            for port in arduino_ports:
                try:
                    self.ser = serial.Serial(port, 115200, timeout=1)
                    time.sleep(2)  # Let Arduino reset
                    print(f"Connected to Arduino on {port}")
                    return True
                except:
                    if self.ser:
                        self.ser.close()
                    continue
            
            print("No Arduino found")
            return False
        except Exception as e:
            print(f"Serial connection error: {e}")
            return False

    def compute_angles(self, hand_x, hand_y):
        """Compute pan and tilt angles from hand position."""
        # Compute errors
        ex = 0.5 - hand_x  # Pan error
        ey = hand_y - 0.5  # Tilt error
        
        # Apply proportional control with larger scaling to bypass deadband
        pan_delta = -self.kp * ex * 80  # Larger scale movement
        tilt_delta = self.kp * ey * 60  # Larger scale movement
        
        # Update angles
        new_pan = self.pan_angle + pan_delta
        new_tilt = self.tilt_angle + tilt_delta
        
        # Clamp angles
        new_pan = max(20, min(160, new_pan))
        new_tilt = max(10, min(80, new_tilt))
        
        return int(new_pan), int(new_tilt)

    def send_servo_command(self, pan, tilt):
        """Send pan,tilt command to Arduino."""
        if self.ser and self.ser.is_open:
            try:
                command = f"{pan},{tilt}\n"
                self.ser.write(command.encode())
                self.ser.flush()
                print(f"Sent: {command.strip()}")  # Debug output
            except Exception as e:
                print(f"Serial error: {e}")

    def run(self):
        """Main tracking loop."""
        if not self.initialize_camera():
            return
        
        if not self.connect_serial():
            print("Running without Arduino (display only)")
        
        print("Balanced Dual Servo Tracker Started")
        print("Press ESC to exit")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Skip frames for performance
                self.frame_count += 1
                if self.frame_count % self.frame_skip != 0:
                    continue
                
                # Flip frame
                frame = cv2.flip(frame, 1)
                
                # Process with MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                current_time = time.time()
                
                if results.multi_hand_landmarks and (current_time - self.last_update) > self.update_interval:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    # Use index finger tip (landmark 8) instead of wrist (landmark 0)
                    index_tip = hand_landmarks.landmark[8]
                    hand_x = index_tip.x
                    hand_y = index_tip.y
                    
                    # Compute angles
                    new_pan, new_tilt = self.compute_angles(hand_x, hand_y)
                    
                    # Only update if angles changed significantly (bypass deadband)
                    if abs(new_pan - self.pan_angle) > 3 or abs(new_tilt - self.tilt_angle) > 3:
                        self.pan_angle = new_pan
                        self.tilt_angle = new_tilt
                        self.send_servo_command(self.pan_angle, self.tilt_angle)
                        self.last_update = current_time
                        
                        print(f"Hand: ({hand_x:.2f}, {hand_y:.2f}) -> Servos: ({self.pan_angle}°, {self.tilt_angle}°)")
                
                # Draw hand landmarks
                if results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, results.multi_hand_landmarks[0], 
                        self.mp_hands.HAND_CONNECTIONS)
                    
                    # Draw index finger tip indicator
                    h, w = frame.shape[:2]
                    index_tip = results.multi_hand_landmarks[0].landmark[8]
                    tip_x = int(index_tip.x * w)
                    tip_y = int(index_tip.y * h)
                    
                    # Draw a bright red circle at the index finger tip
                    cv2.circle(frame, (tip_x, tip_y), 8, (0, 0, 255), -1)  # Red filled circle
                    cv2.circle(frame, (tip_x, tip_y), 12, (255, 255, 255), 2)  # White outline
                
                # Draw center lines
                h, w = frame.shape[:2]
                center_x = w // 2
                center_y = h // 2
                
                # Vertical center line
                cv2.line(frame, (center_x, 0), (center_x, h), (255, 255, 0), 2)
                # Horizontal center line
                cv2.line(frame, (0, center_y), (w, center_y), (255, 255, 0), 2)
                
                # Draw center cross
                cross_size = 20
                cv2.line(frame, (center_x - cross_size, center_y), (center_x + cross_size, center_y), (255, 255, 0), 3)
                cv2.line(frame, (center_x, center_y - cross_size), (center_x, center_y + cross_size), (255, 255, 0), 3)
                
                # Draw info
                cv2.putText(frame, f"Pan: {self.pan_angle}°", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Tilt: {self.tilt_angle}°", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Kp: {self.kp}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Show frame
                cv2.imshow('Balanced Dual Servo Tracker', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
                    
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.cap:
            self.cap.release()
        if self.ser and self.ser.is_open:
            self.ser.close()
        cv2.destroyAllWindows()
        print("Resources cleaned up")

def main():
    parser = argparse.ArgumentParser(description="Balanced Dual Servo Tracker")
    parser.add_argument("--camera-index", type=int, help="Camera index")
    parser.add_argument("--camera-path", type=str, help="Camera path")
    parser.add_argument("--kp", type=float, default=0.5, help="Proportional gain")
    args = parser.parse_args()
    
    tracker = BalancedDualTracker(args.camera_index, args.camera_path, args.kp)
    tracker.run()

if __name__ == "__main__":
    main()
