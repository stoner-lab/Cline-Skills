# Đọc đề bài, variant và số liệu

## 1. Nguyên tắc chung

- Đọc kỹ đề bài trước khi hỏi người dùng.
- Xác định đúng variant; không đoán.
- Đối chiếu số liệu giữa đề bài và bảng variant.
- Nếu số liệu nằm trong ảnh, phải đọc ảnh và kiểm tra lại bằng mắt.
- Nếu đề bài và bảng variant mâu thuẫn, hỏi người dùng.

## 2. File `.docx`

Dùng `python-docx`:

```python
from docx import Document
doc = Document(path)
for p in doc.paragraphs:
    if p.text.strip():
        print(p.text)
for i, table in enumerate(doc.tables, 1):
    print("TABLE", i)
    for row in table.rows:
        print([c.text for c in row.cells])
```

Lưu ý:
- Bảng có ô merge sẽ trả về cùng một text ở nhiều ô; cần đọc theo hàng.
- Ảnh trong docx nằm ở `word/media/`; giải nén để đọc.
- Công thức có thể nằm trong `word/document.xml` dưới dạng OMML; nếu cần,
  đọc text hoặc chuyển sang PDF.

Giải nén ảnh:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($docx, $tmp)
Get-ChildItem $tmp\word\media
```

Sau đó dùng `read_files` để xem ảnh variant.

## 3. File `.pdf`

Dùng `pypdfium2`:

```python
import pypdfium2 as pdfium
pdf = pdfium.PdfDocument(path)
for i in range(len(pdf)):
    print(pdf[i].get_textpage().get_text_range())
```

Nếu PDF là ảnh scan, render trang thành PNG rồi đọc bằng `read_files`:

```python
pdf[i].render(scale=2).to_pil().save(f"page_{i+1}.png")
```

## 4. File `.pptx`

Giải nén và đọc XML:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory($pptx, $tmp)
Get-ChildItem $tmp\ppt\slides -Filter slide*.xml
```

Đọc text bằng Python:

```python
import zipfile, re
from xml.etree import ElementTree as ET
with zipfile.ZipFile(path) as z:
    for name in sorted(z.namelist()):
        if re.match(r"ppt/slides/slide\d+\.xml$", name):
            root = ET.fromstring(z.read(name))
            texts = [e.text for e in root.iter() if e.tag.endswith("}t") and e.text]
            print(name, " ".join(texts))
```

Ảnh trong PPTX nằm ở `ppt/media/`.

## 5. Bảng variant nằm trong ảnh

Thường gặp trong file đề bài `.docx`:

1. Giải nén docx.
2. Liệt kê `word/media/image*.png/jpeg`.
3. Đọc từng ảnh bằng `read_files`.
4. Xác định ảnh có tiêu đề `Вариант N`.
5. Ghi lại bảng số liệu vào file tạm hoặc biến.

Kiểm tra:
- đúng số variant;
- đúng số hàng/cột;
- đúng dấu thập phân;
- đúng đơn vị;
- không nhầm `−` (minus) với `–` (dash).

## 6. Bảng trong PDF/ảnh

- Render trang với scale 2–3 để đọc rõ.
- Cắt vùng bảng nếu cần.
- Đọc theo hàng, ghi lại header.
- Kiểm tra tổng số hàng so với đề.
- Nếu bảng có ô trống, ghi rõ là 0 hay không có dữ liệu.

## 7. Kiểm tra chéo số liệu

Sau khi nhập số liệu:
- tổng số phương án;
- tổng số tiêu chí/trạng thái;
- tổng trọng số (nếu có);
- giá trị min/max;
- các giá trị nằm ngoài thang;
- đơn vị.

Nếu có sai lệch, dừng lại và hỏi người dùng trước khi tính.

## 8. Lưu số liệu

- Lưu bảng gốc vào một file `.csv` hoặc `.py` để tái sử dụng.
- Không sửa số liệu gốc trong lúc tính.
- Ghi rõ nguồn: `вариант 11, таблица 1`.
- Nếu phải sửa do lỗi đề, ghi chú trong báo cáo.
