// Nodo puerta: reed MC-38 entre D5 (INPUT_PULLUP) y GND. Iman cerca = LOW = puerta cerrada.
// Publica puerta_abierta / puerta_cerrada en cada cambio (antirrebote 50 ms) y un latido cada 60 s.
// El limite de "abierta mas de 2 min" lo evalua n8n. LED rojo fijo mientras la puerta esta abierta.
// Si el cambio ocurre sin red o la API no lo guarda, el estado queda pendiente y se reenvia cada 5 s:
// el servidor nunca se queda con la puerta "abierta" cuando ya se cerro.
// Firmware de referencia: solo compilado.
#include "nodo_comun.h"

constexpr uint8_t PIN_REED = D5;
constexpr uint32_t ANTIRREBOTE_MS = 50;
constexpr uint32_t REENVIO_MS = 5000;

bool estable = HIGH, anterior = HIGH;
uint32_t cambio = 0;
bool pendiente = true;  // hay un estado sin entregar (al arrancar: el inicial)
uint32_t ultimoEnvio = 0;
bool intentado = false;

void setup() {
  pinMode(PIN_REED, INPUT_PULLUP);
  estable = anterior = digitalRead(PIN_REED);
  nodo::iniciar();
  Serial.printf("[puerta] estado inicial: %s\n", estable == HIGH ? "abierta" : "cerrada");
}

void loop() {
  nodo::atender(true);
  bool lectura = digitalRead(PIN_REED);
  if (lectura != anterior) {
    cambio = millis();
    anterior = lectura;
  }
  if (nodo::transcurrido(cambio, ANTIRREBOTE_MS) && lectura != estable) {
    estable = lectura;
    pendiente = true;
    intentado = false;  // un cambio nuevo se manda de inmediato
    Serial.printf("[puerta] %s\n", estable == HIGH ? "abierta" : "cerrada");
  }
  if (pendiente && WiFi.status() == WL_CONNECTED && (!intentado || nodo::transcurrido(ultimoEnvio, REENVIO_MS))) {
    bool primero = !intentado;
    intentado = true;
    ultimoEnvio = millis();
    // Solo cuenta como entregado si la API lo guardo: MQTT no confirma, y sin esa fila la base de datos
    // se quedaria con la puerta "abierta". Los reenvios van solo a la API (por MQTT ya salio).
    nodo::publicarEvento(estable == HIGH ? "puerta_abierta" : "puerta_cerrada", NAN, primero);
    if (nodo::eventoGuardado) pendiente = false;
  }
  nodo::alerta = (estable == HIGH);  // actuador: rojo fijo con la puerta abierta
}
