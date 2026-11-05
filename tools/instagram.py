"""Bygger Instagram-rutan på startsidan från instagram.csv.

Användning (från projektmappen):

    python tools/instagram.py

Rutan visar 4–6 utvalda bilder som länkar till inläggen på Instagram. Bilderna
ligger på sajten själv, så besökaren kontaktar inte Instagram förrän hon klickar
(inga cookies, ingen kod från Meta).

instagram.csv, en rad per bild i den ordning de ska visas:
    fil;lank;alt
  fil  = bilden i bilder-original/ (samma mapp som galleriet)
  lank = länken till inlägget, t.ex. https://www.instagram.com/p/ABC123/
         (tom = länkar till profilen tills vidare)
  alt  = vad som syns på bilden (tom = alt-texten från galleri.csv)

Profilen (kontot) står i uppgifter.txt:   instagram = jenniesfargsattningomaleri
Bilderna beskärs kvadratiska från mitten, som på Instagram.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import galleri_lib  # noqa: E402

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow saknas. Installera med:\n    python -m pip install pillow pillow-heif")

try:  # valfritt: stöd för iPhone-bilder
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "bilder-original"
OUT = ROOT / "images" / "instagram"
CSV_PATH = ROOT / "instagram.csv"
SIZES_PX = (400, 800)
SIZES = "(min-width: 900px) min(16vw, 210px), 33vw"
MAX_TILES = 6
START = "<!-- INSTAGRAM:START – genereras av tools/instagram.py, ändra inte för hand -->"
END = "<!-- INSTAGRAM:SLUT -->"

warnings = []


def slug(name):
    table = str.maketrans("åäöÅÄÖéÉ ", "aaoAAOeE-")
    s = "".join(c for c in name.translate(table).lower() if c.isalnum() or c in "-_")
    return re.sub(r"-+", "-", s).strip("-") or "bild"


def profile_url():
    """Profillänken från uppgifter.txt (samma regel som tools/uppgifter.py)."""
    for line in (ROOT / "uppgifter.txt").read_text(encoding="utf-8-sig").splitlines():
        key, _, value = line.partition("=")
        if key.strip() == "instagram" and value.strip():
            handle = value.strip().rstrip("/").split("/")[-1].lstrip("@")
            return f"https://www.instagram.com/{handle}/"
    warnings.append("instagram är tomt i uppgifter.txt – bilderna länkar ingenstans")
    return "#"


def make_versions(src, name):
    newest = OUT / f"{name}-{SIZES_PX[-1]}.jpg"
    if newest.exists() and newest.stat().st_mtime >= src.stat().st_mtime:
        return
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    for px in SIZES_PX:
        r = ImageOps.fit(im, (px, px), Image.LANCZOS)  # kvadrat från mitten
        # Ingen exif= skickas med, så GPS och annan metadata följer inte med
        r.save(OUT / f"{name}-{px}.webp", quality=78)
        r.save(OUT / f"{name}-{px}.jpg", quality=80, optimize=True, progressive=True)
    print(f"  skapade  {name}")


def tile_html(name, link, alt):
    small, big = SIZES_PX
    srcset = lambda ext: f"images/instagram/{name}-{small}.{ext} {small}w, images/instagram/{name}-{big}.{ext} {big}w"
    label = html.escape(f"Se inlägget på Instagram: {alt}" if alt else "Se inlägget på Instagram", quote=True)
    return (f'<li>\n'
            f'  <a class="insta-tile" href="{html.escape(link, quote=True)}" aria-label="{label}">\n'
            f'    <picture>\n'
            f'      <source type="image/webp" srcset="{srcset("webp")}" sizes="{SIZES}">\n'
            f'      <img src="images/instagram/{name}-{small}.jpg" srcset="{srcset("jpg")}" sizes="{SIZES}" '
            f'width="{small}" height="{small}" loading="lazy" decoding="async" alt="">\n'
            f'    </picture>\n'
            f'  </a>\n'
            f'</li>')


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # å/ä/ö i Windows-terminalen
    OUT.mkdir(parents=True, exist_ok=True)
    profile = profile_url()
    gallery_alt = {r["fil"].lower(): r.get("alt", "")
                   for r in galleri_lib.read_csv(ROOT / "galleri.csv") if r.get("fil")}
    rows = [r for r in galleri_lib.read_csv(CSV_PATH) if r.get("fil")]
    if len(rows) > MAX_TILES:
        warnings.append(f"{len(rows)} bilder i instagram.csv – bara de {MAX_TILES} första visas")

    tiles, used = [], set()
    for row in rows[:MAX_TILES]:
        src = SRC / row["fil"]
        if not src.exists():
            warnings.append(f"rad {row['rad']}: hittar inte bilder-original/{row['fil']} – hoppar över")
            continue
        link = row.get("lank", "")
        if not link:
            warnings.append(f"rad {row['rad']} ({row['fil']}): länk till inlägget saknas – länkar till profilen")
            link = profile
        elif "instagram.com" not in link:
            warnings.append(f"rad {row['rad']} ({row['fil']}): '{link}' ser inte ut som en Instagram-länk")
        alt = row.get("alt") or gallery_alt.get(row["fil"].lower(), "")
        name = slug(src.stem)
        try:
            make_versions(src, name)
        except Exception as e:  # t.ex. HEIC utan pillow-heif
            warnings.append(f"rad {row['rad']} ({row['fil']}): kunde inte läsas ({e})")
            continue
        used.add(name)
        tiles.append(tile_html(name, link, alt))

    galleri_lib.write_block("index.html", START, END, "\n".join(tiles))
    print(f"index.html: {len(tiles)} Instagram-bilder")

    # Städa bort bilder som inte längre används
    for f in OUT.iterdir():
        if f.is_file() and re.sub(r"-(\d+)$", "", f.stem) not in used:
            f.unlink()
            print(f"  tog bort {f.name}")

    for w in warnings:
        print("VARNING:", w)


if __name__ == "__main__":
    main()
