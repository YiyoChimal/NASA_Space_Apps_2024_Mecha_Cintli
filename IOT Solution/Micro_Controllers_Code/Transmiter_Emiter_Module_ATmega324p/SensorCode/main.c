#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP3XX.h>
#include <Adafruit_SHT31.h>
#include <SoftwareSerial.h>

#define BMP_CS 10
#define SOIL_MOISTURE_PIN A0
#define PH_SENSOR_PIN A1
#define LORA_TX_PIN 8
#define LORA_RX_PIN 7
#define BIND_BUTTON_PIN 2

Adafruit_BMP3XX bmp;
Adafruit_SHT31 sht31 = Adafruit_SHT31();
SoftwareSerial loraSerial(LORA_RX_PIN, LORA_TX_PIN);  // RX, TX

bool isBound = false;

void setup() {
	Serial.begin(9600);
	Wire.begin();

	pinMode(BIND_BUTTON_PIN, INPUT_PULLUP);

	// Initialize LoRa communication
	loraSerial.begin(9600);
	Serial.println("Initializing LoRa...");
	delay(1000);
}

void loop() {
	// Check if the bind button is pressed
	if (digitalRead(BIND_BUTTON_PIN) == LOW) {
		Serial.println("Bind button pressed. Starting binding...");
		loraSerial.println("BIND_REQUEST");
		delay(1000);  // Wait for a response from the central module

		if (loraSerial.available()) {
			String loraResponse = loraSerial.readStringUntil('\n');
			if (loraResponse.indexOf("BIND_ACK") != -1) {
				Serial.println("Successful binding with the central module.");
				isBound = true;
				// Change LoRa module address to allow more bindings
				loraSerial.println("CHANGE_ADDRESS");
				delay(1000);
			}
		}
	}

	if (isBound && loraSerial.available()) {
		String loraMessage = loraSerial.readStringUntil('\n');
		if (loraMessage.indexOf("READ_SENSORS") != -1) {
			// Initialize BMP388
			if (!bmp.begin_I2C()) {
				Serial.println("Cannot find BMP388 sensor");
				return;
			}

			// Initialize SHT31
			if (!sht31.begin(0x44)) {
				Serial.println("Cannot find SHT31 sensor");
				return;
			}

			// Measure atmospheric pressure
			if (!bmp.performReading()) {
				Serial.println("Error reading BMP388");
				} else {
				Serial.print("Atmospheric pressure: ");
				Serial.print(bmp.pressure / 100.0);
				Serial.println(" hPa");
			}

			// Measure ambient humidity and temperature
			float temperature = sht31.readTemperature();
			float humidity = sht31.readHumidity();
			if (!isnan(temperature) && !isnan(humidity)) {
				Serial.print("Temperature: ");
				Serial.print(temperature);
				Serial.println(" °C");
				Serial.print("Ambient humidity: ");
				Serial.print(humidity);
				Serial.println(" %");
				} else {
				Serial.println("Error reading SHT31 sensor");
			}

			// Measure soil moisture
			int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
			Serial.print("Soil moisture: ");
			Serial.println(soilMoistureValue);

			// Measure soil pH
			int phValue = analogRead(PH_SENSOR_PIN);
			float voltage = phValue * (5.0 / 1023.0);
			float ph = 7.0 + ((2.5 - voltage) * 3.0);  // Approximate conversion from voltage to pH
			Serial.print("Soil pH: ");
			Serial.println(ph);

			// Send results via LoRa
			loraSerial.print("Pressure: ");
			loraSerial.print(bmp.pressure / 100.0);
			loraSerial.print(" hPa, Temperature: ");
			loraSerial.print(temperature);
			loraSerial.print(" °C, Humidity: ");
			loraSerial.print(humidity);
			loraSerial.print(" %, Soil moisture: ");
			loraSerial.print(soilMoistureValue);
			loraSerial.print(", pH: ");
			loraSerial.println(ph);

			// Deactivate sensors and communication for 1 hour
			bmp.end();
			sht31.end();
			loraSerial.end();
			delay(3600000);  // Wait 1 hour

			// Reactivate LoRa to wait for the next signal
			loraSerial.begin(9600);
			Serial.println("Waiting for the next activation signal...");
		}
	}
}
