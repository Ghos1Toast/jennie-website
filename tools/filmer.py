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
   Svart i början eller slutet av filmen klipps bort, så att den inte blir svart
   innan den börjar om.
2. Tar en stillbild ur filmen som visas innan filmen startar.
3. Blandar in filmerna jämnt mellan bilderna i galleriet på inspiration.html,
   sorterade efter filnamn. Den första filmen visas också stort överst på startsidan.
   Filnamnet blir bildtext:
       "1 Kök, Nacka.mov"          ->  "Kök, Nacka"  (siffran styr bara ordningen)
       "Kök_Nacka_1080x1920.mov"   ->  "Kök Nacka"
   Kulören under bildtexten står i filmer.csv (fil;farg;hex). Nya filmer läggs
   till där automatiskt – fyll bara i farg (och hex för färgrutan).
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
CSV_PATH = ROOT / "filmer.csv"
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


def black_trim(ffmpeg, src):
    """Hittar svart i början och slutet av filmen. Returnerar (start, längd) i sekunder,
    eller (0, None) om inget behöver klippas."""
    r = run(ffmpeg, ["-i", str(src), "-an", "-vf", "blackdetect=d=0.2:pix_th=0.08", "-f", "null", "-"])
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        return 0, None
    duration = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    start, end = 0.0, duration
    for b_start, b_end in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr):
        b_start, b_end = float(b_start), float(b_end)
        if b_start < 0.1:
            start = max(start, b_end)
        if b_end > duration - 0.15:
            end = min(end, b_start)
    if end - start < 1:  # nästan helt svart – låt filmen vara som den är
        return 0, None
    if start == 0 and end == duration:
        return 0, None
    return start, end - start


def encode(ffmpeg, src, mp4, poster):
    scale = f"scale='if(gt(iw,ih),min({MAX_SIDE},iw),-2)':'if(gt(iw,ih),-2,min({MAX_SIDE},ih))'"
    start, length = black_trim(ffmpeg, src)
    trim = ["-ss", f"{start:.3f}", "-t", f"{length:.3f}"] if length else []
    if length:
        print(f"    klipper bort svart: använder {start:.1f}–{start + length:.1f} s")
    r = run(ffmpeg, ["-y", "-i", str(src), *trim,
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


def read_colors(sources):
    """Läser filmer.csv (fil;farg;hex) och lägger till rader för nya filmer, så att
    det bara är att fylla i kulören. Returnerar {filnamn: (farg, hex)}."""
    rows = galleri_lib.read_csv(CSV_PATH) if CSV_PATH.exists() else []
    colors, warnings = {}, []
    for row in rows:
        hexcode = galleri_lib.valid_hex(row.get("hex"))
        if hexcode is None:
            warnings.append(f"filmer.csv rad {row['rad']}: hex '{row['hex']}' ska vara sex tecken, t.ex. C9A227")
            hexcode = ""
        colors[row.get("fil", "").lower()] = (row.get("farg", "") or row.get("färg", ""), hexcode)
    new = [s.name for s in sources if s.name.lower() not in colors]
    if new:
        text = CSV_PATH.read_text(encoding="utf-8-sig") if CSV_PATH.exists() else "fil;farg;hex\n"
        text = text if text.endswith("\n") else text + "\n"
        CSV_PATH.write_text(text + "".join(f"{n};;\n" for n in new), encoding="utf-8", newline="\n")
        print(f"  la till {len(new)} filmer i filmer.csv – fyll i kulören där")
    return colors, warnings


def gallery_item(name, caption, w, h, color="", hexcode=""):
    full = f"{caption}. {color}" if caption and color else (caption or color)
    cap = html.escape(full, quote=True)
    video = "\n".join("    " + line for line in video_tag(name, w, h, "autoplay-video", "none").split("\n"))
    return (f'<li class="gallery-item gallery-item--video">\n'
            f'  <a class="gallery-link" href="videos/{name}.mp4" data-video="videos/{name}.mp4" data-caption="{cap}">\n'
            f'{video}\n'
            f'    <span class="visually-hidden">Film: {cap or "utan bildtext"}</span>\n'
            f'  </a>\n'
            f'  {TOGGLE}\n'
            f'  {galleri_lib.caption_html(caption, color, hexcode)}\n'
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

    colors, warnings = read_colors(sources)
    built, used = [], set()
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
        built.append((name, caption_from(src.stem), w, h, *colors.get(src.name.lower(), ("", ""))))
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
