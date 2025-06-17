#include <WiFi.h>
#include <esp_now.h>

typedef struct {
  uint8_t id;
  uint16_t distance;
} SensorData;

typedef struct {
  int x;
  int y;
  bool sw;
} JoystickData;

#define JOY1_X  2
#define JOY1_Y  3
#define JOY1_SW 6

#define JOY2_X  4
#define JOY2_Y  5
#define JOY2_SW 7

void OnDataRecv(const esp_now_recv_info_t *recvInfo, const uint8_t *incomingData, int len) {
  int numEntries = len / sizeof(SensorData);
  const SensorData* data = (const SensorData*)incomingData;

  for (int i = 0; i < numEntries; i++) {
    Serial1.print(data[i].id);
    Serial1.print(",");
    Serial1.print(data[i].distance);
    if (i < numEntries - 1) Serial1.print(",");
  }
  Serial1.print(",");

  JoystickData joy1, joy2;

  joy1.x = analogRead(JOY1_X);
  joy1.y = analogRead(JOY1_Y);
  joy1.sw = !digitalRead(JOY1_SW); 

  joy2.x = analogRead(JOY2_X);
  joy2.y = analogRead(JOY2_Y);
  joy2.sw = !digitalRead(JOY2_SW);  

  Serial1.print("J1:");
  Serial1.print(joy1.x);
  Serial1.print(",");
  Serial1.print(joy1.y);
  Serial1.print(",");
  Serial1.print(joy1.sw);
  Serial1.print(",");

  Serial1.print("J2:");
  Serial1.print(joy2.x);
  Serial1.print(",");
  Serial1.print(joy2.y);
  Serial1.print(",");
  Serial1.print(joy2.sw);

  Serial1.println();
}

void setup() {
  Serial.begin(115200);      
  Serial1.begin(115200, SERIAL_8N1, 20, 21); 

  pinMode(JOY1_SW, INPUT_PULLUP);
  pinMode(JOY2_SW, INPUT_PULLUP);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed!");
    return;
  }

  esp_now_register_recv_cb(OnDataRecv);

  Serial.println("Receiver ready.");
  Serial1.println("Receiver ready.");  
}

void loop() {
}
