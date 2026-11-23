"""Montaje 3D de las tres cajas para el navegador (three.js): exporta la geometria real de las cajas, el gemelo de
las piezas compradas y el cableado de layouts.py, y arma presentacion/montaje_3d.html desde su plantilla.

  uv run --no-project --python 3.12 --with "build123d>=0.10,<0.14" --with matplotlib python cad/montaje_web.py

La caja dht sale en su variante modular y las estaciones en capsula (ARGOS_CAPSULA=1, que este script activa).
"""
import base64
import json
import os
import struct

os.environ["ARGOS_CAPSULA"] = "1"
import nodos  # noqa: E402
from nodos import DIS, layouts, med  # noqa: E402

RAIZ = nodos.RAIZ.parent
PLANTILLA = RAIZ / "presentacion" / "montaje" / "plantilla.html"
SALIDA = RAIZ / "presentacion" / "montaje_3d.html"
ESC = 50.0   # enteros de 0.02 mm


def malla(s):
    """Triangulos de un solido como base64: vertices int16 (x, y, z en pasos de 0.02 mm) e indices uint32."""
    verts, tris = s.tessellate(0.12, 0.45)
    v = struct.pack(f"<{len(verts) * 3}h", *[int(round(c * ESC)) for p in verts for c in (p.X, p.Y, p.Z)])
    i = struct.pack(f"<{len(tris) * 3}I", *[k for t in tris for k in t])
    return {"v": base64.b64encode(v).decode(), "i": base64.b64encode(i).decode(), "n": len(tris)}


def caja_de(s):
    bb = s.bounding_box()
    return [round(c, 2) for c in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)]


def exportar(clave, fn, titulo):
    d = fn()
    lay = layouts.LAYOUTS[layouts.CAJAS[clave]["layout"]]
    giro = clave != "dht"
    p = DIS["pared"]
    cols = layouts.columnas(lay)
    largo = med("protoboard_nodo_propuesta" if cols == 30 else "protoboard_kit", "dimensiones")[0]
    pb = nodos.Protoboard(d["y_pb_inf"] + largo, p, cols)
    W, H = d["W"], d["H"]

    def xy(h):
        x, y = pb.xy(h)
        return [round(W / 2 - y, 2), round(H / 2 + x, 2)] if giro else [round(x, 2), round(y, 2)]

    partes = {nom: {"b": caja_de(s)} for nom, (s, _) in d["gemelo"].partes.items()}
    prefijos = [m["nombre"].split("_", 1)[1] if "_" in m["nombre"] else "" for m in layouts.placas(lay)]
    puentes = [{"de": c["de"], "a": c["a"], "p": xy(c["de"]), "q": xy(c["a"]), "color": c["color"], "nota": c["nota"]}
               for c in lay["puentes"]]
    externos = [{"disp": e["disp"], "pin": e["pin"], "h": e["orificio"], "p": xy(e["orificio"]), "color": e["color"],
                 "nota": e.get("nota", ""), "largo": e.get("largo", "")} for e in lay["externos"]]
    comps = [{"ref": c["ref"], "tipo": c["tipo"], "valor": c["valor"], "pines": c["pines"], "nota": c.get("nota", "")}
             for c in lay["componentes"]]
    piezas = {"base": malla(d["piezas"]["base"]), "tapa": malla(d["piezas"]["tapa"])}
    for extra in ("grapa_oled", "embolo_boton"):
        s = d["piezas"].get(extra) or d["montaje"].get(extra)
        if s is not None:
            piezas[extra] = malla(s)
    return {"titulo": titulo, "W": round(W, 2), "H": round(H, 2), "D": d["D"], "Db": d["Db"], "giro": giro,
            "z_pb": round(pb.z_sup, 2), "prefijos": prefijos, "nodos": list(layouts.CAJAS[clave]["nodos"]),
            "partes": partes, "puentes": puentes, "externos": externos, "comps": comps, "piezas": piezas,
            "intro": lay["intro"]}


if __name__ == "__main__":
    datos = {"dht": exportar("dht", nodos.nodo_dht, "Caja dht"),
             "entrada": exportar("entrada", nodos.estacion_entrada, "Estación de entrada"),
             "anaquel": exportar("anaquel", nodos.estacion_anaquel, "Estación del anaquel")}
    js = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    (RAIZ / "presentacion" / "montaje").mkdir(parents=True, exist_ok=True)
    (RAIZ / "presentacion" / "montaje" / "datos.json").write_text(js, encoding="utf-8")
    print("datos:", round(len(js) / 1024), "KB;",
          {k: {n: m["n"] for n, m in v["piezas"].items()} for k, v in datos.items()})
    if PLANTILLA.exists():
        html = PLANTILLA.read_text(encoding="utf-8").replace("/*__DATOS__*/null", js)
        SALIDA.write_text(html, encoding="utf-8")
        print("escrito", SALIDA, round(len(html) / 1024), "KB")
