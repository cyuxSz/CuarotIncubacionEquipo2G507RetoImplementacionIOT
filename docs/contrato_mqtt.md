# Contrato MQTT de Argos

Broker de la demo: `broker.hivemq.com:1883` (público). Todos los topics van con el prefijo **`argos-eq2/`** para no chocar con otros equipos. Debe coincidir en `firmware/include/nodo_comun.h` (`TOPIC_RAIZ`) y en `servidor/central/motor.js`.

La configuración de Mosquitto propio, con usuarios y ACL, está en `servidor/mosquitto/`. Sirve para la instalación final en el invernadero.

- El usuario MQTT de cada nodo es su id, que también es el sufijo del topic.
- El client id es `argos-eq2-nodo-<id>`.
- El keep-alive es de 45 s.

| Topic (sin prefijo) | Dirección | Payload | QoS / retenido |
|---|---|---|---|
| `invernadero/telemetria/{nodo}` | nodo → servidor | `{"lecturas":[{"parametro":"temperatura","valor":25.4,"unidad":"C"}]}` | 0 / no |
| `invernadero/evento/{nodo}` | nodo → servidor | `{"tipo":"golpe","magnitud":1.8}` (`movimiento`, `golpe`, `puerta_abierta`, `puerta_cerrada`, `sensor_error`) | 0 / no |
| `invernadero/estado/{nodo}` | nodo / LWT | `{"estado":"online","reset_reason":"Power on","uptime_s":12,"rssi":-62}`; LWT `{"estado":"offline"}` | 1 / sí |
| `invernadero/cmd/alarma` | central → `dht` | `on` / `off`, repetido cada 60 s | 0 / no |
| `invernadero/cmd/silenciar` | `dht` o tablero → servidor | `{"minutos":30}` | 0 / no |
| `invernadero/alertas` | central → dashboard | `{"evento":"abierta"\|"cerrada"\|"grave","id_alerta","id_nodo","tipo","valor","ts"}` | 0 / no |

## Frecuencias

| Nodo | Cuándo publica |
|---|---|
| Todos | Latido cada 60 s (`"parametro":"latido"`) |
| `dht` | Cada 30 s |
| `luz` | Muestrea cada 5 s y publica el promedio cada 60 s |
| `pir`, `puerta`, `acel` | Por evento |

Las lecturas y los eventos se guardan por HTTP POST en la API REST de cada nodo. MQTT se usa para el tiempo real: estado y LWT, `cmd/alarma`, el silencio y el dashboard en vivo.
