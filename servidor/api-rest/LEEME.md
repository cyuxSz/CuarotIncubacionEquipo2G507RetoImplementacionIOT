# API REST de un nodo (Equipo 2, Etapa 3)

Parte de la carpeta `api-rest` de la clase (misma estructura: archivo principal, `db.js`, `middleware/auth.js`, `models/`), adaptada a la base `argos`.

Cada integrante corre **su propia API para su nodo**. El código es el mismo para los cinco: solo cambia `NODO` en el `.env`. Las cinco escriben en la misma base de datos.

| Nodo | Responsable | Puerto | Manda |
|---|---|---|---|
| `dht` | Luis Mendoza | 3001 | mediciones (temperatura, humedad) |
| `luz` | Arianna Téllez | 3002 | mediciones (luz) |
| `pir` | José María García | 3003 | eventos (movimiento) |
| `puerta` | Iván Acosta | 3004 | eventos (puerta_abierta, puerta_cerrada) |
| `acel` | Mía Nieto | 3005 | eventos (golpe) |

## Para usarla con tu nodo

1. **Base de datos.** Ejecuta `docs/bd/etapa3/ScriptCreacionBaseDatos_iot_Equipo2.sql` en DBeaver (Alt+X). Debe quedar la base `argos` con 14 tablas. Después ejecuta `datos_prueba_Equipo2.sql` para cargar los datos de prueba.
2. **Permisos.** Si tu usuario de MySQL no es `root`, dale permiso sobre `argos` (en DBeaver, conectado como `root`; cambia `usertec` por tu usuario):
   ```sql
   GRANT SELECT, INSERT, UPDATE ON argos.* TO 'usertec'@'localhost';
   ```
3. **Configuración.** Copia `.env.example` como `.env` y llena: `NODO` (tu nodo), `DB_PORT`, `DB_USER`, `DB_PASSWORD` (los de tu conexión de DBeaver) y una `API_KEY` que tú inventes.
4. **Nombre del archivo.** Lo hace `node preparar_entrega.js <tu nodo>` del paquete del equipo: renombra la API con tu matrícula y arma tu carpeta de entrega. A mano: renombra el archivo `RestApi-Equipo2-...js`, cambia ese nombre en `"main"` de `package.json` y pon tu nombre en el encabezado.
5. **Arrancar.** Necesitas Node.js 20.6 o más nuevo.
   ```bash
   npm install
   ```
   ```bash
   npm start
   ```
   Debe imprimir `API del nodo '...' en http://localhost:300X` y `Conectado a MySQL`.
6. **Probar sin el NodeMCU.** Abre `pruebas.http` en VS Code (extensión REST Client), pon tu clave y tu puerto, y manda las peticiones.
7. **NodeMCU.** En `secrets.h`: `API_HOST` = IPv4 de tu PC (`ipconfig`), `API_PORT` = el puerto de tu nodo, `API_KEY` = la misma del `.env`. El firewall de Windows debe dejar entrar ese puerto.

## Archivos

| Archivo | Qué hace |
|---|---|
| `RestApi-Equipo2-A01669847.js` | Rutas: recibe las peticiones, valida y responde |
| `config.js` | Lee el `.env` y define qué acepta cada nodo |
| `db.js` | Conexión a MySQL |
| `middleware/auth.js` | Valida la cabecera `x-api-key` |
| `models/nodoModel.js` | Todas las consultas SQL |
| `models/umbralModel.js` | Persistencia e histéresis: abre y cierra alertas |
| `pruebas.http` | Pruebas de cada ruta |

## Rutas

| Método | Ruta | Qué hace | Tabla |
|---|---|---|---|
| POST | `/api/mediciones` | Guarda lecturas (solo `dht` y `luz`) | Medicion, Alerta |
| POST | `/api/eventos` | Guarda un evento | Evento |
| POST | `/api/acciones` | Guarda un cambio del LED rojo o del buzzer | AccionControl |
| POST | `/api/latido` | Marca al nodo como vivo | EstadoNodo |
| GET | `/api/comandos` | Instrucciones para el nodo: alarma `on`/`off` y umbrales | Alerta, Umbral |
| GET | `/api/datetime` | Fecha y hora del servidor (UTC) | — |
| GET | `/api/estado` | Ficha del nodo y su último valor | Nodo, EstadoNodo, Medicion |
| GET | `/api/mediciones?parametro=` | Historial (solo `dht` y `luz`) | Medicion |
| GET | `/api/eventos` | Últimos eventos | Evento |
| GET | `/api/acciones` | Últimos eventos de actuación | AccionControl |
| GET | `/api/alertas?estado=activa\|todas` | Alertas del nodo | Alerta |

Respuestas: 200/201 bien, 400 dato inválido, 401 clave incorrecta, 404 ruta inexistente, 500 fallo de la base de datos.

## Umbrales, persistencia e histéresis

- Un sensor puede medir varios parámetros, y cada parámetro tiene su rango. El DHT22 tiene dos filas en `Umbral`: temperatura (22–28 °C) y humedad (40–60 %). No puede haber dos umbrales del mismo parámetro (llave única).
- **Persistencia (3):** la alerta se abre a la tercera lectura seguida fuera de rango.
- **Histéresis (0.5 °C, 2 %):** la alerta se cierra hasta que el valor vuelve claramente al rango (menos de 27.5 °C), también con tres lecturas seguidas. Entre 27.5 y 28 °C no cambia nada.
- Al abrir o cerrar una alerta de temperatura o humedad, la API registra la orden al buzzer en `AccionControl` con origen `alerta`.

Probado el 13-nov-2026 con MySQL local y los cinco nodos sobre el script del equipo (peticiones con curl, sin NodeMCU).
