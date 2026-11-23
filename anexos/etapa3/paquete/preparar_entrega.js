/**
 * Argos (Equipo 2) — arma TU carpeta de entrega de la Etapa 3 con los nombres que pide Canvas.
 *
 * Uso (en una terminal, dentro de la carpeta del paquete):
 *     node preparar_entrega.js <nodo>
 *     node preparar_entrega.js <nodo> <matricula> "<Nombre completo>"     (si cambio quien lleva el nodo)
 *
 * Crea  entrega_<nodo>/  con:
 *     ScriptCreacionBaseDatos_iot_Equipo2.sql      el mismo para los cinco
 *     indicadores_iot_Equipo2-<matricula>.sql      tus tres indicadores
 *     RestApi-Equipo2-<matricula>/                 tu API REST (archivo principal con tu matricula)
 *     Arduino-Equipo2-<matricula>/                 tu programa del NodeMCU (.ino + .h)
 *
 * No toca tu MySQL ni instala nada: solo copia y renombra archivos.
 * Si la carpeta entrega_<nodo>/ ya existe, la vuelve a crear (lo que hayas cambiado ahi dentro se pierde).
 */
const fs = require("fs");
const path = require("path");

const EQUIPO = "2";
// Quien lleva cada nodo (11-nov-2026) y el puerto de su API.
const NODOS = {
  dht:    { matricula: "A01669847", nombre: "Luis Eduardo Mendoza Menéndez", puerto: 3001, sensor: "DHT22: temperatura y humedad" },
  luz:    { matricula: "A00845027", nombre: "Arianna Téllez",                puerto: 3002, sensor: "fotorresistencia: luz" },
  pir:    { matricula: "A00843900", nombre: "José María García",             puerto: 3003, sensor: "HC-SR501: movimiento" },
  puerta: { matricula: "A00227979", nombre: "Iván Acosta",                   puerto: 3004, sensor: "MC-38: puerta abierta o cerrada" },
  acel:   { matricula: "A00845663", nombre: "Mía Nieto",                     puerto: 3005, sensor: "GY-61 + ADS1115: golpes" },
};

const [nodo, matriculaArg, nombreArg] = process.argv.slice(2);
if (!NODOS[nodo]) {
  console.error(`Uso: node preparar_entrega.js <nodo>     nodos: ${Object.keys(NODOS).join(", ")}`);
  process.exit(1);
}
const matricula = matriculaArg || NODOS[nodo].matricula;
const nombre = nombreArg || NODOS[nodo].nombre;
const { puerto, sensor } = NODOS[nodo];
const sufijo = `Equipo${EQUIPO}-${matricula}`;

const AQUI = __dirname;
const SALIDA = path.join(AQUI, `entrega_${nodo}`);
const leer = (f) => fs.readFileSync(f, "utf8");
const escribir = (f, t) => fs.writeFileSync(f, t, "utf8");

fs.rmSync(SALIDA, { recursive: true, force: true });
fs.mkdirSync(SALIDA);

// 1. Script de la base: el mismo para todo el equipo.
fs.copyFileSync(path.join(AQUI, "01_base_de_datos", `ScriptCreacionBaseDatos_iot_Equipo${EQUIPO}.sql`),
  path.join(SALIDA, `ScriptCreacionBaseDatos_iot_Equipo${EQUIPO}.sql`));

// 2. Indicadores de tu nodo, con tu matricula en el nombre y en el encabezado.
const indicadores = `indicadores_iot_${sufijo}.sql`;
escribir(path.join(SALIDA, indicadores),
  leer(path.join(AQUI, "04_indicadores", `indicadores_${nodo}.sql`)).replace(/indicadores_iot_Equipo\d+-\w+\.sql/, indicadores));

// 3. API REST: se copia la base y se renombra el archivo principal.
const api = path.join(SALIDA, `RestApi-${sufijo}`);
fs.cpSync(path.join(AQUI, "02_api_rest"), api, {
  recursive: true,
  filter: (f) => !["node_modules", ".env"].includes(path.basename(f)),
});
const principalViejo = fs.readdirSync(api).find((f) => /^RestApi-Equipo\d+-\w+\.js$/.test(f));
fs.renameSync(path.join(api, principalViejo), path.join(api, `RestApi-${sufijo}.js`));
for (const f of ["package.json", "LEEME.md", `RestApi-${sufijo}.js`]) {
  let t = leer(path.join(api, f)).replace(/RestApi-Equipo\d+-\w+/g, `RestApi-${sufijo}`);
  if (f.endsWith(".js")) t = t.replace(/^ \* Autor:.*$/m, ` * Autor: ${nombre} (${matricula}) — nodo ${nodo} (${sensor}).`);
  escribir(path.join(api, f), t);
}
// El .env.example ya queda con tu nodo; tu lo copias como .env y pones tus claves.
escribir(path.join(api, ".env.example"), leer(path.join(api, ".env.example")).replace(/^NODO=.*$/m, `NODO=${nodo}`));
escribir(path.join(api, "pruebas.http"), pruebasHttp());

// 4. Programa del NodeMCU: la carpeta y el .ino deben llamarse igual (regla de Arduino IDE).
const ino = path.join(SALIDA, `Arduino-${sufijo}`);
fs.cpSync(path.join(AQUI, "03_firmware", `argos_${nodo}`), ino, {
  recursive: true,
  filter: (f) => path.basename(f) !== "secrets.h",
});
fs.renameSync(path.join(ino, `argos_${nodo}.ino`), path.join(ino, `Arduino-${sufijo}.ino`));

console.log(`Listo: ${SALIDA}`);
console.log(`  nodo ${nodo} · ${nombre} · ${matricula} · API en el puerto ${puerto}`);
console.log("Sigue con el paso 3 del LEEME.md (configurar y arrancar tu API).");

/** pruebas.http de tu nodo (extension REST Client de VS Code). El dht conserva el archivo completo. */
function pruebasHttp() {
  const original = leer(path.join(AQUI, "02_api_rest", "pruebas.http"));
  if (nodo === "dht") return original;
  const cabecera = `# Pruebas de la API del nodo ${nodo} (extension "REST Client" de VS Code: clic en "Send Request").
# Cambia @clave por la API_KEY de tu .env.
@url = http://localhost:${puerto}/api
@clave = TU_API_KEY

### Ficha del nodo y su ultimo valor
GET {{url}}/estado
x-api-key: {{clave}}

### Sin clave (401)
GET {{url}}/estado
`;
  const post = (ruta, cuerpo, titulo) => `
### ${titulo}
POST {{url}}/${ruta}
x-api-key: {{clave}}
Content-Type: application/json

${JSON.stringify(cuerpo)}
`;
  const get = (ruta, titulo) => `
### ${titulo}
GET {{url}}/${ruta}
x-api-key: {{clave}}
`;
  let cuerpo = "";
  if (nodo === "luz") {
    cuerpo += post("mediciones", { nodo, lecturas: [{ parametro: "luz", valor: 742 }] }, "Guardar una medicion valida (201)");
    cuerpo += post("mediciones", { nodo, lecturas: [{ parametro: "luz", valor: 5000 }] }, "Valor imposible: lo rechaza y no guarda (400)");
    cuerpo += get("mediciones?parametro=luz&limite=5", "Historial de luz (ultimas 5)");
  } else {
    const eventos = { pir: [{ tipo: "movimiento" }], puerta: [{ tipo: "puerta_abierta" }, { tipo: "puerta_cerrada" }], acel: [{ tipo: "golpe", magnitud: 1.8 }] }[nodo];
    for (const e of eventos) cuerpo += post("eventos", { nodo, ...e }, `Guardar un evento ${e.tipo} (201)`);
    cuerpo += post("eventos", { nodo, tipo: "evento_inventado" }, "Tipo de evento que no es de este nodo (400)");
    cuerpo += get("eventos?limite=10", "Ultimos eventos");
  }
  cuerpo += post("acciones", { nodo, actuador: "led_rojo", comando: "on", origen: "local", duracion_s: 5 }, "Evento de actuacion: LED rojo encendido 5 s (201)");
  cuerpo += get("acciones?limite=10", "Ultimos eventos de actuacion");
  cuerpo += post("latido", { nodo, uptime_s: 120, rssi: -60 }, "Latido: el nodo sigue vivo (200)");
  cuerpo += get("comandos", "Instrucciones para el nodo");
  cuerpo += get("datetime", "Fecha y hora del servidor");
  return cabecera + cuerpo;
}
