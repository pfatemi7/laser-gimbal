#!/bin/bash
# Setup script for visual servo tracker

echo "Visual Servo Tracker Setup"
echo "=========================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if not already installed
echo "Installing dependencies..."
pip install mediapipe opencv-python pyserial

echo ""
echo "Setup complete! To run the visual servo tracker:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Run the tracker: python3 visual_servo_tracker.py"
echo ""
echo "Or use the quick launcher: python3 run_visual_servo.py"
