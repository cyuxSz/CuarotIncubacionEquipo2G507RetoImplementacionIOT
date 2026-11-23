// Genera las dos lineas de la cuenta de administrador para el .env del central.
// La contrasena no se guarda en ningun lado: solo se imprime su hash (scrypt con sal aleatoria).
//
//   node crear_admin.mjs
//
// Copia las dos lineas que imprime al final de servidor/central/.env y reinicia el central.
// No las pegues en chats, capturas ni en git.
import { randomBytes, scryptSync } from "node:crypto";
import { createInterface } from "node:readline/promises";

const rl = createInterface({ input: process.stdin, output: process.stdout });
const usuario = (await rl.question("Usuario administrador (por ejemplo, admin): ")).trim();
const clave = await rl.question("Contraseña (mínimo 10 caracteres; se ve al escribirla): ");
const otra = await rl.question("Repite la contraseña: ");
rl.close();

if (!/^[A-Za-z0-9._-]{3,40}$/.test(usuario)) { console.error("El usuario debe tener de 3 a 40 letras, números, punto, guion o guion bajo."); process.exit(1); }
if (clave !== otra) { console.error("Las contraseñas no coinciden."); process.exit(1); }
if (clave.length < 10 || clave.length > 200) { console.error("La contraseña debe tener entre 10 y 200 caracteres."); process.exit(1); }

const sal = randomBytes(16);
const hash = scryptSync(clave, sal, 64);
console.log("\nAgrega estas dos líneas a servidor/central/.env y reinicia el central:\n");
console.log(`ADMIN_USER=${usuario}`);
console.log(`ADMIN_HASH=scrypt:${sal.toString("base64url")}:${hash.toString("base64url")}`);
console.log("\nLimpia la pantalla de la terminal después de copiarlas.");
