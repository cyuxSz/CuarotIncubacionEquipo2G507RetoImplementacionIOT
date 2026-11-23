# Botón "Silenciar alarma" en el tablero (22-nov-2026, Iván Acosta)

El botón físico del nodo dht se rompió y se usará el nodo de Luis sin botón. El silencio ahora se manda desde el tablero.

## Cómo funciona

1. El tablero muestra el botón **"Silenciar alarma 30 min"** junto a "Alarma del cuarto activa".
2. Al confirmar, el navegador publica por MQTT (WebSocket seguro, `wss://broker.hivemq.com:8884/mqtt`) en
   `argos-eq2/invernadero/cmd/silenciar` el mensaje `{"minutos":30,"origen":"tablero"}`.
3. El nodo dht (firmware v3) recibe la orden, silencia el buzzer 30 min y registra la acción con
   `POST /api/acciones` (`buzzer`, `off`, `manual`, 1800 s), igual que hacía el botón físico.
4. El tablero ya leía ese registro (campo `buzzer` de `/panel/datos`) y cambia solo a "Alarma silenciada hasta las HH:MM".

No se tocó `central.js`, `motor.js`, las API ni la base de datos. **No hay que reiniciar nada en el servidor.**

## Qué instalar

| Dónde | Qué | Archivo |
|---|---|---|
| Servidor (José María) | Reemplazar `servidor/web/index.html` del tablero nuevo (guardar copia del actual) | `para_el_servidor/index.html` |
| Nodo dht (Arduino IDE) | Cargar el firmware v3 (lleva su `secrets.h` aparte) | `../argos_dht_v3/argos_dht/argos_dht.ino` |

`para_el_servidor/index.html` es el `index.html` que estaba en vivo el 22-nov a las 21:45 más el bloque de
`boton_silenciar.html` antes de `</body>`. Si el `index.html` del servidor cambió después, basta pegar ese bloque.

## Qué se probó y qué no

- Probado: el botón aparece en el tablero (servidor local que sirve el index nuevo y toma lo demás del tablero real).
- Probado: al pulsarlo, el mensaje llega al broker (un segundo cliente suscrito lo recibió).
- Probado: el firmware v3 compila para NodeMCU (391,508 bytes).
- **No probado: el nodo real recibiendo la orden y silenciando.** Falta cargar el v3 y pulsar el botón con la alarma sonando.

## Límites

- Cualquiera que abra el tablero puede silenciar (el tablero es público y el broker también). Pide confirmación.
- Solo funciona si el nodo dht está conectado a MQTT. Sin MQTT no hay respaldo por HTTP.
- El navegador necesita internet para cargar MQTT.js (`unpkg.com`) y llegar al broker por el puerto 8884.
- Si no hay alarma en el nodo, la orden se ignora (igual que el botón).
- La alerta sigue abierta y el LED rojo sigue encendido; solo calla el buzzer.

`proxy_prueba.py`, `index_vivo.html` y `bundle.js` son solo para probar; no van al servidor.
