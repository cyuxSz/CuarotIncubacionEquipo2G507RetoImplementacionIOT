// Todas las consultas SQL de la API. Cada funcion trabaja solo con el nodo de esta API.
const pool = require("../db");
const { NODO } = require("../config");

// Escritura

// Marca al nodo como vivo.
function marcarVivo(conexion = pool, extra = {}) {
  return conexion.query(
    `UPDATE EstadoNodo SET estado = 'online', ultimo_reporte = UTC_TIMESTAMP(),
       reset_reason = COALESCE(?, reset_reason), uptime_s = COALESCE(?, uptime_s), rssi = COALESCE(?, rssi)
     WHERE id_nodo = ?`,
    [extra.reset_reason ?? null, extra.uptime_s ?? null, extra.rssi ?? null, NODO]
  );
}

// Guarda las lecturas en una transaccion: entran todas o ninguna.
// El sensor y el parametro se buscan por nombre; la fecha la pone el servidor en UTC.
async function guardarMediciones(lecturas) {
  const conexion = await pool.getConnection();
  try {
    await conexion.beginTransaction();
    for (const [parametro, valor] of lecturas) {
      await conexion.query(
        `INSERT INTO Medicion (id_sensor, id_parametro, valor, fecha_hora)
         SELECT s.id_sensor, p.id_parametro, ?, UTC_TIMESTAMP()
         FROM Sensor s JOIN Parametro p ON p.nombre = ? WHERE s.id_nodo = ?`,
        [valor, parametro, NODO]
      );
    }
    await marcarVivo(conexion);
    await conexion.commit();
  } catch (e) {
    await conexion.rollback();
    throw e;
  } finally {
    conexion.release();
  }
}

// Guarda un evento. Para "movimiento" calcula si fue fuera del horario de acceso.
async function guardarEvento(tipo, magnitud) {
  const [r] = await pool.query(
    `INSERT INTO Evento (id_sensor, tipo, magnitud, fuera_de_horario, fecha_hora)
     SELECT s.id_sensor, ?, ?,
            ? = 'movimiento' AND (
              WEEKDAY(UTC_TIMESTAMP() - INTERVAL 6 HOUR) > 4
              OR TIME(UTC_TIMESTAMP() - INTERVAL 6 HOUR) NOT BETWEEN
                 (SELECT CAST(valor AS TIME) FROM Configuracion WHERE clave = 'horario_acceso_inicio')
                 AND (SELECT CAST(valor AS TIME) FROM Configuracion WHERE clave = 'horario_acceso_fin')),
            UTC_TIMESTAMP()
     FROM Sensor s WHERE s.id_nodo = ?`,
    [tipo, magnitud, tipo, NODO]
  );
  await marcarVivo();
  return r.insertId;
}

// Guarda un evento de actuacion. Regresa null si el nodo no tiene ese actuador.
async function guardarAccion(actuador, comando, origen, duracion_s = null, idAlerta = null) {
  const [r] = await pool.query(
    `INSERT INTO AccionControl (id_actuador, id_alerta, origen, comando, duracion_s, fecha_hora)
     SELECT id_actuador, ?, ?, ?, ?, UTC_TIMESTAMP() FROM Actuador WHERE id_nodo = ? AND tipo = ?`,
    [idAlerta, origen, comando, duracion_s, NODO, actuador]
  );
  if (r.affectedRows === 0) return null;
  if (origen !== "alerta") await marcarVivo();
  return r.insertId;
}

// Umbrales y alertas

// Umbrales del sensor de este nodo, uno por parametro.
async function leerUmbrales() {
  const [filas] = await pool.query(
    `SELECT u.id_umbral, p.nombre AS parametro, p.unidad, u.minimo, u.maximo, u.histeresis,
            u.persistencia, u.activa_buzzer
     FROM Umbral u JOIN Sensor s ON s.id_sensor = u.id_sensor JOIN Parametro p ON p.id_parametro = u.id_parametro
     WHERE s.id_nodo = ?`,
    [NODO]
  );
  return filas;
}

// Abre una alerta. Regresa null si ya habia una activa de ese tipo.
async function abrirAlerta(tipo, valor, idUmbral) {
  const [activa] = await pool.query(
    "SELECT 1 FROM Alerta WHERE id_nodo = ? AND tipo = ? AND ts_fin IS NULL", [NODO, tipo]);
  if (activa.length > 0) return null;
  try {
    const [r] = await pool.query(
      "INSERT INTO Alerta (id_nodo, id_umbral, tipo, valor, ts_inicio) VALUES (?, ?, ?, ?, UTC_TIMESTAMP())",
      [NODO, idUmbral, tipo, valor]
    );
    return r.insertId;
  } catch (e) {
    if (e.code === "ER_DUP_ENTRY") return null; // otro proceso la abrio al mismo tiempo
    throw e;
  }
}

// Cierra la alerta activa de ese tipo.
async function cerrarAlerta(tipo) {
  const [f] = await pool.query(
    "SELECT id_alerta FROM Alerta WHERE id_nodo = ? AND tipo = ? AND ts_fin IS NULL", [NODO, tipo]);
  if (f.length === 0) return null;
  await pool.query("UPDATE Alerta SET ts_fin = UTC_TIMESTAMP() WHERE id_alerta = ?", [f[0].id_alerta]);
  return f[0].id_alerta;
}

// "on" si hay una alerta activa cuyo umbral activa el buzzer.
async function leerAlarma() {
  const [f] = await pool.query(
    `SELECT 1 FROM Alerta a JOIN Umbral u ON u.id_umbral = a.id_umbral
     WHERE a.id_nodo = ? AND a.ts_fin IS NULL AND u.activa_buzzer LIMIT 1`,
    [NODO]
  );
  return f.length ? "on" : "off";
}

// Consultas

// Historial de un parametro entre dos fechas.
async function leerMediciones(parametro, desde, hasta, limite) {
  const [filas] = await pool.query(
    `SELECT m.id_medicion, p.nombre AS parametro, m.valor, p.unidad, m.fecha_hora
     FROM Medicion m
     JOIN Sensor s    ON s.id_sensor = m.id_sensor
     JOIN Parametro p ON p.id_parametro = m.id_parametro
     WHERE s.id_nodo = ? AND p.nombre = ? AND m.fecha_hora BETWEEN ? AND ?
     ORDER BY m.fecha_hora DESC LIMIT ?`,
    [NODO, parametro, desde, hasta, limite]
  );
  return filas;
}

async function leerEventos(limite) {
  const [filas] = await pool.query(
    `SELECT e.id_evento, e.tipo, e.magnitud, e.fuera_de_horario, e.fecha_hora
     FROM Evento e JOIN Sensor s ON s.id_sensor = e.id_sensor
     WHERE s.id_nodo = ? ORDER BY e.fecha_hora DESC LIMIT ?`,
    [NODO, limite]
  );
  return filas;
}

async function leerAcciones(limite) {
  const [filas] = await pool.query(
    `SELECT ac.id_accion, a.tipo AS actuador, ac.comando, ac.origen, ac.duracion_s, ac.id_alerta, ac.fecha_hora
     FROM AccionControl ac JOIN Actuador a ON a.id_actuador = ac.id_actuador
     WHERE a.id_nodo = ? ORDER BY ac.fecha_hora DESC, ac.id_accion DESC LIMIT ?`,
    [NODO, limite]
  );
  return filas;
}

async function leerAlertas(soloActivas, limite) {
  const [filas] = await pool.query(
    `SELECT id_alerta, tipo, valor, ts_inicio, ts_fin FROM Alerta
     WHERE id_nodo = ? AND (? = 0 OR ts_fin IS NULL) ORDER BY ts_inicio DESC LIMIT ?`,
    [NODO, soloActivas ? 1 : 0, limite]
  );
  return filas;
}

// Ficha del nodo y su ultimo valor por parametro.
async function leerEstado() {
  const [[nodo]] = await pool.query(
    `SELECT n.id_nodo, n.descripcion, r.nombre AS responsable, c.descripcion AS caja, s.modelo AS sensor,
            e.estado, e.ultimo_reporte, e.rssi, e.uptime_s, e.reset_reason
     FROM Nodo n
     JOIN Responsable r ON r.id_responsable = n.id_responsable
     JOIN Caja c        ON c.id_caja = n.id_caja
     JOIN Sensor s      ON s.id_nodo = n.id_nodo
     JOIN EstadoNodo e  ON e.id_nodo = n.id_nodo
     WHERE n.id_nodo = ?`,
    [NODO]
  );
  const [ultimos] = await pool.query(
    `SELECT parametro, valor, unidad, fecha_hora FROM (
       SELECT p.nombre AS parametro, m.valor, p.unidad, m.fecha_hora,
              ROW_NUMBER() OVER (PARTITION BY m.id_parametro ORDER BY m.fecha_hora DESC, m.id_medicion DESC) AS rn
       FROM Medicion m
       JOIN Sensor s    ON s.id_sensor = m.id_sensor
       JOIN Parametro p ON p.id_parametro = m.id_parametro
       WHERE s.id_nodo = ?) t
     WHERE rn = 1`,
    [NODO]
  );
  return { nodo, ultimos };
}

module.exports = {
  marcarVivo, guardarMediciones, guardarEvento, guardarAccion,
  leerUmbrales, abrirAlerta, cerrarAlerta, leerAlarma,
  leerMediciones, leerEventos, leerAcciones, leerAlertas, leerEstado,
};
