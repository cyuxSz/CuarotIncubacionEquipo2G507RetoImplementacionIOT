# Estado Argos

Actualizado: 19-nov-2026. Ver [[Decisiones]]. Lo de abajo del 21-oct es historial.

## 19-nov-2026 (copia de trabajo `C:\argos`, PC de Iván; sin git, nada commiteado)
- **Firmware** (compila en los 7 sketches con arduino-cli, core esp8266 3.1.2; NO flasheado ni probado en placa): pausa de 30 s si la API no responde y reintento MQTT creciente (el loop ya no se congela); autoprueba de LED y pitido al arrancar; `pir` ignora el primer minuto; `puerta` reenvía el estado pendiente al volver la red; `acel` mide su reposo al arrancar, reintenta el ADS1115 y avisa `sensor_error`; `luz` imprime cada muestra; `dht` solo consulta `/api/comandos` si no hay MQTT. Sin cambios de pines ni del contrato MQTT. `prueba_alarma.py` no se corrió (no hay g++ en esta PC; `alarma_dht.h` no cambió).
- **Servidor**: nuevo `servidor/central/` (panel web, alertas que cruzan nodos, `cmd/alarma`, avisos graves con la tabla `Notificacion`), `servidor/web/index.html` (panel sin dependencias de internet), `servidor/n8n/avisos_graves.json`, `servidor/arrancar.ps1`, `servidor/LEEME.md`. Prueba `servidor/pruebas/prueba_integracion.js`: 48 de 48 con un MySQL de prueba, las 5 API y un broker aedes. Sin probar: Mosquitto con ACL, n8n real, nodos reales. `docker-compose.yml` y `servidor/api/` quedaron como versión anterior.
- **CAD**: trazos de iconos y ojo a ≥ 1.0 mm, rótulos en negrita, alivios en la raíz de lengüetas, pestañas y collar del buzzer; `cad/cupon_prueba.py`. 0 interferencias, mismas envolventes. Sin imprimir.
- **Hardware**: en la caja `dht` entrada USB-C en col. 10, buzzer suelto (+ a +5V col. 28, − a G28), Q1 en TO-18. Recomendado y no agregado: diodo 1N4148 en paralelo con el buzzer.
- **Guías**: `presentacion/guia_armado.html` y `presentacion/montaje_3d.html`; Fritzing por pasos en `hardware/fritzing/salida/`.
- **Falta medir**: módulo USB-C, OLED 2.42", alto de la 830 con adhesivo, ancho de la placa del DHT22, paso del buzzer. **Falta confirmar**: que hay ADS1115 (Arianna usó un 74HC4052 en la Etapa 3), que el buzzer es activo, modelo de impresora.

### Noche del 19 al 20-nov: todo en UTP y cajas ajustadas (entrega el 22-nov a las 23:59)
- **Cable:** el equipo solo tiene cable UTP (el rojo y negro es de hilos y no entra a la protoboard sin estañar). `layouts.py` lleva `SOLO_UTP = True`: positivos en naranja y tierras en café, en las tres cajas. Regenerados Fritzing (pasos y por pieza), listas de cables y guía.
- **Armado del `dht`:** protoboard con NodeMCU, capacitor, 12 puentes, 5 resistencias (apareció la de 1 kΩ) y transistor ya puestos. Detectado y corregido un contacto flojo (18 y 66 Ω) por una pata inclinada. Faltan los cables soldados a las piezas.
- **Caja `dht` (CAD):** pantalla real de 72.16 × 42.69 mm en `y = 74`, marco con paredes laterales de 0.9 mm, **2 grapas verticales** (antes una horizontal, que ya no cabe), abertura de 60.4 × 31 mm **estimada de foto** (no se midió la zona que enciende), cuna del botón para 6.05 × 4.77 mm, rieles del DHT22 bajo su placa de 13 mm. Respaldo del CAD anterior: `cad/nodos.py.antes_oled_spi`.
- **Estaciones (CAD):** protoboard de 830 con 1 mm de adhesivo; GY-61 y ADS1115 con medida aproximada, por eso la tapa no lleva costilla para ellos.
- Sin medir y supuesto: zona que enciende de la OLED, agujeros de la OLED (no se usan), alto trasero del HC-SR501 (12 mm supuesto).

### OLED en SPI (19-nov, pedido por Iván tras ver las fotos de la pieza)
- **Cambio de pines del nodo `dht`:** la OLED real (ZJY_M242, 7 pines, en SPI de fábrica) va con SCL en D1, SDA en D2 (igual que antes), **DC en D3, RES en D0 y CS a GND**; VCC a 3V3 `[POR PROBAR: el módulo dice VCC=5V]`. Firmware: `U8G2_SSD1309_128X64_NONAME0_F_4W_SW_SPI` con `U8G2_R0` `[orientación POR CONFIRMAR]`. El contrato MQTT no cambia.
- Actualizado: `layouts.py`, esquemático, parte y diagramas de Fritzing del `dht` (4 pasos), lista de cables (32 tramos, 3.9 m), sketches y guía. `chequeo_pines.py` OK, redes OK, `argos_dht` y `argos_dht_sin_oled` compilan. **Sin actualizar:** KiCad, WireViz, `CLAUDE.md` §3 de pines, prompts de armado y la caja impresa (la pantalla mide 72.25 × 43 mm, tira de pines en un lado corto).

- Fritzing por pieza: `generar_fritzing.py --partes` genera, además de los 4 pasos, una imagen por pieza externa (`<caja>_parte<N>_<pieza>`); la guía las usa en el paso 4 (4.1, 4.2, …). La exportación va en lotes de 8 porque Fritzing se cierra con carpetas grandes.

### Auditoría del 19-nov (3 revisores: firmware, servidor, electrónica) y arreglos aplicados
- **Servidor** (54 de 54 en `prueba_integracion.js`): el motor ya no muere con un nodo apagado más de 11.6 días (valor topado y cada regla con su propio manejo de error); un solo cliente MQTT aunque el arranque se reintente; al reiniciar sigue desde `Configuracion.central_ultimo_evento`; no gasta `id_alerta` en cada revisión; aviso opcional de golpe y movimiento (`avisar_<tipo>` = 1); caché de 2 s en `/panel/datos`; último golpe y movimiento con consulta propia; `arrancar.ps1` relanza procesos y se niega si los puertos están ocupados; n8n no se detiene si falla un canal; `mosquitto/mosquitto.windows.conf` (sin probar).
- **Firmware** (compilan los 7 sketches y `dht` con `MODO_DEMO`; sin flashear): `puerta` solo da por entregado lo que guardó la API; LED verde fijo si responde la API o MQTT; `acel` sondea el ADS1115 antes de leer, I2C a 400 kHz, aviso de falla cada 5 s e imprime el pico de g para calibrar; `dht` y `luz` mandan latido; `luz` cambia el LED rojo en 10 s; `MODO_DEMO` en `dht` (rangos 15–30 °C y 20–80 % HR `[POR CONFIRMAR]`, lectura cada 5 s); segunda pulsación larga quita el silencio; timeout de la API 1 s y sin reintento en `/api/acciones`.
- **No aplicado** (es `servidor/api-rest`, código de la entrega del equipo): validar rango de `magnitud`, estado en memoria de `umbralModel.js`, `listen` sin revisar error.
- Confirmado por Iván el 19-nov: la caja `dht` lleva DHT22 (el firmware ya lo asume).
- **Pendiente de decidir o medir**: red de la Expo (router propio de 2.4 GHz); `UMBRAL_G` (esperado 0.15–0.3 g) y umbral de la LDR; relé de `luz_rele` a 3.3 V; lista «Medir antes de armar» de la guía. La alerta de luz fuera de horario sigue sin existir (falta el fotoperiodo).
- Confirmado por Iván el 19-nov: el nodo `acel` usa ADS1115.
- Fotos de las piezas del `dht` (19-nov): resistencias de 330 Ω (al menos 6) y 10 kΩ (2); capacitor 220 µF / 16 V; botón táctil 6×6 de 2 patas; LED verde transparente y rojo difuso de 5 mm (el rojo con patas recortadas: polaridad por el lado plano); módulo USB-C de 4 pads (VCC, D−, D+, GND) sin resistencias en CC; adaptador CGW-0530 de 5 V / 3 A con cable USB-C fijo (fuente simple, no PD: el riesgo de 0 V no aplica); buzzer de 12 mm con fondo sellado y «+» marcado arriba (parece activo, falta probarlo). Segunda tanda de fotos: 2N2222 de lata (TO-18, con pestaña); DHT22 ASAIR AM2302 en placa morada con pines + / out / − y pull-up propio; protoboard de 400 puntos (filas a–j, columnas 1–30, 2 rieles por lado); NodeMCU angosto tipo Amica. **La OLED es un módulo ZJY_M242 de 7 pines configurado en SPI** (CS, DC, RES, SDA, SCL, VCC=5V, GND), no I²C de 4 pines: el cableado y el firmware del `dht` se deben adaptar (decisión pendiente: SPI por software sin tocar el módulo, o mover R4→R3 y puentear R5 para I²C). Su tira de pines va en un lado corto. **Siguen sin aparecer:** resistencia de 1 kΩ y el cable. Medidas nuevas en `cad/medidas.json`; la OLED mide 72.25 × 43 mm y la caja `dht` no se ha ajustado.

## Hecho (en el modelo, sin probar en hardware)
- Circuitos y distribución en protoboard verificados automáticamente, WireViz, esquemáticos y prompts de armado.
- Firmware de referencia de los 5 nodos (solo compila; no se ha flasheado).
- Carcasas en 3 cajas, sin interferencias y sin soportes de impresión; piezas de prueba de ajuste.
- Página del prototipo para los encargados.
- (20-oct) Capuchón LDR v2 (negro + difusor aparte + horquilla) y portas MC-38 v2 (retención, ranuras, calzas); 3MF; `docs/impresion_3d.md`, `docs/prueba_ldr.md`, `docs/arduino_ide.md`; sketches de Arduino IDE generados y compilados.

- (21-oct) `python regenerar.py`: regenera todo y corre chequeos (redes de protoboard, pines firmware = layouts, 21 pruebas en PC de las reglas del buzzer). `dht` usa `nodo_comun.h` + `alarma_dht.h`; los 6 entornos compilan. CAD con medidas de `medidas.json` y rejilla de `layouts.py`: geometria identica a la del 20-oct. BD v2 en `docs/bd/` (Caja, LED rojo como actuador). Simulador MQTT en `simulador/` (sin probar contra un broker). Preguntas en `docs/preguntas.md`.
- (21-oct) Limpieza tras el primer commit: se borraron `Contexto.md`, `docs/reconciliacion_design.md`, `docs/referencia_design/`, `docs/evaluacion_herramientas.md` y `cad/exports/archivo/` (recuperables con git). `Presupuesto.md` y `Guía de ensamble.md` de la raíz solo enlazan a `docs/`, que manda.
- (21-oct) Entregable Avance 2 de hardware (docx/pdf en el escritorio, generador `docs/entregables/entregable4.py`). Simulador probado contra broker local amqtt: telemetria, eventos, cmd/alarma y LWT OK. Hallazgo: el simulador imprime "conectado" aunque el broker rechace credenciales.

## Pendiente
- Enviar `docs/preguntas.md` a profesores y encargados.
- Etapa 3 (semana actual): levantar Mosquitto + MySQL (`docs/bd/esquema.sql`) + n8n en la laptop y probar con el simulador.
- Medir con calibrador NodeMCU, OLED, DHT22, KY-012, GY-61, ADS1115, MC-38, HC-SR501, botón, LED, LDR y espesor del anaquel.
- Imprimir el peine de holguras y las piezas de prueba.
- Prueba de la LDR con la lámpara (elegir difusor, R2 y umbral) y prueba del MC-38 (distancia real de cierre).
- Color del PETG comprado: si no es negro, pintar o forrar el capuchón de la LDR.
- Confirmar con los encargados: pantalla, alarma, fijación, ubicación, luces.
- Calibrar el DHT22 contra el termohigrómetro prestado.
- Verificar que los rieles de 3V3 de la MB-102 estén partidos.
- Precios de la OLED 2.42" y de las fuentes de 2 A.
