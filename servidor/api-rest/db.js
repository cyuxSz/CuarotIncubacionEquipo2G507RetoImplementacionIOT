// Conexion a MySQL con un pool: las conexiones se reutilizan entre peticiones.
const mysql = require("mysql2/promise");
const { BD } = require("./config");

const pool = mysql.createPool({
  ...BD,
  timezone: "Z",        // las fechas van y vienen en UTC
  decimalNumbers: true, // DECIMAL -> numero de JS (no texto)
  connectionLimit: 5,
});
// Cada conexion trabaja en UTC.
pool.pool.on("connection", (c) => c.query("SET time_zone = '+00:00'"));

// Prueba al arrancar: avisa si el usuario, la clave o el puerto estan mal.
pool.query("SELECT 1")
  .then(() => console.log(`Conectado a MySQL: ${BD.user}@${BD.host}:${BD.port}/${BD.database}`))
  .catch((e) => console.error("Error conectando a MySQL:", e.message));

module.exports = pool;
