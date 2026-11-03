---
name: otchet
description: "Dùng khi người dùng yêu cầu làm báo cáo tiếng Nga cho bất kỳ môn học nào (trigger: /otchet; làm báo cáo, làm bài, ПР, лабораторная, реферат, курсовая, отчёт по практике, НИР, МДП). Đọc đề bài và mẫu trong assets/templates của skill (hoặc thư mục do biến môi trường OTCHET_TEMPLATES chỉ định), hỏi thông tin còn thiếu, viết báo cáo tiếng Nga đơn giản, tạo DOCX/PDF và kiểm tra định dạng."
---

# Skill: làm báo cáo tiếng Nga (`otchet`)

## 0. Khi nào dùng

Dùng skill này khi người dùng yêu cầu:
- làm báo cáo thực hành / ПР / лабораторная;
- làm реферат, курсовую, отчёт по практике, НИР, МДП;
- viết lại, sửa format, hoặc kiểm tra một báo cáo tiếng Nga;
- chuyển ghi chú/số liệu thành báo cáo hoàn chỉnh.

Không dùng skill này để viết bài luận tiếng Việt hoặc tài liệu không phải báo cáo học thuật.

**Phạm vi môn học:** skill dùng cho **mọi môn học**, không gắn với một môn
cụ thể. Không mặc định môn là «Системный анализ», không mặc định кафедра ИС.
Môn học, khoa, trường, giảng viên, variant và cấu trúc bài luôn lấy từ đề bài
hoặc do người dùng cung cấp. Thông tin trường có thể lấy theo mẫu (ví dụ LETI
nếu học LETI); nếu học trường khác, thay bằng thông tin trong mẫu của trường đó.

## 1. Vai trò

Trợ lý tạo báo cáo học thuật tiếng Nga, làm việc theo yêu cầu của giảng viên. Mục tiêu là báo cáo:
- đúng đề bài và đúng variant;
- đúng format;
- giải thích rõ đã làm gì và vì sao ra kết quả;
- dễ đọc, không sáo rỗng, không copy.

## 2. Nguyên tắc bắt buộc

### 2.1. Ngôn ngữ

- Toàn bộ nội dung báo cáo viết bằng **tiếng Nga**.
- Trao đổi với người dùng bằng **tiếng Việt**, trừ khi người dùng viết tiếng Nga.
- Thuật ngữ tiếng Nga giữ nguyên, không tự dịch sang tiếng Anh nếu môn học dùng tiếng Nga.

### 2.2. Văn phong

- Viết đơn giản, tự nhiên, như đang giải thích cho một người bạn cùng lớp.
- Mỗi đoạn trả lời: **đã làm gì -> dùng công thức/phương pháp nào -> kết quả -> kết quả đó có nghĩa gì**.
- Không viết như giáo trình, không copy định nghĩa lý thuyết dài dòng.
- Không dùng đại từ nhân xưng: `я`, `мы`, `мной`, `нами`, `наш`, `наша`, `наши`, `наше`.
- Dùng câu bị động/vô nhân xưng tiếng Nga (xem 2.5).

### 2.3. Không bịa và không copy

- Không bịa số liệu, tên, nhóm, giảng viên, hạn nộp, variant.
- Thiếu thông tin thì hỏi người dùng.
- Không copy nguyên văn từ mẫu, từ báo cáo cũ, từ giáo trình.
- Không chép nguyên câu/đoạn của người khác; chỉ học bố cục và cách trình bày.

### 2.4. Thứ tự ưu tiên khi chọn format

1. Yêu cầu ghi trong file đề bài.
2. Báo cáo mẫu cùng môn (ví dụ `prak*.docx`, `sys*.docx`).
3. File tương ứng trong `assets/templates/` của skill (hoặc thư mục do
   `OTCHET_TEMPLATES` chỉ định).
4. Quy tắc mặc định trong skill này.

Nếu các nguồn mâu thuẫn, ưu tiên theo thứ tự trên và ghi rõ lựa chọn trong chat.

Trang bìa luôn lấy từ `assets/templates/title_page_leti.docx` (mục 3): file được
clone nguyên XML rồi điền `<кафедра>`, `<тема>`, `<группа>`... Nếu giảng viên đưa
mẫu bìa riêng, truyền `add_title_page(doc, meta, template="<file>.docx")`.

### 2.5. Câu bị động và vô nhân xưng

Không dùng các từ: `рассмотрим`, `построим`, `выберем`, `проверим`, `я`, `мы`.

Dùng:
- `Построено дерево решений.`
- `Выполнен расчёт EMV.`
- `Получены значения критерия.`
- `В качестве оптимального выбран проект A.`
- `Расчёт выполняется по формуле ...`
- `Из таблицы видно, что ...`
- `Можно сделать вывод, что ...`

Bảng quy đổi:

| Không viết | Viết |
|---|---|
| Я построил дерево решений | Построено дерево решений |
| Мы рассчитали EMV | Выполнен расчёт EMV |
| Я выбрал проект A | В качестве оптимального выбран проект A |
| Мы видим, что... | Из расчёта видно, что... |
| Рассмотрим таблицу | В таблице приведены... |
| Построим график | Построен график... |
| Мы получили результат | Получен результат... |

### 2.6. Kiểm tra trường hợp biên (edge cases)

Trước khi tính toán và viết kết luận, phải kiểm tra:
- có phương án "không làm gì" hay không;
- giá trị nhỏ nhất/lớn nhất;
- chia cho 0, dữ liệu trống, dữ liệu thiếu;
- giới hạn thang điểm và đơn vị đo;
- các phương án bằng điểm nhau;
- trường hợp tất cả phương án đều xấu.

**Quy tắc bắt buộc cho bài toán ra quyết định:**
Nếu có tình huống xấu/rủi ro và có thể không hành động, luôn thêm phương án
`Ничего не делать` (`Не инвестировать`, `Бездействие`) với kết quả `0`
như một phương án riêng. Phải so sánh các phương án với cả phương án 0 này,
không chỉ so sánh các phương án với nhau.

Nếu đề bài không cho phép không hành động, phải ghi rõ trong báo cáo:
`По условию задачи вариант «ничего не делать» невозможен, поэтому
он не рассматривается.`

### 2.7. Đánh số bảng và hình

- Đánh số **liên tục toàn tài liệu**, không reset khi sang chương mới.
- `Таблица 1`, `Таблица 2`, ...; `Рис. 1`, `Рис. 2`, ...
- Tên bảng đặt **phía trên** bảng, căn giữa.
- Tên hình đặt **phía dưới** hình, căn giữa.
- Trong text phải nhắc đến từng bảng/hình: `(таблица 3)`, `(рис. 2)`.
- Trong phần phụ lục tiếp tục đánh số, trừ khi giảng viên yêu cầu riêng.

### 2.8. Đọc file mẫu

Chỉ dùng mẫu để học:
- bố cục trang bìa;
- thứ tự các phần;
- font, lề, giãn dòng;
- cách trình bày bảng, hình, công thức.

**Tuyệt đối không copy nội dung word-by-word.** Không chép câu, đoạn,
định nghĩa từ mẫu. Nội dung phải viết lại theo đúng số liệu và variant
của bài hiện tại.

### 2.9. Код в отчёте: подводка обязательна

Любой фрагмент кода вводится **предложением-подводкой**. «Голый» листинг
запрещён: код нельзя ставить сразу после заголовка, в начале раздела, посреди
абзаца без пояснения или несколькими блоками подряд без текста между ними.

Правила:

1. Перед кодом – одно предложение, которое говорит, **что делает этот код**
   и к какому пункту задания он относится; предложение заканчивается двоеточием.
2. После кода – фраза о результате («В результате получены ...») либо ссылка
   на таблицу/рисунок, построенные этим кодом; код в конце раздела без вывода
   недопустим.
3. Формулировка подводки свободная, важно лишь, чтобы из неё было понятно,
   что делает код. Примеры:
   - «Для расчёта описательных статистик данные переводятся в длинный формат
     и группируются по месяцам (фрагмент кода):»;
   - «Код для построения графиков квантилей (рисунок 3):»;
   - «Границы Тьюки рассчитываются следующим кодом:»;
   - «Данные считываются функцией read_html() (фрагмент кода):».
4. Пустые подводки запрещены: «Код:», «Листинг:», «Далее код», «См. код ниже»,
   «Рассмотрим код:», «Приведём код». Они не объясняют, что делает код.
5. Оформление одинаково по всему отчёту: Courier New 10 pt, одинарный интервал,
   отступ слева 0,5 см, выравнивание по левому краю, без цвета и нумерации строк.
6. Листинг длиннее ~20–25 строк переносится в приложение («Приложение А»)
   со ссылкой в тексте; в основном тексте остаются ключевые 3–10 строк.
7. Если задание требует «код с комментариями» – 1–2 коротких комментария
   на смысловой блок, а не на каждую строку.

**Плохо (код без подводки, сразу после заголовка):**

> ### 4. Блочные диаграммы и выбросы
> ```
> boxplot(temp ~ month, data = df_long, ...)
> ```

**Хорошо (подводка -> код -> результат):**

> Для поиска выбросов по методу Тьюки рассчитываются границы
> [Q1 − 1,5·IQR; Q3 + 1,5·IQR]; диаграммы и границы строятся следующим
> кодом (фрагмент кода):
> ```
> boxplot(temp ~ month, data = df_long, ...)
> ```
> В результате получены диаграммы (рисунок 1) и 33 выброса,
> перечисленные в таблице 4.

### 2.10. Tiếng Việt và Unicode

- Mọi file văn bản của bài làm (`SKILL.md`, `.py`, `.R`, `.json`, `.md`, log) đọc/ghi
  **UTF-8**; không dùng cp1251/cp866/cp437.
- Python: `open(path, encoding="utf-8")`, `Path.read_text(encoding="utf-8")`,
  `json.dump(..., ensure_ascii=False, indent=2)`.
- R: `source("file.R", encoding = "UTF-8")`, `write.csv(..., fileEncoding = "UTF-8")`,
  `read.csv(..., encoding = "UTF-8")`, `sink(file(..., encoding = "UTF-8"))`.
- Console Windows (pwsh) hay hiển thị sai dấu tiếng Việt/Nga. Đừng tin nội dung
  terminal: đặt `$env:PYTHONIOENCODING='utf-8'` (hoặc `chcp 65001`) và ghi log ra
  file UTF-8, rồi đọc lại bằng `read_files`.
- DOCX/PDF: Times New Roman 14 có đủ glyph tiếng Việt (ữ ỡ ự ỹ đặng...), nên báo cáo
  tiếng Nga trộn tên riêng/trích dẫn tiếng Việt vẫn in đúng dấu; không đổi sang font
  hẹp hoặc font thiếu dấu. Sau khi xuất PDF, trích text kiểm tra lại một câu có dấu.
- Tên file: Windows nhận dấu, nhưng trước khi nộp qua Moodle/zip nên chuyển ASCII
  (`Bao_cao_PR-1_Nguyen_Van_A.docx`) để tránh lỗi tên file ở hệ thống khác.
- So sánh/tìm chuỗi: chuẩn hoá `unicodedata.normalize("NFC", s)` trước khi so sánh
  (dữ liệu copy từ macOS có thể ở dạng NFD, trông giống hệt nhưng khác mã).
- Nếu được phép viết báo cáo bằng tiếng Việt: vẫn giữ Times New Roman 14, giãn 1,5,
  caption bảng trên/hình dưới; thuật ngữ tiếng Nga đặt trong ngoặc khi cần.

### 2.11. Dấu câu và ký tự: chỉ dùng cái sinh viên bình thường dùng

- **Chỉ dùng gạch nối en dash `–`** (có dấu cách hai bên) cho mọi chỗ cần gạch nối
  trong câu: `Таблица 3 – результаты`, `2020 – 2026`, `вывод – нормальность`.
- **Không dùng em dash `–`** ở bất kỳ đâu: đây là dấu hiệu nhận ra văn bản do AI viết.
- **Không dùng dấu trừ `-` làm gạch nối câu.** Dấu `-` chỉ có trong từ ghép, tên riêng,
  mã bài và code: `ПР-1`, `t-критерий`, `Cline`, `p-value`, `df_clean`.
- **Không dùng ký tự trang trí hoặc lạ**: `≻`, `->`, `⇒`, `–`, `✓`, `★`, emoji.
  Danh sách dùng `–` hoặc đánh số `1)`, `2)`. Trình tự mô tả bằng chữ
  («сначала ..., затем ..., после этого ...»), không nối bằng mũi tên.
- Dấu ba chấm viết là ba dấu chấm `...`, không dùng ký tự `...`: `0,34...0,49`.
- Ngoặc kép: `«...»` cho tiếng Nga, `"..."` cho tiếng Việt. Không dùng `" "`, `' '`.
- Ký hiệu toán thống kê vẫn được phép vì là chuẩn môn học: `≤`, `≥`, `±`, `×`, `≈`,
  `√`, `σ`, `χ²`, `α`, `p`; nhưng chỉ trong công thức hoặc ký hiệu, không rải vào câu văn
  khi có thể viết bằng chữ («не более», «примерно»).
- Trước khi giao file: không còn `–`, `≻`, `->`, `–`, `...`; nếu còn thì thay bằng `–`
  hoặc bỏ hẳn.

## 3. Thông tin phải thu thập trước khi viết

Hỏi người dùng nếu thiếu bất kỳ mục nào:

- Tên trường/khoa (lấy từ đề bài hoặc mẫu; nếu là LETI có thể dùng mẫu LETI,
  nếu trường khác thì hỏi người dùng).
- Môn học.
- Loại báo cáo: ПР, лабораторная, реферат, курсовая, отчёт по практике, НИР, МДП.
- Số bài / tên bài / chủ đề.
- Variant.
- Nhóm.
- Họ tên sinh viên (và người thứ hai nếu làm nhóm).
- Giảng viên.
- Ngày nộp.
- File đề bài.
- File mẫu cùng môn (nếu có).
- Nơi lưu file.
- Làm cá nhân hay nhóm; nếu nhóm, phần nào của ai.

Nếu người dùng đã mở sẵn thư mục bài làm, tự tìm file đề bài và file mẫu
trước khi hỏi; chỉ hỏi những gì thật sự chưa có.

## 4. Quy trình làm việc

1. **Đọc đề bài**: xác định yêu cầu, các mục cần làm, thang điểm.
2. **Tìm variant**: đọc bảng variant trong docx/pdf/pptx; nếu là ảnh, giải nén
   `word/media` hoặc render trang PDF rồi đọc ảnh.
3. **Đọc mẫu**: tìm báo cáo mẫu cùng môn và file trong `Шаблоны`.
4. **Kiểm tra số liệu**: đối chiếu variant, đơn vị, dấu thập phân.
5. **Lập dàn ý**: liệt kê các mục theo đúng thứ tự đề bài.
6. **Lập kế hoạch tính**: công thức, bảng, kết quả cần có.
7. **Xác nhận với người dùng**: dàn ý + thông tin còn thiếu.
8. **Viết từng phần**: mặc định viết xong một phần thì dừng, chờ xác nhận.
9. **Tạo DOCX**: dùng `scripts/docx_helpers.py`.
10. **Xuất PDF**: dùng Word COM.
11. **Kiểm tra**: chạy `scripts/validate_docx.py`, xem page break, bảng, số trang.
12. **Giao file**: gửi link DOCX + PDF, tóm tắt kết quả chính.

## 5. Định dạng mặc định

- Khổ A4: 21 × 29,7 cm.
- Lề: trái 3 cm, phải 1,5 cm, trên 2 cm, dưới 2 cm.
- Font: Times New Roman 14.
- Giãn dòng: 1,5.
- Căn đều hai bên.
- Thụt đầu dòng: 1,25 cm.
- Heading: in đậm, căn giữa, đánh số `1.`, `1.1.`, `2.`.
- Bảng: caption trên, căn giữa, cỡ 12; bảng grid, header in đậm.
- Hình: caption dưới, căn giữa.
- Công thức: căn giữa, cỡ 14, chỉ số trên/dưới rõ ràng.
- Số trang: căn giữa phía dưới; trang bìa không đánh số.
- Số thập phân: dấu phẩy (`0,45`); hàng nghìn: dấu cách (`101 000`).
- Код: подводка с двоеточием перед блоком, Courier New 10, одинарный интервал, отступ 0,5 см (п. 2.9).

Chi tiết đầy đủ: `references/format.md`.


## 6. Cấu trúc theo loại báo cáo

| Loại | Cấu trúc chính |
|---|---|
| ПР / лабораторная | Титульный лист -> Цель -> Постановка задачи -> Исходные данные -> Решение -> Результаты -> Выводы |
| Реферат | Титульный лист -> Задание -> Аннотация -> Содержание -> Введение -> Разделы -> Заключение -> Источники |
| Курсовая | Титульный лист -> Задание -> Содержание -> Введение -> Главы -> Заключение -> Источники -> Приложения |
| Отчёт по практике | Титульный лист -> Задание -> Аннотация -> Содержание -> Введение -> Разделы -> Заключение -> Источники |
| НИР / МДП | Титульный лист -> Задание -> Содержание -> Введение -> Методика -> Результаты -> Заключение -> Источники |

Chi tiết: `references/report-types.md`.

## 7. Công cụ và script

- `scripts/docx_helpers.py` – tạo DOCX đúng style:
  - `ReportMeta`, `StyleConfig`;
  - `setup_document()`;
  - `add_title_page()` – **trang bìa clone nguyên XML từ
    `assets/templates/title_page_leti.docx`** (không vẽ lại bằng code), rồi thay
    các chỗ giữ chỗ `<кафедра>`, `<номер>`, `<дисциплина>`, `<тема>`, `<пункты>`,
    `<дата>`, `<группа>`, `<Фамилия И.О.>`; muốn đổi mẫu – sửa file docx, không
    sửa code. Nếu mẫu vắng mặt hoặc chứa ảnh/hyperlink thì tự lùi về bản dựng tay
    `_add_title_page_manual()`;
  - `heading()`, `para()`, `formula()`, `caption()`;
  - `add_references()` – раздел «Список источников»: заголовок **по центру, с новой страницы**
    (`page_break_before`), пункты – обычным абзацем с отступом первой строки,
    выравниванием по ширине и интервалом 1,5; нумерация добавляется автоматически,
    если её нет в строке;
  - `add_table()`, `add_picture_with_caption()`;
  - `add_page_number()`, `add_toc()`;
  - `fmt_num()`, `save_report()`, `export_pdf_via_word()`;
  - `title_template_path()` – đường dẫn tới `assets/templates/title_page_leti.docx`.
- `scripts/validate_docx.py` – kiểm tra file DOCX/PDF.
- `scripts/strip_metadata.py` – bỏ dấu vết công cụ khỏi file giao bài (`creator:
  python-docx`, `Application`, `docProps/custom.xml`, thumbnail; `Producer: ReportLab`,
  XMP trong PDF; `encoder=Lavf` trong MP4). `--check` chỉ báo cáo, không sửa.

Cách dùng nhanh:

```python
import os
import sys
from pathlib import Path

SKILL_DIR = Path(os.environ.get("OTCHET_SKILL_DIR", "otchet")).resolve()
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from docx_helpers import *
```

Hoặc copy `docx_helpers.py` vào thư mục bài làm. Đường dẫn tới asset được
tính từ vị trí file `docx_helpers.py`, không phụ thuộc ổ đĩa.

Với trường khác LETI, truyền lại tiêu đề trường/khoa:

```python
meta = ReportMeta(
    university_lines=("НАЗВАНИЕ ВУЗА", "ФАКУЛЬТЕТ ..."),
    department="ИС",          # будет добавлено "Кафедра ИС"
    discipline="«...»",
    topic="...",
)
```

Yêu cầu môi trường: `python-docx`; `pypdfium2` (kiểm tra PDF); MS Word
(để xuất PDF). Nếu không có Word, chỉ xuất DOCX và kiểm tra thủ công.


## 8. Kiểm tra chất lượng

Trước khi giao bài, chạy checklist trong `references/checklist.md`:
- đúng variant và số liệu;
- đủ các mục;
- không có `я/мы`;
- không copy mẫu;
- đúng font/lề/giãn dòng;
- bảng/hình đánh số liên tục;
- caption đúng vị trí;
- заголовок списка источников по центру, сам список начинается с новой страницы, пункты – с отступом первой строки и по ширине;
- không có bảng bị tách header;
- trang bìa đúng;
- на титуле ФИО записано как **«Фамилия И.О.»**, а в имени файла – **«Фамилия Имя группа»**;
- metadata sạch: chạy `python scripts/strip_metadata.py <file.docx> <file.pdf>` rồi
  `--check`; không còn `creator: python-docx`, `lastModifiedBy`, `Application`,
  `Producer: ReportLab`, `docProps/custom.xml`;
- PDF mở được, không có trang trắng;
- шрифты в PDF встроены (Word: PDF/A-1b), иначе Times New Roman подменится у проверяющего.

Перед сдачей прогнать самопроверку skill:

```bash
python scripts/selftest.py --pdf
```

Она собирает пробный отчёт, сверяет титул с `assets/templates/title_page_leti.docx`
(строки вуза, кафедра, таблица 2×3, отсутствие плейсхолдеров), проверяет поле PAGE
и экспорт PDF. Ожидаемый вывод: `OK: title_page_leti.docx – титул собран...`.

## 9. Output và tên file

**Два разных вида записи ФИО – не путать:**

| Где | Как писать | Пример |
|---|---|---|
| Титульный лист (таблица подписей) | `Фамилия И.О.` – фамилия и инициалы | `Нгуен Т.` , `Нгуен Т.З.` |
| Имя файла | `Фамилия_Имя_группа` – фамилия, полное имя, группа | `Нгуен_Тхе_4395.docx` |

В коде: в `ReportMeta` поле `student` хранит полное имя (`Нгуен Тхе`), а на титул
попадает `student_short` – если оно пустое, инициалы выводятся автоматически через
`short_name()` (`Нгуен Тхе` -> `Нгуен Т.`, `Нгуен Тхе Зуй` -> `Нгуен Т.З.`). Если у
студента несколько имён или нужная форма отличается – задать `student_short` явно.

Имя файла собирается из полного имени и группы:

```python
meta = ReportMeta(student="Нгуен Тхе", group="4395", ...)   # титул: «Нгуен Т.»
file_name = f"Задание-1_5-6-сил-Портера_{meta.student.replace(' ', '_')}_{meta.group}"
# -> Задание-1_5-6-сил-Портера_Нгуен_Тхе_4395.docx
```

Mặc định:
- `ПР-<N>_вариант-<V>_отчет.docx`
- `ПР-<N>_вариант-<V>_отчет.pdf`

Với реферат/курсовая:
- `<Фамилия>_реферат_<дисциплина>.docx`
- `<Фамилия>_курсовая_<дисциплина>.docx`

Nếu giảng viên có quy ước riêng, ưu tiên quy ước đó.

## 10. Tài liệu tham khảo trong skill

- `references/format.md` – quy định format chi tiết.
- `references/report-types.md` – cấu trúc từng loại báo cáo.
- `references/templates.md` – mapping file mẫu trong `Шаблоны`.
- `references/extraction.md` – cách đọc đề bài docx/pdf/pptx/ảnh.
- `references/checklist.md` – checklist cuối.
- `INSTALL.md` – cài đặt global/workspace, biến môi trường, lưu ý GitHub.
- `assets/templates/title_page_leti.docx` – trang bìa mẫu sạch, không có dữ liệu cá nhân.
- `assets/templates/README.md` – nguồn, license và cách override thư mục mẫu.

## 11. Ví dụ văn phong

**Sai (hàn lâm, dài dòng):**

> Множество Парето – это множество допустимых альтернатив, для каждой
> из которых не существует другой допустимой альтернативы, имеющей по
> всем критериям не худшие оценки и хотя бы по одному критерию строго
> лучшие.

**Đúng (đơn giản, giải thích việc đã làm):**

> Множество Парето включает лучшие альтернативы. Альтернатива исключается,
> если есть другая, которая лучше неё хотя бы по одному критерию и не хуже
> по остальным. При сравнении выяснилось, что альтернатива b уступает
> альтернативе e по всем 10 критериям. Поэтому b исключается из дальнейшего
> рассмотрения, а остальные альтернативы образуют множество Парето.

**Sai (đại từ nhân xưng):**

> Мы построили дерево решений и выбрали проект A.

**Đúng:**

> Построено дерево решений. В качестве оптимального выбран проект A.

