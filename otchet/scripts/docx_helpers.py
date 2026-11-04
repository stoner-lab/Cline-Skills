# -*- coding: utf-8 -*-
"""Reusable python-docx helpers for Russian study reports (skill `otchet`).

Usage (from the `otchet` skill folder):
    import sys
    sys.path.insert(0, "scripts")
    from docx_helpers import *

Or add `<otchet>/scripts` to sys.path from any workspace.
Assets are resolved relative to this file: `<otchet>/assets/templates/`.
"""
from __future__ import annotations

import copy
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.table import Table, _Row
from docx.text.paragraph import Paragraph

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"
TEMPLATES_DIR = Path(os.environ.get("OTCHET_TEMPLATES", str(ASSETS_DIR / "templates")))
TITLE_TEMPLATE = TEMPLATES_DIR / "title_page_leti.docx"


def title_template_path() -> Path:
    """Return the path to the optional LETI title-page reference template."""
    return TITLE_TEMPLATE


@dataclass
class StyleConfig:
    font_name: str = "Times New Roman"
    font_size: int = 14
    line_spacing: float = 1.5
    first_line_indent_cm: float = 1.25
    margin_left_cm: float = 3.0
    margin_right_cm: float = 1.5
    margin_top_cm: float = 2.0
    margin_bottom_cm: float = 2.0
    page_width_cm: float = 21.0
    page_height_cm: float = 29.7
    heading_size: int = 14
    caption_size: int = 12
    table_size: int = 11
    table_header_size: int = 11


@dataclass
class ReportMeta:
    department: str = ""
    report_label: str = "ОТЧЕТ"
    work_line: str = "по практической работе №<номер>"
    discipline: str = "«<дисциплина>»"
    topic: str = "<тема>"
    variant: str = ""
    group: str = "<группа>"
    student: str = "<Фамилия И.О.>"
    student_short: str = ""  # для титула: «Фамилия И.О.»; если пусто – выводится из student
    student_label: str = "Студент гр. "
    second_student: str = ""
    second_student_label: str = "Студентка гр. "
    teacher: str = "<Фамилия И.О.>"
    submission_date: str = ""
    city: str = "Санкт-Петербург"
    year: str = "2026"
    completed_items: str = ""
    university_lines: tuple[str, ...] = (
        "МИНОБРНАУКИ РОССИИ",
        "САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ",
        "ЭЛЕКТРОТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ",
        "«ЛЭТИ» ИМ. В.И. УЛЬЯНОВА (ЛЕНИНА)",
    )
    extra_lines: list[str] = field(default_factory=list)


def set_run_font(run, size=14, bold=False, italic=False, name="Times New Roman"):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rFonts.set(qn(attr), name)


def _style_font(style, cfg: StyleConfig):
    style.font.name = cfg.font_name
    style.font.size = Pt(cfg.font_size)
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rFonts.set(qn(attr), cfg.font_name)


def add_page_number(paragraph, size=12):
    run = paragraph.add_run()
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "1"
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    for el in (fld1, instr, fld2, txt, fld3):
        run._r.append(el)
    set_run_font(run, size=size)


def setup_document(cfg: StyleConfig | None = None, title: str = "", author: str = ""):
    cfg = cfg or StyleConfig()
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.PORTRAIT
    sec.page_width = Cm(cfg.page_width_cm)
    sec.page_height = Cm(cfg.page_height_cm)
    sec.left_margin = Cm(cfg.margin_left_cm)
    sec.right_margin = Cm(cfg.margin_right_cm)
    sec.top_margin = Cm(cfg.margin_top_cm)
    sec.bottom_margin = Cm(cfg.margin_bottom_cm)
    sec.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    _style_font(normal, cfg)
    pf = normal.paragraph_format
    pf.line_spacing = cfg.line_spacing
    pf.first_line_indent = Cm(cfg.first_line_indent_cm)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size in (("Heading 1", cfg.heading_size), ("Heading 2", cfg.heading_size)):
        h = doc.styles[name]
        _style_font(h, cfg)
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = RGBColor(0, 0, 0)
        h.paragraph_format.first_line_indent = Cm(0)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.first_line_indent = Cm(0)
    add_page_number(footer)

    cp = doc.core_properties
    if title:
        cp.title = title
    if author:
        cp.author = author
    return doc


def para(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=1.25, size=14,
         bold=False, italic=False, before=0, after=0, spacing=1.5, keep=False,
         links=True):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Cm(indent_cm)
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = spacing
    pf.keep_with_next = keep
    if text:
        if links and LINK_RE.search(text):
            add_text_with_links(p, text, size=size, bold=bold, italic=italic)
        else:
            r = p.add_run(text)
            set_run_font(r, size=size, bold=bold, italic=italic)
    return p


def heading(doc, text, level=1, size=14):
    h = doc.add_heading(level=level)
    h.paragraph_format.first_line_indent = Cm(0)
    r = h.add_run(text)
    set_run_font(r, size=size, bold=True)
    r.font.color.rgb = RGBColor(0, 0, 0)
    return h


# Ссылки в отчёте должны быть настоящими гиперссылками (w:hyperlink + внешняя
# связь), иначе в DOCX и в PDF они остаются мёртвым текстом.
LINK_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"«»]+|doi:\s*10\.\d{4,9}/\S+",
                     re.IGNORECASE)
LINK_TRAILING = ".,;:!?)]}»\"'"


def _link_target(raw: str) -> str:
    """«www.x.ru» -> «http://www.x.ru», «doi: 10.1/x» -> «https://doi.org/10.1/x»."""
    value = raw.strip()
    if value.lower().startswith("doi:"):
        return "https://doi.org/" + value[4:].strip()
    if not value.lower().startswith(("http://", "https://")):
        return "http://" + value
    return value


def add_hyperlink(paragraph, url, text=None, size=14, bold=False, italic=False,
                  color=None, underline=None):
    """Добавить в абзац настоящую гиперссылку.

    Создаётся элемент ``w:hyperlink`` со ссылкой на внешний адрес через
    relationship; run переносится внутрь него, поэтому шрифт и оформление
    остаются такими же, как у обычного текста отчёта.
    """
    r_id = paragraph.part.relate_to(_link_target(url), RT.HYPERLINK, is_external=True)
    run = paragraph.add_run(text if text is not None else url)
    set_run_font(run, size=size, bold=bold, italic=italic)
    if color is not None:
        run.font.color.rgb = color
    if underline is not None:
        run.font.underline = underline
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    hyperlink.append(run._r)
    paragraph._p.append(hyperlink)
    return run


def add_text_with_links(paragraph, text, size=14, bold=False, italic=False,
                        color=None, underline=None):
    """Записать текст, превращая URL и DOI в кликабельные гиперссылки.

    Обычный текст остаётся обычными run'ами; точка или запятая после адреса
    не попадает внутрь ссылки.
    """
    position = 0
    for match in LINK_RE.finditer(text):
        start, end = match.span()
        url = match.group(0)
        while url and url[-1] in LINK_TRAILING:
            url = url[:-1]
        if not url:
            continue
        if start > position:
            run = paragraph.add_run(text[position:start])
            set_run_font(run, size=size, bold=bold, italic=italic)
        add_hyperlink(paragraph, url, text=url, size=size, bold=bold, italic=italic,
                      color=color, underline=underline)
        position = start + len(url)
    if position < len(text):
        run = paragraph.add_run(text[position:])
        set_run_font(run, size=size, bold=bold, italic=italic)
    return paragraph


def formula(doc, parts: Sequence[tuple[str, str | None]], size=14):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.5
    for text, mode in parts:
        r = p.add_run(text)
        set_run_font(r, size=size, name="Times New Roman")
        if mode == "sub":
            r.font.subscript = True
        elif mode == "sup":
            r.font.superscript = True
    return p


def caption(doc, text, size=12, links=True):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(8)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.5
    pf.keep_with_next = True
    if links and LINK_RE.search(text):
        add_text_with_links(p, text, size=size)
    else:
        r = p.add_run(text)
        set_run_font(r, size=size)
    return p


def _set_cell_bottom_border(cell, sz=8):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn("w:tcBorders"))
    if tcBorders is None:
        tcBorders = OxmlElement("w:tcBorders")
        tcPr.append(tcBorders)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(sz))
    bottom.set(qn("w:space"), "0")
    bottom.set(qn("w:color"), "000000")
    tcBorders.append(bottom)


def _set_par_text(paragraph, text):
    """Replace paragraph text keeping the formatting of its first run."""
    runs = paragraph.runs
    if not runs:
        run = paragraph.add_run(text)
        set_run_font(run, size=14)
        return paragraph
    runs[0].text = text
    for extra in runs[1:]:
        extra._r.getparent().remove(extra._r)
    return paragraph


def _set_cell_text(cell, text):
    if not cell.paragraphs:
        cell.text = text
        return
    _set_par_text(cell.paragraphs[0], text)


def _drop_paragraph(paragraph):
    el = paragraph._p
    el.getparent().remove(el)



def _page_break_tight(doc):
    """Разрыв страницы, который не создаёт пустую страницу.

    ``doc.add_page_break()`` вставляет абзац с разрывом. Если титульный лист
    занимает страницу почти целиком, этот абзац уезжает на следующую страницу,
    и Word показывает пустой лист перед текстом. Поэтому абзац с разрывом
    делается высотой 1 pt: он остаётся на странице титула, а разрыв работает.
    """
    doc.add_page_break()
    p = doc.paragraphs[-1]
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = Pt(1)
    for run in p.runs:
        run.font.size = Pt(1)
    return p


def _fill_title_from_template(doc, meta: "ReportMeta", tpl_path: Path) -> bool:
    """Clone the cover page XML from the .docx template and fill placeholders.

    The template is the single source of truth for the LETI cover: spacing,
    fonts, the 2x3 signature table and its borders are copied as-is, so the
    result matches ``title_page_leti.docx`` exactly. Placeholders in the
    template: <кафедра>, <номер>, <дисциплина>, <тема>, <пункты>, <дата>,
    <группа>, <Фамилия И.О.> (twice: student and teacher).
    """
    tpl = Document(str(tpl_path))
    body = doc.element.body
    sectPr = body.find(qn("w:sectPr"))
    inserted = []
    for child in list(tpl.element.body.iterchildren()):
        if child.tag == qn("w:sectPr"):
            continue
        clone = copy.deepcopy(child)
        if sectPr is not None:
            sectPr.addprevious(clone)
        else:
            body.append(clone)
        inserted.append(clone)

    paragraphs = [Paragraph(el, doc) for el in inserted if el.tag == qn("w:p")]
    tables = [Table(el, doc) for el in inserted if el.tag == qn("w:tbl")]

    uni = [str(line) for line in (meta.university_lines or ())]
    for idx, paragraph in enumerate(paragraphs):
        text = paragraph.text.strip()

        if idx < 4:  # четыре строки вуза
            if idx < len(uni):
                _set_par_text(paragraph, uni[idx])
            else:
                _drop_paragraph(paragraph)
            continue

        if "<кафедра>" in text:
            if meta.department:
                _set_par_text(paragraph, f"Кафедра {meta.department}")
            else:
                _drop_paragraph(paragraph)
            continue

        if text == "ОТЧЕТ":
            _set_par_text(paragraph, meta.report_label or text)
            continue

        if text.startswith("по ") and "<номер>" in text:
            if (meta.work_line or "").strip():
                _set_par_text(paragraph, meta.work_line)
            else:
                _drop_paragraph(paragraph)
            continue

        if "<дисциплина>" in text:
            disc = (meta.discipline or "").strip().strip("«» ")
            if disc:
                _set_par_text(paragraph, f"по дисциплине «{disc}»")
            else:
                _drop_paragraph(paragraph)
            continue

        if "<тема>" in text:
            topic = (meta.topic or "").strip()
            if topic:
                _set_par_text(paragraph, f"Тема: {topic}")
            else:
                _drop_paragraph(paragraph)
            continue

        if text.startswith("Вариант"):
            variant = str(meta.variant or "").strip()
            if variant:
                _set_par_text(paragraph, f"Вариант {variant}")
            else:
                _drop_paragraph(paragraph)
            continue

        if "<пункты>" in text:
            if (meta.completed_items or "").strip():
                _set_par_text(paragraph, f"Выполненные пункты: {meta.completed_items}")
            else:
                _drop_paragraph(paragraph)
            continue

        if "<дата>" in text:
            date = (meta.submission_date or "").strip()
            if date:
                _set_par_text(paragraph, f"Дата сдачи работы на проверку – {date}")
            else:
                _drop_paragraph(paragraph)
            continue

        if text == "Санкт-Петербург":
            _set_par_text(paragraph, meta.city)
            continue

        if text.isdigit() and len(text) == 4:
            _set_par_text(paragraph, meta.year)
            continue

    for table in tables:
        rows = table.rows
        if len(rows) < 2 or len(rows[0].cells) < 3:
            continue
        _set_cell_text(rows[0].cells[0], meta.student_label + str(meta.group))
        _set_cell_text(rows[0].cells[2], _student_display(meta))
        _set_cell_text(rows[1].cells[0], "Руководитель")
        _set_cell_text(rows[1].cells[2], meta.teacher)
        if meta.second_student:
            tr = copy.deepcopy(rows[1]._tr)
            rows[1]._tr.addprevious(tr)
            extra_row = _Row(tr, table)
            _set_cell_text(extra_row.cells[0], meta.second_student_label + str(meta.group))
            _set_cell_text(extra_row.cells[2], short_name(meta.second_student))
    return True


def normalize_dashes(doc):
    """Заменяет длинное тире «—» на короткое «–» с пробелами.

    Правило `references/format.md` §3.1: в тексте используется только en dash
    с пробелами по сторонам, em dash запрещён. Функция проходит по всем абзацам
    и ячейкам таблиц, поэтому её достаточно вызвать один раз перед сохранением.
    """
    import re

    pattern = re.compile(r"\s*—\s*")

    def fix(paragraph):
        for run in paragraph.runs:
            if "—" in run.text:
                run.text = pattern.sub(" – ", run.text)

    for paragraph in doc.paragraphs:
        fix(paragraph)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    fix(paragraph)
    return doc


def short_name(full_name: str) -> str:
    """«Нгуен Тхе» -> «Нгуен Т.», «Нгуен Тхе Зуй» -> «Нгуен Т.З.».

    На титульном листе принято писать фамилию и инициалы, тогда как в имени
    файла указывается фамилия, имя и группа: ``Нгуен_Тхе_4395``.
    """
    parts = [part for part in str(full_name).replace('.', ' ').split() if part]
    if len(parts) < 2:
        return str(full_name).strip()
    initials = ''.join(f"{part[0].upper()}." for part in parts[1:])
    return f"{parts[0]} {initials}"


def _student_display(meta: "ReportMeta") -> str:
    """ФИО для титула: явно заданное student_short или «Фамилия И.О.»."""
    return (meta.student_short or short_name(meta.student)).strip()


def add_references(doc, items, title="Список источников", cfg: StyleConfig | None = None):
    """Список источников: всегда с новой страницы, пункты по общим правилам.

    Заголовок ставится с новой страницы (``page_break_before``) и выравнивается
    по центру, чтобы не создавать пустой абзац. Пункты оформляются как обычный текст: отступ первой
    строки, выравнивание по ширине, интервал 1,5.

    Адреса (URL, ``www.``, DOI) внутри пункта становятся настоящими гиперссылками,
    чтобы в DOCX и в PDF по ним можно было щёлкнуть. Текст остаётся Times New Roman
    того же кегля, поэтому оформление не отличается от остального списка.
    """
    cfg = cfg or StyleConfig()

    head = doc.add_paragraph()
    head_format = head.paragraph_format
    head_format.page_break_before = True
    head_format.first_line_indent = Cm(0)
    head_format.space_before = Pt(0)
    head_format.space_after = Pt(6)
    head_format.line_spacing = cfg.line_spacing
    head_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    head_format.keep_with_next = True
    head_run = head.add_run(title)
    set_run_font(head_run, size=cfg.heading_size, bold=True)

    for index, item in enumerate(items, start=1):
        text = str(item).strip()
        # Нумерация добавляется, только если её нет в самой строке.
        if text[:1].isdigit() and text[1:3] in ('. ', '.\t'):
            rendered = text
        else:
            rendered = f"{index}. {text}"
        p = para(doc, "", align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                 indent_cm=cfg.first_line_indent_cm, size=cfg.font_size,
                 spacing=cfg.line_spacing)
        add_text_with_links(p, rendered, size=cfg.font_size)
    return doc


def add_title_page(doc, meta: ReportMeta, cfg: StyleConfig | None = None, template=None):
    """Add the official LETI cover page, cloned from the .docx template.

    ``template`` overrides ``assets/templates/title_page_leti.docx``.
    If the template is missing or cannot be cloned (e.g. it references images
    or hyperlinks), the manual layout below is used as a fallback.
    """
    cfg = cfg or StyleConfig()
    tpl_path = Path(template) if template else title_template_path()
    if tpl_path.exists():
        try:
            _fill_title_from_template(doc, meta, tpl_path)
        except Exception:
            _add_title_page_manual(doc, meta, cfg)
            return
        _page_break_tight(doc)
        return
    _add_title_page_manual(doc, meta, cfg)


def _add_title_page_manual(doc, meta: ReportMeta, cfg: StyleConfig | None = None):
    cfg = cfg or StyleConfig()
    lines = list(meta.university_lines)
    if meta.department:
        lines.append(f"Кафедра {meta.department}")
    for line in lines:
        para(doc, line, align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0,
             size=cfg.font_size, bold=True, spacing=cfg.line_spacing)

    for _ in range(3):
        para(doc, "", indent_cm=0, spacing=cfg.line_spacing)

    para(doc, meta.report_label, align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0,
         size=cfg.font_size, bold=True, spacing=cfg.line_spacing)
    para(doc, meta.work_line, align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0,
         size=cfg.font_size, bold=True, spacing=cfg.line_spacing)
    disc = meta.discipline.strip()
    if disc and not disc.startswith("«"):
        disc = f"«{disc}»"
    para(doc, f"по дисциплине {disc}", align=WD_ALIGN_PARAGRAPH.CENTER,
         indent_cm=0, size=cfg.font_size, bold=True, spacing=cfg.line_spacing)
    para(doc, f"Тема: {meta.topic}", align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0,
         size=cfg.font_size, bold=True, spacing=cfg.line_spacing)
    if meta.variant:
        para(doc, f"Вариант {meta.variant}", align=WD_ALIGN_PARAGRAPH.CENTER,
             indent_cm=0, size=cfg.font_size, spacing=cfg.line_spacing)

    for _ in range(4):
        para(doc, "", indent_cm=0, spacing=cfg.line_spacing)

    rows = [(meta.student_label + meta.group, "", _student_display(meta))]
    if meta.second_student:
        rows.append((meta.second_student_label + meta.group, "",
                     meta.student_short or short_name(meta.second_student)))
    rows.append(("Руководитель", "", meta.teacher))

    table = doc.add_table(rows=len(rows), cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = (6.2, 5.6, 5.0)
    aligns = (WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER)
    for r_idx, row in enumerate(rows):
        table_row = table.rows[r_idx]
        table_row.height = Cm(1.08)
        table_row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for c_idx, value in enumerate(row):
            cell = table_row.cells[c_idx]
            cell.width = Cm(widths[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.alignment = aligns[c_idx]
            run = p.add_run(value)
            set_run_font(run, size=cfg.font_size)
            if c_idx == 1:
                _set_cell_bottom_border(cell, sz=8)

    for _ in range(3):
        para(doc, "", indent_cm=0, spacing=cfg.line_spacing)

    if meta.completed_items:
        para(doc, f"Выполненные пункты: {meta.completed_items}",
             align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, size=cfg.font_size,
             bold=True, spacing=cfg.line_spacing)
    if meta.submission_date:
        para(doc, f"Дата сдачи работы на проверку – {meta.submission_date}",
             align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0, size=cfg.font_size,
             bold=True, spacing=cfg.line_spacing)
    para(doc, "", indent_cm=0, spacing=cfg.line_spacing)
    para(doc, meta.city, align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0,
         size=cfg.font_size, spacing=cfg.line_spacing)
    para(doc, meta.year, align=WD_ALIGN_PARAGRAPH.CENTER, indent_cm=0,
         size=cfg.font_size, spacing=cfg.line_spacing)
    _page_break_tight(doc)



def _set_cell(cell, text, size=11, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER):
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    for r in list(p.runs):
        r._element.getparent().remove(r._element)
    r = p.add_run(str(text))
    set_run_font(r, size=size, bold=bold)


def add_table(doc, headers, rows, widths_cm, cfg: StyleConfig | None = None,
              size: int | None = None, header_size: int | None = None,
              align_left_cols=(), last_row_bold=False, spacer=True):
    cfg = cfg or StyleConfig()
    size = size or cfg.table_size
    header_size = header_size or cfg.table_header_size
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    tblPr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)

    mar = OxmlElement("w:tblCellMar")
    for side, val in (("top", 0), ("left", 60), ("bottom", 0), ("right", 60)):
        el = OxmlElement("w:" + side)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tblPr.append(mar)

    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)

    for j, h in enumerate(headers):
        c = table.rows[0].cells[j]
        c.width = Cm(widths_cm[j])
        _set_cell(c, h, size=header_size, bold=True)

    for r_idx, row in enumerate(rows):
        cells = table.add_row().cells
        bold = last_row_bold and r_idx == len(rows) - 1
        for j, value in enumerate(row):
            cells[j].width = Cm(widths_cm[j])
            al = WD_ALIGN_PARAGRAPH.LEFT if j in align_left_cols else WD_ALIGN_PARAGRAPH.CENTER
            _set_cell(cells[j], value, size=size, bold=bold, align=al)

    for r_idx, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if r_idx < len(table.rows) - 1:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True

    if spacer:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        set_run_font(p.add_run(""), size=6)
    return table


def add_picture_with_caption(doc, image_path, caption_text, width_cm=15.0, cfg: StyleConfig | None = None):
    cfg = cfg or StyleConfig()
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(image_path), width=Cm(width_cm))
    c = doc.add_paragraph()
    c.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.first_line_indent = Cm(0)
    c.paragraph_format.space_before = Pt(0)
    c.paragraph_format.space_after = Pt(6)
    r = c.add_run(caption_text)
    set_run_font(r, size=cfg.caption_size)
    return p


def add_toc(doc, title="СОДЕРЖАНИЕ"):
    p_title = doc.add_paragraph()
    p_title.paragraph_format.first_line_indent = Cm(0)
    p_title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run(title)
    set_run_font(r_title, size=14, bold=True)

    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run()
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r'TOC \o "1-3" \h \z \u'
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    txt = OxmlElement("w:t")
    txt.text = "Обновите поле: F9"
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    for el in (fld1, instr, fld2, txt, fld3):
        run._r.append(el)
    settings = doc.settings.element
    update = OxmlElement("w:updateFields")
    update.set(qn("w:val"), "true")
    settings.append(update)


def fmt_num(value, decimals=2):
    """1 234 567,89 – space thousands, comma decimal."""
    s = f"{value:,.{decimals}f}"
    return s.replace(",", " ").replace(".", ",")


def _ps_quote(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def export_pdf_via_word(docx_path, pdf_path, timeout=180):
    """Export DOCX to PDF/A-1b via MS Word COM (Windows only).

    PDF/A forces font embedding, so Times New Roman survives on the checker's
    machine. If Word refuses PDF/A, a plain PDF export is written instead.
    """
    docx_path = str(Path(docx_path).resolve())
    pdf_path = str(Path(pdf_path).resolve())
    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
    script = f"""
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {{
    $doc = $word.Documents.Open({_ps_quote(docx_path)}, $false, $true)
    try {{
        # TOC and PAGE are fields: build them once so the export carries real
        # entries (and clickable /Link annotations) instead of the placeholder.
        try {{ $doc.Fields.Update() | Out-Null }} catch {{}}
        foreach ($toc in $doc.TablesOfContents) {{ try {{ $toc.Update() }} catch {{}} }}
        # PDF/A-1b: BitmapMissingFonts must be False, UseISO19005_1 = True
        $doc.ExportAsFixedFormat({_ps_quote(pdf_path)}, 17, $false, 0, 0, 0, 0, 0, $true, $false, 0, $true, $false, $true)
    }} catch {{
        $doc.ExportAsFixedFormat({_ps_quote(pdf_path)}, 17)
    }}
    $doc.Close($false)
}} finally {{
    $word.Quit()
}}
"""
    fd, ps1 = tempfile.mkstemp(suffix=".ps1")
    os.close(fd)
    try:
        with open(ps1, "w", encoding="utf-8-sig") as f:
            f.write(script)
        res = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps1],
            capture_output=True, text=True, timeout=timeout,
        )
        if res.returncode != 0 or not Path(pdf_path).exists():
            raise RuntimeError("Word PDF export failed: " + (res.stderr or res.stdout))
    finally:
        Path(ps1).unlink(missing_ok=True)
    return pdf_path


def save_report(doc, docx_path, pdf_path=None):
    docx_path = Path(docx_path)
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    if pdf_path:
        export_pdf_via_word(docx_path, pdf_path)
    return str(docx_path)

