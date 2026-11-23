import sys
from docx_lib import Doc

SAL = sys.argv[1]
R = "C:/Users/luedm/Documents/Estudio/IncuMonitor/"
IMG = R + "presentacion/img/"
D = Doc()
D.portada("Prototipo Argos", subtitulo="Cinco nodos en tres cajas para el cuarto de incubación in vitro",
          logo="media/image1.png", curso="Equipo G507 · TC1004B")

D.h1("Introducción")
D.p("Este reporte muestra cómo se verían y cómo se comportarían los sensores que proponemos instalar en el cuarto de incubación in vitro del Invernadero Académico. El sistema solo vigila y avisa: no toca el minisplit ni las lámparas. Lo único que hace cada nodo por su cuenta es encender su LED rojo cuando su sensor detecta algo, y el nodo de temperatura además hace sonar una alarma.")
D.p("Es un borrador para revisar con los encargados y con los profesores antes de fabricar. Las cajas se dibujaron con las medidas típicas de cada componente; todavía no hemos medido las piezas reales ni impreso nada. Todas las medidas de este documento son nominales y se ajustarán después de medir con calibrador.")

D.p("**Actualización del 22 de octubre de 2026.** Los profesores confirmaron que los cinco NodeMCU son obligatorios, así que se mantienen las tres cajas. La Web API pasó a ser obligatoria y se diseñó con webhooks de n8n. El presupuesto se recalculó con precios vistos en tiendas (≈ $1,650) y se evaluaron alternativas a la impresión 3D.")

D.h1("Cinco nodos en tres cajas")
D.p("Son cinco microcontroladores NodeMCU independientes, uno por integrante, cada uno con su sensor, su LED rojo como actuador y su propia conexión al WiFi. Los que van juntos en el cuarto comparten caja y fuente de 5 V: la estación de entrada (accesos y puerta) y la estación del anaquel (golpes y luz). El nodo de temperatura va solo para que el calor de la electrónica no altere su lectura. Agruparlos así ahorra dos fuentes y una protoboard, y permite usar las protoboards de 830 puntos que ya vienen en el kit. Los profesores confirmaron que los cinco NodeMCU son obligatorios, así que este arreglo se mantiene.")
D.tabla("Las tres cajas", [
    ["Caja", "Nodos", "Medidas (mm)", "Montaje", "PETG"],
    ["Temperatura", "dht", "80 × 138 × 40.5, vertical (166 de alto con orejas)", "Pinza en la repisa o placa en la pared, a la altura de los frascos", "≈ 155 g"],
    ["Estación de entrada", "pir + puerta", "174 × 80 × 40.5, horizontal (202 de ancho con orejas)", "Junto a la puerta a ≈ 2 m de altura; dos tacos con tornillos o tiras removibles", "≈ 160 g"],
    ["Estación del anaquel", "acel + luz", "174 × 80 × 40.5, horizontal", "Rígida al anaquel con 2 tornillos o cinchos, para que el acelerómetro sienta los golpes", "≈ 142 g"],
], anchos=[1.2, 0.9, 1.7, 2.0, 0.7], nota="Las tres cajas se imprimen en PETG blanco mate sin soportes, se cierran con 4 tornillos por el frente y suman ≈ 458 g de filamento con las piezas pequeñas.")
D.figura("cap/prototipo_cajas_fig.png", "Cajas, fuentes y sensores externos de los cinco nodos", ancho=6.4,
         nota="Diagrama generado con Archify (tt-a1i, 2026); su versión interactiva está en la carpeta diagramas_interactivos.")
D.figura(IMG + "nodo_dht_vistas.png", "Vistas acotadas de la caja del nodo de temperatura", ancho=6.2,
         nota="El sensor va en una cámara aparte en la parte de abajo, aislada del calor de la electrónica. Medidas en milímetros, nominales.")
D.figura_doble([IMG + "nodo_dht_explosionada.png", IMG + "nodo_dht_escena_anaquel.png"],
               "Ensamble de la caja dht y escena de montaje en la repisa", ancho=3.0,
               nota="Izquierda: base, insertos, electrónica, pantalla, tapa y tornillos; se abre por el frente sin descolgarla. Derecha: escena esquemática colgada de la repisa a la altura de los frascos.")
D.figura(IMG + "nodo_entrada_vistas.png", "Vistas de la estación de entrada", ancho=6.4)
D.figura(IMG + "nodo_anaquel_vistas.png", "Vistas de la estación del anaquel", ancho=6.4,
         nota="Cada par de LED de las estaciones lleva rotulado el nombre de su sensor: PIR y PUERTA, ACEL y LUZ.")

D.h1("Por dentro: cortes por niveles")
D.p("Cada caja se cortó en cinco planos paralelos al frente, de la espalda hacia afuera, para revisar que todo quepa. N1 es el piso con la protoboard, N2 las placas, N3 los conectores, N4 lo que queda debajo de la tapa y N5 el frente con sus ventanas y luces. En el modelo 3D las piezas no chocan entre sí y la holgura mínima es de 3.5 mm en la caja dht y de 4.07 mm en las estaciones.")
D.figura(IMG + "niveles_dht.png", "Cortes por niveles de la caja del nodo de temperatura", ancho=5.2,
         nota="Gris: carcasa impresa. Crema: protoboard. Azul: NodeMCU. Verde: sensores y componentes. Gris oscuro: conectores. Naranja: LED.")
D.figura(IMG + "niveles_entrada.png", "Cortes por niveles de la estación de entrada", ancho=5.6)

D.h1("Piezas que van fuera de la caja")
D.p("Dos sensores van fuera de su caja, unidos por cable. La fotorresistencia va dentro de un capuchón negro de 16 × 26 mm junto a la lámpara: solo entra luz por una ventana de 4.5 mm con un disco difusor blanco, y una visera bloquea la luz lateral del cuarto. Una horquilla sujeta el capuchón con 2 tornillos o 2 cinchos y permite girarlo de −90° a +75° para apuntarlo a la lámpara.")
D.p("El sensor de puerta MC-38 va en el marco y su imán en la hoja, cada uno en una guía impresa de 51 × 18 × 12 mm que lo retiene con un clic. Con la puerta cerrada quedan a unos 20 mm, y las ranuras permiten ajustar ±3 mm cada guía.")
D.figura_doble([IMG + "capuchon_ldr_iso.png", IMG + "soporte_ldr_iso.png"], "Capuchón de la fotorresistencia y su horquilla", ancho=3.0)
D.figura_doble([IMG + "porta_sensor_iso.png", IMG + "porta_iman_iso.png"], "Guías impresas del sensor magnético de la puerta", ancho=3.0,
               nota="Izquierda: guía del sensor, en el marco, con salida de cable hacia la estación. Derecha: guía del imán, en la hoja de la puerta, con cinta doble cara o 2 tornillos.")

D.h1("Versiones del prototipo y alternativas a la impresión 3D")
D.p("Para no imprimir las cajas completas antes de tiempo, el prototipo avanza por versiones. Primero se prueba todo sin caja; después se imprimen piezas pequeñas para revisar ajustes, y solo al final las tres cajas. Las semanas son una propuesta del equipo.")
D.tabla("Versiones del prototipo (propuesta)", [
    ["Versión", "Qué incluye", "Material", "Semanas"],
    ["v0", "Protoboards sin caja; firmware, MQTT y n8n funcionando de punta a punta", "Nada extra", "1 y 2"],
    ["v1", "Piezas de prueba: ventana de la pantalla, cámara del DHT22, capuchón de la fotorresistencia, guía del MC-38 y bahía de la protoboard", "Poco PETG", "2 y 3"],
    ["v2", "Las tres cajas completas; diferencia menor a 1 °C contra el termohigrómetro y pantalla legible a 2 m", "PETG", "3 y 4"],
    ["v3", "Instalación en el cuarto, ajustes y reimpresiones si hacen falta", "Resto del carrete", "5 y 6"],
], anchos=[0.7, 3.6, 1.1, 1.1])
D.p("También se compararon otras formas de hacer las cajas, por si no hubiera impresora disponible. En todas habría que fabricar aparte el capuchón de la fotorresistencia, las guías del sensor de puerta y la cámara del DHT22, que es lo que el modelo impreso resuelve mejor. Sus precios no se pudieron verificar [POR CONFIRMAR].")
D.tabla("Alternativas a la impresión 3D", [
    ["Opción", "Ventaja", "Desventaja", "Veredicto"],
    ["PETG impreso (actual)", "Cámara aislada del DHT22, ventanas y soportes a medida", "Horas de impresión y posibles reimpresiones", "Se mantiene"],
    ["Gabinete ABS comercial", "Acabado limpio y fácil de limpiar", "Sin cámara aislada; perforaciones a mano; el gabinete GP-17 ya se descartó por poco profundo", "Solo si no hay impresora"],
    ["Caja de registro de PVC", "Barata y resistente", "Aspecto de obra; puede no alojar la protoboard de 830 puntos", "Plan de emergencia"],
    ["Acrílico cortado con láser", "Rápido si hay láser disponible", "Rediseño en 2D y uniones pegadas; el MDF absorbe humedad", "No conviene en 6 semanas"],
    ["Protoboard sin caja", "Sin costo y fácil de revisar", "No es removible, ni limpiable, ni tiene tapa", "Solo como versión v0"],
], anchos=[1.4, 1.6, 2.3, 1.2], tam=9.5)

D.h1("Cómo se comporta el nodo de temperatura")
D.p("El nodo lee temperatura y humedad cada 30 s. Para evitar falsas alarmas exige tres lecturas seguidas fuera de rango antes de avisar, y tres lecturas dentro con margen para dar el episodio por cerrado. La regla funciona dentro del propio nodo, así que la alarma suena aunque se caiga el internet. El botón tiene dos usos: una pulsación corta enciende la pantalla y una larga silencia el buzzer 30 minutos, sin detener los avisos por mensaje.")
D.figura("cap/como_funciona_alarma_fig.png", "Estados de la alarma del nodo de temperatura", ancho=6.4)
D.tabla("Lo que se ve y se oye en el nodo dht", [
    ["Situación", "LED verde", "LED rojo", "Buzzer", "Pantalla"],
    ["Todo en rango y conectado", "Fijo", "Apagado", "Callado", "T y HR; se apaga sola a los 30 s"],
    ["Sin WiFi o sin servidor", "Parpadeo lento", "Según la lectura", "Sigue la regla local", "Barra de estado: sin red"],
    ["Alerta de temperatura o humedad", "Fijo", "Fijo", "Suena", "Barra invertida (fondo claro) para notarla de lejos"],
    ["Alerta silenciada con el botón", "Fijo", "Fijo", "Callado 30 min", "Barra de alarma"],
    ["Falla del sensor", "Fijo", "Parpadeo rápido", "Callado", "Barra de falla del sensor"],
], anchos=[1.6, 0.9, 1.0, 1.1, 1.9])
D.p("La pantalla es una OLED de 2.42\" con un área visible de 55 × 27.5 mm. Muestra la temperatura con dígitos de unos 11 mm, la humedad con dígitos de unos 7 mm y una barra de estado. No es un actuador: solo informa a quien está en el cuarto.")

D.h1("Circuitos")
D.p("Las cinco placas usan la misma base: NodeMCU con el ESP8266 (Espressif Systems, s. f.), un capacitor de 220 µF en la entrada de 5 V, y un LED verde (D7) y uno rojo (D8) con resistencias de 330 Ω. Ningún sensor manda más de 3.3 V a la placa; el único elemento a 5 V que se controla, el buzzer, se enciende a través de un transistor 2N2222. En las estaciones, dos circuitos comparten protoboard, caja y fuente, pero no se tocan entre sí salvo en los 5 V y la tierra. El nodo dht lee un DHT22 (Aosong Electronics, s. f.) y el nodo acel lee el acelerómetro GY-61 con un convertidor ADS1115 de 16 bits (Texas Instruments, s. f.).")
D.figura("cap/prototipo_cableado_dht_fig.png", "Conexiones del nodo dht a los pines del NodeMCU", ancho=6.3)
D.figura(R + "hardware/esquematicos/nodo_dht.png", "Esquemático del nodo de temperatura y humedad", ancho=5.4)
D.figura(R + "presentacion/protoboard/nodo_dht_protoboard.png", "Armado en protoboard del nodo dht (400 puntos)", ancho=5.8)
D.figura_doble([R + "presentacion/protoboard/estacion_entrada_protoboard.png", R + "presentacion/protoboard/estacion_anaquel_protoboard.png"],
               "Armado en protoboard de las dos estaciones (MB-102 de 830 puntos)", ancho=3.0,
               nota="Izquierda: estación de entrada (pir y puerta). Derecha: estación del anaquel (acel y luz). Los rieles de 5 V y GND se unen entre mitades; el 3.3 V de cada placa no.")
D.p("Los esquemáticos de los nodos `luz`, `pir`, `puerta` y `acel` y el cableado de cada caja están en el repositorio del proyecto, junto con un chequeo automático que confirma que cada protoboard coincide con su esquemático.")

D.h1("Ubicación propuesta en el cuarto")
D.p("Las posiciones son una propuesta que confirmaríamos con los encargados en la visita. Cada caja necesita un contacto cerca para su fuente de 5 V: uno junto al anaquel, uno junto a la puerta y uno para el nodo de temperatura.")
D.tabla("Dónde va cada caja", [
    ["Caja", "Ubicación", "Motivo"],
    ["Temperatura (dht)", "Colgada del borde de una repisa o en la pared, a la altura de los frascos, lejos del minisplit y de las lámparas", "Medir el aire que rodea a los frascos sin el efecto directo del aire acondicionado ni del calor de las lámparas"],
    ["Estación del anaquel (acel + luz)", "Fija al anaquel; la fotorresistencia, en su capuchón junto a una lámpara", "El acelerómetro tiene que sentir los golpes del anaquel; la fotorresistencia, solo la luz de la lámpara"],
    ["Estación de entrada (pir + puerta)", "Junto a la puerta, a unos 2 m de altura; el sensor magnético en el marco", "Registrar movimiento y avisar si ocurre fuera del horario de lunes a viernes de 8:00 a 17:00, y si la puerta queda abierta"],
], anchos=[1.5, 2.6, 2.4])

D.h1("Puntos para aprobación de los encargados")
D.tabla("Decisiones que necesitamos que los encargados aprueben", [
    ["Tema", "Propuesta", "Pregunta"],
    ["Pantalla en el nodo dht", "Pantalla de 2.42\" que se apaga sola a los 30 s y se enciende con el botón", "El correo autorizaba solo una alarma: ¿podemos incluirla?"],
    ["Alarma sonora", "Suena solo si la temperatura o la humedad salen de rango; el botón la silencia 30 min", "¿Hay restricción de volumen o de horario?"],
    ["Fijación de las cajas", "Pinza impresa en la repisa, o placa en la pared con 2 tornillos o tiras removibles; el nodo de golpes, con 2 tornillos o cinchos al anaquel", "¿Qué fijación permiten en paredes y anaqueles?"],
    ["Ubicación", "Las posiciones de la tabla anterior", "¿Coinciden con el uso diario del cuarto?"],
    ["Luces de estado", "Un LED verde y uno rojo por nodo, de brillo bajo, visibles a unos 3 m", "¿Hay alguna restricción de luz por las plantas?"],
    ["Capuchón junto a la lámpara", "Pieza negra sujeta a la estructura de la lámpara con 2 cinchos o 2 tornillos, sin tocar la lámpara ni los frascos", "¿Podemos sujetarla a la estructura de las lámparas?"],
    ["Guías del sensor de puerta", "Dos piezas de 51 × 18 × 12 mm con cinta doble cara o 2 tornillos pequeños", "¿Se permite cinta o tornillos en el marco y la puerta?"],
    ["Limpieza y contactos", "El PETG resiste el alcohol al 70 %; cada caja necesita un contacto", "¿Usan cloro u otro desinfectante? ¿Hay contactos cerca del anaquel y de la puerta?"],
], anchos=[1.5, 2.8, 2.2])

D.h1("Presupuesto")
D.p("El tope de hardware extra es de $1,500 MXN. Las placas, la mayoría de los sensores, los LED, el botón, los cables y las dos protoboards de 830 puntos salen de los kits del curso. Los precios se leyeron el 21 de octubre de 2026 en la página de cada tienda; el desglose por pieza y proveedor está en el reporte «Cómo funciona Argos».")
D.tabla("Presupuesto por rubro", [
    ["Rubro", "Incluye", "Subtotal"],
    ["Sensores", "DHT22, MC-38 y ADS1115", "$199.84"],
    ["Electrónica", "Buzzer, transistor, resistencias y capacitores", "$37.50"],
    ["Pantalla", "OLED 2.42\" SSD1309 I²C", "$231.99"],
    ["Montaje", "Protoboard de 400 puntos y sílica gel (estimado)", "$115.68"],
    ["Alimentación", "3 fuentes de 5 V y 2 módulos USB-C (estimado)", "$447"],
    ["Impresión", "PETG 1 kg, insertos térmicos y tornillos M3 (estimado)", "$468"],
    ["Envío", "Pedido a las tiendas (estimado)", "$150"],
    ["Total", "", "≈ $1,650"],
], anchos=[1.3, 4.0, 1.2], nota="El total queda ≈ $150 arriba del tope. Para entrar: recoger el pedido en sucursal en lugar de pagar el envío (−$150; MV Electrónica tiene sucursal en San Nicolás, N.L., y falta confirmarlo con las demás tiendas) y usar tuercas M3 en lugar de insertos térmicos, que el diseño admite. Con ambos cambios queda en ≈ $1,500 o menos [POR CONFIRMAR].")

D.h1("Avance y siguientes pasos")
D.p("Al 21 de octubre de 2026 nada se ha instalado ni conectado a una placa real. En computadora, los programas de los cinco nodos compilan, un chequeo automático confirma que las conexiones de cada protoboard y los pines del programa coinciden con los esquemáticos, las reglas de la alarma pasan 21 pruebas y las cajas no tienen piezas que choquen. También hay un simulador que manda por la red los mismos mensajes que mandarían los nodos, para armar el servidor sin esperar al hardware.")
D.p("Lo que sigue es levantar el servidor (mensajería, base de datos, flujos de aviso y la Web API de consulta), medir las piezas reales con calibrador, imprimir las piezas de prueba de ajuste y probar la fotorresistencia junto a la lámpara. Para eso necesitamos las respuestas de la sección anterior, el horario de las lámparas, el horario de acceso y los datos del WiFi.")

D.h1("Diagramas interactivos")
D.p("En la carpeta `diagramas_interactivos` están `prototipo_cajas.html` y `prototipo_cableado_dht.html`, las versiones interactivas de las figuras 1 y 11. Se abren con doble clic en cualquier navegador, sin internet ni cuenta, y permiten acercar, buscar un componente y seguir una conexión. El modelo 3D de las cajas se diseñó con build123d (build123d, s. f.) y el cableado de cada caja con WireViz (WireViz, s. f.).")

D.referencias([
    "Aosong Electronics. (s. f.). *Digital-output relative humidity & temperature sensor/module DHT22 (AM2302)* [Hoja de datos]. https://cdn-shop.adafruit.com/datasheets/Digital+humidity+and+temperature+sensor+AM2302.pdf",
    "build123d. (s. f.). *build123d documentation*. Recuperado el 21 de octubre de 2026, de https://build123d.readthedocs.io/en/latest/",
    "Espressif Systems. (s. f.). *ESP8266EX datasheet*. https://www.espressif.com/sites/default/files/documentation/0a-esp8266ex_datasheet_en.pdf",
    "Texas Instruments. (s. f.). *ADS111x ultra-small, low-power, I2C-compatible, 860-SPS, 16-bit ADCs* [Hoja de datos]. https://www.ti.com/lit/ds/symlink/ads1115.pdf",
    "tt-a1i. (2026). *Archify* (Versión 3.2.0) [Software]. GitHub. https://github.com/tt-a1i/archify",
    "WireViz. (s. f.). *WireViz* [Software]. GitHub. Recuperado el 21 de octubre de 2026, de https://github.com/wireviz/WireViz",
])
D.guardar(SAL)
print("ok", D.ntab, "tablas", D.nfig, "figuras")
