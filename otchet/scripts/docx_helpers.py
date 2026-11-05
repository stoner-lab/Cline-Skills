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
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
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
    # 14 пт – принятый по умолчанию кегль (методички ЛЭТИ: «Times New Roman 12
    # или 14»); менять на 12 только если методичка прямо этого требует.
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
    # ЛЭТИ центрирует заголовки; ГОСТ 7.32-2017 (5.4.3) требует абзацный отступ.
    heading_center: bool = True
    # ГОСТ 7.32-2017 (6.4.3) ставит наименование таблицы слева, без отступа.
    table_caption_center: bool = True
    # Подпись рисунка: «Рис. 1» в ЛЭТИ, «Рисунок 1» по ГОСТ 7.32-2017 и в бланках.
    figure_label: str = "Рис."
    # Подписи рисунков по методичкам ЛЭТИ – курсивом и без точки в конце.
    caption_italic: bool = False
    # Начинать ли каждый раздел (Heading 1) с новой страницы.
    heading_page_break: bool = False
    sources_title: str = "Список использованных источников"


def leti_form_config() -> StyleConfig:
    """Пресет под официальные бланки ЛЭТИ (форма 3004).

    Проверено по файлам `Cognitio\\Шаблоны\\3004_*.doc` (1–6): A4, поля
    30/10/20/20 мм, текст Times New Roman **14 пт**, междустрочный интервал
    **1,5**, красная строка **1,25 см** (в бланках «Normal» стоит 12 пт, но все
    run'ы переопределены на 14 – так бланк и выглядит).

    Рисунки бланки не показывают, поэтому подпись оформляется по методичкам:
    «Рисунок 1 – Название», курсивом, без точки в конце.

    Каждый раздел начинается с новой страницы (``heading_page_break=True``) –
    так требует методичка: «структурные части начинают с нового листа».
    """
    return StyleConfig(
        font_size=14,
        heading_size=14,
        caption_size=12,
        table_size=11,
        table_header_size=11,
        margin_right_cm=1.0,
        figure_label="Рисунок",
        caption_italic=True,
        heading_page_break=True,
    )


def gost_config() -> StyleConfig:
    """Пресет под ГОСТ 7.32-2017 (отчёт о НИР).

    Отличия от пресета ЛЭТИ: кегль 12 пт вместо 14, заголовки с абзацного
    отступа вместо центрирования, наименование таблицы слева без отступа,
    подпись рисунка «Рисунок N». Поля (30/15/20/20 мм), интервал 1,5 и
    абзацный отступ 1,25 см совпадают с ЛЭТИ и остаются как есть.
    Требования методички кафедры всегда важнее стандарта.
    """
    return StyleConfig(
        font_size=12,
        heading_size=12,
        caption_size=12,
        table_size=10,
        table_header_size=10,
        heading_center=False,
        table_caption_center=False,
        figure_label="Рисунок",
    )


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
        h.paragraph_format.first_line_indent = (
            Cm(0) if cfg.heading_center else Cm(cfg.first_line_indent_cm))
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        h.paragraph_format.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER if cfg.heading_center else WD_ALIGN_PARAGRAPH.LEFT)

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


def para(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent_cm=None, size=None,
         bold=False, italic=False, before=0, after=0, spacing=None, keep=False,
         links=True, cfg: StyleConfig | None = None):
    """Абзац обычного текста; ``cfg`` подставляет кегль, отступ и интервал пресета."""
    indent_cm = cfg.first_line_indent_cm if (cfg and indent_cm is None) else indent_cm
    size = cfg.font_size if (cfg and size is None) else size
    spacing = cfg.line_spacing if (cfg and spacing is None) else spacing
    indent_cm = 1.25 if indent_cm is None else indent_cm
    size = 14 if size is None else size
    spacing = 1.5 if spacing is None else spacing
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


def _ends_with_page_break(doc) -> bool:
    """Последний абзац уже заканчивается разрывом страницы."""
    if not doc.paragraphs:
        return False
    last = doc.paragraphs[-1]
    if last.paragraph_format.page_break_before:
        return True
    return any(br.get(qn("w:type")) == "page" for br in last._p.iter(qn("w:br")))


_NUMBERED_HEADING = re.compile(r"^\d+\.\s")


def heading(doc, text, level=1, size=14, cfg: StyleConfig | None = None,
            page_break=None):
    """Заголовок раздела.

    ``page_break``: ``True`` – с новой страницы, ``False`` – подряд, ``None`` –
    по правилу: крупные заголовки (``1.``, ``2.``, ``ЗАКЛЮЧЕНИЕ``…) начинают
    новую страницу, подразделы (``1.1``) – нет. Исключение: **первый**
    нумерованный раздел продолжает страницу с блоком «Цель работы».
    """
    cfg = cfg or StyleConfig()
    numbered = bool(_NUMBERED_HEADING.match(str(text).strip()))
    if page_break is None:
        page_break = bool(cfg.heading_page_break) and level == 1
        if page_break and numbered and not getattr(doc, "_otchet_numbered_started", False):
            page_break = False
    if numbered:
        doc._otchet_numbered_started = True
    # если предыдущий абзац уже завершается разрывом, второй разрыв дал бы пустой лист
    if page_break and _ends_with_page_break(doc):
        page_break = False
    h = doc.add_heading(level=level)
    h.paragraph_format.page_break_before = bool(page_break)
    h.paragraph_format.first_line_indent = (
        Cm(0) if cfg.heading_center else Cm(cfg.first_line_indent_cm))
    h.paragraph_format.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER if cfg.heading_center else WD_ALIGN_PARAGRAPH.LEFT)
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


def formula(doc, parts: Sequence[tuple[str, str | None]], size=14, number=None,
            cfg: StyleConfig | None = None):
    """Формула по центру; при ``number`` – номер в скобках у правого края.

    ГОСТ 7.32-2017 (6.10): формулы нумеруют сквозной нумерацией арабскими
    цифрами в круглых скобках, номер ставят у правого края строки формулы.
    Табуляции (центр + правый край) дают и центрирование, и номер без таблицы.
    """
    cfg = cfg or StyleConfig()
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(3)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.5
    if number:
        text_width_cm = cfg.page_width_cm - cfg.margin_left_cm - cfg.margin_right_cm
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.tab_stops.add_tab_stop(Cm(text_width_cm / 2), WD_TAB_ALIGNMENT.CENTER)
        pf.tab_stops.add_tab_stop(Cm(text_width_cm), WD_TAB_ALIGNMENT.RIGHT)
        p.add_run("\t")
    else:
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for text, mode in parts:
        r = p.add_run(text)
        set_run_font(r, size=size, name="Times New Roman")
        if mode == "sub":
            r.font.subscript = True
        elif mode == "sup":
            r.font.superscript = True
    if number:
        r = p.add_run(f"\t({number})")
        set_run_font(r, size=size, name="Times New Roman")
    return p


def caption(doc, text, size=None, links=True, cfg: StyleConfig | None = None,
            italic=None):
    """Подпись под рисунком/над таблицей: по центру, без отступа, без точки в конце.

    ``italic=None`` берёт значение из ``cfg.caption_italic`` (методички ЛЭТИ
    требуют подписи рисунков курсивом).
    """
    size = cfg.caption_size if (cfg and size is None) else (12 if size is None else size)
    if italic is None:
        italic = bool(cfg.caption_italic) if cfg else False
    text = str(text).rstrip()
    if text.endswith(".") and not text.endswith("..."):
        text = text[:-1]
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(8)
    pf.space_after = Pt(3)
    pf.line_spacing = 1.5
    pf.keep_with_next = True
    if links and LINK_RE.search(text):
        add_text_with_links(p, text, size=size, italic=italic)
    else:
        r = p.add_run(text)
        set_run_font(r, size=size, italic=italic)
    return p


def figure_caption(doc, number, title, cfg: StyleConfig | None = None):
    """Подпись рисунка «Рисунок 1 – Название» (или «Рис. 1 – …»), курсивом."""
    cfg = cfg or StyleConfig()
    return caption(doc, f"{cfg.figure_label} {number} – {str(title).rstrip('. ')}",
                   cfg=cfg, italic=True)


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


def _fill_title_from_template(doc, meta: "ReportMeta", tpl_path: Path,
                              cfg: StyleConfig | None = None) -> bool:
    """Clone the cover page XML from the .docx template and fill placeholders.

    The template is the single source of truth for the LETI cover: spacing,
    fonts, the 2x3 signature table and its borders are copied as-is, so the
    result matches ``title_page_leti.docx`` exactly. Placeholders in the
    template: <кафедра>, <номер>, <дисциплина>, <тема>, <вариант>, <пункты>,
    <дата>, <группа>, <Фамилия И.О. студента>, <Фамилия И.О. руководителя>,
    <город>, <год>. Older templates with <Фамилия И.О.> in both signature cells,
    «Санкт-Петербург» and a bare year still work: those branches are kept as
    fallbacks.
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
    # строки «Выполненные пункты» и «Дата сдачи» необязательные: в шаблоне их нет,
    # они добавляются ниже, только если в ReportMeta есть данные
    optional_used = {"items": False, "date": False, "variant": False}

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
            work_line = (meta.work_line or "").strip()
            # Страховка от дубля: если в work_line положили саму строку дисциплины
            # («по дисциплине «X»»), второй раз её не печатаем – на титуле уже есть
            # отдельная строка по дисциплине.
            if work_line.lower().startswith("по дисциплине"):
                work_line = ""
            if work_line:
                _set_par_text(paragraph, work_line)
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
                optional_used["variant"] = True
            else:
                _drop_paragraph(paragraph)
            continue

        if "<пункты>" in text:
            if (meta.completed_items or "").strip():
                _set_par_text(paragraph, f"Выполненные пункты: {meta.completed_items}")
                optional_used["items"] = True
            else:
                _drop_paragraph(paragraph)
            continue

        if "<дата>" in text:
            date = (meta.submission_date or "").strip()
            if date:
                _set_par_text(paragraph, f"Дата сдачи работы на проверку – {date}")
                optional_used["date"] = True
            else:
                _drop_paragraph(paragraph)
            continue

        if "<город>" in text:
            _set_par_text(paragraph, meta.city)
            continue

        if text == "Санкт-Петербург":
            _set_par_text(paragraph, meta.city)
            continue

        if "<год>" in text:
            _set_par_text(paragraph, meta.year)
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
        _set_cell_text(rows[1].cells[2], short_name(meta.teacher))
        if meta.second_student:
            tr = copy.deepcopy(rows[1]._tr)
            rows[1]._tr.addprevious(tr)
            extra_row = _Row(tr, table)
            _set_cell_text(extra_row.cells[0], meta.second_student_label + str(meta.group))
            _set_cell_text(extra_row.cells[2], short_name(meta.second_student))

    # Необязательные строки: в шаблоне их нет, поэтому добавляем сами, когда в
    # ReportMeta есть данные. Место под «Вариант» сохраняем всегда (пустой строкой),
    # чтобы геометрия бланка не менялась; строки под таблицей места не имеют,
    # поэтому забираем его из отступа над «ОТЧЕТ».
    want_variant = (meta.variant or "").strip()
    under_table = []

    if want_variant and not optional_used["variant"]:
        slot_text = f"Вариант {want_variant}"
    else:
        slot_text = ""
    if (meta.completed_items or "").strip() and not optional_used["items"]:
        under_table.append(f"Выполненные пункты: {meta.completed_items}")
    if (meta.submission_date or "").strip() and not optional_used["date"]:
        under_table.append(f"Дата сдачи работы на проверку – {meta.submission_date}")

    slot_base = next((p for p in paragraphs if p.text.strip().startswith("Тема")), None)
    if slot_base is not None:
        new_p = copy.deepcopy(slot_base._p)
        slot_base._p.addnext(new_p)
        slot_par = Paragraph(new_p, doc)
        slot_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        slot_par.paragraph_format.space_before = Pt(0)
        _set_par_text(slot_par, slot_text)
        for run in slot_par.runs:
            set_run_font(run, size=14, bold=False)

    if under_table:
        base = next((p for p in paragraphs if p.text.strip().startswith("Тема")), None)
        if base is not None:
            anchor = tables[0]._tbl if tables else base._p
            for text in under_table:
                new_p = copy.deepcopy(base._p)
                anchor.addnext(new_p)
                anchor = new_p
                extra_par = Paragraph(new_p, doc)
                extra_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                extra_par.paragraph_format.space_before = Pt(12)
                _set_par_text(extra_par, text)
                for run in extra_par.runs:
                    set_run_font(run, size=14, bold=True)

            # эти строки занимают место – берём его из отступа над «ОТЧЕТ»
            department = next((p for p in paragraphs
                               if p.text.strip().startswith("Кафедра")), None)
            if department is not None:
                for _ in range(len(under_table) + 1):
                    nxt = department._p.getnext()
                    if nxt is None or nxt.tag != qn("w:p"):
                        break
                    if "".join(t.text or "" for t in nxt.iter(qn("w:t"))).strip():
                        break
                    nxt.getparent().remove(nxt)

    # бланки ЛЭТИ – 12 пт, но кегль задаёт отчёт: приводим скопированный титул
    _scale_cover_fonts(paragraphs, tables, cfg.font_size)

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


# Плейсхолдеры, которые не должны попасть на титул вместо ФИО. «И.О.» здесь нет:
# Иванов И.О. – нормальное ФИО, а не заглушка.
NAME_JUNK = ("<", ">", "фамилия", "фио", "0000", "название")


def name_problems(value: str, role: str) -> list[str]:
    """Проверить, что ФИО записано как «Фамилия И.О.».

    Пустая строка, плейсхолдер или одна фамилия без инициалов – проблема:
    угадывать инициалы нельзя, их должен дать пользователь.
    """
    text = str(value or "").strip()
    if not text:
        return [f"{role}: ФИО не задано"]
    if any(mark in text.lower() for mark in NAME_JUNK):
        return [f"{role}: вместо ФИО плейсхолдер {text!r}"]
    short = short_name(text)
    if "." not in short:
        return [f"{role}: {text!r} без инициалов, нужен формат «Фамилия И.О.»"]
    return []


def validate_meta_names(meta: "ReportMeta") -> list[str]:
    """Список проблем с ФИО и группой; пустой список – можно собирать титул."""
    problems = []
    problems += name_problems(_student_display(meta), "Студент")
    problems += name_problems(short_name(meta.teacher), "Руководитель")
    group = str(meta.group or "").strip()
    if not group or any(char in group for char in "<>"):
        problems.append("Группа не задана")
    return problems



def add_references(doc, items, title=None, cfg: StyleConfig | None = None):
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
    head_run = head.add_run(title or cfg.sources_title)
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


def appendix(doc, letter, title="", status=None, cfg: StyleConfig | None = None):
    """Оформить приложение по ГОСТ 7.32-2017 (6.17).

    «ПРИЛОЖЕНИЕ А» печатают прописными, по центру, с новой страницы; строку
    статуса «(обязательное)» или «(справочное)» и наименование – ниже, тоже по
    центру. Заголовок делается стилем Heading 1, поэтому приложение попадает в
    содержание (6.17.7), а нумерация страниц остаётся сквозной (6.17.6).

    Буквы: А, Б, В, Г, Д, Е, Ж, И, К... – кроме Ё, З, Й, О, Ч, Ъ, Ы, Ь; для
    латиницы – кроме I и O (6.17.4). Одно приложение обозначают «ПРИЛОЖЕНИЕ А».
    """
    cfg = cfg or StyleConfig()

    head = doc.add_heading(level=1)
    head.paragraph_format.page_break_before = True
    head.paragraph_format.first_line_indent = Cm(0)
    head.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    head.paragraph_format.space_before = Pt(0)
    head.paragraph_format.space_after = Pt(6)
    head.paragraph_format.keep_with_next = True
    head_run = head.add_run(f"ПРИЛОЖЕНИЕ {str(letter).upper()}")
    set_run_font(head_run, size=cfg.heading_size, bold=True)
    head_run.font.color.rgb = RGBColor(0, 0, 0)

    if status:
        st = doc.add_paragraph()
        st.paragraph_format.first_line_indent = Cm(0)
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        st.paragraph_format.space_before = Pt(0)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = cfg.line_spacing
        st.paragraph_format.keep_with_next = True
        st_run = st.add_run(f"({status})")
        set_run_font(st_run, size=cfg.font_size)

    if title:
        tp = doc.add_paragraph()
        tp.paragraph_format.first_line_indent = Cm(0)
        tp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        tp.paragraph_format.space_before = Pt(0)
        tp.paragraph_format.space_after = Pt(12)
        tp.paragraph_format.line_spacing = cfg.line_spacing
        tp.paragraph_format.keep_with_next = True
        tp_run = tp.add_run(title)
        set_run_font(tp_run, size=cfg.font_size, bold=True)
    return head


def _scale_cover_fonts(paragraphs, tables, size: int) -> None:
    """Привести шрифт скопированного титула к кеглю отчёта (бланк ЛЭТИ – 12 пт)."""
    def fix(paragraph):
        for run in paragraph.runs:
            set_run_font(run, size=size, bold=bool(run.bold), italic=bool(run.italic))

    for paragraph in paragraphs:
        fix(paragraph)
    for table in tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    fix(paragraph)


def task_page(doc, meta: ReportMeta, work_title=None, rows=None, cfg: StyleConfig | None = None,
              page_break=True, signature=True):
    """Страница «ЗАДАНИЕ» – без отдельного .docx-шаблона.

    Собирается из тех же примитивов, что и отчёт: заголовок, подзаголовок
    «на <тип работы>», таблица «поле – значение» и строки для подписей. ФИО
    проверяются так же, как на титуле (см. ``validate_meta_names``).

    ``rows`` – дополнительные строки задания, например
    ``[("Содержание", "1. …; 2. …"), ("Исходные данные", "методичка")]``.
    """
    problems = validate_meta_names(meta)
    if problems:
        raise ValueError("Задание не собрано: " + "; ".join(problems)
                         + ". Спросите у пользователя ФИО и группу.")
    cfg = cfg or StyleConfig()

    head = doc.add_paragraph()
    head.paragraph_format.page_break_before = page_break
    head.paragraph_format.first_line_indent = Cm(0)
    head.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    head.paragraph_format.space_after = Pt(6)
    head.paragraph_format.keep_with_next = True
    set_run_font(head.add_run("ЗАДАНИЕ"), size=cfg.heading_size, bold=True)

    subtitle = (work_title or meta.report_label or "отчёт").strip()
    sub = doc.add_paragraph()
    sub.paragraph_format.first_line_indent = Cm(0)
    sub.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(12)
    sub.paragraph_format.keep_with_next = True
    set_run_font(sub.add_run(f"на {subtitle.lower()}"), size=cfg.font_size)

    fields = [
        ("Студент(ка)", f"{_student_display(meta)}, гр. {meta.group}"),
        ("Тема", (meta.topic or "").strip()),
    ]
    fields.extend(rows if rows is not None else [("Содержание", ""), ("Исходные данные", "")])
    fields.append(("Срок сдачи", (meta.submission_date or "").strip()))
    fields.append(("Руководитель", short_name(meta.teacher)))

    add_table(doc, None, fields, [4.5, 12.0], cfg=cfg, size=cfg.font_size,
              align_left_cols=(1,), spacer=False)

    if signature:
        for label, who in (("Задание выдал", short_name(meta.teacher)),
                           ("Задание принял", _student_display(meta))):
            line = doc.add_paragraph()
            line.paragraph_format.first_line_indent = Cm(0)
            line.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            line.paragraph_format.space_before = Pt(18)
            run = line.add_run(f"{label}: {who} ____________________ (подпись, дата)")
            set_run_font(run, size=cfg.font_size)
    return doc


def annotation(doc, text_ru, text_en=None, keywords=None, cfg: StyleConfig | None = None,
               page_break=True):
    """Страница «Аннотация» и, если передан, блок «Summary».

    По форме ЛЭТИ аннотация занимает 8–10 строк: цель и основное содержание
    работы; ниже – ключевые слова, затем тот же текст по-английски.
    """
    cfg = cfg or StyleConfig()

    head = doc.add_paragraph()
    head.paragraph_format.page_break_before = page_break
    head.paragraph_format.first_line_indent = Cm(0)
    head.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    head.paragraph_format.space_after = Pt(6)
    head.paragraph_format.keep_with_next = True
    set_run_font(head.add_run("Аннотация"), size=cfg.heading_size, bold=True)

    para(doc, str(text_ru).strip(), cfg=cfg)
    if keywords:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(cfg.first_line_indent_cm)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = cfg.line_spacing
        label = p.add_run("Ключевые слова: ")
        set_run_font(label, size=cfg.font_size, bold=True)
        body = p.add_run(str(keywords).strip())
        set_run_font(body, size=cfg.font_size)

    if text_en:
        sub = doc.add_paragraph()
        sub.paragraph_format.first_line_indent = Cm(0)
        sub.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub.paragraph_format.space_before = Pt(12)
        sub.paragraph_format.space_after = Pt(6)
        sub.paragraph_format.keep_with_next = True
        set_run_font(sub.add_run("Summary"), size=cfg.heading_size, bold=True)
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(cfg.first_line_indent_cm)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = cfg.line_spacing
        set_run_font(p.add_run(str(text_en).strip()), size=cfg.font_size)
    return doc


def add_title_page(doc, meta: ReportMeta, cfg: StyleConfig | None = None, template=None):
    """Add the official LETI cover page, cloned from the .docx template.

    ``template`` overrides ``assets/templates/title_page_leti.docx``.
    If the template is missing or cannot be cloned (e.g. it references images
    or hyperlinks), the manual layout below is used as a fallback.

    ФИО и группа проверяются до вставки: без «Фамилия И.О.» и номера группы
    поднимается ValueError – инициалы нельзя придумывать, их должен дать
    пользователь (см. ``validate_meta_names``).
    """
    problems = validate_meta_names(meta)
    if problems:
        raise ValueError(
            "Титульный лист не собран: " + "; ".join(problems)
            + ". Спросите у пользователя полное ФИО (Фамилия Имя Отчество) и номер "
              "группы, затем передайте их в ReportMeta(student=..., teacher=..., "
              "group=...). Придумывать ФИО нельзя."
        )

    cfg = cfg or StyleConfig()
    tpl_path = Path(template) if template else title_template_path()
    if tpl_path.exists():
        body = doc.element.body
        snapshot = list(body.iterchildren())
        try:
            _fill_title_from_template(doc, meta, tpl_path, cfg)
        except Exception:
            # откатить частично вставленный титул, иначе он окажется дважды
            for child in list(body.iterchildren()):
                if child not in snapshot and child.tag != qn("w:sectPr"):
                    body.remove(child)
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
    rows.append(("Руководитель", "", short_name(meta.teacher)))

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
              align_left_cols=(), last_row_bold=False, spacer=True,
              caption: str | None = None, caption_align=None):
    """Таблица в рамке; ``headers=None`` – таблица без строки заголовка."""
    cfg = cfg or StyleConfig()
    size = size or cfg.table_size
    header_size = header_size or cfg.table_header_size

    # Наименование таблицы – над таблицей, в одну строку с номером через тире.
    # ГОСТ 7.32-2017 (6.4.3) ставит его слева без абзацного отступа, ЛЭТИ – по
    # центру; выбор задаёт cfg.table_caption_center или аргумент caption_align.
    if caption:
        align = caption_align or (
            WD_ALIGN_PARAGRAPH.CENTER if cfg.table_caption_center else WD_ALIGN_PARAGRAPH.LEFT)
        cap = doc.add_paragraph()
        cap_fmt = cap.paragraph_format
        cap_fmt.alignment = align
        cap_fmt.first_line_indent = Cm(0)
        cap_fmt.space_before = Pt(6)
        cap_fmt.space_after = Pt(3)
        cap_fmt.line_spacing = cfg.line_spacing
        cap_fmt.keep_with_next = True
        cap_run = cap.add_run(caption)
        set_run_font(cap_run, size=cfg.caption_size)

    ncols = len(headers) if headers else len(widths_cm)
    table = doc.add_table(rows=1 if headers else 0, cols=ncols)
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

    if headers:
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


def add_picture_with_caption(doc, image_path, caption_text, width_cm=15.0,
                             cfg: StyleConfig | None = None):
    """Рисунок по центру и подпись под ним: курсив, без точки в конце."""
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
    text = str(caption_text).rstrip()
    if text.endswith(".") and not text.endswith("..."):
        text = text[:-1]
    r = c.add_run(text)
    set_run_font(r, size=cfg.caption_size, italic=bool(cfg.caption_italic))
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


def report_summary(doc, docx_path, pdf_path=None, cfg: StyleConfig | None = None) -> list[str]:
    """Короткая сводка параметров файла – её показывают пользователю после сборки."""
    cfg = cfg or StyleConfig()
    figures = sum(1 for p in doc.paragraphs if p._p.findall(".//" + qn("w:drawing")))
    return [
        f"Шрифт {cfg.font_name} {cfg.font_size} пт, интервал {cfg.line_spacing:g}, "
        f"абзацный отступ {cfg.first_line_indent_cm:g} см",
        f"Поля L{cfg.margin_left_cm:g} / R{cfg.margin_right_cm:g} / "
        f"T{cfg.margin_top_cm:g} / B{cfg.margin_bottom_cm:g} см, лист "
        f"{cfg.page_width_cm:g}x{cfg.page_height_cm:g} см",
        f"Заголовки {cfg.heading_size} пт, "
        + ("по центру" if cfg.heading_center else "с абзацного отступа"),
        f"Таблиц: {len(doc.tables)}, рисунков: {figures}",
        f"Файлы: {Path(docx_path).name}"
        + (f" + {Path(pdf_path).name}" if pdf_path else ""),
    ]


def save_report(doc, docx_path, pdf_path=None, cfg: StyleConfig | None = None, quiet=False):
    """Сохранить DOCX (и PDF) и напечатать сводку параметров для пользователя."""
    docx_path = Path(docx_path)
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(docx_path))
    if pdf_path:
        export_pdf_via_word(docx_path, pdf_path)
    if not quiet:
        print("Отчёт сохранён:")
        for line in report_summary(doc, docx_path, pdf_path, cfg):
            print(f"  - {line}")
    return str(docx_path)

