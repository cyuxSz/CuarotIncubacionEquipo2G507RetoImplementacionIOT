// Argos · DEMOSTRACIÓN PARA EL VIDEO del nodo dht (valores SIMULADOS; no lee el DHT22 ni usa WiFi).
// Placa: NodeMCU 1.0 (ESP-12E Module). Monitor serie: 115200. Librería: U8g2.
// Usa la misma pantalla del programa real (vista_oled.h), el buzzer, el botón y los dos LED.
//
// Qué hace solo, en un ciclo de unos 90 s:
//   1. Normal: 25.0 °C, 50 % HR, LED verde, barra "EN LINEA".                      (8 s)
//   2. La temperatura SUBE hasta 29.5 °C. Al pasar de 28 °C tres lecturas seguidas:
//      suena el buzzer, LED rojo fijo, barra "ALARMA" y etiqueta ALTA.
//   3. La temperatura regresa a 25 °C y la alarma se apaga sola.
//   4. La temperatura BAJA hasta 20.5 °C: alarma con etiqueta BAJA.
//   5. Regresa a 25 °C y vuelve a empezar.
// Botón: con la alarma sonando, una pulsación la silencia ("ALARMA SILENCIADA"); el LED rojo sigue.
//
// Comandos por el monitor serie (letra y Enter), por si quieres dirigir la toma:
//   s subir ahora · b bajar ahora · n volver a normal y quedarse ahí · a ciclo automático
//   + más rápido · - más lento

#include <U8g2lib.h>
#include "vista_oled.h"

constexpr uint8_t PIN_BUZZER = D5, PIN_BOTON = D6, PIN_LED_V = D7, PIN_LED_R = D8;
constexpr uint8_t PIN_OLED_SCL = D1, PIN_OLED_SDA = D2, PIN_OLED_DC = D3, PIN_OLED_RES = D0;
U8G2_SSD1309_128X64_NONAME0_F_4W_SW_SPI pantalla(U8G2_R0, PIN_OLED_SCL, PIN_OLED_SDA, U8X8_PIN_NONE, PIN_OLED_DC, PIN_OLED_RES);

constexpr float T_MIN = 22.0f, T_MAX = 28.0f, T_HIST = 0.5f;   // mismos rangos que el nodo real
constexpr float T_NORMAL = 25.0f, T_ALTA = 29.5f, T_BAJA = 20.5f;

enum Fase { NORMAL1, SUBE, ARRIBA, REGRESA1, NORMAL2, BAJA, ABAJO, REGRESA2 };
Fase fase = NORMAL1;
bool automatico = true;
float temperatura = T_NORMAL, humedad = 50.0f, objetivo = T_NORMAL;
float paso = 0.3f;            // °C por lectura (una lectura por segundo)
uint32_t ultimaLectura = 0, inicioFase = 0;
uint8_t fuera = 0;            // lecturas seguidas fuera de rango
bool alarma = false, silenciada = false;

void entrar(Fase f) {
  fase = f;
  inicioFase = millis();
  switch (f) {
    case SUBE: case ARRIBA: objetivo = T_ALTA; break;
    case BAJA: case ABAJO: objetivo = T_BAJA; break;
    default: objetivo = T_NORMAL; break;
  }
}

bool paso_de(uint32_t ms) { return millis() - inicioFase >= ms; }
bool llego() { return fabsf(temperatura - objetivo) < 0.05f; }

void avanzarCiclo() {
  if (!automatico) return;
  switch (fase) {
    case NORMAL1: if (paso_de(8000)) entrar(SUBE); break;
    case SUBE: if (llego()) entrar(ARRIBA); break;
    case ARRIBA: if (paso_de(12000)) entrar(REGRESA1); break;
    case REGRESA1: if (llego()) entrar(NORMAL2); break;
    case NORMAL2: if (paso_de(6000)) entrar(BAJA); break;
    case BAJA: if (llego()) entrar(ABAJO); break;
    case ABAJO: if (paso_de(12000)) entrar(REGRESA2); break;
    case REGRESA2: if (llego()) entrar(NORMAL1); break;
  }
}

const char* etiquetaT() {
  if (temperatura > T_MAX) return "ALTA";
  if (temperatura < T_MIN) return "BAJA";
  return "";
}

void lectura() {
  // la temperatura se acerca al objetivo un paso por lectura
  if (temperatura < objetivo) temperatura = min(objetivo, temperatura + paso);
  else if (temperatura > objetivo) temperatura = max(objetivo, temperatura - paso);
  humedad = 50.0f - (temperatura - T_NORMAL) * 1.5f;   // baja un poco cuando sube la temperatura

  bool fueraDeRango = temperatura > T_MAX || temperatura < T_MIN;
  bool dentroConMargen = temperatura <= T_MAX - T_HIST && temperatura >= T_MIN + T_HIST;
  if (fueraDeRango) { if (fuera < 255) fuera++; } else fuera = 0;
  if (!alarma && fuera >= 3) {            // persistencia de 3 lecturas, como el nodo real
    alarma = true;
    Serial.println(F("[demo] ALARMA: temperatura fuera de rango 3 lecturas seguidas"));
  }
  if (alarma && dentroConMargen) {        // histeresis de 0.5 °C
    alarma = false;
    silenciada = false;
    Serial.println(F("[demo] alarma terminada: la temperatura regreso al rango"));
  }
  Serial.printf("[demo] T = %.1f C  HR = %.0f %%  %s%s\n", temperatura, humedad,
                alarma ? "ALARMA" : "normal", silenciada ? " (silenciada)" : "");
}

void atenderBoton() {
  static bool estable = HIGH, anterior = HIGH;
  static uint32_t cambio = 0;
  bool l = digitalRead(PIN_BOTON);
  if (l != anterior) { cambio = millis(); anterior = l; }
  if (millis() - cambio < 40 || l == estable) return;
  estable = l;
  if (estable == LOW && alarma && !silenciada) {
    silenciada = true;
    Serial.println(F("[demo] boton: buzzer silenciado"));
  }
}

void atenderSerie() {
  while (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 's': automatico = false; entrar(SUBE); Serial.println(F("[demo] subiendo")); break;
      case 'b': automatico = false; entrar(BAJA); Serial.println(F("[demo] bajando")); break;
      case 'n': automatico = false; entrar(NORMAL1); Serial.println(F("[demo] a normal")); break;
      case 'a': automatico = true; entrar(NORMAL1); Serial.println(F("[demo] ciclo automatico")); break;
      case '+': paso = min(1.0f, paso + 0.1f); Serial.printf("[demo] paso %.1f C por lectura\n", paso); break;
      case '-': paso = max(0.1f, paso - 0.1f); Serial.printf("[demo] paso %.1f C por lectura\n", paso); break;
      default: break;
    }
  }
}

void dibujar() {
  VistaOled v = {temperatura, humedad, true, false, true, alarma, silenciada, etiquetaT(), ""};
  vista_oled_dibujar(pantalla.getU8g2(), &v);
  pantalla.sendBuffer();
}

void setup() {
  pinMode(PIN_BUZZER, OUTPUT); digitalWrite(PIN_BUZZER, LOW);
  pinMode(PIN_LED_V, OUTPUT); pinMode(PIN_LED_R, OUTPUT);
  pinMode(PIN_BOTON, INPUT_PULLUP);
  Serial.begin(115200);
  delay(200);
  pantalla.begin();
  Serial.println(F("\n=== Argos: demostracion del nodo dht para el video (valores simulados) ==="));
  Serial.println(F("Comandos: s subir | b bajar | n normal | a ciclo automatico | + mas rapido | - mas lento"));
  digitalWrite(PIN_BUZZER, HIGH); delay(80); digitalWrite(PIN_BUZZER, LOW);   // pitido de arranque
  entrar(NORMAL1);
  dibujar();
}

void loop() {
  atenderSerie();
  atenderBoton();
  if (millis() - ultimaLectura >= 1000) {
    ultimaLectura = millis();
    avanzarCiclo();
    lectura();
    dibujar();
  }
  digitalWrite(PIN_BUZZER, (alarma && !silenciada) ? HIGH : LOW);
  digitalWrite(PIN_LED_R, alarma ? HIGH : LOW);
  digitalWrite(PIN_LED_V, HIGH);   // verde fijo: "en linea"
}
