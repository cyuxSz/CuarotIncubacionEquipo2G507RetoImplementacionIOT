/**
 * Argos — servicio central: panel web + motor de alertas (motor.js) + avisos para n8n.
 *
 * Corre junto a las 5 API de los nodos (servidor/api-rest) sobre la misma base `argos`. No recibe
 * datos de los NodeMCU: solo LEE lo que las API guardaron (y escribe Alerta, Notificacion y EstadoNodo).
 *
 *   GET  /                              el panel (servidor/web/index.html)
 *   GET  /panel/datos?horas=24          todo lo que dibuja el panel, en una sola respuesta (solo lectura, sin clave)
 *   GET  /api/notificaciones/pendientes avisos graves que n8n aun no manda        (pide X-API-Key)
 *   POST /api/notificaciones/enviadas   {"ids":[12,13],"canal":"telegram"}        (pide X-API-Key)
 *
 * Configuracion (archivo .env de esta carpeta, ver .env.example): DB_HOST, DB_PORT, DB_USER, DB_PASSWORD,
 * DB_NAME, API_KEY, PUERTO (3000) y, opcionales, MQTT_URL, MQTT_USER, MQTT_PASSWORD.
 * Todas las fechas van en UTC (ISO 8601 con "Z"); el panel las muestra en hora de Monterrey.
 */
const path = require("path");
const express = require("express");
const mysql = require("mysql2/promise");
const { crearMotor, SIN_REPORTE_S } = require("./motor");

const PUERTO = Number(process.env.PUERTO || 3000);
const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  console.error("Falta API_KEY en el .env: el servicio no arranca sin clave.");
  process.exit(1);
}

const pool = mysql.createPool({
  host: process.env.DB_HOST || "localhost",
  port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME || "argos",
  timezone: "Z",
  decimalNumbers: true,
  connectionLimit: 5,
});
pool.pool.on("connection", (c) => c.query("SET time_zone = '+00:00'"));

const motor = crearMotor(pool, { revisionMs: Number(process.env.REVISION_MS || 5000) });

class ErrorHttp extends Error {
  constructor(codigo, mensaje) { super(mensaje); this.codigo = codigo; }
}
const ruta = (fn) => (req, res, next) => fn(req, res).catch(next);

const app = express();
app.use(express.json({ limit: "10kb" }));
app.use(express.static(path.join(__dirname, "..", "web")));

/** GET /panel/datos: nodos, ultimos valores, alertas, eventos y series para las graficas. */
// Varios navegadores (o celulares del jurado) piden lo mismo cada 5 s: la respuesta se reutiliza un momento
// para que 10 pantallas abiertas cuesten lo mismo que una.
const CACHE_MS = Number(process.env.PANEL_CACHE_MS ?? 2000);
const cache = new Map(); // horas -> { hasta, promesa }
app.get("/panel/datos", ruta(async (req, res) => {
  const horas = Number(req.query.horas ?? 24);
  if (!Number.isInteger(horas) || horas < 1 || horas > 168) throw new ErrorHttp(400, "'horas' debe ser entero entre 1 y 168");
  let c = cache.get(horas);
  if (!c || Date.now() >= c.hasta) {
    c = { hasta: Date.now() + CACHE_MS, promesa: leerPanel(horas) };
    cache.set(horas, c);
    c.promesa.catch(() => cache.delete(horas)); // un error no se queda guardado
  }
  res.set("Cache-Control", "no-store");
  res.json(await c.promesa);
}));

async function leerPanel(horas) {
  const cubeta = Math.max(30, Math.round((horas * 3600) / 288)); // unos 288 puntos por serie, sea cual sea el rango

  const [nodos] = await pool.query(
    `SELECT n.id_nodo, n.descripcion, n.id_caja, c.descripcion AS caja, r.nombre AS responsable, s.modelo AS sensor,
            e.estado, e.ultimo_reporte, e.rssi, e.uptime_s,
            TIMESTAMPDIFF(SECOND, e.ultimo_reporte, UTC_TIMESTAMP()) AS hace_s
     FROM Nodo n
     JOIN Caja c ON c.id_caja = n.id_caja
     JOIN Responsable r ON r.id_responsable = n.id_responsable
     JOIN Sensor s ON s.id_nodo = n.id_nodo
     JOIN EstadoNodo e ON e.id_nodo = n.id_nodo
     ORDER BY FIELD(n.id_nodo, 'dht', 'pir', 'puerta', 'acel', 'luz')`
  );
  const [ultimos] = await pool.query(
    `SELECT id_nodo, parametro, unidad, valor, fecha_hora FROM (
       SELECT s.id_nodo, p.nombre AS parametro, p.unidad, m.valor, m.fecha_hora,
              ROW_NUMBER() OVER (PARTITION BY s.id_nodo, m.id_parametro ORDER BY m.fecha_hora DESC, m.id_medicion DESC) AS rn
       FROM Medicion m JOIN Sensor s ON s.id_sensor = m.id_sensor JOIN Parametro p ON p.id_parametro = m.id_parametro
       WHERE m.fecha_hora >= UTC_TIMESTAMP() - INTERVAL 1 DAY) t
     WHERE rn = 1`
  );
  const [series] = await pool.query(
    `SELECT s.id_nodo, p.nombre AS parametro,
            FROM_UNIXTIME(FLOOR(UNIX_TIMESTAMP(m.fecha_hora) / ?) * ?) AS t,
            ROUND(AVG(m.valor), 2) AS valor, MIN(m.valor) AS minimo, MAX(m.valor) AS maximo
     FROM Medicion m JOIN Sensor s ON s.id_sensor = m.id_sensor JOIN Parametro p ON p.id_parametro = m.id_parametro
     WHERE m.fecha_hora >= UTC_TIMESTAMP() - INTERVAL ? HOUR
     GROUP BY s.id_nodo, p.nombre, t ORDER BY t`,
    [cubeta, cubeta, horas]
  );
  const [umbrales] = await pool.query(
    `SELECT s.id_nodo, p.nombre AS parametro, p.unidad, u.minimo, u.maximo
     FROM Umbral u JOIN Sensor s ON s.id_sensor = u.id_sensor JOIN Parametro p ON p.id_parametro = u.id_parametro`
  );
  const [alertas] = await pool.query(
    `SELECT a.id_alerta, a.id_nodo, a.tipo, a.valor, a.ts_inicio, a.ts_fin,
            EXISTS (SELECT 1 FROM Notificacion n WHERE n.id_alerta = a.id_alerta) AS grave
     FROM Alerta a WHERE a.ts_fin IS NULL OR a.ts_inicio >= UTC_TIMESTAMP() - INTERVAL ? HOUR
     ORDER BY (a.ts_fin IS NULL) DESC, a.ts_inicio DESC, a.id_alerta DESC LIMIT 40`,
    [horas]
  );
  const [eventos] = await pool.query(
    `SELECT e.id_evento, s.id_nodo, e.tipo, e.magnitud, e.fuera_de_horario, e.fecha_hora
     FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor
     ORDER BY e.id_evento DESC LIMIT 40`
  );
  // Estado de la puerta = su ultimo evento (no hay "medicion" de puerta).
  const [[puerta]] = await pool.query(
    `SELECT e.tipo, e.fecha_hora FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor
     WHERE s.id_nodo = 'puerta' AND e.tipo IN ('puerta_abierta', 'puerta_cerrada')
     ORDER BY e.fecha_hora DESC, e.id_evento DESC LIMIT 1`
  );
  // Ultimo golpe y ultimo movimiento aparte: en la lista de 40 eventos se pierden tras muchas aperturas de puerta.
  const [porTipo] = await pool.query(
    `SELECT e.tipo, e.magnitud, e.fuera_de_horario, e.fecha_hora FROM Evento e
     WHERE e.id_evento IN (SELECT MAX(id_evento) FROM Evento WHERE tipo IN ('golpe', 'movimiento') GROUP BY tipo)`
  );
  // Ultima accion manual del buzzer del dht (boton): "off" con duracion_s = silencio de 30 min; "on" = quito el silencio.
  // El dashboard la usa para mostrar "Alarma silenciada hasta las HH:MM".
  const [[buzzer]] = await pool.query(
    `SELECT ac.comando, ac.origen, ac.duracion_s, ac.fecha_hora
     FROM AccionControl ac JOIN Actuador a ON a.id_actuador = ac.id_actuador
     WHERE a.id_nodo = 'dht' AND a.tipo = 'buzzer' AND ac.origen = 'manual'
     ORDER BY ac.fecha_hora DESC, ac.id_accion DESC LIMIT 1`
  );
  const [config] = await pool.query("SELECT clave, valor FROM Configuracion");
  return {
    ahora: new Date().toISOString(), horas, cubeta_s: cubeta, sin_reporte_s: SIN_REPORTE_S,
    nodos, ultimos, series, umbrales, alertas, eventos, puerta: puerta ?? null, buzzer: buzzer ?? null,
    ultimo_evento: Object.fromEntries(porTipo.map((e) => [e.tipo, e])),
    config: Object.fromEntries(config.map((r) => [r.clave, r.valor])),
  };
}

// ─── cuenta de administrador del dashboard (admin.js; apagada si faltan ADMIN_USER y ADMIN_HASH) ─
require("./admin").montar(app, pool, { alCambiar: () => cache.clear() });

// ─── avisos para n8n ────────────────────────────────────────────────────────
app.use("/api", (req, res, next) => {
  if (req.get("X-API-Key") !== API_KEY) return res.status(401).json({ error: "clave invalida" });
  next();
});

/**
 * GET /api/notificaciones/pendientes[?canal=telegram]
 * Avisos graves sin mandar de las ultimas 24 h (los mas viejos ya no sirven de aviso).
 */
app.get("/api/notificaciones/pendientes", ruta(async (req, res) => {
  const canal = req.query.canal ?? null;
  if (canal !== null && !["telegram", "whatsapp"].includes(canal)) throw new ErrorHttp(400, "'canal' debe ser telegram o whatsapp");
  const [filas] = await pool.query(
    `SELECT a.id_alerta, a.id_nodo, a.tipo, a.valor, a.ts_inicio, a.ts_fin, n.canal
     FROM Notificacion n JOIN Alerta a ON a.id_alerta = n.id_alerta
     WHERE n.enviada = FALSE AND a.ts_inicio >= UTC_TIMESTAMP() - INTERVAL 1 DAY AND (? IS NULL OR n.canal = ?)
     ORDER BY a.ts_inicio, a.id_alerta`,
    [canal, canal]
  );
  res.json({ total: filas.length, pendientes: filas });
}));

/** POST /api/notificaciones/enviadas  {"ids":[12,13],"canal":"telegram"} */
app.post("/api/notificaciones/enviadas", ruta(async (req, res) => {
  const { ids, canal } = req.body ?? {};
  if (!Array.isArray(ids) || ids.length === 0 || ids.length > 100 || !ids.every((i) => Number.isInteger(i) && i > 0))
    throw new ErrorHttp(400, "'ids' debe ser una lista de 1 a 100 enteros");
  if (!["telegram", "whatsapp"].includes(canal)) throw new ErrorHttp(400, "'canal' debe ser telegram o whatsapp");
  const [r] = await pool.query(
    "UPDATE Notificacion SET enviada = TRUE, ts_envio = UTC_TIMESTAMP() WHERE canal = ? AND enviada = FALSE AND id_alerta IN (?)",
    [canal, ids]
  );
  res.json({ marcadas: r.affectedRows });
}));

app.use("/api", (_req, res) => res.status(404).json({ error: "ruta no encontrada" }));
app.use((err, _req, res, _next) => {
  if (err instanceof ErrorHttp) return res.status(err.codigo).json({ error: err.message });
  if (err.type === "entity.parse.failed") return res.status(400).json({ error: "JSON mal formado" });
  console.error("error interno:", err.message);
  res.status(500).json({ error: "error interno al consultar la base de datos" });
});

app.listen(PUERTO, (err) => {
  if (err) { // puerto ocupado: ya hay otro servicio central corriendo. Dos motores duplicarian las alertas.
    console.error(`No se pudo abrir el puerto ${PUERTO} (${err.code ?? err.message}). ¿Ya hay otro servicio central abierto?`);
    process.exit(1);
  }
  console.log(`Servicio central de Argos: panel en http://localhost:${PUERTO}`);
  // Si MySQL aun no responde, el motor reintenta en 10 s (el panel ya contesta mientras).
  (function arrancarMotor() {
    motor.iniciar().catch((e) => { console.error("el motor no pudo arrancar, reintento en 10 s:", e.message); setTimeout(arrancarMotor, 10000); });
  })();
});
