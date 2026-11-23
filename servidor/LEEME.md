# Servidor de Argos: cómo levantarlo en una laptop (sin Docker)

Actualizado el 19-nov-2026 (con los arreglos de la auditoría). Probado sin hardware con `servidor/pruebas/` (54 comprobaciones). **No** probado: nodos reales, Mosquitto con usuarios y ACL, n8n, `arrancar.ps1` con sus ventanas.

## Qué corre

| Pieza | Carpeta | Puerto | Para qué |
|---|---|---|---|
| API de cada nodo (5 procesos, mismo código) | `api-rest/` | 3001 dht · 3002 luz · 3003 pir · 3004 puerta · 3005 acel | Recibe los POST del NodeMCU y guarda en MySQL. Abre y cierra las alertas de temperatura y humedad |
| Servicio central | `central/` | 3000 | Panel web, alertas que cruzan nodos (puerta abierta de más, nodo caído, golpe, falla de sensor, movimiento fuera de horario), `cmd/alarma` por MQTT y avisos graves para n8n |
| MySQL | — | 3306 | Base `argos` (`docs/bd/esquema.sql`) |
| Mosquitto (opcional para la demo) | `mosquitto/` | 1883 | Estado en vivo (LWT) y `cmd/alarma` |
| n8n (opcional) | `n8n/` | 5678 | Manda los avisos graves por Telegram y WhatsApp |

Sin Mosquitto y sin n8n el sistema ya guarda datos, abre alertas y muestra el panel. El buzzer del `dht` suena igual, porque tiene su alarma local y además pregunta a su API.

## Pasos (una sola vez)

1. **Base de datos.** En MySQL Workbench o DBeaver ejecuta `docs/bd/esquema.sql`. Crea un usuario para las API con permisos `SELECT, INSERT, UPDATE` sobre `argos.*`.
2. **Configuración.** Copia `api-rest/.env.example` como `api-rest/.env` y `central/config.example` como `central/.env`. Llena en los dos el usuario y la contraseña de MySQL y la misma `API_KEY` (invéntala; es la que va en el `secrets.h` de los nodos). En `api-rest/.env` deja `NODO=dht`: el arranque lo cambia solo para cada API.
3. **Dependencias.** `npm install` dentro de `api-rest/` y dentro de `central/`.
4. **Cortafuegos de Windows.** La primera vez que arranque, Windows pregunta si permite a Node.js recibir conexiones: acepta en redes privadas. Sin eso los NodeMCU no llegan a la PC.

## Arrancar

```powershell
powershell -ExecutionPolicy Bypass -File servidor\arrancar.ps1
```

Abre 6 ventanas (5 API y el central). Panel: <http://localhost:3000>. Desde otro equipo de la misma red: `http://IP-DE-LA-PC:3000`.

- Si un proceso se cae, su ventana lo relanza sola a los 3 s. Para detenerlo, cierra la ventana.
- Si ya hay algo en los puertos 3000 a 3005, el arranque se niega: cierra las ventanas viejas de Argos. Dos copias del central duplicarían las alertas.
- **No hagas clic dentro de las ventanas.** En la consola clásica de Windows, seleccionar texto congela el proceso hasta que presionas Esc.
- Sin Mosquitto el LED verde de los nodos queda fijo mientras su API responda (firmware del 19-nov en adelante).

**Mosquitto en Windows:** usa `mosquitto/mosquitto.windows.conf` (el `mosquitto.conf` es el de Docker). Las instrucciones están al inicio de ese archivo. Sin probar.

En el `secrets.h` de cada nodo: `API_HOST` = IP de la PC en el WiFi (sale con `ipconfig`), `API_PORT` = el puerto de su nodo, `API_KEY` = la del `.env`.

## Probar sin hardware

- **Los 5 nodos falsos, con teclas para provocar cosas** (calor, puerta, movimiento, golpe, falla, nodo apagado): `node servidor/simulador_nodos.mjs TU_API_KEY --rapido`. Con `--solo=acel,luz` simula solo esos y los demás pueden ser reales: sirve de respaldo en la Expo si una caja falla. Los datos quedan guardados como si fueran reales.
- Un nodo falso: `node api-rest/simulador_dht.mjs TU_API_KEY`.
- Todo el servidor: `servidor/pruebas/` (lee las instrucciones al inicio de `prueba_integracion.js`). **Usa una base de pruebas aparte**, nunca la del invernadero: la prueba cambia `Configuracion` y mete datos falsos.

## Avisos graves (n8n)

El servicio central marca una alerta como grave cuando dura más que su límite y crea su fila en `Notificacion`. n8n no decide nada: solo lee los pendientes, manda el mensaje y los marca.

| Alerta | Se abre | Se vuelve grave |
|---|---|---|
| Temperatura o humedad fuera de rango | 3 lecturas seguidas (90 s) | a los 15 min |
| Nodo sin reportar | 150 s sin datos | a los 15 min |
| Puerta abierta | `puerta_abierta_max_s` (120 s) | a los 10 min |

Los límites de "grave" se cambian sin tocar código: agrega a la tabla `Configuracion` la clave `grave_s_<tipo>` con los segundos (por ejemplo `grave_s_puerta_abierta` = `300`).

**Golpe y movimiento fuera de horario** son alertas instantáneas y por omisión solo salen en el panel. Para que también manden mensaje, agrega a `Configuracion` la clave `avisar_golpe` o `avisar_movimiento_fuera_de_horario` con valor `1`. Mandan como mucho un aviso cada 10 min por nodo y tipo.

El servicio central guarda en `Configuracion` la clave `central_ultimo_evento` (hasta qué evento revisó). No la borres: gracias a ella, si el central se reinicia no pierde los eventos que llegaron mientras tanto (hasta 10 min atrás).

## Modo demo (Expo, fuera del cuarto de incubación)

Con los rangos reales (22–28 °C, 40–60 % HR) el buzzer sonaría solo en una sala con aire acondicionado. Para exhibir:

1. En el sketch del `dht`, quita las diagonales de `// #define MODO_DEMO` (al inicio) y flashea. Usa rangos amplios y lee cada 5 s, así la alarma reacciona en 15 s.
2. Pon los **mismos** rangos en la base, porque la API también ordena la alarma:

```sql
UPDATE Umbral u JOIN Parametro p ON p.id_parametro = u.id_parametro SET u.minimo = 15, u.maximo = 30 WHERE p.nombre = 'temperatura';
UPDATE Umbral u JOIN Parametro p ON p.id_parametro = u.id_parametro SET u.minimo = 20, u.maximo = 80 WHERE p.nombre = 'humedad';
```

Los rangos de demo (15–30 °C, 20–80 % HR) son una propuesta `[POR CONFIRMAR]`: si los cambian, cámbienlos en `firmware/include/alarma_dht.h` y en la tabla. Para regresar al cuarto real: vuelve a comentar la línea, flashea y regresa la tabla a 22–28 y 40–60.

En el nodo `dht`, una pulsación larga silencia el buzzer 30 min y **otra pulsación larga quita el silencio**, para poder repetir la demostración.

Para usar n8n: importa `n8n/avisos_graves.json` (menú ⋯ → Import from file), llena el nodo **Configuracion** (API, bot de Telegram, CallMeBot) y actívalo. Manda de 7:00 a 22:00, hora de Monterrey; lo que pase de noche sale junto a las 7:00. Si un envío falla, el aviso sigue pendiente y se reintenta al minuto; un fallo de Telegram ya no detiene el envío por WhatsApp (ni al revés). **No exportes el flujo a git con los valores llenos.** El JSON y su lógica se revisaron fuera de n8n; falta importarlo y probarlo en n8n de verdad.

## Si algo falla

| Síntoma | Causa probable |
|---|---|
| El nodo imprime `[api] ... -> -1 connection refused` | `API_HOST` o `API_PORT` mal, la API no está corriendo, o el cortafuegos bloquea a Node.js |
| `[api] ... -> 401` | `API_KEY` distinta en `secrets.h` y en el `.env` |
| `[api] ... -> 400 esta API es del nodo 'x'` | El nodo apunta al puerto de otra API |
| La API dice `Error conectando a MySQL` | Usuario, contraseña o puerto del `.env` |
| El panel dice "Sin respuesta del servidor" | El servicio central no está corriendo |
| Un nodo sale "Sin conexión" aunque está prendido | Lleva más de 150 s sin llegar a su API: revisar su monitor serie |

`docker-compose.yml` y `api/` son la versión anterior (una sola API en Docker); no se actualizaron para las 5 API.
