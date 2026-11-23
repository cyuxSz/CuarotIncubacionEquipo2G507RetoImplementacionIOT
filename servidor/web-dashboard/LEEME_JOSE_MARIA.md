# Dashboard de Argos: qué trae este zip y qué hay que hacer

De: Iván Acosta · 22-nov-2026 · Para: José María García (y su agente de Claude)

Este zip es la carpeta `servidor/web-dashboard/` completa: el dashboard nuevo, ya compilado. Reemplaza al panel de `servidor/web/index.html`. **No trae secretos** ni `node_modules`.

**Probado:** en una laptop, con datos de prueba (casos normal, alerta, nodos caídos, sin datos y servidor caído), a 1440, 1920 y 375 px. El módulo de administrador pasó 22 comprobaciones contra una base falsa.
**No probado:** contra el central real, MySQL real, el simulador ni los nodos. Eso se hace en el servidor con los pasos de abajo.

## 1. Publicar el dashboard (obligatorio, sin reiniciar nada)

El central sirve como estáticos lo que haya en `servidor/web`. Solo hay que copiar archivos; **el central no se reinicia y no se instala nada**.

1. Descomprime el zip en `servidor/web-dashboard/` del servidor (junto a `central/` y `web/`).
2. Guarda el panel actual: renombra `servidor/web/index.html` a `servidor/web/panel_anterior.html`.
3. Copia **el contenido** de `servidor/web-dashboard/dist/` dentro de `servidor/web/` (quedan `index.html`, `favicon.svg` y la carpeta `assets/`).
4. Abre `http://localhost:3000` en el servidor y recarga con Ctrl+F5.

Atajo equivalente a los pasos 2 y 3, si prefieres un comando (usa solo Node, no instala nada):

```powershell
node servidor\web-dashboard\herramientas\publicar.mjs
```

**Para regresar al panel anterior:** borra `servidor/web/index.html`, `favicon.svg` y `assets/`, y renombra `panel_anterior.html` a `index.html`.

### Cómo comprobar que quedó bien

- Arriba a la derecha dice «Actualizado HH:MM:SS» y cambia cada 5 s.
- Hay dos pestañas: **Ahora** (aviso de alertas, 5 ventanas de nodos, eventos recientes y resumen de la noche) e **Historial** (gráficas de 24 h / 7 días y alertas por episodio).
- La pestaña **Ajustes** NO aparece: es lo esperado mientras no se haga la sección 3.
- El nodo dht muestra su temperatura y humedad reales; los nodos que nunca han reportado salen como «SIN DATOS» con borde punteado.
- Si algo se ve raro, mándale a Iván una captura y lo que diga la consola del navegador (F12).

## 2. Verlo desde fuera del servidor (decisión del equipo)

Hoy el central (puerto 3000) no tiene túnel y el firewall solo abre 3001–3005. Para verlo en celulares y en la Expo, Iván propone un sexto túnel rápido, igual que los de los nodos:

```powershell
cloudflared tunnel --url http://localhost:3000 --protocol http2 --loglevel info
```

La URL `https://xxxx.trycloudflare.com` que imprime es la del dashboard. Cambia cada vez que el túnel se reinicia. **Cualquiera con la URL puede ver el tablero** (ver es libre por decisión del equipo; no expone la API key ni permite escribir nada). Anótala en `servidor/ESTADO_SERVIDOR.md`.

## 3. Cuenta de administrador y rangos ajustables (opcional; requiere reiniciar el central)

Permite cambiar desde el dashboard los rangos de temperatura y humedad de la tabla `Umbral`. Sin este paso el dashboard funciona igual, solo que sin la pestaña **Ajustes**.

**Qué cambia en el central:** un archivo nuevo y una línea en `central.js`. No toca `motor.js`, las alertas, MQTT, `servidor/api-rest` ni el esquema de la base. El usuario de MySQL del central ya tiene permiso `UPDATE`.

1. Copia `servidor/web-dashboard/para_el_central/admin.js` a `servidor/central/admin.js`.
2. En `servidor/central/central.js`, justo **antes** de la línea `app.use("/api", (req, res, next) => {` (debajo del comentario «avisos para n8n»), agrega:

   ```js
   require("./admin").montar(app, pool, { alCambiar: () => cache.clear() });
   ```

3. Genera la cuenta. En una terminal del servidor:

   ```powershell
   node servidor\web-dashboard\para_el_central\crear_admin.mjs
   ```

   Pide usuario y contraseña (mínimo 10 caracteres) e imprime dos líneas, `ADMIN_USER=...` y `ADMIN_HASH=...`. Pégalas al final de `servidor/central/.env`. Solo se guarda el hash, no la contraseña. **No las pegues en chats ni en git**, y pásale la contraseña a Iván por privado.
4. Reinicia el central (Ctrl+C y `npm start` en su terminal). Son unos segundos y no se pierden datos: los nodos escriben en sus APIs y el motor retoma desde `central_ultimo_evento`. Hazlo cuando no haya una alerta abierta.
5. Comprueba: `http://localhost:3000/admin/sesion` debe contestar `{"disponible":true,"admin":false}`, y en el dashboard aparece la pestaña **Ajustes**.

### Lo que hay que saber antes de usarlo

- **El nodo dht no se entera.** Sus rangos para el zumbador y el LED están grabados en `firmware/include/alarma_dht.h` (22–28 °C, 40–60 %). Cambiar la tabla cambia cuándo el servidor abre alertas y manda avisos, pero no la alarma local del nodo. Para que coincidan hay que cambiar el firmware y reflashear, igual que con `MODO_DEMO`.
- **No hay silencio remoto.** El zumbador solo se silencia con el botón del nodo; no existe una orden por MQTT para eso, así que el dashboard no ofrece ese botón. Haría falta firmware nuevo. `[POR CONFIRMAR si el equipo lo quiere]`
- La sesión dura 8 horas y vive en memoria: al reiniciar el central hay que volver a entrar.
- Tras 5 intentos fallidos desde un mismo origen, el acceso se bloquea 10 minutos.
- Límites que acepta: temperatura entre 0 y 50 °C con al menos 2 de separación; humedad entre 0 y 100 % con al menos 5.
- Por el túnel la cookie viaja con `Secure`; en `http://localhost:3000` también funciona.

## 4. Mostrar el silencio del zumbador (opcional)

Está descrito aparte en `PARA_JOSE_MARIA_cambio_central.md`: unas 10 líneas de solo lectura en `central.js` para que el aviso diga «Alarma silenciada hasta las HH:MM». Si haces la sección 3, conviene aplicar los dos cambios en el mismo reinicio.

## Avisos por mensaje (n8n)

No es parte del dashboard, pero va en este zip: `ALTERNATIVAS_AVISOS.md` compara los canales posibles ahora que CallMeBot está lleno y la API de Meta pide cuenta verificada. La propuesta es Telegram, que ya está en `servidor/n8n/avisos_graves.json`.

## 5. Cómo continuar el desarrollo (en una laptop, no en el servidor)

```powershell
npm install
```

```powershell
npm run dev
```

- `npm run dev` abre `http://localhost:5173` con **datos de prueba**, sin central ni MySQL. Casos: `?escenario=normal`, `alerta`, `silencio`, `caidos`, `sin_datos`, `error`.
- En ese modo la cuenta de administrador es de mentira (usuario y contraseña en `herramientas/datos_prueba.mjs`); no sirve en el servidor real.
- Para trabajar contra un central de verdad: arranca Vite con la variable `ARGOS_CENTRAL=http://localhost:3000`.
- `npm run build` genera `dist/`; `npm run publicar` lo copia a `servidor/web`.

| Archivo | Qué hace |
|---|---|
| `index.html` | Esqueleto: cabecera, pestañas y las 5 ventanas de nodos |
| `src/main.js` | Sondeo a `/panel/datos` cada 5 s, tema claro/oscuro, pestañas |
| `src/principal.js` | Pestaña Ahora: avisos, estado de la alarma y ventanas de nodos |
| `src/historial.js` | Gráficas (Chart.js) y lista de eventos |
| `src/alertas.js` | Resumen de la noche (22:00 a 7:00) y alertas por episodio |
| `src/ajustes.js` | Pestaña Ajustes: entrar, rangos, cerrar sesión |
| `src/estilos/` | `tokens.css` (colores del póster, claro y oscuro), `base.css`, `app.css` |
| `herramientas/` | Datos de prueba para desarrollo y el script de publicar |
| `para_el_central/` | `admin.js` y `crear_admin.mjs` para la sección 3 |
| `capturas/` | Antes (`antes/`) y después (`despues/`), para el reporte |
| `PRODUCT.md` | Para quién es el dashboard y qué reglas sigue |

Reglas que respeta el código: orden fijo de nodos (dht, luz, pir, puerta, acel); horas en `America/Monterrey` (la base está en UTC); nada de CDN (fuentes y Chart.js van dentro de `dist/assets`); verde y rojo solo como estado, siempre con forma o texto.

## 6. Pendientes

1. Probar con el central real y con `servidor/simulador_nodos.mjs` (en una base de pruebas, nunca la del invernadero).
2. Decidir el túnel del puerto 3000 (sección 2).
3. Decidir si se activa la cuenta de administrador (sección 3) y si se alinean los rangos del firmware.
4. `MODO_DEMO` para la Expo: el dashboard muestra los rangos que haya en la tabla `Umbral`, así que no hay que tocarlo.
5. MQTT en vivo desde el navegador: no se hizo; el sondeo cada 5 s basta.
6. Capturas en tema claro y revisar la animación (el destello de la barra al cambiar un dato) en una pantalla real.
7. Límite conocido: el central entrega solo las últimas 40 alertas y los últimos 40 eventos; con mucha actividad, el resumen de la noche avisa que sus conteos son un mínimo.
