"""Formato común de los entregables (estética del docx Etapa2SoftwareBD, APA 7)."""
import re
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor

FUENTE = "Times New Roman"
AZUL = "9FC5E8"
GRIS = "808080"
INTEGRANTES = ["Luis Mendoza A01669847", "Arianna Téllez A00845027", "Mía Nieto A00845663",
               "Iván Acosta A00227979", "José María García A00843900"]


def _fuente(estilo, tam, negrita=None, cursiva=None):
    f = estilo.font
    f.name = FUENTE
    f.size = Pt(tam)
    f.color.rgb = RGBColor(0, 0, 0)
    if negrita is not None:
        f.bold = negrita
    if cursiva is not None:
        f.italic = cursiva
    rpr = estilo.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), FUENTE)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]


class Doc:
    def __init__(self):
        self.d = Document()
        self.nfig = 0
        self.ntab = 0
        s = self.d.sections[0]
        s.orientation = WD_ORIENT.PORTRAIT
        s.page_width, s.page_height = Inches(8.5), Inches(11)
        for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
            setattr(s, m, Inches(1))
        st = self.d.styles
        _fuente(st["Normal"], 12)
        pf = st["Normal"].paragraph_format
        pf.line_spacing = 1.5
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        for i, nombre in enumerate(["Heading 1", "Heading 2", "Heading 3"]):
            h = st[nombre]
            _fuente(h, 12, negrita=True, cursiva=(i == 2))
            h.paragraph_format.line_spacing = 1.5
            h.paragraph_format.space_before = Pt(12 if i == 0 else 6)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
            h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 else WD_ALIGN_PARAGRAPH.LEFT
        self._numeros_pagina()

    def _numeros_pagina(self):
        p = self.d.sections[0].header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run()
        for tipo, txt in (("begin", None), (None, "PAGE"), ("end", None)):
            if tipo:
                e = OxmlElement("w:fldChar")
                e.set(qn("w:fldCharType"), tipo)
            else:
                e = OxmlElement("w:instrText")
                e.set(qn("xml:space"), "preserve")
                e.text = txt
            r._r.append(e)

    # ---------- texto ----------
    def _runs(self, p, texto, tam=None):
        """Texto con **negrita**, *cursiva* y `código` (código en la misma fuente)."""
        for parte in re.split(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)", texto):
            if not parte:
                continue
            if parte.startswith("**"):
                r = p.add_run(parte[2:-2]); r.bold = True
            elif parte.startswith("*"):
                r = p.add_run(parte[1:-1]); r.italic = True
            elif parte.startswith("`"):
                r = p.add_run(parte[1:-1])
            else:
                r = p.add_run(parte)
            if tam:
                r.font.size = Pt(tam)
        return p

    def portada(self, titulo, subtitulo=None, logo=None, fecha="21 de octubre de 2026", curso=None):
        d = self.d
        if logo:
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(logo, width=Inches(5.0))
        for _ in range(2):
            d.add_paragraph()
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(titulo); r.bold = True; r.font.size = Pt(16)
        if subtitulo:
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(subtitulo)
        for _ in range(7):
            d.add_paragraph()
        lineas = INTEGRANTES + ([curso] if curso else []) + ["Tecnológico de Monterrey", fecha]
        for l in lineas:
            p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run(l)
        d.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def h1(self, t):
        h = self.d.add_heading(t, level=1)
        if getattr(self, "_salto_pendiente", False):
            h.paragraph_format.page_break_before = True
            self._salto_pendiente = False
        return h
    def h2(self, t): return self.d.add_heading(t, level=2)
    def h3(self, t): return self.d.add_heading(t, level=3)

    def p(self, texto, sangria=True, alin=WD_ALIGN_PARAGRAPH.JUSTIFY):
        par = self.d.add_paragraph()
        par.alignment = alin
        if sangria:
            par.paragraph_format.first_line_indent = Inches(0.5)
        return self._runs(par, texto)

    def regla(self, clave, texto):
        """Párrafo tipo RN1 con la clave en negritas y sangría izquierda."""
        par = self.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        par.paragraph_format.left_indent = Inches(0.5)
        par.paragraph_format.space_after = Pt(4)
        r = par.add_run(clave + " "); r.bold = True
        return self._runs(par, texto)

    def viñetas(self, items):
        for it in items:
            par = self.d.add_paragraph(style="List Bullet")
            par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            self._runs(par, it)

    # ---------- APA: tablas y figuras ----------
    def _titulo_apa(self, etiqueta, titulo):
        a = self.d.add_paragraph(); a.paragraph_format.keep_with_next = True
        a.paragraph_format.space_before = Pt(6)
        r = a.add_run(etiqueta); r.bold = True
        b = self.d.add_paragraph(); b.paragraph_format.keep_with_next = True
        r = b.add_run(titulo); r.italic = True

    def nota(self, texto):
        par = self.d.add_paragraph(); par.paragraph_format.space_after = Pt(8)
        par.paragraph_format.line_spacing = 1.0
        r = par.add_run("Nota. "); r.italic = True; r.font.size = Pt(10)
        self._runs(par, texto, tam=10)

    def tabla(self, titulo, filas, anchos=None, nota=None, primera_negrita=True, tam=10.5):
        self.ntab += 1
        self._titulo_apa(f"Tabla {self.ntab}", titulo)
        t = self.d.add_table(rows=len(filas), cols=len(filas[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        tblPr = t._tbl.tblPr
        bordes = OxmlElement("w:tblBorders")
        for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), GRIS)
            bordes.append(e)
        tblPr.append(bordes)
        for i, fila in enumerate(filas):
            tr = t.rows[i]._tr
            if i == 0:  # encabezado repetido en cada página
                trPr = tr.get_or_add_trPr(); h = OxmlElement("w:tblHeader"); h.set(qn("w:val"), "true"); trPr.append(h)
            trPr = tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
            for j, txt in enumerate(fila):
                c = t.cell(i, j)
                c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                if anchos:
                    c.width = Inches(anchos[j])
                par = c.paragraphs[0]
                par.paragraph_format.line_spacing = 1.0
                par.paragraph_format.first_line_indent = Inches(0)
                if (len(filas) <= 10 or i <= 1) and i < len(filas) - 1:
                    par.paragraph_format.keep_with_next = True
                if i == 0:
                    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:fill"), AZUL)
                    c._tc.get_or_add_tcPr().append(sh)
                    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    r = par.add_run(str(txt)); r.bold = True; r.font.size = Pt(tam)
                else:
                    lineas = str(txt).split("\n")
                    for k, l in enumerate(lineas):
                        if k:
                            par = c.add_paragraph(); par.paragraph_format.line_spacing = 1.0
                        self._runs(par, f"**{l}**" if (j == 0 and primera_negrita and l) else l, tam=tam)
        if nota:
            self.nota(nota)
        else:
            self.d.add_paragraph().paragraph_format.space_after = Pt(4)
        return t

    def figura(self, ruta, titulo, ancho=6.0, nota=None):
        self.nfig += 1
        self._titulo_apa(f"Figura {self.nfig}", titulo)
        par = self.d.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = bool(nota)
        par.add_run().add_picture(ruta, width=Inches(ancho))
        if nota:
            self.nota(nota)

    def figura_doble(self, rutas, titulo, ancho=3.0, nota=None):
        self.nfig += 1
        self._titulo_apa(f"Figura {self.nfig}", titulo)
        par = self.d.add_paragraph(); par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.keep_with_next = bool(nota)
        for k, r in enumerate(rutas):
            if k:
                par.add_run("   ")
            par.add_run().add_picture(r, width=Inches(ancho))
        if nota:
            self.nota(nota)

    def salto(self):
        self._salto_pendiente = True

    def referencias(self, refs):
        self.h1("Referencias").paragraph_format.page_break_before = True
        for r in sorted(refs, key=lambda x: x.lower()):
            par = self.d.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.LEFT
            par.paragraph_format.left_indent = Inches(0.5)
            par.paragraph_format.first_line_indent = Inches(-0.5)
            self._runs(par, r)

    def guardar(self, ruta):
        self.d.save(ruta)
