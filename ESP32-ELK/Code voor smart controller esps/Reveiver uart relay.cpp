#include <WiFi.h>
#include <esp_now.h>

#define UART_RX 20
#define UART_TX 21
#define PI_TX_ENABLE_PIN 2

HardwareSerial PiSerial(1);

// MAC van motor-side ESP
uint8_t peerAddress[] = {0x24, 0xEC, 0x4A, 0xC9, 0x5C, 0xD4};

volatile bool triggerSend = false;
uint8_t uartRxBuffer[256];
volatile uint16_t uartRxIndex = 0;

void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  PiSerial.write(data, len);
}

void IRAM_ATTR pi_tx_enable_interrupt_handler() {
  triggerSend = true;
}

void setup() {
  Serial.begin(115200);
  PiSerial.begin(1000000, SERIAL_8N1, UART_RX, UART_TX);
  WiFi.mode(WIFI_STA);

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_recv_cb(onDataRecv);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, peerAddress, 6);
  peerInfo.channel = 0;
  peerInfo.encrypt = false;
  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Error adding peer");
    return;
  }

  pinMode(PI_TX_ENABLE_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PI_TX_ENABLE_PIN), pi_tx_enable_interrupt_handler, RISING);

  Serial.println("ESP-NOW initialized and Pi TX enable interrupt attached.");
}

void loop() {
  if (triggerSend) {
    triggerSend = false; // Reset immediately
    uartRxIndex = 0; // Reset buffer index

    unsigned long readStartTime = millis();
    while (millis() - readStartTime < 50) { // Read for up to 50 milliseconds
      if (PiSerial.available() > 0 && uartRxIndex < sizeof(uartRxBuffer)) {
        uartRxBuffer[uartRxIndex++] = PiSerial.read();
        readStartTime = millis(); // Reset timeout on each received byte
      }
      delayMicroseconds(10);
    }

    if (uartRxIndex > 0) {
      uint8_t sendBuffer[uartRxIndex + 1];
      memcpy(sendBuffer, uartRxBuffer, uartRxIndex);
      sendBuffer[uartRxIndex] = uartRxIndex;
      esp_err_t result = esp_now_send(peerAddress, sendBuffer, uartRxIndex + 1);
      if (result != ESP_OK) {
        Serial.print("Error sending data: ");
        Serial.println(esp_err_to_name(result));
        triggerSend = true; // Consider error handling
      }
    }
  }
  delay(1);
}