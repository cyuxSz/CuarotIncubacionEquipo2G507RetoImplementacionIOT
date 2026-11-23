// Fechas y textos. La base guarda UTC; todo se muestra en hora de Monterrey.
const ZONA = "America/Monterrey";
const f = (o) => new Intl.DateTimeFormat("es-MX", { timeZone: ZONA, hour12: false, ...o });
const fHora = f({ hour: "2-digit", minute: "2-digit" });
const fSeg = f({ hour: "2-digit", minute: "2-digit", second: "2-digit" });
const fDia = f({ day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
const fFecha = f({ day: "numeric", month: "short" });
const fClaveDia = f({ year: "numeric", month: "2-digit", day: "2-digit" });

export const hora = (iso) => fHora.format(new Date(iso));
export const horaSeg = (iso) => fSeg.format(new Date(iso));
export const diaHora = (iso) => fDia.format(new Date(iso));
export const fecha = (iso) => fFecha.format(new Date(iso));
export const mismoDia = (a, b) => fClaveDia.format(new Date(a)) === fClaveDia.format(new Date(b));
/** Hora sola si es de hoy; con fecha si es de otro dia. */
export const cuando = (iso, ahora) => (mismoDia(iso, ahora) ? hora(iso) : diaHora(iso));

export const segDesde = (iso, ahora) => (iso ? (new Date(ahora) - new Date(iso)) / 1000 : null);
export function hace(s) {
  if (s == null) return "sin datos";
  if (s < 60) return `hace ${Math.max(0, Math.round(s))} s`;
  if (s < 3600) return `hace ${Math.round(s / 60)} min`;
  if (s < 86400) return `hace ${Math.round(s / 3600)} h`;
  return `hace ${Math.round(s / 86400)} d`;
}
export function duracion(s) {
  if (s < 60) return `${Math.round(s)} s`;
  if (s < 3600) return `${Math.round(s / 60)} min`;
  return `${Math.floor(s / 3600)} h ${Math.round((s % 3600) / 60)} min`;
}

export const ORDEN_NODOS = ["dht", "luz", "pir", "puerta", "acel"];
export const NOMBRE_NODO = { dht: "Temperatura y humedad", luz: "Luz", pir: "Presencia", puerta: "Puerta", acel: "Golpes" };
export const NOMBRE_ALERTA = {
  temperatura: "Temperatura fuera de rango", humedad: "Humedad fuera de rango", puerta_abierta: "Puerta abierta de más",
  nodo_sin_reporte: "Nodo sin reportar", sensor_falla: "Falla de sensor", golpe: "Golpe en el anaquel",
  movimiento_fuera_de_horario: "Movimiento fuera de horario", luz: "Luz fuera de horario",
};
export const NOMBRE_EVENTO = {
  movimiento: "Movimiento", golpe: "Golpe", puerta_abierta: "Puerta abierta", puerta_cerrada: "Puerta cerrada", sensor_error: "Error de sensor",
};
