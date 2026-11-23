// Copia dist/ a servidor/web para que el servicio central lo sirva (express.static).
// El panel anterior se guarda una sola vez como servidor/web/panel_anterior.html.
// Uso:  npm run build && npm run publicar
import { cpSync, existsSync, readdirSync, readFileSync, renameSync, rmSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const raiz = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(raiz, "dist");
const web = join(raiz, "..", "web");
const MARCA = 'name="argos-dashboard"'; // el index.html nuevo la lleva; el panel anterior no

if (!existsSync(join(dist, "index.html"))) {
  console.error("No existe dist/index.html. Corre primero: npm run build");
  process.exit(1);
}
const viejo = join(web, "index.html");
const respaldo = join(web, "panel_anterior.html");
if (existsSync(viejo) && !readFileSync(viejo, "utf8").includes(MARCA) && !existsSync(respaldo)) {
  renameSync(viejo, respaldo);
  console.log("Panel anterior guardado como servidor/web/panel_anterior.html");
}
// Se quitan solo los recursos de una publicacion anterior del dashboard (carpeta assets), no el respaldo.
rmSync(join(web, "assets"), { recursive: true, force: true });
cpSync(dist, web, { recursive: true });
console.log(`Publicado en servidor/web: ${readdirSync(web).join(", ")}`);
