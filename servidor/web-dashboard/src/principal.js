// Pantalla principal: avisos, y una ventana por nodo (dht, luz, pir, puerta, acel, siempre en ese orden).
// El esqueleto esta en index.html; aqui solo se actualizan textos y clases, para que las transiciones
// de CSS reaccionen al cambio de cada dato.
import { cuando, hace, hora, segDesde, NOMBRE_ALERTA, NOMBRE_NODO, ORDEN_NODOS } from "./formato.js";

const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const $ = (raiz, r) => raiz.querySelector(`[data-r="${r}"]`);

/** Cambia un texto y, si de verdad cambio, dispara la animacion "cambia". */
function texto(el, valor, animar = false) {
  if (el.textContent === valor) return;
  const primera = el.textContent === "" || el.textContent === "—";
  el.textContent = valor;
  if (primera || !animar) return;
  // El valor cambia al instante y la barra de su ventana destella (opcion C, elegida por Ivan).
  const ventana = el.closest(".ventana");
  if (!ventana) return;
  ventana.classList.remove("toca");
  void ventana.offsetWidth; // reinicia la animacion
  ventana.classList.add("toca");
}
function chip(el, tipo, rotulo) {
  el.className = `estado estado--${tipo}`;
  texto(el, rotulo, true);
}

function pintarLectura(caja, d, parametro, decimales, unidad, caido) {
  const u = d.ultimos.find((x) => x.parametro === parametro);
  const r = d.umbrales.find((x) => x.parametro === parametro);
  const dato = caja.querySelector(".dato"), pupila = $(caja, "pupila");
  const edad = u ? segDesde(u.fecha_hora, d.ahora) : null;
  const viejo = !u || caido || edad > d.sin_reporte_s; // con el servidor caido, todo dato es viejo
  const rango = r ? `Rango ${r.minimo}–${r.maximo} ${unidad}` : "Rango sin definir";

  if (r) {
    const tramo = r.maximo - r.minimo, lo = r.minimo - tramo, hi = r.maximo + tramo;
    const pct = (v) => Math.min(100, Math.max(0, ((v - lo) / (hi - lo)) * 100));
    $(caja, "banda").style.cssText = `left:${pct(r.minimo)}%;right:${100 - pct(r.maximo)}%`;
    for (const [k, v] of [["min", r.minimo], ["max", r.maximo]]) { $(caja, k).style.left = `${pct(v)}%`; $(caja, k).textContent = v; }
    if (u) pupila.style.left = `${pct(u.valor)}%`;
  }
  pupila.hidden = viejo || !r;

  if (!u) {
    texto($(caja, "valor"), "—");
    dato.className = "dato dato--apagado";
    chip($(caja, "rango"), "sin-datos", "SIN DATOS");
    texto($(caja, "pie"), `${rango} · aún no llega ninguna lectura`);
    return;
  }
  texto($(caja, "valor"), u.valor.toFixed(decimales), true);
  if (viejo) {
    dato.className = "dato dato--apagado";
    chip($(caja, "rango"), "offline", "DATO VIEJO");
    texto($(caja, "pie"), `${rango} · último dato ${hace(edad)}`);
    return;
  }
  const fuera = r && (u.valor < r.minimo || u.valor > r.maximo);
  dato.className = fuera ? "dato dato--alerta" : "dato";
  pupila.classList.toggle("regla__pupila--alerta", !!fuera);
  if (!r) chip($(caja, "rango"), "sin-datos", "SIN RANGO");
  else if (fuera) chip($(caja, "rango"), "alerta", u.valor > r.maximo ? "ALTA" : "BAJA");
  else chip($(caja, "rango"), "ok", "EN RANGO");
  texto($(caja, "pie"), `${rango} · ${hace(edad)}`);
}

function valorNodo(id, d, vivo) {
  const ultimoEv = (tipo) => d.ultimo_evento?.[tipo] ?? d.eventos.find((e) => e.tipo === tipo);
  if (id === "luz") {
    const u = d.ultimos.find((x) => x.parametro === "luz"), limite = Number(d.config?.umbral_luz_adc);
    if (!u) return ["—", "Aún no llega ninguna lectura"];
    const edad = hace(segDesde(u.fecha_hora, d.ahora)), lectura = `Lectura ${Math.round(u.valor)} de 1023`;
    const estado = Number.isFinite(limite) ? (u.valor >= limite ? "Encendidas" : "Apagadas") : String(Math.round(u.valor));
    return [estado, vivo ? `${lectura} · ${edad}` : `Último dato ${edad}`];
  }
  if (id === "pir") {
    const m = ultimoEv("movimiento");
    if (!m) return ["—", "Sin movimiento registrado"];
    return [cuando(m.fecha_hora, d.ahora), `Último movimiento, ${hace(segDesde(m.fecha_hora, d.ahora))}${m.fuera_de_horario ? " · fuera de horario" : ""}`];
  }
  if (id === "puerta") {
    const p = d.puerta;
    if (!p) return ["—", "Sin eventos de puerta"];
    return [p.tipo === "puerta_abierta" ? "Abierta" : "Cerrada", `Desde las ${cuando(p.fecha_hora, d.ahora)} · ${hace(segDesde(p.fecha_hora, d.ahora))}`];
  }
  const g = ultimoEv("golpe");
  if (!g) return ["—", "Sin golpes registrados"];
  return [g.magnitud != null ? `${g.magnitud.toFixed(2)} g` : "Golpe", `Último golpe: ${cuando(g.fecha_hora, d.ahora)} · ${hace(segDesde(g.fecha_hora, d.ahora))}`];
}

const estaVivo = (n, d) => !!n && n.hace_s != null && n.hace_s <= d.sin_reporte_s && n.estado === "online";

function pintarNodos(d, caido) {
  const activas = d.alertas.filter((a) => !a.ts_fin);
  for (const id of ORDEN_NODOS) {
    const caja = document.querySelector(`[data-nodo="${id}"]`);
    const n = d.nodos.find((x) => x.id_nodo === id);
    const nunca = !n || n.hace_s == null;
    const vivo = !caido && estaVivo(n, d);
    chip($(caja, "chip"), nunca ? "sin-datos" : vivo ? "linea" : "offline", nunca ? "SIN DATOS" : vivo ? "EN LÍNEA" : caido ? "DATO VIEJO" : "SIN CONEXIÓN");
    caja.classList.toggle("nodo--apagado", !vivo);
    // Un nodo sin conexion se ve gris y punteado, no rojo: su aviso ya esta arriba.
    caja.classList.toggle("nodo--alerta", vivo && activas.some((a) => a.id_nodo === id && a.tipo !== "nodo_sin_reporte"));
    caja.title = nunca ? "Nunca ha reportado" : `Último reporte ${hace(n.hace_s)}${n.rssi != null ? ` · WiFi ${n.rssi} dBm` : ""}`;
    if (id === "dht") {
      pintarLectura(caja.querySelector('[data-lectura="temperatura"]'), d, "temperatura", 1, "°C", caido);
      pintarLectura(caja.querySelector('[data-lectura="humedad"]'), d, "humedad", 0, "% HR", caido);
    } else {
      const [valor, pie] = valorNodo(id, d, vivo);
      texto($(caja, "valor"), valor, true);
      texto($(caja, "pie"), nunca && valor === "—" ? "Nunca ha reportado" : pie);
    }
  }
}

function tituloAlerta(a, d) {
  if (a.tipo === "temperatura" || a.tipo === "humedad") {
    const u = d.ultimos.find((x) => x.parametro === a.tipo), r = d.umbrales.find((x) => x.parametro === a.tipo);
    const v = u?.valor ?? a.valor, nombre = a.tipo === "temperatura" ? "Temperatura" : "Humedad", unidad = a.tipo === "temperatura" ? "°C" : "% HR";
    if (v != null && r) return `${nombre} ${v > r.maximo ? "alta" : v < r.minimo ? "baja" : "fuera de rango"}: ${v} ${unidad}`;
  }
  return NOMBRE_ALERTA[a.tipo] ?? a.tipo;
}

let firmaAvisos = "";
function pintarAvisos(d, caido) {
  const activas = d.alertas.filter((a) => !a.ts_fin)
    .sort((a, b) => ORDEN_NODOS.indexOf(a.id_nodo) - ORDEN_NODOS.indexOf(b.id_nodo));
  const alarma = activas.some((a) => a.tipo === "temperatura" || a.tipo === "humedad");
  const filas = activas.map((a) => ({
    clave: a.id_alerta, grave: !!a.grave, titulo: tituloAlerta(a, d),
    detalle: `${NOMBRE_NODO[a.id_nodo] ?? a.id_nodo} · desde las ${cuando(a.ts_inicio, d.ahora)} (${hace(segDesde(a.ts_inicio, d.ahora))})`,
  }));
  // Silencio del buzzer: solo si el central entrega el campo opcional `buzzer` (ver PARA_JOSE_MARIA_cambio_central.md).
  const b = d.buzzer;
  const finSilencio = b && b.comando === "off" && b.origen === "manual" && b.duracion_s ? new Date(b.fecha_hora).getTime() + b.duracion_s * 1000 : 0;
  const silenciada = alarma && finSilencio > new Date(d.ahora).getTime();
  const rotuloAlarma = silenciada ? `Alarma silenciada hasta las ${hora(finSilencio)}` : alarma ? "Alarma del cuarto activa" : "Alarma en reposo";
  // Veredicto en calma: verde solo si de verdad se sabe que todo esta bien.
  const callados = ORDEN_NODOS.filter((id) => !estaVivo(d.nodos.find((n) => n.id_nodo === id), d));
  const calma = callados.length === ORDEN_NODOS.length ? ["sin-datos", "SIN INFORMACIÓN", "Ningún nodo está reportando"]
    : callados.length ? ["offline", "INCOMPLETO", `Sin alertas, pero no ${callados.length === 1 ? "reporta" : "reportan"}: ${callados.map((id) => (NOMBRE_NODO[id] ?? id).toLowerCase()).join(", ")}`]
    : ["ok", "SIN ALERTAS", "No hay alertas activas"];
  // La firma no incluye el valor ni el "hace N min": esos textos se actualizan en su sitio, sin redibujar ni reanunciar.
  const firma = JSON.stringify([filas.map((f) => [f.clave, f.grave]), rotuloAlarma, caido ? hora(d.ahora) : 0, calma]);
  const cajaAvisos = document.getElementById("avisos");
  if (firma === firmaAvisos) {
    for (const f of filas) {
      const fila = cajaAvisos.querySelector(`[data-alerta="${f.clave}"]`);
      if (!fila) continue;
      fila.querySelector(".aviso__titulo").textContent = f.titulo;
      fila.querySelector(".aviso__det").textContent = f.detalle;
    }
    return;
  }
  firmaAvisos = firma;
  document.getElementById("anuncio").textContent = caido ? "El servidor no responde."
    : filas.length ? `${filas.length === 1 ? "Alerta activa" : filas.length + " alertas activas"}: ${filas.map((f) => f.titulo).join("; ")}. ${rotuloAlarma}.`
    : `${calma[2]}.`;

  const campana = `<div class="aviso__alarma"><svg class="icono" aria-hidden="true"><use href="#i-campana${alarma && !silenciada ? "" : "-off"}"/></svg>${esc(rotuloAlarma)}</div>`;
  let h = "";
  if (caido) h += `<div class="aviso aviso--offline"><span class="estado estado--offline">SIN RESPUESTA</span><div><div class="aviso__titulo">El servidor no responde</div><div class="aviso__det">Se muestran los últimos datos recibidos, de las ${esc(hora(d.ahora))}.</div></div></div>`;
  if (filas.length === 0) { if (!caido) h += `<div class="aviso aviso--calma"><span class="estado estado--${calma[0]}">${calma[1]}</span><div class="aviso__titulo">${esc(calma[2])}</div>${callados.length === ORDEN_NODOS.length ? "" : campana}</div>`; }
  else h += filas.map((f, i) => `<div class="aviso aviso--alerta" data-alerta="${f.clave}"><span class="estado estado--alerta">${f.grave ? "ALERTA GRAVE" : "ALERTA"}</span><div><div class="aviso__titulo">${esc(f.titulo)}</div><div class="aviso__det">${esc(f.detalle)}</div></div>${i === 0 ? campana : ""}</div>`).join("");
  cajaAvisos.innerHTML = h;
}

/** `edadS`: segundos desde la ultima respuesta buena, para envejecer los datos cuando el servidor no responde. */
export function pintarPrincipal(d, { caido = false, edadS = 0 } = {}) {
  if (caido) {
    d = { ...d, ahora: new Date(new Date(d.ahora).getTime() + edadS * 1000).toISOString(),
          nodos: d.nodos.map((n) => ({ ...n, hace_s: n.hace_s == null ? null : n.hace_s + edadS })) };
  }
  pintarAvisos(d, caido);
  pintarNodos(d, caido);
}
