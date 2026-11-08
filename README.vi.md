# Cline Skills

Bộ sưu tập skill cho AI agent, được **adapt cho Cline trên Windows**, cùng vài skill
viết tại đây. Nguồn:
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
| `docx` | Tạo, đọc và sửa tài liệu Word, gồm bảng và style | adapt từ upstream (xem `LICENSE`) |
| `pdf` | Đọc, trích text và bảng, gộp, tách, xoay, watermark, điền form, mã hoá, OCR | adapt từ upstream (xem `LICENSE`) |
| `pptx` | Tạo, đọc và sửa bài trình chiếu | adapt từ upstream (xem `LICENSE`) |
| `xlsx` | Tạo, đọc, sửa và làm sạch bảng tính | adapt từ upstream (xem `LICENSE`) |
| `frontend-design` | Hướng dẫn thị giác để giao diện không trông như template | adapt từ upstream (xem `LICENSE`) |
| `mcp-builder` | Viết MCP server bằng Python hoặc Node | adapt từ upstream (xem `LICENSE`) |
| `skill-creator` | Tạo, test, benchmark và đóng gói skill mới | adapt từ upstream (xem `LICENSE`) |
| `grilling` | Phỏng vấn dồn dập, stress-test một kế hoạch/quyết định theo dạng cây quyết định: từng vòng câu hỏi, mỗi câu kèm câu trả lời gợi ý | adapt từ upstream (xem `LICENSE`) |
| `grill-me` | Alias một dòng, khởi động `grilling` | adapt từ upstream (xem `LICENSE`) |
| `diagnosing-bugs` | Vòng chẩn đoán bug khó và suy giảm hiệu năng: dựng feedback loop đỏ, thu nhỏ, đặt giả thuyết, instrument, sửa, dọn dẹp | adapt từ upstream (xem `LICENSE`) |
| `handoff` | Nén hội thoại hiện tại thành tài liệu bàn giao cho phiên sau, đã che secrets | adapt từ upstream (xem `LICENSE`) |
| `ui-ux-pro-max` | Catalog UI/UX offline, tra bằng script local: 80 style, 192 palette theo loại sản phẩm, 74 cặp font, 120 rule UX, 105 icon, 22 stack, kèm generator design system | adapt từ upstream (xem `LICENSE`) |
| `caveman` | Kiểu trả lời cụt: đáp án trước, bỏ rườm rà, giữ nguyên chi tiết kỹ thuật; giữ đến khi nói "stop caveman" | adapt từ upstream (xem `LICENSE`) |
| `impeccable` | Định hướng thiết kế frontend, audit, phê bình và viết lại, kèm thư viện playbook và design detector | adapt từ pbakaus/impeccable |
| `design-taste-frontend` | Website công ty ở mức figma.com và x.ai, được kiểm bằng checker headless browser của chính nó | adapt từ Leonxlnx/taste-skill |
| `manim` | Video minh hoạ toán và vật lý bằng Manim CE, xuất MP4 hoặc GIF | adapt từ iart-ai/manim-skills |
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
- Python 3.11 trở lên với `python-docx`, `python-pptx`, `openpyxl`, `PyMuPDF`, `pypdf`,
  `reportlab`, `lxml` cho `docx`, `pptx`, `xlsx`, `pdf`, `otchet` và `injection-scan`.

## Giấy phép

Điều khoản cấp repo nằm ở [`LICENSE`](LICENSE): các file viết tại đây dùng MIT.
Skill lấy từ dự án khác giữ nguyên giấy phép của họ, và điều khoản đó vẫn áp dụng cho
bản copy này.
