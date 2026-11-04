"""Kollar att paletten i css/tokens.css går att läsa (WCAG 2.1 AA).

Användning (från projektmappen):

    python tools/kontrast.py

Läser de sex --palette-färgerna, räknar ut de färger som blandas fram ur dem
(samma blandning som i tokens.css) och skriver ut kontrasten för alla par
text/bakgrund som finns på sajten. Under gränsen = svårläst, välj en annan färg.
"""
import re
import sys
from pathlib import Path

TOKENS = Path(__file__).resolve().parent.parent / "css" / "tokens.css"


def read_palette():
    s = TOKENS.read_text(encoding="utf-8")
    block = s[s.index(":root"):s.index("}")]  # första :root-blocket = paletten
    pal = dict(re.findall(r"--palette-(\w+):\s*(#[0-9a-fA-F]{6})", block))
    missing = {"bg", "surface", "text", "brand", "accent", "chip"} - pal.keys()
    if missing:
        sys.exit(f"Hittar inte --palette-{', --palette-'.join(sorted(missing))} i tokens.css (skriv dem som #RRGGBB)")
    return {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) for k, v in pal.items()}


def mix(a, b, share_a):
    """Som color-mix(in srgb, a share_a%, b)."""
    return tuple(round(x * share_a + y * (1 - share_a)) for x, y in zip(a, b))


def luminance(rgb):
    c = [v / 255 for v in rgb]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = read_palette()
    c = {
        "bakgrund (bg)": p["bg"], "yta (surface)": p["surface"], "text": p["text"],
        "grön (brand)": p["brand"], "vitt kort (chip)": p["chip"],
        "grå text": mix(p["text"], p["bg"], 0.74),
        "mörkgrön": mix(p["brand"], p["text"], 0.60),
        "ljus text på grönt": mix(p["chip"], p["brand"], 0.78),
        "platta 1": mix(p["brand"], p["bg"], 0.22),
        "platta 2 / ockra kort": mix(p["accent"], p["bg"], 0.34),
        "platta 3": mix(p["surface"], p["chip"], 0.70),
        "platta 4": mix(p["brand"], p["chip"], 0.10),
        "formulärkant": mix(p["text"], p["bg"], 0.55),
    }
    # (förgrund, bakgrund, gräns, var på sajten) – utkast D: ljus sajt, mörk text, grön footer
    checks = []
    for bg, where in (("bakgrund (bg)", "vanliga sektioner"), ("yta (surface)", "varannan sektion"),
                      ("vitt kort (chip)", "kort och etiketter")):
        checks += [
            ("text", bg, 4.5, f"brödtext och rubriker – {where}"),
            ("grå text", bg, 4.5, f"sekundär text – {where}"),
            ("grön (brand)", bg, 4.5, f"länkar och etiketter – {where}"),
        ]
    for tile in ("platta 1", "platta 2 / ockra kort", "platta 3", "platta 4"):
        checks.append(("text", tile, 4.5, f"text på tjänsteplattan – {tile}"))
    checks += [
        ("vitt kort (chip)", "grön (brand)", 4.5, "text på knappar och det gröna kortet"),
        ("ljus text på grönt", "grön (brand)", 4.5, "sekundär text på det gröna kortet"),
        ("vitt kort (chip)", "mörkgrön", 4.5, "text i footern, knappar när man pekar"),
        ("ljus text på grönt", "mörkgrön", 4.5, "sekundär text i footern"),
        ("formulärkant", "vitt kort (chip)", 3.0, "kant runt formulärfält"),
    ]
    fails = 0
    for fg, bg, need, where in checks:
        r = ratio(c[fg], c[bg])
        ok = r >= need
        fails += not ok
        print(f"{'OK  ' if ok else 'FÖR LÅG'} {r:5.2f} (minst {need})  {fg} på {bg} – {where}")
    print()
    print("Allt går att läsa." if not fails else f"{fails} par har för låg kontrast – justera paletten.")


if __name__ == "__main__":
    main()
