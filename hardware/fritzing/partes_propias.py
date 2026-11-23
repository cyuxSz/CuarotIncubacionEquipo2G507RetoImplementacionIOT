"""Partes de Fritzing que no existen en la biblioteca: OLED 2.42" SSD1309 y 0.91" SSD1306 I²C de 4 pines, y GY-61 (ADXL335).

Se dibujan como módulos genéricos con sus pines a 0.1" y la serigrafía del orden que usa layouts.py
([orden de pines POR CONFIRMAR con la pieza real]). Escribe fzp + SVG en hardware/fritzing/partes/.
"""
from pathlib import Path

PARTES = Path(__file__).parent / "partes"

MODULOS = {
    # 19-nov: modulo real ZJY_M242 de 7 pines, en SPI. Orden de la tira leido de la foto de la pieza.
    "argos_oled_242": dict(titulo='OLED 2.42" SSD1309 SPI', etiqueta="OLED", pines=["CS", "DC", "RES", "SDA", "SCL", "VCC", "GND"],
                           ancho=2.4, alto=1.45, color="#1f4f8f", pantalla=True,
                           desc='Pantalla OLED 2.42" 128×64 SSD1309, módulo ZJY_M242 de 7 pines en SPI (Argos, nodo dht).'),
    "argos_oled_091": dict(titulo='OLED 0.91" SSD1306 I²C', etiqueta="OLED", pines=["GND", "VCC", "SCL", "SDA"],
                           ancho=1.5, alto=0.75, color="#1f4f8f", pantalla=True, texto="SSD1306 128×32",
                           desc='Pantalla OLED 0.91" 128×32 SSD1306 I²C de 4 pines, Steren ARD-384 (Argos, nodo dht; adoptada el 18-nov-2026).'),
    "argos_gy61": dict(titulo="GY-61 (ADXL335)", etiqueta="GY-61", pines=["VCC", "X", "Y", "Z", "GND"],
                       ancho=0.7, alto=0.5, color="#5b2c83", pantalla=False,
                       desc="Acelerómetro analógico de 3 ejes GY-61 con ADXL335 (Argos, nodo acel)."),
}


def _svg(ancho, alto, cuerpo):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" version="1.2" '
            f'width="{ancho}in" height="{alto}in" viewBox="0 0 {ancho * 1000:g} {alto * 1000:g}">\n{cuerpo}\n</svg>\n')


def _protoboard(m):
    w, h, n = m["ancho"], m["alto"], len(m["pines"])
    x0 = (w * 1000 - (n - 1) * 100) / 2
    g = [f'<rect x="0" y="0" width="{w * 1000:g}" height="{h * 1000:g}" rx="60" fill="{m["color"]}" stroke="#222" stroke-width="10"/>']
    if m["pantalla"]:
        g.append(f'<rect x="120" y="150" width="{w * 1000 - 240:g}" height="{h * 1000 - (300 if m["ancho"] < 2 else 420):g}" fill="#0b0b12" stroke="#555" stroke-width="10"/>')
        g.append(f'<text x="{w * 500:g}" y="{h * 500 - 60:g}" fill="#7fb3ff" font-family="Droid Sans, sans-serif" font-size="{80 if m["ancho"] < 2 else 120}" text-anchor="middle">{m.get("texto", "SSD1309 128×64")}</text>')
    else:
        g.append(f'<rect x="{w * 500 - 110:g}" y="180" width="220" height="220" fill="#111" stroke="#666" stroke-width="10"/>')
        g.append(f'<text x="{w * 500:g}" y="140" fill="#fff" font-family="Droid Sans, sans-serif" font-size="90" text-anchor="middle">{m["etiqueta"]}</text>')
    for i, p in enumerate(m["pines"]):
        x = x0 + i * 100
        g.append(f'<text x="{x:g}" y="{h * 1000 - 130:g}" fill="#fff" font-family="Droid Sans, sans-serif" font-size="55" text-anchor="middle">{p}</text>')
        g.append(f'<rect id="connector{i}pin" x="{x - 30:g}" y="{h * 1000 - 90:g}" width="60" height="60" fill="#d4af37" stroke="#8a6d1f" stroke-width="8"/>')
    return _svg(w, h, '<g id="breadboard">\n' + "\n".join(g) + "\n</g>")


def _esquematico(m):
    n = len(m["pines"])
    w, h = 1.0, 0.2 + 0.1 * n + 0.2
    g = [f'<rect x="300" y="50" width="600" height="{h * 1000 - 100:g}" fill="#fff" stroke="#000" stroke-width="10"/>',
         f'<text x="600" y="{h * 1000 - 70:g}" font-family="Droid Sans, sans-serif" font-size="70" text-anchor="middle">{m["etiqueta"]}</text>']
    for i, p in enumerate(m["pines"]):
        y = 200 + i * 100
        g.append(f'<line id="connector{i}pin" x1="0" y1="{y}" x2="300" y2="{y}" stroke="#000" stroke-width="10"/>')
        g.append(f'<rect id="connector{i}terminal" x="0" y="{y - 5}" width="10" height="10" fill="none"/>')
        g.append(f'<text x="330" y="{y + 25}" font-family="Droid Sans, sans-serif" font-size="70">{p}</text>')
    return _svg(w, h, '<g id="schematic">\n' + "\n".join(g) + "\n</g>")


def _pcb(m):
    n = len(m["pines"])
    w = 0.1 * n + 0.1
    circ = "\n".join(f'<circle id="connector{i}pad" cx="{100 + i * 100}" cy="100" r="35" fill="none" stroke="#f7bd13" stroke-width="20"/>'
                     for i in range(n))
    return _svg(w, 0.2, f'<g id="copper1"><g id="copper0">\n{circ}\n</g></g>')


def _fzp(clave, m):
    con = []
    for i, p in enumerate(m["pines"]):
        con.append(f'''  <connector id="connector{i}" name="{p}" type="male">
   <description>{p}</description>
   <views>
    <breadboardView><p layer="breadboard" svgId="connector{i}pin"/></breadboardView>
    <schematicView><p layer="schematic" svgId="connector{i}pin" terminalId="connector{i}terminal"/></schematicView>
    <pcbView><p layer="copper0" svgId="connector{i}pad"/><p layer="copper1" svgId="connector{i}pad"/></pcbView>
   </views>
  </connector>''')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<module fritzingVersion="0.9.4" moduleId="{clave}">
 <version>1</version>
 <author>Argos (Equipo G507)</author>
 <title>{m["titulo"]}</title>
 <label>U</label>
 <date>2026-10-23</date>
 <tags><tag>Argos</tag></tags>
 <properties>
  <property name="family">Argos</property>
  <property name="variant">{m["etiqueta"]}</property>
 </properties>
 <description>{m["desc"]} Orden de pines POR CONFIRMAR con la pieza real.</description>
 <views>
  <iconView><layers image="icon/{clave}_breadboard.svg"><layer layerId="icon"/></layers></iconView>
  <breadboardView><layers image="breadboard/{clave}_breadboard.svg"><layer layerId="breadboard"/></layers></breadboardView>
  <schematicView><layers image="schematic/{clave}_schematic.svg"><layer layerId="schematic"/></layers></schematicView>
  <pcbView><layers image="pcb/{clave}_pcb.svg"><layer layerId="copper0"/><layer layerId="copper1"/></layers></pcbView>
 </views>
 <connectors>
{chr(10).join(con)}
 </connectors>
</module>
'''


def escribir():
    for clave, m in MODULOS.items():
        for vista, txt in [("breadboard", _protoboard(m)), ("schematic", _esquematico(m)), ("pcb", _pcb(m))]:
            d = PARTES / "svg" / vista
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{clave}_{vista}.svg").write_text(txt, encoding="utf-8")
        icono = PARTES / "svg" / "icon"
        icono.mkdir(parents=True, exist_ok=True)
        (icono / f"{clave}_breadboard.svg").write_text(_protoboard(m).replace('id="breadboard"', 'id="icon"'), encoding="utf-8")
        (PARTES / f"{clave}.fzp").write_text(_fzp(clave, m), encoding="utf-8")


if __name__ == "__main__":
    escribir()
    print("ok", ", ".join(MODULOS))
