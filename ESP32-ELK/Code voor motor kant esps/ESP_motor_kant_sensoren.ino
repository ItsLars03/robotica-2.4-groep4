#include <Wire.h>
#include <VL53L0X.h>
#include <WiFi.h>
#include <esp_now.h>
#include <AS5600.h> 

#define XSHUT_1 3
#define XSHUT_2 4
#define XSHUT_3 5

VL53L0X distanceSensors[3]; 
uint8_t distanceSensorPins[3] = {XSHUT_1, XSHUT_2, XSHUT_3}; 
uint8_t distanceSensorAddresses[3] = {0x30, 0x31, 0x29}; 
uint8_t numDistanceSensors = 3; 

AS5600 as5600; 

uint8_t receiverMac[] = {0x98, 0x3D, 0xAE, 0xAB, 0xE0, 0x74};

struct CombinedSensorData {
  uint16_t distance[3]; 
  uint16_t encoderAngle;  
};

void setup() {
  Serial.begin(115200);
  Wire.begin();

  WiFi.mode(WIFI_STA); 
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    return;
  }

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, receiverMac, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add peer");
    return;
  }
  Serial.println("ESP-NOW initialized and peer added.");

  pinMode(XSHUT_1, OUTPUT); 
  pinMode(XSHUT_2, OUTPUT); 
  pinMode(XSHUT_3, OUTPUT);

  digitalWrite(XSHUT_1, LOW);
  digitalWrite(XSHUT_2, LOW);
  digitalWrite(XSHUT_3, LOW);
  delay(10);

  digitalWrite(XSHUT_1, HIGH); 
  delay(10);
  distanceSensors[0].init(); 
  distanceSensors[0].setAddress(distanceSensorAddresses[0]); 
  distanceSensors[0].startContinuous(); 
  Serial.print("VL53L0X Sensor 0 initialized with address 0x");
  Serial.println(distanceSensorAddresses[0], HEX);
  
  digitalWrite(XSHUT_2, HIGH);
  delay(10);
  distanceSensors[1].init();
  distanceSensors[1].setAddress(distanceSensorAddresses[1]);
  distanceSensors[1].startContinuous();
  Serial.print("VL53L0X Sensor 1 initialized with address 0x");
  Serial.println(distanceSensorAddresses[1], HEX);

  digitalWrite(XSHUT_3, HIGH); 
  delay(10);
  distanceSensors[2].init(); 
  distanceSensors[2].setAddress(distanceSensorAddresses[2]);
  distanceSensors[2].startContinuous();
  Serial.print("VL53L0X Sensor 2 initialized with address 0x");
  Serial.println(distanceSensorAddresses[2], HEX);


  if (!as5600.begin()) { 
    Serial.println("AS5600 not found or initialization failed!");
    Serial.println("Check wiring (SDA, SCL, VCC, GND) and ensure the magnet is centered and close to the sensor (1-3mm).");
  } else {
    Serial.println("AS5600 encoder initialized.");
  }
}

void loop() {
  CombinedSensorData dataToSend; 

  for (int i = 0; i < numDistanceSensors; i++) {
    dataToSend.distance[i] = distanceSensors[i].readRangeContinuousMillimeters();

    Serial.print("VL53L0X Sensor ");
    Serial.print(i);
    Serial.print(": ");
    Serial.print(dataToSend.distance[i]);
    Serial.println(" mm");
  }

  dataToSend.encoderAngle = as5600.rawAngle(); 

  Serial.print("AS5600 Encoder Angle: ");
  Serial.print(dataToSend.encoderAngle);
  Serial.println(" (0-4095)");

  esp_err_t result = esp_now_send(receiverMac, (uint8_t *)&dataToSend, sizeof(dataToSend));

  if (result == ESP_OK) {
    Serial.println("ESP-NOW send success");
  } else {
    Serial.println("ESP-NOW send failed!");
  }

  delay(100); 
}
