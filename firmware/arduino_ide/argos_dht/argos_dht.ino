// Argos, nodo dht. GENERADO por firmware/herramientas/exportar_arduino.py desde firmware/src/dht/main.cpp (editar alla y regenerar).
// v2 (22-nov, Ivan): pantalla siempre encendida y el boton solo silencia (una pulsacion corta, sin pulsacion larga).
// Con proteccion de la OLED: brillo bajo en estado normal y corrimiento lento de la imagen.
// Pendiente: pasar este mismo cambio a firmware/src/dht/main.cpp para que no se pierda al regenerar.
// Placa: NodeMCU 1.0 (ESP-12E Module). Credenciales: copiar secrets.example.h a secrets.h en esta carpeta.
#define NODO_ID "dht"
#define USAR_OLED 1
// Nodo dht: DHT22 + buzzer (via 2N2222) + boton + LED verde/rojo (+ OLED SSD1309 2.42" I2C).
// Firmware de REFERENCIA: valida pines y el contrato MQTT de CLAUDE.md. Solo se ha compilado;
// no se ha probado en hardware. No flashear sin aprobacion.
// WiFi, MQTT y LED en nodo_comun.h; reglas de aviso en alarma_dht.h (probadas en la PC).

// Para la Expo (fuera del cuarto de incubacion): quita las dos diagonales de la linea de abajo. Usa rangos
// amplios (alarma_dht.h) y lee cada 5 s, asi la alarma reacciona en 15 s y no suena sola por el aire acondicionado.
// Con el nodo instalado en el cuarto debe quedar comentada.
// #define MODO_DEMO

#include "nodo_comun.h"
#include "alarma_dht.h"
#include <DHT.h>
#if USAR_OLED
#include <U8g2lib.h>
#include "vista_oled.h"
#endif

// ── Pines (CLAUDE.md §3; LED en nodo_comun.h) ───────────────────────────────
#if USAR_OLED
constexpr uint8_t PIN_DHT = D4;  // GPIO2: D1/D2 quedan para la OLED
// OLED 2.42" SSD1309, modulo ZJY_M242 de 7 pines, EN SPI como viene de fabrica (19-nov: no es I2C de 4 pines).
// SPI por software: no usa los pines del SPI de hardware (D5 y D7, ocupados por el buzzer y el LED verde).
// El pin CS de la pantalla va fijo a GND.
constexpr uint8_t PIN_OLED_SCL = D1;  // reloj
constexpr uint8_t PIN_OLED_SDA = D2;  // datos
constexpr uint8_t PIN_OLED_DC = D3;   // dato/comando (GPIO0: la pantalla no lo baja, el arranque no se afecta)
constexpr uint8_t PIN_OLED_RES = D0;  // reinicio de la pantalla
#else
constexpr uint8_t PIN_DHT = D2;  // GPIO4
#endif
constexpr uint8_t PIN_BUZZER = D5;  // base de Q1 via R3 (1 k); R4 (10 k) a GND
constexpr uint8_t PIN_BOTON = D6;   // a GND, INPUT_PULLUP

#ifdef MODO_DEMO
constexpr uint32_t PERIODO_MS = 5000;    // demo: 3 lecturas = 15 s (el DHT22 admite una lectura cada 2 s)
#else
constexpr uint32_t PERIODO_MS = 30000;   // muestreo y publicacion
#endif
constexpr uint32_t ANTIRREBOTE_MS = 40;
// Proteccion de la OLED (queda encendida siempre): brillo bajo en estado normal y la imagen se corre
// 1 px a la derecha cada minuto, hasta DESPLAZA_MAX y de regreso, para que no se marquen siempre los mismos puntos.
// La vista ocupa como mucho ~92 px de ancho, (estimado, sin medir en la pantalla), asi que con 24 px de corrimiento no deberia cortarse nada.
constexpr uint8_t BRILLO_NORMAL = 80;    // 0-255
constexpr uint8_t BRILLO_ALARMA = 255;   // con alarma o falla: brillo completo
constexpr uint8_t DESPLAZA_MAX = 24;     // px
constexpr uint8_t ANCHO_BARRA = 128 - DESPLAZA_MAX;  // ancho de la barra de alarma: cabe "ALARMA SILENCIADA" (87 px)
constexpr uint32_t DESPLAZA_MS = 60000;  // un paso por minuto (ida y vuelta en ~48 min)

const char* const TOPIC_CMD_ALARMA = TOPIC_RAIZ "cmd/alarma";
const char* const TOPIC_CMD_SILENCIAR = TOPIC_RAIZ "cmd/silenciar";

DHT dht(PIN_DHT, DHT22);
alarma::Alarma reglas;
#if USAR_OLED
// R0 = imagen derecha con la cinta naranja de la pantalla hacia ABAJO. Si sale de cabeza, cambiar U8G2_R0 por U8G2_R2.
U8G2_SSD1309_128X64_NONAME0_F_4W_SW_SPI pantalla(U8G2_R0, PIN_OLED_SCL, PIN_OLED_SDA, U8X8_PIN_NONE, PIN_OLED_DC, PIN_OLED_RES);
#endif

uint32_t ultimoMuestreo = 0;

// ── MQTT + API ───────────────────────────────────────────────────────────────
// Manda T y HR juntas: por MQTT (tiempo real) y por HTTP POST a la API (se guardan en MySQL).
void publicarTelemetria() {
  Serial.printf("[dht] T = %.1f C  HR = %.1f %%\n", reglas.temperatura, reglas.humedad);
  StaticJsonDocument<256> doc;
  JsonArray lecturas = doc.createNestedArray("lecturas");
  JsonObject t = lecturas.createNestedObject();
  t["parametro"] = "temperatura";
  t["valor"] = roundf(reglas.temperatura * 10) / 10;
  t["unidad"] = "C";
  JsonObject h = lecturas.createNestedObject();
  h["parametro"] = "humedad";
  h["valor"] = roundf(reglas.humedad * 10) / 10;
  h["unidad"] = "%";
  nodo::enviarLecturas(doc);
}

// GET /api/comandos/dht -> {"alarma":"on"|"off"}. Respaldo de cmd/alarma por si MQTT no esta conectado:
// la orden de la nube llega por cualquiera de los dos caminos.
void consultarComandos() {
  String r;
  if (api::pedir("GET", "/api/comandos/" NODO_ID, nullptr, &r) != 200) return;
  StaticJsonDocument<96> doc;
  if (deserializeJson(doc, r)) return;  // respuesta que no es JSON: se ignora
  const char* orden = doc["alarma"] | "";
  if (strcmp(orden, "on") == 0) reglas.orden_nube(true, millis());
  else if (strcmp(orden, "off") == 0) reglas.orden_nube(false, millis());
}

// Boton = solo silenciar. Sin alarma vigente no hace nada (asi no queda silenciada la siguiente alarma).
// Con la alarma ya silenciada, otra pulsacion vuelve a contar los 30 min.
void silenciar() {
  if (!reglas.salidas(millis()).alarma) {
    Serial.println("[dht] boton: no hay alarma, no se silencia nada");
    return;
  }
  reglas.silenciar(millis());
  Serial.println("[dht] buzzer silenciado 30 min (boton)");
  if (nodo::mqtt.connected()) nodo::mqtt.publish(TOPIC_CMD_SILENCIAR, "{\"minutos\":30}");
  api::accion("buzzer", "off", "manual", 30 * 60);  // evento de actuacion: silencio manual de 30 min
}

void alRecibir(char* topic, byte* payload, unsigned int largo) {
  if (strcmp(topic, TOPIC_CMD_ALARMA) != 0) return;
  String orden;
  for (unsigned int i = 0; i < largo; i++) orden += (char)payload[i];
  orden.trim();
  Serial.printf("[dht] cmd/alarma por MQTT: %s\n", orden.c_str());
  if (orden == "on") reglas.orden_nube(true, millis());
  else if (orden == "off") reglas.orden_nube(false, millis());
}

void suscribir() { nodo::mqtt.subscribe(TOPIC_CMD_ALARMA); }

// ── sensor ───────────────────────────────────────────────────────────────────
void muestrear() {
  switch (reglas.muestra(dht.readTemperature(), dht.readHumidity())) {
    case alarma::Lectura::valida: publicarTelemetria(); break;
    case alarma::Lectura::falla_nueva: nodo::publicarEvento("sensor_error"); break;
    case alarma::Lectura::invalida: Serial.println("[dht] lectura invalida (NaN o fuera de rango): no se envia"); break;
  }
  if (!nodo::mqtt.connected()) consultarComandos();  // respaldo: con MQTT conectado la orden ya llega por cmd/alarma
}

// ── boton ────────────────────────────────────────────────────────────────────
// Silencia al apretarlo (pulsacion corta). La pantalla ya no depende del boton: siempre esta encendida.
void atenderBoton() {
  static bool estable = HIGH, anterior = HIGH;
  static uint32_t cambio = 0;
  bool lectura = digitalRead(PIN_BOTON);
  if (lectura != anterior) { cambio = millis(); anterior = lectura; }
  if (!nodo::transcurrido(cambio, ANTIRREBOTE_MS) || lectura == estable) return;
  estable = lectura;
  if (estable == LOW) silenciar();
}

// ── salidas ──────────────────────────────────────────────────────────────────
#if USAR_OLED
void dibujarPantalla(const alarma::Salidas& s) {
  static uint32_t ultimoDibujo = 0;
  if (!nodo::transcurrido(ultimoDibujo, 1000)) return;
  ultimoDibujo = millis();
  // La vista vive en include/vista_oled.h (se revisa en la PC con herramientas/oled_host.py)
  VistaOled v = {reglas.temperatura, reglas.humedad, reglas.hay_dato(), s.falla, nodo::enLinea(), s.alarma,
                 s.silenciada, reglas.temp.etiqueta(reglas.temperatura), reglas.hum.etiqueta(reglas.humedad)};
  vista_oled_dibujar(pantalla.getU8g2(), &v);

  // ── proteccion contra marcas ──
  static uint8_t brillo = 0, desplaza = 0;
  static int8_t paso = 1;
  static uint32_t ultimoPaso = 0;
  bool destacada = s.alarma || s.falla;  // barra invertida (fondo claro de lado a lado)
  // Brillo completo solo mientras la alarma no se ha atendido; silenciada vuelve al brillo normal.
  uint8_t brilloNuevo = (destacada && !s.silenciada) ? BRILLO_ALARMA : BRILLO_NORMAL;
  if (brilloNuevo != brillo) { brillo = brilloNuevo; pantalla.setContrast(brillo); }
  if (nodo::transcurrido(ultimoPaso, DESPLAZA_MS)) {
    ultimoPaso = millis();
    if (desplaza == 0) paso = 1; else if (desplaza >= DESPLAZA_MAX) paso = -1;
    desplaza += paso;
  }
  // Tambien se corre con alarma (una alarma puede durar horas). Unica excepcion: alarma y sin red a la vez,
  // porque ahi "SIN RED" va pegado al borde derecho: la barra queda completa y sin correrse.
  if (!(destacada && !nodo::enLinea())) {
    // El buffer son 8 filas de 128 bytes (cada byte = 8 puntos en vertical): correr k bytes = correr k px a la derecha.
    uint8_t* buf = pantalla.getBufferPtr();
    if (desplaza > 0) {
      for (uint8_t fila = 0; fila < 8; fila++) {
        uint8_t* f = buf + fila * 128;
        memmove(f + desplaza, f, 128 - desplaza);
        memset(f, 0, desplaza);
      }
    }
    if (destacada) {
      // La barra invertida (10 px de alto, y 0-9) se recorta a ANCHO_BARRA para que tambien se mueva con la imagen:
      // asi no queda una franja fija de lado a lado. Se apaga lo que sobra a su derecha.
      for (uint8_t x = desplaza + ANCHO_BARRA; x < 128; x++) { buf[x] = 0; buf[128 + x] &= ~0x03; }
    }
  }
  pantalla.sendBuffer();
}
#endif

// ── setup / loop ─────────────────────────────────────────────────────────────
void setup() {
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_BOTON, INPUT_PULLUP);
  digitalWrite(PIN_BUZZER, HIGH);  // autoprueba: un pitido corto al arrancar (si no suena, revisar Q1 y el buzzer)
  delay(80);
  digitalWrite(PIN_BUZZER, LOW);
  dht.begin();
#if USAR_OLED
  pantalla.begin();  // reinicia la pantalla por RES y la enciende; se queda encendida siempre
#endif
  nodo::iniciar();
  nodo::mqtt.setCallback(alRecibir);
  nodo::alConectar = suscribir;
  ultimoMuestreo = millis() - PERIODO_MS + 3000;  // primera lectura a los ~3 s
}

void loop() {
  nodo::atender(true);  // con latido: si el sensor falla y no hay lecturas, el nodo sigue apareciendo en linea
  if (nodo::transcurrido(ultimoMuestreo, PERIODO_MS)) {
    ultimoMuestreo = millis();
    muestrear();
  }
  atenderBoton();
  alarma::Salidas s = reglas.salidas(millis());
  digitalWrite(PIN_BUZZER, s.buzzer ? HIGH : LOW);
  nodo::alerta = s.rojo;         // fijo = alerta propia
  nodo::sensorFalla = s.falla;   // parpadeo rapido
#if USAR_OLED
  dibujarPantalla(s);
#endif
}
