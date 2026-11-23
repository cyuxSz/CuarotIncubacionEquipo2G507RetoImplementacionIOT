# Cambio en el central: silencio del buzzer en el dashboard (22-nov-2026)

José María García Sánchez (A00843900) · Equipo 2 · respuesta a `PARA_JOSE_MARIA_cambio_central.md` (Iván Acosta)

## Qué se pidió

Que `GET /panel/datos` diga si el buzzer del nodo dht está silenciado, para que el dashboard nuevo pueda mostrar «Alarma silenciada hasta las HH:MM». Era opcional y de un solo archivo.

## Qué se hizo

**Archivo:** solo `servidor/central/central.js`, en `leerPanel(horas)`. Son unas 10 líneas.

1. Una consulta de solo lectura: la última acción **manual** del buzzer del dht.

   ```js
   const [[buzzer]] = await pool.query(
     `SELECT ac.comando, ac.origen, ac.duracion_s, ac.fecha_hora
      FROM AccionControl ac JOIN Actuador a ON a.id_actuador = ac.id_actuador
      WHERE a.id_nodo = 'dht' AND a.tipo = 'buzzer' AND ac.origen = 'manual'
      ORDER BY ac.fecha_hora DESC, ac.id_accion DESC LIMIT 1`
   );
   ```

2. Un campo nuevo en la respuesta: `buzzer: buzzer ?? null`.

**No se tocó:** `motor.js`, las alertas, MQTT, `servidor/api-rest` ni la base de datos. El panel actual y n8n siguen igual, porque no leen ese campo.

## Lo que estaba «por confirmar»

Confirmado en el firmware (`firmware/arduino_ide/argos_dht/argos_dht.ino`):

| Acción del botón | Lo que registra (`POST /api/acciones`) |
|---|---|
| Silenciar (pulsación larga) | `buzzer`, `off`, `manual`, `duracion_s: 1800` (línea 101) |
| Quitar el silencio (segunda pulsación larga) | `buzzer`, `on`, `manual`, sin duración (línea 95) |

## Cómo se probó

- `node --check central.js` → sintaxis válida.
- La consulta se corrió contra la base real antes de reiniciar.
- Se reinició el central a las **14:12** (Monterrey). Retomó sus 2 alertas abiertas y se volvió a conectar a MQTT.
- `GET /panel/datos` en local **y por el túnel del central** trae:

  ```json
  "buzzer": {"comando":"off","origen":"manual","duracion_s":1800,"fecha_hora":"2026-11-22T20:10:14.000Z"}
  ```

  Ese registro es el silencio hecho con el botón del nodo a las 14:10, que dura hasta las 14:40.
- El túnel del central no se reinició y **conserva su URL**.

## Para el dashboard

- `fecha_hora` viene en **UTC** (termina en `Z`). Para mostrar la hora de Monterrey hay que convertirla (UTC−6).
- Silenciado = `buzzer.comando === "off"` y `ahora < fecha_hora + duracion_s`. Si `buzzer` es `null` o `comando` es `"on"`, no hay silencio.
