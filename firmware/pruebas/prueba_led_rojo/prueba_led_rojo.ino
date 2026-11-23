// Argos · PRUEBA DEL LED ROJO (D8) comparado con el LED verde (D7). Sirve para cualquier nodo.
// Placa: NodeMCU 1.0 (ESP-12E Module). Monitor serie: 115200 baudios. No usa WiFi ni librerías extra.
//
// Ciclo que se repite:
//   1. Rojo fijo 5 s        -> aquí se mide con el multímetro (ver abajo)
//   2. Verde fijo 5 s       -> para comparar el brillo
//   3. Los dos juntos 3 s
//   4. Rojo parpadeando rápido 3 s
//   5. Rojo subiendo y bajando de brillo 4 s (si se ve el cambio, el pin y el LED responden bien)
//
// Comandos por el monitor serie (letra y Enter):
//   r rojo fijo hasta que mandes otra letra (para medir con calma) · v verde fijo · a apagar · c seguir el ciclo
//
// Cómo medir (multímetro en DCV, con el rojo fijo):
//   - Entre D8 y GND: unos 3.3 V. Si sale mucho menos, el pin o el puente a la resistencia tiene mal contacto.
//   - Entre las patas del LED rojo: unos 1.8 a 2.0 V. Si sale casi 3.3 V, el LED no conduce (al revés o dañado).
//   - En la resistencia: unos 1.3 a 1.5 V. Si sale casi 3.3 V, la resistencia es de valor muy alto
//     (330 ohm es naranja, naranja, café; 10 k es café, negro, naranja y deja el LED muy tenue).

constexpr uint8_t PIN_LED_V = D7;
constexpr uint8_t PIN_LED_R = D8;

char modo = 'c';  // c = ciclo, r = rojo fijo, v = verde fijo, a = apagado

void apagar() {
  analogWrite(PIN_LED_R, 0);
  digitalWrite(PIN_LED_R, LOW);
  digitalWrite(PIN_LED_V, LOW);
}

// Espera ms milisegundos atendiendo el monitor serie; false si llegó un comando que corta el ciclo.
bool esperar(uint32_t ms) {
  uint32_t t0 = millis();
  while (millis() - t0 < ms) {
    if (Serial.available()) {
      char c = Serial.read();
      if (c == 'r' || c == 'v' || c == 'a' || c == 'c') {
        modo = c;
        return false;
      }
    }
    delay(5);
    yield();
  }
  return true;
}

void ciclo() {
  Serial.println(F("1) ROJO fijo 5 s (mide aqui con el multimetro)"));
  apagar(); digitalWrite(PIN_LED_R, HIGH);
  if (!esperar(5000)) return;

  Serial.println(F("2) VERDE fijo 5 s (compara el brillo con el rojo)"));
  apagar(); digitalWrite(PIN_LED_V, HIGH);
  if (!esperar(5000)) return;

  Serial.println(F("3) Los DOS juntos 3 s"));
  digitalWrite(PIN_LED_R, HIGH); digitalWrite(PIN_LED_V, HIGH);
  if (!esperar(3000)) return;

  Serial.println(F("4) ROJO parpadeando rapido 3 s"));
  apagar();
  for (int i = 0; i < 12; i++) {
    digitalWrite(PIN_LED_R, i % 2);
    if (!esperar(250)) return;
  }

  Serial.println(F("5) ROJO subiendo y bajando de brillo 4 s"));
  apagar();
  for (int i = 0; i <= 100; i++) {
    analogWrite(PIN_LED_R, map(i < 50 ? i : 100 - i, 0, 50, 0, 1023));
    if (!esperar(40)) return;
  }
  apagar();
  Serial.println(F("-- fin del ciclo --\n"));
  esperar(1000);
}

void setup() {
  pinMode(PIN_LED_V, OUTPUT);
  pinMode(PIN_LED_R, OUTPUT);
  apagar();
  Serial.begin(115200);
  delay(300);
  Serial.println(F("\n=== Argos: prueba del LED rojo (D8) contra el verde (D7) ==="));
  Serial.println(F("Comandos: r rojo fijo | v verde fijo | a apagar | c ciclo"));
  Serial.println(F("Si el rojo se ve mucho mas tenue que el verde en el paso 1 y 2, mide con el multimetro."));
}

void loop() {
  switch (modo) {
    case 'c':
      ciclo();
      break;
    case 'r':
      apagar(); digitalWrite(PIN_LED_R, HIGH);
      Serial.println(F("ROJO fijo. Mide: D8-GND ~3.3 V, LED ~1.8-2.0 V, resistencia ~1.3-1.5 V. (c para seguir el ciclo)"));
      while (esperar(60000)) {}
      break;
    case 'v':
      apagar(); digitalWrite(PIN_LED_V, HIGH);
      Serial.println(F("VERDE fijo. (c para seguir el ciclo)"));
      while (esperar(60000)) {}
      break;
    case 'a':
      apagar();
      Serial.println(F("Apagados. (c para seguir el ciclo)"));
      while (esperar(60000)) {}
      break;
  }
}
