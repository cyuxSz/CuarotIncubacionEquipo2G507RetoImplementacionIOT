import { defineConfig } from "vite";
import { generar, ESCENARIOS, ADMIN_PRUEBA } from "./herramientas/datos_prueba.mjs";

// Solo en `npm run dev`: responde GET /panel/datos con datos de prueba, para trabajar sin central ni MySQL.
// El escenario sale de la pagina que pide (http://localhost:5173/?escenario=alerta).
// Con ARGOS_CENTRAL=http://localhost:3000 se usa el central real en lugar de los datos de prueba.
const central = process.env.ARGOS_CENTRAL;
const datosDePrueba = () => ({
  name: "argos-datos-de-prueba",
  apply: "serve",
  configureServer(server) {
    if (central) return;
    // Cuenta de admin de mentira, con la misma forma que para_el_central/admin.js (sesion en memoria).
    let sesion = null; const rangos = {};
    const json = (res, codigo, cuerpo) => { res.statusCode = codigo; res.setHeader("Content-Type", "application/json; charset=utf-8"); res.end(JSON.stringify(cuerpo)); };
    const cuerpoDe = (req) => new Promise((ok) => { let t = ""; req.on("data", (c) => (t += c)); req.on("end", () => { try { ok(JSON.parse(t || "{}")); } catch { ok({}); } }); });
    server.middlewares.use("/admin", async (req, res) => {
      const conSesion = sesion && String(req.headers.cookie ?? "").includes(`argos_sesion=${sesion}`);
      const ruta = req.url.split("?")[0];
      if (ruta === "/sesion") return json(res, 200, { disponible: true, admin: Boolean(conSesion) });
      if (req.method !== "POST" || req.headers["x-argos"] !== "1") return json(res, 400, { error: "petición no válida" });
      const c = await cuerpoDe(req);
      if (ruta === "/entrar") {
        if (c.usuario !== ADMIN_PRUEBA.usuario || c.clave !== ADMIN_PRUEBA.clave) return json(res, 401, { error: "usuario o contraseña incorrectos" });
        sesion = Math.random().toString(36).slice(2);
        res.setHeader("Set-Cookie", `argos_sesion=${sesion}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800`);
        return json(res, 200, { admin: true });
      }
      if (ruta === "/salir") { sesion = null; res.setHeader("Set-Cookie", "argos_sesion=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"); return json(res, 200, { admin: false }); }
      if (ruta === "/umbrales") {
        if (!conSesion) return json(res, 401, { error: "inicia sesión para hacer cambios" });
        if (!["temperatura", "humedad"].includes(c.parametro) || typeof c.minimo !== "number" || typeof c.maximo !== "number") return json(res, 400, { error: "datos no válidos" });
        if (c.maximo - c.minimo < (c.parametro === "temperatura" ? 2 : 5)) return json(res, 400, { error: `el máximo debe ser al menos ${c.parametro === "temperatura" ? 2 : 5} mayor que el mínimo` });
        rangos[c.parametro] = { minimo: c.minimo, maximo: c.maximo };
        return json(res, 200, c);
      }
      json(res, 404, { error: "ruta no encontrada" });
    });
    server.middlewares.use("/panel/datos", (req, res) => {
      const q = new URL(req.url, "http://x").searchParams;
      const deLaPagina = req.headers.referer ? new URL(req.headers.referer).searchParams.get("escenario") : null;
      const escenario = q.get("escenario") ?? deLaPagina ?? "normal";
      res.setHeader("Content-Type", "application/json; charset=utf-8");
      res.setHeader("Cache-Control", "no-store");
      if (escenario === "error" || !ESCENARIOS.includes(escenario)) {
        res.statusCode = 500;
        return res.end(JSON.stringify({ error: "error interno al consultar la base de datos" }));
      }
      res.end(JSON.stringify(generar(escenario, Number(q.get("horas") ?? 24), rangos)));
    });
  },
});

// base "./": la salida funciona desde cualquier ruta (el central la sirve en la raiz).
export default defineConfig({
  base: "./",
  plugins: [datosDePrueba()],
  server: { port: 5173, strictPort: true, proxy: central ? { "/panel": central, "/admin": central } : undefined },
  build: { outDir: "dist", emptyOutDir: true, target: "es2020" },
});
