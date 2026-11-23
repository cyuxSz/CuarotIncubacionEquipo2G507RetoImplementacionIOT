/**
 * Argos — motor central de alertas. Trabaja SOLO leyendo la base de datos, cada REVISION_MS.
 *
 * Por que existe: cada nodo tiene su propia API (servidor/api-rest, puertos 3001-3005) y esa API solo
 * conoce a su nodo. Lo que cruza nodos o depende del tiempo no lo puede hacer ninguna de las cinco:
 *
 *   nodo_sin_reporte             el nodo lleva mas de SIN_REPORTE_S sin mandar nada; se cierra al volver
 *   puerta_abierta               la puerta lleva abierta mas de Configuracion.puerta_abierta_max_s
 *   sensor_falla                 llego un evento sensor_error; se cierra con el siguiente dato valido del nodo
 *   golpe                        evento golpe con magnitud >= Configuracion.umbral_golpe_g (instantanea)
 *   movimiento_fuera_de_horario  evento movimiento marcado fuera_de_horario por la API del pir (instantanea)
 *
 * Las alertas de temperatura y humedad las abre y cierra la API del dht (models/umbralModel.js); aqui
 * solo se anuncian. Como todo sale de la BD, da igual que API escribio el dato.
 *
 * MQTT (si hay MQTT_URL; sin el todo lo demas sigue funcionando):
 *   publica  argos-eq2/invernadero/cmd/alarma  "on" mientras haya una alerta con buzzer (repetido cada 60 s; el dht
 *            da por buena la orden 150 s) y "off" al cerrarse la ultima
 *   publica  argos-eq2/invernadero/alertas     {"evento":"abierta"|"cerrada"|"grave","id_alerta","id_nodo","tipo","valor","ts"}
 *   escucha  argos-eq2/invernadero/estado/+    online/offline (LWT) -> EstadoNodo.estado
 *
 * Avisos graves (CLAUDE.md 1b): cuando una alerta lleva activa mas de su limite se crea su fila en
 * Notificacion (enviada = FALSE). n8n las lee con GET /api/notificaciones/pendientes, manda WhatsApp y
 * Telegram de 7:00 a 22:00 y las marca. Limites por omision abajo; se cambian sin tocar codigo agregando
 * a Configuracion la clave  grave_s_<tipo>  (por ejemplo grave_s_puerta_abierta = 300).
 */
const mqtt = require("mqtt");

// Broker publico (broker.hivemq.com): el prefijo evita chocar con otros equipos. Igual que TOPIC_RAIZ de firmware/include/nodo_comun.h.
const TOPIC_RAIZ = "argos-eq2/invernadero/";
const REPETIR_ALARMA_MS = 60000; // contrato MQTT: cmd/alarma se repite cada 60 s
const SIN_REPORTE_S = 150;       // 2.5 latidos de 60 s sin saber del nodo = caido
const GRAVE_S = { temperatura: 900, humedad: 900, nodo_sin_reporte: 900, puerta_abierta: 600 };

function crearMotor(pool, opciones = {}) {
  const REVISION_MS = opciones.revisionMs ?? 5000;
  let config = {};
  let cliente = null;
  let ultimoEvento = 0;         // id del ultimo Evento ya revisado
  let conocidas = new Map();    // alertas activas en la revision anterior: id_alerta -> fila
  let sonando = false;          // ya se publico cmd/alarma on
  let ultimaRepeticion = 0;
  let ocupado = false;
  let activasClave = new Set(); // "nodo/tipo" de las alertas activas: evita repetir el INSERT cada 5 s
  let guardado = 0;             // ultimoEvento ya escrito en Configuracion

  const VALOR_MAX = 999999;     // Alerta.valor es DECIMAL(8,2): un numero mayor hace fallar el INSERT
  const AVISO_INSTANTANEA_S = 600; // alertas instantaneas con aviso: como mucho uno cada 10 min por nodo y tipo
  const CLAVE_ULTIMO = "central_ultimo_evento";

  const log = (...a) => console.log(new Date().toISOString(), "[motor]", ...a);

  function publicar(topic, mensaje) {
    if (cliente?.connected) cliente.publish(topic, mensaje, { qos: 0, retain: false });
  }
  function anunciar(evento, a) {
    publicar(TOPIC_RAIZ + "alertas", JSON.stringify({
      evento, id_alerta: a.id_alerta, id_nodo: a.id_nodo, tipo: a.tipo, valor: a.valor ?? null, ts: new Date().toISOString(),
    }));
  }

  /** Abre una alerta. Si ya hay una activa del mismo nodo y tipo no hace nada (una por episodio). */
  async function abrir(nodo, tipo, valor, instantanea = false) {
    if (!instantanea && activasClave.has(`${nodo}/${tipo}`)) return; // ya esta activa: no gasta un id_alerta
    if (typeof valor === "number") valor = Math.min(valor, VALOR_MAX);
    let id;
    try {
      const [r] = await pool.query(
        `INSERT INTO Alerta (id_nodo, id_umbral, tipo, valor, ts_inicio, ts_fin)
         VALUES (?, NULL, ?, ?, UTC_TIMESTAMP(), ${instantanea ? "UTC_TIMESTAMP()" : "NULL"})`,
        [nodo, tipo, valor]
      );
      id = r.insertId;
    } catch (e) {
      if (e.code === "ER_DUP_ENTRY") { activasClave.add(`${nodo}/${tipo}`); return; } // ya estaba activa
      throw e;
    }
    log(`ABIERTA #${id} ${nodo}/${tipo} valor=${valor}`);
    if (!instantanea) { activasClave.add(`${nodo}/${tipo}`); return; }
    // Instantanea: nunca aparece como activa, se anuncia aqui (las demas, al comparar con la revision anterior).
    const a = { id_alerta: id, id_nodo: nodo, tipo, valor };
    anunciar("abierta", a);
    anunciar("cerrada", a);
    // Aviso por mensaje solo si se pidio en Configuracion (avisar_golpe = 1, avisar_movimiento_fuera_de_horario = 1).
    if (config[`avisar_${tipo}`] !== "1") return;
    const [[previo]] = await pool.query(
      `SELECT COUNT(*) AS n FROM Notificacion n JOIN Alerta al ON al.id_alerta = n.id_alerta
       WHERE al.id_nodo = ? AND al.tipo = ? AND al.id_alerta <> ? AND al.ts_inicio >= UTC_TIMESTAMP() - INTERVAL ? SECOND`,
      [nodo, tipo, id, AVISO_INSTANTANEA_S]
    );
    if (previo.n) return;
    await pool.query("INSERT IGNORE INTO Notificacion (id_alerta, canal) VALUES (?, 'telegram'), (?, 'whatsapp')", [id, id]);
    log(`AVISO #${id} ${nodo}/${tipo}`);
  }

  async function cerrar(nodo, tipo) {
    activasClave.delete(`${nodo}/${tipo}`);
    const [r] = await pool.query(
      "UPDATE Alerta SET ts_fin = UTC_TIMESTAMP() WHERE id_nodo = ? AND tipo = ? AND ts_fin IS NULL", [nodo, tipo]);
    if (r.affectedRows) log(`CERRADA ${nodo}/${tipo}`);
  }

  // ─── reglas ───────────────────────────────────────────────────────────────
  async function eventosNuevos() {
    const [evs] = await pool.query(
      `SELECT e.id_evento, s.id_nodo, e.tipo, e.magnitud, e.fuera_de_horario
       FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor WHERE e.id_evento > ? ORDER BY e.id_evento`,
      [ultimoEvento]
    );
    const minimoGolpe = Number(config.umbral_golpe_g);
    for (const e of evs) {
      if (e.tipo === "sensor_error") await abrir(e.id_nodo, "sensor_falla", null);
      if (e.tipo === "golpe" && (e.magnitud === null || !Number.isFinite(minimoGolpe) || e.magnitud >= minimoGolpe))
        await abrir(e.id_nodo, "golpe", e.magnitud, true);
      if (e.tipo === "movimiento" && e.fuera_de_horario) await abrir(e.id_nodo, "movimiento_fuera_de_horario", null, true);
      if (e.tipo === "puerta_cerrada") await cerrar(e.id_nodo, "puerta_abierta");
      ultimoEvento = e.id_evento;
    }
    // Se guarda hasta donde se reviso: si el servicio se reinicia, sigue desde ahi y no pierde eventos.
    if (ultimoEvento !== guardado) {
      await pool.query("INSERT INTO Configuracion (clave, valor) VALUES (?, ?) ON DUPLICATE KEY UPDATE valor = VALUES(valor)",
        [CLAVE_ULTIMO, String(ultimoEvento)]);
      guardado = ultimoEvento;
    }
  }

  /** El sensor volvio: hay una medicion o un evento que no es de error posterior a la falla. */
  async function fallasResueltas() {
    const [f] = await pool.query(
      `SELECT a.id_nodo FROM Alerta a
       WHERE a.tipo = 'sensor_falla' AND a.ts_fin IS NULL AND (
         EXISTS (SELECT 1 FROM Medicion m JOIN Sensor s ON s.id_sensor = m.id_sensor
                 WHERE s.id_nodo = a.id_nodo AND m.fecha_hora > a.ts_inicio)
         OR EXISTS (SELECT 1 FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor
                    WHERE s.id_nodo = a.id_nodo AND e.tipo <> 'sensor_error' AND e.fecha_hora > a.ts_inicio))`
    );
    for (const { id_nodo } of f) await cerrar(id_nodo, "sensor_falla");
  }

  async function nodosSinReporte() {
    const [nodos] = await pool.query(
      `SELECT id_nodo, estado, TIMESTAMPDIFF(SECOND, ultimo_reporte, UTC_TIMESTAMP()) AS hace_s
       FROM EstadoNodo WHERE ultimo_reporte IS NOT NULL`
    );
    for (const { id_nodo, estado, hace_s } of nodos) {
      if (hace_s > SIN_REPORTE_S) {
        await abrir(id_nodo, "nodo_sin_reporte", hace_s);
        // Sin MQTT no llega el LWT: el estado se corrige aqui para que el panel no muestre "online" a un nodo caido.
        if (estado === "online") await pool.query("UPDATE EstadoNodo SET estado = 'offline' WHERE id_nodo = ?", [id_nodo]);
      } else {
        await cerrar(id_nodo, "nodo_sin_reporte");
      }
    }
  }

  async function puertaAbierta() {
    const maxPuerta = Number(config.puerta_abierta_max_s);
    if (!Number.isFinite(maxPuerta)) return;
    const [[ultimo]] = await pool.query(
      `SELECT e.tipo, TIMESTAMPDIFF(SECOND, e.fecha_hora, UTC_TIMESTAMP()) AS hace_s
       FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor
       WHERE s.id_nodo = 'puerta' AND e.tipo IN ('puerta_abierta', 'puerta_cerrada')
       ORDER BY e.fecha_hora DESC, e.id_evento DESC LIMIT 1`
    );
    if (ultimo?.tipo === "puerta_abierta" && ultimo.hace_s > maxPuerta) await abrir("puerta", "puerta_abierta", ultimo.hace_s);
    if (ultimo?.tipo === "puerta_cerrada") await cerrar("puerta", "puerta_abierta");
  }

  /** Segundos que lleva el problema (no la alerta): las de puerta y nodo caido se abren con retraso. */
  function edadProblema(a) {
    if (a.tipo === "nodo_sin_reporte") return a.edad_s + SIN_REPORTE_S;
    if (a.tipo === "puerta_abierta") return a.edad_s + (Number(config.puerta_abierta_max_s) || 0);
    return a.edad_s;
  }

  /** Compara las alertas activas con las de la revision anterior: anuncia, ordena el buzzer y escala a grave. */
  async function anunciarCambios(primera) {
    const [activas] = await pool.query(
      `SELECT a.id_alerta, a.id_nodo, a.tipo, a.valor, COALESCE(u.activa_buzzer, 0) AS buzzer,
              TIMESTAMPDIFF(SECOND, a.ts_inicio, UTC_TIMESTAMP()) AS edad_s,
              (SELECT COUNT(*) FROM Notificacion n WHERE n.id_alerta = a.id_alerta) AS avisos
       FROM Alerta a LEFT JOIN Umbral u ON u.id_umbral = a.id_umbral WHERE a.ts_fin IS NULL`
    );
    const ahora = new Map(activas.map((a) => [a.id_alerta, a]));
    if (!primera) {
      for (const [id, a] of ahora) if (!conocidas.has(id)) anunciar("abierta", a);
      for (const [id, a] of conocidas) if (!ahora.has(id)) { anunciar("cerrada", a); log(`anunciada cerrada #${id} ${a.id_nodo}/${a.tipo}`); }
    }
    conocidas = ahora;
    activasClave = new Set(activas.map((a) => `${a.id_nodo}/${a.tipo}`));

    const hayBuzzer = activas.some((a) => a.buzzer);
    if (hayBuzzer && (!sonando || Date.now() - ultimaRepeticion >= REPETIR_ALARMA_MS)) {
      publicar(TOPIC_RAIZ + "cmd/alarma", "on");
      ultimaRepeticion = Date.now();
    }
    if (!hayBuzzer && sonando) publicar(TOPIC_RAIZ + "cmd/alarma", "off");
    sonando = hayBuzzer;

    for (const a of activas) {
      const limite = Number(config[`grave_s_${a.tipo}`]) || GRAVE_S[a.tipo];
      if (!limite || a.avisos > 0 || edadProblema(a) < limite) continue;
      await pool.query(
        "INSERT IGNORE INTO Notificacion (id_alerta, canal) VALUES (?, 'telegram'), (?, 'whatsapp')", [a.id_alerta, a.id_alerta]);
      log(`GRAVE #${a.id_alerta} ${a.id_nodo}/${a.tipo}: lleva ${edadProblema(a)} s`);
      anunciar("grave", a);
    }
  }

  async function revisar(primera = false) {
    if (ocupado) return; // la revision anterior sigue en curso (BD lenta): no se enciman
    ocupado = true;
    try {
      const [c] = await pool.query("SELECT clave, valor FROM Configuracion");
      config = Object.fromEntries(c.map((r) => [r.clave, r.valor]));
      // Cada regla por separado: si una falla, las demas siguen (antes un error en una dejaba sin alertas a todas).
      for (const regla of [eventosNuevos, fallasResueltas, nodosSinReporte, puertaAbierta]) {
        try { await regla(); } catch (e) { log(`error en ${regla.name}:`, e.message); }
      }
      await anunciarCambios(primera);
    } finally {
      ocupado = false;
    }
  }

  // ─── MQTT ─────────────────────────────────────────────────────────────────
  function conectarMqtt() {
    if (cliente) return; // una sola conexion aunque iniciar() se reintente (dos con el mismo clientId se tumban entre si)
    const url = process.env.MQTT_URL;
    if (!url) { log("sin MQTT_URL: las alertas quedan en la BD y en el panel (no se publica cmd/alarma)"); return; }
    cliente = mqtt.connect(url, {
      username: process.env.MQTT_USER,
      password: process.env.MQTT_PASSWORD,
      clientId: "argos-central",
      keepalive: 45,
      reconnectPeriod: 5000, // si se cae Mosquitto, reintenta cada 5 s sin tumbar el servicio
    });
    cliente.on("connect", () => { log("conectado a MQTT"); cliente.subscribe(TOPIC_RAIZ + "estado/+"); sonando = false; });
    cliente.on("error", (e) => log("MQTT:", e.message));
    cliente.on("message", (topic, cuerpo) => {
      const nodo = topic.split("/").pop();
      let estado;
      try { estado = JSON.parse(cuerpo.toString()).estado; } catch { return; }
      if (estado !== "online" && estado !== "offline") return;
      pool.query("UPDATE EstadoNodo SET estado = ? WHERE id_nodo = ?", [estado, nodo])
        .catch((e) => log("no se pudo guardar el estado:", e.message));
    });
  }

  async function iniciar() {
    // Sigue desde el ultimo evento revisado antes de apagarse (Configuracion), pero nunca revisa eventos de
    // hace mas de 10 min: una alerta instantanea de un golpe de ayer, fechada hoy, confundiria.
    const [[m]] = await pool.query(
      `SELECT COALESCE(MAX(id_evento), 0) AS ultimo,
              COALESCE(MAX(CASE WHEN fecha_hora < UTC_TIMESTAMP() - INTERVAL 10 MINUTE THEN id_evento END), 0) AS viejo
       FROM Evento`);
    const [[g]] = await pool.query("SELECT valor FROM Configuracion WHERE clave = ?", [CLAVE_ULTIMO]);
    guardado = g ? Number(g.valor) || 0 : -1;
    ultimoEvento = g ? Math.min(m.ultimo, Math.max(guardado, m.viejo)) : m.ultimo;
    conectarMqtt();
    await revisar(true);
    setInterval(() => revisar().catch((e) => log("error en la revision:", e.message)), REVISION_MS);
    log(`motor listo: revisa cada ${REVISION_MS / 1000} s, ${conocidas.size} alertas activas`);
  }

  return { iniciar, revisar };
}

module.exports = { crearMotor, SIN_REPORTE_S, GRAVE_S };
