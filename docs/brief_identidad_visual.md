# Argos — Brief para identidad visual

Proyecto del equipo G507 · TC1004B · Tec de Monterrey. Duración ~6 semanas. Nombre anterior de trabajo: IncuMonitor.

## 1. Qué es

**Argos** es un sistema IoT de **monitoreo y aviso** (no de control) para el **cuarto de incubación in vitro del Invernadero Académico**, donde se cultivan plantas en frascos bajo condiciones ambientales estrictas. El sistema "vigila" el cuarto de forma continua y avisa a los encargados cuando algo sale de rango, para que intervengan a tiempo.

> `[POR CONFIRMAR]` El origen del nombre "Argos" no está documentado. Si la idea es el vigilante de los cien ojos de la mitología griega, conviene confirmarlo con el equipo antes de usarlo como concepto gráfico.

## 2. Problema que resuelve

Las condiciones del cuarto (temperatura, humedad, luz) afectan el cultivo in vitro. Hoy no hay vigilancia continua: una falla fuera del horario (minisplit, lámparas, puerta abierta) puede pasar desapercibida. Argos mide, registra, muestra y avisa. **No controla el clima**.

Rangos vigilados: **22–28 °C** y **40–60 % HR**; luz según fotoperiodo.

## 3. Cómo funciona (en lenguaje simple)

1. **5 nodos sensores** repartidos en el cuarto, cada uno con su sensor:
   - Temperatura y humedad (con buzzer, botón y pantalla OLED)
   - Luz (fotoperiodo)
   - Movimiento (entrada)
   - Puerta abierta/cerrada
   - Golpes/vibración en el anaquel
2. Los nodos envían datos por WiFi a un servidor.
3. El servidor guarda el historial, evalúa alertas y las manda por **WhatsApp y Telegram**.
4. Un **dashboard web** muestra el estado en vivo y las gráficas.
5. En el cuarto: **LED verde** (todo bien), **LED rojo** (alerta) y un **buzzer** que suena ante alarma de temperatura/humedad (se silencia 30 min con un botón).

## 4. Públicos

- **Usuarios finales:** encargados del invernadero (Ing. Enrique Puga, Dr. Luis Ricardo Salgado Garza). Perfil técnico-agrícola, no necesariamente de TI. Necesitan leer el estado de un vistazo.
- **Evaluadores:** profesores del curso TC1004B (contexto académico).
- **Equipo:** 5 integrantes, un nodo cada uno.

## 5. Dónde se aplicará la identidad

| Soporte | Notas |
|---|---|
| **Logotipo / isotipo** | Debe funcionar pequeño (favicon, avatar de Telegram/WhatsApp) y grabado/rotulado en piezas. |
| **Dashboard web** | Interfaz HTML + Chart.js. Necesita paleta con **estados semánticos**: OK / alerta / sin conexión / sin datos. Modo claro (oscuro opcional). |
| **Carcasas 3D impresas** | 3 cajas en PETG, estaciones horizontales de 174 × 80 mm. Rotulado/relieve de nombre y de cada par de LED por sensor. Impresión en un solo color por pieza: el logo debe ser legible en **relieve monocromo**. |
| **Pantalla OLED** (2.42", monocroma) | Posible pantalla de inicio con el logo en 1 bit. |
| **Mensajes de alerta** | WhatsApp/Telegram: texto, posible icono por tipo de alerta. |
| **Documentos y presentación** | Portada, diapositivas, reporte académico (Times New Roman, APA 7; la identidad no sustituye ese formato en los entregables formales). |
| **Etiquetas** | Rótulos de nodos: `dht`, `luz`, `pir`, `puerta`, `acel`. |

## 6. Restricciones reales (importantes para el diseño)

- **Colores con significado ya fijado por el hardware:** LED **verde = OK**, LED **rojo = alerta**. La paleta del dashboard debería ser coherente con eso (verde/rojo como estados), evitando que el color de marca los confunda.
- **Monocromo obligatorio:** versión del logo en 1 color y en 1 bit (OLED e impresión 3D).
- **Sin PCB ni producción industrial:** todo es prototipo funcional en protoboard y cajas impresas.
- **Entorno:** cuarto de incubación con luz de lámparas; las piezas se ven a ~2 m. Prioridad: legibilidad y contraste.
- **Presupuesto:** hardware extra ≤ $1,500 MXN; usar herramientas y tipografías **gratuitas** (p. ej. Google Fonts).
- **Idioma:** español en todo el texto visible.

## 7. Tono y personalidad (propuesta, a validar con el equipo)

Vigilante, confiable, sereno; técnico pero accesible; "alerta sin alarmismo". Debe transmitir **cuidado del cultivo** (lo vivo/agrícola) y **precisión tecnológica** (sensores/datos) a la vez.

## 8. Entregables sugeridos al diseñador

1. Logotipo (principal, horizontal, isotipo) en color, 1 color y 1 bit.
2. Paleta de color con estados semánticos (OK / alerta / sin conexión) y neutros.
3. Tipografías (títulos + texto + numérica/monoespaciada para lecturas).
4. Set de iconos: temperatura, humedad, luz, movimiento, puerta, golpe, alerta, silencio, nodo sin conexión.
5. Lineamientos mínimos de uso (1 página).
6. Plantilla de portada/diapositiva y avatar para Telegram/WhatsApp.

## 9. Datos del proyecto

- Nombre: **Argos** (antes IncuMonitor)
- Curso/grupo: TC1004B · G507 · Tec de Monterrey
- Líder de proyecto: Luis Eduardo Mendoza Menéndez
- Integrantes y nodos: José María García (`dht`), Arianna Téllez (`luz`), Luis Mendoza (`pir`), Iván Acosta (`puerta`), Mía Nieto (`acel`)
