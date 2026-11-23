# Cambio opcional en el central: mostrar el silencio del buzzer en el dashboard

De: Iván Acosta · 22-nov-2026. Para pasárselo tal cual al agente de Claude de José María.

## Contexto

El dashboard nuevo (`servidor/web-dashboard`, se publica en `servidor/web`) lee todo de `GET /panel/datos`. Hoy esa respuesta no dice si el buzzer del nodo dht está silenciado, así que el dashboard solo puede mostrar «Alarma del cuarto activa» o «Alarma en reposo» según las alertas abiertas. Con este cambio podrá mostrar «Alarma silenciada hasta las HH:MM».

**No es urgente ni obligatorio.** Sin el cambio el dashboard funciona igual; solo no muestra el silencio.

## Tamaño y riesgo

- Un solo archivo: `servidor/central/central.js`. Una consulta de solo lectura y un campo nuevo en la respuesta (unas 10 líneas).
- No toca `motor.js`, ni las alertas, ni MQTT, ni `servidor/api-rest`, ni la base de datos.
- El panel anterior y n8n no se ven afectados: solo se agrega un campo que ellos no leen.
- **Hay que reiniciar el central** para que tome el cambio (Ctrl+C y `npm start` en su terminal; unos segundos). No se pierden datos: los nodos escriben en sus APIs, y el motor retoma desde `central_ultimo_evento`. Conviene hacerlo cuando no haya una alerta abierta.

## El cambio

En `leerPanel(horas)`, junto a las otras consultas (por ejemplo después de la de `porTipo`), agregar:

```js
  // Ultima accion manual del buzzer del dht (el boton: silencio de 30 min, o quitar el silencio).
  const [[buzzer]] = await pool.query(
    `SELECT ac.comando, ac.origen, ac.duracion_s, ac.fecha_hora
     FROM AccionControl ac JOIN Actuador a ON a.id_actuador = ac.id_actuador
     WHERE a.id_nodo = 'dht' AND a.tipo = 'buzzer' AND ac.origen = 'manual'
     ORDER BY ac.fecha_hora DESC, ac.id_accion DESC LIMIT 1`
  );
```

Y en el objeto que devuelve `leerPanel`, agregar el campo:

```js
    buzzer: buzzer ?? null,
```

## Lo que hay que verificar antes de aplicarlo

1. Que el firmware del dht registre el silencio como `POST /api/acciones` con `actuador: "buzzer"`, `comando: "off"`, `origen: "manual"`, `duracion_s: 1800` (así lo documenta el comentario de `servidor/api-rest/RestApi-Equipo2-A01669847.js`, línea 109). `[POR CONFIRMAR]` con una fila real de `AccionControl`.
2. Cómo se registra **quitar** el silencio (segunda pulsación larga). El dashboard supone `comando: "on"`, `origen: "manual"`. `[POR CONFIRMAR]`
3. Que la consulta use el índice `idx_accion_actuador_fecha` (es una fila; no debería pesar).

## Cómo lo usa el dashboard

Si `buzzer.comando === "off"`, `buzzer.origen === "manual"` y `ahora < fecha_hora + duracion_s`, muestra «Alarma silenciada hasta las HH:MM». En cualquier otro caso (o si el campo no existe) se comporta como hoy.

## Prueba

Con el central reiniciado: `curl http://localhost:3000/panel/datos?horas=1` debe traer `"buzzer": null` o un objeto con `comando`, `origen`, `duracion_s` y `fecha_hora`. Silenciar el buzzer en el nodo dht y confirmar que el objeto cambia.
