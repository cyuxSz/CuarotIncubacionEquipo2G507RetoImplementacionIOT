# Argos en GitHub: plan de presentación por sprints

Versión 2, 22-nov-2026. Todavía no se sube ni se cambia nada en GitHub.
Repo: <https://github.com/cyuxSz/CuarotIncubacionEquipo2G507RetoImplementacionIOT> (público, rama `main`; hoy solo trae `LICENSE` y un `README.md` de una línea; 2 commits, 24-sep y 2-oct).
Tablero: GitHub Projects **CalendarizacionIoTEquipo2G507** (Board/Kanban, Roadmap, Priority board, Team items, My items). Columnas: **To-Do / In progress / Done**.

## 0. Fuentes

| Fuente | Qué aporta |
|---|---|
| GitHub (lectura con `gh api`, 22-nov) | Issues #3–#32 con responsables, fechas de apertura y cierre, milestones y etiquetas |
| `git log --date=short` de este repo (22 commits, 21-oct → 10-nov) | Fechas de diseño, plano, servidor y carcasas |
| `CLAUDE.md`, `Estado.md`, `docs/frentes_trabajo.md` (9-nov), `docs/plan_entrega_20nov.md` | Reparto, calendario, prueba del nodo `puerta` del 13-nov |
| Copia de José María `Argos_22nov_noche/` (handoff del 20-nov, estado del 22-nov, `Estado.md` del 19-nov) | Servidor central, auditoría, OLED en SPI, impresión, 5 nodos en línea, Telegram |
| Copia de Iván (`LEEME_PRIMERO.md` y `expo_21nov/`, 22-nov) | Firmware final por nodo, dashboard nuevo, reimpresiones, entregables de la Expo |
| Confirmado por Luis (22-nov) | OLED final = 2.42" de 7 pines en SPI (funcionó); las 2 estaciones están terminadas; todo se imprimió y se reimprimió; el repo general es el de arriba |

Pendiente: el zip `Argos_servidor_para_GitHub_2026-11-22_1758.zip` (12 commits del servidor) no venía en la carpeta de José María. Se pide con el prompt de la §6.

## 1. Lo que ya existe en GitHub

### Milestones (= etapas del curso)

| # | Milestone | Fecha límite | Estado |
|---|---|---|---|
| 5 | Etapa 1: Definición de la aplicación | 30-sep | Cerrado |
| 1 | Etapa 2: Sensores, actuadores y diseño de BD | 21-oct | Cerrado |
| 2 | Etapa 3: Conexión a BD a través del API | 11-nov | Abierto (11 issues abiertos) |
| 3 | Etapa 4: Maqueta de aplicación y dashboard | 27-nov | Abierto |
| 4 | Presentación: ExpoIngeniería | 2-dic | Abierto |
| 6 | Reporte Final: Documentación del Reto | 4-dic | Abierto |

Etiquetas que se usan: `firmware`, `hardware`, `backend`, `base-de-datos`, `dashboard`, `documentación`, `pruebas`, `opcional`, `duplicate`.

### Usuarios de GitHub

| Integrante | Usuario | Nodo |
|---|---|---|
| Luis Mendoza (líder) | `cyuxSz` | dht |
| Arianna Téllez | `AriannaTellez` | luz |
| José María García | `Chema-TPG` | pir |
| Iván Acosta | `ivan-acogar` | puerta |
| Mía Nieto | `Mia-Liz` | acel |

### Limpieza propuesta

- **#1, #2 y #22 fueron borrados** (GitHub responde 410). Sus números no se pueden reutilizar: los huecos se cubren con issues nuevos (§3).
- **Duplicados:** #30 y #32 (Etapa 3 acel) y #29 y #31 (Etapa 3 puerta). #31 y #32 se cerraron el 13-nov; **cerrar #29 y #30** con la etiqueta `duplicate` y dejar en cada uno la referencia al que sí vale.
- Asignar milestone a #24–#32, que no tienen (→ Etapa 3).
- Cerrar lo que ya está hecho (columna Done en las tablas de abajo).

## 2. Sprints

Los sprints siguen las etapas del curso. Fechas de los issues: apertura y cierre en GitHub; las demás salen de los commits y de los LEEME.

### Sprint 0 · Antecedente: Etapas 1 y 2 (24-sep → 5-nov)

Solo como contexto en el README. Repo creado el 24-sep. Backlog inicial (#3–#14) abierto el 2-oct. #15–#21 abiertos el 19-oct.

| Issue | Responsable | Columna | Evidencia |
|---|---|---|---|
| #23 Diseño de la BD (Etapa 2 de software) | cyuxSz, Chema-TPG | Done | Cerrado el 22-oct; commit `9476353` (22-oct) |
| #9 Crear esquema de BD (12 clases) | cyuxSz, Chema-TPG | Done (cerrar) | `docs/bd/esquema.sql`; commit `9476353` |
| N1 Diseño de circuitos y protoboard (`layouts.py`, Fritzing) **(nuevo)** | cyuxSz | Done | `31e000a` (21-oct), Fritzing `c3c85e1` (23-oct) |
| N2 Carcasas v1 en build123d **(nuevo)** | cyuxSz | Done | `31e000a` (21-oct) |

### Sprint 1 · Alcance nuevo, plano y arquitectura (6-nov → 10-nov)

**Objetivo:** cerrar el alcance tras los requisitos del 5-nov, fijar la arquitectura API REST + MQTT y repartir el trabajo.

| Issue | Responsable | Columna | Evidencia |
|---|---|---|---|
| N3 Plano del cuarto 2D/3D y largos de cable **(nuevo)** | cyuxSz | Done | `d284190`, `e5aba85`, `71cd025` (6-nov) |
| #8 Levantar stack local (Mosquitto + n8n + MySQL) | cyuxSz, Chema-TPG | Done (cerrar) | `193d561` (9-nov) |
| N4 Firmware: guardar por HTTP POST en la API **(nuevo)** | cyuxSz | Done | `193d561` (9-nov) |
| N5 Reparto del trabajo en 5 frentes **(nuevo)** | cyuxSz | Done | `docs/frentes_trabajo.md` (9-nov) |
| #20 (Opcional) Carcasas modulares: clips, tapa a presión y grapa de la OLED | AriannaTellez, Mia-Liz | Done (cerrar, ver Sprint 4) | `a80c3a9` (10-nov) |
| #18 Reconocimiento del sitio y confirmación de datos | Los 5 | Done | Cerrado el 12-nov |

Carpetas: `docs/cuarto/`, `docs/arquitectura/`, `servidor/`, `firmware/`, `cad/`.

### Sprint 2 · Etapa 3: API REST por nodo y BD `argos` (11-nov → 13-nov)

**Objetivo:** una API REST por nodo (puertos 3001–3005), script único de la BD y primera prueba real.

| Issue | Responsable | Columna | Evidencia |
|---|---|---|---|
| #25 API REST base por nodo (Node.js + MySQL) | cyuxSz | Done | Cerrado el 13-nov |
| #24 Script único de la BD (`argos`) | cyuxSz, Chema-TPG | Done | Cerrado el 13-nov |
| #26 Etapa 3 (dht): circuito + API + indicadores + documento y video | cyuxSz | Done (cerrar) | `docs/entregables/etapa3/` |
| #27 Etapa 3 (luz) | AriannaTellez | Done (cerrar) | Nodo funcionando el 22-nov |
| #28 Etapa 3 (pir) | Chema-TPG | Done (cerrar) | Nodo en línea el 22-nov |
| #31 Etapa 3 (puerta) | ivan-acogar | Done | Cerrado el 13-nov; prueba real del nodo `puerta` del 13-nov |
| #32 Etapa 3 (acel) | Mia-Liz | Done | Cerrado el 13-nov |
| #29, #30 | — | Cerrar como `duplicate` | Duplicados de #31 y #32 |

Carpetas: `servidor/api-rest/`, `docs/bd/etapa3/`, `anexos/etapa3/`.

### Sprint 3 · Integración y preparación del armado (14-nov → 18-nov)

**Objetivo:** servidor de punta a punta con el simulador, broker con ACL, mediciones y cupón de impresión.

| Issue | Responsable | Columna | Evidencia |
|---|---|---|---|
| #21 Configurar broker con usuario, ACL y contrato de tópicos | cyuxSz, Chema-TPG | Done (cerrar) | Prueba de ACL planeada el 17-nov; al 22-nov los nodos usan HiveMQ con prefijo `argos-eq2/`: documentarlo al cerrar |
| #10 n8n: reglas de alerta | cyuxSz, Chema-TPG | In progress (pasa a Done en el Sprint 4) | — |
| N6 Cupón de clips y mediciones para impresión **(nuevo)** | AriannaTellez, Mia-Liz | Done | `plan_entrega_20nov.md` (17-nov) |
| N7 Plan de entrega 17 → 20-nov **(nuevo)** | cyuxSz | Done | `docs/plan_entrega_20nov.md` |

Carpetas: `servidor/mosquitto/`, `simulador/`, `cad/cupon_prueba.py`, `cad/medidas.json`.

### Sprint 4 · Armado, impresión y sistema en línea (19-nov → 22-nov)

**Objetivo:** las 3 cajas impresas, reimpresas y armadas; los 5 nodos reportando al servidor; alertas por Telegram y dashboard final. Límite de las cajas: 22-nov a las 23:59.

| Issue | Responsable | Columna | Evidencia |
|---|---|---|---|
| N8 Servicio central (panel, alertas que cruzan nodos, `cmd/alarma`) **(nuevo)** | Chema-TPG, cyuxSz | Done | `Estado.md` (19-nov): 54/54 en `prueba_integracion.js` |
| N9 Auditoría de firmware, servidor y electrónica **(nuevo)** | cyuxSz | Done | `Estado.md` (19-nov) |
| N10 OLED 2.42" de 7 pines (ZJY_M242, SSD1309) en SPI por software **(nuevo)** | cyuxSz, ivan-acogar | Done | Pines cambiados el 19-nov; funcionó (confirmado por Luis) |
| N11 Diagramas de Fritzing por pasos y por pieza (modo UTP) **(nuevo)** | cyuxSz, ivan-acogar | Done | 19–21-nov |
| #20 Impresión en PETG (Creality Print, K2, 0.20 mm, sin soportes) de las 3 cajas | AriannaTellez, Mia-Liz, ivan-acogar | Done | Caja `dht` el 20-nov; estaciones terminadas al 22-nov |
| N12 Reimpresión por los cierres de las tapas y el ajuste de sensores **(nuevo)** | AriannaTellez, Mia-Liz, ivan-acogar | Done | Reimpreso todo al 22-nov (fecha exacta `[POR CONFIRMAR]`) |
| N13 Armado y prueba de banco de las 3 cajas **(nuevo)** | ivan-acogar, AriannaTellez, Mia-Liz | Done | `dht`, estación de entrada y estación del anaquel terminadas |
| #4 Firmware dht | cyuxSz | Done (cerrar) | `argos_dht_v2` cargado y probado (22-nov) |
| #3 Firmware luz | AriannaTellez | Done (cerrar) | Funcionó (22-nov) |
| #5 Firmware pir | Chema-TPG | In progress | En línea; HC-SR501 con salida pegada en ALTO |
| #6 Firmware puerta | ivan-acogar | Done (cerrar) | 22-nov |
| #7 Firmware acel | Mia-Liz | Done (cerrar) | Funcionó tras corregir conexiones y ADS1115 (22-nov) |
| #10 n8n: reglas de alerta | Chema-TPG | Done (cerrar) | Flujo activo, alertas graves de 7 a 22 h |
| #11 Avisos de alerta | Chema-TPG | Done (cerrar) con nota | Telegram activo. WhatsApp no, porque necesita una API de paga: abrir N18 con la etiqueta `opcional` |
| #13 Dashboard con los 5 indicadores | ivan-acogar, Chema-TPG | Done (cerrar) | Dashboard nuevo + Ajustes + cuenta admin (22-nov) |
| N14 Botón «Silenciar» en el tablero + firmware dht v3 **(nuevo)** | ivan-acogar | In progress | Compila; falta probarlo en la placa |
| N15 Póster, logo, fondo y carrusel de la Expo **(nuevo)** | ivan-acogar | Done | Subidos a la plataforma |

Carpetas: `servidor/central/`, `servidor/web-dashboard/`, `servidor/n8n/`, `firmware/`, `hardware/`, `cad/`.

### Sprint 5 · Cierre: Etapa 4, Expo y reporte final (23-nov → 4-dic)

| Issue | Responsable | Columna | Fecha |
|---|---|---|---|
| N16 Subir reporte PDF y video MP4 **(nuevo)** | cyuxSz, ivan-acogar | To-Do | 23-nov |
| N17 Fotos de integrantes **(nuevo)** | Los 5 | To-Do | 24-nov |
| #5 Arreglar PIR pegado en ALTO | Chema-TPG | In progress | Antes del ensayo |
| N19 `MODO_DEMO` en la tabla y en el firmware del dht + reflasheo **(nuevo)** | cyuxSz | To-Do | Antes de la Expo (rangos `[POR CONFIRMAR]`) |
| N20 Pasar dht v2/v3 a `firmware/src/dht/main.cpp` **(nuevo)** | cyuxSz | To-Do | — |
| #15 Ejecutar pruebas P-01 a P-09 | AriannaTellez, Mia-Liz, ivan-acogar | In progress | Etapa 4 (27-nov) |
| #16 Instalación física, fijación y calibración | AriannaTellez, Mia-Liz, ivan-acogar | To-Do | Etapa 4 (27-nov) |
| #19 Respaldos y purga de 90 días | cyuxSz, Chema-TPG | To-Do | Etapa 4 (27-nov) |
| N21 Limpiar los datos de prueba de la BD **(nuevo)** | Chema-TPG | To-Do | Antes de la Expo |
| N22 Ensayo general: 5 nodos + dashboard + Telegram **(nuevo)** | Los 5 | To-Do | Antes del 1-dic |
| #14 Repo con código, README y anexos | cyuxSz | In progress | Reporte final (4-dic) |
| #17 Revisión de seguridad y traspaso | cyuxSz, Chema-TPG | To-Do | Reporte final (4-dic) |
| N23 Expo presencial, Arena Borregos **(nuevo)** | Los 5 | To-Do | 1-dic, 12–17 h |
| #12 Migrar a Oracle Cloud | — | Cerrar como `wontfix` | Ya hay servidor en la escuela |
| N18 WhatsApp (opcional) **(nuevo)** | Chema-TPG | To-Do | Solo si lo piden |

Fuera de alcance (backlog, etiqueta `opcional`): N24 actuador del fotoperiodo `luz_rele` y caja de potencia (`c7e2a65`, 5-nov). El control del minisplit tampoco entra.

## 3. Issues nuevos (N1–N24) — **creados el 22-nov**

Aplicado en GitHub el 22-nov: N1→#33, N2→#34 … N24→#56 (en orden). Los que ya estaban hechos se crearon cerrados y en Done. #46 (N14) está en In progress. #48–#56 están en To-Do. Además: #29 y #30 se cerraron como `duplicate` y se archivaron en el tablero; #12 se cerró como `wontfix`; se cerraron #3, #4, #6–#11, #13, #20, #21 y #26–#28, cada uno con un comentario de evidencia; #31 y #32 se agregaron al tablero en Done; #24–#32 quedaron con el milestone de la Etapa 3; #5 lleva un comentario con la falla del PIR.

Distribución original:

Se crean con el título de las tablas, la etiqueta que corresponda, el milestone de su etapa y el responsable. Los que ya están hechos se crean y se cierran en el momento, con un comentario que cite el commit o el archivo que lo prueba. Así se cubren los huecos de #1, #2 y #22 sin inventar historia: GitHub muestra la fecha real de creación y el comentario explica cuándo se hizo el trabajo.

| Etiqueta | Issues nuevos |
|---|---|
| `hardware` | N1, N6, N10, N11, N12, N13, N24 |
| `firmware` | N4, N14, N19, N20 |
| `backend` | N8, N18 |
| `base-de-datos` | N21 |
| `documentación` | N3, N5, N7, N9, N15, N16, N17, N23 |
| `pruebas` | N22 |
| `opcional` | N18, N24 |

N2 (carcasas) va con `hardware`.

## 4. Estructura del repo

```
CuarotIncubacionEquipo2G507RetoImplementacionIOT/
├── README.md                   # ver docs/github/README.md (borrador)
├── LICENSE                     # ya existe
├── .gitignore                  # .env, secrets.h, passwd, node_modules, ESTADO_SERVIDOR.md
├── docs/
│   ├── sprints.md              # este plan, versión final
│   ├── arquitectura/           # arquitectura.dot/.png, despliegue, flujo del firmware
│   ├── bd/                     # esquema.sql, script argos, diagrama ER
│   ├── contrato_mqtt.md        # topics, payloads, QoS; HiveMQ con prefijo argos-eq2/
│   ├── cuarto/                 # plano de ubicación, modelo 3D del cuarto
│   └── pruebas/                # P-01…P-09, integración 54/54, mediciones del 22-nov
├── firmware/
│   ├── include/                # nodo_comun.h, alarma_dht.h, vista_oled.h, secrets.example.h
│   ├── src/{dht,luz,pir,puerta,acel}/main.cpp
│   └── arduino_ide/argos_*/    # sketches que se cargaron
├── servidor/
│   ├── api-rest/               # una API por nodo, puertos 3001–3005
│   ├── central/                # motor de alertas, panel y cuenta admin
│   ├── web-dashboard/          # código fuente del dashboard
│   ├── n8n/                    # flujos SIN credenciales
│   ├── mosquitto/              # conf y ACL (sin passwd)
│   ├── pruebas/
│   └── LEEME.md, OPERACION.md, arrancar.ps1, .env.example
├── hardware/
│   ├── breadboard/layouts.py   # fuente de verdad del armado
│   └── fritzing/               # generador + salida (.fzz y .png): los únicos diagramas que se presentan
├── cad/
│   ├── nodos.py, cielo_argos.py, medidas.json
│   └── impresion/              # STL/3MF finales (versión reimpresa) + perfil Creality Print K2 PETG
├── simulador/
└── anexos/                     # etapa3/, gestion/ (capturas del Kanban y del Roadmap), expo/
```

No se suben: `.env`, `secrets.h`, `servidor/ESTADO_SERVIDOR.md` (túneles y `chat_id`), `mosquitto/passwd`, `node_modules/`, los `.step` pesados, KiCad y WireViz (no se presentan), respaldos (`*.antes_*`, `respaldo_oled_091/`) ni maquetas de textura.

**Historial de commits:** el repo de José María ya trae 12 commits del servidor. Lo más limpio es subir esa historia del servidor y agregar encima un commit por carpeta (firmware, hardware, cad, docs, anexos), con fecha de hoy. Así no se reescriben fechas.

## 5. Pasos en GitHub (solo con el visto bueno de Luis)

**Hecho el 22-nov:** pasos 1 a 3. El código se subió en 6 commits, uno por sprint, cada uno con los issues que cubre. No se reescribieron fechas: cada commit tiene la fecha del día en que se subió, y su mensaje dice a qué sprint corresponde.

1. Limpiar issues (§1) y crear N1–N24 (§3).
2. Mover las tarjetas del tablero a su columna final y llenar las fechas del Roadmap con las de los sprints.
3. Subir el código con la estructura de §4 y el README.
4. Captura final del Kanban y del Roadmap para `anexos/gestion/`.

## 6. Prompt para el Claude de José María

Ver el mensaje del 22-nov en el chat. La versión es la misma que está abajo, para copiarla:

> Necesito información del zip `Argos_servidor_para_GitHub_2026-11-22_1758.zip` (el servidor limpio con 12 commits) para armar el plan de sprints del repo del equipo. No subas, no hagas push ni crees nada en GitHub, y no leas ni copies secretos (`.env`, `secrets.h`, `ESTADO_SERVIDOR.md`, tokens, contraseñas, URLs de túneles, `chat_id`).
> 1. Dame la ruta del zip y, si se puede, deja una copia en una carpeta compartida con Luis.
> 2. Lista los 12 commits como `fecha (YYYY-MM-DD) · hash corto · autor · mensaje`, sacados del `git log --date=short` del repo o del script que los crea. Si el script les pone fechas fijas, dime si son las fechas reales del trabajo o las de cuando se armó el zip.
> 3. Dame el árbol de carpetas del zip, solo dos niveles, y qué contiene `.gitignore`.
> 4. Para cada una de estas piezas, dime la fecha en que quedó funcionando, con su evidencia (commit, LEEME o bitácora), o márcala `[POR CONFIRMAR]`: Mosquitto con ACL; el cambio a HiveMQ con prefijo `argos-eq2/`; el servicio central; la cuenta admin; los túneles (solo la fecha, sin URLs); el flujo de Telegram `avisos_telegram_formato.json`; la publicación del dashboard nuevo; el campo `buzzer`; los 5 nodos en línea.
> 5. Dime si el broker de Mosquitto con usuarios y ACL llegó a usarse o si quedó solo HiveMQ.
> Responde en español, en una sola tabla más una lista de pendientes. No inventes fechas.
