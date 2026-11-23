// Argos, nodo pir. GENERADO por firmware/herramientas/exportar_arduino.py desde firmware/src/pir/main.cpp (editar alla y regenerar).
// Placa: NodeMCU 1.0 (ESP-12E Module). Credenciales: copiar secrets.example.h a secrets.h en esta carpeta.
#define NODO_ID "pir"
// Nodo pir: HC-SR501 en D5 (salida de 3.3 V). Publica "movimiento" en cada flanco de subida,
// con antirrebote de 10 s, y un latido cada 60 s. El horario de acceso lo evalua n8n.
// Actuador: LED rojo encendido 5 s despues de cada deteccion.
// El HC-SR501 tarda cerca de 1 min en estabilizarse al recibir energia y en ese rato dispara en falso:
// durante CALENTAMIENTO_MS no se publica nada (el LED rojo si lo muestra, para ver que el sensor vive).
// Firmware de referencia: solo compilado.
#include "nodo_comun.h"

constexpr uint8_t PIN_PIR = D5;
constexpr uint32_t ANTIRREBOTE_MS = 10000;
constexpr uint32_t ROJO_MS = 5000;
constexpr uint32_t CALENTAMIENTO_MS = 60000;
uint32_t ultimaDeteccion = 0;
bool hayDeteccion = false;

uint32_t ultimoMovimiento = 0;
bool primerMovimiento = true;
bool anterior = LOW;
bool caliente = false;

void setup() {
  pinMode(PIN_PIR, INPUT);
  nodo::iniciar();
  Serial.println("[pir] estabilizando el sensor 60 s: en este rato no se publican movimientos");
}

void loop() {
  nodo::atender(true);
  bool ahora = digitalRead(PIN_PIR);
  if (ahora == HIGH) { ultimaDeteccion = millis(); hayDeteccion = true; }
  nodo::alerta = hayDeteccion && !nodo::transcurrido(ultimaDeteccion, ROJO_MS);
  if (!caliente) {
    if (millis() < CALENTAMIENTO_MS) { anterior = ahora; return; }
    caliente = true;
    Serial.println("[pir] sensor listo");
  }
  if (ahora == HIGH && anterior == LOW &&
      (primerMovimiento || nodo::transcurrido(ultimoMovimiento, ANTIRREBOTE_MS))) {
    primerMovimiento = false;
    ultimoMovimiento = millis();
    nodo::publicarEvento("movimiento");
  }
  anterior = ahora;
}
