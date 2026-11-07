# Cline Skills

Bộ sưu tập skill cho AI agent, được **adapt cho Cline trên Windows**, cùng vài skill
viết tại đây. Nguồn:
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[pbakaus/impeccable](https://github.com/pbakaus/impeccable),
[iart-ai/manim-skills](https://github.com/iart-ai/manim-skills),
[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) và
[tt-a1i/archify](https://github.com/tt-a1i/archify). Skill từ `anthropics/skills`
**không** được công bố ở đây vì lý do giấy phép — xem ghi chú dưới bảng.

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
| `impeccable` | Định hướng thiết kế frontend, audit, phê bình và viết lại, kèm thư viện playbook và design detector | adapt từ pbakaus/impeccable |
| `design-taste-frontend` | Website công ty ở mức figma.com và x.ai, được kiểm bằng checker headless browser của chính nó | adapt từ Leonxlnx/taste-skill |
| `manim` | Video minh hoạ toán và vật lý bằng Manim CE, xuất MP4 hoặc GIF | adapt từ iart-ai/manim-skills |
| `git-workflow-and-versioning` | Nhánh, commit nguyên tử, commit message, pull request, semantic versioning | adapt từ addyosmani/agent-skills |
| `documentation-and-adrs` | Architecture decision record và tài liệu giữ codebase dễ đọc | adapt từ addyosmani/agent-skills |
| `code-review-and-quality` | Review nhiều chiều trước khi merge: tính đúng, thiết kế, lỗi, test, bảo mật | adapt từ addyosmani/agent-skills |

Không có ở đây: `docx`, `pdf`, `pptx`, `xlsx`, `frontend-design`, `mcp-builder` và
`skill-creator`. Chúng lấy từ `anthropics/skills`, nơi `LICENSE.txt` giữ toàn bộ quyền
và cấm sao chép, tạo tác phẩm phái sinh và phân phối — nên chúng nằm trong một repo
**private** và không được công bố ở đây. Bản đã cài vẫn chạy bình thường trên máy.

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

Điều khoản cấp repo nằm ở [`LICENSE`](LICENSE): các file viết tại đây dùng MIT.
Skill lấy từ dự án khác giữ nguyên giấy phép của họ, và điều khoản đó vẫn áp dụng cho
bản copy này.

> Lưu ý: `docx`, `pdf`, `pptx`, `xlsx`, `frontend-design`, `mcp-builder` và
> `skill-creator` lấy từ `anthropics/skills`; `LICENSE.txt` của họ giữ toàn bộ quyền và
> cấm sao chép, tạo tác phẩm phái sinh, phân phối. Vì vậy chúng **không có** trong repo
> này: bản đã adapt nằm ở một repo private, bản đã cài nằm trong `~/.cline/skills` trên
> máy dùng.
