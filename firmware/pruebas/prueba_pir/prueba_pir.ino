// Argos · PRUEBA del nodo pir (sin WiFi ni servidor). Solo revisa el HC-SR501 y los dos LED.
// Placa: NodeMCU 1.0 (ESP-12E Module). Monitor serie: 115200.
// Conexiones que prueba: salida OUT del HC-SR501 en D5, LED verde en D7, LED rojo en D8.
//
// Qué hace:
//   1. Al arrancar enciende el verde 1 s y luego el rojo 1 s (prueba de los LED).
//   2. Después lee D5 todo el tiempo: el LED rojo copia al sensor (encendido = OUT en alto).
//   3. Imprime cada cambio con su hora y cuánto duró, y cada 5 s un resumen.
//
// Cómo leer el resultado:
//   - Recién conectado, el HC-SR501 tarda cerca de 1 min en estabilizarse: es normal que cambie solo.
//   - Sin moverte debe quedarse en BAJO. Al pasar la mano debe subir a ALTO unos segundos y regresar.
//   - Siempre BAJO: revisa alimentación del sensor (5 V en VCC), GND y el cable de OUT a D5.
//   - Siempre ALTO: jumper en modo repetible con mucho movimiento, perilla de tiempo al máximo, o OUT suelto.
//   - Cambia muy rápido sin que nadie se mueva: cable de OUT flojo o falta GND común.
// Comandos (letra y Enter): v prueba LED verde · r prueba LED rojo

constexpr uint8_t PIN_PIR = D5, PIN_LED_V = D7, PIN_LED_R = D8;

bool estado = false;
uint32_t ultimoCambio = 0, ultimoResumen = 0, cambios = 0, altoMs = 0;

void probarLed(uint8_t pin, const __FlashStringHelper* nombre) {
  Serial.print(F("[prueba] LED ")); Serial.print(nombre); Serial.println(F(" encendido 1 s"));
  digitalWrite(pin, HIGH); delay(1000); digitalWrite(pin, LOW);
}

void setup() {
  pinMode(PIN_PIR, INPUT);
  pinMode(PIN_LED_V, OUTPUT); pinMode(PIN_LED_R, OUTPUT);
  digitalWrite(PIN_LED_V, LOW); digitalWrite(PIN_LED_R, LOW);
  Serial.begin(115200);
  delay(300);
  Serial.println(F("\n=== Argos: prueba del nodo pir (HC-SR501 en D5, verde D7, rojo D8) ==="));
  probarLed(PIN_LED_V, F("verde (D7)"));
  probarLed(PIN_LED_R, F("rojo (D8)"));
  Serial.println(F("Leyendo el sensor. El LED rojo copia la salida del PIR. Comandos: v, r"));
  estado = digitalRead(PIN_PIR);
  ultimoCambio = ultimoResumen = millis();
  Serial.printf("[%7.1f s] estado inicial: %s\n", millis() / 1000.0, estado ? "ALTO (movimiento)" : "BAJO (sin movimiento)");
}

void loop() {
  uint32_t t = millis();
  bool ahora = digitalRead(PIN_PIR);
  if (ahora != estado) {
    uint32_t duro = t - ultimoCambio;
    if (estado) altoMs += t - max(ultimoCambio, ultimoResumen);
    Serial.printf("[%7.1f s] %s  (el estado anterior duro %.1f s)%s\n", t / 1000.0,
                  ahora ? "ALTO: movimiento detectado" : "BAJO: sin movimiento", duro / 1000.0,
                  duro < 200 ? "  <-- cambio muy rapido: posible cable flojo" : "");
    estado = ahora;
    ultimoCambio = t;
    cambios++;
  }
  digitalWrite(PIN_LED_R, estado ? HIGH : LOW);
  digitalWrite(PIN_LED_V, (t / 500) % 2);   // verde parpadea: el programa sigue vivo

  if (t - ultimoResumen >= 5000) {
    uint32_t alto = altoMs + (estado ? t - max(ultimoCambio, ultimoResumen) : 0);
    altoMs = 0;
    Serial.printf("[%7.1f s] resumen 5 s: ahora %s, %lu cambios, %.0f %% del tiempo en ALTO%s\n", t / 1000.0,
                  estado ? "ALTO" : "BAJO", (unsigned long)cambios, min(100.0, alto / 50.0),
                  t < 60000 ? "  (el sensor aun se esta estabilizando)" : "");
    cambios = 0;
    ultimoResumen = t;
  }

  while (Serial.available()) {
    char c = Serial.read();
    if (c == 'v') probarLed(PIN_LED_V, F("verde (D7)"));
    if (c == 'r') probarLed(PIN_LED_R, F("rojo (D8)"));
  }
  delay(5);
}
