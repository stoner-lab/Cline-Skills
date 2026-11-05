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
| `Вариант <вариант>` | `variant` – **không có trong mẫu**, tự chèn dưới dòng «Тема:» khi có dữ liệu |
| bảng 2×3: `Студент гр. <группа>` / `<Фамилия И.О. студента>` / `<роль из бланка>` / `<Фамилия И.О. руководителя>` | `student_label` + `group`, `student_short` (или `short_name(student)`), `teacher` |
| `Выполненные пункты: <пункты>` | `completed_items` – **không có trong mẫu**, tự chèn khi có dữ liệu |
| `Дата сдачи работы на проверку – <дата>` | `submission_date` – **không có trong mẫu**, tự chèn khi có dữ liệu |
| `<город>`, `<год>` | `city`, `year` |

`work_line` – только для работ с номером (ПР, лабораторные): `по заданию № 1`,
`по практической работе № 2`. Для реферата, курсовой, отчёта по практике, НИР и
МДП его не передавайте – строку про дисциплину даёт `discipline`. Если в
`work_line` всё же попала строка «по дисциплине …», код её отбросит, чтобы на
титуле не было дубля.

Quy tắc cố định của mẫu (không đổi khi điền):

- Mọi dòng trên trang bìa: Times New Roman **14 pt**, căn giữa, giãn dòng 1,5.
- **Cỡ chữ và font của bìa lấy từ бланк, không theo `cfg.font_size`**: bìa luôn là
  14 pt, kể cả khi preset ГОСТ (12 pt) dùng cho phần nội dung. Trước đây
  `_scale_cover_fonts()` ép cả bìa về `cfg.font_size`, nên preset 12 pt làm bìa
  nhỏ và sai font – nay `_normalize_cover_fonts()` chỉ điền chỗ trống trong бланк
  (`COVER_DEFAULT_SIZE = 14`), không đổi cỡ đã có. `validate_docx.py` so từng run
  của bìa với `title_page_leti.docx` và báo FAIL khi lệch.
- 4 dòng tên trường và dòng `Кафедра` in đậm; `ОТЧЕТ`, dòng `по ...`, `по дисциплине`,
  `Тема`, `Выполненные пункты`, `Дата сдачи` in đậm; `Вариант`, thành phố, năm để chữ thường.
- Bảng chữ ký: 3 cột (≈6,2 / 5,6 / 5,0 cm), chiều cao dòng tối thiểu 1,08 cm,
  **không có khung bảng**, chỉ có đường kẻ dưới ở ô giữa (chỗ ký tên).
- **Nhãn cột 1 lấy từ бланк, code không viết lại**: mẫu hiện tại là
  `Студент гр. <группа>` và `Преподаватель/Руководитель`; `_fill_label_cell()`
  chỉ thay `<группа>` và để nguyên chữ của mẫu (ô trống mới dùng
  `student_label`).
- **Подпись роли печатается одна.** Nếu бланк ghi hai vai trò qua «/»
  (`Преподаватель/Руководитель`), `_fill_teacher_label()` +
  `pick_teacher_label()` in **đúng một** từ: `ReportMeta.teacher_label`
  (`Руководитель` mặc định, hoặc `Преподаватель`) – chọn theo методичка/образец,
  không rõ thì hỏi user. Cặp có «/» в готовом файле không được xuất hiện.
- Kết thúc trang bìa bằng dấu ngắt trang; số trang bắt đầu hiển thị từ trang nội dung
  (`different_first_page_header_footer = True`), trang bìa không đánh số.
- **ФИО trên trang bìa – chỉ `Фамилия И.О.`** (họ + chữ cái đầu của tên/đệm), ví dụ
  `Нгуен Т.` hoặc `Нгуен Т.З.`. Tên đầy đủ chỉ dùng trong tên file:
  `Фамилия_Имя_группа` (`Нгуен_Тхе_4395`). Hàm `short_name()` tự rút gọn; nếu cần
  dạng khác – truyền `student_short` trong `ReportMeta`.
- `add_title_page()` kiểm tra trước khi vẽ: thiếu ФИО, ФИО chỉ có họ (không có chữ
  cái đầu) hoặc còn placeholder thì ném `ValueError` – **phải hỏi người dùng** dạng
  đầy đủ «Фамилия Имя Отчество» và số nhóm, không tự đoán.
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
- **ГОСТ 7.32-2017 (5.4.3)**: заголовки печатают **с абзацного отступа** (1,25 см),
  а не по центру. Расхождение с ЛЭТИ; переключается пресетом:
  `cfg = gost_config()` → `heading(doc, "1. Раздел", cfg=cfg)`. Методичка
  кафедры важнее, поэтому по умолчанию остаётся центрирование.

## 5. Bảng

- Caption đặt **phía trên** bảng, căn giữa, cỡ 12:
  `Таблица 3 – Название таблицы`.
- Cách viết gọn nhất: `add_table(..., caption="Таблица 3 – Название")` – hàm tự
  đặt caption phía trên, `keep_with_next`, không thụt dòng đầu.
- **ГОСТ 7.32-2017 (6.4.3)**: наименование таблицы – **слева, без абзацного
  отступа**; в пресете `gost_config()` это уже включено (`table_caption_center=False`).
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
- **В подписи рисунка точка в конце не ставится**, а сам текст идёт **курсивом**
  (методички ЛЭТИ). Всё готово в helper:
  `add_picture_with_caption(doc, path, "Рисунок 1 – Название", cfg=cfg)` или
  `figure_caption(doc, 1, "Название", cfg=cfg)`.
- **ГОСТ 7.32-2017**: слово пишут полностью – `Рисунок 2 – Название рисунка`;
  в пресетах `leti_form_config()` и `gost_config()` это задаёт
  `figure_label="Рисунок"`. Валидатор принимает оба варианта.
- Hình phải rõ, không mờ, không méo.
- Không dùng ảnh chụp màn hình chứa cả thanh công cụ, tab trình duyệt.
- Trong text phải có câu dẫn: `Схема приведена на рис. 2.`
- Hình và caption phải nằm cùng một trang.

## 7. Công thức

- Công thức đặt trên dòng riêng, căn giữa.
- Cỡ 14, cùng font Times New Roman.
- Chỉ số trên/dưới rõ ràng: `x′ij`, `w_i`, `α_i`.
- Nếu công thức được đánh số, đặt số trong ngoặc tròn bên phải:
  `(1)`, `(2)`. Готовый способ: `formula(doc, [("F", None), ("=", None), ("ma", None)], number=1)`
  – формула остаётся по центру, номер уходит к правому краю (ГОСТ 7.32-2017, 6.10).
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

⚠️ **Mục này cũng là optional.** Tạo `Список использованных источников` chỉ khi:
(a) trong bài thực sự có nguồn được trích, hoặc (b) đề bài/методичка yêu cầu.
Không có nguồn thì **không tạo mục rỗng** – `add_references(doc, [])` sẽ ném
`ValueError`; hỏi user nếu đề không nói rõ.

- Danh sách nguồn đặt cuối báo cáo.
- **Danh sách luôn bắt đầu từ trang mới**: dùng `add_references(doc, items)` –
  hàm đặt `page_break_before` cho tiêu đề (không tạo trang trắng như khi chèn
  page break thủ công).
- Tiêu đề mặc định `Список использованных источников` (đúng tên структурного
  элемента ГОСТ 7.32-2017, §4; задаётся `StyleConfig.sources_title`): Times New
  Roman 14, đậm, **căn giữa**, không thụt đầu dòng, cách đoạn sau 6 pt.
  Вариант ЛЭТИ «Список источников» тоже принимается валидатором.
- Mô tả nguồn theo **ГОСТ 7.1 / ГОСТ 7.80**, ví dụ trong Приложение Д и Е самого
  ГОСТ 7.32-2017: автор, заглавие, вид издания, место, издательство, год, объём;
  для электронных – `[Электронный ресурс]`, `URL`, `(дата обращения: ...)`.
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

Quy tắc dưới đây lấy từ ГОСТ 7.32-2017 п.6.17 (проверено по тексту стандарта).

⚠️ **Phụ lục là optional.** Chỉ tạo `ПРИЛОЖЕНИЕ` khi đề bài/методичка yêu cầu, hoặc
user đồng ý (hỏi trước). Không có yêu cầu thì bỏ hẳn – đừng thêm «cho đủ bộ».

- Phụ lục đặt sau danh sách nguồn; mỗi phụ lục bắt đầu từ trang mới.
- Tiêu đề: `ПРИЛОЖЕНИЕ А`, `ПРИЛОЖЕНИЕ Б` – **chữ hoa**, căn giữa. Một phụ lục
  duy nhất vẫn là `ПРИЛОЖЕНИЕ А` (6.17.4).
- **Chữ cái hợp lệ**: А, Б, В, Г, Д, Е, Ж, И, К... – **trừ Ё, З, Й, О, Ч, Ъ, Ы, Ь**;
  nếu dùng chữ Latin thì trừ I và O; hết chữ cái mới dùng số Ả Rập.
- Dưới tiêu đề có thể có dòng trạng thái: `(обязательное)` hoặc `(справочное)`,
  rồi tên phụ lục (in đậm, căn giữa).
- Giấy A4, **cho phép A3** (6.17.5); đánh số trang **liên tục** với phần thân (6.17.6).
- Mọi phụ lục phải được liệt kê trong **mục lục** (6.17.7) – vì vậy `appendix()`
  tạo heading cấp 1 để field TOC bắt được.
- Bảng/hình trong phụ lục vẫn tiếp tục đánh số toàn tài liệu (trừ khi có
  yêu cầu riêng, khi đó dùng `В.1`, `В.2`).
- Không đưa code dài vào thân báo cáo; code dài đưa vào phụ lục và có chú thích
  (quy tắc chi tiết về code – §16).

```python
from docx_helpers import appendix

appendix(doc, "А", "Пример оформления", status="справочное")   # новая страница, ПРИЛОЖЕНИЕ А
para(doc, "Текст приложения.")
```


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

## 18. ГОСТ 7.32-2017: что уже соблюдено и где расходится с ЛЭТИ

Стандарт: **ГОСТ 7.32-2017 «Отчет о научно-исследовательской работе. Структура и
правила оформления»** (с поправками ИУС 2-2019, 3-2019, 1-2022). Он задаёт
структуру отчёта о НИР; методичка кафедры ЛЭТИ уточняет оформление студенческих
работ и **всегда важнее** стандарта.

| Требование | ГОСТ 7.32-2017 | Пресет ЛЭТИ (по умолчанию) | Как включить ГОСТ |
|---|---|---|---|
| Поля | 30 / 15 / 20 / 20 мм | то же | ничего, совпадает |
| Формат | A4 | A4 | — |
| Интервал | 1,5 | 1,5 | — |
| Абзацный отступ | 1,25 см | 1,25 см | — |
| Шрифт | Times New Roman | Times New Roman | — |
| Кегль | 12 пт | 14 пт | `gost_config()` |
| Заголовки | с абзацного отступа | по центру | `gost_config()` (`heading_center=False`) |
| Наименование таблицы | слева, без отступа | по центру | `gost_config()` или `add_table(..., caption_align=WD_ALIGN_PARAGRAPH.LEFT)` |
| Подпись рисунка | `Рисунок 1 – …` | `Рис. 1 – …` | `gost_config()` (`figure_label="Рисунок"`) |
| Номер страницы | внизу по центру, без точки | то же | — |
| Титульный лист | в нумерации, но номер не печатают | то же (`different_first_page`) | — |
| Кегль титула | 14 пт из бланка | 14 пт из бланка | — (бланк один, `cfg.font_size` его не меняет) |
| «Цель работы» | обязательный раздел | обязательный раздел | — (`goal_section()`, иначе FAIL в `validate_docx.py`) |
| Приложения | `ПРИЛОЖЕНИЕ А`, статус, в содержании, сквозная нумерация | так же с `appendix()` | — |
| Список источников | `Список использованных источников` | тот же заголовок по умолчанию | — |

```python
from docx_helpers import gost_config, setup_document, heading, para

cfg = gost_config()                      # кегль 12, заголовки с отступа, таблицы слева
doc = setup_document(cfg=cfg, title="НИР", author="Иванов И.И.")
heading(doc, "1. Раздел", cfg=cfg)
para(doc, "Текст раздела.", cfg=cfg)     # para()/caption() берут кегль и интервал из cfg
```

Структурные элементы ГОСТ 7.32-2017 (§4), которых нет в студенческом ПР и
которые при необходимости собираются из готовых функций:

| Элемент | Чем делать |
|---|---|
| Список исполнителей (§5.2) | `heading()` + `add_table(["Фамилия, инициалы", "Должность", "Подпись, дата"], …)` |
| Реферат (§5.3): объём, число страниц, иллюстраций, таблиц, приложений, ключевые слова | `heading(doc, "РЕФЕРАТ")` + `para()` |
| Содержание (§5.4) | `add_toc(doc)` |
| Термины и определения (§5.5) | `heading()` + `para("В настоящем отчете о НИР применяют следующие термины…")` |
| Перечень сокращений (§5.6) – нужен, если обозначений больше трёх | `heading()` + `para()` |
| Приложения (§6.17) | `appendix(doc, "А", "Название", status="обязательное")` |

Проверка: `python scripts/validate_docx.py report.docx --pdf report.pdf` – среди
прочего считает приложения (`INFO: Appendices: А`) и предупреждает о
недопустимой букве (`Ё`, `З`, `О`…) или о приложении не стилем Heading 1.


