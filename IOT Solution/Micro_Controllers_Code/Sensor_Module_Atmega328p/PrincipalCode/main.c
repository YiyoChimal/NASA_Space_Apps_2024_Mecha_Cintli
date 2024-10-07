/*
 * PrincipalCode.c
 *
 * Created: 06/10/2024 09:16:14 p. m.
 * Author : Francisco Rios
 */ 

#include <avr/io.h>

#include <SoftwareSerial.h>
#include <Wire.h>
#include <EEPROM.h>
#include <UIPEthernet.h>  // Library for the ENC28J60 module
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128  // Width of the OLED
#define SCREEN_HEIGHT 64  // Height of the OLED
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define LORA_TX_PIN 8
#define LORA_RX_PIN 7
#define MAX_DEVICES 10
#define BIND_BUTTON_PIN 2
#define UP_BUTTON_PIN 3
#define DOWN_BUTTON_PIN 4
#define LEFT_BUTTON_PIN 5
#define RIGHT_BUTTON_PIN 6
#define SELECT_BUTTON_PIN 7

SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);  // RX, TX

struct Device {
    String address;
};

Device devices[MAX_DEVICES];
int numDevices = 0;

int cursorX = 0;
int cursorY = 0;
int selectedDeviceIndex = -1;

// Ethernet configuration
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress server(192, 168, 1, 100);  // Server IP address
EthernetClient client;

void setup() {
    Serial.begin(9600);
    Wire.begin();

    pinMode(BIND_BUTTON_PIN, INPUT_PULLUP);
    pinMode(UP_BUTTON_PIN, INPUT_PULLUP);
    pinMode(DOWN_BUTTON_PIN, INPUT_PULLUP);
    pinMode(LEFT_BUTTON_PIN, INPUT_PULLUP);
    pinMode(RIGHT_BUTTON_PIN, INPUT_PULLUP);
    pinMode(SELECT_BUTTON_PIN, INPUT_PULLUP);

    // Initialize OLED display
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
        Serial.println("Error initializing OLED");
        while (true);
    }
    display.clearDisplay();
    display.display();

    // Initialize LoRa communication
    loraSerial.begin(9600);
    Serial.println("Initializing LoRa...");
    delay(1000);

    // Initialize Ethernet
    if (Ethernet.begin(mac) == 0) {
        Serial.println("Error initializing Ethernet");
        while (true);
    }
    Serial.println("Ethernet initialized");
}

void loop() {
    // Check if the bind button is pressed
    if (digitalRead(BIND_BUTTON_PIN) == LOW) {
        Serial.println("Bind button pressed. Starting binding...");
        loraSerial.println("BIND_REQUEST");
        delay(1000);  // Wait for module response

        if (loraSerial.available()) {
            String loraResponse = loraSerial.readStringUntil('\n');
            if (loraResponse.indexOf("BIND_ACK") != -1) {
                if (numDevices < MAX_DEVICES) {
                    devices[numDevices].address = "DEVICE_" + String(numDevices + 1);
                    numDevices++;
                    Serial.println("Binding successful. Assigned address: " + devices[numDevices - 1].address);

                    // Change the LoRa module's address to allow more bindings
                    loraSerial.println("CHANGE_ADDRESS");
                    delay(1000);
                } else {
                    Serial.println("Cannot bind more devices. Limit reached.");
                }
            }
        }
    }

    // Navigate through the grid using buttons
    if (digitalRead(UP_BUTTON_PIN) == LOW) {
        cursorY = (cursorY - 1 + 3) % 3;
        delay(200);
    }
    if (digitalRead(DOWN_BUTTON_PIN) == LOW) {
        cursorY = (cursorY + 1) % 3;
        delay(200);
    }
    if (digitalRead(LEFT_BUTTON_PIN) == LOW) {
        cursorX = (cursorX - 1 + 3) % 3;
        delay(200);
    }
    if (digitalRead(RIGHT_BUTTON_PIN) == LOW) {
        cursorX = (cursorX + 1) % 3;
        delay(200);
    }

    // Select an area of the grid and assign it to a device
    if (digitalRead(SELECT_BUTTON_PIN) == LOW) {
        int selectedIndex = cursorY * 3 + cursorX;
        if (selectedIndex < numDevices) {
            selectedDeviceIndex = selectedIndex;
            Serial.println("Selected device: " + devices[selectedDeviceIndex].address);
        }
        delay(200);
    }

    // Update OLED display
    display.clearDisplay();
    for (int y = 0; y < 3; y++) {
        for (int x = 0; x < 3; x++) {
            int index = y * 3 + x;
            if (index < numDevices) {
                display.setCursor(x * 40, y * 20);
                display.print(devices[index].address);
            }
        }
    }
    display.drawRect(cursorX * 40, cursorY * 20, 40, 20, SSD1306_WHITE);
    display.display();

    // Send measurement request to each bound device sequentially
    for (int i = 0; i < numDevices; i++) {
        Serial.println("Requesting data from device: " + devices[i].address);
        loraSerial.println("READ_SENSORS " + devices[i].address);
        delay(1000);  // Wait for device response

        if (loraSerial.available()) {
            String sensorData = loraSerial.readStringUntil('\n');
            Serial.println("Data received from device " + devices[i].address + ": " + sensorData);

            // Send data to the server via a POST request
            bool success = false;
            while (!success) {
                if (client.connect(server, 80)) {
                    Serial.println("Connected to server, sending data...");
                    client.println("POST /api/data HTTP/1.1");
                    client.println("Host: 192.168.1.100");
                    client.println("Content-Type: application/json");
                    client.print("Content-Length: ");
                    String payload = "{\"device_id\": \"" + devices[i].address + "\", \"data\": \"" + sensorData + "\"}";
                    client.println(payload.length());
                    client.println();
                    client.println(payload);

                    // Wait for server response
                    delay(1000);
                    if (client.available()) {
                        String response = client.readStringUntil('\n');
                        if (response.indexOf("200") != -1) {
                            Serial.println("Data sent successfully");
                            success = true;
                        } else if (response.indexOf("400") != -1) {
                            Serial.println("Transmission error. Retrying...");
                        }
                    }
                    client.stop();
                } else {
                    Serial.println("Error connecting to the server. Retrying...");
                }

            }
        }
    }

    // Wait before the next round of requests
    delay(3600000);  // Wait 1 hour before starting the loop again
}
