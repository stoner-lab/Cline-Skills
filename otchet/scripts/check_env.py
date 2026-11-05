# -*- coding: utf-8 -*-
"""Проверка окружения для скилла `otchet`.

Что проверяется: python, пакеты (python-docx, pypdf, pypdfium2, lxml), шрифт
Times New Roman, файлы скилла (шаблон титула, скрипты), MS Word через COM
(нужен для экспорта PDF и обновления поля TOC) и фоновые WINWORD.EXE, которые
держат Normal.dotm и вызывают окно Word «This file is in use by another
application or user».

    python scripts/check_env.py                 # только отчёт
    python scripts/check_env.py --clean-word    # закрыть фоновые WINWORD.EXE

``--clean-word`` убивает процессы, поэтому запускать его можно только после
согласия пользователя.

Код возврата: 0 – можно работать, 1 – нет обязательного компонента.
"""
from __future__ import annotations

import importlib.util
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
mark = {"ok": "OK  ", "warn": "WARN", "fail": "FAIL"}
fails = 0
hints: list[str] = []          # что именно предложить пользователю

PIP = "python -m pip install "
WORD_URL = "https://www.microsoft.com/microsoft-365/word"
CLONE_HINT = ("git clone --depth 1 https://github.com/stoner-lab/Cline-Skills.git "
              "\"%TEMP%\\cline-skills\" then copy "
              "\"%TEMP%\\cline-skills\\otchet\" into \"%USERPROFILE%\\.cline\\skills\\\"")


def report(kind: str, name: str, detail: str = "", hint: str = "") -> None:
    global fails
    if kind == "fail":
        fails += 1
    if hint:
        hints.append(hint)
    print(f"  {mark[kind]} {name:<14} {detail}")


def check_python() -> None:
    version = platform.python_version()
    kind = "ok" if sys.version_info >= (3, 9) else "fail"
    report(kind, "python", f"{version} ({sys.executable})",
           hint="" if kind == "ok" else "https://www.python.org/downloads/")


def check_modules() -> None:
    required = {"docx": "python-docx", "pypdf": "pypdf", "lxml": "lxml"}
    optional = {"pypdfium2": "pypdfium2", "PIL": "Pillow"}
    for mod, pip_name in required.items():
        if importlib.util.find_spec(mod):
            report("ok", pip_name, _version(mod))
        else:
            report("fail", pip_name, "не установлен",
                   hint=PIP + pip_name.lower())
    for mod, pip_name in optional.items():
        if importlib.util.find_spec(mod):
            report("ok", pip_name, _version(mod))
        else:
            report("warn", pip_name, "не установлен – соответствующая проверка пропускается",
                   hint=PIP + pip_name.lower())


def _version(mod: str) -> str:
    try:
        module = importlib.import_module(mod)
        return str(getattr(module, "__version__", "") or "")
    except Exception as exc:                            # noqa: BLE001
        return f"ошибка импорта: {exc}"


def check_fonts() -> None:
    for name in ("times.ttf", "timesbd.ttf"):
        path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / name
        exists = path.exists()
        report("ok" if exists else "warn", f"font {name}",
               "" if exists else "Times New Roman не найден – Word подставит другой",
               hint="" if exists else "установите Microsoft Office (шрифт идёт с ним): "
                                      + WORD_URL)


def check_files() -> None:
    for rel in ("SKILL.md", "assets/templates/title_page_leti.docx",
                "scripts/docx_helpers.py", "scripts/validate_docx.py",
                "scripts/strip_metadata.py"):
        path = SKILL_ROOT / rel
        exists = path.exists()
        report("ok" if exists else "fail", "file", rel,
               hint="" if exists else CLONE_HINT)


def _word_tools():
    """Функции работы с процессами Word из docx_helpers, если пакеты на месте."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from docx_helpers import (close_word_processes, ensure_no_word_left,
                                  wait_for_word_exit, word_processes)
        return word_processes, close_word_processes, wait_for_word_exit, ensure_no_word_left
    except Exception:                                  # noqa: BLE001
        return None, None, None, None


def normal_template() -> Path:
    return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Templates" / "Normal.dotm"


def normal_template_locked() -> bool:
    path = normal_template()
    if not path.exists():
        return False
    try:
        with open(path, "r+b"):
            return False
    except OSError:
        return True


def check_word_processes(clean: bool = False, before=None) -> None:
    """Фоновые WINWORD.EXE держат Normal.dotm и вызывают диалог Word.

    Диалог «This file is in use by another application or user
    (…\\Normal.dotm)» появляется, когда второй экземпляр Word пытается открыть
    Normal.dotm, занятый предыдущим. Обычно это «зомби» от COM-экспорта PDF.
    Здесь они только перечисляются: убивает их ``--clean-word`` по согласию
    пользователя, а ``export_pdf_via_word()`` убирает свои сам.
    """
    word_processes, close_word_processes, wait_for_word_exit, ensure_no_word_left = _word_tools()
    if word_processes is None:
        report("warn", "word procs", "нет python-docx – список процессов не проверить")
        return
    before = [p["id"] for p in word_processes()] if before is None else list(before)
    # Word закрывается асинхронно и иногда не закрывается вовсе: снимаем остатки
    if ensure_no_word_left is not None:
        ensure_no_word_left(before, timeout=6.0)
    procs = word_processes()
    zombies = [p for p in procs if not p["title"]]
    if zombies and clean and close_word_processes is not None:
        removed = close_word_processes([p["id"] for p in zombies])
        report("ok", "word procs", f"закрыто фоновых WINWORD.EXE: {removed}")
        procs = word_processes()
        zombies = [p for p in procs if not p["title"]]
    if zombies:
        ids = ", ".join(str(p["id"]) for p in zombies)
        report("warn", "word procs", f"фоновых WINWORD.EXE: {len(zombies)} ({ids})",
               hint="они держат Normal.dotm и вызывают окно «This file is in use by another "
                    "application or user». Спросите пользователя и закройте их: "
                    "`python scripts\\check_env.py --clean-word` (или Диспетчер задач)")
    elif procs:
        report("ok", "word procs", f"открыт Word пользователя: {len(procs)} – экспорт PDF "
                                   "подключится к нему, второй экземпляр не запускается")
    else:
        report("ok", "word procs", "фоновых WINWORD.EXE нет")

    locked = normal_template_locked()
    if locked and not procs:
        report("warn", "normal.dotm", "заблокирован, хотя Word не запущен – остался процесс "
                                      "или файл держит антивирус",
               hint="закройте Word и повторите проверку; если не помогло – перезагрузка")
    elif locked:
        report("ok", "normal.dotm", "занят открытым Word пользователя (это нормально)")
    else:
        report("ok", "normal.dotm", "свободен")


def check_word() -> None:
    """MS Word через COM: без него DOCX собирается, PDF и TOC – нет.

    Проверяется только создание COM-объекта: полноценный экспорт PDF занимает
    десятки секунд и уже покрыт ``selftest.py --pdf``. Запущенный Word
    переиспользуется, свой экземпляр закрывается – иначе остаётся «зомби»,
    который потом мешает следующему Word. Если фоновый экземпляр уже есть,
    COM не трогаем: он может не отвечать, а причина уже видна в строке
    «word procs».
    """
    word_processes, _, _, _ = _word_tools()
    if word_processes is not None and any(not p["title"] or not p.get("handle")
                                          for p in word_processes()):
        report("warn", "ms word", "COM не проверяли: есть фоновый WINWORD.EXE",
               hint="уберите фоновые процессы (ниже) и повторите проверку")
        return
    script = r"""
$ErrorActionPreference = 'Stop'
$startedNew = $false
$word = $null
try {
    try { $word = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application') }
    catch { $word = New-Object -ComObject Word.Application; $startedNew = $true; $word.Visible = $false }
    $word.DisplayAlerts = 0
    "OK $($word.Version)"
} finally {
    $empty = $false
    try { $empty = ($word.Documents.Count -eq 0 -and -not $word.Visible) } catch {}
    if ($startedNew -or $empty) { if ($word -ne $null) { try { $word.Quit(0) } catch {} } }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    if ($word -ne $null) { try { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($word) } catch {} }
}
"""
    fd, ps1_name = tempfile.mkstemp(suffix=".ps1")
    os.close(fd)                       # иначе Windows блокирует файл для PowerShell
    ps1 = Path(ps1_name)
    try:
        ps1.write_text(script, encoding="utf-8-sig")
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(ps1)],
            capture_output=True, text=True, timeout=60,
        )
        out = (result.stdout or "").strip()
        if result.returncode == 0 and out.startswith("OK"):
            report("ok", "ms word", f"v{out.split()[1]} – PDF и TOC доступны")
        else:
            report("warn", "ms word", "COM не отвечает: " + (out or result.stderr or "")[:120],
                   hint="установите Microsoft Word: " + WORD_URL)
    except Exception as exc:                            # noqa: BLE001
        report("warn", "ms word", f"COM недоступен: {exc}",
               hint="установите Microsoft Word: " + WORD_URL)
    finally:
        try:
            ps1.unlink(missing_ok=True)
        except OSError:
            pass


def main() -> int:
    clean_word = "--clean-word" in sys.argv[1:]

    print(f"Окружение скилла otchet ({SKILL_ROOT})")
    check_python()
    check_modules()
    check_fonts()
    check_files()
    word_before = []
    tools = _word_tools()
    if tools[0] is not None:
        word_before = [p["id"] for p in tools[0]()]
    check_word()
    check_word_processes(clean=clean_word, before=word_before)
    print()

    if hints:
        print("  Чего не хватает и что можно предложить пользователю:")
        seen = set()
        for hint in hints:
            if hint in seen:
                continue
            seen.add(hint)
            print(f"    - {hint}")
        print()
        print("  ВАЖНО: ничего не устанавливайте сами. Покажите этот список")
        print("  пользователю, спросите разрешение и только потом выполняйте команды.")
        print("  Пока чего-то не хватает – документ собирать не начинайте.")

    if fails:
        print(f"  Итог: {fails} обязательных компонентов нет (см. FAIL выше).")
        return 1
    print("  Итог: всё обязательное на месте. PDF и обновление TOC зависят от MS Word.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
