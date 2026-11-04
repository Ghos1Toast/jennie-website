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
    missing = {"paper", "ink", "brand", "ochre", "sage", "clay"} - pal.keys()
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
    white = (255, 255, 255)
    c = {
        "papper (paper)": p["paper"], "text (ink)": p["ink"], "grön (brand)": p["brand"],
        "ockra (ochre)": p["ochre"], "salvia (sage)": p["sage"], "terrakotta (clay)": p["clay"],
        "grå text": mix(p["ink"], p["paper"], 0.74),
        "mörkgrön": mix(p["brand"], p["ink"], 0.70),
        "ljus salvia": mix(p["sage"], p["paper"], 0.35),
        "ljus ockra": mix(p["ochre"], p["paper"], 0.18),
        "ljusgrå text på mörkt": mix(p["paper"], p["ink"], 0.70),
        "formulärkant": mix(p["ink"], p["paper"], 0.50),
        "vit ram": (255, 255, 255),
    }
    # (förgrund, bakgrund, gräns, var på sajten) – utkast F: ljus sajt, mörk text på kulörer
    checks = []
    for bg, where in (("papper (paper)", "sidorna"), ("vit ram", "kort och ramar"),
                      ("ljus ockra", "varannan sektion"), ("ljus salvia", "för dig som")):
        checks += [
            ("text (ink)", bg, 4.5, f"text och rubriker – {where}"),
            ("grå text", bg, 4.5, f"sekundär text – {where}"),
            ("grön (brand)", bg, 4.5, f"länkar – {where}"),
        ]
    checks += [
        ("text (ink)", "ockra (ochre)", 4.5, "text på ockra panel och kontaktbandet"),
        ("text (ink)", "salvia (sage)", 4.5, "text på salviapanelen"),
        ("text (ink)", "terrakotta (clay)", 4.5, "text på terrakotta (om den används)"),
        ("papper (paper)", "text (ink)", 4.5, "text på mörkbruna knappar i kontaktbandet"),
        ("papper (paper)", "grön (brand)", 4.5, "text på gröna knappar"),
        ("papper (paper)", "mörkgrön", 4.5, "knapptext när man pekar"),
        ("papper (paper)", "text (ink)", 4.5, "text i footern"),
        ("ljusgrå text på mörkt", "text (ink)", 4.5, "sekundär text i footern"),
        ("formulärkant", "vit ram", 3.0, "kant runt formulärfält"),
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
