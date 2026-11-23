# Argos · Equipo 2 · Etapa 3: paquete para cada integrante

Todo lo que necesitas para tu entrega individual: la base de datos (la misma para los cinco), la API REST (el mismo código para los cinco; solo cambia el nodo), el programa de tu NodeMCU y tus indicadores.

Probado el 13-nov-2026 en MySQL local con los cinco nodos, mandando las peticiones desde la computadora. **Ningún programa se ha probado todavía en un NodeMCU real:** si algo falla al subirlo, avisa en el grupo.

## Quién lleva qué

| Nodo | Integrante | Matrícula | Puerto de su API | Qué guarda |
|---|---|---|---|---|
| `dht` | Luis Mendoza | A01669847 | 3001 | Mediciones de temperatura y humedad |
| `luz` | Arianna Téllez | A00845027 | 3002 | Mediciones de luz |
| `pir` | José María García | A00843900 | 3003 | Eventos de movimiento |
| `puerta` | Iván Acosta | A00227979 | 3004 | Eventos de puerta abierta y cerrada |
| `acel` | Mía Nieto | A00845663 | 3005 | Eventos de golpe |

Revisa tu matrícula. Si está mal, pásala al comando del paso 2.

## Qué trae la carpeta

| Carpeta o archivo | Qué es |
|---|---|
| `01_base_de_datos/` | `ScriptCreacionBaseDatos_iot_Equipo2.sql` (crea la base `argos`) y `datos_prueba_Equipo2.sql` |
| `02_api_rest/` | API REST en Node.js (base de la carpeta `api-rest` de la clase) |
| `03_firmware/` | Programa de Arduino de cada nodo |
| `04_indicadores/` | Tres consultas SQL por nodo |
| `05_modelo_de_documento/` | Documento técnico y PDF de indicadores del nodo `dht`, como ejemplo |
| `preparar_entrega.js` | Arma tu carpeta de entrega con los nombres que pide Canvas |

## Antes de empezar

- **Node.js 20.6 o más nuevo** (`node -v` en una terminal).
- **MySQL** local y **DBeaver**, como en clase.
- **Arduino IDE 2** con la placa *esp8266 by ESP8266 Community* versión 3.1.2 (URL del gestor de placas: `https://arduino.esp8266.com/stable/package_esp8266com_index.json`). Placa: *NodeMCU 1.0 (ESP-12E Module)*.
- Librerías de Arduino, en estas versiones:

| Librería | Versión | Quién la necesita |
|---|---|---|
| PubSubClient (Nick O'Leary) | 2.8 | Todos |
| ArduinoJson (Benoit Blanchon) | 6.21.5 (no la 7) | Todos |
| DHT sensor library (Adafruit) | 1.4.6 | `dht` |
| Adafruit Unified Sensor | 1.1.14 | `dht` |
| U8g2 (oliver) | 2.35.30 | `dht` |
| Adafruit ADS1X15 | 2.5.0 | `acel` |
| Adafruit BusIO | 1.16.1 | `acel` |

## Paso a paso

### 1. Base de datos

1. En DBeaver, abre `01_base_de_datos/ScriptCreacionBaseDatos_iot_Equipo2.sql` y ejecútalo completo con **Alt+X**. Borra y vuelve a crear la base `argos`, así que lo puedes repetir.
2. Ejecuta igual `datos_prueba_Equipo2.sql`. Carga tres días de datos inventados para que tus indicadores tengan resultados.
3. Refresca la conexión: debe aparecer `argos` con 14 tablas.
4. Si tu API no va a entrar como `root`, dale permiso a tu usuario (conectado como `root`; cambia `usertec` por el tuyo):
   ```sql
   GRANT SELECT, INSERT, UPDATE ON argos.* TO 'usertec'@'localhost';
   ```

### 2. Arma tu carpeta de entrega

En una terminal, dentro de esta carpeta, con tu nodo:

```bash
node preparar_entrega.js pir
```

Crea `entrega_pir/` con tus archivos ya renombrados con tu matrícula. Si tu matrícula o tu nombre no son los de la tabla:

```bash
node preparar_entrega.js pir A00000000 "Tu Nombre Completo"
```

Desde aquí trabaja **dentro de tu carpeta `entrega_<nodo>/`**. No vuelvas a correr el comando después de editar tus archivos: los vuelve a crear desde cero.

### 3. Configura y arranca tu API

1. Entra a `entrega_<nodo>/RestApi-Equipo2-<matrícula>/`.
2. Copia el archivo `.env.example` y nombra la copia `.env`. Llena:
   - `DB_PORT`, `DB_USER`, `DB_PASSWORD`: los mismos de tu conexión de DBeaver.
   - `API_KEY`: una clave que tú inventes (sin espacios).
   - `NODO` ya viene con tu nodo.
3. En una terminal, dentro de esa carpeta:
   ```bash
   npm install
   ```
   ```bash
   npm start
   ```
   Debe imprimir `API del nodo '...' en http://localhost:300X` y `Conectado a MySQL`. Deja esa terminal abierta: si la cierras, la API se apaga.

### 4. Prueba la API sin el NodeMCU

Abre `pruebas.http` en VS Code con la extensión **REST Client**, cambia `TU_API_KEY` por tu clave y manda cada petición con *Send Request*. En DBeaver comprueba que las filas nuevas aparecen en tu tabla (`Medicion` o `Evento`, y `AccionControl`). Toma capturas: sirven para la sección de pruebas.

### 5. Programa del NodeMCU

1. Abre `entrega_<nodo>/Arduino-Equipo2-<matrícula>/Arduino-Equipo2-<matrícula>.ino` en Arduino IDE.
2. En esa carpeta, copia `secrets.example.h` y nombra la copia `secrets.h`. Llena:
   - `WIFI_SSID` y `WIFI_PASSWORD`: una red de 2.4 GHz (el ESP8266 no ve redes de 5 GHz). Tu computadora debe estar en la misma red.
   - `API_HOST`: la IPv4 de tu computadora (`ipconfig` en una terminal).
   - `API_PORT`: el puerto de tu nodo (tabla de arriba).
   - `API_KEY`: la misma clave de tu `.env`.
   - `MQTT_HOST` y `MQTT_PASSWORD`: déjalos vacíos. MQTT no se usa en esta etapa. Sin broker, el LED verde parpadea lento; es normal.
3. Sube el programa y abre el monitor serial a **115200**. Debes ver los valores del sensor y líneas como `[api] POST /api/... -> 201`.
4. Si sale `-> -1` o no conecta: revisa la IP, que la API esté corriendo y que el firewall de Windows deje entrar tu puerto.

No entregues tu `secrets.h` ni tu `.env`: tienen tus claves.

### 6. Indicadores

Abre tu `indicadores_iot_Equipo2-<matrícula>.sql` en DBeaver y ejecuta cada consulta. Captura el resultado de las tres para tu PDF.

## Datos de tu nodo para el documento y el video

| Nodo | Tablas que usa | Rutas de la API | Frecuencia de registro |
|---|---|---|---|
| `dht` | Medicion, Umbral, Alerta, AccionControl, EstadoNodo | POST mediciones, acciones; GET comandos | Cada 30 s. Una alerta se abre con 3 lecturas seguidas fuera de rango (90 s) |
| `luz` | Medicion, AccionControl, EstadoNodo | POST mediciones, acciones, latido | Muestra cada 5 s y guarda el promedio cada 60 s; el promedio filtra sombras momentáneas |
| `pir` | Evento, AccionControl, EstadoNodo | POST eventos, acciones, latido | Solo cuando detecta movimiento; latido cada 60 s |
| `puerta` | Evento, AccionControl, EstadoNodo | POST eventos, acciones, latido | Solo cuando la puerta se abre o se cierra; latido cada 60 s |
| `acel` | Evento, AccionControl, EstadoNodo | POST eventos, acciones, latido | Solo cuando hay un golpe mayor al umbral; latido cada 60 s |

- Todos usan además Nodo, Sensor y Actuador para identificar de dónde viene cada dato; `dht` y `luz` también Parametro.
- **Eventos de actuación:** cada nodo registra en `AccionControl` cuando su LED rojo se prende o se apaga. El `dht` registra también el buzzer.
- **Sensor y umbrales (pregunta de la profesora):** un sensor puede medir varios parámetros y cada uno tiene su rango. El DHT22 tiene dos filas en `Umbral`: temperatura y humedad. No puede haber dos umbrales del mismo parámetro. La histéresis es el margen para cerrar la alerta: se abre al pasar de 28 °C y se cierra hasta bajar de 27.5 °C, para que no se abra y cierre sin parar.
- La lista completa de rutas y la explicación del código están en el `LEEME.md` de tu carpeta de la API.

## Qué subes a Canvas

1. `ScriptCreacionBaseDatos_iot_Equipo2.sql`
2. `indicadores_iot_Equipo2-<matrícula>.sql` y su PDF (nombre, utilidad, consulta, resultado y explicación de cada indicador)
3. La carpeta `RestApi-Equipo2-<matrícula>/`, **sin** `node_modules` y **sin** `.env`
4. La carpeta `Arduino-Equipo2-<matrícula>/`, **sin** `secrets.h`
5. El documento técnico en PDF
6. El video (máximo 3 minutos, narrado)

### Documento técnico

Usa el de `05_modelo_de_documento/` como guía de secciones y cambia el contenido por el de tu nodo: portada, introducción, metodología, descripción del circuito, diagrama de conexiones, diagrama global, modelo de base de datos y tablas de tu circuito, implementación en MySQL (capturas de DBeaver), API REST, código de Arduino, funcionamiento e integración, indicadores, pruebas y resultados, administración del proyecto.

Capturas que tienes que tomar tú:

- Diagrama de la base en DBeaver (clic derecho en la base, *Ver diagrama*).
- Contenido de las tablas de tu sensor, con los datos que mandó tu NodeMCU.
- Monitor serial y terminal de la API durante la prueba.
- Kanban y Gantt del GitHub Project: a la mitad del periodo y un día antes de la entrega.

### Video

Debe mostrar: el circuito funcionando, el monitor serial, la API recibiendo las peticiones, los datos en MySQL con una consulta, la frecuencia de registro y por qué se eligió, y una explicación breve del código de Arduino y de la API.

## Problemas comunes

| Síntoma | Causa probable |
|---|---|
| `Falta NODO en el .env` o `Falta API_KEY` | No copiaste `.env.example` como `.env` o le falta un valor |
| `Error conectando a MySQL: Access denied` | Usuario, contraseña o puerto distintos a los de DBeaver, o falta el `GRANT` del paso 1 |
| `Unknown database 'argos'` | No has ejecutado el script de creación |
| La API responde 401 | La `API_KEY` del NodeMCU o de `pruebas.http` no es la del `.env` |
| La API responde 400 | El dato no es de tu nodo o el valor es imposible; el mensaje dice cuál |
| El NodeMCU no llega a la API (`-1`) | IP equivocada, redes distintas, firewall o la API está apagada |
| Tus indicadores salen vacíos | Falta ejecutar `datos_prueba_Equipo2.sql` |
