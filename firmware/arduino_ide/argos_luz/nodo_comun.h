// Partes comunes de los 5 nodos: WiFi, MQTT (contrato de CLAUDE.md), estado retenido + LWT, latido,
// LED de estado y envio a la API REST. Cada lectura/evento sale por los DOS caminos, independientes:
//   HTTP POST a la API  -> se guarda en MySQL (Etapa 3)
//   MQTT a Mosquitto    -> tiempo real (dashboard en vivo, estado/LWT, cmd/alarma)
// Firmware de REFERENCIA: solo compilado.
#pragma once
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif
#include "api_http.h"

constexpr uint8_t PIN_LED_V = D7;  // 330 ohm a GND
constexpr uint8_t PIN_LED_R = D8;  // 330 ohm a GND (GPIO15: bajo en el arranque)
constexpr uint32_t LATIDO_MS = 60000;
constexpr uint32_t REINTENTO_MQTT_MS = 5000;      // primer reintento; se duplica hasta REINTENTO_MQTT_MAX_MS
constexpr uint32_t REINTENTO_MQTT_MAX_MS = 60000;
constexpr uint32_t AUTOPRUEBA_MS = 300;           // al arrancar: verde y rojo se prenden un momento

namespace nodo {

// Broker publico (broker.hivemq.com, compartido con todo el mundo): el prefijo argos-eq2 evita chocar
// con los topicos y los ID de cliente de otros equipos. Debe coincidir con TOPIC_RAIZ de servidor/central/motor.js.
#define TOPIC_RAIZ "argos-eq2/invernadero/"
const char* const TOPIC_TELEMETRIA = TOPIC_RAIZ "telemetria/" NODO_ID;
const char* const TOPIC_EVENTO = TOPIC_RAIZ "evento/" NODO_ID;
const char* const TOPIC_ESTADO = TOPIC_RAIZ "estado/" NODO_ID;
const char* const CLIENT_ID = "argos-eq2-nodo-" NODO_ID;
const char* const LWT_OFFLINE = "{\"estado\":\"offline\"}";

inline WiFiClient red;
inline PubSubClient mqtt(red);
inline uint32_t ultimoIntento = 0;
inline uint32_t esperaMqtt = REINTENTO_MQTT_MS;  // crece si el broker no contesta: asi no congela el loop cada 5 s
inline bool wifiAnunciado = false;
inline uint32_t ultimoLatido = 0;
inline bool alerta = false;       // LED rojo fijo
inline bool sensorFalla = false;  // LED rojo parpadeo rapido
inline bool alertaRegistrada = false;  // ultimo estado del LED rojo que se mando a la API
inline void (*alConectar)() = nullptr;  // tras cada conexion al broker (p. ej. suscripciones del dht)

inline bool transcurrido(uint32_t desde, uint32_t ms) { return (uint32_t)(millis() - desde) >= ms; }

// En linea = hay WiFi y al menos un camino funciona: el broker MQTT o la API (su ultima peticion salio bien).
// Asi el LED verde queda fijo aunque no haya Mosquitto, mientras los datos si se esten guardando.
inline bool enLinea() { return WiFi.status() == WL_CONNECTED && (mqtt.connected() || api::ok); }
inline bool eventoGuardado = false;  // el ultimo publicarEvento lo guardo la API (MQTT no confirma la entrega)

// Manda un documento {"lecturas":[...]} por los dos caminos: MQTT tal cual (contrato) y a la API con "nodo".
inline void enviarLecturas(JsonDocument& doc) {
  char buf[256];
  if (mqtt.connected()) {
    serializeJson(doc, buf);
    mqtt.publish(TOPIC_TELEMETRIA, buf);
  }
  doc["nodo"] = NODO_ID;
  serializeJson(doc, buf);
  api::enviar("/api/mediciones", buf);
}

inline void publicarLectura(const char* parametro, float valor, const char* unidad) {
  StaticJsonDocument<192> doc;
  JsonObject l = doc.createNestedArray("lecturas").createNestedObject();
  l["parametro"] = parametro;
  l["valor"] = roundf(valor * 10) / 10;
  l["unidad"] = unidad;
  Serial.printf("[%s] %s = %.1f %s\n", NODO_ID, parametro, valor, unidad);
  enviarLecturas(doc);
}

// Regresa true si el evento salio por al menos un camino (la API lo guardo o MQTT lo publico).
// porMqttTambien = false al REENVIAR un evento que la API no guardo: por MQTT ya salio la primera vez.
inline bool publicarEvento(const char* tipo, float magnitud = NAN, bool porMqttTambien = true) {
  StaticJsonDocument<128> doc;
  doc["tipo"] = tipo;
  if (!isnan(magnitud)) doc["magnitud"] = roundf(magnitud * 100) / 100;
  Serial.printf("[%s] evento %s\n", NODO_ID, tipo);
  char buf[128];
  bool porMqtt = false;
  if (porMqttTambien && mqtt.connected()) {
    serializeJson(doc, buf);
    porMqtt = mqtt.publish(TOPIC_EVENTO, buf);
  }
  doc["nodo"] = NODO_ID;
  serializeJson(doc, buf);
  bool porApi = api::enviar("/api/eventos", buf);
  eventoGuardado = porApi;
  return porApi || porMqtt;
}

// Latido: por MQTT (contrato) y a la API (marca al nodo como vivo; sin el, la API abre "nodo_sin_reporte").
inline void latido() {
  if (mqtt.connected()) {
    StaticJsonDocument<96> doc;
    JsonObject l = doc.createNestedArray("lecturas").createNestedObject();
    l["parametro"] = "latido";
    l["valor"] = 1;
    l["unidad"] = "";
    char buf[96];
    serializeJson(doc, buf);
    mqtt.publish(TOPIC_TELEMETRIA, buf);
  }
  char json[128];
  snprintf(json, sizeof json, "{\"nodo\":\"%s\",\"uptime_s\":%lu,\"rssi\":%d}", NODO_ID,
           (unsigned long)(millis() / 1000), (int)WiFi.RSSI());
  api::enviar("/api/latido", json);
}

inline void conectarMqtt() {
  ultimoIntento = millis();
  if (!mqtt.connect(CLIENT_ID, NODO_ID, MQTT_PASSWORD, TOPIC_ESTADO, 1, true, LWT_OFFLINE)) {
    // -2 = no hay broker en MQTT_HOST:MQTT_PORT; 4 o 5 = usuario o contrasena rechazados
    Serial.printf("[mqtt] sin conexion (estado %d); reintento en %lu s\n", mqtt.state(), (unsigned long)(esperaMqtt / 1000));
    esperaMqtt = esperaMqtt * 2 > REINTENTO_MQTT_MAX_MS ? REINTENTO_MQTT_MAX_MS : esperaMqtt * 2;
    return;
  }
  esperaMqtt = REINTENTO_MQTT_MS;
  Serial.println("[mqtt] conectado al broker");
  StaticJsonDocument<192> doc;
  doc["estado"] = "online";
  doc["reset_reason"] = ESP.getResetReason();
  doc["uptime_s"] = millis() / 1000;
  doc["rssi"] = WiFi.RSSI();
  char buf[192];
  serializeJson(doc, buf);
  mqtt.publish(TOPIC_ESTADO, buf, true);  // retenido
  if (alConectar) alConectar();
}

inline void iniciar() {
  pinMode(PIN_LED_V, OUTPUT);
  pinMode(PIN_LED_R, OUTPUT);
  Serial.begin(115200);
  Serial.printf("\n[%s] Argos arrancando (%s)\n", NODO_ID, ESP.getResetReason().c_str());
  // Autoprueba: los dos LED se prenden un momento. Si alguno no prende, revisar su soldadura y su polaridad.
  digitalWrite(PIN_LED_V, HIGH);
  delay(AUTOPRUEBA_MS);
  digitalWrite(PIN_LED_V, LOW);
  digitalWrite(PIN_LED_R, HIGH);
  delay(AUTOPRUEBA_MS);
  digitalWrite(PIN_LED_R, LOW);
  WiFi.persistent(false);  // no reescribe la flash con el SSID en cada arranque
  WiFi.mode(WIFI_STA);
  WiFi.hostname(CLIENT_ID);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setKeepAlive(45);
  mqtt.setSocketTimeout(4);  // por omision son 15 s de loop congelado si el broker no contesta
  red.setTimeout(3000);      // tope del intento de conexion TCP al broker
}

// Llamar en cada vuelta de loop(). con_latido = false en nodos que ya publican cada 60 s.
inline void atender(bool con_latido) {
  if (WiFi.status() == WL_CONNECTED) {
    if (!wifiAnunciado) {
      wifiAnunciado = true;
      esperaMqtt = REINTENTO_MQTT_MS;          // red nueva: el broker se reintenta ya, no hasta 60 s despues
      ultimoIntento = millis() - esperaMqtt;
      ultimoLatido = millis() - LATIDO_MS;     // y el primer latido sale de inmediato (el panel lo ve en linea)
      Serial.printf("[wifi] conectado, IP %s, senal %d dBm\n", WiFi.localIP().toString().c_str(), (int)WiFi.RSSI());
    }
    if (!mqtt.connected() && transcurrido(ultimoIntento, esperaMqtt)) conectarMqtt();
    mqtt.loop();
  } else {
    wifiAnunciado = false;
  }
  if (con_latido && transcurrido(ultimoLatido, LATIDO_MS)) {
    ultimoLatido = millis();
    latido();
  }
  // Evento de actuacion: cada vez que el LED rojo cambia, se registra en la API (AccionControl).
  // Si no hay WiFi, espera: al volver la red manda el estado actual.
  if (alerta != alertaRegistrada && WiFi.status() == WL_CONNECTED) {
    alertaRegistrada = alerta;
    api::accion("led_rojo", alerta ? "on" : "off", "local");
  }
  digitalWrite(PIN_LED_V, enLinea() ? HIGH : ((millis() / 1000) % 2));  // fijo o parpadeo lento
  if (sensorFalla) digitalWrite(PIN_LED_R, (millis() / 125) % 2);       // parpadeo rapido
  else digitalWrite(PIN_LED_R, alerta ? HIGH : LOW);
}

}  // namespace nodo
