/*
 * CodigoPrincipal.c
 *
 * Created: 06/10/2024 04:44:57 p. m.
 * Author : Francisco Rios
 */ 

#include <avr/io.h>

#include <SoftwareSerial.h>
#include <Wire.h>
#include <EEPROM.h>
#include <UIPEthernet.h>  // Biblioteca para el módulo ENC28J60
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128  // Ancho del OLED
#define SCREEN_HEIGHT 64  // Altura del OLED
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

// Configuración de Ethernet
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress server(192, 168, 1, 100);  // Dirección IP del servidor
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

	// Inicializar pantalla OLED
	if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
		Serial.println("Error al inicializar OLED");
		while (true);
	}
	display.clearDisplay();
	display.display();

	// Inicializar comunicación LoRa
	loraSerial.begin(9600);
	Serial.println("Inicializando LoRa...");
	delay(1000);

	// Inicializar Ethernet
	if (Ethernet.begin(mac) == 0) {
		Serial.println("Error al inicializar Ethernet");
		while (true);
	}
	Serial.println("Ethernet inicializado");
}

void loop() {
	// Verificar si se presiona el botón de vinculación
	if (digitalRead(BIND_BUTTON_PIN) == LOW) {
		Serial.println("Botón de vinculación presionado. Iniciando vinculación...");
		loraSerial.println("BIND_REQUEST");
		delay(1000);  // Esperar respuesta del módulo

		if (loraSerial.available()) {
			String loraResponse = loraSerial.readStringUntil('\n');
			if (loraResponse.indexOf("BIND_ACK") != -1) {
				if (numDevices < MAX_DEVICES) {
					devices[numDevices].address = "DEVICE_" + String(numDevices + 1);
					numDevices++;
					Serial.println("Vinculación exitosa. Dirección asignada: " + devices[numDevices - 1].address);

					// Cambiar la dirección del módulo LoRa para permitir más vinculaciones
					loraSerial.println("CHANGE_ADDRESS");
					delay(1000);
					} else {
					Serial.println("No se pueden vincular más dispositivos. Límite alcanzado.");
				}
			}
		}
	}

	// Navegar por la matriz usando los botones
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

	// Seleccionar un área de la matriz y asignarla a un dispositivo
	if (digitalRead(SELECT_BUTTON_PIN) == LOW) {
		int selectedIndex = cursorY * 3 + cursorX;
		if (selectedIndex < numDevices) {
			selectedDeviceIndex = selectedIndex;
			Serial.println("Dispositivo seleccionado: " + devices[selectedDeviceIndex].address);
		}
		delay(200);
	}

	// Actualizar pantalla OLED
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

	// Enviar solicitud de medición a cada dispositivo vinculado de manera secuencial
	for (int i = 0; i < numDevices; i++) {
		Serial.println("Solicitando datos del dispositivo: " + devices[i].address);
		loraSerial.println("READ_SENSORS " + devices[i].address);
		delay(1000);  // Esperar respuesta del dispositivo

		if (loraSerial.available()) {
			String sensorData = loraSerial.readStringUntil('\n');
			Serial.println("Datos recibidos del dispositivo " + devices[i].address + ": " + sensorData);

			// Enviar datos al servidor mediante una solicitud POST
			bool success = false;
			while (!success) {
				if (client.connect(server, 80)) {
					Serial.println("Conectado al servidor, enviando datos...");
					client.println("POST /api/data HTTP/1.1");
					client.println("Host: 192.168.1.100");
					client.println("Content-Type: application/json");
					client.print("Content-Length: ");
					String payload = "{\"device_id\": \"" + devices[i].address + "\", \"data\": \"" + sensorData + "\"}";
					client.println(payload.length());
					client.println();
					client.println(payload);

					// Esperar respuesta del servidor
					delay(1000);
					if (client.available()) {
						String response = client.readStringUntil('\n');
						if (response.indexOf("200") != -1) {
							Serial.println("Datos enviados correctamente");
							success = true;
							} else if (response.indexOf("400") != -1) {
							Serial.println("Error en la transmisión. Reintentando...");
						}
					}
					client.stop();
					} else {
					Serial.println("Error al conectar con el servidor. Reintentando...");
				}
				
			}
		}
	}

	// Esperar antes de la próxima ronda de solicitudes
	delay(3600000);  // Esperar 1 hora antes de volver a iniciar el ciclo
}