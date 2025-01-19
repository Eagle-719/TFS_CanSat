#include <Wire.h>
#include <HardwareSerial.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>
#include <TinyGPS++.h>

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BMP280 bmp; // BMP280 szenzor példány
TinyGPSPlus gps;

// LoRa modul UART (UART0 RX GPIO0, TX GPIO1)
HardwareSerial LoraSerial(0);
#define RXD2 0
#define TXD2 1

// GPS modul UART (UART1 RX GPIO4, TX GPIO5)
HardwareSerial GPSSerial(1);
#define RXD1 4
#define TXD1 5

int N = 0;
String V = "";
String H = "";
unsigned long previousMillis = 0;
const unsigned long interval = 950; // 950 ms az adások közötti idő

// Globális változók a szenzoradatok tárolására
float t = 0.0;
float p = 0.0;
float alt = 0.0;
String LAT = "N"; 
String LON = "N";
String ALT = "N";

bool LED = false;

void setup() {
    // LoRa inicializálása
    LoraSerial.begin(115200);
    delay(200);
    LoraSerial.println("sys reset");
    delay(500);
    LoraSerial.println("radio set pwr 20"); // Max teljesítmény az adáshoz

    // GPS inicializálása
    GPSSerial.begin(9600);

    // Beépített LED inicializálása
    pinMode(25, OUTPUT);
    digitalWrite(25, LOW);

    // Soros monitor inicializálása
    Serial.begin(115200);

    // I2C inicializálása (SDA GPIO20, SCL GPIO21)
    Wire.begin(20, 21);

    // BMP280 inicializálása
    if (!bmp.begin(0x76)) { // Ellenőrzi, hogy az I2C cím helyes
        Serial.println("Could not find a valid BMP280 sensor, check wiring!");
        digitalWrite(25, HIGH); // Ha nem működik a BMP280 szenzor, a LED világít
        while (1);
    }
}

void loop() {
    // Szenzoradatok olvasása
    t = bmp.readTemperature();
    p = bmp.readPressure();
    alt = bmp.readAltitude(SEALEVELPRESSURE_HPA);
    readGPSData(); // GPS adatok olvasása

    if (!gps.location.isValid()) {
        LAT = "N"; 
        LON = "N"; 
        ALT = "N";
        Serial.println("GPS location invalid!");
    }

    // Adatok küldése LoRa modulon
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
        previousMillis = currentMillis;
        radio();
    }
}

void readGPSData() {
    while (GPSSerial.available() > 0) {
        char c = GPSSerial.read();
        gps.encode(c);
        if (gps.location.isUpdated() && gps.hdop.value() < 200 && gps.satellites.value() > 3) { // Ellenőrzés
            LAT = String(gps.location.lat(), 6);
            LON = String(gps.location.lng(), 6);
            ALT = String(gps.altitude.meters(), 1);
        }
    }
    // Ha a GPS nem frissült, megtartjuk az előző értékeket
    if (!gps.location.isValid()) {
        LAT = "N"; 
        LON = "N"; 
        ALT = "N"; 
        Serial.println("GPS location invalid!");
    }
}

String toHex(String input) {
    String result = "";
    for (int i = 0; i < input.length(); i++) {
        result += String((int)input.charAt(i), HEX);
    }
    return result + "2C"; // Szeparátor
}

void radio() {
    String ADATOK = "";
    ADATOK += toHex("TFS" + String(N));
    ADATOK += toHex(String(t, 1));
    ADATOK += toHex(String(p / 100, 1));
    ADATOK += toHex(String(alt, 1));
    ADATOK += toHex(LAT);
    ADATOK += toHex(LON);
    ADATOK += toHex(ALT);
    N++;

    String S = "radio tx " + ADATOK + " 3"; // 3x elküldjük a biztonság kedvéért
    LoraSerial.println(S);

    // Nyugtázó üzenetek fogadása az adóból
    bool success = false;
    unsigned long startTime = millis();
    while (millis() - startTime < 1000) { // Max 1 másodpercet vár a válaszra
        if (LoraSerial.available()) {
            String response = LoraSerial.readStringUntil('\n');
            Serial.print(response);
            if (response.indexOf("radio_tx_ok") != -1) {
                success = true;
                break;
            }
        }
    }

    if (success) {
        // LED villogtatás az adás sikerességének jelzésére
        LED = !LED;
        digitalWrite(25, LED ? HIGH : LOW);
    }
    Serial.println(S);
}
