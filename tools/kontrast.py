"""Kollar att paletten i css/tokens.css går att läsa (WCAG 2.1 AA).

Användning (från projektmappen):

    python tools/kontrast.py

Läser --palette-färgerna, räknar ut de färger som blandas fram ur dem
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
    missing = {"dark", "brand", "light", "tint", "paper", "ink", "ochre", "sage", "clay"} - pal.keys()
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
        "mörkgrön": p["dark"], "grön": p["brand"], "beige": p["light"],
        "ljus beige": p["tint"], "bakgrund": p["paper"], "text": p["ink"],
        "grå text": mix(p["ink"], p["paper"], 0.75),
        "grå text på mörkgrönt": mix(p["paper"], p["brand"], 0.75),
        "formulärkant": mix(p["ink"], p["paper"], 0.55),
        "ljus salvia": mix(p["sage"], p["paper"], 0.35),
        "vit": (255, 255, 255),
    }
    # (förgrund, bakgrund, gräns, var på sajten)
    checks = [
        ("text", "bakgrund", 4.5, "brödtext"),
        ("text", "ljus beige", 4.5, "brödtext i beige sektioner"),
        ("grå text", "bakgrund", 4.5, "sekundär text"),
        ("grå text", "ljus beige", 4.5, "sekundär text i beige sektioner"),
        ("grå text", "ljus salvia", 4.5, "text i \"för dig som\""),
        ("grå text", "vit", 4.5, "kulören på bildkorten"),
        ("mörkgrön", "bakgrund", 4.5, "rubriker"),
        ("mörkgrön", "ljus beige", 4.5, "rubriker i beige sektioner"),
        ("mörkgrön", "ljus salvia", 4.5, "rubrik i \"för dig som\""),
        ("beige", "grön", 4.5, "text i kontaktbandet längst ner"),
        ("grön", "bakgrund", 4.5, "länkar, små etiketter"),
        ("grön", "ljus beige", 4.5, "länkar i beige sektioner"),
        ("beige", "mörkgrön", 4.5, "text i header, hero och footer"),
        ("grå text på mörkgrönt", "mörkgrön", 4.5, "sekundär text i header, hero och footer"),
        ("vit", "grön", 4.5, "knapptext när man pekar på en knapp"),
        ("formulärkant", "bakgrund", 3.0, "kant runt formulärfält"),
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
