# File mẫu: `assets/templates` và thư mục `Шаблоны`

Skill dùng `assets/templates/` mặc định (đường dẫn tương đối theo vị trí skill).
Thư mục `Шаблоны` bên ngoài chỉ là nguồn tham khảo/legacy; nếu muốn dùng thư
mục ngoài, đặt biến môi trường `OTCHET_TEMPLATES`.

Thư mục này dùng được cho mọi môn học. Nếu học trường/khoa khác hoặc giảng
viên cung cấp mẫu riêng, dùng mẫu đó thay cho các file dưới đây.

## 1. Danh sách mẫu tham khảo

Các file `.doc` dưới đây là nguồn tham khảo bên ngoài, không bắt buộc phải có
trong repo. Skill chỉ cần `assets/templates/title_page_leti.docx` để tham chiếu
trang bìa; cấu trúc thân bài nằm trong `report-types.md`.

| Loại báo cáo | File mẫu | Dùng cho |
|---|---|---|
| Лабораторная работа | `3004_1_ShABLON-lab.r.doc` | báo cáo lab, ПР có tính thực nghiệm |
| Реферат | `3004_2_ShABLON-referata.doc` | реферат |
| Курсовая работа | `3004_3_ShABLON-kursovika.doc` | курсовая |
| Отчёт по практике | `3004_4_ShABLON-otcheta-po-praktike.doc` | отчёт по практике |
| МДП | `3004_5_ShABLON-MDP.doc` | междисциплинарный проект |
| Отчёт по НИР | `3004_6_ShABLON-otcheta-po-NIR.doc` | НИР |
| ИП магистранта | `3004_7_ShABLON-IP-magistranta.doc` | индивидуальный проект магистранта |

## 2. Thứ tự ưu tiên

1. Yêu cầu trong file đề bài của giảng viên.
2. Báo cáo mẫu cùng môn (ví dụ `prak*.docx`, `sys*.docx`, `ПР-*.docx`).
3. File mẫu trong `Шаблоны`.
4. Quy tắc mặc định của skill.

Nếu mẫu cùng môn khác với `Шаблоны`, ưu tiên mẫu cùng môn. Nếu đề bài khác
cả hai, ưu tiên đề bài.

## 3. Cách đọc file `.doc` cũ

Các file trong `Шаблоны` là `.doc` (Word 97–2003), không đọc trực tiếp bằng
`python-docx`. Dùng Word COM ở chế độ chỉ đọc:

```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open($path, $false, $true)
$text = $doc.Content.Text
$doc.Close($false)
$word.Quit()
```

Chỉ đọc, không lưu đè lên file mẫu.

Nếu cần chuyển sang `.docx` để xử lý:

```powershell
$doc.SaveAs([ref]$newPath, [ref]16)  # 16 = wdFormatDocumentDefault (.docx)
```

Chỉ lưu bản chuyển vào thư mục tạm, không sửa file gốc.

## 4. Lấy thông tin bố cục từ mẫu

Cần đọc:
- kích thước trang, lề;
- font, cỡ chữ, giãn dòng;
- vị trí trang bìa;
- thứ tự các mục;
- cách đánh số heading;
- cách đặt caption bảng/hình;
- cách đánh số trang.

Với `.docx`, dùng `python-docx`:

```python
from docx import Document
doc = Document(path)
for p in doc.paragraphs[:40]:
    print(p.style.name, p.alignment, p.text)
for t in doc.tables[:3]:
    print(t.style.name, len(t.rows), len(t.columns))
```

Với `.doc`, dùng Word COM như trên, sau đó đọc `Styles`, `PageSetup`,
`ParagraphFormat`.

## 5. Quy tắc sử dụng mẫu

- **Chỉ học bố cục**, không copy nội dung.
- Không chép câu, đoạn, định nghĩa, kết luận từ mẫu.
- Không đổi tên file mẫu gốc.
- Không lưu đè lên file trong `Шаблоны`.
- Nếu dùng lại bảng, phải thay số liệu và tiêu đề cho đúng bài.
- Nếu mẫu có lỗi chính tả, không lặp lại lỗi đó.

## 6. Trang bìa theo mẫu LETI

Trang bìa **không dựng tay**: `add_title_page()` mở
`assets/templates/title_page_leti.docx`, clone XML của mẫu vào báo cáo và chỉ thay
các chỗ giữ chỗ. Vì vậy mọi thay đổi về bố cục phải làm trong file .docx, không
sửa code.

Cấu trúc mẫu (để đối chiếu khi mở file):

```text
МИНОБРНАУКИ РОССИИ                        (14 pt, đậm, giữa)
САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ       (14 pt, đậm, giữa)
ЭЛЕКТРОТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ            (14 pt, đậm, giữa)
«ЛЭТИ» ИМ. В.И. УЛЬЯНОВА (ЛЕНИНА)         (14 pt, đậm, giữa)
Кафедра <кафедра>

ОТЧЕТ                                     (đậm)
по <тип работы> №<номер>                  (đậm)
по дисциплине «<дисциплина>»              (đậm)
Тема: <тема>                              (đậm)
Вариант <номер>                           (chữ thường, bỏ nếu không có)
  [bảng 2×3: nhãn | ô ký tên có đường kẻ dưới | họ tên, dòng cao 1,08 cm]
Выполненные пункты: <список>              (đậm, bỏ nếu không có)
Дата сдачи работы на проверку – <дата>    (đậm, bỏ nếu không có)

Санкт-Петербург
<год>
```

Bảng chữ ký trong mẫu gồm 3 cột bằng nhau (3118 twips ≈ 5,5 cm), không có khung
bảng, chỉ ô giữa có đường kẻ dưới. Số trang không hiển thị trên trang bìa
(`different_first_page_header_footer = True`).

## 7. Kiểm tra sau khi dùng mẫu

- Trang bìa đúng thứ tự.
- Không còn chữ placeholder (`Название кафедры`, `Иванов И.И.`, `0000`).
- Đúng tên môn, nhóm, giảng viên, variant.
- Không copy nội dung mẫu.
- Đúng font/lề của mẫu hoặc theo đề bài.
