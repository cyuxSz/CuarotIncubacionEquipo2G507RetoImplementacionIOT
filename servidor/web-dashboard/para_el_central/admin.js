/**
 * Argos — cuenta de administrador para el dashboard (se copia a servidor/central/admin.js).
 *
 * Ver el dashboard sigue siendo libre. Estas rutas solo sirven para las acciones de control:
 *
 *   GET  /admin/sesion     { disponible, admin }            ¿hay cuenta configurada? ¿hay sesion abierta?
 *   POST /admin/entrar     { usuario, clave }               abre sesion (cookie HttpOnly, 8 h)
 *   POST /admin/salir                                       cierra la sesion
 *   POST /admin/umbrales   { parametro, minimo, maximo }    cambia el rango de temperatura o humedad (pide sesion)
 *
 * Configuracion (en el .env del central): ADMIN_USER y ADMIN_HASH. El hash se genera con
 *   node crear_admin.mjs
 * Sin esas dos variables la cuenta queda apagada: /admin/sesion contesta disponible:false y el dashboard
 * no muestra la pestana de ajustes. La contrasena nunca se guarda ni se escribe en la bitacora.
 *
 * Uso en central.js, ANTES de la linea  app.use("/api", ...):
 *   require("./admin").montar(app, pool, { alCambiar: () => cache.clear() });
 */
const crypto = require("crypto");

const COOKIE = "argos_sesion";
const SESION_MS = 8 * 3600e3;
const MAX_FALLOS = 5;
const BLOQUEO_MS = 10 * 60e3;
// Limites fisicos razonables para no guardar un rango absurdo por un dedazo.
const LIMITES = { temperatura: { piso: 0, techo: 50, separacion: 2 }, humedad: { piso: 0, techo: 100, separacion: 5 } };

/** Formato del hash: scrypt:<sal base64url>:<clave derivada base64url> (lo escribe crear_admin.mjs). */
function claveCorrecta(clave, guardado) {
  const [metodo, sal, esperado] = String(guardado).split(":");
  if (metodo !== "scrypt" || !sal || !esperado) return false;
  const a = Buffer.from(esperado, "base64url");
  const b = crypto.scryptSync(String(clave), Buffer.from(sal, "base64url"), a.length || 64);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}
const iguales = (x, y) => {
  const a = crypto.createHash("sha256").update(String(x)).digest(), b = crypto.createHash("sha256").update(String(y)).digest();
  return crypto.timingSafeEqual(a, b);
};

function montar(app, pool, { alCambiar } = {}) {
  const USUARIO = process.env.ADMIN_USER, HASH = process.env.ADMIN_HASH;
  const disponible = Boolean(USUARIO && HASH);
  const sesiones = new Map(); // token -> vence (ms). En memoria: al reiniciar el central hay que volver a entrar.
  const fallos = new Map();   // origen -> { n, desde }

  const origen = (req) => req.get("cf-connecting-ip") || req.ip || "desconocido"; // detras del tunel, la IP real viene en esa cabecera
  const segura = (req) => req.secure || req.get("x-forwarded-proto") === "https";
  const galleta = (req, valor, maxAge) =>
    `${COOKIE}=${valor}; HttpOnly; SameSite=Strict; Path=/; Max-Age=${maxAge}${segura(req) ? "; Secure" : ""}`;
  function tokenDe(req) {
    const par = String(req.headers.cookie ?? "").split(";").map((c) => c.trim()).find((c) => c.startsWith(COOKIE + "="));
    return par ? par.slice(COOKIE.length + 1) : null;
  }
  function hayAdmin(req) {
    const t = tokenDe(req), vence = t && sesiones.get(t);
    if (!vence) return false;
    if (Date.now() > vence) { sesiones.delete(t); return false; }
    return true;
  }
  // La cabecera propia obliga al navegador a pedir permiso (preflight) si la peticion viene de otra pagina;
  // como el central no acepta otros origenes, una pagina ajena no puede usar la sesion abierta.
  const mismaPagina = (req, res, next) => (req.get("X-Argos") === "1" ? next() : res.status(400).json({ error: "petición no válida" }));
  const conSesion = (req, res, next) => (hayAdmin(req) ? next() : res.status(401).json({ error: "inicia sesión para hacer cambios" }));
  const ruta = (fn) => (req, res) => fn(req, res).catch((e) => {
    console.error("admin: error interno:", e.message);
    res.status(500).json({ error: "error interno" });
  });

  app.get("/admin/sesion", (req, res) => {
    res.set("Cache-Control", "no-store");
    res.json({ disponible, admin: disponible && hayAdmin(req) });
  });

  app.post("/admin/entrar", mismaPagina, ruta(async (req, res) => {
    if (!disponible) return res.status(404).json({ error: "no hay cuenta de administrador configurada" });
    const quien = origen(req), f = fallos.get(quien);
    if (f && f.n >= MAX_FALLOS && Date.now() - f.desde < BLOQUEO_MS)
      return res.status(429).json({ error: "demasiados intentos; espera 10 minutos" });
    if (f && Date.now() - f.desde >= BLOQUEO_MS) fallos.delete(quien);

    const { usuario, clave } = req.body ?? {};
    const bien = typeof usuario === "string" && typeof clave === "string" && clave.length <= 200
      && iguales(usuario, USUARIO) & claveCorrecta(clave, HASH); // & (no &&): siempre calcula las dos comparaciones
    if (!bien) {
      const previo = fallos.get(quien) ?? { n: 0, desde: Date.now() };
      fallos.set(quien, { n: previo.n + 1, desde: previo.desde });
      console.log(`admin: intento fallido desde ${quien}`);
      return res.status(401).json({ error: "usuario o contraseña incorrectos" });
    }
    fallos.delete(quien);
    for (const [t, vence] of sesiones) if (Date.now() > vence) sesiones.delete(t);
    const token = crypto.randomBytes(32).toString("base64url");
    sesiones.set(token, Date.now() + SESION_MS);
    res.set("Set-Cookie", galleta(req, token, SESION_MS / 1000));
    console.log(`admin: sesion abierta desde ${quien}`);
    res.json({ admin: true });
  }));

  app.post("/admin/salir", mismaPagina, (req, res) => {
    const t = tokenDe(req);
    if (t) sesiones.delete(t);
    res.set("Set-Cookie", galleta(req, "", 0));
    res.json({ admin: false });
  });

  app.post("/admin/umbrales", mismaPagina, conSesion, ruta(async (req, res) => {
    const { parametro, minimo, maximo } = req.body ?? {};
    const lim = Object.hasOwn(LIMITES, parametro) ? LIMITES[parametro] : null;
    if (!lim) return res.status(400).json({ error: "'parametro' debe ser temperatura o humedad" });
    if (typeof minimo !== "number" || typeof maximo !== "number" || !Number.isFinite(minimo) || !Number.isFinite(maximo))
      return res.status(400).json({ error: "'minimo' y 'maximo' deben ser números" });
    if (minimo < lim.piso || maximo > lim.techo)
      return res.status(400).json({ error: `el rango debe quedar entre ${lim.piso} y ${lim.techo}` });
    if (maximo - minimo < lim.separacion)
      return res.status(400).json({ error: `el máximo debe ser al menos ${lim.separacion} mayor que el mínimo` });
    const [r] = await pool.query(
      `UPDATE Umbral u JOIN Sensor s ON s.id_sensor = u.id_sensor JOIN Parametro p ON p.id_parametro = u.id_parametro
       SET u.minimo = ?, u.maximo = ? WHERE s.id_nodo = 'dht' AND p.nombre = ?`,
      [minimo, maximo, parametro]
    );
    if (r.affectedRows === 0) {
      const [[existe]] = await pool.query(
        `SELECT 1 AS si FROM Umbral u JOIN Sensor s ON s.id_sensor = u.id_sensor JOIN Parametro p ON p.id_parametro = u.id_parametro
         WHERE s.id_nodo = 'dht' AND p.nombre = ?`, [parametro]);
      if (!existe) return res.status(404).json({ error: "no existe ese umbral en la base de datos" });
    }
    console.log(`admin: rango de ${parametro} cambiado a ${minimo}-${maximo}`);
    if (alCambiar) alCambiar(); // el panel no espera a que caduque su cache
    res.json({ parametro, minimo, maximo });
  }));

  if (!disponible) console.log("admin: sin ADMIN_USER y ADMIN_HASH en el .env; las acciones de control quedan apagadas.");
}

module.exports = { montar, claveCorrecta };
