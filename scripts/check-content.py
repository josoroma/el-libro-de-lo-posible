#!/usr/bin/env python3
"""Check local links, chapter continuity, section assets and portable edition.

Run after packaging: python3 scripts/check-content.py
Uses only the Python standard library; it never visits external URLs.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "web/index.html", "web/completo.html", "web/simbolos/index.html")


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.links = []
        self.ids = set()
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
        self.links.extend(values[key] for key in ("src", "href") if key in values)


def read_book(root):
    source = (root / "web/data/libro.js").read_text(encoding="utf-8")
    return json.loads(source.removeprefix("window.LIBRO = ").rstrip(";\n"))


def validate(root, offline=False):
    root = root.resolve()
    book = read_book(root)
    chapters = book["chapters"]
    assert len(chapters) == 36, "Expected the opening and 35 chapters"
    assert [chapter["numero"] for chapter in chapters] == list(range(36)), "Chapter numbering changed"
    slugs = {chapter["slug"] for chapter in chapters}
    assert len(slugs) == len(chapters), "Duplicate chapter slug"
    pages = {name: Page((root / name).read_text(encoding="utf-8")) for name in PAGES}
    references = 0

    def check_link(origin, href, chapter=False):
        nonlocal references
        url = urlsplit(href)
        if url.scheme or href.startswith("//"):
            return
        references += 1
        if chapter and not url.path:
            assert url.fragment in slugs, f"Unknown chapter {origin}: {href}"
            return
        target = ((root / origin).parent / unquote(url.path)).resolve() if url.path else root / origin
        if target.is_dir():
            target = target / "index.html"
        assert target.is_file(), f"Missing local reference {origin}: {href}"
        if url.fragment and target.suffix == ".html":
            relative = target.relative_to(root).as_posix()
            ids = slugs if relative == "web/index.html" else pages[relative].ids
            assert url.fragment in ids, f"Missing fragment {origin}: {href}"

    for name, page in pages.items():
        for href in page.links:
            check_link(name, href)
    for index, chapter in enumerate(chapters):
        assert chapter["prev"] == (chapters[index - 1]["slug"] if index else None), "Broken previous chapter"
        assert chapter["next"] == (chapters[index + 1]["slug"] if index + 1 < len(chapters) else None), "Broken next chapter"
        assert (root / "web/assets/art" / chapter["ilustracion"]).is_file(), "Missing chapter illustration"
        for href in Page(chapter["html"]).links:
            check_link("web/index.html", href, chapter=True)
        if chapter["audio_disponible"]:
            assert not offline, "Portable chapter requests unavailable audio"
            audio = f'{chapter["numero"]:02d}-{chapter["slug"]}.mp3'
            assert (root / "web/assets/audio" / audio).is_file(), "Missing available audio"
    for slug in re.findall(r"slug:\s*'([^']+)'", (root / "web/assets/js/product.js").read_text()):
        assert slug in slugs, f"Unknown interactive-lab chapter: {slug}"
    if offline:
        assert book["edicion"] == "portatil-sin-audio"
        assert all(chapter["audio_nota"] for chapter in chapters)
        assert not any(root.rglob("*.mp3")), "Portable edition unexpectedly contains audio"
    else:
        pending = json.loads((root / "web/audio-pendiente.json").read_text())["capitulos"]
        assert all(not chapters[number]["audio_disponible"] for number in pending), "Stale recording enabled"
    return references


def main():
    online_count = validate(ROOT)
    with zipfile.ZipFile(ROOT / "releases/el-libro-de-lo-posible.zip") as archive:
        assert archive.testzip() is None, "Corrupt ZIP"
        assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in archive.namelist())
        with tempfile.TemporaryDirectory(prefix="libro-check-") as directory:
            archive.extractall(directory)
            offline_count = validate(Path(directory), offline=True)
    print(f"OK: 36 chapters; {online_count} online and {offline_count} offline local references; chapter chain, 4 illustrations, audio availability and ZIP integrity")


if __name__ == "__main__":
    main()
