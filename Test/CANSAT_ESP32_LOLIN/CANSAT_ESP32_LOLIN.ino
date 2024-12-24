// WEMOS Lolin 32 lite CANSAT
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h> // Ez a jó a HW-611 hez
#define SEALEVELPRESSURE_HPA (1013.25)
Adafruit_BMP280 bmp; // Létrehozzuk a BMP280 példányt I2C BMP SCL ->ESP 23, BME SDA ->ESP 19
#define RXD2 16
#define TXD2 17
int N=0;
String V = "";
String H = "";

void setup() {
Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
delay(200);
Serial2.println("sys reset");
delay(500);
Serial2.println("radio set pwr 20");//max teljesítmény az adáshoz
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
float t = bmp.readTemperature();
float p = bmp.readPressure();
String ADATOK="";
V="TFS" + String(N);conv();ADATOK =ADATOK + H;//Adásazonosító
V=String(t);conv();ADATOK =ADATOK + H;//Hőmérséklet 24.25 celsiusba
V=String(p);conv();ADATOK =ADATOK + H;//Nyomás Pa -ban
N++;
Serial.println(ADATOK);
String S="radio tx " + ADATOK + " 1";
Serial2.println(S);
while (Serial2.available()) {
  Serial.print(char(Serial2.read()));
}
 
delay(2000);
}
//**************************************************
void conv(){
int n = V.length();
H = "";
  for (int i = 0; i < n; i++) {
    String D = V.substring(i, i + 1);
    char d = D.charAt(0); // Karakter ASCII kódjának kivétele
    String h = String((int)d, HEX); // ASCII kód hexadecimális konvertálása
    H = H + h;
  }
H=H + "3B";//; szeparátor karakter hozzáadása
}
