// Argos · PRUEBA COMPLETA DEL NODO dht (no es el firmware del nodo; no usa WiFi ni el servidor).
// Placa: NodeMCU 1.0 (ESP-12E Module). Monitor serie: 115200 baudios, "Ambos NL & CR" o "Nueva línea".
// Librerías: las mismas del nodo: "DHT sensor library" (Adafruit) y "U8g2".
//
// Qué hace:
//   1. Prueba guiada al arrancar: LED verde, LED rojo, buzzer, pantalla y botón.
//   2. Después se queda vigilando el DHT22 cada 2.5 s, cuenta lecturas buenas y fallidas y lo muestra en la
//      pantalla y en el monitor serie. Sirve para la "prueba de meneo": mueve un cable a la vez y mira si
//      sube el contador de fallas. El cable que hace fallar el DHT22 es el del falso contacto.
//
// Conexiones que prueba (las del nodo dht, CLAUDE.md §3):
//   DHT22 datos (out) -> D4        LED verde -> D7 (330 ohm)      Buzzer: base del 2N2222 -> D5 (1 k)
//   Botón -> D6 a GND              LED rojo  -> D8 (330 ohm)
//   OLED SSD1309 SPI: SCL D1, SDA D2, DC D3, RES D0, CS a GND, VCC 3V3
//
// Comandos por el monitor serie (escribe la letra y Enter):
//   h ayuda · l LEDs · b buzzer · o patrón de pantalla · t botón · p niveles de los pines · r reiniciar contadores
//   w prende o apaga la carga de WiFi (escanea redes sin parar, como cuando el nodo busca su red)
//   z prende o apaga el buzzer FIJO mientras se sigue leyendo el DHT22 (cuenta fallas con el buzzer sonando)

#include <DHT.h>
#include <U8g2lib.h>
#include <ESP8266WiFi.h>

constexpr uint8_t PIN_DHT = D4;
constexpr uint8_t PIN_BUZZER = D5;
constexpr uint8_t PIN_BOTON = D6;
constexpr uint8_t PIN_LED_V = D7;
constexpr uint8_t PIN_LED_R = D8;
constexpr uint8_t PIN_OLED_SCL = D1, PIN_OLED_SDA = D2, PIN_OLED_DC = D3, PIN_OLED_RES = D0;

constexpr uint32_t PERIODO_DHT_MS = 2500;  // el DHT22 admite una lectura cada 2 s
constexpr uint8_t SEGUIDAS_PARA_FALLA = 3;  // igual que el firmware: 3 fallas seguidas = "--" en pantalla

DHT dht(PIN_DHT, DHT22);
// Si la imagen sale de cabeza, cambia U8G2_R0 por U8G2_R2 (igual que en el firmware del nodo).
U8G2_SSD1309_128X64_NONAME0_F_4W_SW_SPI pantalla(U8G2_R0, PIN_OLED_SCL, PIN_OLED_SDA, U8X8_PIN_NONE, PIN_OLED_DC, PIN_OLED_RES);

uint32_t lecturasOk = 0, lecturasFallidas = 0, peorRacha = 0, rachaFallas = 0;
uint32_t ultimaLectura = 0, ultimoOk = 0, inicio = 0;
float ultT = NAN, ultH = NAN;
uint32_t pulsaciones = 0;
bool botonAntes = HIGH;
bool cargaWifi = false;
bool buzzerFijo = false;
uint32_t fallasConBuzzer = 0, lecturasConBuzzer = 0;
uint32_t fallasConWifi = 0, lecturasConWifi = 0;
uint32_t cambioBoton = 0;

// ── utilidades ──────────────────────────────────────────────────────────────
void pitido(uint16_t ms) {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(ms);
  digitalWrite(PIN_BUZZER, LOW);
}

void titulo(const char* t) {
  Serial.println();
  Serial.println(F("------------------------------------------------------------"));
  Serial.println(t);
  Serial.println(F("------------------------------------------------------------"));
}

void mensajePantalla(const char* l1, const char* l2 = "", const char* l3 = "") {
  pantalla.clearBuffer();
  pantalla.setFont(u8g2_font_6x10_tf);
  pantalla.drawStr(0, 12, l1);
  pantalla.drawStr(0, 30, l2);
  pantalla.drawStr(0, 48, l3);
  pantalla.sendBuffer();
}

// ── pruebas ─────────────────────────────────────────────────────────────────
void probarLeds() {
  titulo("PRUEBA 1 · LEDs");
  mensajePantalla("PRUEBA: LEDs", "verde 2 s, rojo 2 s");
  Serial.println(F("Se enciende el LED VERDE 2 s..."));
  digitalWrite(PIN_LED_V, HIGH); delay(2000); digitalWrite(PIN_LED_V, LOW);
  Serial.println(F("Se enciende el LED ROJO 2 s..."));
  digitalWrite(PIN_LED_R, HIGH); delay(2000); digitalWrite(PIN_LED_R, LOW);
  Serial.println(F("-> Si alguno no encendio: revisa su resistencia de 330 ohm y la polaridad"));
  Serial.println(F("   (pata larga al lado de la resistencia, pata corta a GND). Si enciende muy tenue,"));
  Serial.println(F("   revisa que la resistencia sea de 330 ohm (naranja, naranja, cafe)."));
}

void probarBuzzer() {
  titulo("PRUEBA 2 · BUZZER");
  mensajePantalla("PRUEBA: buzzer", "3 pitidos");
  Serial.println(F("Deben sonar 3 pitidos cortos..."));
  for (int i = 0; i < 3; i++) { pitido(150); delay(250); }
  Serial.println(F("-> Si no sono: revisa el 2N2222 (emisor a GND, colector al - del buzzer),"));
  Serial.println(F("   la resistencia de 1 k entre D5 y la base, y que el + del buzzer vaya a 5 V."));
}

void probarPantalla() {
  titulo("PRUEBA 3 · PANTALLA");
  Serial.println(F("La pantalla se pone toda blanca 1.5 s, luego un marco con texto y un cuadro."));
  pantalla.clearBuffer();
  pantalla.drawBox(0, 0, 128, 64);
  pantalla.sendBuffer();
  delay(1500);
  pantalla.clearBuffer();
  pantalla.drawFrame(0, 0, 128, 64);
  pantalla.setFont(u8g2_font_6x10_tf);
  pantalla.drawStr(6, 16, "PRUEBA PANTALLA");
  pantalla.drawStr(6, 30, "0123456789 -+.%");
  pantalla.drawBox(6, 40, 30, 16);
  pantalla.drawStr(44, 54, "OK si se ve");
  pantalla.sendBuffer();
  delay(2500);
  Serial.println(F("-> Si se vio completa y sin rayas: la pantalla esta bien."));
  Serial.println(F("   Si no prende: revisa VCC (3V3), GND, CS a GND y RES en D0."));
  Serial.println(F("   Si sale basura o se corta: revisa SCL (D1), SDA (D2) y DC (D3)."));
  Serial.println(F("   Si sale de cabeza: cambia U8G2_R0 por U8G2_R2 en el programa."));
}

void probarBoton() {
  titulo("PRUEBA 4 · BOTON");
  mensajePantalla("PRUEBA: boton", "aprietalo en 10 s");
  Serial.println(F("Aprieta el boton en los proximos 10 s..."));
  uint32_t t0 = millis();
  bool visto = false;
  while (millis() - t0 < 10000) {
    if (digitalRead(PIN_BOTON) == LOW) { visto = true; break; }
    delay(10);
    yield();
  }
  if (visto) {
    Serial.println(F("-> BIEN: el boton se detecto."));
    pitido(80);
  } else {
    Serial.println(F("-> NO se detecto. Revisa que el boton vaya de D6 a GND (patas en lados opuestos)."));
  }
  while (digitalRead(PIN_BOTON) == LOW) { delay(10); yield(); }  // espera a que lo suelte
}

void nivelesPines() {
  titulo("NIVELES DE LOS PINES (sin tocar nada)");
  pinMode(PIN_DHT, INPUT);
  delay(5);
  int dhtNivel = digitalRead(PIN_DHT);
  Serial.printf("D4 (datos del DHT22) en reposo: %s\n", dhtNivel ? "ALTO (bien: el pull-up funciona)" :
                "BAJO (mal: cable suelto a +3V3, sin resistencia pull-up o sensor sin alimentacion)");
  Serial.printf("D6 (boton) en reposo: %s\n", digitalRead(PIN_BOTON) ? "ALTO (bien, suelto)" :
                "BAJO (apretado o en corto a GND)");
  dht.begin();  // devuelve el pin al estado que usa la libreria
}

void ayuda() {
  titulo("COMANDOS");
  Serial.println(F("h ayuda | l LEDs | b buzzer | o pantalla | t boton | p niveles de pines | r reiniciar contadores"));
  Serial.println(F("w carga de WiFi: compara las fallas del DHT22 con el radio prendido y apagado"));
  Serial.println(F("z buzzer FIJO: suena sin parar mientras lee el DHT22; z otra vez lo apaga y dice cuantas fallaron"));
  Serial.println(F("PRUEBA DE MENEO: con el nodo vigilando, mueve suavemente UN cable a la vez (DHT22: +, out, -)"));
  Serial.println(F("y mira si sube FALLAS. Si sube al mover un cable, ese es el falso contacto."));
}

// ── vigilancia continua del DHT22 ───────────────────────────────────────────
void leerDht() {
  bool ok = dht.read(true);  // fuerza una lectura nueva
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  bool valida = ok && !isnan(t) && !isnan(h) && t >= -10 && t <= 60 && h >= 0 && h <= 100;
  if (cargaWifi) { lecturasConWifi++; if (!valida) fallasConWifi++; }
  if (buzzerFijo) { lecturasConBuzzer++; if (!valida) fallasConBuzzer++; }
  if (valida) {
    lecturasOk++;
    rachaFallas = 0;
    ultimoOk = millis();
    ultT = t; ultH = h;
    digitalWrite(PIN_LED_V, HIGH); delay(60); digitalWrite(PIN_LED_V, LOW);  // destello verde = lectura buena
  } else {
    lecturasFallidas++;
    rachaFallas++;
    if (rachaFallas > peorRacha) peorRacha = rachaFallas;
  }
  uint32_t total = lecturasOk + lecturasFallidas;
  float pct = total ? 100.0f * lecturasOk / total : 0;
  if (valida) {
    Serial.printf("[dht] OK     T=%.1f C  H=%.1f %%   buenas=%lu fallas=%lu (%.0f%% bien)\n",
                  t, h, (unsigned long)lecturasOk, (unsigned long)lecturasFallidas, pct);
  } else {
    Serial.printf("[dht] FALLA  (%s)  seguidas=%lu  buenas=%lu fallas=%lu (%.0f%% bien)%s\n",
                  ok ? "valor fuera de rango" : "el sensor no respondio",
                  (unsigned long)rachaFallas, (unsigned long)lecturasOk, (unsigned long)lecturasFallidas, pct,
                  rachaFallas >= SEGUIDAS_PARA_FALLA ? "  <- aqui el nodo mostraria \"--\"" : "");
  }
}

void dibujarEstado() {
  char l[32];
  pantalla.clearBuffer();
  pantalla.setFont(u8g2_font_6x10_tf);
  pantalla.drawStr(0, 9, "PRUEBA NODO DHT");
  if (rachaFallas >= SEGUIDAS_PARA_FALLA || isnan(ultT)) {
    pantalla.drawStr(0, 22, "T: --.- C   H: -- %");
  } else {
    snprintf(l, sizeof l, "T: %.1f C   H: %.0f %%", ultT, ultH);
    pantalla.drawStr(0, 22, l);
  }
  snprintf(l, sizeof l, "buenas:%lu fallas:%lu", (unsigned long)lecturasOk, (unsigned long)lecturasFallidas);
  pantalla.drawStr(0, 34, l);
  snprintf(l, sizeof l, "seguidas:%lu peor:%lu", (unsigned long)rachaFallas, (unsigned long)peorRacha);
  pantalla.drawStr(0, 46, l);
  snprintf(l, sizeof l, "boton:%s n=%lu", digitalRead(PIN_BOTON) == LOW ? "APRETADO" : "suelto", (unsigned long)pulsaciones);
  pantalla.drawStr(0, 58, l);
  pantalla.drawFrame(122, 0, 6, 6);  // cuadrito que parpadea: si se congela, la pantalla dejo de recibir datos
  if ((millis() / 500) % 2) pantalla.drawBox(122, 0, 6, 6);
  pantalla.sendBuffer();
}

void atenderBoton() {
  bool ahora = digitalRead(PIN_BOTON);
  if (ahora != botonAntes && millis() - cambioBoton > 40) {
    cambioBoton = millis();
    botonAntes = ahora;
    if (ahora == LOW) {
      pulsaciones++;
      Serial.printf("[boton] apretado (vez %lu)\n", (unsigned long)pulsaciones);
      pitido(40);
    }
  }
}

void atenderComandos() {
  while (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 'h': ayuda(); break;
      case 'l': probarLeds(); break;
      case 'b': probarBuzzer(); break;
      case 'z':
        buzzerFijo = !buzzerFijo;
        digitalWrite(PIN_BUZZER, buzzerFijo ? HIGH : LOW);
        if (buzzerFijo) {
          lecturasConBuzzer = fallasConBuzzer = 0;
          Serial.println(F("[buzzer] FIJO: sonando sin parar. Mira si salen FALLAS o si el nodo se reinicia. z para apagar."));
        } else {
          Serial.printf("[buzzer] apagado. Con el buzzer sonando: %lu lecturas, %lu fallas\n",
                        (unsigned long)lecturasConBuzzer, (unsigned long)fallasConBuzzer);
        }
        break;
      case 'o': probarPantalla(); break;
      case 't': probarBoton(); break;
      case 'p': nivelesPines(); break;
      case 'w':
        cargaWifi = !cargaWifi;
        if (cargaWifi) {
          WiFi.mode(WIFI_STA);
          WiFi.scanNetworks(true);
          Serial.println(F("[wifi] carga de radio PRENDIDA: escanea redes sin parar"));
        } else {
          WiFi.scanDelete();
          WiFi.mode(WIFI_OFF);
          Serial.printf("[wifi] carga APAGADA. Con el radio prendido: %lu lecturas, %lu fallas\n",
                        (unsigned long)lecturasConWifi, (unsigned long)fallasConWifi);
        }
        break;
      case 'r':
        lecturasOk = lecturasFallidas = peorRacha = rachaFallas = pulsaciones = 0;
        Serial.println(F("[ok] contadores en cero"));
        break;
      default: break;
    }
  }
}

void setup() {
  pinMode(PIN_LED_V, OUTPUT); digitalWrite(PIN_LED_V, LOW);
  pinMode(PIN_LED_R, OUTPUT); digitalWrite(PIN_LED_R, LOW);
  pinMode(PIN_BUZZER, OUTPUT); digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_BOTON, INPUT_PULLUP);
  WiFi.persistent(false);
  WiFi.mode(WIFI_OFF);  // sin radio, salvo con el comando w
  Serial.begin(115200);
  delay(300);
  pantalla.begin();
  dht.begin();
  inicio = millis();

  titulo("ARGOS · PRUEBA COMPLETA DEL NODO dht");
  Serial.printf("Motivo del ultimo reinicio: %s\n", ESP.getResetReason().c_str());
  Serial.println(F("Mira el nodo: cada prueba dice que deberias ver u oir."));
  nivelesPines();
  probarLeds();
  probarBuzzer();
  probarPantalla();
  probarBoton();
  titulo("PRUEBA 5 · DHT22 (continua)");
  Serial.println(F("Lee el DHT22 cada 2.5 s. Destello verde = lectura buena; rojo fijo = 3 fallas seguidas."));
  ayuda();
}

void loop() {
  atenderComandos();
  if (cargaWifi && WiFi.scanComplete() >= 0) { WiFi.scanDelete(); WiFi.scanNetworks(true); }  // otra vuelta
  atenderBoton();
  if (millis() - ultimaLectura >= PERIODO_DHT_MS) {
    ultimaLectura = millis();
    leerDht();
  }
  digitalWrite(PIN_LED_R, rachaFallas >= SEGUIDAS_PARA_FALLA ? HIGH : LOW);
  static uint32_t ultimoDibujo = 0;
  if (millis() - ultimoDibujo >= 250) {
    ultimoDibujo = millis();
    dibujarEstado();
  }
  static uint32_t ultimoResumen = 0;
  if (millis() - ultimoResumen >= 60000) {
    ultimoResumen = millis();
    uint32_t total = lecturasOk + lecturasFallidas;
    Serial.printf("[resumen] %lu min: %lu lecturas, %lu fallas, peor racha %lu seguidas\n",
                  (unsigned long)((millis() - inicio) / 60000), (unsigned long)total,
                  (unsigned long)lecturasFallidas, (unsigned long)peorRacha);
  }
}
