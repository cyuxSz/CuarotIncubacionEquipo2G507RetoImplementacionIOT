/**
 * Argos (Equipo 2). API REST de un nodo. Etapa 3.
 * Autor: Luis Eduardo Mendoza Menendez (A01669847), nodo dht (temperatura y humedad).
 *
 * El NodeMCU manda sus datos por HTTP y esta API los guarda en MySQL (base argos).
 * El nodo se elige con NODO en el archivo de configuracion (ver config.js).
 * Todas las rutas piden la cabecera x-api-key. La lista de rutas esta en LEEME.md.
 * Respuestas: 200/201 bien, 400 dato invalido, 401 clave incorrecta, 404 ruta inexistente, 500 fallo de la BD.
 */
const express = require("express");
const config = require("./config");
const { validarApiKey } = require("./middleware/auth");
const modelo = require("./models/nodoModel");
const umbrales = require("./models/umbralModel");

const { NODO, PUERTO } = config;
const app = express();

// Middleware
app.use(express.json({ limit: "10kb" }));        // el NodeMCU manda JSON chico
app.use(express.urlencoded({ extended: true })); // por si se prueba con un formulario

// Muestra en consola cada peticion con su resultado.
app.use((req, res, next) => {
  res.on("finish", () => console.log(`${new Date().toISOString()} ${req.method} ${req.originalUrl} -> ${res.statusCode}`));
  next();
});

app.use("/api", validarApiKey); // sin clave correcta no pasa nada de /api

// Validacion
// Error con codigo HTTP; el manejador final lo convierte en respuesta.
class ErrorHttp extends Error {
  constructor(codigo, mensaje) { super(mensaje); this.codigo = codigo; }
}
// Hace que los errores de una ruta async lleguen al manejador final.
const ruta = (fn) => (req, res, next) => fn(req, res).catch(next);
const esNumero = (v) => typeof v === "number" && Number.isFinite(v);

// Si el cuerpo trae "nodo", debe ser el de esta API.
function revisarNodo(nodo) {
  if (nodo !== undefined && nodo !== NODO)
    throw new ErrorHttp(400, `esta API es del nodo '${NODO}', no de '${nodo}'`);
}
// Entero de la URL entre min y max; vacio usa el valor por omision.
function entero(texto, porOmision, min, max, nombre) {
  if (texto === undefined) return porOmision;
  const n = Number(texto);
  if (!Number.isInteger(n) || n < min || n > max) throw new ErrorHttp(400, `'${nombre}' debe ser entero entre ${min} y ${max}`);
  return n;
}
// Fecha ISO 8601 de la URL; vacia usa el valor por omision.
function fecha(texto, porOmision, nombre) {
  if (texto === undefined) return porOmision;
  const d = new Date(texto);
  if (Number.isNaN(d.getTime())) throw new ErrorHttp(400, `fecha invalida en '${nombre}'`);
  return d;
}

// POST: lo que manda el NodeMCU

if (Object.keys(config.parametros).length > 0) {
  // POST /api/mediciones  {"nodo":"dht","lecturas":[{"parametro":"temperatura","valor":25.4}]}
  // Responde 201 con {"guardadas":2,"alarma":"off"}
  app.post("/api/mediciones", ruta(async (req, res) => {
    const { nodo, lecturas } = req.body ?? {};
    revisarNodo(nodo);
    if (!Array.isArray(lecturas) || lecturas.length === 0 || lecturas.length > 10)
      throw new ErrorHttp(400, "'lecturas' debe ser una lista de 1 a 10 elementos");

    // Se valida todo antes de escribir.
    const filas = [];
    for (const l of lecturas) {
      const rango = config.parametros[l?.parametro];
      if (!rango) throw new ErrorHttp(400, `parametro desconocido para ${NODO}: ${l?.parametro}`);
      if (!esNumero(l.valor) || l.valor < rango[0] || l.valor > rango[1])
        throw new ErrorHttp(400, `valor fuera de rango para ${l.parametro}: ${l.valor}`);
      filas.push([l.parametro, l.valor]);
    }
    await modelo.guardarMediciones(filas);
    // Puede abrir o cerrar una alerta.
    await umbrales.revisar(filas).catch((e) => console.error("error al revisar umbrales:", e.message));
    res.status(201).json({ guardadas: filas.length, alarma: await modelo.leerAlarma() });
  }));

  // GET /api/mediciones?parametro=temperatura (por omision: ultimas 24 h, 500 filas)
  app.get("/api/mediciones", ruta(async (req, res) => {
    const { parametro } = req.query;
    if (!config.parametros[parametro])
      throw new ErrorHttp(400, `'parametro' debe ser uno de: ${Object.keys(config.parametros).join(", ")}`);
    const hasta = fecha(req.query.hasta, new Date(), "hasta");
    const desde = fecha(req.query.desde, new Date(hasta.getTime() - 24 * 3600 * 1000), "desde");
    const limite = entero(req.query.limite, 500, 1, 1000, "limite");
    const datos = await modelo.leerMediciones(parametro, desde, hasta, limite);
    res.json({ nodo: NODO, parametro, total: datos.length, datos });
  }));
}

// POST /api/eventos  {"nodo":"acel","tipo":"golpe","magnitud":1.8}
app.post("/api/eventos", ruta(async (req, res) => {
  const { nodo, tipo, magnitud = null } = req.body ?? {};
  revisarNodo(nodo);
  if (!config.eventos.includes(tipo))
    throw new ErrorHttp(400, `tipo de evento invalido para ${NODO}: ${tipo}. Acepta: ${config.eventos.join(", ")}`);
  if (magnitud !== null && !esNumero(magnitud)) throw new ErrorHttp(400, "'magnitud' debe ser numero");
  res.status(201).json({ id_evento: await modelo.guardarEvento(tipo, magnitud) });
}));

// POST /api/acciones  {"nodo":"dht","actuador":"buzzer","comando":"off","origen":"manual","duracion_s":1800}
// origen: local (lo decidio el nodo) o manual (boton). Las de una alerta las registra la API.
app.post("/api/acciones", ruta(async (req, res) => {
  const { nodo, actuador, comando, duracion_s = null, origen = "local" } = req.body ?? {};
  revisarNodo(nodo);
  if (!["buzzer", "led_rojo"].includes(actuador)) throw new ErrorHttp(400, `actuador invalido: ${actuador}`);
  if (!["on", "off"].includes(comando)) throw new ErrorHttp(400, "'comando' debe ser on u off");
  if (!["local", "manual"].includes(origen)) throw new ErrorHttp(400, "'origen' debe ser local o manual");
  if (duracion_s !== null && !(Number.isInteger(duracion_s) && duracion_s > 0 && duracion_s <= 65535))
    throw new ErrorHttp(400, "'duracion_s' debe ser entero entre 1 y 65535");
  const id = await modelo.guardarAccion(actuador, comando, origen, duracion_s);
  if (id === null) throw new ErrorHttp(400, `el nodo ${NODO} no tiene ${actuador}`);
  res.status(201).json({ id_accion: id });
}));

// POST /api/latido  {"nodo":"dht","uptime_s":3600,"rssi":-62}
app.post("/api/latido", ruta(async (req, res) => {
  const { nodo, uptime_s = null, rssi = null, reset_reason = null } = req.body ?? {};
  revisarNodo(nodo);
  if (uptime_s !== null && !(Number.isInteger(uptime_s) && uptime_s >= 0)) throw new ErrorHttp(400, "'uptime_s' invalido");
  if (rssi !== null && !(Number.isInteger(rssi) && rssi >= -120 && rssi <= 0)) throw new ErrorHttp(400, "'rssi' invalido");
  if (reset_reason !== null && (typeof reset_reason !== "string" || reset_reason.length > 60))
    throw new ErrorHttp(400, "'reset_reason' invalido");
  await modelo.marcarVivo(undefined, { uptime_s, rssi, reset_reason });
  res.json({ ok: true });
}));

// GET: instrucciones para el NodeMCU

// GET /api/comandos: dice al nodo si debe sonar la alarma y cuales son los umbrales vigentes.
app.get(["/api/comandos", "/api/comandos/:nodo"], ruta(async (req, res) => {
  revisarNodo(req.params.nodo);
  res.json({ nodo: NODO, alarma: await modelo.leerAlarma(), umbrales: await modelo.leerUmbrales() });
}));

// GET /api/datetime: fecha y hora del servidor en UTC.
app.get("/api/datetime", (_req, res) => {
  const ahora = new Date();
  res.json({ timestamp: ahora.toISOString(), epoch_s: Math.floor(ahora.getTime() / 1000), dayNumber: ahora.getUTCDay() });
});

// GET: consultas

// GET /api/estado
app.get("/api/estado", ruta(async (_req, res) => res.json(await modelo.leerEstado())));

// GET /api/eventos?limite=50
app.get("/api/eventos", ruta(async (req, res) => {
  const datos = await modelo.leerEventos(entero(req.query.limite, 50, 1, 500, "limite"));
  res.json({ nodo: NODO, total: datos.length, datos });
}));

// GET /api/acciones?limite=50
app.get("/api/acciones", ruta(async (req, res) => {
  const datos = await modelo.leerAcciones(entero(req.query.limite, 50, 1, 500, "limite"));
  res.json({ nodo: NODO, total: datos.length, datos });
}));

// GET /api/alertas?estado=activa|todas&limite=50
app.get("/api/alertas", ruta(async (req, res) => {
  const estado = req.query.estado ?? "activa";
  if (!["activa", "todas"].includes(estado)) throw new ErrorHttp(400, "'estado' debe ser activa o todas");
  const datos = await modelo.leerAlertas(estado === "activa", entero(req.query.limite, 50, 1, 200, "limite"));
  res.json({ nodo: NODO, total: datos.length, datos });
}));

// Errores
app.use("/api", (_req, res) => res.status(404).json({ error: "ruta no encontrada" }));

// 400 para validaciones y JSON mal formado; 500 para lo demas (por ejemplo, MySQL apagado).
app.use((err, _req, res, _next) => {
  if (err instanceof ErrorHttp) return res.status(err.codigo).json({ error: err.message });
  if (err.type === "entity.parse.failed") return res.status(400).json({ error: "JSON mal formado" });
  console.error("error interno:", err.message);
  res.status(500).json({ error: "error interno al guardar o consultar la base de datos" });
});

app.listen(PUERTO, () => console.log(`API del nodo '${NODO}' en http://localhost:${PUERTO}`));
