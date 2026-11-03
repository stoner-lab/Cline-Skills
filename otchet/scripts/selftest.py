# -*- coding: utf-8 -*-
"""Smoke test for the `otchet` skill.

Checks that the cover is cloned from ``assets/templates/title_page_leti.docx``,
that placeholders are replaced and that helpers/export work:

    python scripts/selftest.py          # DOCX only
    python scripts/selftest.py --pdf    # DOCX + PDF via Word (PDF/A)
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from docx import Document

from docx_helpers import (ReportMeta, add_title_page, heading, para, save_report,
                          setup_document, title_template_path)
from strip_metadata import clean as clean_metadata
from strip_metadata import inspect as metadata_findings

PLACEHOLDERS = ("<кафедра>", "<номер>", "<дисциплина>", "<тема>", "<пункты>",
                "<дата>", "<группа>", "<Фамилия И.О.>")

AUTHOR = "Иванов И.И."
TITLE = "ПР-1"


def build(path: Path, pdf: bool):
    doc = setup_document(title=TITLE, author=AUTHOR)
    meta = ReportMeta(
        department="ИС",
        report_label="ОТЧЕТ",
        work_line="по заданию № 1",
        discipline="Тестовая дисциплина",
        topic="Проверка шаблона титульного листа",
        group="4395",
        student=AUTHOR,
        teacher="Петров П.П.",
    )
    add_title_page(doc, meta)
    heading(doc, "1. Проверка")
    para(doc, "Текст проверки.")
    save_report(doc, path, pdf_path=path.with_suffix(".pdf") if pdf else None)

    # the delivery pipeline ends with clean metadata, so the test must prove it
    clean_metadata(path, AUTHOR, TITLE)
    if pdf and path.with_suffix(".pdf").exists():
        clean_metadata(path.with_suffix(".pdf"), AUTHOR, TITLE)



def check(path: Path):
    tpl = Document(str(title_template_path()))
    new = Document(str(path))
    problems = []

    tpl_lines = [p.text.strip() for p in tpl.paragraphs]
    new_lines = [p.text.strip() for p in new.paragraphs]

    for line in tpl_lines[:4]:
        if line not in new_lines:
            problems.append(f"нет строки вуза: {line}")
    if not any(line.startswith("Кафедра") for line in new_lines):
        problems.append("нет строки кафедры")
    for placeholder in PLACEHOLDERS:
        if any(placeholder in line for line in new_lines):
            problems.append(f"не заменён плейсхолдер {placeholder}")

    if not new.tables:
        problems.append("нет таблицы подписей")
    else:
        table = new.tables[0]
        rows, cols = len(table.rows), len(table.columns)
        if (rows, cols) != (2, 3):
            problems.append(f"таблица подписей {rows}x{cols}, ожидалось 2x3")
        else:
            first = [c.text.strip() for c in table.rows[0].cells]
            second = [c.text.strip() for c in table.rows[1].cells]
            if "Иванов И.И." not in first:
                problems.append("в таблице нет фамилии студента")
            if "Петров П.П." not in second:
                problems.append("в таблице нет фамилии руководителя")

    section = new.sections[0]
    if section.different_first_page_header_footer is not True:
        problems.append("титул получит номер страницы (titlePg выключен)")
    if "PAGE" not in section.footer.paragraphs[0]._p.xml:
        problems.append("в колонтитуле нет поля PAGE")

    # metadata must not name the generator (python-docx, ReportLab, LibreOffice...)
    pdf_path = path.with_suffix(".pdf")
    for target in (path, pdf_path):
        if not target.exists():
            continue
        found = metadata_findings(target)
        if found:
            problems.append(f"в метаданных {target.suffix} следы генератора: "
                            + "; ".join(found))

    if pdf_path.exists():
        try:
            import pypdf
            reader = pypdf.PdfReader(str(pdf_path))
            if len(reader.pages) < 2:
                problems.append(f"в PDF {len(reader.pages)} страниц, ожидалось минимум 2")
            text = "".join((page.extract_text() or "") for page in reader.pages)
            if not text.strip():
                problems.append("из PDF не извлекается текст (шрифты/кодировка)")
            elif "Иванов" not in text:
                problems.append("в тексте PDF нет фамилии студента")
        except Exception as exc:                       # noqa: BLE001
            problems.append(f"PDF не читается: {type(exc).__name__}: {exc}")

    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true", help="также собрать PDF через Word")
    args = ap.parse_args()

    tpl = title_template_path()
    if not tpl.exists():
        print(f"FAIL: шаблон не найден: {tpl}")
        return 1

    tmp = Path(tempfile.mkdtemp())
    docx_path = tmp / "selftest.docx"
    build(docx_path, args.pdf)

    problems = check(docx_path)
    if args.pdf and not docx_path.with_suffix(".pdf").exists():
        problems.append("PDF не создан")

    if problems:
        print("FAIL:")
        for problem in problems:
            print("  -", problem)
        return 1

    print(f"OK: {tpl.name} – титул собран, плейсхолдеры заменены, "
          f"метаданные чистые" + (", PDF собран" if args.pdf else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
