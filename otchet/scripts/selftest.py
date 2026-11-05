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
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from docx import Document
from docx.oxml.ns import qn

from docx_helpers import (ReportMeta, add_references, add_table, add_title_page, annotation,
                          appendix, formula, heading, para, save_report, setup_document,
                          short_name, task_page, title_template_path, validate_meta_names)
from strip_metadata import clean as clean_metadata
from strip_metadata import inspect as metadata_findings

PLACEHOLDERS = ("<кафедра>", "<номер>", "<дисциплина>", "<тема>", "<вариант>",
                "<пункты>", "<дата>", "<группа>", "<Фамилия И.О.>",
                "<Фамилия И.О. студента>", "<Фамилия И.О. руководителя>",
                "<город>", "<год>")

AUTHOR = "Иванов И.И."
TITLE = "ПР-1"

SOURCES = [
    "Proceset – платформа процессной аналитики [Электронный ресурс]. – URL: "
    "https://infomaximum.ru/product/ (дата обращения: 01.11.2026).",
    "Документация Python [Электронный ресурс]. – URL: https://docs.python.org/3/.",
]


def build(path: Path, pdf: bool):
    doc = setup_document(title=TITLE, author=AUTHOR)
    meta = ReportMeta(
        department="ИС",
        report_label="ОТЧЕТ",
        work_line="по заданию № 1",
        discipline="Тестовая дисциплина",
        topic="Проверка шаблона титульного листа",
        variant="2",
        group="4395",
        student=AUTHOR,
        teacher="Петров П.П.",
        completed_items="1, 2",
        submission_date="05.11.2026",
    )
    add_title_page(doc, meta)
    task_page(doc, meta, rows=[("Содержание", "1. Проверка; 2. Выводы")])
    annotation(doc, "Цель работы – проверить шаблон отчёта.",
               text_en="The purpose is to test the report template.",
               keywords="шаблон, проверка")
    heading(doc, "1. Проверка")
    para(doc, "Текст проверки, подробнее: https://example.org/method.")
    formula(doc, [("E", None), ("=", None), ("mc", "sup"), ("2", None)], number=1)
    add_table(doc, ["Показатель", "Значение"], [["Первый", "10"]], [8.0, 8.5],
              caption="Таблица 1 – Проверочные значения")
    add_references(doc, SOURCES)
    appendix(doc, "А", "Пример оформления", status="справочное")
    para(doc, "Текст приложения.")
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

    # ГОСТ 7.32-2017: приложение, нумерованная формула, наименование таблицы
    if "ПРИЛОЖЕНИЕ А" not in new_lines:
        problems.append("нет заголовка «ПРИЛОЖЕНИЕ А» (appendix())")
    if not any("(1)" in line for line in new_lines):
        problems.append("нет номера формулы «(1)» (formula(..., number=1))")
    if not any(line.startswith("Таблица 1") for line in new_lines):
        problems.append("нет наименования таблицы «Таблица 1 …»")

    # строки шаблона, которых раньше не было в .docx
    if "Вариант 2" not in new_lines:
        problems.append("нет строки «Вариант 2» на титуле")
    if not any(line.startswith("Выполненные пункты: 1, 2") for line in new_lines):
        problems.append("нет строки «Выполненные пункты» на титуле")
    if not any(line.startswith("Дата сдачи работы на проверку") for line in new_lines):
        problems.append("нет строки «Дата сдачи работы на проверку» на титуле")

    # страницы «ЗАДАНИЕ» и «Аннотация» собираются хелперами, а не шаблоном
    if "ЗАДАНИЕ" not in new_lines:
        problems.append("нет страницы «ЗАДАНИЕ» (task_page())")
    if "на отчёт" not in new_lines and "на отчет" not in new_lines:
        problems.append("нет подзаголовка «на отчёт» на странице задания")
    if "Аннотация" not in new_lines:
        problems.append("нет страницы «Аннотация» (annotation())")
    if "Summary" not in new_lines:
        problems.append("нет блока «Summary»")
    if not any(line.startswith("Ключевые слова:") for line in new_lines):
        problems.append("нет строки «Ключевые слова»")

    # metadata must not name the generator (python-docx, ReportLab, LibreOffice...)
    pdf_path = path.with_suffix(".pdf")
    for target in (path, pdf_path):
        if not target.exists():
            continue
        found = metadata_findings(target)
        if found:
            problems.append(f"в метаданных {target.suffix} следы генератора: "
                            + "; ".join(found))

    # links must be real hyperlinks, and must survive the PDF export
    docx_links = len(list(new.element.body.iter(qn("w:hyperlink"))))
    if docx_links < len(SOURCES):
        problems.append(f"ссылок в DOCX {docx_links}, ожидалось минимум {len(SOURCES)}")
    with zipfile.ZipFile(path) as archive:
        rels = archive.read("word/_rels/document.xml.rels").decode("utf-8")
    if 'TargetMode="External"' not in rels:
        problems.append("в DOCX нет внешних связей: адреса не кликаются")
    if "infomaximum.ru" not in rels:
        problems.append("адрес источника не попал в связи DOCX")

    if pdf_path.exists():
        try:
            import pypdf
            reader = pypdf.PdfReader(str(pdf_path))
            if len(reader.pages) < 2:
                problems.append(f"в PDF {len(reader.pages)} страниц, ожидалось минимум 2")
            pdf_links = 0
            for page in reader.pages:
                for ref in page.get("/Annots") or []:
                    try:
                        if ref.get_object().get("/Subtype") == "/Link":
                            pdf_links += 1
                    except Exception:                  # noqa: BLE001
                        continue
            if docx_links and not pdf_links:
                problems.append(f"в DOCX {docx_links} гиперссылок, а в PDF нет ни одной аннотации /Link")
            text = "".join((page.extract_text() or "") for page in reader.pages)
            if not text.strip():
                problems.append("из PDF не извлекается текст (шрифты/кодировка)")
            elif "Иванов" not in text:
                problems.append("в тексте PDF нет фамилии студента")
        except Exception as exc:                       # noqa: BLE001
            problems.append(f"PDF не читается: {type(exc).__name__}: {exc}")

    return problems


def check_names():
    """ФИО всегда «Фамилия И.О.»; без данных сборка падает, а не выдумывает."""
    problems = []
    for raw, expected in (("Нгуен Тхе", "Нгуен Т."),
                          ("Нгуен Тхе Зуй", "Нгуен Т.З."),
                          ("Иванов И.И.", "Иванов И.И."),
                          ("Петров Пётр Петрович", "Петров П.П.")):
        got = short_name(raw)
        if got != expected:
            problems.append(f"short_name({raw!r}) = {got!r}, ожидалось {expected!r}")

    empty = ReportMeta(student="", teacher="", group="")
    if len(validate_meta_names(empty)) < 3:
        problems.append("validate_meta_names не поймал пустые ФИО и группу")
    junk = ReportMeta(student="<Фамилия И.О.>", teacher="Иванов", group="4395")
    if len(validate_meta_names(junk)) < 2:
        problems.append("validate_meta_names не поймал плейсхолдер и фамилию без инициалов")

    try:
        add_title_page(setup_document(), empty)
    except ValueError:
        pass
    else:
        problems.append("add_title_page не упал на пустых ФИО")

    # work_line не должен дублировать строку «по дисциплине» на титуле
    dup = ReportMeta(student="Иванов И.И.", teacher="Петров П.П.", group="4395",
                     discipline="Тестовая дисциплина", topic="Тема",
                     work_line="по дисциплине «Тестовая дисциплина»")
    title_doc = setup_document()
    add_title_page(title_doc, dup)
    lines = [p.text.strip().lower() for p in title_doc.paragraphs]
    if sum(1 for line in lines if line.startswith("по дисциплине")) != 1:
        problems.append("строка «по дисциплине» на титуле печатается дважды")

    # пустой список источников не должен создавать пустой раздел
    try:
        add_references(setup_document(), [])
    except ValueError:
        pass
    else:
        problems.append("add_references([]) не упал: пустой раздел источников недопустим")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", action="store_true", help="также собрать PDF через Word")
    args = ap.parse_args()

    tpl = title_template_path()
    if not tpl.exists():
        print(f"FAIL: шаблон не найден: {tpl}")
        return 1

    problems = check_names()
    if problems:
        print("FAIL:")
        for problem in problems:
            print("  -", problem)
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
          f"метаданные чистые, ссылки кликабельные"
          + (", PDF собран" if args.pdf else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
