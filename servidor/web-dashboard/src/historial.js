// Historial: graficas de la medida contra el tiempo (temperatura, humedad, luz) con la banda del rango,
// y los eventos de puerta, movimiento y golpe en una lista.
import { Chart, LineController, LineElement, PointElement, LinearScale, Tooltip } from "chart.js";
import { cuando, diaHora, fecha, hora, mismoDia, NOMBRE_EVENTO, NOMBRE_NODO } from "./formato.js";

Chart.register(LineController, LineElement, PointElement, LinearScale, Tooltip);

const EJE_Y = 48; // ancho fijo del eje: las tres graficas quedan alineadas
const SERIES = [
  { id: "temperatura", titulo: "Temperatura", unidad: "°C", decimales: 1, holgura: 2 },
  { id: "humedad", titulo: "Humedad", unidad: "% HR", decimales: 0, holgura: 6, piso: 0, techo: 100 },
  { id: "luz", titulo: "Luz", unidad: "ADC", decimales: 0, holgura: 40, piso: 0, techo: 1023 },
];
const ICONO_NODO = { dht: "termometro", luz: "sol", pir: "ondas", puerta: "puerta", acel: "golpe" };
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

let horas = 24, ultimo = null, periodoPintado = null;
const graficas = {};

/** Banda del rango permitido y sus dos limites, dibujados detras de la linea. */
const bandaRango = {
  id: "bandaRango",
  beforeDatasetsDraw(chart) {
    const r = chart.options.plugins.bandaRango?.rango;
    if (!r) return;
    const { ctx, chartArea: a, scales: { y } } = chart;
    const arriba = Math.max(a.top, y.getPixelForValue(r.maximo)), abajo = Math.min(a.bottom, y.getPixelForValue(r.minimo));
    if (abajo <= arriba) return;
    ctx.save();
    ctx.fillStyle = css("--banda");
    ctx.fillRect(a.left, arriba, a.width, abajo - arriba);
    ctx.strokeStyle = css("--acento-texto"); ctx.lineWidth = 1.5; ctx.setLineDash([6, 4]);
    for (const py of [arriba, abajo]) { ctx.beginPath(); ctx.moveTo(a.left, py); ctx.lineTo(a.right, py); ctx.stroke(); }
    ctx.restore();
  },
};

function crearGrafica(s) {
  const lienzo = document.querySelector(`[data-grafica="${s.id}"] canvas`);
  return new Chart(lienzo, {
    type: "line",
    plugins: [bandaRango],
    data: { datasets: [{ data: [], borderWidth: 2.5, pointRadius: 0, pointHoverRadius: 5, pointHitRadius: 12, tension: 0, spanGaps: false }] },
    options: {
      responsive: true, maintainAspectRatio: false, parsing: false, normalized: true,
      animation: matchMedia("(prefers-reduced-motion: reduce)").matches ? false : { duration: 500, easing: "easeOutQuart" },
      interaction: { mode: "nearest", axis: "x", intersect: false },
      layout: { padding: { right: 8, top: 4 } },
      scales: {
        x: { type: "linear", grid: { display: false }, border: { display: true },
             // Marcas en horas redondas de Monterrey (UTC-6 fijo, sin horario de verano): cada 4 h, o cada dia en 7 dias.
             afterBuildTicks: (eje) => {
               const angosta = eje.width < 520; // en celular, la mitad de marcas
               const paso = (horas > 36 ? (angosta ? 48 : 24) : angosta ? 6 : 4) * 3600e3, corrimiento = 6 * 3600e3, marcas = [];
               for (let t = Math.ceil((eje.min - corrimiento) / paso) * paso + corrimiento; t <= eje.max; t += paso) marcas.push({ value: t });
               eje.ticks = marcas;
             },
             ticks: { autoSkip: false, maxRotation: 0, callback: (v) => (horas > 36 ? fecha(v) : hora(v)) } },
        y: { type: "linear", afterFit: (eje) => { eje.width = EJE_Y; }, ticks: { maxTicksLimit: 6, includeBounds: false } },
      },
      plugins: {
        legend: { display: false },
        bandaRango: { rango: null },
        tooltip: {
          displayColors: false, cornerRadius: 0, padding: 10, caretSize: 0,
          callbacks: { title: (it) => diaHora(it[0].parsed.x), label: (it) => `${it.parsed.y.toFixed(s.decimales)} ${s.unidad}` },
        },
      },
    },
  });
}

/** Colores del tema actual; se vuelve a llamar cuando cambia el tema. */
function vestir(chart, rango) {
  const tinta2 = css("--tinta-2"), linea = css("--linea"), serie = css("--tinta"), alerta = css("--alerta");
  const fMono = css("--f-mono"), fTexto = css("--f-texto");
  const ds = chart.data.datasets[0], o = chart.options;
  ds.borderColor = serie; ds.pointHoverBackgroundColor = serie;
  // Un tramo fuera del rango se pinta en color de alerta (ademas, se sale de la banda: no depende solo del color).
  ds.segment = { borderColor: (c) => (rango && [c.p0.parsed.y, c.p1.parsed.y].some((v) => v < rango.minimo || v > rango.maximo) ? alerta : undefined) };
  for (const eje of [o.scales.x, o.scales.y]) { eje.ticks.color = tinta2; eje.ticks.font = { family: fMono, size: 12 }; eje.border = { ...eje.border, color: css("--tinta-3") }; }
  o.scales.y.grid = { color: linea };
  o.plugins.tooltip.backgroundColor = css("--negro"); o.plugins.tooltip.titleColor = "#c9cbd3"; o.plugins.tooltip.bodyColor = "#fff";
  o.plugins.tooltip.titleFont = { family: fMono, size: 12, weight: "500" }; o.plugins.tooltip.bodyFont = { family: fTexto, size: 15, weight: "600" };
}

function pintarGraficas(d) {
  const hasta = new Date(d.ahora).getTime(), desde = hasta - d.horas * 3600e3, hueco = d.cubeta_s * 1000 * 3.5;
  const animar = periodoPintado !== d.horas;
  for (const s of SERIES) {
    const caja = document.querySelector(`[data-grafica="${s.id}"]`), chart = (graficas[s.id] ??= crearGrafica(s));
    const r = d.umbrales.find((u) => u.parametro === s.id) ?? null;
    const crudos = d.series.filter((x) => x.parametro === s.id).map((x) => ({ x: new Date(x.t).getTime(), y: x.valor }));
    // Un hueco largo corta la linea (el nodo estuvo apagado): no se inventa un tramo.
    const puntos = [];
    for (const p of crudos) { if (puntos.length && p.x - puntos[puntos.length - 1].x > hueco) puntos.push({ x: p.x - 1, y: null }); puntos.push(p); }
    const ys = crudos.map((p) => p.y);
    const lo = Math.min(...ys, r?.minimo ?? Infinity) - s.holgura, hi = Math.max(...ys, r?.maximo ?? -Infinity) + s.holgura;
    chart.data.datasets[0].data = puntos;
    Object.assign(chart.options.scales.x, { min: desde, max: hasta });
    Object.assign(chart.options.scales.y, { min: Math.max(s.piso ?? -Infinity, Math.floor(lo)), max: Math.min(s.techo ?? Infinity, Math.ceil(hi)) });
    chart.options.plugins.bandaRango.rango = r;
    vestir(chart, r);
    chart.update(animar ? undefined : "none");

    const vacio = crudos.length < 2;
    caja.classList.toggle("grafica--vacia", vacio);
    const resumen = caja.querySelector("[data-r=resumen]");
    if (vacio) { resumen.textContent = "Aún no hay lecturas suficientes en este periodo."; chart.canvas.setAttribute("aria-label", `${s.titulo}: sin lecturas en el periodo`); continue; }
    const mn = Math.min(...ys), mx = Math.max(...ys), fin = crudos[crudos.length - 1].y, n = (v) => v.toFixed(s.decimales);
    const fuera = r ? crudos.filter((p) => p.y < r.minimo || p.y > r.maximo).length / crudos.length : null;
    resumen.textContent = `mín ${n(mn)} · máx ${n(mx)} · último ${n(fin)} ${s.unidad}` + (r ? ` · rango ${r.minimo}–${r.maximo}` + (fuera > 0 ? ` · fuera de rango ${Math.max(1, Math.round(fuera * 100))} % del periodo` : " · siempre en rango") : "");
    chart.canvas.setAttribute("aria-label", `${s.titulo} de las últimas ${d.horas} horas: ${resumen.textContent}`);
  }
  periodoPintado = d.horas;
}

// ── eventos ──
const LIMITE_EVENTOS = 40; // el central entrega los ultimos 40
let firmaLista = "";
function pintarLista(d) {
  const caja = document.querySelector("[data-r=lista]");
  // Solo se redibuja si llego un evento nuevo o cambio el dia: asi no se pierde el desplazamiento de la lista.
  const firma = `${d.eventos.length}:${d.eventos[0]?.id_evento}:${fecha(d.ahora)}`;
  if (firma === firmaLista) return;
  firmaLista = firma;
  if (d.eventos.length === 0) { caja.innerHTML = `<p class="pie">Aún no hay eventos. Aquí aparecerán las aperturas de la puerta, los movimientos y los golpes.</p>`; return; }
  const ayer = new Date(new Date(d.ahora).getTime() - 86400e3).toISOString();
  let h = "", dia = null;
  for (const e of d.eventos) {
    const rotulo = mismoDia(e.fecha_hora, d.ahora) ? "Hoy" : mismoDia(e.fecha_hora, ayer) ? "Ayer" : fecha(e.fecha_hora);
    if (rotulo !== dia) { h += `${dia ? "</ol>" : ""}<h3 class="lista-ev__dia">${esc(rotulo)}</h3><ol class="lista-ev">`; dia = rotulo; }
    const detalle = e.magnitud != null ? ` de ${e.magnitud.toFixed(2)} g` : "";
    h += `<li><time datetime="${esc(e.fecha_hora)}">${esc(hora(e.fecha_hora))}</time><svg class="icono" aria-hidden="true"><use href="#i-${ICONO_NODO[e.id_nodo] ?? "ondas"}"/></svg><span class="lista-ev__texto">${esc(NOMBRE_EVENTO[e.tipo] ?? e.tipo)}${detalle}${e.fuera_de_horario ? ` <span class="chip">fuera de horario</span>` : ""}</span><span class="lista-ev__nodo">${esc((NOMBRE_NODO[e.id_nodo] ?? e.id_nodo).toLowerCase())}</span></li>`;
  }
  caja.innerHTML = h + "</ol>" + (d.eventos.length >= LIMITE_EVENTOS ? `<p class="pie">Se muestran los últimos ${LIMITE_EVENTOS} eventos.</p>` : "");
}

export function iniciarHistorial({ alCambiarPeriodo }) {
  const raiz = document.querySelector('[data-vista="historial"]');
  raiz.innerHTML = `
    <div class="historial__col">
    <div class="historial__cab">
      <h2 class="etiqueta">Argos / historial</h2>
      <div class="periodo" role="group" aria-label="Periodo del historial">
        <button type="button" data-h="24" aria-pressed="true">24 h</button><button type="button" data-h="168" aria-pressed="false">7 días</button>
      </div>
    </div>
    <div class="graficas">${SERIES.map((s) => `
      <section class="ventana grafica" data-grafica="${s.id}">
        <div class="ventana__barra"><span>${s.id} / tiempo</span><span>${s.unidad}</span></div>
        <div class="ventana__cuerpo"><div class="grafica__lienzo"><canvas role="img" aria-label="${s.titulo}"></canvas></div><p class="grafica__resumen" data-r="resumen"></p></div>
      </section>`).join("")}
    </div>
    </div>
`;
  raiz.querySelectorAll(".periodo button").forEach((b) => b.addEventListener("click", () => {
    horas = Number(b.dataset.h);
    raiz.querySelectorAll(".periodo button").forEach((o) => o.setAttribute("aria-pressed", String(o === b)));
    alCambiarPeriodo(horas);
  }));
  const revestir = () => { if (ultimo) { periodoPintado = null; pintarGraficas(ultimo); } };
  document.addEventListener("argos:tema", revestir);
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", revestir);
  document.fonts?.ready.then(revestir);
}

export function pintarHistorial(d) {
  ultimo = d;
  pintarGraficas(d);
  pintarLista(d);
}
