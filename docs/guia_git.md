# Guía de git para Argos (lo haces tú, a mano)

Regla: **una rama por pieza**, con commits pequeños. Todo en Git Bash, desde la raíz del repo.

## El ciclo (se repite igual cada vez)

```bash
git switch master                      # 1. partir de la rama principal (el repo usa master)
git switch -c servidor-mosquitto       # 2. crear y entrar a la rama nueva (-c = create)
# ... trabajas / editas archivos ...
git status                             # 3. ver qué cambió (rojo = sin agregar, verde = listo)
git add servidor/mosquitto servidor/crear_usuarios_mqtt.sh   # 4. elegir qué entra al commit
git diff --staged                      # 5. revisar lo que vas a guardar
git commit -m "Mensaje"                # 6. guardar
git switch master && git merge servidor-mosquitto   # 7. unir a master al terminar la pieza
```

- `git add` siempre con rutas concretas, **nunca** `git add .` (arrastraría `node_modules/`, `package.json` y otros archivos que no son de esta pieza).
- Antes de cada `add`, confirma que **no** aparece `.env` ni `servidor/mosquitto/passwd` en `git status`. Ya están en `.gitignore`.
- Los cambios sin guardar viajan contigo al crear una rama nueva, así que puedes crearla después de haber editado.
- No hay remoto configurado. Si creas un repo **privado** en GitHub: `git remote add origin <URL>` y luego `git push -u origin HEAD` (la primera vez) o `git push` (las siguientes).

## Formato del mensaje

Primera línea en español, en imperativo, máximo ~60 caracteres, sin punto: `Agrega ...`, `Arregla ...`, `Documenta ...`.
Si hace falta explicar, deja una línea en blanco y escribe el porqué. Para un cuerpo largo usa `git commit` sin `-m` (se abre el editor).

## Ramas y commits sugeridos (en este orden)

Los archivos ya están escritos; para cada rama haz `switch -c`, `add` de sus rutas y `commit`.

**1. `servidor-mosquitto`**
```bash
git add servidor/mosquitto/mosquitto.conf servidor/mosquitto/acl servidor/crear_usuarios_mqtt.sh servidor/generar_secretos.py .env.example .gitignore .gitattributes .vscode/settings.json
git commit -m "Agrega broker Mosquitto con usuarios y ACL" -m "Un usuario por nodo, mas n8n y dashboard. Cada nodo solo publica en sus topics. Contrasenas solo en el archivo de secretos."
```

**2. `servidor-mysql`**
```bash
git add servidor/mysql/02_usuarios.sh
git commit -m "Agrega usuarios de MySQL de escritura y lectura"
```

**3. `servidor-web`**
```bash
git add servidor/web
git commit -m "Agrega pagina inicial del servidor web"
```
(El compose y nginx van en la rama 5 porque ya incluyen la API.)

**4. `simulador-rc`**
```bash
git add simulador/simulador_nodos.py
git commit -m "Arregla el simulador: avisa si el broker rechaza la conexion"
```

**5. `api-rest`**
```bash
git add servidor/api servidor/docker-compose.yml servidor/nginx/default.conf
git status   # confirma que NO aparecen servidor/api/node_modules ni servidor/api/config_local
git commit -m "Agrega API REST en Node.js con motor de alertas" -m "Los NodeMCU guardan por HTTP POST; la API es la unica que escribe en MySQL. Alertas con las mismas reglas del firmware (3 lecturas, histeresis); cmd/alarma por MQTT al instante y cada 60 s."
```
(`acl`, `crear_usuarios_mqtt.sh`, `.env.example` y `.gitignore` ya entraron completos en la rama 1.)

**5c. `firmware-http`**
```bash
git add firmware/include/api_http.h firmware/include/nodo_comun.h firmware/include/secrets.example.h firmware/src/dht/main.cpp firmware/src/puerta/main.cpp firmware/herramientas/exportar_arduino.py firmware/arduino_ide
git status   # confirma que NO aparece ningun secrets.h (solo secrets.example.h)
git commit -m "Agrega envio por HTTP a la API en los 5 nodos" -m "Cada lectura y evento sale por HTTP POST (se guarda en MySQL) y por MQTT (tiempo real). El dht consulta GET /api/comandos como respaldo de cmd/alarma. El LED rojo y el silencio se registran como acciones."
```

**5d. `etapa3-bd`**
```bash
git add docs/bd/etapa3 docs/bd/esquema.sql
git commit -m "Agrega script de entrega, datos de prueba e indicadores de la Etapa 3" -m "Script unico generado desde esquema.sql; 3 indicadores SQL por nodo. Probado en MySQL 8.4 limpio."
```

**6. `docs-servidor`**
```bash
git add CLAUDE.md docs/api.md docs/tutorial_servidor.md docs/guia_git.md
git commit -m "Documenta el montaje del servidor y el flujo de git"
```

Nota: `.gitignore` y `.env.example` cambiaron para varias piezas; entran con la rama 1 y no hace falta repetirlos.
`docs/argos_prompts_identidad.md`, `docs/brief_identidad_visual.md`, `package.json`, `package-lock.json` y `node_modules/` no son de esta pieza: déjalos fuera.

## Comandos útiles

```bash
git log --oneline -10      # historial corto
git diff                   # cambios sin agregar
git restore --staged RUTA  # sacar un archivo del add (no borra cambios)
git branch                 # ramas locales
```

## Poner el stack en marcha con tus secretos reales

```bash
python servidor/generar_secretos.py        # crea tu archivo de secretos (no imprime valores)
bash servidor/crear_usuarios_mqtt.sh       # regenera servidor/mosquitto/passwd
docker compose --env-file .env -f servidor/docker-compose.yml down -v   # borra el stack de PRUEBA (datos incluidos)
docker compose --env-file .env -f servidor/docker-compose.yml up -d
```

El `down -v` va antes del primer arranque real: MySQL solo ejecuta los scripts de init con el volumen vacío, y el volumen actual tiene contraseñas de prueba.
