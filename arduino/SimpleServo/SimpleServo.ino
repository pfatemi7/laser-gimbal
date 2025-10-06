#include <Servo.h>

Servo servo;
int servoPin = 9;

void setup() {
  Serial.begin(115200);
  servo.attach(servoPin);
  
  // Center the servo on startup
  servo.write(90);
  delay(1000);
  
  Serial.println("Simple Servo Ready");
  Serial.println("Send angle (0-180)");
}

void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    
    int angle = input.toInt();
    
    // Clamp angle to valid range (0-180 degrees)
    if (angle < 0) angle = 0;
    if (angle > 180) angle = 180;
    
    servo.write(angle);
    Serial.print("Servo moved to: ");
    Serial.println(angle);
  }
}