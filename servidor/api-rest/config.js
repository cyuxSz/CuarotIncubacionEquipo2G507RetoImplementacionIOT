// Configuracion de la API. Para usarla con otro nodo solo se cambia NODO: dht, luz, pir, puerta o acel.

// Por nodo: puerto de su API, mediciones que manda con su rango posible, y tipos de evento.
const NODOS = {
  dht:    { puerto: 3001, parametros: { temperatura: [-40, 80], humedad: [0, 100] }, eventos: ["sensor_error"] },
  luz:    { puerto: 3002, parametros: { luz: [0, 1023] },                             eventos: ["sensor_error"] },
  pir:    { puerto: 3003, parametros: {},                                             eventos: ["movimiento", "sensor_error"] },
  puerta: { puerto: 3004, parametros: {},                                             eventos: ["puerta_abierta", "puerta_cerrada", "sensor_error"] },
  acel:   { puerto: 3005, parametros: {},                                             eventos: ["golpe", "sensor_error"] },
};

const NODO = process.env.NODO;
if (!NODOS[NODO]) {
  console.error(`Falta NODO en el .env o no existe ("${NODO}"). Opciones: ${Object.keys(NODOS).join(", ")}`);
  process.exit(1);
}
if (!process.env.API_KEY) {
  console.error("Falta API_KEY en el .env: la API no arranca sin clave.");
  process.exit(1);
}

module.exports = {
  NODO,
  ...NODOS[NODO], // puerto, parametros, eventos de ESTE nodo
  PUERTO: Number(process.env.PUERTO || NODOS[NODO].puerto),
  API_KEY: process.env.API_KEY,
  BD: {
    host: process.env.DB_HOST || "localhost",
    port: Number(process.env.DB_PORT || 3306),
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME || "argos",
  },
};
