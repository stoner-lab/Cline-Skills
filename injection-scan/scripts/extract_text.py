"""extract_text.py - trich noi dung text tu tai lieu de dua vao scan_injection.ps1

Khong goi mang. Khong ghi file (chi in ra stdout).
Dung: python extract_text.py <file> [--max-chars N]
Exit: 0 = ok, 2 = khong trich duoc
"""
import sys
import os

MAX_CHARS = 2_000_000
TEXT_EXT = {'.txt', '.md', '.csv', '.json', '.log', '.py', '.ps1', '.psm1', '.js', '.ts',
            '.xml', '.html', '.htm', '.yaml', '.yml', '.ini', '.cfg', '.bat', '.cmd',
            '.sh', '.sql', '.rtf', '.tex', '.srt', '.vtt'}


def clip(text):
    if text is None:
        return ''
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + '\n[... truncated ...]'
    return text


def from_docx(path):
    try:
        import docx
    except ImportError:
        return None
    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            parts.append(' | '.join(c.text for c in row.cells))
    return '\n'.join(parts)


def from_pptx(path):
    try:
        from pptx import Presentation
    except ImportError:
        return None
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides, 1):
        parts.append(f'--- slide {i} ---')
        for shape in slide.shapes:
            if shape.has_text_frame:
                parts.append(shape.text_frame.text)
    return '\n'.join(parts)


def from_xlsx(path):
    try:
        import openpyxl
    except ImportError:
        return None
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts = []
    for ws in wb.worksheets:
        parts.append(f'--- sheet {ws.title} ---')
        for row in ws.iter_rows(values_only=True):
            cells = [str(c) for c in row if c is not None]
            if cells:
                parts.append(' | '.join(cells))
    wb.close()
    return '\n'.join(parts)


def from_pdf(path):
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError:
            pymupdf = None
    if pymupdf is not None:
        doc = pymupdf.open(path)
        try:
            return '\n'.join(page.get_text() for page in doc)
        finally:
            doc.close()
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    reader = PdfReader(path)
    return '\n'.join((p.extract_text() or '') for p in reader.pages)


def from_zip(path):
    import zipfile
    parts = []
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            ext = os.path.splitext(info.filename)[1].lower()
            if ext in TEXT_EXT:
                try:
                    raw = z.read(info)
                    parts.append(f'--- {info.filename} ---')
                    parts.append(raw.decode('utf-8', errors='replace'))
                except Exception:
                    continue
            else:
                parts.append(f'--- {info.filename} (khong trich) ---')
    return '\n'.join(parts)


def from_text(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def main():
    global MAX_CHARS
    args = [a for a in sys.argv[1:]]
    max_idx = None
    for i, a in enumerate(args):
        if a == '--max-chars' and i + 1 < len(args):
            MAX_CHARS = int(args[i + 1])
            max_idx = i
    if max_idx is not None:
        args = args[:max_idx] + args[max_idx + 2:]
    if not args:
        print('usage: extract_text.py <file> [--max-chars N]', file=sys.stderr)
        return 2

    path = args[0]
    if not os.path.isfile(path):
        print(f'not a file: {path}', file=sys.stderr)
        return 2

    ext = os.path.splitext(path)[1].lower()
    handler = {
        '.docx': from_docx, '.docm': from_docx,
        '.pptx': from_pptx, '.pptm': from_pptx,
        '.xlsx': from_xlsx, '.xlsm': from_xlsx,
        '.pdf': from_pdf,
        '.zip': from_zip,
    }.get(ext, from_text)

    try:
        text = handler(path)
    except Exception as exc:
        print(f'extract error: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 2

    if text is None:
        print(f'khong co thu vien doc {ext}', file=sys.stderr)
        return 2

    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stdout.write(clip(text))
    return 0


if __name__ == '__main__':
    sys.exit(main())
