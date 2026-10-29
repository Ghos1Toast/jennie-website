"""Lägger ut filmerna i filmer-original/ på sidan Inspiration.

Användning (från projektmappen):

    python tools/filmer.py

Kräver ffmpeg. Enklast:   python -m pip install imageio-ffmpeg
(eller ett ffmpeg som redan finns i PATH).

Vad skriptet gör:
1. Komprimerar varje film i filmer-original/ till MP4 (H.264, max 1280 px på
   långsidan) i videos/. Metadata som GPS-position tas bort.
   Filmer som redan är gjorda och inte ändrats hoppas över.
2. Tar en stillbild ur filmen som visas innan man trycker play.
3. Skriver in filmerna i inspiration.html mellan FILMER:START och FILMER:SLUT,
   sorterade efter filnamn. Filnamnet blir bildtext:
       "1 Kök, Nacka.mp4"  ->  "Kök, Nacka"   (siffran i början styr bara ordningen)
4. Har filmen tal: lägg en undertextfil med samma namn bredvid, t.ex.
   "1 Kök, Nacka.vtt", så kopplas den in automatiskt.
5. Tar bort filer i videos/ för filmer som inte längre finns i mappen.
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "filmer-original"
OUT = ROOT / "videos"
PAGE = ROOT / "inspiration.html"
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp"}
MAX_SIDE = 1280
WARN_MB = 25

START = "<!-- FILMER:START – genereras av tools/filmer.py, ändra inte för hand -->"
END = "<!-- FILMER:SLUT -->"
PLACEHOLDER = ('<li class="video-item">\n'
               '  <div class="img-ph img-ph--video">[PLATSHÅLLARE: film]</div>\n'
               '  <p class="gallery-caption"><span class="ph">[PLATSHÅLLARE: kort beskrivning]</span></p>\n'
               '</li>\n') * 4


def find_ffmpeg():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg saknas. Installera med:\n    python -m pip install imageio-ffmpeg\n"
                 "(använd samma python som du kör skriptet med)")


def slug(name):
    table = str.maketrans("åäöÅÄÖéÉ ", "aaoAAOeE-")
    s = "".join(c for c in name.translate(table).lower() if c.isalnum() or c in "-_")
    return re.sub(r"-+", "-", s).strip("-") or "film"


def caption_from(stem):
    return re.sub(r"^\d+[\s._-]*", "", stem).strip()


def run(ffmpeg, args):
    return subprocess.run([ffmpeg, "-hide_banner", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def size_of(ffmpeg, path):
    """Läser bredd x höjd ur ffmpegs utskrift (den färdiga filen har ingen rotation kvar)."""
    out = run(ffmpeg, ["-i", str(path)]).stderr
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", out)
    if not m:
        sys.exit(f"Kunde inte läsa storleken på {path.name}")
    return int(m.group(1)), int(m.group(2))


def encode(ffmpeg, src, mp4, poster):
    scale = (f"scale='if(gt(iw,ih),min({MAX_SIDE},iw),-2)':'if(gt(iw,ih),-2,min({MAX_SIDE},ih))'")
    r = run(ffmpeg, ["-y", "-i", str(src),
                     "-map", "0:v:0", "-map", "0:a:0?",
                     "-map_metadata", "-1", "-map_chapters", "-1",  # tar bort GPS och annan metadata
                     "-vf", scale,
                     "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
                     "-c:a", "aac", "-b:a", "128k",
                     "-movflags", "+faststart",  # kan börja spelas innan hela filen laddats
                     str(mp4)])
    if r.returncode != 0:
        mp4.unlink(missing_ok=True)
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "okänt fel")
    # Stillbild efter 1 sekund (eller första bilden om filmen är kortare)
    for t in ("1", "0"):
        if run(ffmpeg, ["-y", "-ss", t, "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(poster)]).returncode == 0 \
                and poster.exists():
            break


def item_html(name, caption, w, h, has_vtt):
    cap = html.escape(caption, quote=True)
    wide = " video-item--wide" if w > h else ""
    track = (f'\n    <track kind="captions" src="videos/{name}.vtt" srclang="sv" label="Svenska" default>'
             if has_vtt else "")
    cap_p = f'\n  <p class="gallery-caption">{cap}</p>' if cap else ""
    label = f' aria-label="{cap}"' if cap else ""
    return (f'<li class="video-item{wide}">\n'
            f'  <video controls preload="none" playsinline poster="videos/{name}.jpg" width="{w}" height="{h}"{label}>\n'
            f'    <source src="videos/{name}.mp4" type="video/mp4">{track}\n'
            f'  </video>{cap_p}\n'
            f'</li>\n')


def write_block(items):
    s = PAGE.read_text(encoding="utf-8")
    m = re.search(r"( *)" + re.escape(START) + r"\n.*?( *)" + re.escape(END), s, re.S)
    if not m:
        sys.exit("Hittar inte FILMER:START/SLUT i inspiration.html")
    indent = m.group(1)
    body = "".join(items) if items else PLACEHOLDER
    body = "".join(indent + line + "\n" for line in body.rstrip("\n").split("\n"))
    PAGE.write_text(s[:m.start()] + f"{indent}{START}\n{body}{indent}{END}" + s[m.end():],
                    encoding="utf-8", newline="\n")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ffmpeg = find_ffmpeg()
    OUT.mkdir(exist_ok=True)
    sources = sorted((p for p in SRC.iterdir() if p.suffix.lower() in VIDEO_EXT), key=lambda p: p.name.lower())
    print(f"{len(sources)} filmer i filmer-original/")

    items, used, warnings = [], set(), []
    for src in sources:
        name = slug(src.stem)
        if name in used:
            name = f"{name}-{len(used)}"
        mp4, poster = OUT / f"{name}.mp4", OUT / f"{name}.jpg"
        if not mp4.exists() or mp4.stat().st_mtime < src.stat().st_mtime:
            print(f"  komprimerar {src.name} … (kan ta en stund)")
            try:
                encode(ffmpeg, src, mp4, poster)
            except RuntimeError as e:
                warnings.append(f"{src.name}: kunde inte komprimeras ({e})")
                continue
        mb = mp4.stat().st_size / 1_000_000
        if mb > WARN_MB:
            warnings.append(f"{src.name} blev {mb:.0f} MB – korta filmen eller den laddar långsamt")
        vtt_src = src.with_suffix(".vtt")
        if vtt_src.exists():
            shutil.copyfile(vtt_src, OUT / f"{name}.vtt")
        w, h = size_of(ffmpeg, mp4)
        used.add(name)
        items.append(item_html(name, caption_from(src.stem), w, h, vtt_src.exists()))
        print(f"  {name}.mp4  {w}x{h}  {mb:.1f} MB")

    write_block(items)
    print(f"inspiration.html: {len(items)} filmer")

    for f in OUT.iterdir():
        if f.is_file() and f.stem not in used:
            f.unlink()
            print(f"  tog bort {f.name}")

    for w in warnings:
        print("VARNING:", w)


if __name__ == "__main__":
    main()
