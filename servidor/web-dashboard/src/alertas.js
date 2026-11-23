// W4: alertas por episodio (inicio, duracion, grave) y resumen de la noche (22:00 a 7:00, el horario en que
// n8n no manda avisos y los junta para las 7:00). Todo sale de GET /panel/datos; no pide nada mas al servidor.
import { cuando, duracion, hora, NOMBRE_ALERTA, NOMBRE_NODO } from "./formato.js";

const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const ms = (iso) => new Date(iso).getTime();
const LIMITE = 40; // el central entrega como mucho 40 alertas y 40 eventos
const NOCHE_INICIO = 22, NOCHE_FIN = 7; // horas de Monterrey
const UTC_MTY = 6 * 3600e3; // Monterrey = UTC-6 fijo, sin horario de verano

/** Golpe y movimiento fuera de horario son alertas instantaneas: abren y cierran en el mismo momento. */
const duro = (a, hasta) => { const s = ((a.ts_fin ? ms(a.ts_fin) : hasta) - ms(a.ts_inicio)) / 1000; return s < 1 ? "instantánea" : duracion(s); };
const nombreNodo = (id) => (NOMBRE_NODO[id] ?? id).toLowerCase();
function tituloAlerta(a) {
  const base = NOMBRE_ALERTA[a.tipo] ?? a.tipo;
  if (a.valor == null) return base;
  if (a.tipo === "temperatura") return `${base} (${a.valor} °C)`;
  if (a.tipo === "humedad") return `${base} (${a.valor} % HR)`;
  return base;
}

/** La noche mas reciente: la que esta en curso si son entre 22:00 y 7:00; si no, la que acaba de terminar. */
function nocheReciente(ahoraIso) {
  const ahora = ms(ahoraIso), local = new Date(ahora - UTC_MTY); // sus campos UTC son la hora de Monterrey
  const h = local.getUTCHours();
  const medianoche = Date.UTC(local.getUTCFullYear(), local.getUTCMonth(), local.getUTCDate()) + UTC_MTY;
  const enCurso = h >= NOCHE_INICIO || h < NOCHE_FIN;
  const inicio = medianoche + (h >= NOCHE_INICIO ? NOCHE_INICIO : NOCHE_INICIO - 24) * 3600e3;
  const fin = enCurso ? ahora : medianoche + NOCHE_FIN * 3600e3;
  return { inicio, fin, enCurso };
}

export function pintarAnoche(d) {
  const caja = document.querySelector("[data-r=anoche]");
  if (!caja) return;
  const { inicio, fin, enCurso } = nocheReciente(d.ahora);
  const dentro = (t) => t >= inicio && t <= fin;
  // Alertas que empezaron en la noche o que seguian abiertas al empezar.
  const alertas = d.alertas.filter((a) => ms(a.ts_inicio) <= fin && (a.ts_fin ? ms(a.ts_fin) : Infinity) >= inicio)
    .sort((a, b) => ms(a.ts_inicio) - ms(b.ts_inicio));
  const eventos = d.eventos.filter((e) => dentro(ms(e.fecha_hora)));
  const cuenta = (tipo) => eventos.filter((e) => e.tipo === tipo).length;
  const fuera = eventos.filter((e) => e.tipo === "movimiento" && e.fuera_de_horario).length;
  // Si la lista de 40 eventos no alcanza a cubrir toda la noche, los conteos son un minimo.
  const masViejo = d.eventos.length >= LIMITE ? Math.min(...d.eventos.map((e) => ms(e.fecha_hora))) : -Infinity;
  const parcial = masViejo > inicio;
  const cuantos = (n, uno, varios) => `${parcial ? "al menos " : ""}${n} ${n === 1 ? uno : varios}`;

  const graves = alertas.filter((a) => a.grave).length;
  const titular = alertas.length === 0 ? (enCurso ? "Noche sin alertas hasta ahora" : "Noche sin alertas")
    : `${alertas.length} ${alertas.length === 1 ? "alerta" : "alertas"}${graves ? `, ${graves} ${graves === 1 ? "grave" : "graves"}` : ""}`;
  const datos = [
    ["i-puerta", cuantos(cuenta("puerta_abierta"), "apertura de puerta", "aperturas de puerta")],
    ["i-ondas", cuantos(cuenta("movimiento"), "movimiento", "movimientos") + (fuera ? ` (${fuera} fuera de horario)` : "")],
    ["i-golpe", cuantos(cuenta("golpe"), "golpe", "golpes")],
  ];
  caja.innerHTML = `
    <p class="anoche__periodo">${enCurso ? "Esta noche, desde las" : "De las"} ${esc(hora(inicio))}${enCurso ? "" : ` a las ${esc(hora(fin))}`}</p>
    <p class="anoche__titular"><span class="estado estado--${alertas.length ? "alerta" : "ok"}">${alertas.length ? "CON ALERTAS" : "SIN ALERTAS"}</span>${esc(titular)}</p>
    ${alertas.length ? `<ul class="anoche__alertas">${alertas.map((a) => `<li><time>${esc(cuando(a.ts_inicio, d.ahora))}</time> ${esc(tituloAlerta(a))} · ${esc(nombreNodo(a.id_nodo))} · ${a.ts_fin ? (duro(a) === "instantánea" ? "instantánea" : `duró ${esc(duro(a))}`) : "sigue activa"}</li>`).join("")}</ul>` : ""}
    <ul class="anoche__datos">${datos.map(([icono, texto]) => `<li><svg class="icono" aria-hidden="true"><use href="#${icono}"/></svg>${esc(texto)}</li>`).join("")}</ul>
    ${parcial ? `<p class="pie">Los conteos son un mínimo: el servidor entrega solo los últimos ${LIMITE} eventos.</p>` : ""}`;
}

export function pintarEpisodios(d) {
  const caja = document.querySelector("[data-r=episodios]");
  if (!caja) return;
  const periodo = d.horas >= 48 ? `${Math.round(d.horas / 24)} días` : `${d.horas} h`;
  const rotulo = document.querySelector("[data-r=episodios-periodo]");
  if (rotulo) rotulo.textContent = `últimas ${periodo}`;
  if (d.alertas.length === 0) { caja.innerHTML = `<p class="pie">No hubo alertas en las últimas ${esc(periodo)}.</p>`; return; }
  const ahora = ms(d.ahora);
  caja.innerHTML = `<div class="desliza"><table class="episodios">
    <thead><tr><th scope="col">Inicio</th><th scope="col">Alerta</th><th scope="col">Nodo</th><th scope="col">Duración</th><th scope="col">Estado</th></tr></thead>
    <tbody>${d.alertas.map((a) => {
      const dur = duro(a, ahora);
      const estado = a.ts_fin ? `<span class="chip">cerrada ${esc(hora(a.ts_fin))}</span>` : `<span class="estado estado--alerta">ACTIVA</span>`;
      return `<tr${a.ts_fin ? "" : ' class="episodios__activa"'}><td class="n">${esc(cuando(a.ts_inicio, d.ahora))}</td><td>${esc(tituloAlerta(a))}</td><td>${esc(nombreNodo(a.id_nodo))}</td><td class="n">${esc(dur)}${a.ts_fin ? "" : " y sigue"}</td><td>${estado}${a.grave ? ` <span class="chip chip--grave">grave</span>` : ""}</td></tr>`;
    }).join("")}</tbody></table></div>
    ${d.alertas.length >= LIMITE ? `<p class="pie">Se muestran las ${LIMITE} más recientes.</p>` : ""}`;
}

const VENTANA_ANOCHE = `<section class="ventana anoche" aria-label="Resumen de la noche"><div class="ventana__barra"><h3 class="ventana__nombre">resumen de la noche</h3><span>22:00 a 7:00</span></div><div class="ventana__cuerpo" data-r="anoche"></div></section>`;
const VENTANA_EPISODIOS = `<section class="ventana" aria-label="Alertas del periodo"><div class="ventana__barra"><h3 class="ventana__nombre">alertas / episodios</h3><span data-r="episodios-periodo"></span></div><div class="ventana__cuerpo" data-r="episodios"></div></section>`;

/** Coloca las dos ventanas: el resumen de la noche en Ahora, junto a los eventos; los episodios en Historial. */
export function colocarAlertas() {
  const eventos = document.querySelector('[data-vista="ahora"] .eventos');
  eventos.classList.add("eventos--dos");
  eventos.insertAdjacentHTML("beforeend", VENTANA_ANOCHE);
  eventos.previousElementSibling.textContent = "Argos / eventos recientes y anoche";
  document.querySelector('[data-vista="historial"]').insertAdjacentHTML("beforeend",
    `<div class="bloque"><h2 class="etiqueta">Argos / alertas del periodo</h2>${VENTANA_EPISODIOS}</div>`);
}
