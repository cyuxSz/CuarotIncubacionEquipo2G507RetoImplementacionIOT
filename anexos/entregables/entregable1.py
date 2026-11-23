import sys
from docx_lib import Doc

SAL = sys.argv[1]
M = "media/"
D = Doc()
D.portada("Etapa 2 - Administración del Reto - Software - Diseño", logo=M + "image1.png")

# ---------------- 1 ----------------
D.h1("1. Investigación de artículos científicos de IoT con modelos de datos")
D.h2("a) Descripción general del proyecto y prototipo a desarrollar")
D.p("Nuestro proyecto es un sistema IoT de monitoreo y aviso (no de control) para el cuarto de incubación in vitro del Invernadero Académico, donde se cultivan plantas pequeñas en frascos de vidrio sellados. Hoy el cuarto se revisa a mano: si la temperatura (ideal de 22 a 28 °C) o la humedad relativa (40 a 60 %) se salen de rango durante horas, nadie se entera a tiempo y pueden perderse semanas de trabajo. El dominio es la agricultura en ambiente controlado (cultivo de tejidos vegetales). El sistema mide el ambiente, guarda el historial, lo muestra en un dashboard web y avisa al equipo por WhatsApp y Telegram; si la falla es de temperatura o humedad, además suena una alarma dentro del cuarto. El prototipo se instalará y probará en el cuarto real.")
D.p("El prototipo usa cinco NodeMCU (ESP8266), uno por integrante, repartidos en tres cajas impresas en PETG. El nodo `dht` va solo en su caja para que el calor de la electrónica no altere la lectura. Los nodos `pir` y `puerta` comparten la estación de entrada, y `acel` y `luz` la estación del anaquel. Cada caja tiene una fuente de 5 V; dentro de una estación las dos placas comparten 5 V y tierra, pero cada una conserva su propio regulador de 3.3 V. Los nodos se conectan al WiFi del invernadero y publican mensajes JSON por MQTT a un broker Mosquitto; n8n los recibe, los guarda en MySQL 8 y evalúa las reglas de alerta. Todo corre en Docker, primero en una laptop y después en una máquina gratuita de Oracle Cloud.")
D.p("Aprovechamos los sensores y protoboards del kit del curso y solo se solicitan dos sensores extra (un DHT22 y un reed switch MC-38), un convertidor ADS1115 para el acelerómetro y material menor (capacitores, transistor, resistencias, jumpers y cables). El presupuesto máximo aproximado es de $1,500 MXN.")
D.tabla("Nodos del prototipo, sensor y origen del componente", [
    ["Nodo", "Qué monitorea", "Sensor", "Caja", "Origen"],
    ["dht", "Temperatura y humedad", "DHT22 (una lectura cada 30 s)", "Propia", "Extra: reemplaza al DHT11 del kit (±0.5 °C)"],
    ["luz", "Luz / fotoperiodo", "Fotorresistencia (lectura analógica)", "Anaquel", "Kit"],
    ["pir", "Movimiento / accesos", "PIR HC-SR501", "Entrada", "Kit"],
    ["puerta", "Puerta abierta o cerrada", "Reed switch MC-38", "Entrada", "Extra: reemplaza al ultrasónico"],
    ["acel", "Golpes / vibración", "GY-61 (ADXL335) leído por un ADS1115", "Anaquel", "GY-61 del kit; ADS1115 extra"],
], anchos=[0.8, 1.3, 1.6, 0.8, 2.0])
D.p("Cada nodo tiene un sensor y un actuador: un LED rojo que reacciona a su sensor (`pir`, 5 s tras un movimiento; `puerta`, mientras está abierta; `acel`, 5 s tras un golpe; `luz`, cuando lee las lámparas apagadas; `dht`, mientras hay alerta de temperatura o humedad). El `dht` tiene además el buzzer KY-012 con transistor, el único actuador que suena; lo enciende la regla local del nodo o la orden de n8n. El LED verde solo indica si el nodo está conectado. El sistema no controla el minisplit ni las lámparas. Los nodos no tienen reloj, así que la base de datos pone la hora al recibir cada dato: se guarda en UTC y se muestra en hora de Monterrey. Una alerta se abre cuando una medición sale de rango tres lecturas seguidas y se cierra al normalizarse, con un margen (histéresis) para no repetir avisos.")

D.h2("b) Revisión de artículos")
D.tabla("Artículos revisados por integrante", [
    ["Integrante", "Artículo y enlace", "Dominio", "Modelo revisado"],
    ["José María García", "Arz von Straussenburg et al. (2024). Extending the SensorThings API data model. CEUR-WS Vol. 3849.\nhttps://ceur-ws.org/Vol-3849/forum1.pdf", "Agricultura / invernadero (dominio del Reto)", "Modelos ER con cardinalidades (mín, máx): Figs. 1, 2, 4 y 9. La Fig. 3 es un esquema de módulos y no se usa."],
    ["Arianna Téllez", "Abuseta (2020). A context aware framework for IoT based healthcare monitoring systems. arXiv.\nhttps://arxiv.org/abs/2008.10341", "Salud (monitoreo de pacientes)", "Metamodelo (Fig. 1) y clases UML de los componentes (sección III-D). Las Figs. 2 y 3 son lazos de control (arquitectura) y no se usan."],
    ["Iván Acosta", "Thramboulidis y Christoulakis (2015). UML4IoT. arXiv.\nhttps://arxiv.org/abs/1512.04894", "Manufactura / Industria 4.0", "Perfil UML con clases estereotipadas para componentes ciberfísicos. Se revisó el perfil de clases, no el código generado."],
    ["Mía Nieto", "Geller y Meneses (2021). Modelling IoT systems with UML. Am. J. Eng. Appl. Sci., 14(1).\nhttps://doi.org/10.3844/ajeassp.2021.81.93", "Energía", "Modelo de dominio con clases UML (Fig. 12) y casos de uso para requerimientos (Figs. 8, 11 y 18). Las Figs. 6 y 16 son arquitectura y no se usan."],
    ["Luis Mendoza", "Li et al. (2018). A unified knowledge representation and context-aware recommender system in Internet of Things. arXiv.\nhttps://arxiv.org/abs/1805.04007", "Edificios inteligentes / recursos IoT", "Modelo ER de recursos IoT (Fig. 1) y atributos de sensor, actuador y rango de operación (Tabla 1). Las Figs. 2 y 5 son arquitectura y proceso y no se usan."],
], anchos=[1.1, 2.4, 1.2, 1.8])

D.h2("c) Integración de la investigación")
D.p("La tabla integradora se presenta en fichas. Cada ficha indica el integrante que revisó el artículo, el problema, el enlace, las entidades y relaciones, los sensores, las mediciones, los actuadores y lo que aporta a nuestro proyecto.")
fichas = [
    ("José María García · Arz von Straussenburg et al. (2024) · Agricultura / invernadero", [
        "Plataforma de datos IoT para invernaderos y campos, con gestión de dispositivos y alertas.",
        "https://ceur-ws.org/Vol-3849/forum1.pdf",
        "Un Thing (1:N) tiene Sensores; un Datastream agrupa las Observation de un Sensor y una ObservedProperty. Device (con DeviceType) se conecta a Sensor y Actuator y genera Event. Rule y FailureDetection activan un Trigger que lleva a AlertConfig y AlertChannel (hacia el User).",
        "Sensores ambientales de campo e invernadero (Sensor dentro de un Thing).",
        "Temperatura, humedad, humedad de suelo y luminosidad, como observaciones con propiedad observada.",
        "Actuator, TaskingCapability y Task (por ejemplo, válvulas de riego o abrir ventanas).",
        "Separar nodo, sensor y medición; reglas y alertas aparte; canales de aviso y estado del dispositivo como entidades."]),
    ("Arianna Téllez · Abuseta (2020) · Salud", [
        "Monitoreo de pacientes con IoT que usan el contexto para decidir.",
        "https://arxiv.org/abs/2008.10341",
        "MonitoredElement (Patient, Elderly, Disabled) se asocia a 0..* Sensor y tiene un MedicalHistory. Context y ContextHistory alimentan un Insight; este llega a un InterestedParty por InterestRegistration.",
        "Sensores de signos vitales y del entorno asociados al paciente.",
        "Signos vitales, temperatura de la habitación y actividad.",
        "Sin actuadores físicos: acciones correctivas y notificaciones a interesados.",
        "Una alerta nace de reglas sobre el historial y se notifica a interesados (canales)."]),
    ("Iván Acosta · Thramboulidis y Christoulakis (2015) · Manufactura", [
        "Integrar componentes ciberfísicos de manufactura a IoT con un perfil UML.",
        "https://arxiv.org/abs/1512.04894",
        "Un componente ciberfísico (clase UML) expone recursos observables (estado y lecturas) y recursos operables (comandos) mediante una interfaz.",
        "Sensores de la planta, vistos como recursos observables del componente.",
        "Estado y variables de proceso expuestos como recursos observables.",
        "Actuadores industriales, como recursos operables (comandos).",
        "Distinguir lo que se observa (Medición, Evento) de lo que se ordena (AcciónControl del buzzer y de los LED rojos)."]),
    ("Mía Nieto · Geller y Meneses (2021) · Energía", [
        "Modelar con UML un sistema IoT que monitorea y predice el consumo eléctrico.",
        "https://doi.org/10.3844/ajeassp.2021.81.93",
        "Clases «participant»: equipo monitoreado, sensor, página web y red LSTM; servicios de actualizar datos y predecir. Casos de uso para requerimientos funcionales y no funcionales.",
        "Sensor de corriente en el equipo monitoreado.",
        "Consumo eléctrico como serie de tiempo.",
        "No tiene: solo monitorea y predice.",
        "Redactar requerimientos como objetivos verificables. Un sistema de monitoreo es válido aunque tenga pocos actuadores; el nuestro usa un LED rojo por nodo y un buzzer."]),
    ("Luis Mendoza · Li et al. (2018) · Edificios inteligentes / recursos IoT", [
        "Representar con un modelo unificado los recursos IoT (físicos, de borde y de nube).",
        "https://arxiv.org/abs/1805.04007",
        "Resource se especializa en recursos físicos (Sensor, Actuator), edge y nube; un Service accede a varios recursos. Cada sensor y actuador tiene un OperatingRange.",
        "Sensores de temperatura y otros, con rango de operación, precisión y exactitud.",
        "Temperatura y otras magnitudes con su rango; disponibilidad del sensor.",
        "Actuator con atributo de disponibilidad.",
        "El atributo de disponibilidad inspira EstadoNodo; la precisión del sensor (DHT22 ±0.5 °C) se documenta, sin entidad propia."]),
]
filas = [["Ficha", "Contenido"]]
etiq = ["Problema", "Enlace", "Entidades y relaciones", "Sensores", "Mediciones", "Actuadores", "Aporte"]
for cab, vals in fichas:
    filas.append([cab, ""])
    filas += [[e, v] for e, v in zip(etiq, vals)]
t = D.tabla("Fichas de integración de los artículos revisados", filas, anchos=[1.5, 5.0])
# fila de cabecera de cada ficha: combinar y sombrear
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
for i, fila in enumerate(filas):
    if i and fila[1] == "":
        c = t.cell(i, 0).merge(t.cell(i, 1))
        sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), "DCE9F7")
        c._tc.get_or_add_tcPr().append(sh)

D.p("**Elementos comunes.** Los cinco modelos separan el dispositivo del dato que produce; toda medición lleva valor, unidad y tiempo; las reglas o umbrales viven aparte de las lecturas; y el actuador, cuando existe, es una entidad con sus propias órdenes. Cuatro de los cinco consideran también el estado o la disponibilidad del dispositivo o la notificación a personas.")
D.p("**Diferencias.** Los modelos de CEUR y de edificios son genéricos y buscan interoperabilidad; los de salud y energía son concretos y están pensados para su dominio. Dos usan ER con cardinalidades y tres usan UML. Solo el de energía no tiene actuadores. El del invernadero agrega usuarios, cuentas y licencias, que no necesitamos. Ninguno agrupa varios dispositivos en un mismo gabinete; esa entidad (Caja) la agregamos nosotros porque dos nodos de una estación comparten ubicación y fuente.")
D.p("**Ideas aplicables y justificación.** Solo se tomó lo que responde a un requisito del cuarto de incubación:")
D.tabla("Ideas tomadas de los artículos y su pertinencia", [
    ["Idea (fuente)", "Cómo se aplica en Argos", "Por qué es pertinente"],
    ["1. Separar nodo, sensor, parámetro y medición (José María; Luis)", "Entidades Nodo, Sensor, Parametro y Medicion.", "Un DHT22 produce dos parámetros; el catálogo evita repetir unidades en cada lectura."],
    ["2. Reglas y alertas fuera de las lecturas (José María; Arianna)", "Umbral (límites, histéresis, persistencia) y Alerta con inicio y fin.", "Los límites 22 a 28 °C y 40 a 60 % se cambian en un solo lugar, sin tocar las mediciones."],
    ["3. Canales de aviso explícitos (José María; Arianna)", "Canales de la alerta (WhatsApp o Telegram), atributo multivaluado.", "Una alerta puede avisar por más de un canal."],
    ["4. Actuador y órdenes como entidades (José María; Iván; Luis)", "Actuador (buzzer y LED rojo de cada nodo) y AccionControl con su origen, ligada a la alerta cuando la ordena n8n.", "Cada encendido queda registrado y se sabe si lo decidió el nodo, una alerta o una prueba manual."],
    ["5. Estado del dispositivo (José María; Luis)", "EstadoNodo: en línea, último reporte, RSSI, motivo de reinicio.", "Una alimentación inestable causa falsos avisos; hay que distinguirlos de una falla real."],
    ["6. Eventos aparte de las mediciones (José María; Arianna)", "Evento: movimiento, golpe, puerta abierta o cerrada, falla del sensor.", "Son sucesos puntuales, no series de lecturas."],
    ["7. Requerimientos como objetivos verificables (Mía)", "RF y RNF numerados por integrante (sección 2).", "Cada requisito se puede comprobar en pruebas."],
    ["No adoptado (varios)", "Usuarios, cuentas y licencias; historial de ubicación; contexto médico; predicción con IA.", "Fuera del alcance: un solo cuarto, un equipo y actuadores de aviso."],
], anchos=[2.0, 2.3, 2.2])

# ---------------- 2 ----------------
D.h1("2. Análisis y especificación de requerimientos")
D.h2("a) Requerimientos funcionales y no funcionales")
D.tabla("Requerimientos funcionales y no funcionales", [
    ["Clave", "Responsable", "Requerimiento"],
    ["RF01", "Luis Mendoza (nodo pir)", "El sistema deberá registrar cada evento de movimiento con su fecha y hora, indicar si ocurrió fuera del horario autorizado de acceso (guardado en Configuración) y encender el LED rojo del nodo durante 5 s tras cada detección."],
    ["RF02", "José María García (nodo dht)", "El sistema deberá almacenar las mediciones de temperatura y humedad del DHT22 con su parámetro, unidad y marca de tiempo."],
    ["RF03", "Arianna Téllez (nodo luz)", "El sistema deberá registrar el nivel de luz de la fotorresistencia, encender el LED rojo cuando lea las lámparas apagadas y abrir una alerta cuando el nivel no coincida con el fotoperiodo esperado."],
    ["RF04", "Iván Acosta (nodo puerta)", "El sistema deberá registrar la apertura y el cierre de la puerta, mantener encendido el LED rojo mientras esté abierta y abrir una alerta si permanece abierta más del tiempo configurado."],
    ["RF05", "Mía Nieto (nodo acel)", "El sistema deberá registrar cada golpe o vibración con su magnitud, encender el LED rojo durante 5 s y abrir una alerta cuando supere el umbral calibrado."],
    ["RF06", "Equipo", "El sistema deberá abrir una alerta cuando la temperatura o la humedad salgan de su rango durante tres lecturas seguidas y cerrarla cuando se normalicen, considerando la histéresis."],
    ["RF07", "Equipo", "El sistema deberá registrar los canales (WhatsApp y/o Telegram) por los que se avisó cada alerta."],
    ["RF08", "Equipo", "El sistema deberá registrar cada acción de control de los seis actuadores (buzzer y LED rojos), indicando si la originó una alerta, la regla local del nodo o una prueba manual."],
    ["RF09", "Equipo", "El sistema deberá registrar el estado de cada nodo (en línea o fuera de línea, último reporte, señal, motivo de reinicio) y abrir una alerta si un nodo deja de reportar o su sensor falla."],
    ["RF10", "Equipo", "El sistema deberá permitir consultar el último valor y el historial de temperatura, humedad, luz, accesos y golpes, y el estado de la puerta, para el dashboard."],
    ["RF11", "Equipo", "El sistema deberá registrar a qué caja pertenece cada nodo y la ubicación de la caja."],
    ["RNF01", "Luis Mendoza", "La base de datos deberá implementarse en MySQL 8 (motor InnoDB) con llaves foráneas activas."],
    ["RNF02", "José María García", "Todas las fechas y horas se almacenarán en UTC, asignadas por el servidor de base de datos, y se mostrarán en la zona America/Monterrey."],
    ["RNF03", "Arianna Téllez", "Las mediciones con más de 90 días se purgarán automáticamente (con dos parámetros cada 30 s son unas 5,760 filas al día)."],
    ["RNF04", "Iván Acosta", "Todas las consultas de lectura y escritura deberán usar parámetros (consultas preparadas) para evitar errores e inyección SQL."],
    ["RNF05", "Mía Nieto", "No podrá existir más de una alerta activa para el mismo nodo y tipo al mismo tiempo."],
    ["RNF06", "Equipo", "La base de datos se respaldará periódicamente y deberá poder restaurarse en el servidor de Oracle Cloud."],
    ["RNF07", "Equipo", "Los nodos de una misma caja compartirán la fuente de 5 V, pero nunca su salida de 3.3 V."],
], anchos=[0.7, 1.6, 4.2])

D.h2("b) Descripción textual del problema")
D.p("En el cuarto de incubación in vitro del invernadero académico se instalan cinco nodos NodeMCU repartidos en tres cajas. Cada caja tiene un nombre corto único (`dht`, `entrada` o `anaquel`), una descripción y una ubicación compuesta por área y punto de montaje, y aloja uno o dos nodos. Cada nodo pertenece a una sola caja y tiene un nombre corto único (`dht`, `luz`, `pir`, `puerta` o `acel`) que coincide con su tópico MQTT (por ejemplo, `invernadero/telemetria/dht`), y un responsable del equipo. Cada responsable tiene un nombre único y puede atender uno o más nodos. Un nodo tiene uno o más sensores (DHT22, fotorresistencia, PIR, reed switch y acelerómetro) y cada sensor pertenece a un solo nodo. Cada nodo reporta un único estado: en línea o fuera de línea, fecha del último reporte, motivo del reinicio, tiempo encendido e intensidad de señal.")
D.p("Los sensores de clima y luz producen mediciones. Cada medición pertenece a un sensor y a un parámetro del catálogo (temperatura en °C, humedad en %, luz), tiene un valor y una fecha y hora que asigna la base de datos al recibirla, en UTC. Los sensores de movimiento, golpe y puerta producen eventos puntuales (movimiento, golpe, puerta abierta o cerrada) con fecha y hora, una magnitud opcional y una marca que indica si ocurrieron fuera del horario autorizado. Cualquier sensor produce además un evento `sensor_error` cuando deja de dar lecturas válidas, y ese evento abre una alerta de tipo `sensor_falla`.")
D.p("Para decidir cuándo avisar se usan umbrales: cada umbral se aplica a un sensor y a un parámetro que ese sensor mide, y define mínimo, máximo, histéresis, número de lecturas seguidas (tres) y si se debe encender la alarma. Cuando se incumple un umbral, o cuando ocurre una condición sin umbral (golpe, puerta abierta, movimiento fuera de horario, falla del sensor o nodo que no reporta), se abre una alerta de un nodo, con tipo, valor, inicio y fin; la alerta está activa mientras no tenga fin. Cada alerta se avisa por uno o más canales (WhatsApp y/o Telegram); de cada aviso se guarda si se envió y cuándo. La duración se calcula como fin menos inicio.")
D.p("Cada nodo tiene al menos un actuador, su LED rojo, y el nodo `dht` tiene además un buzzer. Un actuador pertenece a un solo nodo y ejecuta acciones de control (encender o apagar) con fecha y hora y, si aplica, una duración. Cada acción tiene un origen: una alerta (el buzzer que ordena n8n), la regla local del nodo (el LED que reacciona a su sensor) o una prueba manual. Solo las acciones originadas por una alerta quedan ligadas a ella. El sistema guarda además parámetros de configuración como pares clave y valor (horario de lámparas, horario de acceso, umbral de golpe).")
D.p("**Restricciones.** El nombre de la caja, el del nodo y el del parámetro son únicos; el máximo de un umbral es mayor que su mínimo; el fin de una alerta no es anterior a su inicio; toda medición, evento y alerta tiene valor y fecha obligatorios; no puede haber dos alertas activas del mismo nodo y tipo; y un nodo no puede tener dos actuadores del mismo tipo.")
D.p("**Eventos históricos.** El sistema conserva como historial las mediciones (90 días), los eventos, las alertas con sus avisos (canal y estado de envío) y las acciones de control, para consultarlos en el dashboard y revisar qué pasó antes y después de una falla.")
D.h3("Reglas de negocio")
for k, v in [
    ("RN1.", "Un nodo tiene uno o varios sensores; cada sensor pertenece a un solo nodo (1:N, participación total del sensor)."),
    ("RN2.", "Una medición pertenece exactamente a un sensor y a un parámetro; un sensor y un parámetro tienen muchas mediciones (1:N)."),
    ("RN3.", "Un evento pertenece a un solo sensor; un sensor puede registrar muchos eventos (1:N, participación parcial del sensor)."),
    ("RN4.", "Un nodo genera muchas alertas y cada alerta es de un solo nodo (1:N). Una alerta puede estar regida por un umbral o no (puerta, golpe, falla del sensor y nodo sin reporte no tienen umbral); un umbral rige muchas alertas."),
    ("RN5.", "No puede haber dos alertas activas del mismo nodo y tipo al mismo tiempo."),
    ("RN6.", "Toda alerta se avisa por al menos un canal (WhatsApp y/o Telegram); no se repite el mismo canal para una alerta, y de cada aviso se registra si se envió y cuándo."),
    ("RN7.", "Cada nodo tiene uno o dos actuadores: todos tienen su LED rojo y solo el `dht` tiene además el buzzer. Un actuador pertenece a un solo nodo y ejecuta muchas acciones. Una acción pertenece a un actuador y puede originarse en una alerta (participación opcional); si su origen es `alerta`, la alerta es obligatoria, y en otro caso queda vacía."),
    ("RN8.", "Cada nodo tiene exactamente un estado reportado (1:1)."),
    ("RN9.", "Una caja aloja uno o dos nodos y cada nodo está en exactamente una caja (1:1..2, participación total en ambos lados)."),
    ("RN10.", "Un nodo no puede tener dos actuadores del mismo tipo."),
    ("RN11.", "Cada nodo tiene un solo responsable y un responsable puede atender uno o más nodos (1:N, participación total en ambos lados). El nombre del responsable es único."),
    ("RN12.", "Cada umbral se aplica a un solo sensor y a un solo parámetro; un sensor puede tener varios umbrales (uno por parámetro que mide) o ninguno (los sensores de evento no tienen umbral). Un sensor no tiene dos umbrales del mismo parámetro."),
]:
    D.regla(k, v)
D.p("**Verificación del texto.** Permite identificar las entidades, atributos, relaciones, cardinalidades y reglas; es coherente con RF01 a RF11 y RNF01 a RNF07; y representa el dominio más allá de las lecturas (cajas, alertas, canales, eventos, estado del nodo, actuadores y configuración).")

# ---------------- 3 ----------------
D.h1("3. Diseño conceptual: diagrama de clases UML")
D.p("Se eligió un diagrama de clases UML para representar atributos, identificadores, cardinalidades y participación. Tiene trece clases conectadas más una de configuración sin relaciones, cada una justificada por una necesidad de información. Las llaves foráneas no se dibujan: se obtienen de las relaciones en el diseño lógico.")
D.figura("fig/uml.png", "Diagrama de clases UML de Argos (14 clases)", ancho=4.9,
         nota="La barra diagonal (/) marca atributos derivados. La ubicación de Caja es un atributo compuesto por área y punto de montaje.")
D.h3("Clases y justificación")
D.tabla("Clases del modelo y su justificación", [
    ["Clase", "Identificador", "Justificación"],
    ["Caja", "id_caja", "Gabinete impreso con su fuente de 5 V (dht, entrada, anaquel); guarda la ubicación que comparten sus nodos."],
    ["Responsable", "id_responsable", "Integrante del equipo que atiende uno o más nodos; guarda su nombre una sola vez."],
    ["Nodo", "id_nodo", "Cada microcontrolador del cuarto (dht, luz, pir, puerta, acel)."],
    ["Sensor", "id_sensor", "Sensor instalado en un nodo; guarda su modelo."],
    ["Parámetro", "id_parametro", "Catálogo de magnitudes medidas con su unidad (evita repetirla)."],
    ["Medición", "id_medicion", "Cada lectura de temperatura, humedad o luz."],
    ["Evento", "id_evento", "Sucesos puntuales: movimiento, golpe, puerta abierta o cerrada, falla del sensor."],
    ["Umbral", "id_umbral", "Reglas de comparación de un sensor para un parámetro (rango, histéresis, persistencia, alarma)."],
    ["Alerta", "id_alerta", "Episodio de aviso con inicio y fin; está activa mientras no tenga fin."],
    ["Notificación", "id_alerta, canal", "Aviso de una alerta por un canal (WhatsApp o Telegram), con su estado de envío."],
    ["Actuador", "id_actuador", "El buzzer del nodo dht y el LED rojo de cada nodo (seis en total)."],
    ["AcciónControl", "id_accion", "Cada orden de encender o apagar un actuador, con su origen y duración."],
    ["EstadoNodo", "id_nodo", "Conexión y salud de cada nodo (1:1 con Nodo)."],
    ["Configuración", "clave", "Parámetros operativos (horarios, umbral de golpe, umbral de luz)."],
], anchos=[1.3, 1.3, 3.9])
D.h3("Cardinalidades y participación")
D.tabla("Relaciones, cardinalidades y participación", [
    ["Relación", "Cardinalidad", "Participación"],
    ["Caja aloja Nodo", "1 caja : 1..2 nodos", "Total en ambos lados (RN9)."],
    ["Responsable responde de Nodo", "1 responsable : 1..* nodos", "Total en ambos lados (RN11)."],
    ["Nodo tiene Sensor", "1 nodo : 1..* sensores", "Total en ambos lados (RN1)."],
    ["Nodo reporta EstadoNodo", "1 : 1", "Total en ambos lados (RN8)."],
    ["Sensor produce Medición", "1 sensor : 0..* mediciones", "Total de la medición (RN2)."],
    ["Parámetro describe Medición", "1 parámetro : 0..* mediciones", "Total de la medición (RN2)."],
    ["Sensor registra Evento", "1 sensor : 0..* eventos", "Total del evento, parcial del sensor (RN3)."],
    ["Nodo genera Alerta", "1 nodo : 0..* alertas", "Total de la alerta (RN4)."],
    ["Umbral rige Alerta", "0..1 umbral : 0..* alertas", "Parcial en ambos lados (RN4)."],
    ["Alerta se avisa por Notificación", "1 alerta : 1..* notificaciones", "Total en ambos lados (RN6)."],
    ["Parámetro se evalúa con Umbral", "1 parámetro : 0..* umbrales", "Total del umbral."],
    ["Sensor se compara con Umbral", "1 sensor : 0..* umbrales", "Total del umbral, parcial del sensor (RN12)."],
    ["Nodo posee Actuador", "1 nodo : 1..2 actuadores", "Total en ambos lados (RN7, RN10)."],
    ["Actuador ejecuta AcciónControl", "1 actuador : 0..* acciones", "Total de la acción (RN7)."],
    ["Alerta dispara AcciónControl", "0..1 alerta : 0..* acciones", "Parcial: las acciones locales y manuales no tienen alerta (RN7)."],
], anchos=[2.3, 2.1, 2.1])
D.p("**Atributos revisados.** Compuesto: la ubicación de la caja se descompone en área y punto de montaje. Multivaluado: canales de la alerta (WhatsApp y/o Telegram), que se modelan como la clase Notificación con su estado de envío. Derivados: la duración (fin menos inicio) y el estado de la alerta no se almacenan, porque la alerta está activa mientras no tenga fin. La fecha y hora de las mediciones las asigna el reloj del servidor.")
D.h3("Cobertura de requerimientos")
D.tabla("Requerimientos y clases que los representan", [
    ["Requerimientos", "Clases que los representan"],
    ["RF01, RF04, RF05", "Evento, Sensor, Actuador, AcciónControl, Configuración"],
    ["RF02, RF03", "Medición, Parámetro, Sensor, Configuración (y AcciónControl del LED en RF03)"],
    ["RF06", "Umbral, Sensor, Alerta, Parámetro"],
    ["RF07", "Alerta, Notificación"],
    ["RF08", "Actuador, AcciónControl, Alerta"],
    ["RF09", "EstadoNodo, Evento, Alerta"],
    ["RF10", "Medición, Evento, Alerta, EstadoNodo"],
    ["RF11", "Caja, Nodo, Responsable"],
], anchos=[1.8, 4.7])

# ---------------- 4 ----------------
D.h1("4. Diseño lógico: modelo relacional")
D.p("**Reglas de mapeo aplicadas.** Cada clase se convierte en una relación. Las relaciones 1:N se resuelven con una llave foránea en el lado «muchos»; así, Nodo recibe id_caja e id_responsable y Umbral recibe id_sensor. La relación 1:1 (Nodo y EstadoNodo) usa la misma llave como PK y FK. El atributo multivaluado canales se convierte en la relación Notificacion con llave compuesta (id_alerta, canal) y los atributos enviada y ts_envio. El atributo compuesto ubicación se convierte en dos columnas de Caja (area y punto_montaje). Los atributos derivados duración y estado no se almacenan. Las llaves foráneas opcionales (id_umbral en Alerta, id_alerta en AccionControl) aceptan NULL.")
D.tabla("Esquema relacional con llaves primarias y foráneas", [
    ["Relación", "Atributos", "PK", "FK"],
    ["Caja", "id_caja, descripcion, area, punto_montaje", "id_caja", "—"],
    ["Responsable", "id_responsable, nombre", "id_responsable", "—"],
    ["Nodo", "id_nodo, id_caja, id_responsable, descripcion", "id_nodo", "id_caja → Caja; id_responsable → Responsable"],
    ["Sensor", "id_sensor, id_nodo, modelo", "id_sensor", "id_nodo → Nodo"],
    ["Parametro", "id_parametro, nombre, unidad", "id_parametro", "—"],
    ["Medicion", "id_medicion, id_sensor, id_parametro, valor, fecha_hora", "id_medicion", "id_sensor → Sensor; id_parametro → Parametro"],
    ["Evento", "id_evento, id_sensor, tipo, magnitud, fuera_de_horario, fecha_hora", "id_evento", "id_sensor → Sensor"],
    ["Umbral", "id_umbral, id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer", "id_umbral", "id_sensor → Sensor; id_parametro → Parametro; UNIQUE (id_sensor, id_parametro)"],
    ["Alerta", "id_alerta, id_nodo, id_umbral, tipo, valor, ts_inicio, ts_fin", "id_alerta", "id_nodo → Nodo; id_umbral → Umbral (opcional)"],
    ["Notificacion", "id_alerta, canal, enviada, ts_envio", "(id_alerta, canal)", "id_alerta → Alerta"],
    ["Actuador", "id_actuador, id_nodo, tipo", "id_actuador", "id_nodo → Nodo; UNIQUE (id_nodo, tipo)"],
    ["AccionControl", "id_accion, id_actuador, id_alerta, origen, comando, duracion_s, fecha_hora", "id_accion", "id_actuador → Actuador; id_alerta → Alerta (opcional)"],
    ["EstadoNodo", "id_nodo, estado, ultimo_reporte, reset_reason, uptime_s, rssi", "id_nodo", "id_nodo → Nodo"],
    ["Configuracion", "clave, valor", "clave", "—"],
], anchos=[1.2, 2.6, 1.0, 1.7])

# ---------------- 5 ----------------
D.h1("5. Normalización a Tercera Forma Normal (3FN)")
D.p("**1FN.** Todas las relaciones tienen llave primaria y atributos atómicos. El único atributo multivaluado (canales) y el compuesto (ubicación) se resolvieron en el mapeo: guardar «whatsapp,telegram» en una celda violaría 1FN.")
D.p("**2FN.** Todas las relaciones cumplen 1FN y ninguna tiene dependencias parciales. Casi todas tienen llave simple, y en Notificacion, con llave compuesta (id_alerta, canal), los atributos enviada y ts_envio dependen de la llave completa.")
D.p("**3FN.** En la primera versión del modelo, Nodo guardaba area y punto_montaje. Al reunir dos nodos en una misma estación apareció la dependencia transitiva id_nodo → caja → (area, punto_montaje): la ubicación se repetía en los dos nodos de la caja y podía quedar distinta en cada uno. Se descompuso Nodo en Nodo (id_nodo, id_caja, id_responsable, descripcion) y Caja (id_caja, descripcion, area, punto_montaje). El responsable también se separó en su propia relación: guardado como texto en Nodo, el nombre se repetiría y podría escribirse distinto. Además se revisaron otros cuatro puntos con riesgo de redundancia: la unidad (se pasó a Parametro), los datos del umbral dentro de Alerta (no se copian), el estado de la alerta (se eliminó, se obtiene de ts_fin) y el atributo derivable tiene_buzzer (se eliminó). Con estos ajustes no hace falta descomponer más relaciones.")
D.tabla("Dependencias funcionales y justificación de 3FN", [
    ["Relación", "Dependencias funcionales", "Justificación 3FN"],
    ["Caja", "id_caja → descripcion, area, punto_montaje", "La ubicación depende de la caja y no se repite en sus dos nodos."],
    ["Responsable", "id_responsable → nombre; nombre → id_responsable", "nombre es llave candidata: el responsable no se repite en Nodo."],
    ["Nodo", "id_nodo → id_caja, id_responsable, descripcion", "Se quitó la dependencia transitiva id_nodo → id_caja → area, punto_montaje. Sin derivados: tiene_buzzer se obtiene de Actuador."],
    ["Sensor", "id_sensor → id_nodo, modelo", "Las columnas dependen solo de la llave."],
    ["Parametro", "id_parametro → nombre, unidad; nombre → id_parametro, unidad", "La unidad depende del parámetro y no se repite en Medicion ni en Umbral. nombre es llave candidata."],
    ["Medicion", "id_medicion → id_sensor, id_parametro, valor, fecha_hora", "No guarda unidad ni datos del sensor: evita la dependencia transitiva parámetro → unidad."],
    ["Evento", "id_evento → id_sensor, tipo, magnitud, fuera_de_horario, fecha_hora", "El nodo se obtiene por Sensor; no se repite id_nodo."],
    ["Umbral", "id_umbral → id_sensor, id_parametro, minimo, maximo, histeresis, persistencia, activa_buzzer", "Los límites viven solo aquí. (id_sensor, id_parametro) es llave candidata: un sensor no tiene dos umbrales del mismo parámetro."],
    ["Alerta", "id_alerta → id_nodo, id_umbral, tipo, valor, ts_inicio, ts_fin", "No copia parámetro ni límites del umbral. tipo se conserva porque id_umbral es opcional: no existe id_umbral → tipo sobre toda la relación. El estado se obtiene de ts_fin."],
    ["Notificacion", "(id_alerta, canal) → enviada, ts_envio", "Los atributos dependen de la llave completa, no de id_alerta ni de canal por separado: cumple 2FN y 3FN."],
    ["Actuador", "id_actuador → id_nodo, tipo; (id_nodo, tipo) → id_actuador", "(id_nodo, tipo) es llave candidata; no hay dependencias transitivas."],
    ["AccionControl", "id_accion → id_actuador, id_alerta, origen, comando, duracion_s, fecha_hora", "origen no se deduce de id_alerta (las acciones local y manual dejan id_alerta vacío), así que no es redundante."],
    ["EstadoNodo", "id_nodo → estado, ultimo_reporte, reset_reason, uptime_s, rssi", "Relación 1:1 separada porque se actualiza en cada reporte."],
    ["Configuracion", "clave → valor", "Una sola dependencia, sin transitividad."],
], anchos=[1.2, 2.6, 2.7])
D.p("**Esquema relacional final normalizado.** Es el de la sección 4, con 14 relaciones.")

# ---------------- 6 ----------------
D.h1("6. Diseño físico: diccionario de datos")
D.p("Todas las fechas y horas son UTC; el servidor MySQL se configura con `time_zone = '+00:00'`. Los campos AUTO_INCREMENT generan los identificadores numéricos.")
CAB = ["Atributo", "Descripción", "Tipo", "Long.", "Restricciones"]
AN = [1.25, 1.95, 0.95, 0.5, 1.85]
dic = {
 "Caja": [
    ["id_caja", "Nombre corto de la caja (dht, entrada, anaquel)", "VARCHAR", "10", "PK, NOT NULL"],
    ["descripcion", "Qué nodos aloja", "VARCHAR", "60", "NOT NULL"],
    ["area", "Área de instalación", "VARCHAR", "40", "NOT NULL, DEFAULT 'Cuarto de incubación'"],
    ["punto_montaje", "Punto de montaje (pared, anaquel, etc.)", "VARCHAR", "40", "NULL"]],
 "Responsable": [
    ["id_responsable", "Identificador del responsable", "INT", "—", "PK, AUTO_INCREMENT"],
    ["nombre", "Nombre del integrante", "VARCHAR", "60", "UNIQUE, NOT NULL"]],
 "Nodo": [
    ["id_nodo", "Nombre corto del nodo (igual al tópico MQTT)", "VARCHAR", "10", "PK, NOT NULL"],
    ["id_caja", "Caja que lo aloja", "VARCHAR", "10", "FK → Caja, NOT NULL"],
    ["descripcion", "Qué mide el nodo", "VARCHAR", "60", "NOT NULL"],
    ["id_responsable", "Responsable del nodo", "INT", "—", "FK → Responsable, NOT NULL"]],
 "Sensor": [
    ["id_sensor", "Identificador del sensor", "INT", "—", "PK, AUTO_INCREMENT"],
    ["id_nodo", "Nodo al que pertenece", "VARCHAR", "10", "FK → Nodo, NOT NULL"],
    ["modelo", "Modelo (DHT22, HC-SR501, MC-38, etc.)", "VARCHAR", "40", "NOT NULL"]],
 "Parametro": [
    ["id_parametro", "Identificador del parámetro", "INT", "—", "PK, AUTO_INCREMENT"],
    ["nombre", "Nombre (temperatura, humedad, luz)", "VARCHAR", "30", "UNIQUE, NOT NULL"],
    ["unidad", "Unidad de medida", "VARCHAR", "10", "NOT NULL"]],
 "Medicion": [
    ["id_medicion", "Identificador de la medición", "BIGINT", "—", "PK, AUTO_INCREMENT"],
    ["id_sensor", "Sensor que la produce", "INT", "—", "FK → Sensor, NOT NULL"],
    ["id_parametro", "Parámetro medido", "INT", "—", "FK → Parametro, NOT NULL"],
    ["valor", "Valor medido", "DECIMAL", "8,2", "NOT NULL"],
    ["fecha_hora", "Fecha y hora de recepción (UTC)", "DATETIME", "—", "NOT NULL, DEFAULT CURRENT_TIMESTAMP"]],
 "Evento": [
    ["id_evento", "Identificador del evento", "BIGINT", "—", "PK, AUTO_INCREMENT"],
    ["id_sensor", "Sensor que lo registra", "INT", "—", "FK → Sensor, NOT NULL"],
    ["tipo", "Tipo de evento", "ENUM", "—", "NOT NULL (movimiento, golpe, puerta_abierta, puerta_cerrada, sensor_error)"],
    ["magnitud", "Magnitud (golpes)", "DECIMAL", "8,2", "NULL"],
    ["fuera_de_horario", "Si ocurrió fuera del horario autorizado", "BOOLEAN", "—", "NOT NULL, DEFAULT FALSE"],
    ["fecha_hora", "Fecha y hora (UTC)", "DATETIME", "—", "NOT NULL, DEFAULT CURRENT_TIMESTAMP"]],
 "Umbral": [
    ["id_umbral", "Identificador del umbral", "INT", "—", "PK, AUTO_INCREMENT"],
    ["id_sensor", "Sensor al que se aplica", "INT", "—", "FK → Sensor, NOT NULL"],
    ["id_parametro", "Parámetro que evalúa", "INT", "—", "FK → Parametro, NOT NULL; UNIQUE (id_sensor, id_parametro)"],
    ["minimo", "Valor mínimo aceptado", "DECIMAL", "8,2", "NOT NULL"],
    ["maximo", "Valor máximo aceptado", "DECIMAL", "8,2", "NOT NULL, CHECK (maximo > minimo)"],
    ["histeresis", "Margen para normalizar", "DECIMAL", "8,2", "NOT NULL, DEFAULT 0"],
    ["persistencia", "Lecturas seguidas requeridas", "TINYINT UNSIGNED", "—", "NOT NULL, DEFAULT 3"],
    ["activa_buzzer", "Si la alerta enciende el buzzer", "BOOLEAN", "—", "NOT NULL, DEFAULT FALSE"]],
 "Alerta": [
    ["id_alerta", "Identificador de la alerta", "BIGINT", "—", "PK, AUTO_INCREMENT"],
    ["id_nodo", "Nodo que la genera", "VARCHAR", "10", "FK → Nodo, NOT NULL"],
    ["id_umbral", "Umbral que la rige", "INT", "—", "FK → Umbral, NULL"],
    ["tipo", "Tipo (temperatura, humedad, luz, golpe, puerta_abierta, movimiento_fuera_de_horario, nodo_sin_reporte, sensor_falla)", "VARCHAR", "30", "NOT NULL"],
    ["valor", "Valor que la disparó", "DECIMAL", "8,2", "NULL"],
    ["ts_inicio", "Inicio (UTC)", "DATETIME", "—", "NOT NULL, DEFAULT CURRENT_TIMESTAMP"],
    ["ts_fin", "Fin (UTC); NULL mientras la alerta está activa", "DATETIME", "—", "NULL, CHECK (ts_fin IS NULL OR ts_fin >= ts_inicio)"],
    ["activa_clave", "Columna generada: 1 si la alerta está activa (ts_fin es NULL), NULL si ya terminó", "TINYINT", "—", "GENERATED STORED AS (IF(ts_fin IS NULL, 1, NULL)); UNIQUE (id_nodo, tipo, activa_clave) cumple RN5"]],
 "Notificacion": [
    ["id_alerta", "Alerta avisada", "BIGINT", "—", "PK, FK → Alerta, NOT NULL"],
    ["canal", "Canal de aviso", "ENUM", "—", "PK, NOT NULL (whatsapp, telegram)"],
    ["enviada", "Si el aviso ya se envió", "BOOLEAN", "—", "NOT NULL, DEFAULT FALSE"],
    ["ts_envio", "Fecha y hora del envío (UTC)", "DATETIME", "—", "NULL"]],
 "Actuador": [
    ["id_actuador", "Identificador del actuador", "INT", "—", "PK, AUTO_INCREMENT"],
    ["id_nodo", "Nodo al que pertenece", "VARCHAR", "10", "FK → Nodo, NOT NULL"],
    ["tipo", "Tipo de actuador", "ENUM", "—", "NOT NULL (buzzer, led_rojo); UNIQUE (id_nodo, tipo)"]],
 "AccionControl": [
    ["id_accion", "Identificador de la acción", "BIGINT", "—", "PK, AUTO_INCREMENT"],
    ["id_actuador", "Actuador que la ejecuta", "INT", "—", "FK → Actuador, NOT NULL"],
    ["id_alerta", "Alerta que la originó", "BIGINT", "—", "FK → Alerta, NULL"],
    ["origen", "Quién decidió la acción", "ENUM", "—", "NOT NULL (alerta, local, manual); CHECK ((origen = 'alerta') = (id_alerta IS NOT NULL))"],
    ["comando", "Orden enviada", "ENUM", "—", "NOT NULL (on, off)"],
    ["duracion_s", "Duración del encendido en segundos (LED 5 s); NULL significa hasta un off", "SMALLINT UNSIGNED", "—", "NULL"],
    ["fecha_hora", "Fecha y hora (UTC)", "DATETIME", "—", "NOT NULL, DEFAULT CURRENT_TIMESTAMP"]],
 "EstadoNodo": [
    ["id_nodo", "Nodo reportado", "VARCHAR", "10", "PK, FK → Nodo, NOT NULL"],
    ["estado", "Estado de conexión", "ENUM", "—", "NOT NULL, DEFAULT 'offline' (online, offline)"],
    ["ultimo_reporte", "Último reporte (UTC); lo actualiza el latido", "DATETIME", "—", "NULL"],
    ["reset_reason", "Motivo del último reinicio", "VARCHAR", "60", "NULL"],
    ["uptime_s", "Segundos encendido", "INT UNSIGNED", "—", "NULL"],
    ["rssi", "Intensidad de señal WiFi (dBm)", "SMALLINT", "—", "NULL"]],
 "Configuracion": [
    ["clave", "Nombre del parámetro de configuración", "VARCHAR", "40", "PK, NOT NULL"],
    ["valor", "Valor del parámetro", "VARCHAR", "60", "NOT NULL"]],
}
for nombre, filas in dic.items():
    D.h3(nombre)
    D.tabla(f"Diccionario de datos de {nombre}", [CAB] + filas, anchos=AN, tam=10)

D.h2("Carga de datos desde MQTT (flujo de n8n)")
D.p("Los nodos no escriben en la base de datos. Publican por MQTT y un flujo de n8n suscrito a `invernadero/#` decide en qué tablas guardar cada mensaje. El firmware no publica el estado de sus LED, así que n8n registra la acción del LED rojo a partir del evento y de la regla documentada de cada nodo.")
D.tabla("Destino en la base de datos de cada mensaje MQTT", [
    ["Mensaje", "Tablas que se llenan"],
    ["telemetria/{nodo} con temperatura, humedad o luz", "Medicion (una fila por lectura). Si la luz cruza el umbral configurado, o la temperatura o humedad abren o cierran su alerta, también AccionControl del LED rojo con origen = 'local', solo cuando cambia de estado."],
    ["telemetria/{nodo} con latido", "Solo EstadoNodo.ultimo_reporte; el latido no se guarda como medición."],
    ["evento/{nodo}", "Evento, y AccionControl del LED rojo con origen = 'local' (movimiento o golpe: on 5 s; puerta abierta: on; puerta cerrada: off). Un sensor_error abre además una Alerta de tipo sensor_falla."],
    ["estado/{nodo} (incluye el último deseo, LWT)", "EstadoNodo."],
    ["n8n publica cmd/alarma = on", "AccionControl del buzzer con origen = 'alerta' y su id_alerta; Notificacion por cada canal avisado."],
], anchos=[2.2, 4.3])

# ---------------- 7 ----------------
D.h1("7. Actualización del roadmap del proyecto y Kanban")
D.p("Se actualizaron los cuatro milestones y los 20 issues del proyecto para reflejar únicamente el trabajo pendiente: firmware de los cinco nodos, broker Mosquitto con ACL, esquema de base de datos de 14 clases (con Caja, Responsable y los seis actuadores), flujo n8n de MQTT a MySQL con alertas por WhatsApp y/o Telegram, dashboard con cinco indicadores, instalación física y pruebas P-01 a P-09. Cada issue conservó su número y ahora incluye objetivo, checklist, criterio de aceptación, etiquetas por área y responsable propuesto. Los 20 quedaron integrados al Project y organizados entre Backlog y Por hacer, sin cerrar ni eliminar elementos existentes.")
D.p("Al 21 de octubre el proyecto está en la etapa 3 (base de datos, del 19 de octubre al 6 de noviembre). El diseño físico (cajas, protoboards y firmware) ya compila y pasa sus chequeos automáticos en computadora; lo siguiente es montar MySQL con el esquema de 13 tablas, el broker y el flujo de n8n descrito en la sección 6, usando el simulador de los cinco nodos mientras no se flashean las placas.")
D.figura(M + "image4.png", "Milestones actualizados", ancho=6.2)
D.figura(M + "image5.png", "Issues actualizados con títulos y etiquetas", ancho=4.7)
D.figura(M + "image2.png", "Kanban actualizado", ancho=6.5)
D.figura(M + "image6.png", "Roadmap actualizado", ancho=6.5)

D.referencias([
    "Abuseta, Y. (2020). *A context aware framework for IoT based healthcare monitoring systems* (arXiv:2008.10341). arXiv. https://doi.org/10.48550/arXiv.2008.10341",
    "Arz von Straussenburg, A. F., Aldenhoff, T. T., & Riehle, D. M. (2024). Extending the SensorThings API data model: Improving interoperability and use case flexibility in IoT. En E. Gallinucci & H. Yasar (Eds.), *ER Forum, Special Topics, Posters and Demos 2024 (ER-Companion 2024)* (CEUR Workshop Proceedings, Vol. 3849, pp. 1-14). CEUR-WS.org. https://ceur-ws.org/Vol-3849/forum1.pdf",
    "Geller, M. T. B., & Meneses, A. A. de M. (2021). Modelling IoT systems with UML: A case study for monitoring and predicting power consumption. *American Journal of Engineering and Applied Sciences, 14*(1), 81-93. https://doi.org/10.3844/ajeassp.2021.81.93",
    "Li, Y., Alqahtani, A., Solaiman, E., Perera, C., Jayaraman, P. P., Benatallah, B., & Ranjan, R. (2018). *A unified knowledge representation and context-aware recommender system in Internet of Things* (arXiv:1805.04007). arXiv. https://doi.org/10.48550/arXiv.1805.04007",
    "Thramboulidis, K., & Christoulakis, F. (2015). *UML4IoT: A UML profile to exploit IoT in cyber-physical manufacturing systems* (arXiv:1512.04894). arXiv. https://doi.org/10.48550/arXiv.1512.04894",
])

# ---------------- Anexo ----------------
D.salto()
D.h1("Anexo A. Cambios respecto a la entrega del 20 de octubre")
D.tabla("Cambios incorporados en esta versión", [
    ["#", "Antes", "Ahora", "Motivo"],
    ["1", "Cada nodo con su propia fuente de 5 V", "Tres cajas, una fuente de 5 V por caja: dht sola; estación de entrada (pir + puerta); estación del anaquel (acel + luz)", "Reacomodo del 19 de octubre por presupuesto. Siguen siendo cinco microcontroladores, uno por integrante."],
    ["2", "Único actuador: el buzzer", "Seis actuadores: el buzzer del dht y el LED rojo de cada nodo, que reacciona a su sensor", "El reto pide un sensor y un actuador por integrante. El LED verde es indicador de estado y ya queda en EstadoNodo."],
    ["3", "Nodo guardaba area y punto_montaje", "Nueva clase Caja; Nodo apunta a su caja", "Dos nodos de una estación comparten ubicación; dejarla en Nodo rompía 3FN."],
    ["4", "AccionControl solo con alerta opcional", "Agrega origen (alerta, local, manual) y duracion_s", "El LED rojo lo decide el propio nodo y a veces dura 5 s; el buzzer lo ordena n8n por una alerta."],
    ["5", "Evento sin falla de sensor", "sensor_error en Evento y sensor_falla en Alerta", "El firmware ya lo publica."],
    ["6", "Acelerómetro del kit (modelo por confirmar)", "GY-61 (ADXL335) leído por un ADS1115", "Definido el 19 de octubre."],
    ["7", "Sin regla para el latido", "El latido solo actualiza EstadoNodo.ultimo_reporte", "Evita llenar Medicion de filas sin significado."],
    ["8", "Responsable como texto dentro de Nodo; Umbral ligado solo a Parámetro", "Nueva clase Responsable (Nodo apunta a ella) y Umbral ligado directamente a Sensor además de Parámetro (14 clases)", "El nombre del responsable se repetía en cada nodo; el umbral debe saber a qué sensor se aplica."],
    ["9", "Sin flujo de carga documentado", "Tabla de destino de cada mensaje MQTT (sección 6)", "Es el flujo que se implementará en n8n."],
], anchos=[0.3, 1.6, 2.3, 2.3], primera_negrita=False)

D.guardar(SAL)
print("ok", D.ntab, "tablas", D.nfig, "figuras")
