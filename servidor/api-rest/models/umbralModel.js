// Decide cuando una medicion abre o cierra una alerta, con los valores de la tabla Umbral.
// Persistencia: se abre con N lecturas seguidas fuera de rango (N = 3).
// Histeresis: se cierra con N lecturas seguidas dentro del rango menos un margen.
// Ejemplo: se abre al pasar de 28 C y se cierra al bajar de 27.5 C.
const modelo = require("./nodoModel");

// Conteo en memoria por parametro: { fuera, dentro, alarma }
const vigilancia = new Map();

// Regresa "abrir", "cerrar" o null.
function evaluar(u, valor, s) {
  const n = u.persistencia;
  if (valor < u.minimo || valor > u.maximo) {                                         // fuera de rango
    s.dentro = 0;
    s.fuera = Math.min(s.fuera + 1, n);
    if (s.fuera >= n && !s.alarma) { s.alarma = true; return "abrir"; }
  } else if (valor >= u.minimo + u.histeresis && valor <= u.maximo - u.histeresis) {  // claramente dentro
    s.fuera = 0;
    s.dentro = Math.min(s.dentro + 1, n);
    if (s.dentro >= n && s.alarma) { s.alarma = false; return "cerrar"; }
  } else {                                                                            // zona de histeresis
    s.fuera = s.dentro = 0;
  }
  return null;
}

// Se llama despues de guardar las mediciones.
async function revisar(lecturas) {
  const umbrales = await modelo.leerUmbrales(); // se leen cada vez: si se editan en la BD, aplican solos
  for (const [parametro, valor] of lecturas) {
    const u = umbrales.find((x) => x.parametro === parametro);
    if (!u) continue; // parametro sin umbral
    if (!vigilancia.has(parametro)) {
      // Primera lectura desde que arranco la API: revisa si ya habia una alerta activa.
      const activas = await modelo.leerAlertas(true, 50);
      vigilancia.set(parametro, { fuera: 0, dentro: 0, alarma: activas.some((a) => a.tipo === parametro) });
    }
    const decision = evaluar(u, valor, vigilancia.get(parametro));
    if (decision === "abrir") {
      const id = await modelo.abrirAlerta(parametro, valor, u.id_umbral);
      if (id) console.log(`ALERTA ABIERTA #${id}: ${parametro} = ${valor} (rango ${u.minimo} a ${u.maximo})`);
      if (id && u.activa_buzzer) await modelo.guardarAccion("buzzer", "on", "alerta", null, id);
    }
    if (decision === "cerrar") {
      const id = await modelo.cerrarAlerta(parametro);
      if (id) console.log(`ALERTA CERRADA #${id}: ${parametro} = ${valor}`);
      if (id && u.activa_buzzer) await modelo.guardarAccion("buzzer", "off", "alerta", null, id);
    }
  }
}

module.exports = { revisar, evaluar };
