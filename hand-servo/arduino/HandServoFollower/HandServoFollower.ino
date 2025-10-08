#include <Servo.h>

// Servo pins
const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

// Serial communication
const int BAUD_RATE = 115200;

// Smoothing and deadband
const int DEADBAND_DEGREES = 2;
const float SMOOTHING_ALPHA = 0.33;  // EMA smoothing factor

// Watchdog timeout
const unsigned long WATCHDOG_TIMEOUT_MS = 1000;

// Center positions
const int PAN_CENTER = 90;
const int TILT_CENTER = 45;

// Servo objects
Servo panServo;
Servo tiltServo;

// Current positions
float currentPanAngle = PAN_CENTER;
float currentTiltAngle = TILT_CENTER;

// Last command time
unsigned long lastCommandTime = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  
  // Initialize servos
  panServo.attach(PAN_SERVO_PIN);
  tiltServo.attach(TILT_SERVO_PIN);
  
  // Center servos on startup
  panServo.write(PAN_CENTER);
  tiltServo.write(TILT_CENTER);
  delay(1000);
  
  Serial.println("Dual Servo Controller Ready");
  Serial.println("Send: PAN\\n or PAN,TILT\\n");
  
  lastCommandTime = millis();
}

void loop() {
  // Check for serial data
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    if (input.length() > 0) {
      processCommand(input);
      lastCommandTime = millis();
    }
  }
  
  // Watchdog: return to center if no commands received
  if (millis() - lastCommandTime > WATCHDOG_TIMEOUT_MS) {
    returnToCenter();
    lastCommandTime = millis();
  }
}

void processCommand(String command) {
  int commaIndex = command.indexOf(',');
  
  if (commaIndex == -1) {
    // Single value: PAN only (backward compatibility)
    int panAngle = command.toInt();
    updatePanServo(panAngle);
  } else {
    // Two values: PAN,TILT
    String panStr = command.substring(0, commaIndex);
    String tiltStr = command.substring(commaIndex + 1);
    
    int panAngle = panStr.toInt();
    int tiltAngle = tiltStr.toInt();
    
    updatePanServo(panAngle);
    updateTiltServo(tiltAngle);
  }
}

void updatePanServo(int targetAngle) {
  // Clamp to valid range
  targetAngle = constrain(targetAngle, 0, 180);
  
  // Apply deadband
  if (abs(targetAngle - currentPanAngle) < DEADBAND_DEGREES) {
    return;
  }
  
  // Apply EMA smoothing
  currentPanAngle = currentPanAngle + SMOOTHING_ALPHA * (targetAngle - currentPanAngle);
  
  // Write to servo
  panServo.write(round(currentPanAngle));
  
  Serial.print("Pan: ");
  Serial.println(round(currentPanAngle));
}

void updateTiltServo(int targetAngle) {
  // Clamp to valid range (0-90 degrees)
  targetAngle = constrain(targetAngle, 0, 90);
  
  // Apply deadband
  if (abs(targetAngle - currentTiltAngle) < DEADBAND_DEGREES) {
    return;
  }
  
  // Apply EMA smoothing
  currentTiltAngle = currentTiltAngle + SMOOTHING_ALPHA * (targetAngle - currentTiltAngle);
  
  // Write to servo
  tiltServo.write(round(currentTiltAngle));
  
  Serial.print("Tilt: ");
  Serial.println(round(currentTiltAngle));
}

void returnToCenter() {
  // Gently return to center positions
  updatePanServo(PAN_CENTER);
  updateTiltServo(TILT_CENTER);
}