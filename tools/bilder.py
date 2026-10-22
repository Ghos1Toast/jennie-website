"""Gör webbversioner av projektbilder till galleriet.

Användning (kräver Pillow 11.3+ för AVIF:  python -m pip install pillow):

    python tools/bilder.py MAPP_MED_ORIGINALBILDER

Varje bild blir 480/960/1600 px bred i AVIF, WebP och JPEG i images/projekt/,
och ett färdigt <li>-block skrivs ut som du klistrar in i inspiration.html.
Fyll i alt-text och bildtext i blocket. Originalen läggs inte i repot.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

WIDTHS = (480, 960, 1600)
OUT = Path(__file__).resolve().parent.parent / "images" / "projekt"
SIZES = "(min-width: 1100px) 25vw, (min-width: 700px) 33vw, 50vw"


def slug(name):
    table = str.maketrans("åäöÅÄÖ ", "aaoAAO-")
    return "".join(c for c in name.translate(table).lower() if c.isalnum() or c == "-")


def process(path):
    # exif_transpose vänder mobilbilder rätt; EXIF (bl.a. GPS-position) sparas inte i utfilerna
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    name = slug(path.stem)
    for w in WIDTHS:
        tw = min(w, im.width)  # skala aldrig upp, men behåll filnamnet så att srcset stämmer
        r = im.resize((tw, round(im.height * tw / im.width)), Image.LANCZOS)
        r.save(OUT / f"{name}-{w}.avif", quality=55)
        r.save(OUT / f"{name}-{w}.webp", quality=78)
        r.save(OUT / f"{name}-{w}.jpg", quality=80, optimize=True, progressive=True)
    h960 = round(im.height * 960 / im.width)
    srcset = lambda ext: f"images/projekt/{name}-480.{ext} 480w, images/projekt/{name}-960.{ext} 960w"
    return f"""          <li class="gallery-item">
            <a class="gallery-link" href="images/projekt/{name}-1600.jpg" data-caption="BILDTEXT">
              <picture>
                <source type="image/avif" srcset="{srcset('avif')}" sizes="{SIZES}">
                <source type="image/webp" srcset="{srcset('webp')}" sizes="{SIZES}">
                <img src="images/projekt/{name}-960.jpg" srcset="{srcset('jpg')}" sizes="{SIZES}" width="960" height="{h960}" loading="lazy" decoding="async" alt="ALT-TEXT">
              </picture>
            </a>
            <p class="gallery-caption">BILDTEXT</p>
          </li>"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1])
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".heic", ".webp"))
    for p in files:
        try:
            print(process(p))
        except Exception as e:  # t.ex. HEIC utan pillow-heif
            print(f"<!-- Hoppade över {p.name}: {e} -->", file=sys.stderr)


if __name__ == "__main__":
    main()
