#!/usr/bin/env python3
"""
Check both servos after ID setup
"""

import serial
import time
import struct

class STServo:
    def __init__(self, port='/dev/ttyACM0', baudrate=1000000):
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
    
    def test_servo_movement(self, servo_id, name):
        """Test servo movement"""
        print(f"Testing {name} servo (ID {servo_id})...")
        
        # Enable torque
        torque_data = bytes([0x01])
        self.write_buf(servo_id, 0x28, torque_data, 1, 0x03)
        time.sleep(0.1)
        
        # Set position mode
        mode_data = bytes([0x00])
        self.write_buf(servo_id, 0x0B, mode_data, 1, 0x03)
        time.sleep(0.1)
        
        # Test movement
        positions = [2048, 1024, 3072, 2048]
        for pos in positions:
            data = struct.pack('<HHH', pos, 1000, 200)
            self.write_buf(servo_id, 0x2A, data, 6, 0x03)
            print(f"  Moving to position {pos}")
            time.sleep(1)

def main():
    print("=== CHECKING BOTH SERVOS ===")
    print("Make sure both servos are connected!")
    print()
    
    servo = STServo()
    if not servo.connect():
        return
    
    # Check all servo IDs
    print("1. CHECKING ALL SERVO IDs...")
    found_servos = []
    for servo_id in range(1, 6):
        if servo.ping(servo_id):
            found_servos.append(servo_id)
            print(f"✅ Servo ID {servo_id} found")
        else:
            print(f"❌ Servo ID {servo_id} not found")
    
    print(f"Found servos: {found_servos}")
    print()
    
    if len(found_servos) == 0:
        print("❌ No servos found! Check connections and power.")
        return
    
    if len(found_servos) == 1:
        print("⚠️  Only one servo found!")
        print("Please connect both servos and run this script again.")
        return
    
    if len(found_servos) > 2:
        print("⚠️  More than 2 servos found!")
        print("This might cause conflicts. Please disconnect extra servos.")
        return
    
    # Test both servos
    print("2. TESTING BOTH SERVOS...")
    
    # Assign servos
    servo_1 = None
    servo_2 = None
    
    for servo_id in found_servos:
        if servo_id == 1:
            servo_1 = servo_id
        elif servo_id == 2:
            servo_2 = servo_id
    
    if servo_1:
        servo.test_servo_movement(servo_1, "Pan (horizontal)")
        print()
    
    if servo_2:
        servo.test_servo_movement(servo_2, "Tilt (vertical)")
        print()
    
    # Test independent movement
    print("3. TESTING INDEPENDENT MOVEMENT...")
    if servo_1 and servo_2:
        print("Moving Pan servo (ID 1) to position 1024...")
        data = struct.pack('<HHH', 1024, 1000, 200)
        servo.write_buf(servo_1, 0x2A, data, 6, 0x03)
        time.sleep(2)
        
        print("Moving Tilt servo (ID 2) to position 3072...")
        data = struct.pack('<HHH', 3072, 1000, 200)
        servo.write_buf(servo_2, 0x2A, data, 6, 0x03)
        time.sleep(2)
        
        print("Moving both servos to center...")
        data = struct.pack('<HHH', 2048, 1000, 200)
        servo.write_buf(servo_1, 0x2A, data, 6, 0x03)
        servo.write_buf(servo_2, 0x2A, data, 6, 0x03)
        time.sleep(2)
        
        print("✅ Independent movement test completed!")
        print("Did you see the servos moving independently?")
    
    servo.disconnect()
    print("\n✅ Servo check completed!")

if __name__ == "__main__":
    main()