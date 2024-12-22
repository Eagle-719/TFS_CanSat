// WEMOS Lolin 32 lite CANSAT
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h> // Ez a jó a HW-611 hez
#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BMP280 bmp; // Létrehozzuk a BMP280 példányt I2C BMP SCL ->ESP 23, BME SDA ->ESP 19
#define RXD2 16
#define TXD2 17
int N=0;


void setup() {
Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
delay(200);
Serial2.println("sys reset");
pinMode(LED_BUILTIN, OUTPUT);
digitalWrite(LED_BUILTIN, LOW);
Serial.begin(115200);
Wire.begin();
   if (!bmp.begin(0x76)) { // Ellenőrzi, hogy az I2C cím helyes
        Serial.println("Could not find a valid BMP280 sensor, check wiring!");
        digitalWrite(LED_BUILTIN, HIGH);//Ha nem működik a BMP 280 szenzor a LED nem világít
        while (1);
    }
}

void loop() {
  double t=bmp.readTemperature()*100;
  double p=bmp.readPressure();
  int ti=(int)t;
  int pi=(int)p;
  String T=String(ti);
  String P=String(pi);

  String S="radio tx " + T + " 1";
  Serial.println(S);
  Serial2.println(S);
   while (Serial2.available()) {
    Serial.print(char(Serial2.read()));
   }
  delay(1000);
  S="radio tx " + P + " 1";
  Serial.println(S);
  Serial2.println(S);
   while (Serial2.available()) {
    Serial.print(char(Serial2.read()));
   }

delay(1000);
N++;

}
