#!/usr/bin/env python3
"""
Quick launcher for visual servo tracker with common configurations
"""

import subprocess
import sys
import os

def main():
    print("Visual Servo Hand Tracker Launcher")
    print("==================================")
    print()
    print("Available configurations:")
    print("1. Auto-detect external camera (default)")
    print("2. Use camera index 1")
    print("3. Use camera path /dev/video1")
    print("4. Use camera index 0 (built-in)")
    print("5. Custom configuration")
    print()
    
    choice = input("Select option (1-5): ").strip()
    
    if choice == "1":
        # Auto-detect external camera
        cmd = [sys.executable, "visual_servo_tracker.py"]
    elif choice == "2":
        # Camera index 1
        cmd = [sys.executable, "visual_servo_tracker.py", "--camera-index", "1"]
    elif choice == "3":
        # Camera path /dev/video1
        cmd = [sys.executable, "visual_servo_tracker.py", "--camera-path", "/dev/video1"]
    elif choice == "4":
        # Camera index 0
        cmd = [sys.executable, "visual_servo_tracker.py", "--camera-index", "0"]
    elif choice == "5":
        # Custom configuration
        print("\nCustom configuration:")
        camera_index = input("Camera index (or press Enter to skip): ").strip()
        camera_path = input("Camera path (or press Enter to skip): ").strip()
        kp = input("Proportional gain (default 0.5): ").strip() or "0.5"
        ki = input("Integral gain (default 0.0): ").strip() or "0.0"
        enable_integral = input("Enable integral control? (y/N): ").strip().lower() == 'y'
        
        cmd = [sys.executable, "visual_servo_tracker.py"]
        if camera_index:
            cmd.extend(["--camera-index", camera_index])
        if camera_path:
            cmd.extend(["--camera-path", camera_path])
        cmd.extend(["--kp", kp, "--ki", ki])
        if enable_integral:
            cmd.append("--enable-integral")
    else:
        print("Invalid choice. Using default configuration.")
        cmd = [sys.executable, "visual_servo_tracker.py"]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running tracker: {e}")
    except FileNotFoundError:
        print("Error: visual_servo_tracker.py not found in current directory")

if __name__ == "__main__":
    main()
