// Datos de prueba para desarrollar sin el central ni MySQL. Solo los usa `npm run dev`
// (vite.config.js); nunca entran en dist. Misma forma que GET /panel/datos de servidor/central/central.js.
// Escenarios: normal · alerta · caidos · sin_datos · error   (http://localhost:5173/?escenario=alerta)

const ORDEN_BD = ["dht", "pir", "puerta", "acel", "luz"]; // el central los entrega asi; el dashboard reordena
const FICHA = {
  dht: { descripcion: "Temperatura y humedad", sensor: "DHT22" },
  luz: { descripcion: "Luz", sensor: "LDR" },
  pir: { descripcion: "Movimiento", sensor: "HC-SR501" },
  puerta: { descripcion: "Puerta", sensor: "MC-38" },
  acel: { descripcion: "Golpes", sensor: "GY-61" },
};
const iso = (ms) => new Date(ms).toISOString();
const r1 = (v) => Math.round(v * 10) / 10;

export const ESCENARIOS = ["normal", "alerta", "silencio", "caidos", "sin_datos", "error"];

// Cuenta de prueba SOLO para `npm run dev` (datos falsos, nunca llega a dist ni al servidor real).
export const ADMIN_PRUEBA = { usuario: "admin", clave: "argos-prueba" };

export function generar(escenario = "normal", horas = 24, rangos = {}) {
  const ahora = Date.now();
  const cubeta = Math.max(30, Math.round((horas * 3600) / 288));
  const vacio = escenario === "sin_datos";
  const alerta = ["alerta", "silencio", "caidos"].includes(escenario);
  const caidos = escenario === "caidos";

  // lectura "viva": cambia un poco en cada sondeo para ver las animaciones
  const onda = Math.sin(ahora / 9000);
  const temp = r1((alerta ? 29.4 : 25.2) + onda * 0.3);
  const hum = r1(52 + Math.cos(ahora / 7000) * 1.5);

  const haceS = { dht: 12, luz: caidos ? 720 : 25, pir: 40, puerta: 35, acel: caidos ? null : 50 };
  const nodos = ORDEN_BD.map((id) => {
    const h = vacio ? null : haceS[id];
    return {
      id_nodo: id, descripcion: FICHA[id].descripcion, id_caja: 1, caja: "caja de prueba", responsable: "Equipo 2", sensor: FICHA[id].sensor,
      estado: h == null ? "offline" : h > 150 ? "offline" : "online",
      ultimo_reporte: h == null ? null : iso(ahora - h * 1000), rssi: h == null ? null : -61, uptime_s: h == null ? null : 5400, hace_s: h,
    };
  });

  const ultimos = vacio ? [] : [
    { id_nodo: "dht", parametro: "temperatura", unidad: "°C", valor: temp, fecha_hora: iso(ahora - 12000) },
    { id_nodo: "dht", parametro: "humedad", unidad: "%", valor: hum, fecha_hora: iso(ahora - 12000) },
    { id_nodo: "luz", parametro: "luz", unidad: "ADC", valor: 718, fecha_hora: iso(ahora - haceS.luz * 1000) },
  ];

  const series = [];
  if (!vacio) {
    const paso = cubeta * 1000, fin = Math.floor(ahora / paso) * paso, n = Math.floor((horas * 3600) / cubeta);
    for (let i = n; i >= 0; i--) {
      const t = fin - i * paso, dia = (t % 86400e3) / 86400e3;
      if (horas >= 24 && i > n * 0.55 && i < n * 0.62) continue; // hueco: el nodo estuvo apagado
      let T = 25 + Math.sin(dia * 2 * Math.PI) * 1.6 + Math.sin(t / 2.1e6) * 0.4;
      if (alerta && i < 6) T = 29.4 - i * 0.6;
      if (i > n * 0.3 && i < n * 0.34) T += 3.6; // episodio pasado fuera de rango
      const H = 50 + Math.cos(dia * 2 * Math.PI) * 6 + Math.sin(t / 1.7e6) * 2;
      series.push({ id_nodo: "dht", parametro: "temperatura", t: iso(t), valor: r1(T), minimo: r1(T - 0.2), maximo: r1(T + 0.2) });
      series.push({ id_nodo: "dht", parametro: "humedad", t: iso(t), valor: r1(H), minimo: r1(H - 1), maximo: r1(H + 1) });
      series.push({ id_nodo: "luz", parametro: "luz", t: iso(t), valor: dia > 0.5 || dia < 0.17 ? 720 : 60, minimo: 50, maximo: 730 });
    }
  }

  const umbrales = [
    { id_nodo: "dht", parametro: "temperatura", unidad: "°C", minimo: 22, maximo: 28, ...rangos.temperatura },
    { id_nodo: "dht", parametro: "humedad", unidad: "%", minimo: 40, maximo: 60, ...rangos.humedad },
  ];

  const min = 60000;
  const alertas = vacio ? [] : [
    ...(alerta ? [{ id_alerta: 9, id_nodo: "dht", tipo: "temperatura", valor: 29.4, ts_inicio: iso(ahora - 6 * min), ts_fin: null, grave: 0 }] : []),
    ...(caidos ? [{ id_alerta: 8, id_nodo: "luz", tipo: "nodo_sin_reporte", valor: null, ts_inicio: iso(ahora - 9.5 * min), ts_fin: null, grave: 0 }] : []),
    { id_alerta: 7, id_nodo: "puerta", tipo: "puerta_abierta", valor: null, ts_inicio: iso(ahora - 200 * min), ts_fin: iso(ahora - 188 * min), grave: 1 },
    { id_alerta: 6, id_nodo: "dht", tipo: "temperatura", valor: 28.9, ts_inicio: iso(ahora - 420 * min), ts_fin: iso(ahora - 395 * min), grave: 1 },
    { id_alerta: 5, id_nodo: "pir", tipo: "movimiento_fuera_de_horario", valor: null, ts_inicio: iso(ahora - 610 * min), ts_fin: iso(ahora - 610 * min), grave: 0 },
    { id_alerta: 4, id_nodo: "puerta", tipo: "puerta_abierta", valor: null, ts_inicio: iso(ahora - 700 * min), ts_fin: iso(ahora - 682 * min), grave: 1 },
  ];

  const ev = (id, nodo, tipo, haceMin, extra = {}) => ({ id_evento: id, id_nodo: nodo, tipo, magnitud: null, fuera_de_horario: 0, fecha_hora: iso(ahora - haceMin * min), ...extra });
  const eventos = vacio ? [] : [
    ev(31, "pir", "movimiento", 33),
    ev(30, "puerta", "puerta_cerrada", 40),
    ev(29, "puerta", "puerta_abierta", 42),
    ...(caidos ? [] : [ev(28, "acel", "golpe", 95, { magnitud: 0.9 })]),
    ev(27, "pir", "movimiento", 96),
    ev(26, "puerta", "puerta_cerrada", 188),
    ev(25, "puerta", "puerta_abierta", 203),
    ev(24, "pir", "movimiento", 204),
    ev(23, "pir", "movimiento", 610, { fuera_de_horario: 1 }),
    ev(22, "dht", "sensor_error", 900),
  ];
  const ultimo = (tipo) => eventos.find((e) => e.tipo === tipo);

  return {
    ahora: iso(ahora), horas, cubeta_s: cubeta, sin_reporte_s: 150,
    nodos, ultimos, series, umbrales, alertas, eventos,
    puerta: vacio ? null : { tipo: "puerta_cerrada", fecha_hora: iso(ahora - 40 * min) },
    ultimo_evento: Object.fromEntries(["golpe", "movimiento"].filter(ultimo).map((t) => [t, ultimo(t)])),
    ...(escenario === "silencio" ? { buzzer: { comando: "off", origen: "manual", duracion_s: 1800, fecha_hora: iso(ahora - 4 * min) } } : {}),
    config: { umbral_luz_adc: "400", puerta_abierta_max_s: "120" },
  };
}
