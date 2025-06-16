#include <WiFi.h>
#include <esp_now.h>

// Dynamixel pins
#define DXL_TX 20
#define DXL_RX 21
#define TX_ENABLE_PIN 2

HardwareSerial DxlSerial(0);

// MAC van Pi-side ESP
uint8_t peerAddress[] = {0x24, 0xEC, 0x4A, 0xCA, 0x82, 0x58};

void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  if (len < 1) return;

  uint8_t dataLen = data[len - 1];
  if (dataLen == 0 || dataLen > len - 1) return;

  // Zet TX-enable aan en stuur data naar Dynamixel
  digitalWrite(TX_ENABLE_PIN, HIGH);
  DxlSerial.write(data, dataLen);
  DxlSerial.flush();

  digitalWrite(TX_ENABLE_PIN, LOW);

  // Wacht op eerste respons-byte max 2 ms
  unsigned long waitStart = micros();
  while (!DxlSerial.available()) {
    if (micros() - waitStart > 2000) return;
  }

  // Lees respons met 500 µs timeout na laatste byte
  unsigned long start = micros();
  const unsigned long timeout = 500;
  uint8_t response[16];
  int bytesRead = 0;

  while (micros() - start < timeout) {
    if (DxlSerial.available()) {
      response[bytesRead++] = DxlSerial.read();
      start = micros();
      if (bytesRead >= sizeof(response)) break;
    }
  }

  if (bytesRead > 0) {
    esp_now_send(peerAddress, response, bytesRead);
  }
}

void setup() {
  Serial.begin(115200);
  DxlSerial.begin(1000000, SERIAL_8N1, -1, -1);
  pinMode(TX_ENABLE_PIN, OUTPUT);
  digitalWrite(TX_ENABLE_PIN, LOW);

  WiFi.mode(WIFI_STA);
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init mislukt");
    return;
  }

  esp_now_register_recv_cb(onDataRecv);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, peerAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Peer toevoegen mislukt");
    return;
  }

  Serial.println("Motor-side ESP klaar.");
}

void loop() {
  // niets
}
