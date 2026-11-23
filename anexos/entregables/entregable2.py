import sys
from docx_lib import Doc

SAL = sys.argv[1]
D = Doc()
D.portada("Cómo funciona Argos", subtitulo="Reporte del sistema de monitoreo del cuarto de incubación in vitro",
          logo="media/image1.png", curso="Equipo G507 · TC1004B")

D.h1("Introducción")
D.p("Argos vigila el cuarto de incubación in vitro del Invernadero Académico y avisa cuando algo se sale de rango. En ese cuarto se cultivan plantas pequeñas dentro de frascos de vidrio sellados, y hoy se revisa a mano: si la temperatura o la humedad pasan horas fuera de rango, nadie se entera a tiempo y se pueden perder semanas de trabajo.")
D.p("El sistema mide temperatura, humedad, luz, movimiento en la entrada, la puerta y los golpes en el anaquel. Guarda el historial, lo muestra en una página web y manda avisos por WhatsApp y Telegram. Si falla la temperatura o la humedad, además suena una alarma dentro del cuarto. No controla el clima: el minisplit y las lámparas siguen funcionando como siempre, y el sistema solo observa y avisa.")
D.p("Este reporte explica el proyecto para cualquier persona que lo necesite entender: integrantes del equipo, encargados del invernadero, profesores o alguien sin formación técnica. Las tablas guardan el detalle técnico para quien lo quiera revisar.")
D.p("**Actualización del 22 de octubre de 2026.** Los profesores confirmaron que los cinco NodeMCU son obligatorios, así que se mantienen las tres cajas. La Web API pasó a ser obligatoria y se diseñó con webhooks de n8n. El presupuesto se recalculó con precios vistos en tiendas (≈ $1,650) y se evaluaron alternativas a la impresión 3D.")
D.tabla("Rangos que vigila el sistema", [
    ["Variable", "Rango aceptable", "Margen para dar por normalizado", "Qué pasa si sale de rango"],
    ["Temperatura", "22 a 28 °C", "0.5 °C hacia dentro (22.5 a 27.5 °C)", "Alerta, aviso y alarma sonora"],
    ["Humedad relativa", "40 a 60 %", "2 % hacia dentro (42 a 58 %)", "Alerta, aviso y alarma sonora"],
    ["Luz", "Según el fotoperiodo [horario POR CONFIRMAR]", "—", "Alerta y aviso, sin alarma"],
], anchos=[1.3, 1.6, 2.0, 1.6], nota="Los rangos de temperatura y humedad los dieron los encargados. El horario de las lámparas aún no está confirmado.")

D.h1("Los cinco nodos")
D.p("Cada integrante del equipo tiene a su cargo un nodo: una placa NodeMCU (un pequeño microcontrolador con WiFi, el ESP8266; Espressif Systems, s. f.) con un sensor y un actuador. El actuador de todos es un LED rojo que reacciona a su propio sensor; el nodo de temperatura tiene además el buzzer, la única pieza que suena. Cada nodo tiene también un LED verde que solo indica si está conectado.")
D.tabla("Nodos, responsables y lo que hace cada uno", [
    ["Nodo", "Responsable", "Sensor", "Qué envía", "Cuándo enciende su LED rojo"],
    ["dht", "José María García", "DHT22", "Temperatura y humedad cada 30 s", "Mientras haya alerta de temperatura o humedad; el buzzer suena con la alerta"],
    ["luz", "Arianna Téllez", "Fotorresistencia", "Promedio de 12 muestras cada 60 s", "Cuando lee las lámparas apagadas"],
    ["pir", "Luis Mendoza", "HC-SR501", "Un evento por cada movimiento", "5 s después de cada detección"],
    ["puerta", "Iván Acosta", "Reed switch MC-38", "Puerta abierta o cerrada", "Mientras la puerta está abierta"],
    ["acel", "Mía Nieto", "GY-61 con ADS1115", "Un evento por cada golpe, con su magnitud", "5 s después de cada golpe"],
], anchos=[0.7, 1.3, 1.1, 1.6, 1.8])

D.h1("Del sensor al aviso")
D.p("Los nodos se conectan al WiFi del invernadero y mandan mensajes cortos en formato JSON con el protocolo MQTT, pensado para aparatos pequeños que envían datos con frecuencia (OASIS, 2014). Los mensajes llegan a un servidor que tiene cuatro programas en contenedores Docker: Mosquitto, que recibe y reparte los mensajes (Light, 2017); n8n, que aplica las reglas y guarda los datos (n8n, s. f.); MySQL, la base de datos (Oracle, s. f.-a); y nginx, que sirve la página web y reenvía las consultas de la Web API a n8n. El servidor corre primero en una laptop y después en una máquina gratuita de Oracle Cloud (Oracle, s. f.-b).")
D.figura("cap/como_funciona_arquitectura_fig.png", "Recorrido de los datos desde los nodos hasta los avisos", ancho=6.5,
         nota="Diagrama generado con Archify (tt-a1i, 2026). La versión interactiva está en la carpeta diagramas_interactivos.")
D.p("Los nodos no tienen reloj, así que la base de datos pone la hora al recibir cada dato y la guarda en hora universal (UTC). La página web la muestra en hora de Monterrey. Cada nodo deja además un mensaje de estado al conectarse; si se apaga o pierde la red, el propio servidor publica que el nodo quedó fuera de línea cuando pasan 45 s sin noticias de él.")
D.p("**Web API de consulta.** La página web pide el estado y el historial a una Web API de solo lectura construida con webhooks de n8n. Son tres direcciones GET que devuelven JSON: `/api/estado` (último valor y estado de cada nodo), `/api/mediciones` (historial por nodo y parámetro) y `/api/alertas` (alertas activas o todas). Cada una exige una clave en la cabecera `X-API-Key` y consulta MySQL con un usuario de solo lectura. nginx reenvía `/api/` a n8n, así que la página usa el mismo origen y el editor de n8n no queda expuesto. Los nodos no usan la API: siguen publicando por MQTT. Por ahora la API está diseñada, pero no se ha construido ni probado.")
D.tabla("Mensajes MQTT del sistema", [
    ["Tópico", "De dónde a dónde", "Ejemplo"],
    ["invernadero/telemetria/{nodo}", "Nodo → n8n", "{\"lecturas\":[{\"parametro\":\"temperatura\",\"valor\":25.4,\"unidad\":\"C\"}]}"],
    ["invernadero/evento/{nodo}", "Nodo → n8n", "{\"tipo\":\"golpe\",\"magnitud\":1.8}"],
    ["invernadero/estado/{nodo}", "Nodo o servidor (último deseo)", "{\"estado\":\"online\",\"rssi\":-62}"],
    ["invernadero/cmd/alarma", "n8n → nodo dht", "on / off, repetido cada 60 s"],
    ["invernadero/cmd/silenciar", "Nodo dht → n8n", "{\"minutos\":30}"],
], anchos=[2.1, 1.6, 2.8], primera_negrita=False, tam=9.5)

D.h1("Cuándo suena la alarma")
D.p("Una alerta se abre cuando hay tres lecturas seguidas fuera de rango, es decir, 90 s con el nodo de temperatura. Se cierra cuando hay tres lecturas seguidas dentro del rango ya descontado el margen. Ese margen (histéresis) evita que una lectura que oscila justo en el límite genere un aviso cada 30 s. Por cada episodio sale un solo aviso.")
D.p("La alarma tiene dos caminos. El nodo `dht` aplica la regla por su cuenta, así que suena aunque se caiga el WiFi. Además, mientras la alerta siga abierta, n8n le repite la orden de encender cada 60 s; si la orden deja de llegar durante 150 s, el nodo la da por vencida. El botón del nodo silencia el buzzer 30 minutos, pero el LED rojo sigue encendido y los avisos por mensaje no se detienen.")
D.figura("cap/como_funciona_alarma_fig.png", "Estados de la alarma del nodo de temperatura", ancho=6.5)
D.figura("cap/como_funciona_aviso_calor_fig.png", "Secuencia de un aviso por calor, del sensor al celular del encargado", ancho=5.6,
         nota="Los valores son un ejemplo: 28.6 °C es una lectura supuesta para ilustrar el caso.")
D.tabla("Qué significa cada luz", [
    ["Luz", "Significado"],
    ["Verde fija", "Conectado al WiFi y al servidor"],
    ["Verde con parpadeo lento", "Sin WiFi o sin servidor; el nodo sigue midiendo y la alarma local del dht sigue activa"],
    ["Roja fija o pulso de 5 s", "El nodo reacciona a su sensor (ver la tabla de los cinco nodos)"],
    ["Roja con parpadeo rápido", "Falla del sensor: tres lecturas inválidas seguidas; el nodo avisa una vez con sensor_error"],
], anchos=[1.8, 4.7])

D.h1("Hardware: tres cajas para cinco nodos")
D.p("Al principio cada nodo iba a tener su propia caja y su propia fuente. Al sumar el presupuesto, ese arreglo quedaba unos $343 MXN arriba del tope de $1,500, así que el 19 de octubre reagrupamos los nodos en tres cajas impresas en 3D con PETG. Siguen siendo cinco microcontroladores independientes, uno por integrante, cada uno con su sensor, sus LED y su propio usuario en el servidor; lo que se comparte es la caja, la protoboard y la fuente de 5 V. Los profesores confirmaron que los cinco NodeMCU son obligatorios, así que este arreglo se mantiene y se descartaron las opciones con menos microcontroladores.")
D.viñetas([
    "La **caja dht** va sola, en vertical (80 × 138 × 40.5 mm). Lleva el DHT22 en una cámara aislada debajo de la placa para que el calor de la electrónica no altere la lectura, una pantalla OLED de 2.42\" (una pantalla pequeña de alto contraste), el botón, el buzzer y su fuente de 5 V de al menos 1 A.",
    "La **estación de entrada** (174 × 80 × 40.5 mm, horizontal) junta los nodos `pir` y `puerta` junto a la puerta. El sensor de movimiento asoma por la tapa y el sensor magnético llega por cable al marco de la puerta, con guías impresas.",
    "La **estación del anaquel** (174 × 80 × 40.5 mm) junta `acel` y `luz` y va atornillada al anaquel para que el acelerómetro sienta los golpes. La fotorresistencia sale por cable a un capuchón negro junto a la lámpara.",
])
D.figura("cap/prototipo_cajas_fig.png", "Cinco nodos en tres cajas, con una fuente de 5 V por caja", ancho=6.5)
D.h2("Reutilización del kit del curso")
D.p("Casi todo sale de los kits de los cinco integrantes: las cinco placas NodeMCU, la fotorresistencia, el sensor de movimiento HC-SR501, el acelerómetro GY-61, los LED, el botón, las resistencias, los cables y las protoboards. Cada estación usa una protoboard MB-102 de 830 puntos del kit, así que solo se compra una protoboard pequeña de 400 puntos para la caja `dht`. Los kits traen 50 resistencias de 330 Ω, suficientes para los diez LED. Los puentes cortos se hacen con cable UTP sólido reciclado.")
D.p("Se compran solo las piezas que el kit no trae o que no sirven para el cuarto: el DHT22, con ±0.5 °C de exactitud (Aosong Electronics, s. f.), porque el DHT11 del kit es menos preciso, el reed switch MC-38 en lugar del sensor ultrasónico, el convertidor ADS1115 de 16 bits para leer el acelerómetro con más resolución (Texas Instruments, s. f.), el buzzer con su transistor, la pantalla, las fuentes y el filamento.")
D.h2("Alternativas a la impresión 3D")
D.p("Las cajas se imprimen en PETG; el equipo registra el filamento como comprado. Por si no hubiera impresora disponible, se compararon un gabinete ABS comercial, una caja de registro eléctrico de PVC, acrílico cortado con láser y dejar las protoboards sin caja. Ninguna resuelve la cámara aislada del DHT22, las ventanas de la pantalla y de los LED ni los soportes de la fotorresistencia y del sensor magnético, que habría que imprimir o fabricar de todos modos, y todas suman costo; sus precios no se pudieron verificar [POR CONFIRMAR]. Por eso se mantiene la impresión, y las protoboards sin caja solo se usan como primer prototipo.")
D.h2("Alimentación y fuentes")
D.p("Todo va conectado a la corriente, sin baterías: el monitoreo es continuo y el cuarto tiene contactos. Hay tres fuentes de 5 V, una por caja; las de las estaciones son de al menos 2 A porque alimentan dos placas. En cada estación, un módulo de entrada USB-C lleva los 5 V a los rieles de la protoboard. Las dos placas comparten 5 V y tierra, pero la salida de 3.3 V de cada placa nunca se une con la de la otra, porque cada una tiene su propio regulador. Un capacitor de 220 µF en cada entrada de 5 V amortigua los picos de consumo del WiFi y del buzzer.")
D.tabla("Consumo y corrientes", [
    ["Concepto", "Valor", "Origen del dato"],
    ["Consumo promedio del nodo dht", "≈ 42 mA", "Estimado; se medirá en la prueba P-05"],
    ["Pico del ESP8266 al transmitir", "≈ 300–400 mA", "Valor de diseño del equipo; se medirá"],
    ["Estación con 2 nodos, promedio y pico", "≈ 0.1–0.2 A y ≈ 0.6 A", "Estimado"],
    ["Corriente por LED con 330 Ω a 3.3 V", "≈ 3.3–4.5 mA", "Cálculo; el límite por pin es ≈ 12 mA"],
    ["Base y colector del 2N2222 (buzzer)", "≈ 2.5 mA y ≈ 30 mA", "Cálculo"],
], anchos=[2.6, 1.6, 2.3])
D.figura("cap/prototipo_cableado_dht_fig.png", "Conexiones del nodo dht a los pines del NodeMCU", ancho=6.3)
D.tabla("Pines de cada nodo", [
    ["Nodo", "Pin", "Conexión"],
    ["dht", "D4", "Dato del DHT22, con resistencia de 10 kΩ a 3.3 V"],
    ["dht", "D1 / D2", "Pantalla OLED por I²C (reloj y datos)"],
    ["dht", "D5", "Base del transistor 2N2222 que enciende el buzzer"],
    ["dht", "D6", "Botón de silencio a tierra"],
    ["luz", "A0", "Divisor de la fotorresistencia con 10 kΩ"],
    ["pir / puerta", "D5", "Salida del HC-SR501 / reed switch a tierra"],
    ["acel", "D1 / D2", "ADS1115 por I²C (dirección 0x48); el GY-61 entra por A0 a A2 del ADS1115"],
    ["Todos", "D7 / D8", "LED verde y LED rojo, cada uno con 330 Ω a tierra"],
], anchos=[1.1, 0.9, 4.5])

D.h1("Presupuesto")
D.p("El tope de hardware extra es de $1,500 MXN. Los precios se leyeron el 21 de octubre de 2026 en la página de cada tienda, no en un carrito; los marcados como estimados no se pudieron verificar. El escenario es el de tres cajas, con la sílica gel nueva y sin repuestos del buzzer ni del transistor. El tiempo de entrega de cada tienda está [POR CONFIRMAR].")
D.tabla("Presupuesto del escenario de tres cajas", [
    ["Concepto", "Cant.", "Unitario", "Subtotal", "Proveedor"],
    ["DHT22 (AM2302)", "1", "$119", "$119", "Geek Factory"],
    ["Reed switch MC-38 con imán", "1", "$24", "$24", "MV Electrónica"],
    ["Convertidor ADS1115", "1", "$56.84", "$56.84", "Lionchip México"],
    ["Buzzer activo KY-012", "1", "$18", "$18", "Ideaelectronica"],
    ["Transistor 2N2222 TO-92 (estimado)", "1", "$1", "$1", "UNIT Electronics"],
    ["Resistencias 1 kΩ (3) y 10 kΩ (4) (estimado)", "7", "$0.50", "$3.50", "Kit o por confirmar"],
    ["Capacitor 220 µF / 25 V", "5", "$3", "$15", "Steren"],
    ["OLED 2.42\" SSD1309 I²C", "1", "$231.99", "$231.99", "Amazon México"],
    ["Protoboard de 400 puntos", "1", "$55.68", "$55.68", "Steren"],
    ["Fuentes de 5 V: una de ≥ 1 A y dos de ≥ 2 A", "3", "$139", "$417", "Cyberpuerta (Steren)"],
    ["Módulos de entrada USB-C (estimado)", "2", "$15", "$30", "Por confirmar"],
    ["Filamento PETG 1 kg", "1", "$348", "$348", "Creality México"],
    ["Insertos térmicos y tornillos M3 (estimado)", "1 lote", "$120", "$120", "Por confirmar"],
    ["Sílica gel (estimado)", "1", "$60", "$60", "Por confirmar"],
    ["Termohigrómetro de referencia", "—", "prestado", "$0", "—"],
    ["Envío (estimado)", "1", "$150", "$150", "Por confirmar"],
    ["Total", "", "", "≈ $1,650", ""],
], anchos=[2.5, 0.6, 0.9, 0.9, 1.6], tam=9.5, nota="El total queda ≈ $150 arriba del tope. Para entrar: recoger el pedido en sucursal en lugar de pagar el envío (−$150; MV Electrónica tiene sucursal en San Nicolás, N.L., y falta confirmarlo con las demás tiendas) y usar tuercas M3 en lugar de insertos térmicos, que el diseño admite. Con ambos cambios queda en ≈ $1,500 o menos [POR CONFIRMAR]. El arreglo original de cinco cajas separadas excedía el tope por unos $343. Las NodeMCU, los sensores del kit, los LED, los botones, los cables y las protoboards MB-102 no se compran.")

D.h1("Base de datos")
D.p("La base de datos tiene 13 tablas. Además de las lecturas, guarda las cajas y su ubicación, los sensores, los umbrales, las alertas con sus avisos, el estado de cada nodo, los seis actuadores (el buzzer y los cinco LED rojos) y cada vez que uno se enciende, con su origen: una alerta, la regla local del nodo o una prueba manual. Las mediciones se conservan 90 días. El diseño completo, con el modelo de clases, la normalización y el diccionario de datos, está en el entregable de la Etapa 2 de software.")

D.h1("Qué está probado y qué no")
D.p("Casi todo el diseño sale de un solo archivo de configuración del armado. De ahí se generan el dibujo de cada protoboard, el cableado, los esquemáticos, las instrucciones de armado y un modelo 3D de las cajas con sus componentes adentro. Un solo comando regenera todo y corre los chequeos.")
D.tabla("Estado de las verificaciones al 21 de octubre de 2026", [
    ["Chequeo", "Resultado", "Cómo se hizo"],
    ["Programa de los 6 entornos (5 nodos y dht sin pantalla)", "Compila", "PlatformIO; RAM 35–38 %, memoria 27–29 %"],
    ["Conexiones de las 8 protoboards", "Sin errores", "Cada orificio existe, no se repite y las conexiones eléctricas coinciden con las esperadas"],
    ["Pines del programa contra el armado", "6 de 6", "Se comparan las constantes del código con las conexiones de la protoboard"],
    ["Reglas del buzzer", "21 de 21 pruebas", "En la computadora, con reloj simulado"],
    ["Cajas", "0 choques entre piezas", "Modelo 3D; holgura mínima de 3.5 mm (dht) y 4.07 mm (estaciones)"],
    ["Programa en una placa real", "Pendiente", "No se ha cargado en ningún NodeMCU"],
    ["Medidas reales de las piezas", "Pendiente", "Falta medir con calibrador"],
    ["Servidor (Mosquitto, n8n, MySQL, Web API y página web)", "Sin empezar", "Ya existe un simulador de los 5 nodos para probarlo sin hardware"],
], anchos=[2.4, 1.3, 2.8])

D.h1("Calendario y riesgos")
D.tabla("Avance por etapa", [
    ["Etapa", "Fechas", "Estado"],
    ["1. Definición", "21 sep – 2 oct", "Hecha"],
    ["2. Sensores y actuadores", "5 – 16 oct", "Diseño completo; falta probar en placa"],
    ["3. Base de datos", "19 oct – 6 nov", "En curso: esquema y Web API diseñados; falta montar el servidor"],
    ["4. Análisis de datos", "9 – 20 nov", "Integración y cinco indicadores"],
    ["5. Pruebas y presentación", "23 nov – 4 dic", "Pruebas finales y presentación"],
], anchos=[2.0, 1.5, 3.0])
D.p("El diseño físico va adelantado y el software del servidor, que es lo que pide la etapa actual, todavía no empieza; la prioridad de las próximas dos semanas pasa de las cajas al servidor. La Web API es obligatoria y se construirá con webhooks de n8n; falta confirmar con el profesor que esa forma cumple el requisito. El tipo de WiFi del invernadero tampoco está confirmado: el ESP8266 se conecta bien a redes con contraseña, pero no a redes empresariales con usuario, y en ese caso habría que pedir una red aparte. Por último, todas las medidas de las cajas son nominales hasta medir las piezas reales e imprimir las piezas de prueba de ajuste.")

D.h1("Preguntas abiertas")
D.tabla("Preguntas pendientes por destinatario", [
    ["Para quién", "Pregunta"],
    ["Profesores", "¿Cuenta el LED rojo como actuador de cada integrante?\n¿Aceptan tres cajas con dos placas que comparten fuente?\n¿La Web API hecha con webhooks de n8n cumple el requisito?\n¿Qué evidencia aceptan antes de cargar el programa en las placas?\n¿Qué cuenta como cinco indicadores distintos?"],
    ["Encargados del invernadero", "Horario de las lámparas y horario de acceso al cuarto.\nTipo de WiFi, registro de MAC y puertos permitidos.\nSi autorizan la pantalla y que suene el buzzer.\nSi se puede atornillar a la pared y al anaquel.\nQuién recibe los avisos por WhatsApp y Telegram."],
], anchos=[1.6, 4.9])

D.h1("Diagramas interactivos")
D.p("En la carpeta `diagramas_interactivos` hay tres páginas HTML que se abren con doble clic en cualquier navegador, sin internet y sin cuenta: `como_funciona_arquitectura.html`, `como_funciona_aviso_calor.html` y `como_funciona_alarma.html`. Permiten acercar, mover el diagrama, buscar un componente y seguir una ruta de punta a punta. Las figuras 1, 2 y 3 son capturas de esas páginas.")

D.referencias([
    "Espressif Systems. (s. f.). *ESP8266EX datasheet*. https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf",
    "Aosong Electronics. (s. f.). *Digital-output relative humidity & temperature sensor/module DHT22 (AM2302)* [Hoja de datos]. https://cdn-shop.adafruit.com/datasheets/Digital+humidity+and+temperature+sensor+AM2302.pdf",
    "Light, R. A. (2017). Mosquitto: Server and client implementation of the MQTT protocol. *Journal of Open Source Software, 2*(13), 265. https://doi.org/10.21105/joss.00265",
    "n8n. (s. f.). *n8n docs*. Recuperado el 21 de octubre de 2026, de https://docs.n8n.io/",
    "OASIS. (2014). *MQTT version 3.1.1* (OASIS Standard). https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/os/mqtt-v3.1.1-os.html",
    "Oracle. (s. f.-a). *MySQL 8.0 reference manual*. Recuperado el 21 de octubre de 2026, de https://dev.mysql.com/doc/refman/8.0/en/",
    "Oracle. (s. f.-b). *Oracle Cloud Free Tier*. Recuperado el 21 de octubre de 2026, de https://www.oracle.com/cloud/free/",
    "Texas Instruments. (s. f.). *ADS111x ultra-small, low-power, I2C-compatible, 860-SPS, 16-bit ADCs* [Hoja de datos]. https://www.ti.com/lit/ds/symlink/ads1115.pdf",
    "tt-a1i. (2026). *Archify* (Versión 3.2.0) [Software]. GitHub. https://github.com/tt-a1i/archify",
])
D.guardar(SAL)
print("ok", D.ntab, "tablas", D.nfig, "figuras")
