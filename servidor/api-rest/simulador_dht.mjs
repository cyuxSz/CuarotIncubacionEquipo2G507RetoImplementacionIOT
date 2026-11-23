// Simulador del nodo dht: manda a la API las mismas peticiones que el NodeMCU.
// Uso, con la API corriendo: node simulador_dht.mjs TU_API_KEY [segundos] [puerto]
const clave = process.argv[2] ?? process.env.API_KEY;
const cadaS = Number(process.argv[3] ?? 5);
const puerto = process.argv[4] ?? 3001;
if (!clave) { console.error("Uso: node simulador_dht.mjs TU_API_KEY [segundos] [puerto]"); process.exit(1); }

const base = `http://localhost:${puerto}/api`;
const inicio = Date.now();
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));

async function enviar(ruta, cuerpo) {
  const r = await fetch(base + ruta, {
    method: "POST",
    headers: { "x-api-key": clave, "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo),
  });
  return { codigo: r.status, datos: await r.json().catch(() => ({})) };
}

// Escenario: 6 lecturas normales, 5 con calor (>28 C, abre la alerta a la 3.a), 5 normales (cierra a la 3.a).
const normal = [24, 25, 25, 26, 25, 24];
const calor = [30, 31, 31, 30, 30];
const vuelta = [25, 25, 24, 24, 24];
const escenario = [...normal, ...calor, ...vuelta].map((t, i) => ({ t, h: 45 + (i % 4) * 3 })); // DHT11: sin decimales

let alarmaAntes = "off";
console.log(`Simulador dht -> ${base} (una lectura cada ${cadaS} s). Ctrl+C para parar.\n`);
for (let n = 0; ; n = (n + 1) % escenario.length) {
  const { t, h } = escenario[n];
  const m = await enviar("/mediciones", {
    nodo: "dht",
    lecturas: [{ parametro: "temperatura", valor: t }, { parametro: "humedad", valor: h }],
  });
  console.log(`[api] POST /api/mediciones T=${t} C H=${h} % -> ${m.codigo}  alarma=${m.datos.alarma ?? "?"}`);
  if (m.codigo >= 400) console.log("      ", JSON.stringify(m.datos));

  const alarma = m.datos.alarma ?? "off";
  if (alarma !== alarmaAntes) {   // el LED rojo cambia con la alarma; el nodo real lo registra asi
    const a = await enviar("/acciones", { nodo: "dht", actuador: "led_rojo", comando: alarma, origen: "local" });
    console.log(`[api] POST /api/acciones led_rojo=${alarma} -> ${a.codigo}`);
    alarmaAntes = alarma;
  }
  if (n % 3 === 2) {
    const l = await enviar("/latido", { nodo: "dht", uptime_s: Math.round((Date.now() - inicio) / 1000), rssi: -60 });
    console.log(`[api] POST /api/latido -> ${l.codigo}`);
  }
  await dormir(cadaS * 1000);
}
