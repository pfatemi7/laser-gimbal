/*
 * LIDAR-Lite V3 Distance Sensor Reporter
 * 
 * Hardware Setup:
 * - Arduino UNO: SDA=A4, SCL=A5
 * - 5V and GND to the sensor
 * - Add 680-1000 µF capacitor across 5V/GND at the sensor for stability
 * - Default 7-bit I2C address: 0x62
 * 
 * Wiring:
 * LIDAR-Lite V3    Arduino UNO
 * VCC     ->      5V
 * GND     ->      GND
 * SDA     ->      A4 (SDA)
 * SCL     ->      A5 (SCL)
 * 
 * Libraries Required:
 * - Wire.h (built-in)
 * - LIDARLite.h (from https://github.com/garmin/LIDARLite_Arduino_Library)
 * 
 * Features:
 * - Reads distance at ~50 Hz
 * - Uses median of 3 readings for noise reduction
 * - Configurable I2C speed (100kHz or 400kHz)
 * - Serial commands for rate, averaging, and mode configuration
 * - Error handling for invalid readings
 */

#include <Wire.h>
#include <LIDARLite.h>

// Configuration constants
#define I2C_400KHZ 1        // Set to 1 for 400kHz, 0 for 100kHz
#define LOOP_HZ    50       // Target loop frequency
#define AVG_N      3        // Number of readings for median calculation
#define MAX_DISTANCE 4000   // Maximum valid distance in cm
#define MIN_DISTANCE 0      // Minimum valid distance in cm

// Global variables
LIDARLite lidar;
uint8_t currentRate = LOOP_HZ;
uint8_t currentAvg = AVG_N;
uint8_t currentMode = 0;
unsigned long lastCommandTime = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize I2C
  Wire.begin();
  
  // Set I2C clock speed
  if (I2C_400KHZ) {
    Wire.setClock(400000);
  } else {
    Wire.setClock(100000);
  }
  
  // Initialize LIDAR-Lite sensor
  // begin(0, true) - 0 = default address (0x62), true = fast I2C
  lidar.begin(0, I2C_400KHZ);
  
  // Configure sensor mode (0 = default mode)
  lidar.configure(currentMode);
  
  // Print banner with configuration info
  Serial.print("BANNER,LIDARLiteV3,addr=0x62,i2c=");
  Serial.print(I2C_400KHZ ? "400k" : "100k");
  Serial.print(",mode=lib,rate=");
  Serial.print(currentRate);
  Serial.println("Hz");
  
  // Small delay to ensure sensor is ready
  delay(100);
}

/**
 * Calculate median of three values
 * @param a First value
 * @param b Second value  
 * @param c Third value
 * @return Median value
 */
uint16_t median3(uint16_t a, uint16_t b, uint16_t c) {
  // Sort the three values to find median
  if (a > b) {
    uint16_t temp = a; a = b; b = temp;
  }
  if (b > c) {
    uint16_t temp = b; b = c; c = temp;
  }
  if (a > b) {
    uint16_t temp = a; a = b; b = temp;
  }
  return b; // b is now the median
}

/**
 * Take multiple distance readings and return median
 * @param numReadings Number of readings to take (1-7)
 * @return Median distance in cm, or 0 if error
 */
uint16_t getMedianDistance(uint8_t numReadings) {
  if (numReadings < 1 || numReadings > 7) {
    numReadings = 3; // Default to 3 readings
  }
  
  uint16_t readings[7];
  uint8_t validReadings = 0;
  
  // Take the specified number of readings
  for (uint8_t i = 0; i < numReadings; i++) {
    uint16_t distance = lidar.distance();
    
    // Check if reading is valid (non-zero and within reasonable range)
    if (distance > MIN_DISTANCE && distance <= MAX_DISTANCE) {
      readings[validReadings] = distance;
      validReadings++;
    }
    
    // Small delay between readings
    if (i < numReadings - 1) {
      delay(2);
    }
  }
  
  // If no valid readings, return 0
  if (validReadings == 0) {
    return 0;
  }
  
  // If only one valid reading, return it
  if (validReadings == 1) {
    return readings[0];
  }
  
  // If two valid readings, return average
  if (validReadings == 2) {
    return (readings[0] + readings[1]) / 2;
  }
  
  // For 3 or more readings, find median
  if (validReadings == 3) {
    return median3(readings[0], readings[1], readings[2]);
  }
  
  // For more than 3 readings, use bubble sort to find median
  // Sort the array
  for (uint8_t i = 0; i < validReadings - 1; i++) {
    for (uint8_t j = 0; j < validReadings - i - 1; j++) {
      if (readings[j] > readings[j + 1]) {
        uint16_t temp = readings[j];
        readings[j] = readings[j + 1];
        readings[j + 1] = temp;
      }
    }
  }
  
  // Return median (middle value)
  return readings[validReadings / 2];
}

/**
 * Process serial commands
 * Commands: RATE,<hz> | AVG,<n> | MODE,<m>
 */
void processSerialCommands() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("RATE,")) {
      int rate = command.substring(5).toInt();
      if (rate >= 10 && rate <= 100) {
        currentRate = rate;
        Serial.print("ACK,RATE,");
        Serial.println(currentRate);
      } else {
        Serial.println("ERR,RATE,invalid_range");
      }
    }
    else if (command.startsWith("AVG,")) {
      int avg = command.substring(4).toInt();
      if (avg >= 1 && avg <= 7) {
        currentAvg = avg;
        Serial.print("ACK,AVG,");
        Serial.println(currentAvg);
      } else {
        Serial.println("ERR,AVG,invalid_range");
      }
    }
    else if (command.startsWith("MODE,")) {
      int mode = command.substring(5).toInt();
      if (mode >= 0 && mode <= 5) {
        currentMode = mode;
        lidar.configure(currentMode);
        Serial.print("ACK,MODE,");
        Serial.println(currentMode);
      } else {
        Serial.println("ERR,MODE,invalid_range");
      }
    }
    else if (command == "STATUS") {
      Serial.print("STATUS,RATE=");
      Serial.print(currentRate);
      Serial.print(",AVG=");
      Serial.print(currentAvg);
      Serial.print(",MODE=");
      Serial.println(currentMode);
    }
    else if (command == "HELP") {
      Serial.println("Commands:");
      Serial.println("RATE,<10-100> - Set measurement rate");
      Serial.println("AVG,<1-7> - Set number of readings for median");
      Serial.println("MODE,<0-5> - Set sensor mode");
      Serial.println("STATUS - Show current settings");
      Serial.println("HELP - Show this help");
    }
    
    lastCommandTime = millis();
  }
}

void loop() {
  // Process any incoming serial commands
  processSerialCommands();
  
  // Get distance measurement using median of multiple readings
  uint16_t distance = getMedianDistance(currentAvg);
  
  // Determine status based on distance reading
  const char* status;
  if (distance == 0 || distance > MAX_DISTANCE) {
    status = "ERR";
    distance = 0; // Set to 0 for error cases
  } else {
    status = "OK";
  }
  
  // Print distance reading with timestamp
  Serial.print("DIST,");
  Serial.print(millis());
  Serial.print(",");
  Serial.print(distance);
  Serial.print(",");
  Serial.println(status);
  
  // Calculate delay to maintain target frequency
  // Account for processing time
  unsigned long loopTime = 1000 / currentRate;
  if (loopTime > 2) {
    delay(loopTime - 2); // Subtract ~2ms for processing overhead
  }
}
