import os
import sys
from docx_lib import Doc

SAL = sys.argv[1]
R = "C:/Users/luedm/Documents/Estudio/IncuMonitor/"
D = Doc()
# FIGURAS=fritzing: versión alterna con los esquemáticos y armados de hardware/fritzing (para comparar)
FRITZING = os.environ.get("FIGURAS") == "fritzing"
FZ = R + "hardware/fritzing/salida/"
# PROTOBOARD=0: sin las figuras de armado en protoboard. BREVE=1: solo lo que pide la rúbrica del Avance 2
# (sin protoboard, sin la Figura 2 de conexiones, sin el párrafo de la Web API, sin 6.3 batería ni 6.5 costo)
BREVE = os.environ.get("BREVE") == "1"
PROTOBOARD = os.environ.get("PROTOBOARD", "1") != "0" and not BREVE
FIG_TOPOLOGIA = 1 + (not BREVE) + 3 + 2 * PROTOBOARD + 1
FIG_SECUENCIA = FIG_TOPOLOGIA + 2
D.portada("Avance 2: Diseño de hardware, comunicaciones y administración energética",
          subtitulo="Especificación técnica de hardware de Argos: Monitoreo ambiental del cuarto de incubación in vitro",
          logo="media/image1.png", curso="Equipo G507 · TC1004B")

# ------------------------------------------------------------------ 1
D.h1("1. Actualización del proyecto")
D.p("**Nombre:** Argos: Monitoreo ambiental del cuarto de incubación in vitro (en el Avance 1, IncuMonitor; en adelante, Argos). **Objetivo:** vigilar las condiciones ambientales del cuarto de incubación in vitro del Invernadero Académico y avisar a los encargados cuando la temperatura o la humedad salen de rango, cuando se abre la puerta, cuando hay movimiento o un golpe en el anaquel, y cuando la iluminación no coincide con el fotoperiodo. Los rangos que dieron los encargados son 22 a 28 °C y 40 a 60 % de humedad relativa. Argos no controla el clima: el minisplit y las lámparas siguen funcionando como hasta ahora, y los únicos actuadores son señales para las personas (un LED rojo por nodo y un buzzer).")
D.p("Desde el Avance 1 cambiaron varias decisiones de hardware. La Tabla 1 las resume con su motivo; el resto del documento ya usa la versión nueva.")
D.tabla("Cambios relevantes respecto al Avance 1", [
    ["Tema", "Antes", "Ahora", "Motivo"],
    ["Nodo de la puerta", "Sensor ultrasónico HC-SR04 (nodo ultra)", "Reed switch MC-38 (nodo puerta)", "Detecta apertura de forma directa y no depende de reflejos ni de la posición de la persona"],
    ["Cajas y fuentes", "Una caja y una fuente por nodo", "Tres cajas: dht solo, estación de entrada (pir + puerta) y estación del anaquel (acel + luz); una fuente de 5 V por caja", "El arreglo de cinco cajas costaba ≈ $1,843, $343 arriba del tope de $1,500"],
    ["Actuadores", "Un buzzer en el nodo dht", "LED rojo en cada nodo que reacciona a su sensor, más el buzzer del dht", "Cada integrante integra un sensor y un actuador"],
    ["Interfaz local del dht", "Sin pantalla", "OLED SSD1309 de 2.42\" por I²C; el DHT22 pasa de D2 a D4", "Leer la temperatura a 2 m sin abrir el dashboard"],
    ["Acelerómetro", "GY-61 al ADC del NodeMCU", "GY-61 leído por un ADS1115 de 16 bits por I²C", "El NodeMCU solo tiene una entrada analógica y el GY-61 entrega tres ejes"],
    ["Microcontroladores", "Cinco nodos", "Cinco NodeMCU obligatorios, confirmado por los profesores", "Se mantienen las tres cajas; se descartaron las opciones con menos microcontroladores"],
    ["Web API", "n8n sin API propia", "Tres consultas GET de solo lectura con webhooks de n8n", "La Web API es obligatoria en la etapa 3"],
], anchos=[1.1, 1.5, 2.1, 1.8], tam=9.5,
   nota="Las fechas de cada decisión (19 a 22 de octubre de 2026) están en la bitácora del proyecto (Decisiones.md).")
D.p("Argos sigue en iteración. La asignación de pines, los componentes, las cajas y las cifras de este documento son la versión vigente al cierre del avance y pueden cambiar al armar y probar los nodos con las piezas reales. Cada cambio se registra en la bitácora con su motivo, y los valores que aún no se verifican se marcan como [POR CONFIRMAR].")

# ------------------------------------------------------------------ 2
D.h1("2. Arquitectura física y adquisición de datos")
D.p("Argos tiene cinco nodos IoT, cada uno con un NodeMCU v1.0 (módulo ESP-12E con el ESP8266EX; Espressif Systems, s. f.) y a cargo de un integrante. Los cinco van en tres cajas impresas en PETG. Cada caja tiene una función distinta dentro del cuarto (Figura 1). Los nodos solo hablan con el broker MQTT del servidor y nunca entre sí.")
D.figura("cap/prototipo_cajas_fig.png", "Arquitectura física: cinco nodos en tres cajas, con una fuente de 5 V por caja", ancho=6.4,
         nota="Diagrama generado con Archify (tt-a1i, 2026). Medidas nominales de las cajas; se ajustan al medir las piezas reales.")
D.h2("2.1 Matriz de nodos")
D.tabla("Identificación, ubicación y función de cada nodo", [
    ["Nodo (id)", "Plataforma", "Caja y ubicación", "Función", "Sensor y actuadores", "Responsable"],
    ["dht", "NodeMCU v1.0 ESP-12E", "Caja dht, a la altura de los frascos, lejos del minisplit y de las lámparas", "Mide temperatura y humedad; alarma sonora local; muestra los valores en pantalla", "DHT22; OLED 2.42\"; botón; LED rojo; buzzer activo de 5 V con 2N2222", "José María García"],
    ["luz", "NodeMCU v1.0 ESP-12E", "Estación del anaquel; la fotorresistencia va por cable a un capuchón junto a la lámpara", "Comprueba que las lámparas sigan el fotoperiodo", "Fotorresistencia con divisor de 10 kΩ; LED rojo", "Arianna Téllez"],
    ["pir", "NodeMCU v1.0 ESP-12E", "Estación de entrada, junto a la puerta; el sensor asoma por la tapa", "Registra movimiento en la entrada para detectar accesos fuera de horario", "HC-SR501; LED rojo", "Luis Mendoza"],
    ["puerta", "NodeMCU v1.0 ESP-12E", "Estación de entrada; reed en el marco e imán en la hoja", "Registra apertura y cierre de la puerta", "Reed switch MC-38; LED rojo", "Iván Acosta"],
    ["acel", "NodeMCU v1.0 ESP-12E", "Estación del anaquel, atornillada a la repisa", "Detecta golpes o movimientos del anaquel", "GY-61 (ADXL335) con ADS1115; LED rojo", "Mía Nieto"],
], anchos=[0.65, 0.95, 1.45, 1.35, 1.25, 0.85], tam=9)
D.tabla("Adquisición, procesamiento local y transmisión por nodo", [
    ["Nodo", "Variable", "Interfaz y pin", "Muestreo", "Procesamiento local", "Transmisión", "Eventos y actuador"],
    ["dht", "Temperatura (°C) y humedad (%HR)", "1 hilo en D4 (pull-up 10 kΩ)", "Cada 30 s", "Descarta lecturas inválidas o fuera de −10 a 60 °C; persistencia de 3 lecturas e histéresis de 0.5 °C y 2 %HR", "Telemetría cada 30 s", "LED rojo y buzzer con alerta de T o HR; sensor_error tras 3 lecturas inválidas"],
    ["luz", "Nivel de luz (ADC 0 a 1023)", "ADC en A0", "Cada 5 s", "Promedio de 12 muestras; compara contra UMBRAL_ADC", "Promedio cada 60 s", "LED rojo fijo si el promedio indica lámparas apagadas; n8n decide la alerta según el horario"],
    ["pir", "Movimiento (sí/no)", "GPIO D5, salida de 3.3 V del módulo", "Cada vuelta del programa", "Flanco de subida con antirrebote de 10 s", "Evento movimiento; latido cada 60 s", "LED rojo 5 s tras cada detección"],
    ["puerta", "Puerta abierta o cerrada", "GPIO D5 con pull-up interno; reed a GND", "Cada vuelta del programa", "Antirrebote de 50 ms; publica solo cambios", "Eventos puerta_abierta y puerta_cerrada; latido cada 60 s", "LED rojo mientras la puerta esté abierta"],
    ["acel", "Aceleración en X, Y, Z (g)", "I²C en D1/D2 al ADS1115 (0x48), que lee el GY-61 en A0 a A2", "Continuo, ≈ 3 ms por canal a 860 muestras/s", "Calcula |a| y su desviación de 1 g; golpe si supera 0.5 g, con antirrebote de 2 s", "Evento golpe con su magnitud; latido cada 60 s", "LED rojo 5 s tras cada golpe"],
], anchos=[0.55, 0.85, 1.0, 0.75, 1.35, 0.9, 1.1], primera_negrita=True, tam=8.5,
   nota="Valores tomados del firmware de referencia (firmware/src). El umbral de 0.5 g y UMBRAL_ADC = 300 son provisionales y se calibran en sitio.")
D.h2("2.2 Muestreo contra transmisión")
D.p("Cada variable se muestrea al ritmo que necesita su fenómeno y se transmite solo lo que sirve al servidor. La temperatura y la humedad del cuarto cambian en minutos, y el DHT22 necesita al menos 2 s entre lecturas (Aosong Electronics, s. f.), así que el nodo `dht` lee y publica cada 30 s; con la persistencia de tres lecturas, una alerta se confirma en 90 s. La luz se muestrea cada 5 s y se envía el promedio cada minuto, lo que filtra sombras momentáneas y reduce los mensajes doce veces. Movimiento, puerta y golpes son eventos: se vigilan de forma continua y solo se transmite el cambio, con antirrebote para no inundar el broker. Para saber que esos tres nodos siguen vivos aunque no pase nada, mandan un latido cada 60 s.")
D.h2("2.3 Justificación de la distribución")
D.viñetas([
    "**Ubicación y cobertura.** El DHT22 mide el aire a la altura de los frascos, que es lo que importa para el cultivo, y lejos del flujo del minisplit y del calor de las lámparas. El PIR y el reed van en la única entrada del cuarto. La fotorresistencia se coloca junto a la lámpara dentro de un capuchón negro, para que no la confunda la luz de la puerta. El acelerómetro va fijo a la repisa porque lo que se quiere detectar es el golpe sobre ella.",
    "**Condiciones ambientales.** El sensor de temperatura va en una cámara aislada, debajo de la placa, para que el calor del ESP8266 y de la pantalla no altere la lectura. Las cajas son de PETG por su resistencia a la humedad y a la limpieza [producto de limpieza POR CONFIRMAR con los encargados].",
    "**Longitud de conexiones.** Todos los enlaces locales miden menos de 1 m. Los únicos sensores fuera de su caja son la fotorresistencia y el MC-38, que son señales lentas (analógica y de contacto), así que un cable de ese largo no las afecta. El bus I²C y el bus de un hilo quedan dentro de la caja.",
    "**Alimentación.** Agrupar en tres cajas deja tres fuentes en lugar de cinco y requiere solo tres contactos [contactos cerca del anaquel y de la puerta POR CONFIRMAR].",
])

# ------------------------------------------------------------------ 3
D.h1("3. Integración eléctrica de sensores y actuadores")
D.p("Todos los nodos se alimentan con 5 V en el pin VIN del NodeMCU. El regulador de la placa entrega 3.3 V al ESP8266 y a los sensores de bajo consumo, y los componentes que necesitan 5 V (PIR y buzzer) toman la tensión directamente del riel de VIN. Ninguna señal de más de 3.3 V entra a un GPIO, porque el ESP8266 opera de 2.5 a 3.6 V (Espressif Systems, s. f.).")
D.tabla("Características eléctricas de los componentes", [
    ["Componente", "Alimentación", "Corriente", "Señal o interfaz", "Fuente del dato"],
    ["NodeMCU v1.0 (ESP8266EX)", "5 V en VIN; 3.3 V en el chip", "80 mA promedio; 170 mA al transmitir (802.11b); 15 mA en modem-sleep", "WiFi 2.4 GHz; GPIO de 3.3 V, 12 mA máx. por pin", "Espressif Systems (s. f.)"],
    ["DHT22 (AM2302)", "3.3 a 6 V (se usa 3.3 V)", "1 a 1.5 mA midiendo; 40 a 50 µA en reposo", "Digital de un hilo; ±0.5 °C y ±2 %HR", "Aosong Electronics (s. f.)"],
    ["OLED SSD1309 2.42\"", "3.3 V", "≈ 10 a 20 mA encendida", "I²C, 4 pines", "Valor de diseño; se mide en P-05"],
    ["Fotorresistencia + R2 10 kΩ", "3.3 V", "≤ 0.33 mA (3.3 V / 10 kΩ)", "Analógica al ADC A0", "Cálculo"],
    ["HC-SR501", "VIN (4.5 a 20 V de entrada)", "≈ 65 µA en reposo", "Digital de 3.3 V", "Hoja comercial; se mide en P-05"],
    ["Reed MC-38", "Sin alimentación propia", "Solo la del pull-up interno, < 0.1 mA", "Contacto seco a GND", "Estimado"],
    ["ADS1115", "3.3 V (2 a 5.5 V)", "150 µA en conversión continua", "I²C, dirección 0x48 (ADDR a GND)", "Texas Instruments (2024)"],
    ["GY-61 (ADXL335)", "3.3 V", "< 0.5 mA [POR CONFIRMAR]", "Tres salidas analógicas, ratiométricas", "Sin verificar; se mide en P-05"],
    ["Buzzer activo de 5 V (KY-012 o equivalente)", "5 V desde VIN", "30 mA máx.", "Se enciende con nivel alto en su entrada", "UNIT Electronics, ficha del producto"],
    ["LED verde y rojo con 330 Ω", "GPIO de 3.3 V", "3.3 a 3.9 mA (verde); 3.9 a 4.5 mA (rojo)", "Salida digital D7 y D8", "Cálculo: (3.3 V − Vf) / 330 Ω"],
], anchos=[1.3, 1.1, 1.6, 1.4, 1.1], tam=9)
D.h2("3.1 Asignación de pines")
D.tabla("Pines del NodeMCU por nodo", [
    ["Nodo", "Pin", "Conexión", "Modo"],
    ["dht", "D4 (GPIO2)", "DATA del DHT22 con pull-up de 10 kΩ a 3V3", "Un hilo"],
    ["dht", "D1 (GPIO5) / D2 (GPIO4)", "SCL / SDA de la OLED", "I²C"],
    ["dht", "D5 (GPIO14)", "Base de Q1 (2N2222) por R3 de 1 kΩ; R4 de 10 kΩ de base a GND", "Salida"],
    ["dht", "D6 (GPIO12)", "Botón de silencio a GND", "Entrada con pull-up interno"],
    ["luz", "A0", "Divisor: fotorresistencia a 3V3 y R2 de 10 kΩ a GND", "ADC"],
    ["pir", "D5 (GPIO14)", "OUT del HC-SR501", "Entrada"],
    ["puerta", "D5 (GPIO14)", "Reed MC-38 a GND", "Entrada con pull-up interno"],
    ["acel", "D1 (GPIO5) / D2 (GPIO4)", "SCL / SDA del ADS1115; X, Y, Z del GY-61 a A0, A1, A2 del ADS1115", "I²C"],
    ["Todos", "D7 (GPIO13)", "LED verde por 330 Ω a GND", "Salida"],
    ["Todos", "D8 (GPIO15)", "LED rojo por 330 Ω a GND", "Salida"],
], anchos=[0.8, 1.6, 3.0, 1.1], tam=9.5,
   nota="La tabla coincide con el firmware: el chequeo automático hardware/chequeo_pines.py compara los pines del código con la distribución en protoboard y dio OK en los seis entornos (21 de octubre de 2026).")
D.p("Se evitan D3 (GPIO0) y D4 (GPIO2) porque definen el modo de arranque. D4 se usa en el `dht` solo porque el pull-up del DHT22 lo mantiene en alto al encender, que es justo lo que el arranque necesita. D8 (GPIO15) debe estar en bajo al arrancar, y el LED rojo conectado a GND con 330 Ω no lo sube.")
if not BREVE:
    D.figura("cap/prototipo_cableado_dht_fig.png", "Conexiones del nodo dht a los pines del NodeMCU", ancho=6.3)
if FRITZING:
    D.figura(FZ + "nodo_dht_schematic.png", "Esquemático del nodo dht (Fritzing)", ancho=6.4,
             nota="Cada pin lleva una etiqueta de red; las etiquetas con el mismo nombre están conectadas.")
    D.figura_doble([FZ + "nodo_luz_schematic.png", FZ + "nodo_puerta_schematic.png"],
                   "Esquemáticos de los nodos luz (izquierda) y puerta (derecha), en Fritzing", ancho=3.1)
    D.figura_doble([FZ + "nodo_pir_schematic.png", FZ + "nodo_acel_schematic.png"],
                   "Esquemáticos de los nodos pir (izquierda) y acel (derecha), en Fritzing", ancho=3.1)
else:
    D.figura(R + "hardware/esquematicos/nodo_dht.png", "Esquemático del nodo dht", ancho=5.2)
    D.figura_doble([R + "hardware/esquematicos/nodo_luz.png", R + "hardware/esquematicos/nodo_puerta.png"],
                   "Esquemáticos de los nodos luz (izquierda) y puerta (derecha)", ancho=3.1)
    D.figura_doble([R + "hardware/esquematicos/nodo_pir.png", R + "hardware/esquematicos/nodo_acel.png"],
                   "Esquemáticos de los nodos pir (izquierda) y acel (derecha)", ancho=3.1)
D.h2("3.2 Compatibilidad de niveles y componentes adicionales")
D.viñetas([
    "**Sensores a 3.3 V.** DHT22, OLED, ADS1115, GY-61 y el divisor de la fotorresistencia se alimentan del riel de 3V3, así que sus salidas nunca pasan de 3.3 V.",
    "**PIR a 5 V.** El HC-SR501 se alimenta de VIN, pero su salida sale de un regulador interno de 3.3 V y entra directo a D5 sin divisor. Su mínimo de entrada es 4.5 V y VIN queda en ≈ 4.7 V tras el diodo de la placa, así que se mide en P-02.",
    "**Entrada analógica.** El A0 del NodeMCU ya trae un divisor interno para un rango de 0 a 3.3 V; el divisor de la fotorresistencia nunca lo supera.",
    "**Componentes adicionales.** Resistencia de pull-up de 10 kΩ para el DHT22, R2 de 10 kΩ para el divisor de luz, 330 Ω por LED, R3 de 1 kΩ y R4 de 10 kΩ para el transistor, el 2N2222, el ADS1115 y un capacitor C1 de 220 µF / 16 V entre VIN y GND en cada nodo.",
])
D.h2("3.3 Circuito de accionamiento del buzzer")
D.p("El único actuador que necesita más corriente de la que da un pin es el buzzer. El buzzer activo toma hasta 30 mA a 5 V, más del doble de los 12 mA que soporta un GPIO del ESP8266 (Espressif Systems, s. f.), y además trabaja a 5 V. Por eso se conmuta en el lado bajo con un 2N2222: el positivo del buzzer va a VIN, el negativo al colector y el emisor a GND.")
D.p("Con D5 en alto, la corriente de base es (3.3 V − 0.7 V) / 1 kΩ ≈ 2.6 mA, de la que R4 desvía ≈ 0.07 mA. Para 30 mA de colector eso da una ganancia forzada de ≈ 12, muy por debajo de la ganancia mínima del 2N2222, así que el transistor queda saturado y disipa poco. R4 mantiene la base en bajo mientras el ESP8266 arranca, para que el buzzer no suene al encender. Los LED sí se conectan directo al GPIO porque con 330 Ω piden menos de 4.5 mA.")
D.h2("3.4 Protecciones eléctricas")
D.viñetas([
    "C1 de 220 µF / 16 V en cada entrada de 5 V para absorber los picos del WiFi y del buzzer; se respeta la polaridad y 16 V deja margen sobre 5 V.",
    "El buzzer es piezoeléctrico y no necesita diodo de rueda libre. Si el módulo que llegue resulta electromagnético, se agrega un 1N4148 en antiparalelo [pinout y tipo del módulo POR CONFIRMAR].",
    "En cada estación las dos placas comparten 5 V y GND, pero el riel de 3.3 V de cada placa nunca se une, porque cada una tiene su propio regulador. En la MB-102 se revisa con multímetro que el riel de 3V3 esté partido a la mitad.",
    "Resistencia en serie en cada LED y en la base del transistor, para que ningún pin pase de su corriente máxima.",
    "El proyecto no tiene bombas, motores, válvulas ni otras cargas inductivas: es de monitoreo y no controla el clima del cuarto, así que no hacen falta relevadores ni fuentes de potencia aparte.",
])
if not PROTOBOARD:
    D.p("La distribución paso a paso de cada nodo en protoboard (400 puntos para el `dht` y una MB-102 de 830 puntos en cada estación) está en la guía de armado que se genera desde hardware/breadboard/layouts.py. El chequeo automático de redes de esa guía dio OK en las ocho distribuciones el 21 de octubre de 2026.")
elif FRITZING:
    D.figura(FZ + "nodo_dht_breadboard.png", "Armado en protoboard del nodo dht (400 puntos), en Fritzing", ancho=5.4,
             nota="Fritzing dibuja el NodeMCU Amica visto desde arriba. Con el USB hacia la columna 1, sus pines D0 a D8 quedan del lado de las filas a a e, así que las filas aparecen reflejadas respecto a la guía de armado (a↔j) [verificar con la protoboard real].")
    D.figura(FZ + "nodos_protoboard_fritzing.png", "Armado en protoboard de los nodos luz y puerta (arriba) y pir y acel (abajo), en Fritzing", ancho=6.3,
             nota="Cada nodo se arma y prueba primero solo en una protoboard de 400 puntos; en las estaciones, cada par de nodos pasa a una MB-102 de 830 puntos. Las distribuciones salen de hardware/breadboard/layouts.py.")
else:
    D.figura(R + "presentacion/protoboard/nodo_dht_protoboard.png", "Armado en protoboard del nodo dht (400 puntos)", ancho=5.4)
    D.figura_doble([R + "presentacion/protoboard/estacion_entrada_protoboard.png", R + "presentacion/protoboard/estacion_anaquel_protoboard.png"],
                   "Armado de la estación de entrada (izquierda) y de la estación del anaquel (derecha) en una MB-102 de 830 puntos", ancho=3.1,
                   nota="Las tres distribuciones salen de hardware/breadboard/layouts.py; el chequeo automático de redes dio OK en las ocho distribuciones el 21 de octubre de 2026.")

# ------------------------------------------------------------------ 4
D.h1("4. Protocolos de comunicación")
D.p(f"La comunicación tiene dos niveles. Dentro de cada caja, el microcontrolador habla con sus sensores y actuadores por cable, con el protocolo que cada componente impone. Fuera de la caja, cada nodo se conecta por WiFi al punto de acceso del invernadero y de ahí al broker MQTT del servidor, en una topología de estrella con el broker al centro (Figura {FIG_TOPOLOGIA}). Se eligió MQTT porque es ligero, funciona con publicar y suscribir sobre TCP y define mecanismos de sesión como el último deseo (LWT) y los mensajes retenidos (OASIS, 2014), que se usan para saber si un nodo está en línea.")
D.figura("cap/avance2_topologia_fig.png", "Topología, enlaces y protocolos de Argos", ancho=6.5,
         nota="Diagrama generado con Archify (tt-a1i, 2026). La versión interactiva está en diagramas_interactivos/avance2_topologia.html.")
D.tabla("Protocolos por enlace", [
    ["Enlace", "Emisor → receptor", "Protocolo y medio", "Información", "Cuándo"],
    ["DHT22 ↔ NodeMCU dht", "Sensor → nodo", "Un hilo, cable < 10 cm", "Temperatura y humedad", "Cada 30 s"],
    ["OLED ← NodeMCU dht", "Nodo → pantalla", "I²C a 3.3 V", "Estado, T y HR", "Al pulsar el botón; se apaga a los 30 s"],
    ["ADS1115 ↔ NodeMCU acel", "Nodo ↔ convertidor", "I²C a 3.3 V", "Tensión de los tres ejes", "Continuo"],
    ["Fotorresistencia → NodeMCU luz", "Sensor → nodo", "Analógica (ADC), cable < 1 m", "Nivel de luz", "Cada 5 s"],
    ["PIR, reed y botón → NodeMCU", "Sensor → nodo", "GPIO digital", "Cambio de estado", "Al ocurrir"],
    ["NodeMCU → LED y transistor", "Nodo → actuador", "GPIO digital", "Encendido y apagado", "Según la lógica de la sección 5"],
    ["NodeMCU ↔ punto de acceso", "Bidireccional", "WiFi 802.11 b/g/n, 2.4 GHz", "Tramas TCP/IP", "Permanente"],
    ["NodeMCU ↔ Mosquitto", "Bidireccional", "MQTT 3.1.1 sobre TCP 1883", "Telemetría, eventos, estado, órdenes", "Ver la Tabla 8"],
    ["Mosquitto → n8n", "Broker → servicio", "MQTT, suscripción a invernadero/#", "Todos los mensajes de los nodos", "Al llegar cada mensaje"],
    ["n8n → MySQL", "Servicio → BD", "SQL sobre TCP 3306 (red interna de Docker)", "Lecturas, eventos, alertas", "Por mensaje"],
    ["n8n → WhatsApp y Telegram", "Servicio → externo", "HTTPS (CallMeBot y API de bots)", "Un aviso por episodio", "Al abrir y cerrar una alerta"],
    ["Dashboard ↔ Mosquitto", "Bidireccional", "MQTT sobre WebSocket", "Valores en vivo y alertas", "Permanente mientras está abierto"],
    ["Dashboard → n8n (Web API)", "Cliente → servicio", "HTTP GET; nginx reenvía /api/ a n8n", "Estado, historial y alertas en JSON", "Al abrir la página y al pedir historial"],
], anchos=[1.45, 1.05, 1.45, 1.4, 1.15], tam=9)
if not BREVE:
    D.p("La Web API de consulta es de solo lectura y no la usan los nodos: sirve al dashboard. Son tres webhooks de n8n (`/api/estado`, `/api/mediciones` y `/api/alertas`) que consultan MySQL con un usuario de solo lectura y exigen una clave en la cabecera `X-API-Key`. Está diseñada, pero todavía no se construye ni se prueba.")
D.h2("4.1 Alcance, restricciones y recuperación")
D.p("El ESP8266 solo trabaja en 2.4 GHz, así que la red del invernadero debe ofrecer esa banda. Falta confirmar con los encargados el tipo de autenticación, si hay que registrar las direcciones MAC y si está abierto el puerto 1883 de salida [POR CONFIRMAR]; si la red usa WPA2 empresarial, el ESP8266 tendría problemas para conectarse y se pediría una red aparte. Cada nodo reporta su intensidad de señal (RSSI) al conectarse, lo que permite revisar la cobertura en el sitio.")
D.tabla("Detección de fallas y recuperación de la comunicación", [
    ["Falla", "Cómo se detecta", "Qué hace Argos"],
    ["Se cae el WiFi", "WiFi.status() distinto de conectado", "Reconexión automática del ESP8266; LED verde con parpadeo lento; el dht sigue midiendo y su alarma local sigue activa"],
    ["Se cae el broker", "mqtt.connected() en falso", "Reintento de conexión cada 5 s"],
    ["El nodo se apaga o se cuelga", "El broker no recibe nada en 1.5 veces el keep-alive de 45 s", "Mosquitto publica el LWT {\"estado\":\"offline\"} retenido; n8n lo registra y avisa"],
    ["El nodo reinicia", "Mensaje de estado online retenido con reset_reason y uptime_s", "n8n registra la causa del reinicio"],
    ["Nodo vivo pero sin eventos", "Latido cada 60 s en pir, puerta y acel", "n8n distingue un nodo en silencio de uno caído"],
    ["Se pierde la orden de alarma", "La orden on vence a los 150 s si no se repite", "n8n la repite cada 60 s; si n8n cae, el dht vuelve a su alarma local"],
], anchos=[1.5, 2.2, 2.8], tam=9.5)
D.h2("4.2 Diseño MQTT")
D.p("El broker es Mosquitto 2.0.22 (Light, 2017) en un contenedor de Docker, primero en una laptop y después en una máquina gratuita de Oracle Cloud. Cada nodo usa su id como usuario MQTT, con contraseña propia y una lista de control de acceso que solo le permite publicar en sus tópicos; el client id es nodo-<id> y el keep-alive de 45 s. Las contraseñas viven en un archivo .env que no se sube al repositorio. La jerarquía de tópicos empieza en invernadero, sigue con el tipo de mensaje y termina con el id del nodo, todo en ASCII y minúsculas.")
D.tabla("Tópicos, publicadores y suscriptores", [
    ["Tópico", "Publica", "Se suscribe", "QoS / retenido", "Condición de publicación"],
    ["invernadero/telemetria/{nodo}", "dht, luz; latido de pir, puerta y acel", "n8n", "0 / no", "dht cada 30 s; luz cada 60 s; latido cada 60 s"],
    ["invernadero/evento/{nodo}", "pir, puerta, acel, dht", "n8n", "0 / no", "Movimiento, golpe, cambio de puerta o sensor_error"],
    ["invernadero/estado/{nodo}", "Cada nodo; el broker publica el LWT", "n8n, dashboard", "1 / sí", "Al conectar (online) o al perder al nodo (offline)"],
    ["invernadero/cmd/alarma", "n8n", "dht", "0 / no", "on cada 60 s mientras haya alerta de T o HR; off al cerrarla"],
    ["invernadero/cmd/silenciar", "dht", "n8n", "0 / no", "Pulsación larga del botón"],
    ["invernadero/alertas", "n8n", "dashboard", "0 / no", "Al abrir o cerrar una alerta"],
], anchos=[1.75, 1.35, 0.85, 0.75, 1.8], primera_negrita=False, tam=9)
D.tabla("Ejemplos de mensajes", [
    ["Tipo", "Tópico", "Payload"],
    ["Medición", "invernadero/telemetria/dht", "{\"lecturas\":[{\"parametro\":\"temperatura\",\"valor\":25.4,\"unidad\":\"C\"},{\"parametro\":\"humedad\",\"valor\":51.0,\"unidad\":\"%\"}]}"],
    ["Medición", "invernadero/telemetria/luz", "{\"lecturas\":[{\"parametro\":\"luz\",\"valor\":712,\"unidad\":\"adc\"}]}"],
    ["Latido", "invernadero/telemetria/pir", "{\"lecturas\":[{\"parametro\":\"latido\",\"valor\":1,\"unidad\":\"\"}]}"],
    ["Evento", "invernadero/evento/acel", "{\"tipo\":\"golpe\",\"magnitud\":1.8}"],
    ["Evento", "invernadero/evento/puerta", "{\"tipo\":\"puerta_abierta\"}"],
    ["Estado", "invernadero/estado/dht", "{\"estado\":\"online\",\"reset_reason\":\"Power on\",\"uptime_s\":12,\"rssi\":-62}"],
    ["Estado (LWT)", "invernadero/estado/luz", "{\"estado\":\"offline\"}"],
    ["Comando", "invernadero/cmd/alarma", "on"],
    ["Comando", "invernadero/cmd/silenciar", "{\"minutos\":30}"],
], anchos=[0.95, 1.9, 3.65], tam=8.5,
   nota="Los nodos no tienen reloj: la hora la pone MySQL al guardar cada mensaje, en UTC.")

# ------------------------------------------------------------------ 5
D.h1("5. Lógica de control y actuación")
D.p("Cada nodo decide por su cuenta cuándo encender su LED rojo, a partir de su propio sensor. El buzzer del `dht` tiene dos orígenes: la regla local del nodo, que funciona aunque no haya red, y la orden cmd/alarma que manda n8n. Suena si se cumple cualquiera de las dos y no está silenciado. Solo la temperatura y la humedad activan el buzzer; los demás nodos avisan con su LED y con mensajes al celular.")
D.tabla("Condiciones de actuación", [
    ["Variable o evento", "Umbral de activación", "Actuador y nodo", "Origen", "Desactivación", "Ante falla"],
    ["Temperatura", "3 lecturas seguidas fuera de 22 a 28 °C", "Buzzer y LED rojo del dht", "Local y comando de n8n", "3 lecturas dentro de 22.5 a 27.5 °C; off de n8n; botón silencia 30 min", "Sin red: suena por la regla local. Sensor inválido 3 veces: LED rojo con parpadeo rápido y sensor_error"],
    ["Humedad relativa", "3 lecturas seguidas fuera de 40 a 60 %", "Buzzer y LED rojo del dht", "Local y comando de n8n", "3 lecturas dentro de 42 a 58 %; igual que arriba", "Igual que temperatura"],
    ["Luz", "Promedio por debajo de UMBRAL_ADC (lámparas apagadas)", "LED rojo del luz", "Local", "Promedio por encima del umbral", "Sin red: el LED sigue funcionando; n8n detecta la falta de datos por el LWT"],
    ["Movimiento", "Flanco de subida del PIR", "LED rojo del pir", "Local", "5 s después de la última detección", "Igual; el evento se pierde si no hay red"],
    ["Puerta", "Reed abierto (imán lejos)", "LED rojo de puerta", "Local", "Al cerrar la puerta", "Igual"],
    ["Golpe", "Desviación de |a| mayor que 0.5 g", "LED rojo del acel", "Local", "5 s después del golpe", "ADS1115 no responde: LED rojo con parpadeo rápido"],
], anchos=[0.9, 1.25, 0.95, 0.8, 1.35, 1.25], tam=8.5,
   nota="Las alertas por mensaje (luz fuera de horario, acceso fuera de horario, puerta abierta más de 2 min [POR CONFIRMAR], golpe) las decide n8n con los mismos eventos; no mueven actuadores.")
D.figura("cap/como_funciona_alarma_fig.png", "Estados de la alarma del nodo dht", ancho=6.4)
D.p(f"La alarma es el único mecanismo que depende de un flujo distribuido. El `dht` publica su lectura, n8n la recibe, aplica la misma regla de persistencia e histéresis, abre la alerta, avisa por WhatsApp y Telegram y publica cmd/alarma = on cada 60 s. El nodo da por vencida la orden si pasan 150 s sin repetirse, de modo que una caída de n8n no deja el buzzer sonando para siempre. El botón publica cmd/silenciar para que n8n registre quién silenció y cuándo (Figura {FIG_SECUENCIA}).")
D.figura("cap/como_funciona_aviso_calor_fig.png", "Secuencia de mensajes de un aviso por calor", ancho=5.6,
         nota="28.6 °C es una lectura de ejemplo para ilustrar el caso.")
D.h2("5.1 Sensores, actuadores y compras")
D.p("El DHT22 usa un sensor capacitivo de humedad y un termistor, con salida digital calibrada de un hilo, resolución de 0.1 y exactitud de ±0.5 °C y ±2 %HR (Aosong Electronics, s. f.). El ADS1115 es un convertidor de 16 bits con amplificador de ganancia programable y hasta 860 muestras/s (Texas Instruments, 2024); se usa porque el NodeMCU tiene una sola entrada analógica. El MC-38 es un interruptor de lengüeta con imán, sin alimentación. El HC-SR501 detecta cambios de radiación infrarroja y entrega un pulso digital de 3.3 V. La Tabla 11 lista lo que hay que comprar; lo demás sale de los kits del curso.")
D.tabla("Componentes a comprar: proveedor, enlace, costo y entrega", [
    ["Componente (clave del proveedor)", "Proveedor", "Enlace del proveedor", "Cant. × costo (MXN)", "Entrega a Monterrey"],
    ["DHT22 (AM2302) con cables (AR0600)", "UNIT Electronics", "uelectronics.com/producto/sensor-de-temperatura-y-humedad-dht22-con-cables/", "1 × $120", "3 a 8 días hábiles"],
    ["Reed switch MC-38 con imán (AR1246)", "UNIT Electronics", "uelectronics.com/producto/sensor-magnetico-mc-38/", "1 × $25", "3 a 8 días hábiles"],
    ["ADS1115, ADC de 16 bits I²C (AR0318)", "UNIT Electronics", "uelectronics.com/producto/ads1115-adc-amplificador-de-ganancia-programable/", "1 × $51", "3 a 8 días hábiles"],
    ["Buzzer activo de 5 V", "UNIT Electronics", "uelectronics.com/producto/buzzer-activo-3v-5v-12v-zumbador/", "1 × $9", "3 a 8 días hábiles"],
    ["Transistor 2N2222 TO-92 (AR0192)", "UNIT Electronics", "uelectronics.com/producto/2n2222-transistor-bjt-npn-40v-to-92/", "1 × $1", "3 a 8 días hábiles"],
    ["Resistencias 1 kΩ y 10 kΩ, 1/4 W", "UNIT Electronics", "uelectronics.com/producto/resistencia-de-1-ohm-1m-ohms-1-4w/", "(3 + 4) × $0.50", "3 a 8 días hábiles"],
    ["Capacitor electrolítico 220 µF / 16 V", "UNIT Electronics", "uelectronics.com/producto/capacitor-electrolitico-16v/", "5 × $1", "3 a 8 días hábiles"],
    ["OLED 2.4\" 128×64 SSD1309 I²C (azul)", "UNIT Electronics", "uelectronics.com/producto/display-oled-i2c-2-4%e2%80%b3-128x64-blanco-azul-amarillo/", "1 × $249", "3 a 8 días hábiles"],
    ["Protoboard de 400 puntos (caja dht)", "UNIT Electronics", "uelectronics.com/producto/protoboard-de-400pts-y-830pts-blanco-o-transparente/", "1 × $18", "3 a 8 días hábiles"],
    ["Eliminador 5 V 3 A con USB-C (uno por caja)", "UNIT Electronics", "uelectronics.com/producto/fuente-de-alimentacion-5v-3a-usb-c/", "3 × $71", "3 a 8 días hábiles"],
    ["Adaptador USB-C hembra a DIP de 4 pines", "UNIT Electronics", "uelectronics.com/producto/adaptador-usb-tipo-c-hembra-a-dip-pcb-4-pines/", "3 × $8", "3 a 8 días hábiles"],
    ["Insertos de latón M3", "UNIT Electronics", "uelectronics.com/producto/rosca-de-laton-m2-m3-m4/", "12 × $3", "3 a 8 días hábiles"],
    ["Envío del pedido de UNIT", "UNIT Electronics", "uelectronics.com/metodos-de-envio/", "$89", "Junto con el pedido"],
    ["Kit de tornillos M3 Allen con tuercas, 280 piezas (B0742DDLQ1)", "Amazon México", "amazon.com.mx/dp/B0742DDLQ1", "1 × $206", "1 a 3 días"],
    ["Sílica gel, 100 sobres de 5 g (B08FBJQQFP)", "Amazon México", "amazon.com.mx/dp/B08FBJQQFP", "1 × $99", "1 a 3 días"],
    ["PETG blanco 1 kg, 1.75 mm, SUNLU (B0FKMRYC62)", "Amazon México", "amazon.com.mx/dp/B0FKMRYC62", "1 × $249.99", "1 a 3 días"],
], anchos=[1.55, 0.85, 1.95, 0.85, 1.3], tam=8,
   nota='Precios con IVA leídos el 22 de octubre de 2026 en la página de cada tienda, no en un carrito. Total ≈ $1,398.49 MXN con envíos, $101.51 debajo del tope de $1,500; si el PETG ya está comprado, baja a ≈ $1,148.50. Son dos pedidos con envío a Monterrey: UNIT Electronics (1 a 3 días hábiles de preparación más 2 a 5 de envío; UNIT Electronics, s. f.) y Amazon México (gratis, 1 a 3 días según el código postal). El buzzer de 5 V reemplaza al módulo KY-012, agotado, con el mismo circuito, y la OLED es azul porque la blanca está agotada. Lo demás (NodeMCU, fotorresistencia, HC-SR501, GY-61, LED, resistencias de 330 Ω, botón y MB-102) sale del kit del curso. La lista completa, con tiendas alternativas, está en docs/solicitud_compra.xlsx.')

# ------------------------------------------------------------------ 6
D.h1("6. Alimentación y presupuesto energético")
D.p("Todos los nodos van conectados a la corriente del cuarto y ninguno usa batería. El monitoreo es continuo: el `dht` debe poder sonar en cualquier momento y escuchar la orden de alarma, y los nodos de eventos deben estar despiertos para no perder un movimiento o una apertura. Un ESP8266 en deep-sleep consume 20 µA (Espressif Systems, s. f.), pero en ese modo no escucha MQTT y el broker lo daría por caído al vencer el keep-alive. Esta sección calcula el consumo para dimensionar las fuentes" + ("." if BREVE else " y para mostrar, con la fórmula del curso, qué autonomía tendría una versión con batería."))
D.h2("6.1 Modelo de consumo por ciclo")
D.p("Se usa Iprom = Σ (Ii × ti) / T. Para el ESP8266 se toman tres estados: base con la CPU activa y el radio en modem-sleep (15 mA), escucha del radio para los beacons del punto de acceso y el keep-alive de MQTT (56 mA, 10 % del tiempo) y transmisión de un mensaje (170 mA durante 50 ms). Las corrientes vienen de la hoja de datos (Espressif Systems, s. f.); el 10 % de escucha y los 50 ms por mensaje son supuestos del equipo que se comprueban en P-05. Con T = 30 s en el `dht`:")
D.p("Iprom(ESP8266) = 15 mA + (56 − 15) mA × 0.10 + (170 − 15) mA × 0.05 s / 30 s ≈ 15 + 4.1 + 0.26 ≈ 19.4 mA", sangria=False)
D.p("En los nodos que publican cada 60 s el último término baja a 0.13 mA y el resultado queda en ≈ 19.2 mA. A eso se suman los sensores y los actuadores con su tiempo de uso. El regulador del NodeMCU es lineal, así que la corriente que entra por VIN a 5 V es prácticamente la misma que sale a 3.3 V; a falta de medir el consumo propio de la placa, se toma ese valor.")
D.tabla("Presupuesto de corriente por nodo", [
    ["Nodo", "Componentes y tiempo de uso", "Iprom normal", "Caso con alerta", "Caso pesimista"],
    ["dht", "ESP8266 19.4 mA; LED verde 3.6 mA siempre; DHT22 0.05 mA; OLED 20 mA solo 30 s tras el botón (≈ 0 en promedio)", "≈ 23 mA (≈ 43 mA con la OLED encendida)", "+ LED rojo 4.5 mA, base 2.5 mA y buzzer 30 mA: ≈ 80 mA con la OLED", "≈ 141 mA (ESP8266 a 80 mA continuos y todo encendido)"],
    ["luz", "ESP8266 19.2 mA; LED verde 3.6 mA; divisor ≤ 0.33 mA; LED rojo 4.5 mA la mitad del día [horario POR CONFIRMAR]", "≈ 25 mA", "Igual: el LED rojo ya está incluido", "≈ 88 mA"],
    ["pir", "ESP8266 19.2 mA; LED verde 3.6 mA; HC-SR501 0.065 mA; LED rojo 5 s por evento", "≈ 23 mA", "+ 4.5 mA durante 5 s", "≈ 88 mA"],
    ["puerta", "ESP8266 19.2 mA; LED verde 3.6 mA; pull-up < 0.1 mA; LED rojo con la puerta abierta", "≈ 23 mA", "+ 4.5 mA mientras está abierta", "≈ 88 mA"],
    ["acel", "ESP8266 19.2 mA; LED verde 3.6 mA; ADS1115 0.15 mA; GY-61 < 0.5 mA", "≈ 24 mA", "+ 4.5 mA durante 5 s", "≈ 89 mA"],
], anchos=[0.6, 2.5, 1.1, 1.2, 1.1], tam=8.5,
   nota="El caso pesimista usa el promedio de 80 mA que da la hoja de datos del ESP8266 en lugar del modelo por ciclo. La guía de ensamble espera medir ≈ 55 a 60 mA en el dht con la OLED y ≈ 40 mA en los demás; la prueba P-05 dirá qué modelo se acerca más.")
D.h2("6.2 Fuentes de alimentación")
D.p("Al transmitir, el ESP8266 sube a 170 mA (Espressif Systems, s. f.), y el equipo diseña con 300 a 400 mA por placa para cubrir el arranque del radio, valor que se medirá. Con eso se dimensiona cada fuente (Tabla 13). Las tres son eliminadores comerciales de 5 V. Ninguna parte del circuito necesita otro voltaje, porque el regulador de cada NodeMCU da los 3.3 V y los dos componentes de 5 V (PIR y buzzer) toman VIN.")
D.tabla("Dimensionamiento de las fuentes por caja", [
    ["Caja", "Promedio (modelo)", "Promedio pesimista", "Pico estimado", "Fuente", "Margen sobre el pico"],
    ["dht", "≈ 43 mA", "≈ 141 mA", "≈ 0.46 A (400 + 20 + 9 + 2.5 + 30 mA)", "5 V, ≥ 1 A (eliminador USB-C de 3 A a VIN [POR CONFIRMAR])", "≈ 2.2 veces"],
    ["Estación de entrada (pir + puerta)", "≈ 46 mA", "≈ 176 mA", "≈ 0.82 A (2 × 409 mA)", "5 V, ≥ 2 A, entrada USB-C a los rieles", "≈ 2.4 veces"],
    ["Estación del anaquel (acel + luz)", "≈ 49 mA", "≈ 177 mA", "≈ 0.82 A", "5 V, ≥ 2 A, entrada USB-C a los rieles", "≈ 2.4 veces"],
], anchos=[1.35, 0.85, 0.9, 1.45, 1.2, 0.75], tam=9,
   nota="Energía diaria de Argos a 5 V: ≈ 17 Wh con el modelo por ciclo y ≈ 59 Wh en el caso pesimista.")
if not BREVE:
    D.h2("6.3 Autonomía si se usara batería")
    D.p("Como referencia, se calcula la autonomía del `dht` con un banco de baterías de 10,000 mAh a 3.7 V. Si se aprovecha el 80 % de la capacidad y la conversión a 5 V tiene 85 % de eficiencia, la capacidad útil a 5 V es 10,000 × 3.7 / 5 × 0.80 × 0.85 ≈ 5,030 mAh. Con 43 mA la autonomía sería 5,030 / 43 ≈ 117 h, unos cinco días; en el caso pesimista, 5,030 / 141 ≈ 36 h. Habría que cambiar baterías cada pocos días en un cuarto que tiene contactos, así que la alimentación por red es la opción viable. Una versión con batería solo tendría sentido en `puerta` o `pir`, despertando por interrupción, y a cambio de perder el estado en línea y la reacción inmediata del LED.")
D.h2(("6.3" if BREVE else "6.4") + " Medidas para reducir el consumo")
D.viñetas([
    "La OLED se apaga sola a los 30 s y solo se enciende con el botón, lo que quita hasta 20 mA del promedio del `dht`.",
    "El radio queda en modem-sleep entre transmisiones; el firmware no lo fuerza a estar siempre activo.",
    "El nodo `luz` manda un promedio por minuto en lugar de cada muestra, y los nodos de eventos solo transmiten cambios, con antirrebote.",
    "Mensajes JSON cortos, QoS 0 para datos y un keep-alive de 45 s, que es el mínimo necesario para detectar un nodo caído en poco más de un minuto.",
    "LED con 330 Ω (menos de 4.5 mA cada uno) y buzzer conmutado por transistor, apagado salvo en alerta.",
])
if not BREVE:
    D.h2("6.5 Consumo mensual y costo de operación en Monterrey")
    D.p("Para pasar de la energía a 5 V a la que se toma del contacto, se supone que los eliminadores tienen 80 % de eficiencia, incluido su consumo sin carga; el valor se revisará con un medidor de enchufe. Con eso, los cinco nodos consumen ≈ 21 Wh al día con el modelo por ciclo y ≈ 74 Wh en el caso pesimista. El precio se toma de la tarifa doméstica 1C de CFE, la que corresponde a Monterrey, vigente en octubre y diciembre de 2026: de $1.019 a $4.054 por kWh en verano y de $1.148 a $4.08 fuera de verano, según el bloque de consumo, más 16 % de IVA (Comisión Federal de Electricidad [CFE], 2026). El cuarto lo paga el Tec con su propio contrato, cuya tarifa no se conoce [POR CONFIRMAR]; la 1C se usa como referencia pública, y el rango de la Tabla 14 va del bloque básico al excedente.")
    D.tabla("Consumo mensual estimado y costo de la energía", [
        ["Concepto", "Potencia media", "Energía al mes (30 días)", "Costo al mes con IVA"],
        ["Cinco nodos, modelo por ciclo", "≈ 0.86 W", "≈ 0.62 kWh", "≈ $0.73 a $2.94"],
        ["Cinco nodos, caso pesimista", "≈ 3.1 W", "≈ 2.2 kWh", "≈ $2.62 a $10.51"],
        ["Laptop como servidor de pruebas (Docker encendido todo el día)", "≈ 15 a 30 W [POR CONFIRMAR, medir]", "≈ 10.8 a 21.6 kWh", "≈ $12.80 a $102.20"],
        ["Servidor final en Oracle Cloud Always Free", "Sin consumo en el cuarto", "0 kWh", "$0"],
    ], anchos=[2.3, 1.4, 1.3, 1.5], tam=9.5,
       nota="Costo = energía × precio por kWh × 1.16, con $1.019 (básico de verano) como mínimo y $4.08 (excedente fuera de verano) como máximo. En un año, los nodos consumen ≈ 7.5 kWh con el modelo y ≈ 27 kWh en el caso pesimista, es decir, de ≈ $9 a ≈ $126.")
    D.p("Los nodos de Argos cuestan menos de $11 al mes de luz aun en el caso pesimista. Lo que más gasta es la laptop encendida como servidor de pruebas, y ese gasto termina al pasar el servidor a Oracle Cloud Always Free. Los demás servicios (Mosquitto, n8n, MySQL, CallMeBot y Telegram) no cobran, y la red es la del invernadero. Lo único que se repone con el tiempo es la sílica gel de las cajas, que ya viene incluida en la compra (100 sobres).")

# ------------------------------------------------------------------ 7
D.h1("7. Estrategia de integración y validación")
D.p("Las pruebas van de lo eléctrico a lo distribuido: primero que cada nodo esté bien cableado y alimentado, luego que lea su sensor y mueva su actuador, y al final que hable con el broker y con n8n. El firmware todavía no se ha cargado en ningún NodeMCU, así que las evidencias disponibles hoy son de software y de simulación. Las pruebas en hardware tienen fecha en la sección 8.")
D.h2("7.1 Evidencias disponibles")
D.tabla("Pruebas ya realizadas (21 de octubre de 2026)", [
    ["Prueba", "Condición inicial", "Procedimiento", "Respuesta esperada", "Resultado observado", "Conclusión"],
    ["V-01 Compilación del firmware", "Código de los 5 nodos en firmware/src", "pio run para dht, dht_sin_oled, luz, pir, puerta y acel (sin cargar)", "Los 6 entornos compilan", "6 de 6 SUCCESS; RAM 35 a 38 % y flash 27 a 29 %", "El firmware cabe con holgura en el ESP8266"],
    ["V-02 Pines del firmware contra el armado", "layouts.py y firmware/src", "python hardware/chequeo_pines.py", "Mismos pines en código y protoboard", "OK en los 6 entornos", "No hay pines cruzados"],
    ["V-03 Redes de la protoboard", "Distribución de 8 armados", "protoboard.py revisa orificios, cruces y redes", "Ninguna red distinta a la esperada", "OK en los 8 armados", "Los diagramas de armado son consistentes"],
    ["V-04 Reglas del buzzer en PC", "alarma_dht.h compilado en la PC", "21 casos: persistencia, histéresis, silencio, orden de n8n, vencimiento a 150 s, sensor_error", "Cada caso con la salida esperada", "21 de 21 OK", "La lógica de actuación del dht se comporta como se especificó"],
    ["V-05 Publicar y suscribir MQTT", "Broker local de prueba (amqtt) en la PC; simulador de los 5 nodos", "Escenario calor en modo rápido; un cliente suscrito a invernadero/# y otro publica cmd/alarma = on", "Llegan estado, telemetría y eventos de los 5 nodos; el dht recibe la orden", "88 mensajes; la temperatura sube de 25.0 a 29.9 °C; el dht simulado recibe on", "El contrato de tópicos funciona de punta a punta"],
    ["V-06 Caída de un nodo (LWT)", "Mismo broker; escenario sin_red", "El nodo luz simulado cierra su conexión sin despedirse", "El broker publica estado offline retenido", "offline publicado a las 14:31:07, justo tras el corte", "El LWT funciona; falta probar el vencimiento por keep-alive"],
], anchos=[1.0, 0.95, 1.25, 1.05, 1.2, 1.05], tam=8,
   nota="V-05 y V-06 usan valores inventados por el simulador y un broker de prueba (amqtt), no Mosquitto ni hardware real.")
D.tabla("Extracto del registro de la prueba V-05", [
    ["Hora", "Tópico", "Payload"],
    ["14:29:30", "invernadero/estado/dht", "{\"estado\": \"online\", \"reset_reason\": \"Power on\", \"uptime_s\": 0, \"rssi\": -63}"],
    ["14:29:30", "invernadero/telemetria/dht", "{\"lecturas\": [{\"parametro\": \"temperatura\", \"valor\": 25.0, \"unidad\": \"C\"}, {\"parametro\": \"humedad\", \"valor\": 49.8, \"unidad\": \"%\"}]}"],
    ["14:29:30", "invernadero/telemetria/luz", "{\"lecturas\": [{\"parametro\": \"luz\", \"valor\": 737.7, \"unidad\": \"adc\"}]}"],
    ["14:29:49", "invernadero/evento/puerta", "{\"tipo\": \"puerta_abierta\"}"],
    ["14:29:49", "invernadero/cmd/alarma", "on (recibido por el dht simulado)"],
    ["14:30:27", "invernadero/telemetria/dht", "{\"lecturas\": [{\"parametro\": \"temperatura\", \"valor\": 29.9, \"unidad\": \"C\"}, {\"parametro\": \"humedad\", \"valor\": 51.1, \"unidad\": \"%\"}]}"],
], anchos=[0.7, 1.8, 4.0], primera_negrita=False, tam=8.5)
D.p("Las pruebas dejaron dos hallazgos. El simulador imprime \"conectado\" aunque el broker rechace las credenciales, así que se va a corregir para que revise el código de respuesta. Con el broker de prueba, los nodos simulados recibieron mensajes de estado a los que no estaban suscritos; se repetirá con Mosquitto 2.0.22 para saber si es un efecto de amqtt.")
D.h2("7.2 Plan de pruebas en hardware")
D.tabla("Pruebas pendientes en hardware", [
    ["Prueba", "Condición inicial", "Procedimiento", "Respuesta esperada", "Resp."],
    ["P-01 Continuidad", "Nodo armado, sin energía", "Multímetro: 5V y 3V3 contra GND, LED, divisor, transistor", "Sin cortos; valores de la guía de ensamble", "Cada integrante"],
    ["P-02 Voltajes", "Nodo con su fuente, sin flashear", "Medir 3V3, VIN y cada pin que entra a un GPIO", "3V3 entre 3.14 y 3.47 V; VIN ≈ 4.6 a 5.1 V; ningún GPIO arriba de 3.3 V", "Cada integrante"],
    ["P-03 Lectura de sensor real", "Firmware cargado con aprobación del equipo", "DHT22 junto al termohigrómetro prestado durante 30 min", "Diferencia ≤ 0.5 °C y ≤ 2 %HR", "José María"],
    ["P-04 Actuadores", "dht con firmware", "Forzar 3 lecturas fuera de rango (calor de la mano o de una secadora a distancia); pulsar el botón", "Buzzer y LED rojo encienden; el botón silencia el buzzer y el LED sigue", "José María"],
    ["P-05 Consumo", "Fuente de 5 V y multímetro en serie con VIN", "Medir en reposo, al transmitir y con la alarma; repetir en una estación con 2 placas", "dht ≈ 43 a 60 mA con la OLED; otros ≈ 23 a 40 mA", "Mía y José María"],
    ["P-06 MQTT con nodo real", "Mosquitto, n8n y MySQL en la laptop", "Conectar un nodo real y suscribirse a invernadero/#", "Telemetría, latido y estado retenido llegan con su usuario", "Luis"],
    ["P-07 Orden de alarma", "P-06 lista", "Publicar cmd/alarma = on cada 60 s y luego dejar de mandarla", "Suena con la orden; se apaga sola a los 150 s", "Luis y José María"],
    ["P-08 Pérdida de red", "P-06 lista", "Desconectar la fuente de un nodo; apagar el punto de acceso", "offline retenido en ≈ 68 s; reconexión sola al volver la red", "Luis"],
    ["P-09 Calibración en sitio", "Nodos luz, puerta y acel armados", "Prueba de la fotorresistencia con la lámpara; distancia de cierre del MC-38; golpes de prueba en la repisa", "UMBRAL_ADC, holgura del reed y umbral de golpe definidos", "Arianna, Iván y Mía"],
], anchos=[1.15, 1.15, 1.75, 1.55, 0.9], tam=8.5,
   nota="Cada prueba registrará condición inicial, procedimiento, respuesta esperada, resultado observado y conclusión, con foto o captura como evidencia.")

# ------------------------------------------------------------------ 8
D.h1("8. Planeación del siguiente avance")
D.p("El siguiente avance se entrega en tres semanas. La semana 1 va del 22 al 28 de octubre, la 2 del 29 de octubre al 4 de noviembre y la 3 del 5 al 11 de noviembre de 2026. Las piezas compradas se esperan para la semana 3, así que las dos primeras semanas se dedican sobre todo al software del servidor y a lo que se puede armar con el kit del curso; la semana 3 se reserva para medir todas las piezas, imprimir las cajas y terminar el armado.")
D.tabla("Actividades del equipo por semana", [
    ["Semana", "Actividades", "Hito verificable"],
    ["1 (22 al 28 de octubre)", "Hacer el pedido de la Tabla 11; levantar Mosquitto 2.0.22, MySQL, n8n y nginx con Docker Compose en la laptop; flujo de n8n que guarda la telemetría en MySQL; reglas de alerta con persistencia e histéresis y la orden cmd/alarma; avisos por WhatsApp y Telegram; primera versión del dashboard; probar todo con el simulador de los cinco nodos; enviar las preguntas a profesores y encargados", "Pedido confirmado; el simulador llena MySQL y una alerta de prueba llega por WhatsApp y Telegram"],
    ["2 (29 de octubre al 4 de noviembre)", "Web API con webhooks de n8n (estado, mediciones y alertas) con clave y usuario de solo lectura; dashboard con historial por la API y tiempo real por MQTT; registro de eventos y de alertas en MySQL; con el kit del curso, armar en protoboard lo que ya se puede (NodeMCU, LED, fotorresistencia, HC-SR501 y GY-61) y hacer P-01, P-02 y P-06", "Las tres consultas responden con datos del simulador; los nodos luz y pir publican lecturas reales al servidor"],
    ["3 (5 al 11 de noviembre)", "Recibir y revisar el pedido; medir todas las piezas con calibrador y actualizar medidas.json; imprimir el peine de holguras y las tres cajas en PETG; completar los nodos dht, puerta y acel; P-03, P-04, P-05, P-07, P-08 y P-09; medir el consumo; montar las cajas y probar los cinco nodos juntos", "Cinco nodos reales en sus cajas publicando al servidor; consumo medido; evidencias de las nueve pruebas"],
], anchos=[1.1, 3.4, 2.0], tam=9.5)
D.tabla("Riesgos y decisiones por resolver", [
    ["Riesgo o decisión", "Impacto", "Acción"],
    ["Autenticación del WiFi del invernadero y puerto 1883 [POR CONFIRMAR]", "Si es WPA2 empresarial, el ESP8266 no se conecta con facilidad", "Preguntar a los encargados en la semana 1; plan B: un punto de acceso propio"],
    ["Medidas reales de las piezas", "Las cajas pueden no cerrar", "Medir antes de imprimir; imprimir primero el peine de holguras"],
    ["VIN ≈ 4.7 V, cerca del mínimo de 4.5 V del HC-SR501", "El PIR podría fallar", "Medir en P-02; si falla, alimentarlo desde el riel de 5 V antes del diodo"],
    ["Horario de las lámparas y de acceso [POR CONFIRMAR]", "Sin ellos no se pueden calibrar las alertas de luz y de acceso", "Preguntar a los encargados"],
    ["Presupuesto de ≈ $1,398.49 con envíos (Tabla 11)", "Queda solo $101.51 debajo del tope de $1,500. El total es variable: precios, envío y existencias cambian de un día a otro", "Revisar cada precio en el carrito antes de pagar y comprar pronto; plan B: tiendas alternativas de docs/solicitud_compra.xlsx o la variante dht_sin_oled"],
    ["Entrega del pedido (3 a 8 días hábiles en UNIT)", "Si llega después del 5 de noviembre, se recorren las mediciones, la impresión de las cajas y el armado final", "Pedir a más tardar el 24 de octubre; mientras tanto avanzar con el software y con las piezas del kit del curso"],
    ["Web API obligatoria hecha con webhooks de n8n", "Si el profesor exige una API propia, hay que agregar un servicio", "Confirmar con el profesor; plan B: servicio pequeño en el mismo Docker Compose con las mismas tres consultas"],
    ["Autorización de la pantalla y del buzzer en el cuarto", "Cambia el diseño del dht", "Preguntar a los encargados"],
], anchos=[2.2, 2.0, 2.3], tam=9.5)

# ------------------------------------------------------------------ 9
D.h1("9. Participación individual")
D.p("Cada integrante es responsable de su nodo, de su sensor y de su LED rojo, y comparte con su compañero de estación la caja y la fuente. Las secciones siguientes las redacta y firma cada integrante.")

def integrante(nombre, part, resp, s1, s2, s3, evid, riesgos):
    D.h2(nombre)
    for k, v in [("Participación en el Avance 2", part), ("Responsabilidad principal para el siguiente avance", resp),
                 ("Actividades de la semana 1 (22 al 28 de octubre)", s1), ("Actividades de la semana 2 (29 de octubre al 4 de noviembre)", s2),
                 ("Actividades de la semana 3 (5 al 11 de noviembre)", s3), ("Resultados y evidencias comprometidas", evid),
                 ("Dependencias y riesgos identificados", riesgos)]:
        D.regla(k + ":", v)

integrante("Luis Eduardo Mendoza Menéndez (A01669847)",
    "Como líder del proyecto definí la arquitectura de cinco nodos en tres cajas y el contrato MQTT de tópicos y payloads. Diseñé las cajas en build123d, las distribuciones de protoboard y los esquemáticos de los cinco nodos, y escribí el firmware de referencia junto con sus chequeos automáticos (V-01 a V-04). También armé la solicitud de compra con envío a Monterrey, que deja el hardware extra en ≈ $1,398.49, corrí la prueba MQTT con el simulador (V-05 y V-06) y preparé la lista de preguntas para profesores y encargados.",
    "Nodo pir (HC-SR501 y su LED rojo), la estación de entrada junto con Iván Acosta y el servidor de pruebas (Mosquitto, n8n y MySQL en Docker).",
    "Hacer el pedido; levantar Mosquitto 2.0.22, MySQL con docs/bd/esquema.sql, n8n y nginx con Docker Compose en la laptop; flujo de n8n que guarda la telemetría en MySQL; repetir V-05 contra Mosquitto con el simulador; enviar las preguntas.",
    "Webhooks de la Web API (GET /api/estado, /api/mediciones y /api/alertas) con clave y usuario de solo lectura; corregir el simulador para que revise el código de respuesta del broker; armar el nodo pir con el HC-SR501 y el NodeMCU del kit; P-01 y P-02; cargar el firmware con aprobación del equipo; P-06 con el pir real.",
    "Revisar el pedido; medir con calibrador el HC-SR501, el NodeMCU y la MB-102; imprimir y montar la estación de entrada con Iván; P-07 con José María y P-08 (pérdida de red y LWT por keep-alive); integrar los cinco nodos reales con el servidor.",
    "Registro de P-01, P-02, P-06, P-07 y P-08 con capturas del broker; tabla de mensajes en MySQL; respuestas de las tres consultas de la Web API; flujos de n8n exportados; foto de la estación de entrada armada.",
    "Necesito la red del invernadero o un punto de acceso de 2.4 GHz, la laptop con Docker y el reed de Iván para la estación. Riesgo: VIN ≈ 4.7 V queda cerca del mínimo del HC-SR501.")
for nombre, nodo, comp, prueba, extra, software, kit in [
    ("José María García (A00843900)", "dht", "DHT22, OLED 2.42\", botón, buzzer activo de 5 V con 2N2222 y LED rojo", "P-03, P-04 y P-07", "calibrar el DHT22 contra el termohigrómetro prestado",
     "reglas de alerta de temperatura y humedad en n8n (persistencia de 3 lecturas, histéresis y orden cmd/alarma) probadas con el simulador", "el NodeMCU, los LED y el botón del kit"),
    ("Arianna Téllez (A00845027)", "luz", "fotorresistencia con capuchón y LED rojo; estación del anaquel junto con Mía Nieto", "P-09 (luz)", "elegir difusor, R2 y UMBRAL_ADC con docs/prueba_ldr.md",
     "vista de luz y fotoperiodo del dashboard con Chart.js, con datos del simulador", "el NodeMCU, la fotorresistencia y los LED del kit"),
    ("Iván Acosta (A00227979)", "puerta", "reed MC-38, sus guías impresas y LED rojo; estación de entrada junto con Luis Mendoza", "P-09 (distancia de cierre del MC-38)", "medir la distancia real de cierre y ajustar las calzas",
     "avisos por WhatsApp (CallMeBot) y Telegram desde n8n, con una alerta por episodio", "el NodeMCU y los LED del kit; el reed llega con el pedido"),
    ("Mía Nieto (A00845663)", "acel", "GY-61 con ADS1115 y LED rojo; estación del anaquel junto con Arianna Téllez", "P-05 y P-09 (golpes)", "calibrar CERO_V, SENSIBILIDAD y el umbral de golpe",
     "registro de eventos (golpe, movimiento y puerta) en MySQL y su tabla en el dashboard", "el NodeMCU, el GY-61 y los LED del kit; el ADS1115 llega con el pedido"),
]:
    integrante(nombre,
        "[POR CONFIRMAR: cada integrante describe aquí, con sus palabras, las actividades técnicas que hizo para este avance]",
        f"Nodo {nodo}: {comp}.",
        f"{software[0].upper() + software[1:]}. [Revisar y ajustar]",
        f"Armar en protoboard la parte del nodo {nodo} que permite el kit ({kit}); P-01 y P-02; cargar el firmware con aprobación del equipo y publicar al servidor de pruebas (P-06). [Revisar y ajustar]",
        f"Medir con calibrador las piezas recibidas y completar el nodo {nodo}; {prueba}; {extra}; montar el nodo en su caja impresa; prueba integrada con los cinco nodos. [Revisar y ajustar]",
        f"Registro de sus pruebas con condición inicial, procedimiento, resultado y foto; captura de los mensajes del nodo {nodo} en el broker. [Revisar y ajustar]",
        "[POR CONFIRMAR: componentes, apoyos de otros integrantes y riesgos propios]")

D.referencias([
    "Comisión Federal de Electricidad. (2026). *Tarifa 1C* [Esquema tarifario vigente]. Recuperado el 23 de octubre de 2026, de https://app.cfe.mx/Aplicaciones/CCFE/Tarifas/TarifasCRECasa/Tarifas/Tarifa1C.aspx",
    "Espressif Systems. (s. f.). *ESP8266EX datasheet* (Versión 7.1). https://documentation.espressif.com/0a-esp8266ex_datasheet_en.pdf",
    "Aosong Electronics. (s. f.). *Digital-output relative humidity & temperature sensor/module DHT22 (AM2302)* [Hoja de datos]. https://cdn-shop.adafruit.com/datasheets/Digital+humidity+and+temperature+sensor+AM2302.pdf",
    "Light, R. A. (2017). Mosquitto: Server and client implementation of the MQTT protocol. *Journal of Open Source Software, 2*(13), 265. https://doi.org/10.21105/joss.00265",
    "OASIS. (2014). *MQTT version 3.1.1* (OASIS Standard). https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html",
    "Texas Instruments. (2024). *ADS111x ultra-small, low-power, I2C-compatible, 860-SPS, 16-bit ADCs with internal reference, oscillator, and programmable comparator* (SBAS444E) [Hoja de datos]. https://www.ti.com/lit/ds/symlink/ads1115.pdf",
    "tt-a1i. (2026). *Archify* (Versión 3.2.0) [Software]. GitHub. https://github.com/tt-a1i/archify",
    "UNIT Electronics. (s. f.). *Envíos y entregas*. Recuperado el 21 de octubre de 2026, de https://uelectronics.com/metodos-de-envio/",
])
D.guardar(SAL)
print("ok", D.ntab, "tablas", D.nfig, "figuras")
