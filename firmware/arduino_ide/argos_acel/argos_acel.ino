// Argos, nodo acel. GENERADO por firmware/herramientas/exportar_arduino.py desde firmware/src/acel/main.cpp (editar alla y regenerar).
// Placa: NodeMCU 1.0 (ESP-12E Module). Credenciales: copiar secrets.example.h a secrets.h en esta carpeta.
#define NODO_ID "acel"
// Nodo acel: GY-61 (ADXL335) leido por un ADS1115 (I2C 0x48, D1 SCL / D2 SDA).
// Publica "golpe" cuando la aceleracion se aparta del reposo mas que el umbral. El umbral se calibra
// en sitio [POR CONFIRMAR]; el cierre de la alerta (5 min) lo hace n8n. Latido cada 60 s.
// Actuador: LED rojo encendido 5 s despues de cada golpe.
//
// Reposo medido, no supuesto: al arrancar promedia 64 lecturas de cada eje (el anaquel debe estar quieto
// 1 s) y despues compara contra ese reposo. Asi no importa el voltaje exacto de 0 g del modulo, que
// cambia de una pieza a otra y con el regulador del GY-61; con un valor fijo saldrian golpes falsos.
// El reposo se sigue ajustando muy despacio (deriva termica, anaquel que queda un poco inclinado).
// Si el ADS1115 no responde o un eje queda pegado a 0 V o a 3.3 V: sensor_error y reintento cada 10 s.
// Firmware de referencia: solo compilado.
#include "nodo_comun.h"
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

constexpr float SENSIBILIDAD = 0.330f;  // V/g a 3.3 V (ratiometrico) [calibrar]
constexpr float UMBRAL_G = 0.5f;        // [POR CONFIRMAR en sitio]
constexpr float V_MIN = 0.15f, V_MAX = 3.15f;  // fuera de esto el eje esta suelto o en corto
constexpr float SEGUIMIENTO = 0.002f;   // fraccion del reposo que se corrige en cada lectura
constexpr uint8_t MUESTRAS_REPOSO = 64;
constexpr uint8_t PEGADO_MAX = 20;      // lecturas seguidas fuera de rango para declarar falla
constexpr uint32_t ANTIRREBOTE_MS = 2000;
constexpr uint32_t ROJO_MS = 5000;
constexpr uint32_t REINTENTO_SENSOR_MS = 10000;
constexpr uint32_t AVISO_MS = 5000;     // reintento del aviso sensor_error mientras no se entregue

Adafruit_ADS1115 ads;
float reposo[3];
uint32_t ultimoGolpe = 0;
bool primerGolpe = true;
bool fallaPendiente = false;  // falta avisar sensor_error
uint32_t ultimoIntentoSensor = 0;
uint8_t pegado = 0;
uint32_t ultimoAviso = 0;
float pico = 0;               // mayor desviacion de los ultimos 5 s: se imprime para calibrar UMBRAL_G
uint32_t ultimoPico = 0;

// La libreria espera la conversion sin limite de tiempo: si el ADS1115 se afloja, el nodo se colgaria y lo
// reiniciaria el watchdog. Por eso se pregunta primero si sigue en el bus.
bool adsPresente() {
  Wire.beginTransmission(0x48);
  return Wire.endTransmission() == 0;
}

void leer(float v[3]) {
  for (uint8_t i = 0; i < 3; i++) v[i] = ads.computeVolts(ads.readADC_SingleEnded(i));
}

bool enRango(const float v[3]) {
  for (uint8_t i = 0; i < 3; i++)
    if (v[i] < V_MIN || v[i] > V_MAX) return false;
  return true;
}

// Arranca el ADS1115 y mide el reposo. false si no responde o si algun eje esta fuera de rango.
bool iniciarSensor() {
  if (!ads.begin(0x48)) {
    Serial.println("[acel] el ADS1115 no responde en 0x48: revisa SDA (D2), SCL (D1), 3V3, GND y ADDR a GND");
    return false;
  }
  Wire.setClock(400000);                 // despues de begin (que lo regresa a 100 kHz): cada lectura baja de ~3 a ~1.7 ms
  ads.setGain(GAIN_ONE);                 // +-4.096 V
  ads.setDataRate(RATE_ADS1115_860SPS);  // ~3 ms por canal
  float suma[3] = {0, 0, 0}, v[3];
  for (uint8_t n = 0; n < MUESTRAS_REPOSO; n++) {
    leer(v);
    for (uint8_t i = 0; i < 3; i++) suma[i] += v[i];
    yield();
  }
  for (uint8_t i = 0; i < 3; i++) reposo[i] = suma[i] / MUESTRAS_REPOSO;
  Serial.printf("[acel] reposo X=%.3f V  Y=%.3f V  Z=%.3f V\n", reposo[0], reposo[1], reposo[2]);
  if (!enRango(reposo)) {
    Serial.println("[acel] un eje esta en 0 V o en 3.3 V: revisa los cables X, Y, Z del GY-61 a A0, A1, A2");
    return false;
  }
  pegado = 0;
  return true;
}

void marcarFalla() {
  nodo::sensorFalla = true;
  fallaPendiente = true;
  ultimoIntentoSensor = millis();
  ultimoAviso = millis() - AVISO_MS;  // el primer aviso sale de inmediato
}

void setup() {
  nodo::iniciar();
  Wire.begin();  // SDA = D2, SCL = D1
  if (!iniciarSensor()) marcarFalla();
}

void loop() {
  nodo::atender(true);
  nodo::alerta = !primerGolpe && !nodo::transcurrido(ultimoGolpe, ROJO_MS);
  if (nodo::sensorFalla) {
    if (fallaPendiente && WiFi.status() == WL_CONNECTED && nodo::transcurrido(ultimoAviso, AVISO_MS)) {
      ultimoAviso = millis();  // un intento cada 5 s, no uno por vuelta
      if (nodo::publicarEvento("sensor_error")) fallaPendiente = false;
    }
    if (nodo::transcurrido(ultimoIntentoSensor, REINTENTO_SENSOR_MS)) {
      ultimoIntentoSensor = millis();
      if (iniciarSensor()) nodo::sensorFalla = false;
    }
    return;
  }
  if (!adsPresente()) {
    Serial.println("[acel] el ADS1115 dejo de responder: revisa sus cables");
    marcarFalla();
    return;
  }
  float v[3];
  leer(v);
  if (!enRango(v)) {
    if (++pegado >= PEGADO_MAX) marcarFalla();
    return;
  }
  pegado = 0;
  float suma = 0;
  for (uint8_t i = 0; i < 3; i++) {
    float d = (v[i] - reposo[i]) / SENSIBILIDAD;
    suma += d * d;
    reposo[i] += SEGUIMIENTO * (v[i] - reposo[i]);
  }
  float desviacion = sqrtf(suma);  // en g, respecto al reposo
  if (desviacion > pico) pico = desviacion;
  if (nodo::transcurrido(ultimoPico, 5000)) {  // para calibrar: golpea el anaquel y mira que pico sale
    Serial.printf("[acel] pico de los ultimos 5 s: %.2f g (umbral %.2f g)\n", pico, UMBRAL_G);
    ultimoPico = millis();
    pico = 0;
  }
  if (desviacion > UMBRAL_G && (primerGolpe || nodo::transcurrido(ultimoGolpe, ANTIRREBOTE_MS))) {
    primerGolpe = false;
    ultimoGolpe = millis();
    nodo::publicarEvento("golpe", desviacion);
  }
}
