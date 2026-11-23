# Solicitud: modelos 3D, circuitos en protoboard y conexiones (resumen)

Equipo G507 · 19-oct-2026. Resumen de la orden de trabajo del usuario. Pines y contexto en `CLAUDE.md`.

## Entregables

**A. Carcasas 3D (5 nodos):** script paramétrico build123d (`cad/nodos.py`, diccionario `medidas`, una función por nodo); gemelo digital del ensamble (protoboard + NodeMCU + módulos) para derivar la envolvente, comprobar interferencias (= 0) y holguras (≥ 2 mm); exportes STEP y STL `cad/exports/nodo_<id>_<pieza>.step|stl` con orientación de impresión; renders (isométrico por nodo, vistas con cotas, explosionada del `dht`, escena del `dht` en anaquel con frascos); BOM de fijaciones (M3, insertos, cinta, sílica); `cad/informe_verificacion.md` (holguras, chequeo de imprimibilidad, volumen/masa de filamento).

**B. Protoboard por nodo:** tabla punto a punto (color y longitud de cable); distribución con coordenadas (columnas, filas a–j, rieles) como tabla y SVG/PNG; componentes con polaridad; verificación eléctrica escrita (niveles, corrientes, 3V3 vs VIN).

**C. Documentación:** WireViz (`.yml` + SVG/PNG) por nodo; diagrama de arquitectura; `docs/guia_ensamble.md` (orden de armado, continuidad, voltajes); firmware de referencia en `firmware/` que **solo compila** (`nodemcuv2`).

## Notas de diseño

- NodeMCU en protoboard: probablemente queda **un orificio libre por pin** (filas a y j). Es una deducción de la geometría estándar que hay que verificar con las piezas reales. Riel superior partido en 3V3 y 5 V (rotulados); riel inferior = GND.
- `dht`: con y sin OLED (variante en `CLAUDE.md` §3).
- Medidas nominales: NodeMCU Amica ≈ 49×26 mm; DHT22 ≈ 15.1×25×7.7 mm; HC-SR501 ≈ 32×24 mm con domo Ø23 mm; OLED 0.96" ≈ 27×27 mm, ventana ≈ 22×11 mm. El resto `[MEDIR]`.

## Fases (con puerta de ok del usuario)

0 diagnóstico ✔ · 1 instalación ✔ · 2 mediciones → `cad/medidas.json` (valor, unidad, fuente medido/nominal) · 3 circuitos del `dht` y compilación del firmware · 4 modelo 3D del `dht` · 5 variantes `luz`, `pir`, `puerta`, `acel` · 6 explosionada, escena, guía, BOM, arquitectura · 7 archivos para prueba de ajuste en PLA.

## Preguntas antes de modelar

1. ¿NodeMCU Amica o LoLin? Largo, ancho, alto y posición del micro-USB.
2. ¿Protoboard del kit (puntos) y medidas exactas?
3. ¿Se usa la OLED? ¿Qué módulo exacto y sus medidas? ¿Ya se avisó a los encargados?
4. ¿DHT22 de 3 o 4 pines? ¿Pinout del KY-012?
5. ¿Quién tiene impresora y filamento, y de qué material?
6. ¿Diseño de Claude Design o imágenes de referencia?
7. ¿Qué tornillos e insertos M3 hay disponibles (largos)?
8. ¿Dónde y con qué fijación se monta cada nodo?

## No hacer

Wokwi; KiCad/tscircuit/PCB; InfluxDB/Grafana; flashear; tocar n8n productivo; cambiar pines, topics, alertas o BD; generadores de IA 3D; sobredesarrollar.
