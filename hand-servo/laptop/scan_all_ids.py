#!/usr/bin/env python3
"""
Scan for all possible servo IDs
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
            time.sleep(0.1)
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

def main():
    print("=== SCAN ALL SERVO IDs ===")
    print("Scanning for all possible servo IDs...")
    print()
    
    servo = STServo()
    if not servo.connect():
        return
    
    # Scan all possible IDs
    print("1. SCANNING ALL SERVO IDs...")
    found_servos = []
    
    for servo_id in range(0, 255):  # Scan all possible IDs
        if servo.ping(servo_id):
            found_servos.append(servo_id)
            print(f"✅ Servo ID {servo_id} found")
        else:
            if servo_id % 50 == 0:  # Show progress every 50 IDs
                print(f"  Scanned {servo_id} IDs...")
    
    print(f"\nFound servos: {found_servos}")
    print()
    
    if len(found_servos) == 0:
        print("❌ No servos found! Check connections and power.")
    elif len(found_servos) == 1:
        print("⚠️  Only one servo found!")
        print("This means both servos have the same ID.")
        print("You need to change one of them to a different ID.")
    elif len(found_servos) == 2:
        print("✅ Two servos found with different IDs!")
        print("This is perfect for dual servo control.")
    else:
        print(f"⚠️  {len(found_servos)} servos found!")
        print("This might cause conflicts.")
    
    servo.disconnect()
    print("\n✅ Scan completed!")

if __name__ == "__main__":
    main()
