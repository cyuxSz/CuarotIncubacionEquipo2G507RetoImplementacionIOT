// Argos · PRUEBA DEL NODO acel (no es el firmware del nodo; no usa WiFi ni servidor).
// Placa: NodeMCU 1.0 (ESP-12E Module). Monitor serie: 115200. Librería: Adafruit ADS1X15.
//
// Qué hace, cada 3 s:
//   1. Dice el nivel de las líneas I2C en reposo (SDA = D2, SCL = D1). Las dos deben estar en ALTO.
//   2. Busca dispositivos I2C en todo el bus y lista las direcciones que contestan.
//      El ADS1115 debe salir en 0x48 (ADDR a GND). 0x49 = ADDR a VDD, 0x4A = ADDR a SDA, 0x4B = ADDR a SCL.
//   3. Si hay un ADS1115, lee los 4 canales en volts. Con el GY-61 bien conectado, A0, A1 y A2 dan
//      entre 1.0 y 2.3 V en reposo (un eje cerca de 1.3 o 2.0 V por la gravedad). A3 queda al aire.
//   4. LED verde (D7) = ADS1115 encontrado; LED rojo (D8) = no hay nada en el bus.

#include <Wire.h>
#include <Adafruit_ADS1X15.h>

constexpr uint8_t PIN_LED_V = D7, PIN_LED_R = D8;
Adafruit_ADS1115 ads;

void setup() {
  pinMode(PIN_LED_V, OUTPUT);
  pinMode(PIN_LED_R, OUTPUT);
  Serial.begin(115200);
  delay(300);
  Serial.println(F("\n=== Argos: prueba del nodo acel (bus I2C, ADS1115 y GY-61) ==="));
}

void loop() {
  // 1) líneas en reposo: se sueltan y se leen como entradas (el módulo ADS1115 trae sus resistencias pull-up)
  pinMode(D2, INPUT);
  pinMode(D1, INPUT);
  delay(5);
  bool sda = digitalRead(D2), scl = digitalRead(D1);
  Serial.printf("\nLineas en reposo: SDA(D2)=%s  SCL(D1)=%s", sda ? "ALTO" : "BAJO", scl ? "ALTO" : "BAJO");
  if (!sda || !scl) Serial.print(F("   <- una linea en BAJO: corto a GND, cable en otro pin, o el ADS1115 sin corriente o danado"));
  Serial.println();

  // 2) búsqueda en el bus
  Wire.begin();  // SDA = D2, SCL = D1
  Wire.setClock(100000);
  uint8_t encontrados = 0, dirAds = 0;
  for (uint8_t d = 1; d < 127; d++) {
    Wire.beginTransmission(d);
    if (Wire.endTransmission() == 0) {
      Serial.printf("  dispositivo en 0x%02X", d);
      if (d >= 0x48 && d <= 0x4B) {
        Serial.print(d == 0x48 ? F("  <- ADS1115 con ADDR a GND (correcto)") : F("  <- ADS1115, pero ADDR NO esta a GND"));
        if (!dirAds) dirAds = d;
      }
      Serial.println();
      encontrados++;
    }
    yield();
  }
  if (!encontrados) Serial.println(F("  NADA contesta en el bus I2C: revisa VDD y GND del ADS1115, SDA en D2 y SCL en D1"));

  // 3) lectura de canales
  if (dirAds && ads.begin(dirAds)) {
    ads.setGain(GAIN_ONE);
    Serial.print(F("  canales:"));
    for (uint8_t c = 0; c < 4; c++) {
      float v = ads.computeVolts(ads.readADC_SingleEnded(c));
      Serial.printf("  A%u=%.3f V", c, v);
    }
    Serial.println(F("   (A0=X, A1=Y, A2=Z del GY-61; A3 al aire)"));
  }
  digitalWrite(PIN_LED_V, dirAds ? HIGH : LOW);
  digitalWrite(PIN_LED_R, encontrados ? LOW : HIGH);
  delay(3000);
}
