# Title page assets

`title_page_leti.docx` is the **source of truth** for the cover page. It uses the
LETI layout and contains only placeholders:

- `<кафедра>` — department line, dropped when `department` is empty
- `<номер>` — the work number inside the `по практической работе №…` line
- `<дисциплина>` — inside `по дисциплине «…»`
- `<тема>` — inside `Тема: …`
- `<вариант>` — inside `Вариант …`, dropped when `variant` is empty
- `<группа>` — inside `Студент гр. …`
- `<Фамилия И.О. студента>`, `<Фамилия И.О. руководителя>` — the two signature cells
- `<город>`, `<год>` — the last two lines

`<пункты>` and `<дата>` are **not** in the template on purpose: `completed_items`
and `submission_date` are optional. When either is set, `_fill_title_from_template()`
inserts the line under the signature table itself (bold, centred, 12 pt above) and
takes the space from the gap over «ОТЧЕТ», so the cover still fits one page. A custom
template that keeps `<пункты>` / `<дата>` is filled in place instead of getting a
second copy.

It contains no personal data. The signature block is a 2x3 table with real bottom
borders in the middle column, not underscore characters.

`add_title_page()` **clones this file's XML** into the report and only replaces
the placeholders, so the generated cover matches the template exactly. To change
the cover (other institution, extra lines, different spacing), edit this .docx –
no code changes are needed. The programmatic layout in `_add_title_page_manual()`
is used only as a fallback when the template is missing or cannot be cloned
(e.g. it contains images or hyperlinks). Override the folder with:

```powershell
$env:OTCHET_TEMPLATES = "D:\my-templates"
```

or pass a file explicitly: `add_title_page(doc, meta, template="cover.docx")`.

Older templates that used `<Фамилия И.О.>` in both cells, `Санкт-Петербург` and a
bare year still work: `_fill_title_from_template()` keeps those branches as
fallbacks.

`scripts/selftest.py` fills the template with `variant`, `completed_items` and
`submission_date` set and fails if a placeholder survives, so the template and
the code cannot drift apart unnoticed.

If you redistribute the skill publicly, replace the LETI-specific lines with your
own institution's title-page layout or confirm that you have permission to
redistribute the template.
