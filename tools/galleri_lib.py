"""Gemensamt för bilder.py och filmer.py: läser och skriver galleriet i HTML-sidorna.

Galleriet ligger mellan GALLERI:START och GALLERI:SLUT. Bilder (från bilder.py)
och filmer (från filmer.py) blandas jämnt, så att varje skript kan köras för sig
utan att ta bort det andra skriptets innehåll.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = "<!-- GALLERI:START – genereras av tools/bilder.py och tools/filmer.py, ändra inte för hand -->"
END = "<!-- GALLERI:SLUT -->"
_BLOCK = re.compile(r"( *)<!-- GALLERI:START[^\n]*-->\n(.*?)( *)" + re.escape(END), re.S)
_ITEM = re.compile(r"<li class=\"gallery-item.*?</li>\n", re.S)


def is_video(item):
    return "gallery-item--video" in item


def _find(page):
    path = ROOT / page
    s = path.read_text(encoding="utf-8")
    m = _BLOCK.search(s)
    if not m:
        sys.exit(f"Hittar inte GALLERI:START/SLUT i {page}")
    return path, s, m


def read_items(page):
    """Alla <li> i galleriet, utan indrag."""
    _, _, m = _find(page)
    indent = m.group(1)
    body = "".join(line[len(indent):] if line.startswith(indent) else line
                   for line in m.group(2).splitlines(keepends=True))
    return _ITEM.findall(body)


def mix(photos, videos):
    """Sprider filmerna jämnt mellan bilderna. Första kortet är alltid en bild
    (den laddas först), och två filmer hamnar inte bredvid varandra så länge
    det finns bilder nog."""
    if not photos:
        return list(videos)
    out, n, m = [], len(photos), len(videos)
    # Filmen k (0-baserad) läggs efter bild nummer round((k+1) * n / (m+1))
    after = [max(1, round((k + 1) * n / (m + 1))) for k in range(m)]
    vi = 0
    for i, photo in enumerate(photos, start=1):
        out.append(photo)
        while vi < m and after[vi] == i:
            out.append(videos[vi])
            vi += 1
    out.extend(videos[vi:])
    return out


def write_items(page, items):
    path, s, m = _find(page)
    indent = m.group(1)
    body = "".join(items)
    lines = "".join((indent + line + "\n") if line else "\n" for line in body.rstrip("\n").split("\n")) if body else ""
    path.write_text(s[:m.start()] + f"{indent}{START}\n{lines}{indent}{END}" + s[m.end():],
                    encoding="utf-8", newline="\n")
