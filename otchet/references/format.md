# Quy định format báo cáo tiếng Nga

Tài liệu này là chuẩn format mặc định cho skill `otchet`. Khi đề bài hoặc
giảng viên có yêu cầu riêng, ưu tiên yêu cầu của giảng viên.

Quy định áp dụng cho **mọi môn học**. Không hardcode tên môn, khoa, trường
hay giảng viên; các thông tin này lấy từ đề bài hoặc do người dùng cung cấp.

## 1. Trang và lề

- Khổ giấy: **A4**, 21 × 29,7 cm.
- Lề trái: **3 cm** (để đóng gáy).
- Lề phải: **1,5 cm**.
- Lề trên: **2 cm**.
- Lề dưới: **2 cm**.
- Hướng giấy: dọc. Bảng quá rộng có thể xoay ngang một trang, nhưng phải
  quay lại dọc ngay sau đó.
- Số trang: căn giữa phía dưới; trang bìa không đánh số nhưng vẫn tính là
  trang 1.

## 2. Trang bìa

**Nguồn chuẩn:** file `assets/templates/title_page_leti.docx` (hoặc file do
`OTCHET_TEMPLATES` / tham số `template=` chỉ định). Trang bìa **không vẽ lại bằng
code** – XML của mẫu được clone nguyên trạng (`_fill_title_from_template`) và chỉ
thay các chỗ giữ chỗ. Nhờ vậy khổ chữ, khoảng trống, bảng chữ ký và đường kẻ khớp
100% với mẫu của trường. Nếu sửa mẫu (đổi dòng trường, thêm dòng), báo cáo tự
động đổi theo – không cần sửa code.

Chỗ giữ chỗ trong mẫu và giá trị thay thế:

| Trong mẫu | Lấy từ `ReportMeta` |
|---|---|
| 4 dòng đầu (МИНОБРНАУКИ РОССИИ ...) | `university_lines` |
| `Кафедра <кафедра>` | `department` (bỏ dòng nếu rỗng) |
| `ОТЧЕТ` | `report_label` (`РЕФЕРАТ`, `КУРСОВАЯ РАБОТА`, `ГЛОССАРИЙ`...) |
| `по практической работе №<номер>` | `work_line` (`по заданию № 1`...) |
| `по дисциплине «<дисциплина>»` | `discipline` (bỏ dòng nếu rỗng) |
| `Тема: <тема>` | `topic` (bỏ dòng nếu rỗng) |
| `Вариант <номер>` | `variant` (bỏ dòng nếu rỗng) |
| bảng 2×3: `Студент гр. <группа>` / `<Фамилия И.О.>` / `Руководитель` | `student_label` + `group`, `student_short` (или `short_name(student)`), `teacher` |
| `Выполненные пункты: <пункты>` | `completed_items` (bỏ dòng nếu rỗng) |
| `Дата сдачи работы на проверку – <дата>` | `submission_date` (bỏ dòng nếu rỗng) |
| `Санкт-Петербург`, `2026` | `city`, `year` |

Quy tắc cố định của mẫu (không đổi khi điền):

- Mọi dòng trên trang bìa: Times New Roman **14 pt**, căn giữa, giãn dòng 1,5.
- 4 dòng tên trường và dòng `Кафедра` in đậm; `ОТЧЕТ`, dòng `по ...`, `по дисциплине`,
  `Тема`, `Выполненные пункты`, `Дата сдачи` in đậm; `Вариант`, thành phố, năm để chữ thường.
- Bảng chữ ký: 3 cột rộng bằng nhau (3118 twips ≈ 5,5 cm), chiều cao dòng tối thiểu
  1,08 cm, **không có khung bảng**, chỉ có đường kẻ dưới ở ô giữa (cột ký tên).
- Kết thúc trang bìa bằng dấu ngắt trang; số trang bắt đầu hiển thị từ trang nội dung
  (`different_first_page_header_footer = True`), trang bìa không đánh số.
- **ФИО trên trang bìa – chỉ `Фамилия И.О.`** (họ + chữ cái đầu của tên/đệm), ví dụ
  `Нгуен Т.` hoặc `Нгуен Т.З.`. Tên đầy đủ chỉ dùng trong tên file:
  `Фамилия_Имя_группа` (`Нгуен_Тхе_4395`). Hàm `short_name()` tự rút gọn; nếu cần
  dạng khác – truyền `student_short` trong `ReportMeta`.
- Nếu mẫu có ảnh/logo hoặc hyperlink, cơ chế clone sẽ bỏ liên kết đó – khi đó
  `add_title_page()` tự chuyển sang bản dựng tay (`_add_title_page_manual`).

## 3. Font và đoạn văn

- Font: **Times New Roman**.
- Cỡ chữ chính: **14 pt** (có thể 13 nếu bài quá dài và giảng viên cho phép).
- Giãn dòng: **1,5**.
- Căn đều hai bên (**Justify**).
- Thụt đầu dòng: **1,25 cm**.
- Khoảng cách trước/sau đoạn: 0 pt.
- Không dùng chữ in nghiêng cho cả đoạn; chỉ dùng cho thuật ngữ, biến,
  ký hiệu nếu cần.
- Không dùng chữ in đậm cho cả đoạn; chỉ in đậm tiêu đề và nhãn quan trọng.
- Không dùng dấu chấm than, biểu tượng cảm xúc, teencode.

### 3.1. Dấu câu

- Gạch nối trong câu: chỉ `–` (en dash) có dấu cách hai bên. Em dash `—` không dùng.
- Dấu `-` chỉ dùng trong từ ghép, tên riêng, mã bài, code (`ПР-1`, `t-критерий`,
  `p-value`), không dùng làm gạch nối câu.
- Không dùng `≻`, `→`, `⇒`, `•`, `✓`, `★`, emoji. Danh sách: `–` hoặc `1)`, `2)`.
- Dấu ba chấm: `...`, không dùng ký tự `…`.
- Ngoặc kép: `«...»` (tiếng Nga), `"..."` (tiếng Việt); không dùng `“ ”`, `‘ ’`.
- Автоматическая замена: `normalize_dashes(doc)` из `docx_helpers` меняет `—`
  на ` – ` во всех абзацах и ячейках таблиц; вызывать перед `save_report()`.

## 4. Tiêu đề

- Heading cấp 1: `1. Название раздела`, `2. ...`
- Heading cấp 2: `1.1. Название подраздела`, `1.2. ...`
- Heading in đậm, **căn giữa**, cỡ 14.
- Không có dấu chấm ở cuối tiêu đề.
- Trước heading có thể có 12 pt khoảng trắng; sau heading 6 pt.
- Không để heading đứng một mình ở cuối trang mà không có đoạn văn theo sau.
- `Цель работы`, `Постановка задачи`, `Выводы`, `Заключение` cũng là heading
  và in đậm, căn giữa.

## 5. Bảng

- Caption đặt **phía trên** bảng, căn giữa, cỡ 12:
  `Таблица 3 – Название таблицы`.
- Bảng dùng khung **Table Grid**.
- Dòng tiêu đề in đậm.
- Nội dung ô: căn giữa; cột văn bản dài có thể căn trái.
- Cỡ chữ trong bảng: 11–12 pt; bảng nhiều cột có thể 8–10 pt nhưng phải đọc được.
- Không để bảng bị tách dòng tiêu đề sang trang khác.
- Nếu bảng dài hơn một trang, lặp lại dòng tiêu đề ở trang sau.
- Không dùng ảnh chụp bảng thay cho bảng thật.
- Trong text phải có câu dẫn: `Результаты приведены в таблице 3.`
- Số liệu trong cùng một cột phải có cùng số chữ số sau dấu phẩy.

## 6. Hình

- Caption đặt **phía dưới** hình, căn giữa, cỡ 12:
  `Рис. 2 – Название рисунка`.
- Hình phải rõ, không mờ, không méo.
- Không dùng ảnh chụp màn hình chứa cả thanh công cụ, tab trình duyệt.
- Trong text phải có câu dẫn: `Схема приведена на рис. 2.`
- Hình và caption phải nằm cùng một trang.

## 7. Công thức

- Công thức đặt trên dòng riêng, căn giữa.
- Cỡ 14, cùng font Times New Roman.
- Chỉ số trên/dưới rõ ràng: `x′ij`, `w_i`, `α_i`.
- Nếu công thức được đánh số, đặt số trong ngoặc tròn bên phải:
  `(1)`, `(2)`.
- Ngay sau công thức cần giải thích ký hiệu:
  `где xij – оценка альтернативы j по критерию i.`
- Không chèn công thức dưới dạng ảnh nếu có thể gõ bằng Word.
- Không viết công thức bằng ký tự `*`, `/` nếu có thể dùng ký hiệu toán học.

## 8. Đánh số bảng và hình

**Quy tắc bắt buộc:** đánh số liên tục toàn tài liệu, không reset về 1 khi
sang chương mới.

- `Таблица 1`, `Таблица 2`, `Таблица 3`, ...
- `Рис. 1`, `Рис. 2`, `Рис. 3`, ...
- Tên bảng nằm trên bảng.
- Tên hình nằm dưới hình.
- Trong phần phụ lục tiếp tục đánh số toàn tài liệu, trừ khi giảng viên yêu
  cầu đánh số riêng kiểu `В.1`, `В.2`.
- Không đánh số trùng hoặc nhảy số.
- Mỗi bảng/hình phải được nhắc đến ít nhất một lần trong text.

## 9. Định dạng số

- Dấu thập phân: **dấu phẩy** (`0,45`; `3,14`).
- Hàng nghìn: **dấu cách** (`101 000`; `1 234 567`).
- Không dùng dấu chấm cho hàng nghìn.
- Phần trăm: `45 %` hoặc `45%` theo thống nhất toàn bài; ưu tiên `45 %`.
- Đơn vị đo: có dấu cách giữa số và đơn vị: `10 кг`, `5 м`, `20 °C`.
- Trong một cột bảng, giữ cùng số chữ số sau dấu phẩy.
- Nếu số liệu gốc có 1 chữ số thập phân, không tự thêm 3 chữ số thập phân.

## 10. Làm việc với file mẫu

File mẫu trong `assets/templates/` (hoặc thư mục `Шаблоны` do người dùng
cấu hình) và báo cáo mẫu cùng môn chỉ dùng để học:
- bố cục trang bìa;
- thứ tự các phần;
- font, lề, giãn dòng;
- cách trình bày bảng, hình, công thức.

**Tuyệt đối không copy nội dung word-by-word.** Không chép câu, đoạn,
định nghĩa, kết luận từ mẫu. Nếu cần dùng ý, phải viết lại bằng lời của
mình và gắn với số liệu của bài hiện tại.

## 11. Văn phong vô nhân xưng

Không dùng:
- `я`, `мы`, `мной`, `нами`, `наш`, `наша`, `наши`, `наше`;
- `рассмотрим`, `построим`, `выберем`, `проверим`;
- các câu cảm thán, khẩu ngữ.

Dùng câu bị động/vô nhân xưng:

| Không viết | Viết |
|---|---|
| Я построил дерево решений | Построено дерево решений |
| Мы рассчитали EMV | Выполнен расчёт EMV |
| Я выбрал проект A | В качестве оптимального выбран проект A |
| Мы видим, что... | Из расчёта видно, что... |
| Рассмотрим таблицу | В таблице приведены... |
| Построим график | Построен график... |
| Мы получили результат | Получен результат... |

Các dạng được phép:
- `построено`, `выполнен`, `рассчитан`, `получен`, `выбран`, `определён`;
- `рассчитывается`, `строится`, `определяется`, `сравнивается`;
- `из расчёта видно`, `следует отметить`, `можно сделать вывод`.

## 12. Ngôn ngữ đơn giản, không hàn lâm

- Không copy định nghĩa từ giáo trình.
- Nếu cần định nghĩa, viết 1–2 câu đơn giản rồi chuyển ngay sang bài toán.
- Mỗi đoạn nên trả lời: làm gì -> công thức nào -> kết quả nào -> nghĩa là gì.
- Không dùng từ hoa mỹ: `является неотъемлемой частью`, `играет важнейшую
  роль`, `в современном мире` nếu không cần thiết.
- Không viết lại lý thuyết chỉ để làm dài báo cáo.

**Ví dụ sai:**

> Множество Парето – это множество допустимых альтернатив, для каждой из
> которых не существует другой допустимой альтернативы, имеющей по всем
> критериям не худшие оценки и хотя бы по одному критерию строго лучшие.

**Ví dụ đúng:**

> Множество Парето включает лучшие альтернативы. Альтернатива исключается,
> если есть другая, которая лучше неё хотя бы по одному критерию и не хуже
> по остальным. При сравнении выяснилось, что альтернатива b уступает
> альтернативе e по всем 10 критериям. Поэтому b исключается, а остальные
> альтернативы образуют множество Парето.

## 13. Kiểm tra trường hợp biên

Trước khi viết kết quả, kiểm tra:
- có phương án `Ничего не делать` / `Не инвестировать` / `Бездействие`;
- nếu có, thêm phương án này với kết quả `0` và so sánh với tất cả phương án;
- nếu đề không cho phép, ghi rõ lý do không xét;
- giá trị nhỏ nhất/lớn nhất;
- chia cho 0;
- dữ liệu trống/thiếu;
- giới hạn thang điểm;
- các phương án bằng điểm nhau;
- trường hợp tất cả phương án đều xấu.

Ví dụ câu trong báo cáo:

> Дополнительно рассматривается вариант «ничего не делать» с результатом 0.
> Он используется как база для сравнения: проект считается выгодным только
> тогда, когда его результат больше нуля.

Nếu không thể không hành động:

> По условию задачи вариант «ничего не делать» невозможен, поэтому
> он не рассматривается.


## 14. Nguồn tham khảo

- Danh sách nguồn đặt cuối báo cáo.
- **Danh sách luôn bắt đầu từ trang mới**: dùng `add_references(doc, items)` –
  hàm đặt `page_break_before` cho tiêu đề (không tạo trang trắng như khi chèn
  page break thủ công).
- Tiêu đề `Список источников`: Times New Roman 14, đậm, **căn giữa**, không thụt
  đầu dòng, cách đoạn sau 6 pt.
- Mỗi nguồn là **một đoạn văn bình thường**: thụt lề dòng đầu 1,25 cm, căn đều
  hai bên (justify), giãn dòng 1,5, không treo dòng (không dùng hanging indent),
  không đánh số tự động của Word – số `1.`, `2.` nằm trong text.
- Mỗi nguồn đủ: tác giả, tên tài liệu, nhà xuất bản, năm; tài liệu điện tử có
  `URL` và `(дата обращения: ...)`.
- Địa chỉ phải là **hyperlink thật** (`w:hyperlink` + liên kết ngoài), không phải
  chữ thường: `add_references()` tự chuyển `https://`, `www.` và `doi:` thành link,
  text vẫn giữ Times New Roman 14. Link còn nguyên khi xuất PDF (Word sinh annotation
  `/Link`), nên `validate_docx.py` báo FAIL nếu gặp URL dạng chữ.
- Không đưa nguồn không sử dụng vào danh sách.
- Trong text có thể ghi `[1]`, `[2]` nếu giảng viên yêu cầu.
- Không copy danh sách nguồn từ mẫu nếu không đọc.

```python
from docx_helpers import add_references

add_references(doc, [
    "Портер М.Э. Как конкурентные силы формируют стратегию // HBR. – 1979. – С. 137–145.",
    "Proceset – платформа процессной аналитики [Электронный ресурс]. – URL: "
    "https://infomaximum.ru/product/ (дата обращения: 01.11.2026).",
])
```

## 15. Phụ lục

- Phụ lục đặt sau danh sách nguồn.
- Tiêu đề: `ПРИЛОЖЕНИЕ А`, `ПРИЛОЖЕНИЕ Б`.
- Bảng/hình trong phụ lục vẫn tiếp tục đánh số toàn tài liệu (trừ khi có
  yêu cầu riêng).
- Không đưa code dài vào thân báo cáo; code dài đưa vào phụ lục và có chú thích
  (quy tắc chi tiết về code – §16).

## 16. Фрагменты кода в отчёте

Пункт с кодом строится по схеме:
**подводка -> код -> результат (таблица или рисунок) -> вывод**.
Код никогда не вставляется «голым».

### 16.1. Подводка

- Перед каждым блоком кода – одно предложение, заканчивающееся двоеточием.
  Оно объясняет, что делает код и к какому пункту задания относится.
- После блока кода – фраза о результате («В результате получены ...») либо
  ссылка на таблицу/рисунок, которые построены этим кодом.
- Формулировка свободная, смысл обязателен. Допустимые варианты:
  «Для расчёта ... данные переводятся в длинный формат (фрагмент кода):»,
  «Код для построения рисунка 2:», «Границы Тьюки рассчитываются
  следующим кодом:», «Данные считываются функцией read_html()
  (фрагмент кода):».
- Запрещены пустые подводки: «Код:», «Листинг:», «Далее код»,
  «См. код ниже», «Рассмотрим код:», «Приведём код».
- Запрещены: код сразу после заголовка; два и более блока кода подряд
  без текста между ними; код в конце пункта без вывода.
- В подводке используется страдательный залог или 3-е лицо
  («выполняется», «приведён», «рассчитывается»); «я/мы» не употребляются.

### 16.2. Оформление кода

- Courier New, 10 pt, одинарный интервал.
- Отступ слева 0,5 см, выравнивание по левому краю (не по ширине),
  первая строка без отступа.
- Без цвета, без подсветки синтаксиса, без нумерации строк, без рамки.
- Одинаковое оформление во всём отчёте; размер шрифта не «прыгает».
- В коде нет отладочного мусора: лишних `print()`, закомментированных
  кусков, локальных путей вида `C:\Users\...`.
- Код даётся текстом, а не скриншотом: иначе его нельзя проверить
  и скопировать.

### 16.3. Длина и приложение

- До 20–25 строк – в основном тексте.
- Длиннее – в «Приложение А», в тексте остаётся ссылка «(приложение А)»,
  а в основном тексте приводят ключевые 3–10 строк
  (чтение данных, расчёт, построение графика).
- В приложении код тоже начинается с подводки, а не с заголовка.

### 16.4. Пример

**Плохо:**

> ### 4. Блочные диаграммы и выбросы
> ```
> boxplot(temp ~ month, data = df_long, ...)
> ```

**Хорошо:**

> Для поиска выбросов по методу Тьюки рассчитываются границы
> [Q1 − 1,5·IQR; Q3 + 1,5·IQR]; диаграммы и границы строятся следующим
> кодом (фрагмент кода):
> ```
> boxplot(temp ~ month, data = df_long, ...)
> ```
> В результате получены диаграммы (рисунок 1) и 33 выброса,
> перечисленные в таблице 4.

## 17. Kiểm tra DOCX/PDF trước khi giao

- Mở DOCX bằng Word: không lỗi font, không lỗi bảng.
- Xuất PDF: không có trang trắng, không có bảng bị cắt.
- Trang bìa đúng, không có số trang.
- Tất cả heading in đậm, căn giữa.
- Tất cả bảng/hình có caption đúng vị trí.
- Đánh số bảng/hình liên tục.
- Không có `я/мы`.
- Số liệu khớp với file tính.
- Tên file đúng quy ước.

