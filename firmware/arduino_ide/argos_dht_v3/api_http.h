// Cliente HTTP de la API REST de Argos (servidor/api/RestApi.js).
// El nodo GUARDA sus datos por HTTP (la API es la unica que escribe en MySQL; el nodo nunca toca la BD)
// y usa MQTT aparte para lo de tiempo real (estado/LWT, cmd/alarma). Si uno de los dos falla, el otro sigue.
//
// Manejo de errores:
//   - sin WiFi: no intenta (no bloquea el loop) y lo dice por el monitor serial
//   - sin respuesta o error del servidor (5xx): reintenta UNA vez
//   - 400 (dato rechazado) o 401 (clave): no reintenta, porque repetirlo daria lo mismo; lo explica por serial
//   - API caida: tras 3 fallas de conexion seguidas deja de intentar durante 30 s. Sin esto, cada envio
//     congelaria el loop hasta 2 x TIMEOUT_MS (con reintento) y el nodo perderia pulsaciones, golpes y movimientos.
//
// HTTP o HTTPS segun API_PORT (secrets.h):
//   - 443: HTTPS, para llegar por el tunel de Cloudflare (API_HOST = xxxx.trycloudflare.com). Cloudflare
//     redirige http:// a https:// (301), asi que por el tunel HTTP plano no llega a la API.
//   - otro (3001-3005): HTTP plano, con el servidor en la misma red (API_HOST = IP del servidor).
#pragma once
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

namespace api {

constexpr bool USAR_HTTPS = (API_PORT == 443);
// Tope de espera por peticion: el loop no se congela mas que esto. En red local la API contesta en menos de 0.1 s;
// por HTTPS el ESP8266 tarda 1-2 s en negociar cada conexion, mas el viaje por internet.
constexpr uint16_t TIMEOUT_MS = USAR_HTTPS ? 5000 : 1000;
constexpr uint8_t FALLAS_PARA_PAUSA = 3;
constexpr uint32_t PAUSA_MS = 30000;
constexpr int EN_PAUSA = -100;         // codigo propio: no se intento porque la API esta en pausa
inline WiFiClient redPlana;            // conexiones propias (MQTT usa otra)
inline BearSSL::WiFiClientSecure redSegura;
inline bool seguraLista = false;

// Conexion a usar. La segura cifra pero NO valida el certificado (setInsecure): el de trycloudflare.com
// cambia y validarlo haria fallar al nodo sin aviso. La clave sigue viajando cifrada.
inline WiFiClient& red() {
  if (!USAR_HTTPS) return redPlana;
  if (!seguraLista) {
    redSegura.setInsecure();
    // Buffers de 1 KB en vez de 16 KB si el servidor lo acepta (ahorra RAM). Si no, se queda con los normales.
    bool chico = BearSSL::WiFiClientSecure::probeMaxFragmentLength(API_HOST, API_PORT, 1024);
    if (chico) redSegura.setBufferSizes(1024, 1024);
    Serial.printf("[api] HTTPS a %s (buffers %s)\n", API_HOST, chico ? "1 KB" : "16 KB");
    seguraLista = true;
  }
  return redSegura;
}
inline uint8_t fallas = 0;             // fallas de conexion seguidas
inline uint32_t ultimaFalla = 0;
inline bool ok = false;                // la ultima peticion la acepto la API (2xx): sirve para el LED verde

inline bool enPausa() { return fallas >= FALLAS_PARA_PAUSA && (uint32_t)(millis() - ultimaFalla) < PAUSA_MS; }

// Hace una peticion y regresa el codigo HTTP (negativo = no hubo conexion). Imprime el resultado.
inline int pedir(const char* metodo, const char* ruta, const char* cuerpo, String* respuesta = nullptr) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.printf("[api] %s %s: sin WiFi, no se envia\n", metodo, ruta);
    return -1;
  }
  if (enPausa()) return EN_PAUSA;
  HTTPClient http;
  http.setTimeout(TIMEOUT_MS);
  String url = String(USAR_HTTPS ? "https://" : "http://") + API_HOST + ":" + String(API_PORT) + ruta;
  if (!http.begin(red(), url)) {
    Serial.printf("[api] URL invalida: %s\n", url.c_str());
    return -1;
  }
  http.addHeader("X-API-Key", API_KEY);
  int codigo;
  if (cuerpo) {
    http.addHeader("Content-Type", "application/json");
    codigo = http.POST(cuerpo);
  } else {
    codigo = http.GET();
  }
  String r = codigo > 0 ? http.getString() : HTTPClient::errorToString(codigo);
  http.end();
  Serial.printf("[api] %s %s -> %d %s\n", metodo, ruta, codigo, r.c_str());
  ok = codigo >= 200 && codigo < 300;
  if (codigo < 0) {
    if (fallas < 255) fallas++;
    ultimaFalla = millis();
    if (fallas == FALLAS_PARA_PAUSA) Serial.println("[api] la API no responde: se pausa 30 s (revisa API_HOST y que el servidor este prendido)");
  } else {
    fallas = 0;
  }
  if (respuesta) *respuesta = r;
  return codigo;
}

// POST con un reintento (reintentar = false para lo que no vale la pena repetir). true si la API lo guardo (2xx).
inline bool enviar(const char* ruta, const char* json, bool reintentar = true) {
  if (enPausa()) return false;
  Serial.printf("[api] enviando %s\n", json);
  int c = pedir("POST", ruta, json);
  if (reintentar && ((c < 0 && WiFi.status() == WL_CONNECTED && fallas < 2) || c >= 500)) {  // solo reintenta la primera falla
    delay(200);
    c = pedir("POST", ruta, json);
  }
  if (c == 400) Serial.println("[api] la API rechazo el dato (400): no se guardo");
  if (c == 401) Serial.println("[api] clave incorrecta (401): revisa API_KEY en secrets.h");
  return c >= 200 && c < 300;
}

// Evento de actuacion: el LED rojo o el buzzer cambio de estado.
// origen: "local" (lo decidio el nodo) o "manual" (boton). duracion_s = 0 -> hasta el siguiente cambio.
inline bool accion(const char* actuador, const char* comando, const char* origen, uint16_t duracion_s = 0) {
  char json[160];
  if (duracion_s)
    snprintf(json, sizeof json, "{\"nodo\":\"%s\",\"actuador\":\"%s\",\"comando\":\"%s\",\"origen\":\"%s\",\"duracion_s\":%u}",
             NODO_ID, actuador, comando, origen, duracion_s);
  else
    snprintf(json, sizeof json, "{\"nodo\":\"%s\",\"actuador\":\"%s\",\"comando\":\"%s\",\"origen\":\"%s\"}",
             NODO_ID, actuador, comando, origen);
  return enviar("/api/acciones", json, false);  // sin reintento: es un registro, no vale congelar el loop por el
}

}  // namespace api
