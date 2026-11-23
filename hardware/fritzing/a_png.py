"""Convierte los SVG que exporta Fritzing a PNG con Edge sin ventana (150 px por pulgada, fondo blanco).

Uso: python hardware/fritzing/a_png.py [archivo.svg ...]   (por omisión, todos los de salida/ menos los de PCB)
"""
import re
import subprocess
import sys
from pathlib import Path

EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
SALIDA = Path(__file__).resolve().parent / "salida"
DPI = 150


def a_png(svg):
    txt = svg.read_text(encoding="utf-8", errors="ignore")[:800]
    # CD-548 usa comillas simples; Fritzing 1.0.x, dobles
    w = float(re.search(r"""width=['"]([\d.]+)in['"]""", txt)[1]) * DPI
    h = float(re.search(r"""height=['"]([\d.]+)in['"]""", txt)[1]) * DPI
    pagina = svg.with_suffix(".html")
    pagina.write_text(f'<html><body style="margin:0;background:#fff"><img src="{svg.name}" '
                      f'style="width:{w:.0f}px;height:{h:.0f}px;display:block"></body></html>', encoding="utf-8")
    png = svg.with_suffix(".png")
    subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--hide-scrollbars", f"--screenshot={png}",
                    f"--window-size={w:.0f},{h:.0f}", pagina.as_uri()], check=True, capture_output=True, timeout=120)
    pagina.unlink()
    return png


def mosaico(pngs, salida, columnas=2, margen=40):
    """Une varias vistas en una sola imagen (rejilla), para usarla como una figura del reporte."""
    from PIL import Image
    imgs = [Image.open(p).convert("RGB") for p in pngs]
    w = max(i.width for i in imgs)
    h = max(i.height for i in imgs)
    filas = -(-len(imgs) // columnas)
    lienzo = Image.new("RGB", (columnas * w + (columnas - 1) * margen, filas * h + (filas - 1) * margen), "white")
    for n, im in enumerate(imgs):
        f, c = divmod(n, columnas)
        lienzo.paste(im, (c * (w + margen) + (w - im.width) // 2, f * (h + margen) + (h - im.height) // 2))
    lienzo.save(salida)
    return salida


if __name__ == "__main__":
    archivos = [Path(a) for a in sys.argv[1:]] or [p for p in SALIDA.glob("*.svg") if not p.stem.endswith("_pcb")]
    for s in archivos:
        print("ok", a_png(s.resolve()).name)
