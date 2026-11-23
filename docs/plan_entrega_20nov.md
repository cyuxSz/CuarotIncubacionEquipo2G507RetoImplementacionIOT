# Plan de entrega: martes 17 → viernes 20 de nov (23:59)

Hecho el martes 17 a las 16:30. Entrega en la plataforma de ExpoIngenierías: **video MP4 de 3–5 min, reporte técnico y 3 imágenes del perfil (la primera de preferencia GIF)**. Meta interna: **subir el viernes a las 21:00**, con 3 h de margen.

Datos que faltan y cambian el plan: hora de llegada del hardware y del filamento PETG el miércoles `[POR CONFIRMAR]`; modelo de la impresora (Creality, por el CrealityPrint) `[POR CONFIRMAR]`; si hay una segunda impresora (de alguien del equipo o del makerspace del Tec) `[POR CONFIRMAR]`; si los insertos y tornillos M3 se compraron `[POR CONFIRMAR]`. Acceso al cuarto: L–V de 8:00 a 17:00.



## Decisiones para no perder tiempo (tomarlas hoy)

1. **No se modela nada nuevo.** Persianas, ojo e iconos quedan como trabajo futuro. El contraste del texto y un ojo pequeño se resuelven con marcador permanente después de imprimir.
2. **Base: variante modular (clips).** Tapa: a presión si el broche 2 del cupón cierra; si no, tornillos M3 (versión de respaldo, solo si hay insertos).
3. **Ajustes de impresión rápidos para el prototipo** (ver abajo). Las cajas de la Expo no necesitan 5 perímetros.
4. **La impresora no para.** Siempre hay algo en la cola; las piezas largas van de noche.

## Cómo imprimir (resumen)

El filamento llega el miércoles junto con el hardware: **hoy no se imprime nada**.

### Hoy martes: dejar todo listo para imprimir

1. Instalar CrealityPrint (el instalador está en `Downloads/CrealityPrint`) y elegir el perfil de la impresora.
2. Crear un perfil de PETG con los ajustes de abajo.
3. **Laminar desde ahora todas las piezas** con las medidas nominales y guardar los proyectos con su tiempo y sus gramos. Mañana solo se vuelven a laminar las que cambien con las medidas reales. Así se confirma si la cola cabe en el tiempo.
4. Comprobar que las bases de las estaciones (202 mm) caben en la cama sin falda ni borde.

### Miércoles: al llegar el filamento y el hardware (H = hora de llegada)

| Desde H | Impresora | Personas |
|---|---|---|
| 0:00 | **Cupón de clips (base + tira).** Ya está laminado | Inventario; medir la prioridad 1 de la hoja `Mediciones para impresion 3D (17 nov).xlsx`: protoboards de 400 y 830, NodeMCU clavado (alto, separación, vuelo del USB), LED y C1. Una sola persona con el calibrador |
| Al terminar el cupón (≈ 1–2 h, confirmar con el laminador) | Base del `dht` | Probar los clips con la protoboard de 400 real y los broches de la tira a mano: clic, no se suelta, 20 aperturas. Luis pasa las medidas a `cad/medidas.json` y el cupón ganador a `DIS`, regenera, revisa 0 interferencias y vuelve a laminar |
| Después | Tapa del `dht` + grapa → bases y tapas de las estaciones | Medir la prioridad 2 (OLED, PIR, MC-38) y regenerar las tapas antes de que les toque |

```bash
uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/nodos.py --modular dht entrada anaquel
```

- Si la regeneración no está lista cuando termine el cupón, no se deja la impresora parada: va el peine de holguras o un accesorio corto.
- Si cambiar las medidas lleva mucho tiempo y la protoboard real coincide con la nominal (±0.3 mm), se imprime la base del `dht` tal como está.

**Cola de impresión** (una impresora): cupón → base `dht` → tapa `dht` + grapa de la OLED → base entrada → tapa entrada → base anaquel → tapa anaquel. Las bases, que son lo más largo, van de noche. Los **accesorios** (soportes de pared, tacos, calzas, émbolo, portas del MC-38, capuchón y difusores de la LDR, ≈ 75 g) llenan los huecos cortos o van al final: el video se puede grabar sin ellos. Si aparece una segunda impresora, se le pasan las estaciones y los accesorios.

### Ajustes de impresión

| Ajuste | Bases | Tapas | Por qué |
|---|---|---|---|
| Capa | 0.24 mm | 0.20 mm | El texto y la ventana de la OLED están en la tapa |
| Perímetros | 4 | 4 | Los brazos de 1.4–1.6 mm salen sólidos igual |
| Relleno | 15 % giroide | 15 % giroide | El 25 % no hace falta para el prototipo |
| Soportes | Ninguno | Ninguno | Ya verificado en el modelo |
| PETG | 235–245 °C / cama 75–85 °C, ventilador 30–50 % | | Partir de la ficha del filamento comprado |

- Antes de lanzar la base del `dht`, laminarla con estos ajustes y con los de `docs/impresion_3d.md` (5 perímetros, 25 %) y anotar las dos horas. Con eso se confirma o se corrige la cola.
- Las bases de las estaciones miden 202 mm con orejas: en una cama de 220 mm, quitar falda y borde (brim) y revisar que la línea de purga no las toque.
- Revisar la primera capa de cada pieza grande (unos 10 min) antes de dejarla sola.
- Si el PETG hace hilos o burbujas, secarlo (≈ 65 °C, 4 h) antes de las bases.
- Para marcar: anotar en una tabla la hora de inicio, la de fin y si salió bien. Va al reporte (`[POR COMPLETAR: impresora y horas]`).

## Calendario

Bloques de unas 6 h con 30 min de descanso. Las noches tienen un sueño corto **mientras la impresora trabaja**: así no se pierde avance y se arma con menos errores.

### Martes 17

| Hora | Luis | Equipo |
|---|---|---|
| 16:30–17:00 | Decisiones de arriba; confirmar impresora, insertos y hora de llegada del hardware y el filamento | — |
| 17:00–19:00 | Instalar CrealityPrint, crear el perfil de PETG y laminar todas las piezas (tiempos y gramos) | — |
| 19:00–22:30 | Reporte técnico: llenar todo lo que no depende del hardware (método, diseño, figuras de renders) | Frente 4: Mosquitto en el server y prueba de la ACL (guía del broker). Frente 5: tomas que no dependen del hardware (giro del modelo 3D, diagramas, KiCad, DBeaver con los datos del 13-nov). Frente 1: imprimir y repasar el paquete de banco |
| 22:30–23:00 | **Descanso** | **Descanso** |
| 23:00–02:00 | Guion del video: cerrar textos y quién narra cada bloque | Narración de los bloques 1–5 (no dependen del hardware) |
| 02:00–07:00 | **Dormir** | **Dormir** |

### Miércoles 18 (llega el hardware)

| Hora | Luis | Equipo |
|---|---|---|
| 07:00–08:00 | Limpiar la cama de la impresora y tener abiertos los proyectos laminados | — |
| 08:00–llegada | Fotos del cuarto, frascos y minisplit (acceso de 8:00 a 17:00) | Frente 4: dashboard con el simulador; API en el server |
| Llegada + 0:00–2:00 | **Lanzar el cupón de inmediato**; medir, probar el cupón, regenerar y **lanzar la base `dht`** | Inventario; revisar los rieles de las MB-102 (3V3 partido) |
| +1:15 a +6:00 | Cambiar de pieza al terminar cada una; regenerar tapas con la prioridad 2 | Cada quien arma su nodo en protoboard, un cable a la vez; P-01 sin energía, P-02 y P-05 con energía. **Grabar mientras se arma** |
| **Descanso de 30 min** | | |
| Siguientes 6 h | Cola de impresión; flashear y probar el `dht` (monitor serie, POST 201, MySQL) | Flashear un nodo a la vez; prueba del MC-38 y del PIR; MQTT de punta a punta |
| ≈ 01:00–05:00 | **Dormir** (imprime la base de la entrada) | **Dormir** |

### Jueves 19

| Hora | Luis | Equipo |
|---|---|---|
| 05:00–08:00 | Armar la caja `dht` con su electrónica; tomas sobre fondo blanco | Tapa de la entrada a la cola |
| 08:00–11:00 | Si se puede, instalar el `dht` en el cuarto y grabar | Armar la estación de entrada; toma del imán y el LED rojo (sirve para el GIF) |
| **Descanso de 30 min** | | |
| 11:30–17:00 | Reporte: pruebas y resultados reales | Alerta al celular (WhatsApp o Telegram); P-06 a P-09; captura del dashboard con datos reales |
| 17:00–17:30 | **Descanso** | **Descanso** |
| 17:30–23:00 | Armar la estación del anaquel en cuanto salgan sus piezas | Narración de los bloques 6–8 con los resultados; GIF del perfil |
| 23:00–04:00 | **Dormir** (imprime la tapa del anaquel) | **Dormir** |

### Viernes 20 (entrega 23:59)

| Hora | Luis | Equipo |
|---|---|---|
| 04:00–09:00 | Últimas tomas de la estación del anaquel; P-09 de repetibilidad (20 de 20) | — |
| 09:00–09:30 | **Descanso** | **Descanso** |
| 09:30–15:00 | Reporte: cerrar los `[POR COMPLETAR]`, figuras, anexos y formato | Edición del video (3–5 min, nombre `Argos_Equipo2_G507.mp4`, sin caras del equipo) |
| 15:00–15:30 | **Descanso** | **Descanso** |
| 15:30–19:00 | Revisión cruzada: alguien que no lo escribió lee el reporte y ve el video completo | Imágenes del perfil (GIF + 2) |
| 19:00–21:00 | **Subir todo** y comprobar que la plataforma lo muestra | — |
| 21:00–23:59 | Margen para fallas de la plataforma | — |

## Faltantes del 18-nov

- **OLED 2.42" SSD1309 no llegó.** Comprar una de 4 pines I²C con entrega para el jueves 19 (Mercado Libre Full o Amazon Prime). Mientras tanto se arma y prueba el `dht` con el firmware `dht_sin_oled` (DHT22 en D2). La tapa del `dht` va al final de la cola; la base no depende de la OLED. Si la OLED no llega el 19, el video muestra el `dht` sin pantalla.
- **PETG no llegó.** Llamar a tiendas de Monterrey para recogerlo hoy. Si no hay, imprimir en PLA para el video (el cuarto está a 22–28 °C) y reimprimir en PETG para la exposición del 1 de diciembre. En PLA, probar con el cupón el clip más suave (gancho de 0.8 mm), porque el PLA se rompe antes de doblarse.

### Actualización del 18-nov, tarde

- La OLED tampoco se consiguió en tienda física. **No se compra la LCD 2×16 de Steren (ARD-380):**
  - es paralela de 16 pines y necesita 6 GPIO libres; el `dht` no los tiene;
  - funciona a 5 V;
  - obligaría a rehacer la tapa (tarjeta de 80 × 36 mm) y la pantalla del firmware.

  Para el 20 el `dht` va **sin pantalla** (`dht_sin_oled`, ya compila). La OLED se pide en línea para la exposición del 1-dic.
- PETG a $1,000 no conviene: comprar **PLA de 1.75 mm, 1 kg, blanco** (≈ $300–400). Probar primero el cupón de clips.

### Actualización del 18-nov, noche: se consiguió la OLED 2.42"

- **Se regresó todo a la OLED 2.42" SSD1309 128×64** (la del diseño original): firmware (`vista_oled.h`, `main.cpp`, sketches de Arduino IDE; compila), tapa y grapa del `dht` en las dos variantes (0 interferencias), página web, renders y Fritzing.
- Lo de la 0.91" que sigue abajo queda como historial. Sus archivos están en `respaldo_oled_091/`.
- Falta medir el módulo real (`oled.modulo_2p42`, `area_activa_2p42`, `centro_activo_desde_conector`) antes de imprimir la tapa del `dht`.

### (Historial) Decisión del 18-nov, tarde: OLED 0.91"

- Se usa la **OLED 0.91" SSD1306 128×32 de Steren (ARD-384)**. Mismos pines: D1 = SCL, D2 = SDA, 3V3, GND. En el video y el reporte se explica que la 2.42" no se consiguió a tiempo.
- **Ya cambiado:**
  - Firmware: `firmware/src/dht/main.cpp` y `firmware/include/vista_oled.h`. Compila (`dht` y `dht_sin_oled`) y los sketches de Arduino IDE ya están regenerados.
  - Pantalla nueva: temperatura grande a la izquierda; estado y humedad a la derecha. Ver `docs/oled_estados.png`.
  - Tapa del `dht`: ventana de 24.4 × 7.6 mm y grapa que cruza de arriba abajo, del lado derecho. Regenerada la versión modular y la de tornillos: 0 interferencias. La tapa no necesita soportes; **la grapa conviene imprimirla con borde (brim)**.
  - Página web (`presentacion/`).
- **Falta al tenerla en la mano:**
  1. Medir el módulo (largo × alto × grueso, área que se ilumina y su centro desde el lado de los pines) y pasarlo a `cad/medidas.json` (`oled.modulo_0p91`, `area_activa_0p91`, `centro_activo_desde_conector_0p91`). Regenerar antes de imprimir la tapa.
  2. Si la imagen sale de cabeza, cambiar `U8G2_R0` por `U8G2_R2` en `main.cpp`.
  3. Se lee a ≈ 1 m, no a 2 m: en el reporte va como limitación.

## Plan B

- **La impresora falla o se atrasa:** la prioridad es que salga la caja `dht` completa. Las estaciones se muestran armadas en protoboard sobre fondo blanco, junto a sus renders, y en el video se explica que su caja se imprime para la exposición del 1 de diciembre.
- **El hardware llega tarde o incompleto:** se usa como evidencia la prueba real del nodo puerta del 13-nov, más el simulador y el dashboard, como dice el guion.
- **La red del Tec no deja conectarse a los nodos:** router propio con el server conectado a él.
- **El broche de la tapa no funciona y no hay insertos:** cerrar con cinta o con 2 tornillos directos en plástico solo para el video. Se reimprime después del 20.
