"""Lägger ut filmerna i filmer-original/ på sajten.

Användning (från projektmappen):

    python tools/filmer.py

Kräver ffmpeg. Enklast:   python -m pip install imageio-ffmpeg
(eller ett ffmpeg som redan finns i PATH).

Vad skriptet gör:
1. Komprimerar varje film i filmer-original/ till en tyst MP4 (H.264, max
   1280 px på långsidan) i videos/. Ljud och metadata som GPS-position tas bort.
   Filmerna spelas automatiskt utan ljud, så ljudspåret behövs inte – och
   musik från t.ex. Instagram får ändå inte användas på hemsidan.
2. Tar en stillbild ur filmen som visas innan filmen startar.
3. Blandar in filmerna jämnt mellan bilderna i galleriet på inspiration.html,
   sorterade efter filnamn. Den första filmen visas också stort överst på startsidan.
   Filnamnet blir bildtext:
       "1 Kök, Nacka.mov"          ->  "Kök, Nacka"  (siffran styr bara ordningen)
       "Kök_Nacka_1080x1920.mov"   ->  "Kök Nacka"
4. Tar bort filer i videos/ för filmer som inte längre finns i mappen.
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import galleri_lib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "filmer-original"
OUT = ROOT / "videos"
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp"}
MAX_SIDE = 1280
WARN_MB = 15

BLOCKS = {
    "index.html": ("<!-- HERO:START – genereras av tools/filmer.py, ändra inte för hand -->",
                   "<!-- HERO:SLUT -->",
                   '<div class="img-ph img-ph--hero">[PLATSHÅLLARE: film eller projektbild]</div>\n'),
}

TOGGLE = ('<button class="video-toggle" type="button" aria-label="Pausa filmen" hidden>'
          '<span class="video-toggle-icon" aria-hidden="true"></span></button>')


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
    name = re.sub(r"[\s_-]*\d{3,4}x\d{3,4}", "", name)  # "_1080x1920" bort ur filnamnet
    table = str.maketrans("åäöÅÄÖéÉ ", "aaoAAOeE-")
    s = "".join(c for c in name.translate(table).lower() if c.isalnum() or c in "-_")
    return re.sub(r"[-_]+", "-", s).strip("-") or "film"


def caption_from(stem):
    s = re.sub(r"^\d+[\s._-]*", "", stem)             # "1 Kök" -> "Kök"
    s = re.sub(r"[\s_-]*\d{3,4}x\d{3,4}", "", s)       # "_1080x1920" bort
    s = re.sub(r"[_]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def run(ffmpeg, args):
    return subprocess.run([ffmpeg, "-hide_banner", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def size_of(ffmpeg, path):
    """Läser bredd x höjd ur ffmpegs utskrift (den färdiga filen har ingen rotation kvar)."""
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", run(ffmpeg, ["-i", str(path)]).stderr)
    if not m:
        sys.exit(f"Kunde inte läsa storleken på {path.name}")
    return int(m.group(1)), int(m.group(2))


def encode(ffmpeg, src, mp4, poster):
    scale = f"scale='if(gt(iw,ih),min({MAX_SIDE},iw),-2)':'if(gt(iw,ih),-2,min({MAX_SIDE},ih))'"
    r = run(ffmpeg, ["-y", "-i", str(src),
                     "-map", "0:v:0", "-an",                          # bara bild, inget ljud
                     "-map_metadata", "-1", "-map_chapters", "-1",    # tar bort GPS och annan metadata
                     "-vf", scale,
                     "-c:v", "libx264", "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p",
                     "-movflags", "+faststart",                      # kan börja spelas innan hela filen laddats
                     str(mp4)])
    if r.returncode != 0:
        mp4.unlink(missing_ok=True)
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "okänt fel")
    for t in ("1", "0"):  # stillbild efter 1 s, eller första bilden om filmen är kortare
        if run(ffmpeg, ["-y", "-ss", t, "-i", str(mp4), "-frames:v", "1", "-q:v", "3", str(poster)]).returncode == 0 \
                and poster.exists():
            break


def video_tag(name, w, h, cls, preload):
    return (f'<video class="{cls}" muted loop playsinline preload="{preload}" '
            f'poster="videos/{name}.jpg" width="{w}" height="{h}" aria-hidden="true">\n'
            f'  <source src="videos/{name}.mp4" type="video/mp4">\n'
            f'</video>')


def gallery_item(name, caption, w, h):
    cap = html.escape(caption, quote=True)
    video = "\n".join("    " + line for line in video_tag(name, w, h, "autoplay-video", "none").split("\n"))
    cap_p = f'\n  <p class="gallery-caption">{cap}</p>' if cap else ""
    return (f'<li class="gallery-item gallery-item--video">\n'
            f'  <a class="gallery-link" href="videos/{name}.mp4" data-video="videos/{name}.mp4" data-caption="{cap}">\n'
            f'{video}\n'
            f'    <span class="visually-hidden">Film: {cap or "utan bildtext"}</span>\n'
            f'  </a>\n'
            f'  {TOGGLE}{cap_p}\n'
            f'</li>\n')


def hero_item(name, w, h):
    return (f'<div class="hero-video-wrap">\n'
            + "\n".join("  " + line for line in video_tag(name, w, h, "hero-video autoplay-video", "metadata").split("\n"))
            + f'\n  {TOGGLE}\n</div>\n')


def write_block(page, body):
    start, end, placeholder = BLOCKS[page]
    path = ROOT / page
    s = path.read_text(encoding="utf-8")
    m = re.search(r"( *)" + re.escape(start) + r"\n.*?( *)" + re.escape(end), s, re.S)
    if not m:
        sys.exit(f"Hittar inte markeringarna i {page}")
    indent = m.group(1)
    body = body or placeholder
    lines = "".join(indent + line + "\n" for line in body.rstrip("\n").split("\n")) if body else ""
    path.write_text(s[:m.start()] + f"{indent}{start}\n{lines}{indent}{end}" + s[m.end():],
                    encoding="utf-8", newline="\n")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ffmpeg = find_ffmpeg()
    OUT.mkdir(exist_ok=True)
    script_time = Path(__file__).stat().st_mtime
    sources = sorted((p for p in SRC.iterdir() if p.suffix.lower() in VIDEO_EXT), key=lambda p: p.name.lower())
    print(f"{len(sources)} filmer i filmer-original/")

    built, used, warnings = [], set(), []
    for src in sources:
        name = slug(src.stem)
        if name in used:
            name = f"{name}-{len(used)}"
        mp4, poster = OUT / f"{name}.mp4", OUT / f"{name}.jpg"
        # Gör om filmen om den saknas, om originalet ändrats eller om skriptet ändrats sedan sist
        if not mp4.exists() or mp4.stat().st_mtime < max(src.stat().st_mtime, script_time):
            print(f"  komprimerar {src.name} … (kan ta en stund)")
            try:
                encode(ffmpeg, src, mp4, poster)
            except RuntimeError as e:
                warnings.append(f"{src.name}: kunde inte komprimeras ({e})")
                continue
        mb = mp4.stat().st_size / 1_000_000
        if mb > WARN_MB:
            warnings.append(f"{src.name} blev {mb:.0f} MB – korta filmen, den spelas automatiskt och ska vara lätt")
        w, h = size_of(ffmpeg, mp4)
        used.add(name)
        built.append((name, caption_from(src.stem), w, h))
        print(f"  {name}.mp4  {w}x{h}  {mb:.1f} MB")

    # Filmerna blandas in jämnt mellan bilderna som bilder.py lagt i galleriet
    photos = [i for i in galleri_lib.read_items("inspiration.html") if not galleri_lib.is_video(i)]
    galleri_lib.write_items("inspiration.html", galleri_lib.mix(photos, [gallery_item(*b) for b in built]))
    write_block("index.html", hero_item(built[0][0], built[0][2], built[0][3]) if built else "")
    print(f"inspiration.html: {len(built)} filmer inblandade bland bilderna")
    print(f"index.html: {'filmen ' + built[0][0] if built else 'platshållare'} överst")

    for f in OUT.iterdir():
        if f.is_file() and f.stem not in used:
            f.unlink()
            print(f"  tog bort {f.name}")

    for w in warnings:
        print("VARNING:", w)


if __name__ == "__main__":
    main()
