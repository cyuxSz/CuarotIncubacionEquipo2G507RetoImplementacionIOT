// Argos · PRUEBA 2 del nodo pir: lee CUATRO pines a la vez para saber si el problema es el pin D5,
// el cable o el sensor. Sin WiFi. Placa: NodeMCU 1.0 (ESP-12E Module). Monitor serie: 115200.
//
// Imprime una linea por segundo, por ejemplo:   D5=1  D6=0  D1=0  D2=0
//   1 = el pin ve 3.3 V (ALTO)     0 = el pin ve 0 V (BAJO)
// El LED rojo (D8) se enciende si CUALQUIERA de los cuatro esta en 1.
//
// Uso: mueve el cable blanco (OUT del PIR) de D5 a D6, D1 o D2 y mira cual columna cambia.
// Un pin SIN nada conectado puede marcar 0 o 1 al azar: eso es normal, no es falla.

constexpr uint8_t PINES[] = {D5, D6, D1, D2};
const char* const NOMBRES[] = {"D5", "D6", "D1", "D2"};
constexpr uint8_t PIN_LED_V = D7, PIN_LED_R = D8;

void setup() {
  for (uint8_t p : PINES) pinMode(p, INPUT);
  pinMode(PIN_LED_V, OUTPUT); pinMode(PIN_LED_R, OUTPUT);
  Serial.begin(115200);
  delay(300);
  Serial.println(F("\n=== Argos: prueba 2 del pir (lee D5, D6, D1 y D2) ==="));
}

void loop() {
  static uint32_t ultimo = 0;
  bool alguno = false;
  bool v[4];
  for (uint8_t i = 0; i < 4; i++) { v[i] = digitalRead(PINES[i]); alguno |= v[i]; }
  digitalWrite(PIN_LED_R, alguno ? HIGH : LOW);
  digitalWrite(PIN_LED_V, (millis() / 500) % 2);
  if (millis() - ultimo >= 1000) {
    ultimo = millis();
    Serial.printf("[%6.1f s]", millis() / 1000.0);
    for (uint8_t i = 0; i < 4; i++) Serial.printf("  %s=%d", NOMBRES[i], v[i]);
    Serial.println();
  }
  delay(5);
}
