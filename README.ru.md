# Cline Skills

Коллекция навыков (skills) для ИИ-агентов, адаптированных для **Cline на Windows**,
плюс несколько написанных здесь. Источники:
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[pbakaus/impeccable](https://github.com/pbakaus/impeccable),
[iart-ai/manim-skills](https://github.com/iart-ai/manim-skills),
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) и
[tt-a1i/archify](https://github.com/tt-a1i/archify). Навыки из `anthropics/skills`
здесь **не публикуются** по лицензионным причинам — см. примечание под таблицей.

Каждый навык это папка с `SKILL.md` (YAML frontmatter и инструкции) и, при необходимости,
`scripts/`, `references/`, `assets/`. Скопируйте папку в `C:\Users\<user>\.cline\skills\` и
перезапустите Cline или начните новую задачу, чтобы список навыков перечитался. Вызывать
навык можно по имени или просто описав задачу: в `description` есть вьетнамские, русские и
английские фразы-триггеры.

**Языки:** [English](README.md) | [Русский](README.ru.md) | [Tiếng Việt](README.vi.md)

## Навыки

| Навык | Что делает | Источник |
|---|---|---|
| `otchet` | Учебные отчёты (ПР, лабораторная, реферат, курсовая): титульный лист ЛЭТИ, Times New Roman 14, подписи, правила DOCX и PDF | этот репозиторий |
| `injection-scan` | Офлайн-сканер prompt injection для недоверенного текста и документов (docx, pdf, pptx, xlsx, zip), коды возврата 0 чисто, 1 проверить или не просканировано, 2 блокировать | этот репозиторий |
| `archify` | Превращает идею, план, Mermaid или кодовую базу в проверенную автономную HTML-схему (архитектура, процесс, последовательность, поток данных, состояния, ERD, классы, дерево, таймлайн, waterfall) или в объяснение на одной странице | адаптирован из tt-a1i/archify |
| `impeccable` | Дизайн-направление фронтенда, аудит, критика и переделка, библиотека плейбуков и детектор дизайна | адаптирован из pbakaus/impeccable |
| `design-taste-frontend` | Сайты компаний уровня figma.com и x.ai, проверяются собственным headless-браузерным чекером | адаптирован из Leonxlnx/taste-skill |
| `manim` | Анимации по математике и физике на Manim CE, рендер в MP4 или GIF | адаптирован из iart-ai/manim-skills |
| `git-workflow-and-versioning` | Ветки, атомарные коммиты, сообщения коммитов, pull request, семантическое версионирование | адаптирован из addyosmani/agent-skills |
| `documentation-and-adrs` | Architecture decision records и документация, которая сохраняет код читаемым | адаптирован из addyosmani/agent-skills |
| `code-review-and-quality` | Многоаспектное ревью перед merge: корректность, дизайн, ошибки, тесты, безопасность | адаптирован из addyosmani/agent-skills |

Здесь нет: `docx`, `pdf`, `pptx`, `xlsx`, `frontend-design`, `mcp-builder` и
`skill-creator`. Они взяты из `anthropics/skills`, где `LICENSE.txt` сохраняет все
права и запрещает воспроизведение, производные работы и распространение, поэтому они
лежат в **приватном** репозитории и не публикуются здесь. Установленные копии
продолжают работать локально.

## Что значит "адаптирован"

Каждый адаптированный навык начинается с раздела **Cline runtime notes**: имена
инструментов заменены на Cline (`read_files`, `editor`, `run_commands`, `search_codebase`),
указана реальная папка навыка и как от неё считаются пути, что установлено на этой машине,
PowerShell вместо Bash, без субагентов, а в `description` добавлены вьетнамские и русские
фразы-триггеры.

Адаптация воспроизводима, а не правится вручную: `upstream.json` фиксирует коммит каждого
источника, `tools/adapt_config.json` хранит описание, файл заметок, замены и список
сохраняемых файлов, `tools/notes/*.md` содержит заметки для Cline, а
`tools/sync_upstream.py` (`check`, `apply`, `status`, `add`) пересобирает `SKILL.md`.

## Требования

- Cline в VS Code или приложение Cline Desktop; навыки лежат в `~/.cline/skills`.
- Node 18 или новее для `archify` и `design-taste-frontend`.
- Python 3.11 или новее с `python-docx`, `python-pptx`, `openpyxl`, `pypdf`, `reportlab`,
  `lxml` для `docx`, `pptx`, `xlsx`, `pdf`, `otchet`.

## Лицензия

Условия уровня репозитория — в [`LICENSE`](LICENSE): файлы, написанные здесь, под MIT.
Навыки, взятые из других проектов, сохраняют свои лицензии, и эти условия действуют
для данной копии.

> Важно: `docx`, `pdf`, `pptx`, `xlsx`, `frontend-design`, `mcp-builder` и
> `skill-creator` взяты из `anthropics/skills`; их `LICENSE.txt` сохраняет все права и
> запрещает воспроизведение, производные работы и распространение. Поэтому их нет в
> этом репозитории: адаптированные копии лежат в приватном репозитории, а
> установленные — в `~/.cline/skills` на рабочей машине.
