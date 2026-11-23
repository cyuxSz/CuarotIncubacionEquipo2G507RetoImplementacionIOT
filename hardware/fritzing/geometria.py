"""Lee la posición de los conectores de una parte de Fritzing (fzp + svg) en unidades de escena (90 px/in)."""
import re
from pathlib import Path

from svgelements import SVG, Shape, Group, SimpleLine

DPI = 90.0


def _sin_uso_en_pulgadas(valor, defecto):
    m = re.match(r"\s*([\d.]+)\s*([a-z%]*)", valor or "")
    if not m:
        return defecto
    n, u = float(m[1]), m[2]
    return {"in": n, "mm": n / 25.4, "cm": n / 2.54, "pt": n / 72, "px": n / 90, "": n / 90}.get(u, defecto)


def leer_svg(ruta):
    """Devuelve (ancho, alto, {id: (x, y, ancho, alto)}) en px de escena (90 por pulgada)."""
    texto = Path(ruta).read_text(encoding="utf-8", errors="replace")
    raiz = re.search(r"<svg[^>]*>", texto, re.S)[0]
    w = re.search(r'\swidth="([^"]*)"', raiz)
    sin_unidad = w is None or re.fullmatch(r"[\d.]+(px)?", w[1].strip())
    # Fritzing lee los SVG sin unidades de Illustrator a 72 dpi y los demas a 90 dpi
    k = 90 / 72 if sin_unidad and "Illustrator" in texto[:600] else 1.0
    doc = SVG.parse(ruta, reify=True, ppi=DPI)
    cajas, lineas = {}, {}
    leer_svg.lineas = lineas
    for el in doc.elements():
        i = el.values.get("id") if hasattr(el, "values") else None
        if not i or not isinstance(el, (Shape, Group)):
            continue
        bb = el.bbox()
        if bb is None:
            continue
        x0, y0, x1, y1 = bb
        cajas[i] = (x0 * k, y0 * k, (x1 - x0) * k, (y1 - y0) * k)
        if isinstance(el, SimpleLine):
            lineas[i] = (el.x1 * k, el.y1 * k, el.x2 * k, el.y2 * k)
    return doc.width * k, doc.height * k, cajas


def conectores(fzp, carpeta_svg, vista="breadboard"):
    """{connector_id: {'nombre', 'desc', 'x', 'y'}} con el punto de conexión (centro o terminal)."""
    t = Path(fzp).read_text(encoding="utf-8", errors="replace")
    img = re.search(rf"<{vista}View[^>]*>\s*<layers\s+image=\"([^\"]*)\"", t)[1]
    ancho, alto, cajas = leer_svg(Path(carpeta_svg) / img)
    out = {}
    for m in re.finditer(r"<connector\b([^>]*)>(.*?)</connector>", t, re.S):
        atr, cuerpo = m[1], m[2]
        cid = re.search(r'id="([^"]*)"', atr)[1]
        nombre = re.search(r'name="([^"]*)"', atr)[1]
        d = re.search(r"<description>([^<]*)", cuerpo)
        v = re.search(rf"<{vista}View>(.*?)</{vista}View>", cuerpo, re.S)
        if not v:
            continue
        p = re.search(r'<p [^>]*svgId="([^"]*)"[^>]*?(?:terminalId="([^"]*)")?[^>]*/?>', v[1])
        svgid, term = p[1], p[2]
        if not term:
            tm = re.search(r'terminalId="([^"]*)"', v[1])
            term = tm[1] if tm else None
        if svgid not in cajas:
            continue
        x, y, w, h = cajas[term] if term and term in cajas else cajas[svgid]
        out[cid] = {"nombre": nombre, "desc": d[1].strip() if d else "", "x": x + w / 2, "y": y + h / 2}
        leg = re.search(r'legId="([^"]*)"', v[1])
        if leg and leg[1] in leer_svg.lineas:
            # pata flexible: (x2, y2) es la base en el cuerpo y (x1, y1) la punta
            x1, y1, x2, y2 = leer_svg.lineas[leg[1]]
            out[cid].update(base=(x2, y2), punta=(x1, y1), x=x1, y=y1)
    return ancho, alto, out
