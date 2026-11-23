/**
 * Prueba de punta a punta del servidor de Argos SIN hardware: levanta las 5 API de los nodos
 * (servidor/api-rest), el servicio central (servidor/central) y un broker MQTT de prueba, y hace de
 * NodeMCU mandando las mismas peticiones que el firmware. Revisa la BD, las respuestas y lo que sale por MQTT.
 *
 * Necesita una base `argos` VACIA de pruebas (nunca la del invernadero: la prueba cambia Configuracion
 * y mete datos falsos). Variables: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME.
 * Dependencias: npm install (en esta carpeta).
 *   node prueba_integracion.js
 * Sale con 0 si todo pasa y con 1 si algo falla.
 */
const { spawn } = require("child_process");
const net = require("net");
const path = require("path");
const mysql = require("mysql2/promise");
const mqtt = require("mqtt");
const crearBroker = require("aedes");

const RAIZ = path.resolve(__dirname, "..");
const CLAVE = "clave-del-banco";
const PUERTO_MQTT = 1899;
const BD = {
  DB_HOST: process.env.DB_HOST || "127.0.0.1", DB_PORT: process.env.DB_PORT || "3399",
  DB_USER: process.env.DB_USER, DB_PASSWORD: process.env.DB_PASSWORD, DB_NAME: process.env.DB_NAME || "argos",
};
const PUERTOS = { dht: 3101, luz: 3102, pir: 3103, puerta: 3104, acel: 3105 };
const CENTRAL = 3100;

const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const hijos = [];
let fallas = 0, pasadas = 0;
function revisa(nombre, ok, detalle = "") {
  if (ok) { pasadas++; console.log(`  ok    ${nombre}`); }
  else { fallas++; console.log(`  FALLA ${nombre} ${detalle}`); }
}
/** Espera hasta que fn() regrese algo verdadero (revisa cada 250 ms). */
async function hasta(fn, ms = 8000) {
  const fin = Date.now() + ms;
  for (;;) {
    const v = await fn();
    if (v || Date.now() > fin) return v;
    await dormir(250);
  }
}

function lanzar(nombre, carpeta, archivo, env) {
  const h = spawn(process.execPath, [archivo], { cwd: path.join(RAIZ, carpeta), env: { ...process.env, ...BD, API_KEY: CLAVE, ...env } });
  h.stdout.on("data", (d) => process.env.VERBOSO && process.stdout.write(`[${nombre}] ${d}`));
  h.stderr.on("data", (d) => process.stdout.write(`[${nombre}!] ${d}`));
  hijos.push(h);
}

async function pedir(puerto, metodo, ruta, cuerpo, clave = CLAVE) {
  const r = await fetch(`http://127.0.0.1:${puerto}${ruta}`, {
    method: metodo,
    headers: { ...(clave ? { "X-API-Key": clave } : {}), ...(cuerpo ? { "Content-Type": "application/json" } : {}) },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  return { codigo: r.status, datos: await r.json().catch(() => null) };
}
const nodo = (id, ruta, cuerpo) => pedir(PUERTOS[id], "POST", ruta, { nodo: id, ...cuerpo });
const lectura = (t, h) => nodo("dht", "/api/mediciones", { lecturas: [{ parametro: "temperatura", valor: t }, { parametro: "humedad", valor: h }] });

async function main() {
  const bd = await mysql.createPool({ host: BD.DB_HOST, port: Number(BD.DB_PORT), user: BD.DB_USER, password: BD.DB_PASSWORD, database: BD.DB_NAME, timezone: "Z", decimalNumbers: true });
  const uno = async (sql, p) => (await bd.query(sql, p))[0][0];
  const [[{ n: previas }]] = await bd.query("SELECT COUNT(*) AS n FROM Medicion");
  if (previas > 500) throw new Error("la base tiene muchos datos: parece la real, no una de pruebas. No se corre.");
  await bd.query("UPDATE Configuracion SET valor = '2' WHERE clave = 'puerta_abierta_max_s'");
  await bd.query("INSERT INTO Configuracion (clave, valor) VALUES ('grave_s_puerta_abierta', '4') ON DUPLICATE KEY UPDATE valor = '4'");

  // broker de prueba (sin usuarios: la ACL de Mosquitto no se prueba aqui)
  const broker = crearBroker();
  const servidor = net.createServer(broker.handle);
  await new Promise((r) => servidor.listen(PUERTO_MQTT, "127.0.0.1", r));
  const mensajes = [];
  const escucha = mqtt.connect(`mqtt://127.0.0.1:${PUERTO_MQTT}`, { clientId: "banco" });
  await new Promise((r) => escucha.on("connect", r));
  escucha.subscribe("argos-eq2/invernadero/#");
  escucha.on("message", (t, c) => mensajes.push({ t, c: c.toString() }));
  const llego = (topic, texto) => mensajes.some((m) => m.t === topic && m.c.includes(texto));

  for (const [id, puerto] of Object.entries(PUERTOS))
    lanzar(id, "api-rest", "RestApi-Equipo2-A01669847.js", { NODO: id, PUERTO: String(puerto) });
  lanzar("central", "central", "central.js", { PUERTO: String(CENTRAL), REVISION_MS: "500", PANEL_CACHE_MS: "0", MQTT_URL: `mqtt://127.0.0.1:${PUERTO_MQTT}` });
  const arriba = await hasta(async () => {
    try { return (await Promise.all([...Object.values(PUERTOS).map((p) => pedir(p, "GET", "/api/estado")), pedir(CENTRAL, "GET", "/panel/datos")])).every((r) => r.codigo === 200); }
    catch { return false; }
  }, 15000);
  revisa("las 5 API y el servicio central responden", arriba);
  if (!arriba) return;

  console.log("\n1. Seguridad y validacion");
  revisa("sin clave -> 401", (await pedir(PUERTOS.dht, "POST", "/api/mediciones", { nodo: "dht", lecturas: [] }, null)).codigo === 401);
  revisa("clave equivocada -> 401", (await pedir(PUERTOS.dht, "GET", "/api/estado", null, "otra")).codigo === 401);
  revisa("temperatura imposible -> 400", (await lectura(150, 50)).codigo === 400);
  revisa("evento de otro nodo -> 400", (await nodo("pir", "/api/eventos", { tipo: "golpe" })).codigo === 400);
  revisa("nodo equivocado en la API del dht -> 400", (await pedir(PUERTOS.dht, "POST", "/api/latido", { nodo: "luz" })).codigo === 400);
  revisa("avisos sin clave -> 401", (await pedir(CENTRAL, "GET", "/api/notificaciones/pendientes", null, null)).codigo === 401);
  revisa("el panel se sirve en /", (await fetch(`http://127.0.0.1:${CENTRAL}/`)).status === 200);

  console.log("\n2. Lecturas normales del dht y de luz");
  const r1 = await lectura(25.4, 51.2);
  revisa("POST /api/mediciones -> 201 con alarma off", r1.codigo === 201 && r1.datos.guardadas === 2 && r1.datos.alarma === "off", JSON.stringify(r1));
  revisa("luz -> 201", (await nodo("luz", "/api/mediciones", { lecturas: [{ parametro: "luz", valor: 640 }] })).codigo === 201);
  revisa("latidos -> 200", (await Promise.all(["pir", "puerta", "acel"].map((n) => nodo(n, "/api/latido", { uptime_s: 60, rssi: -60 })))).every((r) => r.codigo === 200));
  const p1 = (await pedir(CENTRAL, "GET", "/panel/datos")).datos;
  revisa("el panel ve los 5 nodos en linea", p1.nodos.length === 5 && p1.nodos.every((n) => n.estado === "online"), JSON.stringify(p1.nodos.map((n) => [n.id_nodo, n.estado])));
  revisa("el panel trae el ultimo valor de temperatura", p1.ultimos.some((u) => u.parametro === "temperatura" && u.valor === 25.4));
  revisa("el panel trae la serie para la grafica", p1.series.some((s) => s.parametro === "humedad"));

  console.log("\n3. Temperatura alta: 3 lecturas abren la alerta y suena el buzzer");
  await lectura(29.1, 50); await lectura(29.3, 50);
  revisa("2 lecturas altas aun no abren alerta", !(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'temperatura' AND ts_fin IS NULL")));
  const r3 = await lectura(29.6, 50);
  revisa("la 3.a responde alarma on", r3.datos.alarma === "on", JSON.stringify(r3.datos));
  revisa("GET /api/comandos/dht -> on", (await pedir(PUERTOS.dht, "GET", "/api/comandos/dht")).datos.alarma === "on");
  revisa("MQTT: cmd/alarma on", await hasta(() => llego("argos-eq2/invernadero/cmd/alarma", "on")));
  revisa("MQTT: alerta abierta de temperatura", await hasta(() => llego("argos-eq2/invernadero/alertas", '"evento":"abierta"') && llego("argos-eq2/invernadero/alertas", '"tipo":"temperatura"')));
  revisa("queda el encendido del buzzer en AccionControl", !!(await uno("SELECT 1 AS x FROM AccionControl WHERE origen = 'alerta' AND comando = 'on'")));
  await lectura(27.8, 50);
  revisa("27.8 C (zona de histeresis) no cierra", !!(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'temperatura' AND ts_fin IS NULL")));
  await lectura(26, 50); await lectura(26, 50); await lectura(26, 50);
  revisa("3 lecturas normales cierran la alerta", !(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'temperatura' AND ts_fin IS NULL")));
  revisa("MQTT: cmd/alarma off", await hasta(() => llego("argos-eq2/invernadero/cmd/alarma", "off")));
  revisa("MQTT: alerta cerrada", await hasta(() => llego("argos-eq2/invernadero/alertas", '"evento":"cerrada"')));

  console.log("\n4. Boton de silencio y LED rojo (acciones)");
  revisa("silencio manual -> 201", (await nodo("dht", "/api/acciones", { actuador: "buzzer", comando: "off", origen: "manual", duracion_s: 1800 })).codigo === 201);
  revisa("LED rojo del pir -> 201", (await nodo("pir", "/api/acciones", { actuador: "led_rojo", comando: "on", origen: "local" })).codigo === 201);
  revisa("buzzer en un nodo que no lo tiene -> 400", (await nodo("pir", "/api/acciones", { actuador: "buzzer", comando: "on" })).codigo === 400);

  console.log("\n5. Puerta abierta de mas (limite de prueba: 2 s; grave a los 4 s)");
  revisa("puerta_abierta -> 201", (await nodo("puerta", "/api/eventos", { tipo: "puerta_abierta" })).codigo === 201);
  revisa("al momento no hay alerta", !(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'puerta_abierta' AND ts_fin IS NULL")));
  revisa("pasado el limite se abre la alerta", !!(await hasta(() => uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'puerta_abierta' AND ts_fin IS NULL"), 6000)));
  revisa("se vuelve grave: fila en Notificacion y aviso por MQTT", !!(await hasta(() => uno("SELECT 1 AS x FROM Notificacion WHERE enviada = FALSE"), 6000)) && (await hasta(() => llego("argos-eq2/invernadero/alertas", '"evento":"grave"'))));
  const pend = (await pedir(CENTRAL, "GET", "/api/notificaciones/pendientes?canal=telegram")).datos;
  revisa("n8n ve 1 aviso pendiente de telegram", pend.total === 1 && pend.pendientes[0].tipo === "puerta_abierta", JSON.stringify(pend));
  const marca = await pedir(CENTRAL, "POST", "/api/notificaciones/enviadas", { ids: pend.pendientes.map((p) => p.id_alerta), canal: "telegram" });
  revisa("marcar enviado -> 1", marca.datos.marcadas === 1);
  revisa("ya no esta pendiente en telegram, si en whatsapp", (await pedir(CENTRAL, "GET", "/api/notificaciones/pendientes?canal=telegram")).datos.total === 0 && (await pedir(CENTRAL, "GET", "/api/notificaciones/pendientes?canal=whatsapp")).datos.total === 1);
  await dormir(1200);
  revisa("la misma alerta no se avisa dos veces", (await uno("SELECT COUNT(*) AS n FROM Notificacion")).n === 2);
  await nodo("puerta", "/api/eventos", { tipo: "puerta_cerrada" });
  revisa("al cerrar la puerta se cierra la alerta", await hasta(async () => !(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'puerta_abierta' AND ts_fin IS NULL"))));
  const p5 = (await pedir(CENTRAL, "GET", "/panel/datos")).datos;
  revisa("el panel dice puerta cerrada y marca la alerta como grave", p5.puerta.tipo === "puerta_cerrada" && p5.alertas.some((a) => a.tipo === "puerta_abierta" && a.grave));

  console.log("\n6. Golpes");
  await nodo("acel", "/api/eventos", { tipo: "golpe", magnitud: 0.2 });
  await nodo("acel", "/api/eventos", { tipo: "golpe", magnitud: 0.85 });
  revisa("solo el golpe sobre el umbral (0.5 g) hace alerta", await hasta(async () => (await uno("SELECT COUNT(*) AS n FROM Alerta WHERE tipo = 'golpe'")).n === 1));
  await dormir(700);
  revisa("y es una sola, ya cerrada", (await uno("SELECT COUNT(*) AS n, SUM(ts_fin IS NULL) AS abiertas FROM Alerta WHERE tipo = 'golpe'")).abiertas == 0);

  console.log("\n7. Movimiento");
  const ev = await nodo("pir", "/api/eventos", { tipo: "movimiento" });
  const fila = await uno("SELECT fuera_de_horario FROM Evento WHERE id_evento = ?", [ev.datos.id_evento]);
  await dormir(1200);
  const alertaMov = (await uno("SELECT COUNT(*) AS n FROM Alerta WHERE tipo = 'movimiento_fuera_de_horario'")).n;
  revisa(`movimiento ${fila.fuera_de_horario ? "FUERA" : "dentro"} de horario -> ${fila.fuera_de_horario ? "con" : "sin"} alerta`, alertaMov === (fila.fuera_de_horario ? 1 : 0));

  console.log("\n8. Falla del sensor");
  await dormir(1100); // la falla debe quedar en un segundo posterior a la ultima medicion
  await nodo("dht", "/api/eventos", { tipo: "sensor_error" });
  revisa("sensor_error abre sensor_falla", !!(await hasta(() => uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'sensor_falla' AND ts_fin IS NULL"))));
  await dormir(1100);
  await lectura(25, 50);
  revisa("la siguiente lectura valida la cierra", await hasta(async () => !(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'sensor_falla' AND ts_fin IS NULL"))));

  console.log("\n9. Nodo caido");
  await bd.query("UPDATE EstadoNodo SET ultimo_reporte = UTC_TIMESTAMP() - INTERVAL 200 SECOND WHERE id_nodo = 'luz'");
  revisa("200 s sin reporte abre nodo_sin_reporte", !!(await hasta(() => uno("SELECT 1 AS x FROM Alerta WHERE id_nodo = 'luz' AND tipo = 'nodo_sin_reporte' AND ts_fin IS NULL"))));
  revisa("y el nodo queda offline", (await uno("SELECT estado FROM EstadoNodo WHERE id_nodo = 'luz'")).estado === "offline");
  await nodo("luz", "/api/mediciones", { lecturas: [{ parametro: "luz", valor: 120 }] });
  revisa("al volver a reportar se cierra", await hasta(async () => !(await uno("SELECT 1 AS x FROM Alerta WHERE id_nodo = 'luz' AND tipo = 'nodo_sin_reporte' AND ts_fin IS NULL"))));
  escucha.publish("argos-eq2/invernadero/estado/acel", '{"estado":"offline"}');
  revisa("el LWT por MQTT marca offline al acel", await hasta(async () => (await uno("SELECT estado FROM EstadoNodo WHERE id_nodo = 'acel'")).estado === "offline"));

  console.log("\n10. Temperatura baja");
  await lectura(20, 50); await lectura(20, 50); await lectura(20, 50);
  revisa("temperatura baja abre alerta", !!(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'temperatura' AND ts_fin IS NULL")));
  await lectura(25, 50); await lectura(25, 50); await lectura(25, 50);
  revisa("y se cierra al normalizarse", !(await uno("SELECT 1 AS x FROM Alerta WHERE tipo = 'temperatura' AND ts_fin IS NULL")));

  console.log("\n11. Nodo apagado 20 dias (antes tumbaba al motor) y aviso inmediato");
  await bd.query("UPDATE EstadoNodo SET ultimo_reporte = UTC_TIMESTAMP() - INTERVAL 20 DAY WHERE id_nodo = 'luz'");
  const caido = await hasta(() => uno("SELECT id_alerta, valor FROM Alerta WHERE id_nodo = 'luz' AND tipo = 'nodo_sin_reporte' AND ts_fin IS NULL"));
  revisa("20 dias sin reporte abre la alerta (valor topado)", !!caido && caido.valor <= 999999, JSON.stringify(caido));
  await bd.query("INSERT INTO Configuracion (clave, valor) VALUES ('avisar_golpe', '1') ON DUPLICATE KEY UPDATE valor = '1'");
  await dormir(1500); // el motor relee Configuracion en cada revision
  const antes = (await uno("SELECT COUNT(*) AS n FROM Alerta WHERE tipo = 'golpe'")).n;
  await nodo("acel", "/api/eventos", { tipo: "golpe", magnitud: 1.1 });
  const golpe = await hasta(async () => (await uno("SELECT COUNT(*) AS n FROM Alerta WHERE tipo = 'golpe'")).n > antes);
  revisa("con un nodo caido 20 dias el motor sigue: el golpe hace alerta", !!golpe);
  revisa("avisar_golpe = 1 crea el aviso del golpe", !!(await hasta(() => uno("SELECT 1 AS x FROM Notificacion n JOIN Alerta a ON a.id_alerta = n.id_alerta WHERE a.tipo = 'golpe'"))));
  await nodo("acel", "/api/eventos", { tipo: "golpe", magnitud: 1.2 });
  await dormir(1500);
  revisa("un segundo golpe en 10 min no manda otro aviso", (await uno("SELECT COUNT(DISTINCT n.id_alerta) AS n FROM Notificacion n JOIN Alerta a ON a.id_alerta = n.id_alerta WHERE a.tipo = 'golpe'")).n === 1);
  const idA = (await uno("SELECT MAX(id_alerta) AS m FROM Alerta")).m;
  await dormir(2500); // 5 revisiones con la alerta de 'luz' activa
  await nodo("acel", "/api/eventos", { tipo: "golpe", magnitud: 1.3 });
  await hasta(async () => (await uno("SELECT MAX(id_alerta) AS m FROM Alerta")).m > idA);
  revisa("una alerta activa no gasta ids en cada revision", (await uno("SELECT MAX(id_alerta) AS m FROM Alerta")).m === idA + 1);
  revisa("el motor guarda hasta que evento reviso", Number((await uno("SELECT valor FROM Configuracion WHERE clave = 'central_ultimo_evento'")).valor) === (await uno("SELECT MAX(id_evento) AS m FROM Evento")).m);

  await bd.end();
  escucha.end(true);
  servidor.close();
  broker.close();
}

main()
  .catch((e) => { fallas++; console.error("ERROR DE LA PRUEBA:", e); })
  .finally(() => {
    for (const h of hijos) h.kill();
    console.log(`\n${pasadas} pasaron, ${fallas} fallaron`);
    setTimeout(() => process.exit(fallas ? 1 : 0), 300);
  });
