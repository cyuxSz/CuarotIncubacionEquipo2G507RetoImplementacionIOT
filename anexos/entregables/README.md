# Entregables del 21-oct-2026 (actualizados el 22-oct)

Salida en `OneDrive/Escritorio/Entregables 21-10 IoT/` (docx + pdf + `diagramas_interactivos/`).

| Archivo | Qué es |
|---|---|
| `Etapa2SoftwareBD_v2.docx` | Etapa 2 software (BD) corregida con `docs/bd/etapa2_software_v2.md`: 13 clases (Caja), 6 actuadores, origen de AccionControl, flujo MQTT → BD, Anexo A de cambios |
| `Argos_Como_funciona.docx` | Reporte libre: funcionamiento, hardware de 3 cajas, reutilización del kit, fuentes, Web API, alternativas a la impresión 3D, presupuesto con precios de tiendas (≈ $1,650) |
| `Argos_Prototipo.docx` | Reporte libre: versiones v0–v3 del prototipo, alternativas a la impresión 3D, cajas, cortes, piezas externas, comportamiento del dht, circuitos, ubicación, aprobaciones |
| `Avance2_Hardware_Comunicaciones_Energia.docx` | Avance 2 de hardware (REQ-A2-01 a 07), `entregable4.py`: matriz de nodos, eléctrica, protocolos y MQTT, actuación, presupuesto energético por ciclo, pruebas V-01 a V-06 y plan P-01 a P-09, participación individual (las de los otros 4 integrantes van como borrador `[POR CONFIRMAR]`). Diagrama nuevo `archify/topologia.json`; prueba MQTT con broker local en `pruebas/` |

Formato: TNR 12, 1.5, sangría 0.5", justificado, APA 7 (tablas/figuras numeradas, referencias abiertas sin login, verificadas el 21-oct).

## Regenerar

Los scripts esperan, en el directorio de trabajo, `media/` (imágenes del docx original: `fig/image*.png`), `fig/uml.png` y `cap/*_fig.png` (aquí en `fig/`); ajustar rutas si se corren desde esta carpeta.

```bash
uv run --no-project --python 3.12 --with python-docx python entregable1.py salida.docx
```

Diagramas: `fig/uml.py` (Graphviz, Figura 1 del UML) y `archify/*.json` (Archify 3.2.0, `node bin/archify.mjs finalize <tipo> <json> <html> --quality showcase`). `recorta.py` recorta las capturas de Edge headless.
