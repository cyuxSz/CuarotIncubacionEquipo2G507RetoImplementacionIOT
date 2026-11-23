"""Etapa 3 (individual, Luis Mendoza, nodo dht): arma la carpeta de entrega y los documentos.

Uso (desde la raiz del repo, con la base `argos` y sus datos de prueba cargados en el MySQL local):
  DB_PORT=3307 DB_USER=usertec MYSQL_PWD=... uv run --no-project --python 3.12 --with python-docx \
      python docs/entregables/etapa3/generar.py

Salida en entregas/etapa3_A01669847/:
  ScriptCreacionBaseDatos_iot_Equipo2.sql, indicadores_iot_Equipo2-A01669847.sql,
  RestApi-Equipo2-A01669847/ (API sin node_modules ni claves), Arduino-Equipo2-A01669847/ (.ino + .h),
  Indicadores_Equipo2-A01669847.docx y Etapa3_Documentacion_Equipo2-A01669847.docx (borrador con pendientes).
Los resultados de los indicadores se consultan en vivo: cambian con los datos que tenga la base.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

AQUI = Path(__file__).resolve().parent
R = AQUI.parents[2]
sys.path.insert(0, str(AQUI.parent))
import docx_lib  # noqa: E402

EQUIPO, MATRICULA, NODO = "2", "A01669847", "dht"
SUF = f"Equipo{EQUIPO}-{MATRICULA}"
SAL = Path(os.environ["SAL_DIR"]) if os.environ.get("SAL_DIR") else R / "entregas" / f"etapa3_{MATRICULA}"
MYSQL = os.environ.get("MYSQL_EXE", r"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe")
docx_lib.INTEGRANTES = [f"Luis Eduardo Mendoza Menéndez {MATRICULA}"]
FECHA = "Noviembre de 2026"
CURSO = f"Equipo {EQUIPO} · G507 · TC1004B"
LOGO = str(AQUI.parent / "fig" / "image1.png")
PEND = "**[PENDIENTE]**"


# ───────────────────────────── 1. carpeta de entrega ─────────────────────────────
def armar_carpeta():
    if SAL.exists():
        shutil.rmtree(SAL)
    SAL.mkdir(parents=True)
    bd = R / "docs/bd/etapa3"
    shutil.copy(bd / f"ScriptCreacionBaseDatos_iot_Equipo{EQUIPO}.sql", SAL)
    shutil.copy(bd / f"datos_prueba_Equipo{EQUIPO}.sql", SAL)
    shutil.copy(bd / f"indicadores_{NODO}.sql", SAL / f"indicadores_iot_{SUF}.sql")
    shutil.copytree(R / "servidor/api-rest", SAL / f"RestApi-{SUF}",
                    ignore=shutil.ignore_patterns("node_modules", ".env"))
    ino = SAL / f"Arduino-{SUF}"
    ino.mkdir()
    origen = R / f"firmware/arduino_ide/argos_{NODO}"
    shutil.copy(origen / f"argos_{NODO}.ino", ino / f"Arduino-{SUF}.ino")
    for h in ("alarma_dht.h", "api_http.h", "nodo_comun.h", "vista_oled.h", "secrets.example.h"):
        shutil.copy(origen / h, ino)


# ───────────────────────────── 2. indicadores en vivo ────────────────────────────
def consultas():
    """Las consultas del .sql de indicadores, en orden (sin comentarios ni el USE)."""
    texto = (R / f"docs/bd/etapa3/indicadores_{NODO}.sql").read_text(encoding="utf-8")
    salida = []
    for trozo in texto.split(";\n"):
        sql = "\n".join(l for l in trozo.splitlines() if l.strip() and not l.strip().startswith("--"))
        if sql.upper().startswith("SELECT"):
            salida.append(sql)
    return salida


def ejecutar(sql):
    """Corre una consulta con el cliente mysql y regresa [encabezados, fila, ...]."""
    r = subprocess.run(
        [MYSQL, "-h", "127.0.0.1", "-P", os.environ.get("DB_PORT", "3306"), "-u", os.environ.get("DB_USER", "root"),
         "-B", "--default-character-set=utf8mb4", os.environ.get("DB_NAME", "argos"), "-e", sql],
        capture_output=True, text=True, encoding="utf-8", check=True)
    return [l.split("\t") for l in r.stdout.strip().splitlines()]


IMG_COD = AQUI / "capturas" / "codigo"


def codigo(D, texto, tam=8.5, lang="javascript"):
    """Bloque de codigo como imagen con resaltado de sintaxis (tema oscuro, como el editor)."""
    from pygments import highlight
    from pygments.formatters import ImageFormatter
    from pygments.lexers import get_lexer_by_name
    import hashlib
    IMG_COD.mkdir(parents=True, exist_ok=True)
    texto = texto.strip("\n")
    ruta = IMG_COD / (hashlib.md5((lang + texto).encode()).hexdigest()[:10] + ".png")
    if not ruta.exists():
        png = highlight(texto, get_lexer_by_name(lang), ImageFormatter(
            style="monokai", font_name="Consolas", font_size=22, line_numbers=False, image_pad=18))
        ruta.write_bytes(png)
    from PIL import Image
    ancho_px = Image.open(ruta).width
    imagen(D, ruta, min(6.3, ancho_px / 150))


def imagen(D, ruta, ancho):
    """Imagen sin numero de figura (capturas de codigo)."""
    par = D.d.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.space_after = Pt(6)
    par.add_run().add_picture(str(ruta), width=Inches(ancho))


SQL = consultas()
RES = [ejecutar(q) for q in SQL]
assert len(SQL) == 3, "se esperaban 3 indicadores"

# Datos para redactar las explicaciones con los numeros reales
r1, r2, r3 = RES
dias = sorted({f[0] for f in r1[1:]})
t_max = max((float(f[5]), f[0]) for f in r1[1:] if f[1] == "temperatura")
h_max = max((float(f[5]), f[0]) for f in r1[1:] if f[1] == "humedad")
peor = max(r2[1:], key=lambda f: float(f[5]))
n_alertas = len(r3) - 1

INDICADORES = [
    dict(
        nombre="Resumen diario de temperatura y humedad",
        desc="Promedio, mínimo y máximo de cada parámetro por día, con el número de lecturas.",
        util="Muestra si el cuarto se mantuvo entre 22 y 28 °C y entre 40 y 60 % cada día. Si un día tiene pocas "
             "lecturas, el nodo estuvo apagado o sin red. En el dashboard será la gráfica diaria.",
        titulo="Resultado del indicador 1: resumen diario del nodo dht",
        expl=f"Los promedios quedan dentro de rango, pero los máximos muestran dos episodios: {t_max[0]:.1f} °C el "
             f"{t_max[1]} y {h_max[0]:.1f} % de humedad el {h_max[1]}. El primer día tiene pocas lecturas porque "
             f"los datos de prueba no empiezan a medianoche.",
    ),
    dict(
        nombre="Porcentaje de lecturas fuera de rango por día",
        desc="Qué porcentaje de las lecturas de cada día quedó fuera del rango permitido.",
        util="Si el porcentaje sube de un día a otro, hay un problema con el clima o la puerta antes de que dañe "
             "los cultivos. El rango se toma de la tabla Umbral, así que si cambia, el indicador lo sigue.",
        titulo="Resultado del indicador 2: lecturas fuera de rango del nodo dht",
        expl=f"El peor día fue el {peor[0]} en {peor[1]}: {peor[3]} de {peor[4]} lecturas fuera de rango "
             f"({peor[5]} %). Coincide con los máximos del indicador 1.",
    ),
    dict(
        nombre="Alertas de temperatura y humedad",
        desc="Cada alerta con el valor que la abrió, cuánto duró, si encendió el buzzer y si alguien lo silenció.",
        util="Una alerta larga indica que nadie la atendió. Si nadie silenció el buzzer, no había nadie en el "
             "cuarto, y eso ayuda a decidir si hacen falta avisos por mensaje.",
        titulo="Resultado del indicador 3: alertas del nodo dht",
        expl=" ".join(f"La alerta de {f[1]} se abrió con {float(f[2]):.1f} y duró {f[4]} minutos"
                      + (", y alguien silenció el buzzer." if f[6] != "0" else "; nadie silenció el buzzer.")
                      for f in r3[1:])
             + " Cada episodio genera una sola alerta aunque haya muchas lecturas fuera de rango.",
    ),
]


def seccion_indicadores(D, nivel_h):
    D.p("Para las consultas investigamos cuatro funciones de MySQL (Oracle, s. f.-a, s. f.-b). INTERVAL resta "
        "6 horas para pasar de UTC a la hora de Monterrey. TIMESTAMPDIFF calcula los minutos que duró una alerta. "
        "UTC_TIMESTAMP da la hora actual en UTC. COALESCE regresa el primer valor que no sea nulo; lo usamos "
        "para medir hasta ahora una alerta que sigue abierta.")
    for i, (ind, res) in enumerate(zip(INDICADORES, RES), 1):
        nivel_h(f"Indicador {i}. {ind['nombre']}")
        D.p(f"**Descripción.** {ind['desc']}")
        D.p(f"**Utilidad.** {ind['util']}")
        imagen(D, AQUI / "capturas" / f"sql_indicador{i}.png", 6.3)
        D.figura(str(AQUI / "capturas" / f"res_indicador{i}.png"), ind["titulo"], ancho=6.3,
                 nota="Ejecutado en DBeaver con tres días de datos de prueba; horas de Monterrey.")
        D.p(f"**Resultado.** {ind['expl']}")


# ───────────────────────────── 3. PDF de indicadores ─────────────────────────────
def doc_indicadores():
    D = docx_lib.Doc()
    D.portada("Etapa 3: Indicadores de la base de datos",
              subtitulo="Argos: Monitoreo ambiental del cuarto de incubación in vitro. Nodo dht (temperatura y humedad)",
              logo=LOGO, fecha=FECHA, curso=CURSO)
    D.h1("Indicadores del nodo dht")
    D.p("Tres consultas del script `indicadores_iot_" + SUF + ".sql` sobre los datos del nodo dht. Servirán "
        "de base para el dashboard. La base guarda las fechas en UTC y las consultas las muestran en hora de "
        "Monterrey.")
    seccion_indicadores(D, D.h2)
    D.referencias([
        "Oracle. (s. f.-a). *Date and time functions*. MySQL 8.4 Reference Manual. https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html",
        "Oracle. (s. f.-b). *Comparison functions and operators*. MySQL 8.4 Reference Manual. https://dev.mysql.com/doc/refman/8.4/en/comparison-operators.html",
    ])
    D.guardar(str(SAL / f"Indicadores_{SUF}.docx"))


# ───────────────────────────── 4. documento tecnico ──────────────────────────────
def doc_tecnico():
    D = docx_lib.Doc()
    D.portada("Etapa 3: Integración del dispositivo IoT con una API REST y MySQL",
              subtitulo="Argos: Monitoreo ambiental del cuarto de incubación in vitro. Circuito individual: nodo dht",
              logo=LOGO, fecha=FECHA, curso=CURSO)
    CAP = AQUI / "capturas"
    FZ = AQUI / "fritzing"
    API = f"RestApi-{SUF}"

    D.h1("1. Introducción")
    D.p("Argos vigila el cuarto de incubación in vitro del Invernadero Académico y avisa a los encargados cuando "
        "las condiciones salen de lo esperado. Tiene cinco nodos con un NodeMCU ESP8266 cada uno: temperatura y "
        "humedad (dht), luz, movimiento (pir), puerta y golpes en el anaquel (acel).")
    D.p("Mi circuito es el nodo dht. Mide la temperatura y la humedad del cuarto y enciende un LED rojo cuando "
        "salen del rango de 22 a 28 °C y 40 a 60 % de humedad. Envía cada lectura por WiFi a una API REST en "
        "Node.js, y la API la guarda en MySQL en mi computadora. El NodeMCU nunca se conecta directo a la base. "
        "El diseño final lleva un DHT22, un buzzer y una pantalla; para esta entrega lo armé con el material del "
        "kit del curso: un DHT11 y dos LED.")

    D.h1("2. Metodología")
    D.p("Primero el equipo hizo un solo script de la base de datos a partir del modelo de la Etapa 2, con la "
        "corrección de la profesora sobre Sensor y Umbral. Después adapté la API de la clase a esa base; el código "
        "es el mismo para los cinco integrantes y cada quien elige su nodo en la configuración. Luego programé el "
        "NodeMCU, probé la API con peticiones desde la computadora y al final probé el circuito armado. Usé Arduino "
        "IDE, Node.js con Express y mysql2, MySQL, DBeaver, Fritzing y GitHub Projects.")

    D.h1("3. Descripción del circuito")
    D.p("La temperatura y la humedad son las dos variables que más afectan a los cultivos, así que este nodo es el "
        "que los protege directamente. Los otros cuatro nodos ayudan a explicar por qué cambió el ambiente.")
    D.tabla("Componentes del circuito de prueba", [
        ["Componente", "Pin", "Función"],
        ["Módulo DHT11", "D2, a 3.3 V", "Mide temperatura y humedad cada 30 s"],
        ["LED rojo (actuador)", "D8, con 220 Ω", "Encendido: alerta activa. Parpadeo rápido: falla del sensor"],
        ["LED verde", "D7, con 220 Ω", "Encendido: conectado. Parpadeo lento: sin WiFi"],
    ], anchos=[1.6, 1.4, 3.5], tam=9.5,
        nota="En el diseño final el DHT11 se cambia por un DHT22 y se agregan un buzzer en D5, un botón de "
             "silencio en D6 y una pantalla OLED.")

    D.h1("4. Diagrama de conexiones")
    D.figura(str(FZ / "esquematico_dht11.png"), "Esquemático del nodo dht", ancho=5.2,
             nota="Elaboración propia. Los LED se conectan con una resistencia de 220 Ω cada uno; todas las tierras van al GND del NodeMCU.")
    D.figura(str(FZ / "prueba_dht11_breadboard.png"), "Armado en protoboard", ancho=4.4,
             nota="Elaborado en Fritzing. El sensor aparece con la pieza del DHT22 porque Fritzing no trae el "
                  "módulo DHT11; las conexiones son las mismas.")
    D.figura(str(CAP / "foto_circuito.jpg"), "Circuito armado durante la prueba", ancho=4.6)

    D.h1("5. Diagrama global del sistema")
    D.figura(str(AQUI / "arquitectura_individual.png"), "Arquitectura del circuito: hardware, red y software",
             ancho=4.2)
    D.p("En el hardware, el NodeMCU lee el sensor y maneja los LED; se alimenta por USB. Para la red usa el WiFi "
        "de 2.4 GHz que trae integrado el ESP8266 y se conecta a la red del campus, que le da una dirección IP. "
        "En el software, mi computadora es el servidor: corre la API en Node.js en el puerto 3001 y MySQL con la "
        "base argos, y DBeaver sirve para ver las tablas.")

    D.h1("6. Modelo de base de datos")
    D.figura(str(AQUI.parent / "fig" / "uml.png"), "Modelo de la base de datos del equipo", ancho=4.4)
    D.tabla("Tablas que usa el nodo dht", [
        ["Tabla", "Uso"],
        ["Nodo, Sensor, Parametro", "Identifican de qué nodo, sensor y magnitud viene cada dato"],
        ["Medicion", "Una fila por lectura de temperatura y otra de humedad, con fecha y hora"],
        ["Umbral", "Rango, histéresis y persistencia de cada parámetro"],
        ["Alerta", "Cada episodio fuera de rango; la API la abre y la cierra"],
        ["Actuador, AccionControl", "Cada vez que el LED rojo o el buzzer cambian de estado"],
        ["EstadoNodo, Evento", "Último reporte del nodo y fallas del sensor"],
    ], anchos=[1.9, 4.6], tam=9.5)
    D.p("La profesora preguntó por qué un sensor tiene varios umbrales. Es porque un sensor puede medir más de un "
        "parámetro y cada uno tiene su rango: el sensor del nodo dht mide temperatura y humedad, así que tiene dos "
        "filas en Umbral. No puede haber dos umbrales del mismo parámetro para el mismo sensor. Cada fila guarda "
        "además la persistencia (la alerta se abre a la tercera lectura seguida fuera de rango) y la histéresis "
        "(se cierra hasta bajar de 27.5 °C, no de 28 °C, para que no se abra y cierre sin parar).")

    D.h1("7. Implementación en MySQL")
    D.p("El script `ScriptCreacionBaseDatos_iot_Equipo2.sql` crea la base argos con 14 tablas, sus llaves y "
        "restricciones, y los datos fijos (nodos, sensores, parámetros, umbrales y actuadores). Se puede ejecutar "
        "varias veces porque borra la base antes de crearla. Las tablas de abajo tienen los datos que envió el "
        "NodeMCU en la prueba del 13 de noviembre de 2026; las horas están en UTC.")
    D.figura(str(CAP / "diagrama_er.png"), "Diagrama de la base argos en DBeaver", ancho=6.0)
    D.figura(str(CAP / "tabla_medicion.png"), "Tabla Medicion con las lecturas del NodeMCU", ancho=5.6)
    D.figura(str(CAP / "tabla_umbral.png"), "Tabla Umbral: un umbral por parámetro", ancho=5.6)
    D.figura(str(CAP / "tabla_alerta.png"), "Tabla Alerta: las dos alertas que abrió la API", ancho=5.6,
             nota="21 °C está debajo del mínimo y 80 % arriba del máximo. Siguen abiertas, por eso ts_fin está vacío.")
    D.figura(str(CAP / "tabla_accioncontrol.png"), "Tabla AccionControl: eventos de actuación", ancho=5.6,
             nota="origen local: el nodo encendió su LED rojo. origen alerta: la API registró la orden del buzzer.")

    D.h1("8. API REST")
    D.p(f"La API está en `{API}-index.js` (rutas), `{API}-db.js` (conexión a MySQL), `models/{API}-SensorModel.js` "
        "(consultas SQL), `models/umbralModel.js` (reglas de alerta), `config.js` y `middleware/auth.js` (clave). "
        "Las instrucciones para configurarla están en `LEEME.md`.")
    D.tabla("Endpoints de la API", [
        ["Método", "Ruta", "Qué hace"],
        ["POST", "/api/mediciones", "Guarda temperatura y humedad y responde si debe sonar la alarma"],
        ["POST", "/api/acciones", "Guarda un cambio del LED rojo o del buzzer"],
        ["POST", "/api/eventos, /api/latido", "Guarda una falla del sensor o marca al nodo como vivo"],
        ["GET", "/api/comandos", "Le dice al nodo si hay alarma y cuáles son los umbrales"],
        ["GET", "/api/mediciones, /api/alertas, /api/acciones, /api/estado", "Consultas del historial"],
    ], anchos=[0.8, 2.4, 3.3], tam=9.5,
        nota="Todas piden la cabecera x-api-key. Responden 201 si guardaron, 400 si el dato es inválido, 401 si "
             "la clave no coincide y 500 si falla la base.")
    D.p("La conexión usa un grupo de conexiones que se reutilizan y fija la zona horaria en UTC:")
    codigo(D, """
const pool = mysql.createPool({
  ...BD,               // host, puerto, usuario, clave y base
  timezone: "Z",       // fechas en UTC
  connectionLimit: 5,
});""")
    D.p("La ruta POST de mediciones valida todo antes de escribir y después revisa los umbrales:")
    codigo(D, """
for (const l of lecturas) {
  const rango = config.parametros[l?.parametro];
  if (!rango) throw new ErrorHttp(400, `parametro desconocido: ${l?.parametro}`);
  if (!esNumero(l.valor) || l.valor < rango[0] || l.valor > rango[1])
    throw new ErrorHttp(400, `valor fuera de rango: ${l.valor}`);
  filas.push([l.parametro, l.valor]);
}
await modelo.guardarMediciones(filas);   // INSERT en Medicion
await umbrales.revisar(filas);           // puede abrir o cerrar una alerta
res.status(201).json({ guardadas: filas.length, alarma: await modelo.leerAlarma() });""")
    D.p("Cada medición queda ligada a su sensor y parámetro, con la hora del servidor:")
    codigo(D, """
INSERT INTO Medicion (id_sensor, id_parametro, valor, fecha_hora)
SELECT s.id_sensor, p.id_parametro, ?, UTC_TIMESTAMP()
FROM Sensor s JOIN Parametro p ON p.nombre = ? WHERE s.id_nodo = ?""", lang="sql")

    D.h1("9. Código de Arduino")
    D.p(f"El programa es `Arduino-{SUF}.ino`, con `api_http.h` (peticiones), `nodo_comun.h` (WiFi y LED) y "
        "`alarma_dht.h` (reglas). Se conecta al WiFi en modo estación con reconexión automática. Cada 30 segundos "
        "lee el sensor y descarta la lectura si no es un número o si es imposible; tres lecturas malas seguidas se "
        "reportan como falla. Para la prueba solo cambié el tipo de sensor a DHT11.")
    codigo(D, """
switch (reglas.muestra(dht.readTemperature(), dht.readHumidity())) {
  case alarma::Lectura::valida:      publicarTelemetria(); break;   // POST /api/mediciones
  case alarma::Lectura::falla_nueva: nodo::publicarEvento("sensor_error"); break;
  case alarma::Lectura::invalida:    Serial.println("[dht] lectura invalida: no se envia"); break;
}
consultarComandos();   // GET /api/comandos/dht""", lang="cpp")
    D.p("El POST manda los datos en JSON con la clave en la cabecera. Si no hay respuesta o hay error del servidor, "
        "reintenta una vez; un 400 o un 401 no se reintentan. Todo se imprime en el monitor serial. Con el GET el "
        "nodo sabe si debe encender la alarma, y cada vez que el LED rojo cambia lo registra con un POST a "
        "`/api/acciones`.")
    codigo(D, """
int c = pedir("POST", ruta, json);
if (c < 0 || c >= 500) { delay(200); c = pedir("POST", ruta, json); }   // un reintento
if (c == 400) Serial.println("[api] la API rechazo el dato (400)");
if (c == 401) Serial.println("[api] clave incorrecta (401)");
return c >= 200 && c < 300;""", lang="cpp")

    D.h1("10. Funcionamiento e integración")
    D.p("Cada 30 segundos el NodeMCU lee el sensor, arma un JSON con las dos lecturas y lo envía por WiFi a "
        "`/api/mediciones`. La API revisa la clave y los datos, guarda dos filas en Medicion con la hora en UTC y "
        "actualiza EstadoNodo. Luego compara con Umbral: a la tercera lectura fuera de rango abre una Alerta. "
        "Responde 201 con la orden de alarma, y el nodo enciende el LED rojo y lo registra en AccionControl. Los "
        "datos se consultan con SQL en DBeaver o con las rutas GET.")
    D.p("Elegí 30 segundos porque la temperatura de un cuarto cambia despacio: así una alerta se abre en 90 "
        "segundos y la base no se llena de datos repetidos (son 5,760 filas al día). Los eventos de actuación no "
        "tienen intervalo; se guardan cuando el LED o el buzzer cambian de estado.")

    D.h1("11. Indicadores")
    D.p(f"Las tres consultas están en el script `indicadores_iot_{SUF}.sql`. Como el circuito lleva pocas horas "
        "registrando, se probaron con tres días de datos de prueba (mediciones, eventos y alertas) generados con "
        "ayuda de inteligencia artificial y cargados con el script `datos_prueba_Equipo2.sql`.")
    seccion_indicadores(D, D.h2)

    D.h1("12. Pruebas y resultados")
    D.tabla("Pruebas de la API (sin el NodeMCU)", [
        ["Prueba", "Resultado esperado", "Resultado obtenido"],
        ["Script de creación ejecutado dos veces", "14 tablas, sin errores", "Correcto"],
        ["Petición sin clave", "401", "401"],
        ["Medición válida (25.4 °C, 51.2 %)", "201 y dos filas", "201, guardadas: 2"],
        ["Humedad de 150 % o dato de otro nodo", "400, no guarda", "400"],
        ["Tres lecturas de 28.6 a 28.9 °C", "Se abre la alerta en la tercera", "Correcto"],
        ["Tres lecturas de 27.4 a 27.2 °C", "Se cierra la alerta en la tercera", "Correcto"],
    ], anchos=[2.4, 2.0, 2.1], tam=9.5)
    D.p("Después probé el circuito completo. El NodeMCU se conectó al WiFi del campus y mandó sus lecturas a la "
        "API cada 30 segundos, todas con respuesta 201. El sensor marcó 21 °C y 80 % de humedad, fuera de rango, "
        "así que a la tercera lectura la API abrió dos alertas y el LED rojo se encendió.")
    D.figura(str(CAP / "monitor_serial.png"), "Monitor serial durante la prueba", ancho=6.3)
    D.figura(str(CAP / "consola_api.png"), "Consola de la API durante la prueba", ancho=4.2)
    D.p("Problemas que tuve: el sensor no respondía porque tenía intercambiados los cables de alimentación y de "
        "datos; algunas lecturas salían en cero hasta que conecté el sensor directo a la placa; esas lecturas "
        "abrieron una alerta falsa, así que borré los datos y reinicié la API; y Windows bloqueaba al NodeMCU "
        "hasta que abrí el puerto 3001 en el firewall. No alcancé a probar el cierre de la alerta con el "
        "circuito; lo probé con peticiones desde la computadora.")

    D.h1("13. Administración del proyecto")
    D.p("El equipo usa el GitHub Project CalendarizacionIoTEquipo2G507: https://github.com/users/cyuxSz/projects/1")
    D.figura_doble([str(CAP / "github_kanban.png"), str(CAP / "github_kanban_final.png")],
                   "Kanban a la mitad de la etapa (izquierda) y un día antes de la entrega (derecha)", ancho=3.1)
    D.figura_doble([str(CAP / "github_roadmap.png"), str(CAP / "github_roadmap_final.png")],
                   "Gantt a la mitad de la etapa (izquierda) y un día antes de la entrega (derecha)", ancho=3.1)
    D.p("Lo más atrasado es la prueba con el hardware final, porque las piezas llegaron tarde. Lo resolvimos "
        "probando primero la API desde la computadora y después cada nodo con el material del kit. Falta repetir "
        "la prueba con el DHT22, el buzzer y la pantalla, y conectar los cinco nodos a la vez.")

    D.referencias([
        "Espressif Systems. (s. f.). *ESP8266EX datasheet* (Versión 7.1). https://documentation.espressif.com/0a-esp8266ex_datasheet_en.pdf",
        "ESP8266 Community. (s. f.). *ESP8266WiFi library*. ESP8266 Arduino Core. https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html",
        "OpenJS Foundation. (s. f.). *Express 5.x API reference*. https://expressjs.com/en/5x/api.html",
        "Oracle. (s. f.-a). *Date and time functions*. MySQL 8.4 Reference Manual. https://dev.mysql.com/doc/refman/8.4/en/date-and-time-functions.html",
        "Oracle. (s. f.-b). *Comparison functions and operators*. MySQL 8.4 Reference Manual. https://dev.mysql.com/doc/refman/8.4/en/comparison-operators.html",
        "Sidorares, A. (s. f.). *MySQL2 documentation*. https://sidorares.github.io/node-mysql2/docs",
    ])
    D.guardar(str(SAL / f"Etapa3_Documentacion_{SUF}.docx"))


if not os.environ.get("SOLO_DOCS"):  # SOLO_DOCS=1: no borra la carpeta de entrega ya configurada y probada
    armar_carpeta()
doc_indicadores()
doc_tecnico()
print("listo:", SAL.relative_to(R))
for f in sorted(SAL.rglob("*")):
    if f.is_file():
        print("  ", f.relative_to(SAL))
