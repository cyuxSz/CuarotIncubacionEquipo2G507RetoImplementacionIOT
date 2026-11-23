# Argos · Monitoreo IoT del cuarto de incubación in vitro

Reto de Implementación de internet de las cosas (TC1004B) · Grupo 507 · Equipo 2 · Tec de Monterrey

Argos vigila el cuarto de incubación in vitro del Invernadero Académico. Mide temperatura, humedad, encendido de las luminarias, movimiento, apertura de la puerta y golpes en el anaquel. Cuando algo sale de rango, avisa con una alarma local, en un dashboard y por Telegram.

| Variable | Rango aceptable |
|---|---|
| Temperatura | 22–28 °C |
| Humedad relativa | 40–60 % |

## Equipo

| Integrante | GitHub | Nodo | Sensor |
|---|---|---|---|
| Luis Eduardo Mendoza Menéndez (líder) | [@cyuxSz](https://github.com/cyuxSz) | `dht` | DHT22, buzzer, botón y OLED 2.42" |
| Arianna Téllez | [@AriannaTellez](https://github.com/AriannaTellez) | `luz` | LDR |
| José María García Sánchez | [@Chema-TPG](https://github.com/Chema-TPG) | `pir` | HC-SR501 |
| Iván Acosta | [@ivan-acogar](https://github.com/ivan-acogar) | `puerta` | Reed switch MC-38 |
| Mía Nieto | [@Mia-Liz](https://github.com/Mia-Liz) | `acel` | GY-61 (ADXL335) + ADS1115 |

## Arquitectura

```
5 × NodeMCU ESP8266 ──HTTP POST──► API REST por nodo (Node.js, puertos 3001–3005) ──► MySQL (base argos)
        │                                                                                ▲
        └──MQTT (estado, LWT, cmd/alarma)──► broker ◄── servicio central (alertas, panel) ┘
                                                             │
                                                             └──► n8n ──► Telegram (de 7:00 a 22:00)
```

- **Nodos:** 5 NodeMCU ESP8266 en 3 cajas impresas en PETG. La caja `dht` va sola. La estación de entrada lleva `pir` y `puerta`, y la estación del anaquel lleva `acel` y `luz`.
- **API REST:** el mismo código para los 5 nodos; solo cambia `NODO` en el `.env`. Es lo único que escribe en MySQL.
- **Servicio central:** abre y cierra las alertas que cruzan nodos (nodo caído, puerta abierta de más, golpe, falla de sensor) y sirve el dashboard.
- **Alertas graves:** se envían por Telegram de 7:00 a 22:00 (America/Monterrey). La BD guarda en UTC.
- **Actuadores:** el LED rojo de cada nodo y el buzzer del nodo `dht`. El buzzer se silencia 30 min con el botón o desde el dashboard.

Detalle en [`docs/arquitectura/`](docs/arquitectura/) y [`docs/contrato_mqtt.md`](docs/contrato_mqtt.md).

## Estructura

| Carpeta | Contenido |
|---|---|
| [`firmware/`](firmware/) | Código de los 5 nodos (PlatformIO y sketches de Arduino IDE) |
| [`servidor/`](servidor/) | APIs REST, servicio central, dashboard, flujos de n8n, broker y pruebas |
| [`hardware/`](hardware/) | Armado en protoboard (`layouts.py`) y diagramas de Fritzing |
| [`cad/`](cad/) | Carcasas en build123d y archivos de impresión |
| [`simulador/`](simulador/) | Simulador de los 5 nodos sin hardware |
| [`docs/`](docs/) | Arquitectura, BD, contrato MQTT, plano del cuarto, pruebas y sprints |
| [`anexos/`](anexos/) | Entregables por etapa, capturas de gestión y material de la Expo |

## Cómo correrlo

1. **Base de datos:** en MySQL 8, ejecuta el script de `docs/bd/etapa3/` (`ScriptCreacionBaseDatos_iot_Equipo2.sql`, base `argos`).
2. **Servidor:** sigue [`servidor/LEEME.md`](servidor/LEEME.md). Copia los `.env.example` a `.env`, corre `npm install` en `servidor/api-rest` y en `servidor/central`, y después `servidor/arrancar.ps1`.
3. **Firmware:** abre `firmware/arduino_ide/argos_<nodo>/` en Arduino IDE (placa NodeMCU 1.0 / ESP-12E). Crea `secrets.h` a partir de `secrets.example.h` y carga el programa.
4. **Sin hardware:** usa `simulador/` para publicar datos de los 5 nodos.

Los secretos (`.env`, `secrets.h`, contraseñas y tokens) no se versionan.

## Gestión del proyecto

- **Tablero:** GitHub Projects *CalendarizacionIoTEquipo2G507*, con vista Kanban (To-Do / In progress / Done) y Roadmap.
- **Milestones:** una por etapa del curso, más la Expo y el reporte final.
- **Issues:** uno por tarea, con responsable, etiqueta (`firmware`, `hardware`, `backend`, `base-de-datos`, `dashboard`, `documentación`, `pruebas`) y prioridad P0–P2.
- **Flujo de trabajo:** continuo sobre la rama principal, con revisión interna del equipo. No se usaron pull requests.
- **Sprints:** detalle en [`docs/sprints.md`](docs/sprints.md).

| Sprint | Fechas | Objetivo |
|---|---|---|
| 0 | 24-sep → 5-nov | Etapas 1 y 2: definición, sensores, circuitos y diseño de BD |
| 1 | 6 → 10-nov | Alcance nuevo, plano del cuarto y arquitectura API REST + MQTT |
| 2 | 11 → 13-nov | Etapa 3: API REST por nodo y base `argos` |
| 3 | 14 → 18-nov | Integración del servidor, broker y preparación del armado |
| 4 | 19 → 22-nov | Impresión, reimpresión y armado de las 3 cajas; 5 nodos en línea, Telegram y dashboard |
| 5 | 23-nov → 4-dic | Etapa 4, ExpoIngenierías (1-dic) y reporte final |

## Anexos

| # | Anexo | Ubicación |
|---|---|---|
| A | Arquitectura del sistema y despliegue | [`docs/arquitectura/`](docs/arquitectura/) |
| B | Contrato MQTT | [`docs/contrato_mqtt.md`](docs/contrato_mqtt.md) |
| C | Base de datos: esquema, diagrama ER y script `argos` | [`docs/bd/`](docs/bd/) |
| D | API REST por nodo: endpoints y pruebas | [`servidor/api-rest/LEEME.md`](servidor/api-rest/LEEME.md) |
| E | Servicio central y reglas de alerta | [`servidor/central/`](servidor/central/) |
| F | Flujos de n8n (Telegram) | [`servidor/n8n/`](servidor/n8n/) |
| G | Dashboard | [`servidor/web-dashboard/`](servidor/web-dashboard/) |
| H | Diagramas de conexión en Fritzing | [`hardware/fritzing/`](hardware/fritzing/) |
| I | Armado en protoboard (fuente de verdad de pines) | [`hardware/breadboard/layouts.py`](hardware/breadboard/layouts.py) |
| J | Carcasas 3D y perfil de impresión (Creality K2, PETG) | [`cad/`](cad/) |
| K | Plano de ubicación en el cuarto | [`docs/cuarto/`](docs/cuarto/) |
| L | Pruebas: integración del servidor y programas de prueba de los nodos | [`servidor/pruebas/`](servidor/pruebas/), [`firmware/pruebas/`](firmware/pruebas/) |
| M | Entregables de la Etapa 3 | [`anexos/etapa3/`](anexos/etapa3/) |
| N | Capturas del tablero Kanban y del Roadmap | [`anexos/gestion/`](anexos/gestion/) |
| O | Póster, láminas y figuras de ExpoIngenierías | [`anexos/expo/`](anexos/expo/) |
| P | Guía de armado y montaje 3D (HTML) | [`presentacion/`](presentacion/) |
| Q | Bitácora y decisiones | [`docs/bitacora/`](docs/bitacora/) |
| R | Entregables anteriores del curso (generadores) | [`anexos/entregables/`](anexos/entregables/) |

## Encargados del cuarto

Ing. Enrique Puga y Dr. Luis Ricardo Salgado Garza, Invernadero Académico.
