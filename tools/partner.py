"""Bygger avsnittet Samarbetspartner på startsidan från partner-original/ och partner.csv.

Användning (från projektmappen):

    python tools/partner.py

Kräver Pillow:   python -m pip install pillow

Vad skriptet gör:
1. Läser partner.csv (en rad per partner, i den ordning de ska visas).
   Kolumner: fil;namn;text;lank
     fil   = loggans filnamn i partner-original/ (kan lämnas tom – då visas bara namnet)
     namn  = partnerns namn
     text  = en rad om vad ni gör ihop (valfri)
     lank  = partnerns hemsida, t.ex. https://exempel.se (valfri)
2. Gör webbversioner av loggorna till images/partner/ (PNG och WebP, genomskinlig
   bakgrund behålls). SVG-loggor kopieras som de är – det är bästa formatet för loggor.
3. Skriver in partnerna i index.html mellan PARTNER:START och PARTNER:SLUT.
4. Tar bort loggor i images/partner/ som inte längre används.
"""
import html
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import galleri_lib  # noqa: E402

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow saknas. Installera med:\n    python -m pip install pillow\n"
             "(använd samma python som du kör skriptet med)")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "partner-original"
OUT = ROOT / "images" / "partner"
CSV_PATH = ROOT / "partner.csv"
MAX_BOX = (480, 320)  # dubbla visningsstorleken, skarpt på mobil
LOGO_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
START = "<!-- PARTNER:START – genereras av tools/partner.py, ändra inte för hand -->"
END = "<!-- PARTNER:SLUT -->"

PLACEHOLDER = ('<li class="partner">\n'
               '  <div class="partner-logo">[PLATSHÅLLARE: logga]</div>\n'
               '  <p class="partner-name"><span class="ph">[SAKNAS: namn]</span></p>\n'
               '  <p class="partner-what"><span class="ph">[SAKNAS: en rad om vad ni gör ihop]</span></p>\n'
               '</li>\n') * 3

warnings = []


def slug(name):
    table = str.maketrans("åäöÅÄÖéÉ ", "aaoAAOeE-")
    s = "".join(c for c in name.translate(table).lower() if c.isalnum() or c in "-_")
    return re.sub(r"-+", "-", s).strip("-") or "logga"


def make_logo(src, name):
    """Gör webbversioner om de saknas eller originalet är nyare. Returnerar (sökväg, bredd, höjd, webp-sökväg)."""
    if src.suffix.lower() == ".svg":
        out = OUT / f"{name}.svg"
        if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            shutil.copyfile(src, out)
            print(f"  kopierade {out.name}")
        return f"images/partner/{out.name}", None, None, None
    png, webp = OUT / f"{name}.png", OUT / f"{name}.webp"
    if not png.exists() or png.stat().st_mtime < src.stat().st_mtime:
        im = Image.open(src)
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        im.thumbnail(MAX_BOX, Image.LANCZOS)  # skalar bara ner, aldrig upp
        # Ingen exif= skickas med, så metadata följer inte med
        im.save(png, optimize=True)
        im.save(webp, quality=90)
        print(f"  skapade  {name}")
    with Image.open(png) as m:
        w, h = m.size
    return f"images/partner/{png.name}", w, h, f"images/partner/{webp.name}"


def item_html(row, logo):
    name = html.escape(row.get("namn", ""))
    text = html.escape(row.get("text", ""))
    link = row.get("lank", "") or row.get("länk", "")
    if link and not re.match(r"https?://", link):
        link = "https://" + link
    # Namnet står som text under loggan, så loggan behöver ingen egen alt-text
    alt = "" if name else html.escape(f"Logotyp {row.get('fil', '')}")
    if logo:
        src, w, h, webp = logo
        size = f' width="{w}" height="{h}"' if w else ""
        img = f'<img src="{src}"{size} loading="lazy" decoding="async" alt="{alt}">'
        if webp:
            img = (f'<picture>\n'
                   f'    <source type="image/webp" srcset="{webp}">\n'
                   f'    {img}\n'
                   f'  </picture>')
        logo_div = f'  <div class="partner-logo">\n    {img.replace(chr(10), chr(10) + "  ")}\n  </div>\n'
    else:
        logo_div = f'  <div class="partner-logo partner-logo--text" aria-hidden="true">{name}</div>\n'
    name_html = f'<a href="{html.escape(link, quote=True)}" rel="noopener">{name}</a>' if link else name
    text_p = f'  <p class="partner-what">{text}</p>\n' if text else ""
    return (f'<li class="partner">\n'
            f'{logo_div}'
            f'  <p class="partner-name">{name_html}</p>\n'
            f'{text_p}'
            f'</li>\n')


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [r for r in galleri_lib.read_csv(CSV_PATH) if r.get("namn") or r.get("fil")] if CSV_PATH.exists() else []
    print(f"{len(rows)} partner i partner.csv")

    items, used = [], set()
    for row in rows:
        if not row.get("namn"):
            warnings.append(f"rad {row['rad']} ({row['fil']}): namn saknas")
        logo = None
        if row.get("fil"):
            src = SRC / row["fil"]
            if not src.exists():
                warnings.append(f"rad {row['rad']}: hittar inte partner-original/{row['fil']} – visar bara namnet")
            else:
                name = slug(src.stem)
                try:
                    logo = make_logo(src, name)
                    used.add(name)
                except Exception as e:
                    warnings.append(f"rad {row['rad']} ({row['fil']}): kunde inte läsas ({e})")
        items.append(item_html(row, logo))

    body = "".join(items) or PLACEHOLDER
    galleri_lib.write_block("index.html", START, END, body)
    print(f"index.html: {len(items) or 'platshållare för'} partner")

    for f in OUT.iterdir():
        if f.is_file() and f.stem not in used:
            f.unlink()
            print(f"  tog bort {f.name}")

    listed = {r.get("fil", "").lower() for r in rows}
    for f in sorted(SRC.iterdir()):
        if f.suffix.lower() in LOGO_EXT and f.name.lower() not in listed:
            warnings.append(f"{f.name} ligger i partner-original/ men står inte i partner.csv")

    for w in warnings:
        print("VARNING:", w)


if __name__ == "__main__":
    main()
