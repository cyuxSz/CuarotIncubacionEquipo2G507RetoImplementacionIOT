# Decisiones Argos (19-oct-2026)

Contexto del proyecto: `CLAUDE.md`. Presupuesto: `docs/presupuesto.md`. Armado: `docs/guia_ensamble.md`. Preguntas abiertas: `docs/preguntas.md`.

- **5 microcontroladores, uno por integrante**, en **3 cajas**: `dht` solo; estación de entrada (`pir` + `puerta`); estación del anaquel (`acel` + `luz`). Cada estación: 2 NodeMCU independientes en una MB-102 de 830 puntos, una fuente de 5 V y un módulo USB-C a VIN. El 3V3 de cada placa nunca se une.
- **OLED 2.42" SSD1309 I²C de 4 pines** en `dht`. Pantalla: estado, temperatura y humedad a la vez.
- **LED rojo reacciona al sensor** en todos los nodos (Etapa 2 del reto).
- **Estaciones en horizontal** (174 × 80 mm, 202 con orejas) para no ocupar altura útil; `dht` queda vertical (80 × 138). Entrada: 2 tacos de pared impresos. Anaquel: orejas rígidas M3.
- **LED rotulados por sensor** en cada estación (PIR/PUERTA, ACEL/LUZ).
- **Pantalla:** barra de estado (EN LINEA / SIN RED / ALARMA / FALLA) + temperatura (≈ 11 mm) + humedad (≈ 7 mm), una sola vista; layout en `firmware/include/vista_oled.h` y preview real en `docs/oled_estados.png`.
- PETG impreso (≈ 1 kg), LED con 330 Ω, protoboard de 400 puntos solo en `dht`.
- Fuentes de 5 V **se compran**; termohigrómetro **prestado**.
- No usar Wokwi ni Tinkercad para validar (no soportan ESP8266/OLED I²C).
- Todas las medidas son **nominales** hasta medir las piezas reales.

Prototipo para los encargados: https://claude.ai/artifact/8s1uQZNsibdkANYaeyZ9Ny (privado hasta compartirlo).
- (20-oct) Capuchón LDR: cuerpo negro opaco + disco difusor aparte (0.6/0.9/1.2 mm) y horquilla orientable; R2 y umbral se eligen con la prueba de multímetro.
- (20-oct) MC-38: reed en el marco, imán en la hoja; portas con topes de retención, ranuras ±3 mm y calzas; gap real POR CONFIRMAR.
- (20-oct) No se usan 3D CAD Converter ni 3DOptix.
- (20-oct) PlatformIO sigue como principal; Arduino IDE 2.x con sketches generados; ArduinoJson fijo en 6.21.5; ESP32 no aplica.
- (21-oct) Actuador por integrante = **LED rojo** de su nodo; buzzer = actuador extra del `dht`; LED verde = indicador de estado (no actuador). Una **fuente de 5 V por caja** (3 en total).
- (21-oct) BD v2: entidad **Caja** (3FN: la ubicacion es de la caja), `Actuador.tipo` buzzer/led_rojo, `AccionControl.origen` alerta/local/manual; el estado del LED lo deduce n8n del evento (no se cambia el contrato MQTT).
- (21-oct) Simulacion: pruebas en PC + simulador MQTT en Python; Gazebo/MATLAB no aplican (sin robot ni lazo de control), Wokwi no soporta ESP8266.
