#include <Servo.h>

// Servo pins
const int PAN_SERVO_PIN = 9;
const int TILT_SERVO_PIN = 10;

// Servo objects
Servo panServo;
Servo tiltServo;

void setup() {
  Serial.begin(115200);
  
  // Initialize servos
  panServo.attach(PAN_SERVO_PIN);
  tiltServo.attach(TILT_SERVO_PIN);
  
  // Center servos on startup
  panServo.write(90);
  tiltServo.write(45);
  delay(1000);
  
  Serial.println("Simple Servo Test Ready");
  Serial.println("Send: PAN\\n or PAN,TILT\\n");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    if (input.length() > 0) {
      processCommand(input);
    }
  }
}

void processCommand(String command) {
  int commaIndex = command.indexOf(',');
  
  if (commaIndex == -1) {
    // Single value: PAN only
    int panAngle = command.toInt();
    panAngle = constrain(panAngle, 0, 180);
    panServo.write(panAngle);
    Serial.print("Pan: ");
    Serial.println(panAngle);
  } else {
    // Two values: PAN,TILT
    String panStr = command.substring(0, commaIndex);
    String tiltStr = command.substring(commaIndex + 1);
    
    int panAngle = panStr.toInt();
    int tiltAngle = tiltStr.toInt();
    
    panAngle = constrain(panAngle, 0, 180);
    tiltAngle = constrain(tiltAngle, 0, 90);
    
    panServo.write(panAngle);
    tiltServo.write(tiltAngle);
    
    Serial.print("Pan: ");
    Serial.print(panAngle);
    Serial.print(", Tilt: ");
    Serial.println(tiltAngle);
  }
}
