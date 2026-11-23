# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Vite + JavaScript sin framework (decisión de Iván, 22-nov-2026). Chart.js para las gráficas. Fuentes y librerías empaquetadas en el proyecto: nada de CDN. La salida `dist/` se copia a `servidor/web`, que el servicio central (`servidor/central/central.js`, Express, puerto 3000) sirve como estáticos. Se expone con un túnel rápido de Cloudflare; página y datos comparten origen.

## Users

Dos públicos con el mismo peso (confirmado por Iván):

- **Encargados del Invernadero Académico** (Ing. Enrique Puga; Dr. Luis Ricardo Salgado Garza). Perfil técnico-agrícola, no de TI. Revisan desde el celular si el cuarto de incubación está bien y qué pasó mientras no había nadie.
- **Jurado y visitantes de Expo Ingenierías** (1-dic-2026). Lo ven en una pantalla grande a unos 2 m y en su celular, junto al póster del equipo.

## Product Purpose

Argos vigila el cuarto de incubación in vitro con 5 nodos NodeMCU (dht, luz, pir, puerta, acel) y avisa cuando algo sale de rango. El dashboard muestra el estado actual de los 5 nodos, la temperatura y la humedad contra sus rangos, las alertas activas, el estado de la alarma y el historial. Éxito: saber en un vistazo si el cuarto está bien, y si no, qué falla y desde cuándo.

## Positioning

Solo monitorea, no controla el clima. Una alerta por episodio, sin saturar el chat.

## Operating Context

- El hardware se queda instalado en el invernadero; en la Expo se muestran imágenes y este dashboard.
- Los datos llegan de `GET /panel/datos?horas=N` (sin clave, caché de 2 s): nodos, últimos valores, umbrales, alertas, eventos y series. Sondeo cada pocos segundos; MQTT en vivo es mejora opcional.
- La base guarda fechas en UTC; todo se muestra en `America/Monterrey`.
- El servidor está en el Tec y solo entra José María García; cada cambio al central se le entrega a él.
- No se sabe si el WiFi del invernadero tiene internet [POR CONFIRMAR].

## Capabilities and Constraints

- Orden fijo de los nodos en todo: dht, luz, pir, puerta, acel.
- Rangos de alerta: 22–28 °C y 40–60 % HR (vienen de la tabla `Umbral`; en modo demo pueden cambiar a 15–30 °C y 20–80 % HR [POR CONFIRMAR]). El dashboard muestra los que entregue el servidor.
- Nodo «sin conexión» a los 150 s sin reporte (`sin_reporte_s`).
- Ver es libre, sin login. Las acciones de control (silenciar alarma, cambiar umbrales) pedirán una cuenta admin real con sesión por cookie; todavía no existen en el central.
- Mínimo para entregar: pantalla principal e historial. Alertas por episodio, umbrales y login, solo si da tiempo.
- Fecha de entrega del dashboard [POR CONFIRMAR].

## Brand Commitments

- Nombre: Argos. Equipo 2 · G507 · TC1004B · Tec de Monterrey.
- El póster `Argos_Poster_B_ventanas.pdf` es el brandbook y es vinculante: cabecera casi negra `#121212`, cuerpo crema `#F4F4F0`, tarjetas con aspecto de ventana y sombra dura, acento azul `#2F4FD8`, etiquetas en monoespaciada, logo del ojo con pupila cuadrada y 3 rayos. Fuentes: Space Grotesk, Inter, JetBrains Mono.
- Semánticos fijos por el hardware: verde `#10B981` en rango, rojo `#EF4444` alerta, gris o ámbar sin conexión, y un estado «sin datos». Verde y rojo nunca son decoración; cada estado lleva además forma o texto.
- Todo el texto visible en español; identificadores en ASCII.
- Tono: vigilante, sereno, «alerta sin alarmismo».

## Evidence on Hand

- Panel anterior: `servidor/web/index.html` (consume `/panel/datos`).
- Simulador de los 5 nodos: `servidor/simulador_nodos.mjs`.
- No hay datos reales de luz, pir, puerta ni acel todavía: solo el nodo dht está probado con hardware.

## Product Principles

1. El estado se lee en un vistazo, a 2 m y en un celular.
2. Nunca se inventa un dato: lo que no llega se muestra como «sin datos» o «sin conexión».
3. El color nunca va solo: cada estado lleva forma o texto.
4. Sereno cuando todo está bien; inconfundible cuando algo falla.

## Accessibility & Inclusion

Alto contraste, legible a distancia, usable a 375 px, tema claro y oscuro, respeto a `prefers-reduced-motion`.
