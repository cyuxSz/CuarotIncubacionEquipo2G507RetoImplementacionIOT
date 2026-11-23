"""Genera los prompts de armado para herramientas de IA de protoboard (constructa.io, Tinkercad u otras).

Salen de layouts.py, igual que los dibujos y el WireViz: el prompt describe orificio por orificio
la misma distribucion verificada. Uso (desde la raiz):
    python hardware/breadboard/prompts.py
Salida: docs/prompts_armado.md
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import layouts  # noqa: E402

NODOS = [(c["layout"], caja) for caja, c in layouts.CAJAS.items()]
RIEL = {"A_5V": "riel superior interior (+5V)", "A_GND": "riel superior exterior (GND)",
        "J_3V3": "riel inferior exterior, linea roja (+3.3V)", "J_GND": "riel inferior interior, linea azul (GND)"}
MODULOS = {
    "OLED": "pantalla OLED 2.42\" SSD1309 de 7 pines en SPI (CS, DC, RES, SDA, SCL, VCC, GND)",
    "DHT22": "sensor DHT22 de 3 pines (VCC, DATA, GND)",
    "Buzzer": "buzzer activo KY-012 de 5 V (+, -)",
    "Boton": "pulsador táctil de 6x6 mm",
    "LED_V": "LED verde de 5 mm", "LED_R": "LED rojo de 5 mm",
    "LDR": "fotorresistencia (LDR) de 5 mm",
    "PIR": "sensor de movimiento HC-SR501 (VCC, OUT, GND)",
    "Reed": "sensor magnético de puerta MC-38 (2 cables)",
    "Entrada5V": "módulo de entrada USB-C a terminales (+5V, GND)",
}


def modulo_desc(d):
    return MODULOS.get(d) or MODULOS.get(d.split("_", 1)[-1], d)


def orificio(h):
    if ":" in h:
        riel, col = h.split(":")
        return f"{RIEL[riel]}, junto a la columna {col}"
    return f"{h[0]}{h[1:]}"


def bloque(clave, nodo):
    lay = layouts.LAYOUTS[clave]
    cols, puntos = layouts.columnas(lay), layouts.puntos(lay)
    L = [f"### `{nodo}`: {lay['titulo']}", "", "```text",
         f"Dibuja en una protoboard de {puntos} puntos el circuito '{nodo}' EXACTAMENTE como se describe.",
         "No agregues, quites ni muevas componentes. No cambies pines ni valores.", "",
         f"PROTOBOARD: {puntos} puntos, {cols} columnas (1 a {cols}) y filas a-e / f-j separadas por el canal central.",
         "Rieles: arriba (junto a la fila a) interior = +5V, exterior = GND.",
         "        abajo (junto a la fila j) interior = GND, exterior = +3.3V (sigue las líneas impresas: roja = +, azul = GND)."]
    if lay.get("rieles_partidos"):
        L.append(f"Los 4 rieles están PARTIDOS entre las columnas {lay['rieles_partidos'] - 1} y "
                 f"{lay['rieles_partidos']}. 5V y GND se unen con puentes; el de 3.3V NO se une (cada placa "
                 "tiene su propio 3.3V).")
    L.append("")
    lado_a = ", ".join(layouts.NODEMCU_LADO_A[c] for c in sorted(layouts.NODEMCU_LADO_A))
    lado_j = ", ".join(layouts.NODEMCU_LADO_J[c] for c in sorted(layouts.NODEMCU_LADO_J))
    for m in layouts.placas(lay):
        c0 = m["col0"]
        L += [f"PLACA {m['nombre']}: NodeMCU v1.0 Amica (ESP8266), clavada en las columnas {c0}-{c0 + 14}, "
              f"puerto micro-USB hacia la columna {c0}.",
              f"  Fila b (col. {c0} a {c0 + 14}): {lado_a}.",
              f"  Fila i (col. {c0} a {c0 + 14}): {lado_j}."]
    L += ["", "COMPONENTES EN LA PROTOBOARD:"]
    for c in lay["componentes"]:
        pines = "; ".join(f"pin {p} en {orificio(h)}" for p, h in c["pines"].items())
        L.append(f"  - {c['ref']} ({c['valor']}): {pines}. {c.get('nota', '').replace('**', '')}".rstrip())
    L += ["", "PUENTES (cable corto rígido, color indicado):"]
    for p in lay["puentes"]:
        L.append(f"  - de {orificio(p['de'])} a {orificio(p['a'])}, color {p['color']} ({p['nota']}).")
    if lay["externos"]:
        L += ["", "MÓDULOS FUERA DE LA PROTOBOARD (cable Dupont macho-hembra desde el orificio indicado):"]
        vistos = []
        for e in lay["externos"]:
            if e["disp"] not in vistos:
                vistos.append(e["disp"])
        for d in vistos:
            pines = [e for e in lay["externos"] if e["disp"] == d]
            con = "; ".join(f"{e['pin']} ← {orificio(e['orificio'])} (cable {e['color']})" for e in pines)
            L.append(f"  - {modulo_desc(d)}: {con}.")
    L += ["", "REDES QUE DEBEN QUEDAR CONECTADAS (para verificar):"]
    for nombre, miembros in lay["redes"].items():
        L.append(f"  - {nombre}: {', '.join(sorted(miembros))}")
    L += ["```", ""]
    return "\n".join(L)


def main():
    L = ["# Prompts de armado en protoboard (constructa.io, Tinkercad u otras herramientas con IA)", "",
         "Generado por `hardware/breadboard/prompts.py` desde `layouts.py`: es la misma distribución verificada "
         "de los dibujos `hardware/breadboard/nodo_<id>_protoboard.png` y del WireViz. Si cambias `layouts.py`, "
         "vuelve a generarlo.", "",
         "## Cómo usarlos", "",
         "1. Copia el bloque de **una** caja completa (el `dht` o una estación) y pégalo en la herramienta. Una caja "
         "por conversación funciona mejor que todas juntas.",
         "2. Compara el resultado con `hardware/breadboard/nodo_<id>_protoboard.png` y la sección *Redes* del bloque. "
         "Si la herramienta movió algo, pídele que lo corrija citando el orificio exacto.",
         "3. **No sustituyas componentes** para que el dibujo \"funcione\": el armado real usa estas piezas.", "",
         "> **Limitaciones que no pude verificar.** No encontré documentación pública de constructa.io ni de una "
         "función de IA en Tinkercad que genere circuitos desde texto. Hasta donde sé, Tinkercad Circuits **no "
         "incluye** el NodeMCU (ESP8266), la OLED I²C, el ADS1115 ni el DHT22. Si la herramienta no tiene una "
         "pieza, el dibujo no será fiel: en ese caso usa como referencia los dibujos de protoboard de este "
         "proyecto, que ya están orificio por orificio.", "",
         "## Prompt general (pegar antes de cualquier nodo si la herramienta lo permite)", "",
         "```text",
         "Vas a dibujar circuitos para armar físicamente en protoboard. Respeta al pie de la letra las coordenadas "
         "de orificio (columna 1-30, fila a-j o riel), los valores y los colores de cable. Si te falta una pieza "
         "en tu biblioteca, dímelo en lugar de sustituirla. Todos los GPIO son de 3.3 V; nada que entre a un "
         "GPIO puede ser de 5 V.",
         "```", ""]
    for clave, nodo in NODOS:
        L.append(bloque(clave, nodo))
    destino = AQUI.parent.parent / "docs" / "prompts_armado.md"
    destino.write_text("\n".join(L), encoding="utf-8")
    print("ok", destino)


if __name__ == "__main__":
    main()
