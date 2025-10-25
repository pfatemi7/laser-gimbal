#!/usr/bin/env python3
"""
Final working dual servo tracker using the correct ST_Servo method
"""

import cv2
import mediapipe as mp
import serial
import time
import struct
import math

class STServo:
    def __init__(self, port='/dev/ttyACM1', baudrate=1000000):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        
    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"Connected to {self.port} at {self.baudrate} baud")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        if self.ser:
            self.ser.close()
    
    def write_buf(self, servo_id, mem_addr, data, data_len, instruction):
        """Write buffer using correct ST protocol"""
        if not self.ser:
            return False
            
        # Calculate message length
        msg_len = 2  # Base length
        if data:
            msg_len += data_len + 1  # +1 for mem_addr
        
        # Build packet header
        packet = bytes([0xFF, 0xFF, servo_id, msg_len, instruction])
        
        # Add memory address if we have data
        if data:
            packet += bytes([mem_addr])
            packet += data
        
        # Calculate checksum
        checksum = servo_id + msg_len + instruction
        if data:
            checksum += mem_addr
            for byte in data:
                checksum += byte
        
        # Add checksum (inverted)
        packet += bytes([~checksum & 0xFF])
        
        try:
            self.ser.write(packet)
            time.sleep(0.01)
            return True
        except Exception as e:
            print(f"Write error: {e}")
            return False
    
    def ping(self, servo_id):
        """Ping servo using correct protocol"""
        if self.write_buf(servo_id, 0, None, 0, 0x01):
            time.sleep(0.1)
            if self.ser.in_waiting > 0:
                response = self.ser.read(self.ser.in_waiting)
                return True
        return False
    
    def write_pos(self, servo_id, position, speed=0, time_ms=1500):
        """Write position using correct protocol"""
        # Convert position, speed, time to bytes (little endian)
        data = struct.pack('<HHH', position, time_ms, speed)
        
        # Write to goal position address (0x2A)
        return self.write_buf(servo_id, 0x2A, data, 6, 0x03)  # 0x03 = WRITE instruction
    
    def enable_torque(self, servo_id, enable=True):
        """Enable/disable torque"""
        value = 1 if enable else 0
        data = bytes([value])
        return self.write_buf(servo_id, 0x28, data, 1, 0x03)  # 0x28 = torque enable address
    
    def set_position_mode(self, servo_id):
        """Set servo to position mode"""
        data = bytes([0x00])  # 0x00 = position mode
        return self.write_buf(servo_id, 0x0B, data, 1, 0x03)  # 0x0B = mode address

def main():
    print("=== WORKING DUAL SERVO TRACKER (FINAL) ===")
    
    # Setup servo
    servo = STServo()
    if not servo.connect():
        return
    
    # Setup MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    
    # Setup camera
    cap = cv2.VideoCapture(2)
    if not cap.isOpened():
        print("Camera failed!")
        return
    print("✅ Camera ready")
    
    # Check which servos are available
    print("\n1. Checking available servos...")
    available_servos = []
    for servo_id in range(1, 6):
        if servo.ping(servo_id):
            available_servos.append(servo_id)
            print(f" Servo ID {servo_id} found")
        else:
            print(f" Servo ID {servo_id} not found")
    
    if not available_servos:
        print(" No servos found!")
        return
    
    # Setup servos
    print(f"\n2. Setting up {len(available_servos)} servos...")
    for servo_id in available_servos:
        print(f"Setting up servo {servo_id}...")
        servo.enable_torque(servo_id, True)
        time.sleep(0.1)
        servo.set_position_mode(servo_id)
        time.sleep(0.1)
        servo.write_pos(servo_id, 2048, 200, 1000)  # Center
        time.sleep(0.5)
    
    print(" Servos ready!")
    
    # Assign servos
    pan_servo = available_servos[0] if len(available_servos) > 0 else None
    tilt_servo = available_servos[1] if len(available_servos) > 1 else available_servos[0]
    
    print(f"Pan servo: ID {pan_servo}")
    print(f"Tilt servo: ID {tilt_servo}")
    
    print("\n3. Starting finger tracking...")
    print("Show your hand to the camera!")
    print("Press 'q' to quit")
    
    # FAST but SMOOTH PID parameters
    pan_kp = 0.20  #
    tilt_kp = 0.20  # 
    pan_deadband = 3   # 
    tilt_deadband = 4  # 
    
    # Light smoothing for stability
    smoothing_factor = 0.4  # Some smoothing to reduce jitter
    
    pan_pos = 2048
    tilt_pos = 2048
    
    # Search mode variables
    search_mode = False
    search_direction = 1  # 1 for right, -1 for left
    search_speed = 50  # Speed for search movement
    search_center_tilt = 1800  # Look slightly above center
    search_range = 1000  # How far to scan left/right from center
    search_start_time = 0
    last_hand_detected = 0
    last_search_move = 0  # Time of last search movement
    transition_from_search = False  # Flag to prevent jumping during transition
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            continue
        
        frame_count += 1
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        center_x, center_y = width // 2, height // 2
        
        # Draw center crosshair
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 2)
        
        # Process with MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            print(f" Frame {frame_count}: Hand detected!")
            if search_mode:
                print("🔍 Exiting search mode - following hand immediately")
                search_mode = False  # Exit search mode
                transition_from_search = True  # Set flag to prevent jumping
                # Only reset pan to center, keep current tilt position
                pan_pos = 2048
                # Don't reset tilt_pos - keep current position to maintain view of hand
            last_hand_detected = time.time()
            
            for hand_landmarks in results.multi_hand_landmarks:
                # Track wrist position directly
                wrist = hand_landmarks.landmark[0]
                middle_base = hand_landmarks.landmark[13]
                
                # Calculate hand size for distance compensation
                # Use distance between wrist and middle finger base as hand size reference
                hand_size = ((wrist.x - middle_base.x) ** 2 + (wrist.y - middle_base.y) ** 2) ** 0.5
                
                # Distance compensation: adjust sensitivity based on hand size
                # Larger hand (closer) = less sensitive, smaller hand (farther) = more sensitive
                distance_factor = max(0.5, min(2.0, 0.1 / max(hand_size, 0.01)))  # Clamp between 0.5 and 2.0
                
                wrist_x = int(wrist.x * width)
                wrist_y = int(wrist.y * height)
                
                # Calculate errors
                x_error = wrist_x - center_x
                y_error = wrist_y - center_y + 15  # Offset correction
                
                # Draw wrist position
                cv2.circle(frame, (wrist_x, wrist_y), 10, (0, 0, 255), -1)
                cv2.circle(frame, (wrist_x, wrist_y), 15, (255, 255, 255), 2)
                
                # Update servo positions with distance compensation and smoothing
                if not transition_from_search:  # Only move servos if not in transition
                    if abs(x_error) > pan_deadband and pan_servo:  # Pan (horizontal) - more precise
                        # Apply distance compensation to PID gain
                        adjusted_pan_kp = pan_kp * distance_factor
                        # Add extra precision for small horizontal errors
                        if abs(x_error) < 20:  # Fine adjustment for small errors
                            adjusted_pan_kp *= 1.5
                        pan_delta = int(x_error * adjusted_pan_kp)
                        new_pan_pos = max(0, min(4095, pan_pos - pan_delta))
                        # Apply smoothing
                        pan_pos = int(pan_pos * smoothing_factor + new_pan_pos * (1 - smoothing_factor))
                        servo.write_pos(pan_servo, pan_pos, 1023, 80)  # Fast but smooth
                        print(f"  Pan: {pan_pos} (error: {x_error}, dist_factor: {distance_factor:.2f})")
                    
                    if abs(y_error) > tilt_deadband and tilt_servo:  # Tilt (vertical)
                        # Apply distance compensation to PID gain
                        adjusted_tilt_kp = tilt_kp * distance_factor
                        tilt_delta = int(y_error * adjusted_tilt_kp)
                        new_tilt_pos = max(0, min(4095, tilt_pos + tilt_delta))
                        # Apply smoothing
                        tilt_pos = int(tilt_pos * smoothing_factor + new_tilt_pos * (1 - smoothing_factor))
                        servo.write_pos(tilt_servo, tilt_pos, 1023, 80)  # Fast but smooth
                        print(f"  Tilt: {tilt_pos} (error: {y_error}, dist_factor: {distance_factor:.2f})")
                else:
                    print("🔍 Transition from search - skipping servo movement")
                    # Reset flag after a few frames to resume normal tracking
                    if frame_count % 5 == 0:  # Every 5 frames
                        transition_from_search = False
                        print("🔍 Resuming normal tracking")
                
                # Draw hand landmarks
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            # No hand detected - check if we should enter search mode
            current_time = time.time()
            if current_time - last_hand_detected > 2.0:  # 2 seconds without hand
                if not search_mode:
                    search_mode = True
                    search_start_time = current_time
                    print(" Entering search mode - scanning for hands...")
                
                # Search mode: continuous left-right scanning
                if search_mode:
                    current_time = time.time()
                    
                    # Set tilt to look slightly above center
                    if tilt_servo:
                        servo.write_pos(tilt_servo, search_center_tilt, 200, 500)
                    
                    # Create smooth periodic left-right motion
                    search_center = 2048  # Center position
                    search_period = 4.0  # 4 seconds for full left-right cycle
                    
                    # Calculate position using sine wave for smooth periodic motion
                    time_in_period = (current_time - search_start_time) % search_period
                    phase = (time_in_period / search_period) * 2 * 3.14159  # 0 to 2π
                    search_offset = int(search_range * 0.5 * math.sin(phase))
                    search_pan = search_center + search_offset
                    
                    # Move pan servo in smooth periodic pattern
                    if pan_servo:
                        servo.write_pos(pan_servo, search_pan, search_speed, 100)
                        pan_pos = search_pan  # Update pan_pos to prevent bounce-back
                    
                    # Show search progress every 0.5 seconds
                    if current_time - last_search_move > 0.5:
                        direction_text = "right" if search_offset > 0 else "left" if search_offset < 0 else "center"
                        print(f"🔍 Searching: pan={search_pan}, moving {direction_text}")
                        last_search_move = current_time
            else:
                if frame_count % 30 == 0:  # Every second
                    print(f"Frame {frame_count}: No hand detected (waiting for search mode)")
        
        # Show status
        if results.multi_hand_landmarks:
            status = "HAND DETECTED"
            color = (0, 255, 0)
        elif search_mode:
            status = "SEARCH MODE"
            color = (255, 255, 0)  # Yellow for search mode
        else:
            status = "NO HAND"
            color = (0, 0, 255)
        
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.putText(frame, f"Frame: {frame_count}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Pan: {pan_pos}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Tilt: {tilt_pos}", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Show distance compensation info if hand is detected
        if results.multi_hand_landmarks:
            try:
                cv2.putText(frame, f"Distance Factor: {distance_factor:.2f}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            except:
                pass  # distance_factor might not be defined if no hand detected
        
        cv2.imshow('Working Dual Servo Tracker', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    servo.disconnect()
    print(" Tracking stopped")

if __name__ == "__main__":
    main()
