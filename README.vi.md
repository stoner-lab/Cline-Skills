# Cline Skills

Bộ sưu tập skill cho AI agent, được **adapt cho Cline trên Windows** từ nhiều nền tảng:
[anthropics/skills](https://github.com/anthropics/skills),
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[pbakaus/impeccable](https://github.com/pbakaus/impeccable),
[iart-ai/manim-skills](https://github.com/iart-ai/manim-skills),
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) và
[tt-a1i/archify](https://github.com/tt-a1i/archify), cùng vài skill viết tại đây.

Mỗi skill là một thư mục có `SKILL.md` (YAML frontmatter + hướng dẫn) và tuỳ chọn
`scripts/`, `references/`, `assets/`. Copy thư mục vào `C:\Users\<user>\.cline\skills\`
rồi khởi động lại Cline hoặc mở task mới để danh sách skill được nạp lại. Gọi skill theo
tên, hoặc chỉ cần mô tả việc cần làm: phần `description` đã có trigger tiếng Việt, tiếng Nga
và tiếng Anh.

**Ngôn ngữ:** [English](README.md) | [Русский](README.ru.md) | [Tiếng Việt](README.vi.md)

## Danh sách skill

| Skill | Việc nó làm | Nguồn |
|---|---|---|
| `otchet` | Báo cáo học tập tiếng Nga (ПР, лабораторная, реферат, курсовая): trang bìa LETI, Times New Roman 14, chú thích hình bảng, quy tắc DOCX và PDF | repo này |
| `injection-scan` | Quét prompt injection offline cho văn bản và tài liệu không tin cậy (docx, pdf, pptx, xlsx, zip), exit code 0 sạch, 1 cần xem hoặc chưa quét, 2 chặn | repo này |
| `archify` | Biến ý tưởng, kế hoạch, Mermaid hoặc codebase thành sơ đồ HTML standalone đã validate (kiến trúc, quy trình, tuần tự, luồng dữ liệu, trạng thái, ERD, lớp, cây, timeline, waterfall) hoặc một trang giải thích | adapt từ tt-a1i/archify |
| `skill-creator` | Tạo, test, benchmark và đóng gói skill mới | adapt từ anthropics/skills |
| `impeccable` | Định hướng thiết kế frontend, audit, phê bình và viết lại, kèm thư viện playbook và design detector | adapt từ pbakaus/impeccable |
| `design-taste-frontend` | Website công ty ở mức figma.com và x.ai, được kiểm bằng checker headless browser của chính nó | adapt từ Leonxlnx/taste-skill |
| `frontend-design` | Hướng dẫn thị giác để giao diện không trông như template | adapt từ anthropics/skills |
| `docx` | Tạo, đọc và sửa tài liệu Word | adapt từ anthropics/skills |
| `xlsx` | Tạo, đọc, sửa và làm sạch bảng tính | adapt từ anthropics/skills |
| `pptx` | Tạo, đọc và sửa bài trình chiếu | adapt từ anthropics/skills |
| `pdf` | Đọc, trích xuất, gộp, tách, điền form và tạo PDF | adapt từ anthropics/skills |
| `manim` | Video minh hoạ toán và vật lý bằng Manim CE, xuất MP4 hoặc GIF | adapt từ iart-ai/manim-skills |
| `mcp-builder` | Viết MCP server bằng Python hoặc Node | adapt từ anthropics/skills |
| `git-workflow-and-versioning` | Nhánh, commit nguyên tử, commit message, pull request, semantic versioning | adapt từ addyosmani/agent-skills |
| `documentation-and-adrs` | Architecture decision record và tài liệu giữ codebase dễ đọc | adapt từ addyosmani/agent-skills |
| `code-review-and-quality` | Review nhiều chiều trước khi merge: tính đúng, thiết kế, lỗi, test, bảo mật | adapt từ addyosmani/agent-skills |

## "Adapt" nghĩa là gì

Mỗi skill đã adapt mở đầu bằng mục **Cline runtime notes**: tên tool được ánh xạ sang Cline
(`read_files`, `editor`, `run_commands`, `search_codebase`), nêu đúng thư mục skill và cách
tính đường dẫn từ đó, liệt kê những gì đã có trên máy này, dùng PowerShell thay Bash, bỏ phụ
thuộc subagent, và thêm trigger tiếng Việt cùng tiếng Nga vào `description`.

Việc adapt là tái lập được, không sửa tay: `upstream.json` ghim commit của từng nguồn,
`tools/adapt_config.json` giữ mô tả, file notes, các thay thế và danh sách file cần giữ,
`tools/notes/*.md` chứa ghi chú cho Cline, và `tools/sync_upstream.py`
(`check`, `apply`, `status`, `add`) sinh lại `SKILL.md` từ các đầu vào đó.

## Yêu cầu

- Cline trong VS Code hoặc app Cline Desktop; skill nằm ở `~/.cline/skills`.
- Node 18 trở lên cho `archify` và `design-taste-frontend`.
- Python 3.11 trở lên với `python-docx`, `python-pptx`, `openpyxl`, `pypdf`, `reportlab`,
  `lxml` cho `docx`, `pptx`, `xlsx`, `pdf`, `otchet`.

## Giấy phép

Mỗi skill giữ giấy phép của nguồn gốc; xem file `LICENSE` trong thư mục skill. Các skill viết
tại repo này dùng MIT nếu không ghi khác.
