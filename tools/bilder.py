"""Bygger galleriet från bilder-original/ och galleri.csv.

Användning (från projektmappen):

    python tools/bilder.py

Kräver Pillow 11.3+ (AVIF):   python -m pip install pillow
iPhone-bilder (.heic) kräver dessutom:   python -m pip install pillow-heif

Vad skriptet gör:
1. Läser galleri.csv (en rad per bild, i den ordning de ska visas).
2. Gör webbversioner av varje bild i bilder-original/ till images/projekt/
   (480/960/1600 px bred i AVIF, WebP och JPEG). Platsdata (GPS) och annan
   EXIF tas bort. Bilder som redan är gjorda och inte ändrats hoppas över.
3. Skriver in galleriet i inspiration.html (alla bilder) och index.html
   (bilder med startsida = ja, max 6) mellan GALLERI:START och GALLERI:SLUT.
4. Tar bort webbversioner av bilder som inte längre finns med i galleri.csv.
5. Varnar för saknade filer, saknad alt-text och bilder som ligger i
   mappen men inte står i galleri.csv.
"""
import csv
import html
import io
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow saknas. Installera med:\n    python -m pip install pillow pillow-heif\n"
             "(använd samma python som du kör skriptet med)")

try:  # valfritt: stöd för iPhone-bilder
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "bilder-original"
OUT = ROOT / "images" / "projekt"
CSV_PATH = ROOT / "galleri.csv"
WIDTHS = (480, 960, 1600)
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
SIZES = "(min-width: 900px) min(33vw, 410px), 50vw"
MAX_START = 6

START = "<!-- GALLERI:START – genereras av tools/bilder.py från galleri.csv, ändra inte för hand -->"
END = "<!-- GALLERI:SLUT -->"

PLACEHOLDER = {
    "index.html": '<li class="gallery-item"><div class="img-ph img-ph--card">[PLATSHÅLLARE: projektbild]</div></li>\n' * 6,
    "inspiration.html": ('<li class="gallery-item">\n'
                         '  <div class="img-ph img-ph--card">[PLATSHÅLLARE: projektbild]</div>\n'
                         '  <p class="gallery-caption"><span class="ph">[PLATSHÅLLARE: rum, ort]</span></p>\n'
                         '</li>\n') * 12,
}

warnings = []


def slug(name):
    table = str.maketrans("åäöÅÄÖéÉ ", "aaoAAOeE-")
    s = "".join(c for c in name.translate(table).lower() if c.isalnum() or c in "-_")
    return re.sub(r"-+", "-", s).strip("-") or "bild"


def read_csv():
    raw = CSV_PATH.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:  # Excel sparar ibland som Windows-1252
        text = raw.decode("cp1252")
    delimiter = ";" if text.splitlines()[0].count(";") > text.splitlines()[0].count(",") else ","
    rows = []
    for i, row in enumerate(csv.DictReader(io.StringIO(text), delimiter=delimiter), start=2):
        row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
        if not row.get("fil"):
            continue
        row["rad"] = i
        rows.append(row)
    return rows


def make_versions(src, name):
    """Skapar webbversioner om de saknas eller originalet är nyare. Returnerar (bredd, höjd) för 960-versionen."""
    newest = OUT / f"{name}-1600.jpg"
    im = None
    if not newest.exists() or newest.stat().st_mtime < src.stat().st_mtime:
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        for w in WIDTHS:
            tw = min(w, im.width)  # skala aldrig upp, men behåll filnamnet så att srcset stämmer
            r = im.resize((tw, round(im.height * tw / im.width)), Image.LANCZOS)
            # Ingen exif= skickas med, så GPS och annan metadata följer inte med
            r.save(OUT / f"{name}-{w}.avif", quality=55)
            r.save(OUT / f"{name}-{w}.webp", quality=78)
            r.save(OUT / f"{name}-{w}.jpg", quality=80, optimize=True, progressive=True)
        print(f"  skapade  {name}")
    with Image.open(OUT / f"{name}-960.jpg") as m:
        return m.size


def caption(row):
    text = row.get("bildtext", "")
    color = row.get("farg", "") or row.get("färg", "")
    return f"{text}. {color}" if text and color else (text or color)


def item_html(row, name, size, eager):
    w, h = size
    cap = html.escape(caption(row), quote=True)
    alt = html.escape(row.get("alt", ""), quote=True)
    srcset = lambda ext: f"images/projekt/{name}-480.{ext} 480w, images/projekt/{name}-960.{ext} 960w"
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    cap_p = f'\n  <p class="gallery-caption">{cap}</p>' if cap else ""
    return (f'<li class="gallery-item">\n'
            f'  <a class="gallery-link" href="images/projekt/{name}-1600.jpg" data-caption="{cap}">\n'
            f'    <picture>\n'
            f'      <source type="image/avif" srcset="{srcset("avif")}" sizes="{SIZES}">\n'
            f'      <source type="image/webp" srcset="{srcset("webp")}" sizes="{SIZES}">\n'
            f'      <img src="images/projekt/{name}-960.jpg" srcset="{srcset("jpg")}" sizes="{SIZES}" '
            f'width="{w}" height="{h}" {loading} decoding="async" alt="{alt}">\n'
            f'    </picture>\n'
            f'  </a>{cap_p}\n'
            f'</li>\n')


def write_block(page, items):
    path = ROOT / page
    s = path.read_text(encoding="utf-8")
    m = re.search(r"( *)" + re.escape(START) + r"\n.*?( *)" + re.escape(END), s, re.S)
    if not m:
        sys.exit(f"Hittar inte GALLERI:START/SLUT i {page}")
    indent = m.group(1)
    body = "".join(items) if items else PLACEHOLDER[page]
    body = "".join(indent + line + "\n" if line else "\n" for line in body.rstrip("\n").split("\n"))
    s = s[:m.start()] + f"{indent}{START}\n{body}{indent}{END}" + s[m.end():]
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # å/ä/ö i Windows-terminalen
    OUT.mkdir(parents=True, exist_ok=True)
    rows = read_csv()
    print(f"{len(rows)} bilder i galleri.csv")

    built, used_names, seen_names = [], set(), {}
    for row in rows:
        src = SRC / row["fil"]
        if not src.exists():
            warnings.append(f"rad {row['rad']}: hittar inte bilder-original/{row['fil']} – hoppar över")
            continue
        name = slug(src.stem)
        if name in seen_names and seen_names[name] != row["fil"]:
            name = f"{name}-{row['rad']}"
        seen_names[name] = row["fil"]
        if not row.get("alt"):
            warnings.append(f"rad {row['rad']} ({row['fil']}): alt-text saknas – beskriv vad som syns på bilden")
        try:
            size = make_versions(src, name)
        except Exception as e:  # t.ex. HEIC utan pillow-heif
            warnings.append(f"rad {row['rad']} ({row['fil']}): kunde inte läsas ({e}). "
                            "Är det en .heic? Kör: python -m pip install pillow-heif")
            continue
        used_names.add(name)
        built.append((row, name, size))

    write_block("inspiration.html", [item_html(r, n, s, i == 0) for i, (r, n, s) in enumerate(built)])

    start = [b for b in built if b[0].get("startsida", "").lower() in ("ja", "j", "x", "yes", "1")]
    if len(start) > MAX_START:
        warnings.append(f"{len(start)} bilder är märkta för startsidan – bara de {MAX_START} första visas")
    write_block("index.html", [item_html(r, n, s, False) for r, n, s in start[:MAX_START]])
    print(f"inspiration.html: {len(built)} bilder, index.html: {len(start[:MAX_START])} bilder")

    # Städa bort webbversioner av bilder som inte längre används
    for f in OUT.iterdir():
        if f.is_file() and re.sub(r"-(480|960|1600)$", "", f.stem) not in used_names:
            f.unlink()
            print(f"  tog bort {f.name}")

    listed = {r["fil"].lower() for r in rows}
    for f in sorted(SRC.iterdir()):
        if f.suffix.lower() in IMAGE_EXT and f.name.lower() not in listed:
            warnings.append(f"{f.name} ligger i bilder-original/ men står inte i galleri.csv")

    for w in warnings:
        print("VARNING:", w)


if __name__ == "__main__":
    main()
