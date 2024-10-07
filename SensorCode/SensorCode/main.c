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

	// Inicializar comunicaci�n LoRa
	loraSerial.begin(9600);
	Serial.println("Inicializando LoRa...");
	delay(1000);
}

void loop() {
	// Verificar si se presiona el bot�n de vinculaci�n
	if (digitalRead(BIND_BUTTON_PIN) == LOW) {
		Serial.println("Bot�n de vinculaci�n presionado. Iniciando vinculaci�n...");
		loraSerial.println("BIND_REQUEST");
		delay(1000);  // Esperar respuesta del m�dulo central

		if (loraSerial.available()) {
			String loraResponse = loraSerial.readStringUntil('\n');
			if (loraResponse.indexOf("BIND_ACK") != -1) {
				Serial.println("Vinculaci�n exitosa con el m�dulo central.");
				isBound = true;
				// Cambiar direcci�n del m�dulo LoRa para permitir m�s vinculaciones
				loraSerial.println("CHANGE_ADDRESS");
				delay(1000);
			}
		}
	}

	if (isBound && loraSerial.available()) {
		String loraMessage = loraSerial.readStringUntil('\n');
		if (loraMessage.indexOf("READ_SENSORS") != -1) {
			// Inicializar BMP388
			if (!bmp.begin_I2C()) {
				Serial.println("No se puede encontrar el sensor BMP388");
				return;
			}

			// Inicializar SHT31
			if (!sht31.begin(0x44)) {
				Serial.println("No se puede encontrar el sensor SHT31");
				return;
			}

			// Medir presi�n atmosf�rica
			if (!bmp.performReading()) {
				Serial.println("Error al leer el BMP388");
				} else {
				Serial.print("Presi�n atmosf�rica: ");
				Serial.print(bmp.pressure / 100.0);
				Serial.println(" hPa");
			}

			// Medir humedad del ambiente y temperatura
			float temperature = sht31.readTemperature();
			float humidity = sht31.readHumidity();
			if (!isnan(temperature) && !isnan(humidity)) {
				Serial.print("Temperatura: ");
				Serial.print(temperature);
				Serial.println(" �C");
				Serial.print("Humedad ambiente: ");
				Serial.print(humidity);
				Serial.println(" %");
				} else {
				Serial.println("Error al leer el sensor SHT31");
			}

			// Medir humedad del suelo
			int soilMoistureValue = analogRead(SOIL_MOISTURE_PIN);
			Serial.print("Humedad del suelo: ");
			Serial.println(soilMoistureValue);

			// Medir pH del suelo
			int phValue = analogRead(PH_SENSOR_PIN);
			float voltage = phValue * (5.0 / 1023.0);
			float ph = 7.0 + ((2.5 - voltage) * 3.0);  // Conversi�n aproximada del voltaje a pH
			Serial.print("pH del suelo: ");
			Serial.println(ph);

			// Enviar resultados v�a LoRa
			loraSerial.print("Presi�n: ");
			loraSerial.print(bmp.pressure / 100.0);
			loraSerial.print(" hPa, Temperatura: ");
			loraSerial.print(temperature);
			loraSerial.print(" �C, Humedad: ");
			loraSerial.print(humidity);
			loraSerial.print(" %, Humedad del suelo: ");
			loraSerial.print(soilMoistureValue);
			loraSerial.print(", pH: ");
			loraSerial.println(ph);

			// Desactivar sensores y comunicaci�n durante 1 hora
			bmp.end();
			sht31.end();
			loraSerial.end();
			delay(3600000);  // Esperar 1 hora

			// Reactivar LoRa para esperar la pr�xima se�al
			loraSerial.begin(9600);
			Serial.println("Esperando pr�xima se�al de activaci�n...");
		}
	}
}
