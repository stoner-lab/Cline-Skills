# -*- coding: utf-8 -*-
"""Проверка окружения для скилла `otchet`.

Что проверяется: python, пакеты (python-docx, pypdf, pypdfium2, lxml), шрифт
Times New Roman, файлы скилла (шаблон титула, скрипты) и MS Word через COM
(нужен для экспорта PDF и обновления поля TOC).

    python scripts/check_env.py

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


def report(kind: str, name: str, detail: str = "") -> None:
    global fails
    if kind == "fail":
        fails += 1
    print(f"  {mark[kind]} {name:<14} {detail}")


def check_python() -> None:
    version = platform.python_version()
    kind = "ok" if sys.version_info >= (3, 9) else "fail"
    report(kind, "python", f"{version} ({sys.executable})")


def check_modules() -> None:
    required = {"docx": "python-docx", "pypdf": "pypdf", "lxml": "lxml"}
    optional = {"pypdfium2": "pypdfium2 (проверка PDF)", "PIL": "Pillow (картинки)"}
    for mod, pip_name in required.items():
        if importlib.util.find_spec(mod):
            report("ok", pip_name, _version(mod))
        else:
            report("fail", pip_name, f"нет: python -m pip install {pip_name.split()[0]}")
    for mod, pip_name in optional.items():
        if importlib.util.find_spec(mod):
            report("ok", pip_name, _version(mod))
        else:
            report("warn", pip_name, "не установлен – соответствующая проверка пропускается")


def _version(mod: str) -> str:
    try:
        module = importlib.import_module(mod)
        return str(getattr(module, "__version__", "") or "")
    except Exception as exc:                            # noqa: BLE001
        return f"ошибка импорта: {exc}"


def check_fonts() -> None:
    for name in ("times.ttf", "timesbd.ttf"):
        path = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / name
        report("ok" if path.exists() else "warn", f"font {name}",
               "" if path.exists() else "Times New Roman не найден – Word подставит другой")


def check_files() -> None:
    for rel in ("SKILL.md", "assets/templates/title_page_leti.docx",
                "scripts/docx_helpers.py", "scripts/validate_docx.py",
                "scripts/strip_metadata.py"):
        path = SKILL_ROOT / rel
        report("ok" if path.exists() else "fail", "file", rel)


def check_word() -> None:
    """MS Word через COM: без него DOCX собирается, PDF и TOC – нет.

    Проверяется только создание COM-объекта: полноценный экспорт PDF занимает
    десятки секунд и уже покрыт ``selftest.py --pdf``.
    """
    script = r"""
$ErrorActionPreference = 'Stop'
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try { "OK $($word.Version)" } finally { $word.Quit() }
"""
    fd, ps1_name = tempfile.mkstemp(suffix=".ps1")
    os.close(fd)                       # иначе Windows блокирует файл для PowerShell
    ps1 = Path(ps1_name)
    try:
        ps1.write_text(script, encoding="utf-8-sig")
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1)],
            capture_output=True, text=True, timeout=60,
        )
        out = (result.stdout or "").strip()
        if result.returncode == 0 and out.startswith("OK"):
            report("ok", "ms word", f"v{out.split()[1]} – PDF и TOC доступны")
        else:
            report("warn", "ms word", "COM не отвечает: " + (out or result.stderr or "")[:120])
    except Exception as exc:                            # noqa: BLE001
        report("warn", "ms word", f"COM недоступен: {exc}")
    finally:
        try:
            ps1.unlink(missing_ok=True)
        except OSError:
            pass


def main() -> int:
    print(f"Окружение скилла otchet ({SKILL_ROOT})")
    check_python()
    check_modules()
    check_fonts()
    check_files()
    check_word()
    print()
    if fails:
        print(f"  {fails} обязательных компонентов не хватает – см. FAIL выше.")
        return 1
    print("  Всё обязательное на месте. PDF и обновление TOC зависят от MS Word (см. выше).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
