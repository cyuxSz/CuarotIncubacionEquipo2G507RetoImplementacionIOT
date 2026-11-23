// Toda peticion debe traer la cabecera x-api-key con la clave configurada.
const { API_KEY } = require("../config");

function validarApiKey(req, res, next) {
  const clave = req.headers["x-api-key"];
  if (!clave) return res.status(401).json({ error: "API Key no proporcionada" });
  if (clave !== API_KEY) return res.status(401).json({ error: "API Key no autorizada" });
  next();
}

module.exports = { validarApiKey };
