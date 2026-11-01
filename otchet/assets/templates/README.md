# Title page assets

`title_page_leti.docx` is the **source of truth** for the cover page. It uses the
LETI layout and contains only placeholders:

- `<кафедра>`
- `<номер>`
- `<дисциплина>`
- `<тема>`
- `<группа>`
- `<Фамилия И.О.>`
- `<дата>`
- `<пункты>`

It contains no personal data. The signature block is a 2x3 table (equal columns,
1.08 cm rows) with real bottom borders in the middle column, not underscore
characters.

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

If you redistribute the skill publicly, replace the LETI-specific lines with
your own institution's title-page layout or confirm that you have permission
to redistribute the template.

If you redistribute the skill publicly, replace the LETI-specific lines with
your own institution's title-page layout or confirm that you have permission
to redistribute the template.
