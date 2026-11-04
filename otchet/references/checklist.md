# Checklist trước khi giao báo cáo

## 1. Đề bài và số liệu

- [ ] Đúng loại báo cáo.
- [ ] Đúng môn học.
- [ ] Đúng số bài / chủ đề.
- [ ] Đúng variant.
- [ ] Đúng nhóm, họ tên sinh viên, giảng viên.
- [ ] Đúng hạn nộp.
- [ ] Đã đọc bảng variant (kể cả ảnh).
- [ ] Đã kiểm tra số liệu gốc: số hàng, số cột, đơn vị.
- [ ] Đã kiểm tra giá trị min/max và giới hạn thang.
- [ ] Đã kiểm tra trường hợp biên.
- [ ] Nếu là bài ra quyết định: đã xét `Ничего не делать` / `Не инвестировать` = 0.
- [ ] Nếu không xét phương án 0: đã ghi rõ lý do.

## 2. Nội dung

- [ ] Đủ các mục theo đề.
- [ ] Mỗi mục trả lời: làm gì -> công thức -> kết quả -> nghĩa.
- [ ] Không copy định nghĩa từ giáo trình.
- [ ] Không copy câu/đoạn từ mẫu.
- [ ] Không dùng `я`, `мы`, `мной`, `нами`, `наш`.
- [ ] Không dùng `рассмотрим`, `построим`, `выберем`, `проверим`.
- [ ] Kết quả cuối cùng trả lời đúng câu hỏi của đề.
- [ ] Có nhận xét ngắn sau mỗi bảng kết quả.
- [ ] Kết luận không mâu thuẫn với phần tính.
- [ ] Перед каждым фрагментом кода есть подводка с двоеточием: понятно, что делает код и к какому пункту он относится.
- [ ] После фрагмента кода есть результат или ссылка на таблицу/рисунок.
- [ ] Нет двух блоков кода подряд без текста между ними и кода сразу после заголовка.

## 3. Tính toán

- [ ] Công thức đúng.
- [ ] Thay số đúng.
- [ ] Đơn vị đúng.
- [ ] Làm tròn nhất quán.
- [ ] Tổng trọng số đúng (nếu có).
- [ ] Không chia cho 0.
- [ ] Không bỏ qua phương án 0 (nếu bài cho phép).
- [ ] Đã kiểm tra chéo bằng script hoặc bảng tính.
- [ ] Các bảng kết quả khớp với nhau.

## 4. Định dạng

- [ ] A4, lề trái 3 cm, phải 1,5 cm, trên/dưới 2 cm.
- [ ] Times New Roman 14.
- [ ] Giãn dòng 1,5.
- [ ] Căn đều hai bên.
- [ ] Thụt đầu dòng 1,25 cm.
- [ ] Heading in đậm, căn giữa.
- [ ] Đánh số heading đúng `1.`, `1.1.`.
- [ ] Bảng: caption trên, căn giữa.
- [ ] Hình: caption dưới, căn giữa.
- [ ] Đánh số bảng/hình liên tục toàn tài liệu, không reset.
- [ ] Không có bảng bị tách header.
- [ ] Số trang căn giữa phía dưới.
- [ ] Trang bìa không có số trang.
- [ ] Số thập phân dùng dấu phẩy.
- [ ] Все фрагменты кода оформлены одинаково: Courier New 10, одинарный интервал, отступ 0,5 см; длинные листинги – в приложении со ссылкой в тексте.
- [ ] Hàng nghìn dùng dấu cách.
- [ ] Không có placeholder (`Иванов И.И.`, `0000`, `Название кафедры`).
- [ ] Không có em dash `–`, chỉ dùng `–` (en dash) có dấu cách hai bên.
- [ ] Không có `≻`, `->`, `–`, `...`, ngoặc kép kiểu `" "`: chỉ dùng ký tự sinh viên hay dùng.
- [ ] Dấu `-` chỉ xuất hiện trong từ ghép, tên riêng, mã bài và code.
- [ ] Заголовок `Список источников` по центру, сам список с новой страницы.
- [ ] Все `URL` и `DOI` в списке источников – кликабельные гиперссылки в DOCX и в
  PDF; голого текста `https://…` в документе нет (`validate_docx.py`).


## 5. Trang bìa

- [ ] Đúng tên trường, khoa.
- [ ] Đúng loại báo cáo.
- [ ] Đúng tên môn.
- [ ] Đúng chủ đề.
- [ ] Đúng variant.
- [ ] Đúng nhóm.
- [ ] Đúng họ tên sinh viên.
- [ ] Đúng giảng viên.
- [ ] Đúng ngày nộp.
- [ ] Đúng thành phố/năm.
- [ ] Nếu làm nhóm: ghi rõ phần của từng người.

## 6. File và PDF

- [ ] DOCX mở được, không lỗi font.
- [ ] PDF xuất được.
- [ ] PDF không có trang trắng.
- [ ] PDF không có bảng bị cắt.
- [ ] Tên file đúng quy ước.
- [ ] Đã gửi cả DOCX và PDF.
- [ ] Đã tóm tắt kết quả chính trong chat.

## 7. Kiểm tra nhanh bằng script

```powershell
python scripts/validate_docx.py "duong_dan_bao_cao.docx"
```

Script sẽ cảnh báo:
- sai font/lề;
- heading không căn giữa;
- caption sai vị trí;
- đánh số bảng/hình không liên tục;
- có đại từ nhân xưng;
- trang trắng trong PDF.
