// Simulador de los 5 nodos de Argos: manda a las 5 API las mismas peticiones que los NodeMCU.
// Sirve para ensayar el panel y las alertas sin hardware, y como respaldo en la Expo si un nodo falla.
// No necesita instalar nada (Node 18 o mas nuevo). Con el servidor corriendo (servidor/arrancar.ps1):
//
//   node servidor/simulador_nodos.mjs TU_API_KEY                 ritmo real (dht cada 30 s, luz cada 60 s)
//   node servidor/simulador_nodos.mjs TU_API_KEY --rapido        10 veces mas rapido (para ensayar)
//   node servidor/simulador_nodos.mjs TU_API_KEY --solo=dht,luz  solo esos nodos (los demas, reales)
//   --host=192.168.1.50   si el servidor esta en otra PC
//
// Mientras corre, escribe una letra y Enter para provocar algo:
//   c  calor: la temperatura sube a 30 C (a la 3.a lectura se abre la alerta); c otra vez la regresa
//   p  abre o cierra la puerta          m  movimiento          g  golpe de 0.9 g
//   f  falla del sensor dht (deja de mandar lecturas); f otra vez lo arregla
//   x  apaga o prende el nodo luz (a los 150 s sale "sin conexion")          q  salir
// OJO: los datos se guardan en la base como si fueran reales. Para ensayar usa una base de pruebas.
import readline from "node:readline";

const args = process.argv.slice(2);
const clave = args.find((a) => !a.startsWith("--")) ?? process.env.API_KEY;
const opcion = (n, porOmision) => args.find((a) => a.startsWith(`--${n}=`))?.split("=")[1] ?? porOmision;
if (!clave) { console.error("Uso: node simulador_nodos.mjs TU_API_KEY [--rapido] [--solo=dht,luz] [--host=IP]"); process.exit(1); }
const host = opcion("host", "localhost");
const factor = args.includes("--rapido") ? 10 : 1;
const PUERTOS = { dht: 3001, luz: 3002, pir: 3003, puerta: 3004, acel: 3005 };
const activos = new Set(opcion("solo", Object.keys(PUERTOS).join(",")).split(","));
const inicio = Date.now();
const estado = { calor: false, falla: false, luzApagada: false, puertaAbierta: false, alarma: "off" };

async function enviar(nodo, ruta, cuerpo) {
  if (!activos.has(nodo)) return null;
  try {
    const r = await fetch(`http://${host}:${PUERTOS[nodo]}/api${ruta}`, {
      method: "POST", headers: { "x-api-key": clave, "Content-Type": "application/json" },
      body: JSON.stringify({ nodo, ...cuerpo }), signal: AbortSignal.timeout(4000),
    });
    const datos = await r.json().catch(() => ({}));
    if (r.status >= 400) console.log(`  [${nodo}] ${ruta} -> ${r.status} ${datos.error ?? ""}`);
    return datos;
  } catch (e) {
    console.log(`  [${nodo}] ${ruta}: la API del puerto ${PUERTOS[nodo]} no responde`);
    return null;
  }
}
const latido = (nodo) => enviar(nodo, "/latido", { uptime_s: Math.round((Date.now() - inicio) / 1000), rssi: -55 - Math.round(Math.random() * 15) });
const evento = (nodo, tipo, magnitud) => { console.log(`  [${nodo}] ${tipo}${magnitud ? " " + magnitud + " g" : ""}`); return enviar(nodo, "/eventos", magnitud ? { tipo, magnitud } : { tipo }); };
const led = (nodo, comando) => enviar(nodo, "/acciones", { actuador: "led_rojo", comando, origen: "local" });

let temp = 25, hum = 50;
async function cicloDht() {
  if (estado.falla) return;
  temp += ((estado.calor ? 30 : 25) - temp) * 0.6 + (Math.random() - 0.5) * 0.2;
  hum += (50 - hum) * 0.3 + (Math.random() - 0.5) * 0.8;
  const r = await enviar("dht", "/mediciones", { lecturas: [
    { parametro: "temperatura", valor: Math.round(temp * 10) / 10 }, { parametro: "humedad", valor: Math.round(hum * 10) / 10 }] });
  if (r?.alarma && r.alarma !== estado.alarma) { estado.alarma = r.alarma; console.log(`  [dht] el servidor dice: alarma ${r.alarma} (el buzzer ${r.alarma === "on" ? "sonaria" : "se calla"})`); }
  console.log(`  [dht] ${temp.toFixed(1)} C  ${hum.toFixed(0)} % HR`);
}
async function cicloLuz() {
  if (estado.luzApagada) return;
  const hora = Number(new Intl.DateTimeFormat("en-US", { timeZone: "America/Monterrey", hour: "numeric", hourCycle: "h23" }).format(new Date()));
  const valor = Math.round((hora >= 6 && hora < 22 ? 720 : 60) + (Math.random() - 0.5) * 30); // de 6 a 22 h: lamparas prendidas (horario inventado para el ensayo)
  await enviar("luz", "/mediciones", { lecturas: [{ parametro: "luz", valor }] });
}
async function movimiento() { await evento("pir", "movimiento"); await led("pir", "on"); setTimeout(() => led("pir", "off"), 5000 / factor); }
async function puerta() {
  estado.puertaAbierta = !estado.puertaAbierta;
  await evento("puerta", estado.puertaAbierta ? "puerta_abierta" : "puerta_cerrada");
  await led("puerta", estado.puertaAbierta ? "on" : "off");
}
async function golpe() { await evento("acel", "golpe", 0.9); await led("acel", "on"); setTimeout(() => led("acel", "off"), 5000 / factor); }

console.log(`Simulando ${[...activos].join(", ")} contra ${host}${factor > 1 ? " (10 veces mas rapido)" : ""}.  c calor · p puerta · m movimiento · g golpe · f falla dht · x apagar luz · q salir`);
await evento("puerta", "puerta_cerrada"); // estado inicial, como el firmware
await cicloDht(); await cicloLuz();
setInterval(cicloDht, 30000 / factor);
setInterval(cicloLuz, 60000 / factor);
setInterval(() => ["pir", "puerta", "acel"].forEach(latido), 60000 / factor);
["pir", "puerta", "acel"].forEach(latido);

readline.createInterface({ input: process.stdin }).on("line", async (linea) => {
  const t = linea.trim().toLowerCase();
  if (t === "c") { estado.calor = !estado.calor; console.log(estado.calor ? "  calor: sube a 30 C" : "  la temperatura regresa a 25 C"); }
  else if (t === "p") await puerta();
  else if (t === "m") await movimiento();
  else if (t === "g") await golpe();
  else if (t === "f") { estado.falla = !estado.falla; if (estado.falla) await evento("dht", "sensor_error"); else console.log("  [dht] sensor arreglado"); }
  else if (t === "x") { estado.luzApagada = !estado.luzApagada; console.log(estado.luzApagada ? "  [luz] apagado: deja de reportar" : "  [luz] prendido"); }
  else if (t === "q") process.exit(0);
}).on("close", () => {}); // sin teclado (corriendo en segundo plano) sigue mandando datos
