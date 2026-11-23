import "@fontsource-variable/space-grotesk";
import "@fontsource-variable/inter";
import "@fontsource-variable/jetbrains-mono";
import "./estilos/tokens.css";
import "./estilos/base.css";
import "./estilos/app.css";
import sprite from "./iconos.svg?raw";
import { hace, horaSeg } from "./formato.js";
import { pintarPrincipal } from "./principal.js";
import { iniciarHistorial, pintarHistorial } from "./historial.js";
import { colocarAlertas, pintarAnoche, pintarEpisodios } from "./alertas.js";
import { iniciarAjustes } from "./ajustes.js";

document.body.insertAdjacentHTML("afterbegin", sprite);

// ── tema: sigue al sistema hasta que se elige uno con el boton ──
const raiz = document.documentElement;
document.getElementById("tema").addEventListener("click", () => {
  const oscuroAhora = raiz.dataset.tema ? raiz.dataset.tema === "oscuro" : matchMedia("(prefers-color-scheme: dark)").matches;
  raiz.dataset.tema = oscuroAhora ? "claro" : "oscuro";
  try { localStorage.setItem("argos-tema", raiz.dataset.tema); } catch {}
  document.dispatchEvent(new Event("argos:tema"));
});

// ── datos: sondeo a /panel/datos (mismo origen que la pagina) ──
const SONDEO_MS = 5000;
const enlace = document.getElementById("enlace"), enlaceTexto = document.getElementById("enlaceTexto");
let horas = 24, ultimo = null, ultimaBuena = 0, pidiendo = false, pedido = 0;
// Solo en desarrollo: ?escenario=alerta elige los datos de prueba (herramientas/datos_prueba.mjs).
const extra = import.meta.env.DEV ? (new URLSearchParams(location.search).get("escenario") ?? "") : "";

async function actualizar(forzar = false) {
  if (pidiendo && !forzar) return; // la peticion anterior sigue en curso: no se enciman
  pidiendo = true;
  const mio = ++pedido;
  try {
    const r = await fetch(`panel/datos?horas=${horas}${extra ? `&escenario=${encodeURIComponent(extra)}` : ""}`, { cache: "no-store", signal: AbortSignal.timeout(15000) });
    if (!r.ok) throw new Error(r.status);
    const d = await r.json();
    if (mio !== pedido) return; // llego tarde: ya se pidio otro periodo
    ultimo = d; ultimaBuena = Date.now();
    pintarPrincipal(d);
    pintarHistorial(d);
    pintarAnoche(d);
    pintarEpisodios(d);
    enlace.className = "enlace enlace--ok";
    enlaceTexto.textContent = `Actualizado ${horaSeg(d.ahora)}`;
  } catch {
    if (mio !== pedido) return;
    enlace.className = "enlace enlace--caido";
    enlaceTexto.textContent = ultimaBuena ? `Sin respuesta · datos de ${hace((Date.now() - ultimaBuena) / 1000)}` : "Sin respuesta del servidor";
    if (ultimo) pintarPrincipal(ultimo, { caido: true, edadS: (Date.now() - ultimaBuena) / 1000 });
    else document.getElementById("avisos").innerHTML = `<div class="aviso aviso--offline"><span class="estado estado--offline">SIN RESPUESTA</span><div><div class="aviso__titulo">El servidor no responde</div><div class="aviso__det">Todavía no se recibe ningún dato. Se reintenta cada 5 s.</div></div></div>`;
  } finally {
    if (mio === pedido) pidiendo = false;
  }
}

iniciarHistorial({ alCambiarPeriodo: (h) => { horas = h; actualizar(true); } });
colocarAlertas();

// ── pestanas: #ahora y #historial (los avisos se ven en las dos) ──
function mostrarPestana() {
  const pedida = location.hash.slice(1);
  const cual = document.querySelector(`[data-vista="${CSS.escape(pedida)}"]`) ? pedida : "ahora";
  document.querySelectorAll("[data-vista]").forEach((v) => { v.hidden = v.dataset.vista !== cual; });
  document.querySelectorAll("[data-pestana]").forEach((a) => {
    if (a.dataset.pestana === cual) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  document.title = cual === "historial" ? "Argos · Historial" : "Argos · Cuarto de incubación";
  if (cual === "historial" && ultimo) pintarHistorial(ultimo); // las graficas toman su tamano al hacerse visibles
}
addEventListener("hashchange", () => { mostrarPestana(); scrollTo(0, 0); });
mostrarPestana();
// La pestana Ajustes solo existe si el central tiene cuenta de administrador.
iniciarAjustes({ umbrales: () => ultimo?.umbrales ?? [], alGuardar: () => actualizar(true) }).then((hay) => { if (hay) mostrarPestana(); });
actualizar();
setInterval(() => { if (!document.hidden) actualizar(); }, SONDEO_MS);
document.addEventListener("visibilitychange", () => { if (!document.hidden) actualizar(); });
