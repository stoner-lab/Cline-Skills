# -*- coding: utf-8 -*-
"""Validate a DOCX report produced for the `otchet` skill.

Usage:
    python validate_docx.py report.docx [--pdf report.pdf]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

PRONOUNS = re.compile(
    r"\b(я|мы|мной|нами|наш|наша|наше|наши|рассмотрим|построим|выберем|проверим)\b",
    re.IGNORECASE,
)
TABLE_CAP = re.compile(r"^\s*Таблица\s+(\d+)\b", re.IGNORECASE)
FIG_CAP = re.compile(r"^\s*(?:Рис\.|Рисунок)\s*(\d+)\b", re.IGNORECASE)
APPENDIX_CAP = re.compile(r"^\s*ПРИЛОЖЕНИЕ\s+([^\s]+)")
APPENDIX_BAD_LETTERS = set("ЁЗЙОЧЪЫЬIO")
DECIMAL_DOT = re.compile(r"(?<![\d.])\d+\.\d+(?![\d.])")
DATE_LIKE = re.compile(r"\b(?:0?[1-9]|[12]\d|3[01])\.(?:0?[1-9]|1[0-2])(?:\.\d{2,4})?\b")
PLACEHOLDERS = (
    "0000", "Название кафедры", "Наименование темы",
    "Наименование дисциплины", "Фамилия И.О.",
)


class Report:
    def __init__(self):
        self.fails = []
        self.warns = []
        self.infos = []

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def info(self, msg):
        self.infos.append(msg)

    def show(self):
        for m in self.infos:
            print("INFO:", m)
        for m in self.warns:
            print("WARN:", m)
        for m in self.fails:
            print("FAIL:", m)
        print(f"\nSummary: {len(self.fails)} fail, {len(self.warns)} warn, {len(self.infos)} info")
        return 1 if self.fails else 0


def para_text(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def has_drawing(el):
    return any(True for _ in el.iter(qn("w:drawing")))


def heading_is_bold(p):
    if any(r.bold for r in p.runs):
        return True
    style = p.style
    return bool(style and style.font and style.font.bold)


def effective_alignment(p):
    if p.alignment is not None:
        return p.alignment
    if p.style and p.style.paragraph_format.alignment is not None:
        return p.style.paragraph_format.alignment
    return None


def check_page_setup(doc, rep):
    for i, sec in enumerate(doc.sections, 1):
        w = sec.page_width.cm if sec.page_width else 0
        h = sec.page_height.cm if sec.page_height else 0
        portrait = 20.8 <= w <= 21.1 and 29.5 <= h <= 29.9
        landscape = 29.5 <= w <= 29.9 and 20.8 <= h <= 21.1
        if not (portrait or landscape):
            rep.warn(f"Section {i}: page size {w:.2f} x {h:.2f} cm (expected A4 21 x 29.7 or 29.7 x 21)")
        margins = (sec.left_margin.cm, sec.right_margin.cm, sec.top_margin.cm, sec.bottom_margin.cm)
        expected = (3.0, 1.5, 2.0, 2.0)
        if any(abs(a - b) > 0.15 for a, b in zip(margins, expected)):
            rep.warn(f"Section {i}: margins L/R/T/B = {margins} (expected 3/1.5/2/2)")


def check_styles(doc, rep):
    n = doc.styles["Normal"]
    name = n.font.name
    size = n.font.size.pt if n.font.size else None
    if name and name != "Times New Roman":
        rep.fail(f"Normal font is {name}, expected Times New Roman")
    if size and size not in (12, 13, 14):
        rep.warn(f"Normal font size is {size}, expected 12 (ГОСТ 7.32-2017), 13 or 14 (ЛЭТИ)")
    ls = n.paragraph_format.line_spacing
    if ls is not None and abs(float(ls) - 1.5) > 0.01:
        rep.warn(f"Normal line spacing is {ls}, expected 1.5")
    if n.paragraph_format.alignment != WD_ALIGN_PARAGRAPH.JUSTIFY:
        rep.warn("Normal alignment is not JUSTIFY")


def check_headings(doc, rep):
    heads = [p for p in doc.paragraphs if p.style.name in ("Heading 1", "Heading 2")]
    rep.info(f"Headings: {len(heads)}")
    for p in heads:
        if not p.text.strip():
            continue
        al = effective_alignment(p)
        # ЛЭТИ центрирует заголовки, ГОСТ 7.32-2017 – с абзацного отступа (LEFT).
        if al not in (WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT):
            rep.warn(f"Heading alignment is {al}, expected CENTER (ЛЭТИ) or LEFT (ГОСТ): "
                     f"{p.text[:60]!r}")
        if not heading_is_bold(p):
            rep.warn(f"Heading not bold: {p.text[:60]!r}")
    for p in heads:
        if p.style.name == "Heading 1" and not re.match(r"^\d+\.\s", p.text.strip()):
            if p.text.strip().lower() not in (
                "цель работы", "постановка задачи и исходные данные",
                "выводы", "заключение", "содержание",
                "список использованных источников",
                "список источников",
            ):
                rep.info(f"Heading 1 without number: {p.text[:60]!r}")


def check_captions_and_tables(doc, rep):
    children = list(doc.element.body.iterchildren())
    first_heading = len(children)
    for i, el in enumerate(children):
        if el.tag.endswith("}p"):
            texts = "".join(t.text or "" for t in el.iter(qn("w:t")))
            styles = el.findall(".//" + qn("w:pStyle"))
            style_ids = [s.get(qn("w:val")) for s in styles]
            if any(s in ("Heading1", "Heading2", "1", "2") for s in style_ids):
                first_heading = i
                break

    table_caps = []
    fig_caps = []
    for idx, el in enumerate(children):
        tag = el.tag.split("}")[-1]
        if tag == "tbl":
            if idx < first_heading:
                continue
            prev = children[idx - 1] if idx > 0 else None
            prev_text = para_text(prev).strip() if prev is not None and prev.tag.endswith("}p") else ""
            if not TABLE_CAP.match(prev_text):
                rep.warn(f"Table without caption above (previous text: {prev_text[:50]!r})")
            else:
                table_caps.append(int(TABLE_CAP.match(prev_text).group(1)))
        if tag == "p":
            text = para_text(el).strip()
            m = FIG_CAP.match(text)
            if m:
                fig_caps.append(int(m.group(1)))
                prev = children[idx - 1] if idx > 0 else None
                if prev is None or not has_drawing(prev):
                    rep.warn(f"Figure caption without image above: {text[:60]!r}")

    for label, nums in (("Table", table_caps), ("Figure", fig_caps)):
        if nums:
            rep.info(f"{label} captions: {len(nums)} (numbers: {nums[:8]}{'...' if len(nums) > 8 else ''})")
            if nums != list(range(1, len(nums) + 1)):
                rep.fail(f"{label} numbering is not continuous: {nums}")

    pos_by_tbl = {id(el): idx for idx, el in enumerate(children) if el.tag.endswith("}tbl")}
    for ti, table in enumerate(doc.tables, 1):
        if pos_by_tbl.get(id(table._tbl), 0) < first_heading:
            continue
        if table.style is None or "Grid" not in (table.style.name or ""):
            rep.warn(f"Table {ti}: style is {table.style.name if table.style else None}, expected Table Grid")
        if len(table.rows) > 1:
            header_runs = [r for c in table.rows[0].cells for p in c.paragraphs for r in p.runs if r.text.strip()]
            if header_runs and not any(r.bold for r in header_runs):
                rep.warn(f"Table {ti}: header row is not bold")


def check_personal_style(doc, rep):
    found = []
    for p in doc.paragraphs:
        for m in PRONOUNS.finditer(p.text):
            found.append((m.group(0), p.text[:80]))
    if found:
        for word, line in found[:10]:
            rep.fail(f"First-person word {word!r}: {line!r}")
    else:
        rep.info("No first-person pronouns/verbs found")


def check_placeholders_and_numbers(doc, rep):
    body_parts = []
    for p in doc.paragraphs:
        if p.style.name in ("Heading 1", "Heading 2"):
            continue
        if re.search(r"\b(пункт|раздел|глава|рис\.|табл\.|таблица|рисунок)", p.text, re.IGNORECASE):
            continue
        body_parts.append(p.text)
    all_text = "\n".join(body_parts)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_text += "\n" + cell.text
    for ph in PLACEHOLDERS:
        if ph == "0000":
            hit = re.search(r"(?<![\d,])0000(?![\d,])", all_text)
            if hit:
                rep.warn(f"Placeholder still present: {ph!r}")
        elif ph in all_text:
            rep.warn(f"Placeholder still present: {ph!r}")
    # номера стандартов (ГОСТ 7.32-2017, ГОСТ Р 7.0.5-2008) – не десятичные дроб
    all_text_no_std = re.sub(r"(?i)ГОСТ(?:\s+Р)?\s*\d+(?:[.,]\d+)*", " ", all_text)
    dots = DECIMAL_DOT.findall(DATE_LIKE.sub(" ", all_text_no_std))
    if dots:
        rep.warn(f"Decimal dots found (use comma): {dots[:10]}")


def check_dashes(doc, rep):
    """Em dash запрещён: в тексте только en dash с пробелами (format.md §3.1)."""
    hits = []
    for p in doc.paragraphs:
        if "—" in p.text:
            hits.append(p.text.strip()[:60])
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if "—" in cell.text:
                    hits.append(cell.text.strip()[:60])
    if hits:
        rep.warn(f"Em dash «—» found {len(hits)} time(s), use « – »: {hits[:3]}")
    else:
        rep.info("No em dashes")


LINK_TEXT_RE = re.compile(r"(?:https?://|www\.)[^\s<>\"«»]+|doi:\s*10\.\d{4,9}/\S+",
                          re.IGNORECASE)


def _unlinked_runs_text(p_el):
    """Текст абзаца, который лежит вне элементов w:hyperlink."""
    chunks = []
    for child in p_el.iterchildren():
        if child.tag == qn("w:hyperlink"):
            continue
        if child.tag == qn("w:r"):
            chunks.append("".join(t.text or "" for t in child.iter(qn("w:t"))))
    return "".join(chunks)


def check_links(doc, rep):
    """Адреса в отчёте должны быть настоящими гиперссылками, а не текстом.

    Ссылка, набранная обычным run'ом, не кликается ни в Word, ни в PDF, поэтому
    это ошибка, а не предупреждение.
    """
    total = 0
    dead = []
    for p in doc.paragraphs:
        total += len(p._p.findall(qn("w:hyperlink")))
        for match in LINK_TEXT_RE.finditer(_unlinked_runs_text(p._p)):
            dead.append(match.group(0)[:70])
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    total += len(p._p.findall(qn("w:hyperlink")))
                    for match in LINK_TEXT_RE.finditer(_unlinked_runs_text(p._p)):
                        dead.append(match.group(0)[:70])
    if dead:
        for url in dead[:10]:
            rep.fail(f"URL is plain text, not a hyperlink: {url!r}")
    if total:
        rep.info(f"Hyperlinks: {total}")
    else:
        rep.info("Hyperlinks: none")
    return total


def check_appendices(doc, rep):
    """Приложения по ГОСТ 7.32-2017 (6.17).

    Обозначение – прописная буква, кроме Ё, З, Й, О, Ч, Ъ, Ы, Ь (и I, O в
    латинице); заголовок должен быть стилем Heading 1, иначе приложение не
    попадёт в содержание, как требует 6.17.7.
    """
    letters = []
    for p in doc.paragraphs:
        match = APPENDIX_CAP.match(p.text.strip())
        if not match:
            continue
        letter = match.group(1)
        letters.append(letter)
        if letter in APPENDIX_BAD_LETTERS or letter.lower() in APPENDIX_BAD_LETTERS:
            rep.fail(f"Appendix letter {letter!r} is not allowed by GOST 7.32-2017 (6.17.4)")
        if p.style.name != "Heading 1":
            rep.warn(f"Appendix {letter!r} is not Heading 1, it will not appear in the contents")
    if letters:
        if len(set(letters)) != len(letters):
            rep.fail(f"Duplicate appendix letters: {letters}")
        rep.info(f"Appendices: {', '.join(letters)}")
    else:
        rep.info("Appendices: none")


def check_footer_page_numbers(doc, rep):
    for i, sec in enumerate(doc.sections, 1):
        xml = sec.footer._element.xml
        if "PAGE" not in xml:
            rep.fail(f"Section {i}: footer has no PAGE field")


def check_pdf(pdf_path, rep, docx_links=0):
    try:
        import pypdfium2 as pdfium
    except ImportError:
        rep.info("pypdfium2 not installed; PDF page check skipped")
    else:
        pdf = pdfium.PdfDocument(str(pdf_path))
        rep.info(f"PDF pages: {len(pdf)}")
        for i in range(len(pdf)):
            text = pdf[i].get_textpage().get_text_range().strip()
            if len(re.sub(r"\s", "", text)) < 5:
                rep.fail(f"PDF page {i + 1} looks blank")
        check_pdf_fonts(pdf_path, rep)
    check_pdf_links(pdf_path, rep, docx_links)


def check_pdf_links(pdf_path, rep, docx_links=0):
    """Ссылки в PDF должны остаться кликабельными (/Link аннотации)."""
    try:
        from pypdf import PdfReader
    except ImportError:
        rep.info("pypdf not installed; PDF link check skipped")
        return
    reader = PdfReader(str(pdf_path))
    total = 0
    for page in reader.pages:
        for ref in page.get("/Annots") or []:
            try:
                obj = ref.get_object()
            except Exception:                      # noqa: BLE001
                continue
            if obj.get("/Subtype") == "/Link":
                total += 1
    if total:
        rep.info(f"PDF links: {total}")
    elif docx_links:
        rep.fail(f"DOCX has {docx_links} hyperlink(s), but the PDF has none")
    else:
        rep.info("PDF links: none")


def check_pdf_fonts(pdf_path, rep):
    """Embedded fonts keep Times New Roman intact on the checker's machine."""
    try:
        from pypdf import PdfReader
    except ImportError:
        rep.info("pypdf not installed; font embedding check skipped")
        return
    reader = PdfReader(str(pdf_path))
    fonts = {}
    for page in reader.pages:
        resources = page.get("/Resources") or {}
        for ref in (resources.get("/Font") or {}).values():
            font = ref.get_object()
            fonts.setdefault(font.get("/BaseFont"), font)
    missing = []
    for name, font in fonts.items():
        descriptors = []
        if font.get("/FontDescriptor"):
            descriptors.append(font["/FontDescriptor"])
        for descendant in font.get("/DescendantFonts") or []:
            obj = descendant.get_object()
            if obj.get("/FontDescriptor"):
                descriptors.append(obj["/FontDescriptor"])
        embedded = any(
            any(key in desc.get_object() for key in ("/FontFile", "/FontFile2", "/FontFile3"))
            for desc in descriptors
        )
        if not embedded:
            missing.append(str(name))
    if missing:
        rep.warn("PDF fonts are not embedded, viewer may substitute them: " + ", ".join(missing))
    else:
        rep.info(f"PDF fonts embedded: {len(fonts)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--pdf", default=None)
    args = ap.parse_args()

    path = Path(args.docx)
    if not path.exists():
        print("FAIL: file not found:", path)
        return 1

    doc = Document(str(path))
    rep = Report()
    check_page_setup(doc, rep)
    check_styles(doc, rep)
    check_headings(doc, rep)
    check_captions_and_tables(doc, rep)
    check_personal_style(doc, rep)
    check_placeholders_and_numbers(doc, rep)
    check_dashes(doc, rep)
    check_footer_page_numbers(doc, rep)
    check_appendices(doc, rep)
    links = check_links(doc, rep)
    if args.pdf:
        check_pdf(args.pdf, rep, links)
    return rep.show()


if __name__ == "__main__":
    sys.exit(main())

