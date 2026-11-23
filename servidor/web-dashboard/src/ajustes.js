// Pestana «Ajustes»: cuenta de administrador y rangos de alerta. Solo aparece si el central tiene la cuenta
// configurada (GET /admin/sesion -> disponible). La sesion vive en una cookie HttpOnly que pone el servidor:
// aqui no se guarda ninguna contrasena ni token.
const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const PARAMETROS = [
  { id: "temperatura", nombre: "Temperatura", unidad: "°C", paso: 0.5 },
  { id: "humedad", nombre: "Humedad", unidad: "% HR", paso: 1 },
];

let vista = null, admin = false, leerUmbrales = () => [], alGuardar = () => {};

async function pedir(ruta, cuerpo) {
  const r = await fetch(ruta, {
    method: cuerpo === undefined ? "GET" : "POST", cache: "no-store", credentials: "same-origin",
    headers: cuerpo === undefined ? {} : { "Content-Type": "application/json", "X-Argos": "1" },
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo), signal: AbortSignal.timeout(15000),
  });
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) throw Object.assign(new Error(datos.error ?? "El servidor no pudo completar la acción."), { codigo: r.status });
  return datos;
}
const mensaje = (e) => (e.codigo ? e.message : "No hay respuesta del servidor. Revisa la conexión e inténtalo de nuevo.");

function pintar() {
  if (!admin) {
    vista.innerHTML = `
      <h2 class="etiqueta">Argos / ajustes</h2>
      <section class="ventana ajustes" aria-label="Cuenta de administrador">
        <div class="ventana__barra"><h3 class="ventana__nombre">cuenta de administrador</h3><span>sin sesión</span></div>
        <div class="ventana__cuerpo">
          <p class="ajustes__texto">Ver el tablero es libre. Para cambiar los rangos de alerta, entra con la cuenta de administrador.</p>
          <form class="formulario" data-r="entrar" novalidate>
            <label>Usuario<input name="usuario" type="text" autocomplete="username" autocapitalize="none" spellcheck="false" required></label>
            <label>Contraseña<input name="clave" type="password" autocomplete="current-password" required></label>
            <p class="formulario__error" role="alert" data-r="error"></p>
            <button type="submit" class="boton boton--principal">Entrar</button>
          </form>
        </div>
      </section>`;
    vista.querySelector("[data-r=entrar]").addEventListener("submit", entrar);
    return;
  }
  const umbrales = leerUmbrales();
  vista.innerHTML = `
    <h2 class="etiqueta">Argos / ajustes</h2>
    <section class="ventana ajustes" aria-label="Rangos de alerta">
      <div class="ventana__barra"><h3 class="ventana__nombre">rangos de alerta</h3><span>sesión de administrador</span></div>
      <div class="ventana__cuerpo">
        <form class="formulario" data-r="rangos" novalidate>
          ${PARAMETROS.map((p) => {
            const u = umbrales.find((x) => x.parametro === p.id);
            return `<fieldset data-parametro="${p.id}"><legend>${p.nombre} (${p.unidad})</legend>
              <label>Mínimo<input name="${p.id}_min" type="number" inputmode="decimal" step="${p.paso}" value="${esc(u?.minimo ?? "")}" required></label>
              <label>Máximo<input name="${p.id}_max" type="number" inputmode="decimal" step="${p.paso}" value="${esc(u?.maximo ?? "")}" required></label>
            </fieldset>`;
          }).join("")}
          <p class="formulario__error" role="alert" data-r="error"></p>
          <p class="formulario__ok" role="status" data-r="ok"></p>
          <div class="formulario__botones">
            <button type="submit" class="boton boton--principal">Guardar rangos</button>
            <button type="button" class="boton" data-r="salir">Cerrar sesión</button>
          </div>
        </form>
        <p class="ajustes__nota">Estos rangos deciden cuándo el servidor abre una alerta y manda avisos. El nodo de temperatura y humedad trae sus propios rangos grabados para su zumbador y su LED, y no cambian desde aquí: hay que volver a grabar el nodo.</p>
        <p class="ajustes__nota">La alarma solo se silencia con el botón del nodo; desde el tablero no se puede.</p>
      </div>
    </section>`;
  vista.querySelector("[data-r=rangos]").addEventListener("submit", guardar);
  vista.querySelector("[data-r=salir]").addEventListener("click", salir);
}

async function ocupado(form, tarea) {
  const boton = form.querySelector("[type=submit]"), error = form.querySelector("[data-r=error]"), ok = form.querySelector("[data-r=ok]");
  error.textContent = ""; if (ok) ok.textContent = "";
  boton.disabled = true;
  try { await tarea(); } catch (e) { error.textContent = mensaje(e); } finally { boton.disabled = false; }
}

function entrar(ev) {
  ev.preventDefault();
  const f = ev.currentTarget, usuario = f.usuario.value.trim(), clave = f.clave.value;
  if (!usuario || !clave) { f.querySelector("[data-r=error]").textContent = "Escribe el usuario y la contraseña."; return; }
  ocupado(f, async () => {
    await pedir("admin/entrar", { usuario, clave });
    admin = true;
    pintar();
    vista.querySelector("input")?.focus();
  });
}

function guardar(ev) {
  ev.preventDefault();
  const f = ev.currentTarget, actuales = leerUmbrales();
  ocupado(f, async () => {
    const cambios = [];
    for (const p of PARAMETROS) {
      const minimo = f[`${p.id}_min`].valueAsNumber, maximo = f[`${p.id}_max`].valueAsNumber;
      if (!Number.isFinite(minimo) || !Number.isFinite(maximo)) throw Object.assign(new Error(`Escribe el mínimo y el máximo de ${p.nombre.toLowerCase()}.`), { codigo: 400 });
      if (minimo >= maximo) throw Object.assign(new Error(`En ${p.nombre.toLowerCase()}, el mínimo debe ser menor que el máximo.`), { codigo: 400 });
      const u = actuales.find((x) => x.parametro === p.id);
      if (!u || u.minimo !== minimo || u.maximo !== maximo) cambios.push({ parametro: p.id, minimo, maximo });
    }
    if (cambios.length === 0) { f.querySelector("[data-r=ok]").textContent = "No hay cambios que guardar."; return; }
    try {
      for (const c of cambios) await pedir("admin/umbrales", c);
    } catch (e) {
      if (e.codigo === 401) { admin = false; pintar(); vista.querySelector("[data-r=error]").textContent = "La sesión caducó. Entra de nuevo para guardar."; return; }
      throw e;
    }
    f.querySelector("[data-r=ok]").textContent = "Rangos guardados.";
    alGuardar();
  });
}

async function salir() {
  try { await pedir("admin/salir", {}); } catch { /* si el servidor no responde, la sesion caduca sola */ }
  admin = false;
  pintar();
}

/** Devuelve true si la pestana existe (para que main.js vuelva a revisar la pestana pedida en la direccion). */
export async function iniciarAjustes(opciones) {
  leerUmbrales = opciones.umbrales; alGuardar = opciones.alGuardar;
  let s;
  try { s = await pedir("admin/sesion"); } catch { return false; } // central sin cuenta de admin: no hay pestana
  if (!s.disponible) return false;
  admin = Boolean(s.admin);
  document.querySelector(".cab__nav").insertAdjacentHTML("beforeend", `<a href="#ajustes" data-pestana="ajustes">Ajustes</a>`);
  document.querySelector('[data-vista="historial"]').insertAdjacentHTML("afterend", `<div class="vista" data-vista="ajustes" hidden></div>`);
  vista = document.querySelector('[data-vista="ajustes"]');
  pintar();
  return true;
}
