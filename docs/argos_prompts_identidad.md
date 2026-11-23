# Argos — prompts de identidad y brandbook mínimo

## 1. Prompt: logotipo (isotipo 1-bit)

```
Minimalist 1-bit monochrome icon, pure black on pure white, no gray, no gradients,
no anti-aliasing. A pixelated eye built on a 16x16 grid of square pixels: almond-shaped
outline, a solid 4x4 pixel pupil, and a single row of 3 pixels above as an eyelash.
Inside the pupil, one white pixel as a highlight. Thick uniform strokes (minimum 2 pixels),
perfectly symmetrical, centered, generous margin. Flat vector look, hard pixel edges,
readable at 32 px and at 128x64 OLED resolution, and suitable for 3D-printed relief
(no details thinner than 1.2 mm at 40 mm width). No text, no color, no shadows.
Style: technical, utilitarian, bitmap/terminal aesthetic.
```

Variantes: radar (tres arcos de píxeles saliendo de un punto) o escudo pixelado con un punto central.

## 2. Prompt: avatar Telegram / WhatsApp

```
Circular avatar, 1024x1024, solid charcoal background (#121212). Centered pixel-art eye
icon (1-bit style, square pixels, hard edges) in bright off-white (#F8F9FA), occupying
about 60% of the circle's diameter, with a thin 2-pixel off-white ring near the edge.
Maximum contrast, no gradients, no gray, no text. Do NOT use green or red anywhere
(reserved for sensor status). Must stay recognizable at 48x48 px in a notification list.
```

## 3. Brandbook mínimo (1 página)

**Argos — lineamientos mínimos**

**Idea.** Sistema de monitoreo y aviso. Estética de terminal estructurada: bordes sólidos de 2 px, retícula sutil, ventanas con barra de título, acentos de píxel y líneas de conexión.

**Color**
| Uso | Valor |
|---|---|
| Fondo oscuro | `#121212` |
| Fondo claro (hueso) | `#F4F4F0` |
| Texto sobre oscuro | `#F8F9FA` |
| Texto sobre claro | `#111827` |
| Acento de marca (azul) | `#2F4FD8` / `#3B5BDB` |
| Acentos secundarios | cian `#22D3EE`, lila `#D8B4FE` |

**Colores semánticos (estrictos, no se alteran)**
- Verde `#10B981`: estado OK.
- Rojo `#EF4444`: alerta.
- Ámbar `#F59E0B` o gris `#6B7280`: nodo sin conexión.

Reglas:
1. Verde y rojo **nunca** se usan como decoración, ni en logo, avatar, fondos o gráficos de marca.
2. No se cambia su tono, ni se usan para otro significado.
3. Si dos estados deben distinguirse, además del color se diferencian por forma o texto.

**Tipografía.** Títulos: Space Grotesk. Cuerpo: Inter. Datos y lecturas: JetBrains Mono. Mínimo 22 px en diapositivas (lectura a 2 m).

**Íconos.** Trazo grueso (2.4–2.5 px en rejilla de 24), extremos redondeados: termómetro, gota, sol, ondas, puerta, bloque vibrando, campana tachada, wifi tachado.

**Logo.** Isotipo 1-bit (ojo pixelado). Versiones: negro sobre blanco o blanco sobre negro.

**Hardware (carcasas, rotulado, OLED).** Solo **blanco y negro**. Sin color en piezas impresas, etiquetas ni pantalla. El único color permitido en el hardware son los LED de estado (verde y rojo), con su significado fijo.

**Avatar.** Fondo `#121212`, trazo `#F8F9FA`, sin verde ni rojo.
