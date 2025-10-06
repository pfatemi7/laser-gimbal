#!/usr/bin/env python3
"""
Test script for dual-axis servo control
Tests both pan and tilt servo communication
"""

import serial
import time

def test_dual_servo():
    print("Dual Servo Test")
    print("==============")
    
    try:
        # Connect to Arduino
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        time.sleep(2)
        
        print("Connected to Arduino")
        print("Testing dual-axis commands...")
        
        # Test 1: Pan only (backward compatibility)
        print("\n1. Testing pan-only command: 90")
        ser.write('90\n'.encode())
        ser.flush()
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"Response: {response.decode()}")
        else:
            print("No response")
        
        # Test 2: Pan and tilt
        print("\n2. Testing pan,tilt command: 120,45")
        ser.write('120,45\n'.encode())
        ser.flush()
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"Response: {response.decode()}")
        else:
            print("No response")
        
        # Test 3: Center position
        print("\n3. Testing center command: 90,45")
        ser.write('90,45\n'.encode())
        ser.flush()
        time.sleep(1)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"Response: {response.decode()}")
        else:
            print("No response")
        
        ser.close()
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_dual_servo()
