// Diagnostico del DHT11: busca en que pin del NodeMCU esta respondiendo el sensor.
// No usa WiFi ni la API. Subir, abrir el monitor serie a 115200 y leer el resultado.
#include <DHT.h>

const uint8_t PINES[] = {D1, D2, D5, D6};
const char* NOMBRES[] = {"D1", "D2", "D5", "D6"};

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== Diagnostico DHT11 ===");
}

void loop() {
  for (int i = 0; i < 4; i++) {
    // Se baja la linea un instante y se suelta: si hay un sensor con corriente conectado,
    // su resistencia la vuelve a subir (ALTO). Si el pin esta al aire, se queda en BAJO.
    pinMode(PINES[i], OUTPUT);
    digitalWrite(PINES[i], LOW);
    delay(20);
    pinMode(PINES[i], INPUT);
    delayMicroseconds(200);
    int reposo = digitalRead(PINES[i]);

    DHT sensor(PINES[i], DHT11);
    sensor.begin();
    delay(2000);
    float t = sensor.readTemperature();
    float h = sensor.readHumidity();

    Serial.print(NOMBRES[i]);
    Serial.print(": linea en reposo = ");
    Serial.print(reposo ? "ALTO" : "BAJO");
    if (isnan(t) || isnan(h)) Serial.println("  -> sin respuesta");
    else {
      Serial.print("  -> RESPONDE  T = "); Serial.print(t);
      Serial.print(" C  HR = "); Serial.print(h); Serial.println(" %");
    }
  }
  Serial.println("---");
  delay(3000);
}
