# Small drawing helpers on top of python-pptx, matching the lab template style.
import copy
from lxml import etree
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

FONT = "Yu Gothic"
GREEN = "005732"
BLUE = "8BA8B5"
TXT = "141414"
GRAY = "47534C"
LIGHT = "E6EBE8"
MID = "9AA3A0"
WHITE = "FFFFFF"
ORANGE = "E97132"

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
ALIGN = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}
ANCHOR = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}


def rgb(h):
    return RGBColor.from_string(h)


def style_run(r, size=None, bold=None, color=None, font=FONT, italic=None):
    f = r.font
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = rgb(color)
    f.name = font
    rPr = r._r.get_or_add_rPr()
    latin = rPr.find(qn("a:latin"))
    for old in rPr.findall(qn("a:ea")):
        rPr.remove(old)
    ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", font)
    latin.addnext(ea)


def fill_paras(tf, paras, size, bold=False, color=TXT, align="l", space_after=0, line_spacing=None):
    """paras: list of str | list[(text, opts)]; opts keys: size, bold, color."""
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ALIGN[align]
        if space_after:
            p.space_after = Pt(space_after)
        if line_spacing:
            p.line_spacing = line_spacing
        runs = para if isinstance(para, list) else [(para, {})]
        for t, o in runs:
            r = p.add_run()
            r.text = t
            style_run(r, size=o.get("size", size), bold=o.get("bold", bold), color=o.get("color", color))


def text(slide, x, y, w, h, paras, size=20, bold=False, color=TXT, align="l", anchor="t", space_after=0,
         line_spacing=None, name=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = ANCHOR[anchor]
    if isinstance(paras, str):
        paras = [paras]
    fill_paras(tf, paras, size, bold, color, align, space_after, line_spacing)
    return tb


def _strip_style(shape):
    st = shape._element.find(qn("p:style"))
    if st is not None:
        shape._element.remove(st)


def box(slide, x, y, w, h, paras=None, size=18, bold=False, color=TXT, fill=WHITE, line=GREEN, line_w=0.9,
        align="c", anchor="m", shape=MSO_SHAPE.RECTANGLE, name=None, margin=0.08):
    sp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    _strip_style(sp)
    if name:
        sp.name = name
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = rgb(fill)
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = rgb(line)
        sp.line.width = Pt(line_w)
    tf = sp.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    tf.vertical_anchor = ANCHOR[anchor]
    if paras is not None:
        if isinstance(paras, str):
            paras = [paras]
        fill_paras(tf, paras, size, bold, color, align)
    return sp


def line(slide, x1, y1, x2, y2, color=GREEN, width=0.9, arrow=False, dash=False, name=None):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    _strip_style(c)
    if name:
        c.name = name
    c.line.color.rgb = rgb(color)
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    if dash:
        d = etree.SubElement(ln, qn("a:prstDash"))
        d.set("val", "dash")
    if arrow:
        t = etree.SubElement(ln, qn("a:tailEnd"))
        t.set("type", "triangle")
    return c


def table(slide, x, y, w, col_w, rows, size=18, header_size=None, row_h=0.55, header_fill=LIGHT, bold_rows=(),
          aligns=None, name=None):
    """rows[0] is the header. Cells are str or list of runs."""
    nr, nc = len(rows), len(rows[0])
    gs = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w), Inches(row_h * nr))
    if name:
        gs.name = name
    tbl = gs.table
    tbl.first_row = False
    tbl.horz_banding = False
    for j, cw in enumerate(col_w):
        tbl.columns[j].width = Inches(cw)
    for i in range(nr):
        tbl.rows[i].height = Inches(row_h)
        for j in range(nc):
            c = tbl.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.1)
            c.margin_top = c.margin_bottom = Inches(0.04)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = c.text_frame
            tf.word_wrap = True
            paras = [rows[i][j]]  # one paragraph: str or list of (text, opts) runs
            fill_paras(tf, paras, (header_size or size) if i == 0 else size, bold=(i == 0 or i in bold_rows),
                       color=TXT, align=(aligns[j] if aligns else "l"))
            tcPr = c._tc.get_or_add_tcPr()
            for ch in list(tcPr):
                tcPr.remove(ch)
            for side in ("lnL", "lnR", "lnT", "lnB"):
                ln = etree.SubElement(tcPr, qn(f"a:{side}"))
                ln.set("w", "6350")
                sf = etree.SubElement(ln, qn("a:solidFill"))
                etree.SubElement(sf, qn("a:srgbClr")).set("val", "C3CAC6")
            sf = etree.SubElement(tcPr, qn("a:solidFill"))
            etree.SubElement(sf, qn("a:srgbClr")).set("val", header_fill if i == 0 else WHITE)
    return gs


FOOTER_XML = """
<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="{a}">
 <p:nvSpPr><p:cNvPr id="{id}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
 <p:nvPr><p:ph type="{typ}" idx="{idx}"/></p:nvPr></p:nvSpPr><p:spPr/>
 <p:txBody><a:bodyPr/><a:lstStyle/><a:p>{body}</a:p></p:txBody></p:sp>"""


def add_footer(slide, number):
    """Date field, lab name and slide number placeholders (python-pptx does not clone these)."""
    tree = slide.shapes._spTree
    items = [
        ("dt", 10, "日付プレースホルダー 3",
         '<a:fld id="{1BD6EC33-F415-8551-C358-184B02307ABF}" type="datetime1"><a:rPr lang="en-US"/><a:t>11/13/2026</a:t></a:fld>'),
        ("ftr", 11, "フッター プレースホルダー 4", "<a:r><a:rPr lang=\"en-US\"/><a:t>Hiroshima Univ. Nagahara Lab</a:t></a:r>"),
        ("sldNum", 12, "スライド番号プレースホルダー 5",
         '<a:fld id="{AD75FED6-38D0-DE9C-92C0-6E7FA635581C}" type="slidenum"><a:rPr lang="en-US"/><a:t>%d</a:t></a:fld>' % number),
    ]
    for k, (typ, idx, name, body) in enumerate(items):
        xml = FOOTER_XML.format(a=A_NS, id=900 + k, name=name, typ=typ, idx=idx, body=body)
        tree.append(etree.fromstring(xml))


def content_slide(prs, title, number):
    s = prs.slides.add_slide(prs.slide_layouts[1])
    for ph in list(s.placeholders):
        if ph.placeholder_format.idx == 1:  # unused body placeholder
            ph._element.getparent().remove(ph._element)
    s.shapes.title.text = title
    add_footer(s, number)
    return s


def clear_slides(prs):
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        prs.part.drop_rel(sid.rId)
        lst.remove(sid)
