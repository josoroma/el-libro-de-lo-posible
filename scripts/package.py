#!/usr/bin/env python3
"""Build a portable text-and-art edition without audio or development state.

Run from any directory: python3 scripts/package.py
The online source remains unchanged. Only the archived reader is configured
without audio, and the archived cover downloads Markdown instead of itself.
"""
from pathlib import Path
import json
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "releases" / "el-libro-de-lo-posible.zip"
ROOT_FILES = {
    "README.md", "OBRA-COMPLETA.md", "indice.md", "index.html", "index.htm",
    "requirements.txt", ".nojekyll", "LICENSE", "THIRD-PARTY-NOTICES.md",
}
DIRECTORIES = {"web", "capitulos", "simbolos", "assets", "scripts", "docs"}
EXTENSIONS = {".html", ".htm", ".css", ".js", ".mjs", ".json", ".md", ".txt",
              ".cjs", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".woff", ".woff2", ".py"}
EXCLUDED_PARTS = {"__pycache__", "node_modules", ".venv", ".git", "audio", "screenshots", "docs-capturas"}


def included(path):
    relative = path.relative_to(ROOT)
    if not path.is_file() or any(part in EXCLUDED_PARTS for part in relative.parts):
        return False
    return (len(relative.parts) == 1 and path.name in ROOT_FILES) or (
        relative.parts[0] in DIRECTORIES and path.suffix.lower() in EXTENSIONS
    )


def archive_content(path):
    relative = path.relative_to(ROOT).as_posix()
    if relative == "web/data/libro.js":
        source = path.read_text(encoding="utf-8")
        book = json.loads(source.removeprefix("window.LIBRO = ").rstrip(";\n"))
        book["edicion"] = "portatil-sin-audio"
        for chapter in book["chapters"]:
            chapter["audio_disponible"] = False
            chapter["audio_nota"] = "Edición portátil de texto e ilustraciones. El audio no está incluido."
        return ("window.LIBRO = " + json.dumps(book, ensure_ascii=False, indent=1) + ";\n").encode()
    if relative in {"index.html", "index.htm"}:
        source = path.read_text(encoding="utf-8")
        source = source.replace("releases/el-libro-de-lo-posible.zip", "OBRA-COMPLETA.md")
        source = source.replace('href="./"', 'href="index.html"')
        source = re.sub(r'(<[^>]+data-package-label[^>]*>)[^<]*(</[^>]+>)',
                        r'\1Markdown · sin conexión\2', source)
        return source.encode()
    return path.read_bytes()


def main():
    subprocess.run([sys.executable, str(ROOT / "web" / "build.py")], check=True)
    DEST.parent.mkdir(exist_ok=True)
    files = sorted(path for path in ROOT.rglob("*") if included(path))
    with zipfile.ZipFile(DEST, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, archive_content(path))
        note_info = zipfile.ZipInfo("LEEME-EDICION-PORTATIL.txt", date_time=(2026, 1, 1, 0, 0, 0))
        note_info.compress_type = zipfile.ZIP_DEFLATED
        note_info.external_attr = 0o644 << 16
        archive.writestr(note_info, (
            "EL LIBRO DE LO POSIBLE — EDICIÓN PORTÁTIL\n\n"
            "Descomprime esta carpeta y abre index.html.\n"
            "El lector está en web/index.html; la edición sin JavaScript en web/completo.html.\n"
            "Incluye el texto íntegro, ilustraciones, símbolos SVG y fuentes editables.\n"
            "Esta descarga ligera no incluye las grabaciones de audio.\n"
            "El botón de descarga de la portada entrega el Markdown completo.\n"
            "No hace falta instalar Python para leer. Solo se necesita para reconstruir la edición.\n"
        ))
    with zipfile.ZipFile(DEST) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Archive integrity check failed")
    print(f"OK: {DEST.relative_to(ROOT)} · {len(files) + 1} archivos · {DEST.stat().st_size / 1024:.0f} KiB · sin audio")


if __name__ == "__main__":
    main()
