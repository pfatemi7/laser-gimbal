#!/usr/bin/env python3
"""
Setup servo IDs properly - one servo at a time
"""

import serial
import time
import struct

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
    
    def change_servo_id(self, old_id, new_id):
        """Change servo ID from old_id to new_id"""
        print(f"Changing servo ID from {old_id} to {new_id}...")
        
        # Step 1: Unlock EEPROM
        print("  Step 1: Unlocking EEPROM...")
        unlock_data = bytes([0x00])  # 0x00 = unlock
        if not self.write_buf(old_id, 0x30, unlock_data, 1, 0x03):
            print("  Failed to unlock EEPROM")
            return False
        time.sleep(0.1)
        
        # Step 2: Write new ID
        print("  Step 2: Writing new ID...")
        id_data = bytes([new_id])
        if not self.write_buf(old_id, 0x05, id_data, 1, 0x03):
            print("  Failed to write new ID")
            return False
        time.sleep(0.1)
        
        # Step 3: Lock EEPROM
        print("  Step 3: Locking EEPROM...")
        lock_data = bytes([0x01])  # 0x01 = lock
        if not self.write_buf(new_id, 0x30, lock_data, 1, 0x03):
            print("  Failed to lock EEPROM")
            return False
        time.sleep(0.1)
        
        print(f"  ✅ Servo ID changed from {old_id} to {new_id}")
        return True
    
    def test_servo_movement(self, servo_id):
        """Test servo movement"""
        print(f"Testing servo {servo_id} movement...")
        
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
    print("=== SERVO ID SETUP ===")
    print("This will help you set up servo IDs properly")
    print()
    
    servo = STServo()
    if not servo.connect():
        return
    
    # Step 1: Check current servo status
    print("1. CHECKING CURRENT SERVO STATUS...")
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
        print("✅ Only one servo found. This is perfect for setup!")
        current_id = found_servos[0]
        print(f"Current servo ID: {current_id}")
        
        # Ask user what ID they want
        print("\nWhat ID do you want for this servo?")
        print("1 = Pan servo (horizontal movement)")
        print("2 = Tilt servo (vertical movement)")
        
        try:
            new_id = int(input("Enter servo ID (1 or 2): "))
            if new_id in [1, 2]:
                if new_id != current_id:
                    servo.change_servo_id(current_id, new_id)
                    time.sleep(0.5)
                    
                    # Test the new ID
                    if servo.ping(new_id):
                        print(f"✅ Servo ID {new_id} is working!")
                        servo.test_servo_movement(new_id)
                    else:
                        print(f"❌ Servo ID {new_id} not responding")
                else:
                    print(f"Servo is already ID {new_id}")
                    servo.test_servo_movement(new_id)
            else:
                print("Invalid ID. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    elif len(found_servos) > 1:
        print("⚠️  Multiple servos found with the same ID!")
        print("This means they're both responding to the same commands.")
        print()
        print("SOLUTION:")
        print("1. Disconnect one servo")
        print("2. Change the connected servo's ID")
        print("3. Reconnect the other servo")
        print()
        print("Let's do this step by step...")
        
        # Find which ID they're all responding to
        common_id = found_servos[0]
        print(f"All servos are responding to ID {common_id}")
        
        print(f"\nStep 1: Disconnect one servo, then press Enter...")
        input("Press Enter when you've disconnected one servo...")
        
        # Check again
        print("Checking servos after disconnection...")
        remaining_servos = []
        for servo_id in range(1, 6):
            if servo.ping(servo_id):
                remaining_servos.append(servo_id)
                print(f"✅ Servo ID {servo_id} found")
        
        if len(remaining_servos) == 1:
            print("✅ Perfect! One servo connected.")
            current_id = remaining_servos[0]
            
            # Change this servo's ID
            new_id = 2 if current_id == 1 else 1
            print(f"Changing servo from ID {current_id} to ID {new_id}...")
            servo.change_servo_id(current_id, new_id)
            time.sleep(0.5)
            
            # Test the new ID
            if servo.ping(new_id):
                print(f"✅ Servo ID {new_id} is working!")
                servo.test_servo_movement(new_id)
            else:
                print(f"❌ Servo ID {new_id} not responding")
        else:
            print("❌ Still multiple servos found. Please disconnect more servos.")
    
    servo.disconnect()
    print("\n✅ Setup completed!")
    print("Now you can reconnect both servos and they should have different IDs.")

if __name__ == "__main__":
    main()
