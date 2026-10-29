"""Skriver in kontaktuppgifterna från uppgifter.txt på alla sidor.

Användning (från projektmappen):

    python tools/uppgifter.py

I HTML:en markeras var uppgifterna ska stå:
  - text:  <!--uppgift:telefon-->0735 019 247<!--/uppgift-->
  - länk:  <a href="tel:+46735019247" data-uppgift="telefon">
Skriptet byter allt mellan markeringarna och alla href med data-uppgift.
Tomt värde i uppgifter.txt = gul platshållare på sidan.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "uppgifter.txt"

PLACEHOLDER = {
    "telefon": "[SAKNAS: telefonnummer]",
    "epost": "[SAKNAS: e-post]",
    "foretagsnamn": "[SAKNAS: registrerat företagsnamn]",
    "orgnr": "[SAKNAS: org.nr]",
}

TEXT_RE = re.compile(r"<!--uppgift:(\w+)-->.*?<!--/uppgift-->")
HREF_RE = re.compile(r'href="[^"]*"(\s+data-uppgift="(\w+)")')


def read_values():
    values = {}
    for n, line in enumerate(FILE.read_text(encoding="utf-8-sig").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            sys.exit(f"uppgifter.txt rad {n}: saknar '=' ({line})")
        key, value = (s.strip() for s in line.split("=", 1))
        if key not in PLACEHOLDER:
            sys.exit(f"uppgifter.txt rad {n}: okänt namn '{key}'. Giltiga: {', '.join(PLACEHOLDER)}")
        values[key] = value
    return values


def tel_href(number):
    digits = re.sub(r"[^\d+]", "", number)
    if digits.startswith("00"):
        digits = "+" + digits[2:]
    elif digits.startswith("0"):
        digits = "+46" + digits[1:]  # svenskt nummer -> internationellt format, fungerar även från utlandet
    return "tel:" + digits


def href_for(key, value):
    if not value:
        return {"telefon": "tel:", "epost": "mailto:"}.get(key, "#")
    if key == "telefon":
        return tel_href(value)
    if key == "epost":
        return "mailto:" + value
    return "#"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    values = read_values()

    def text(m):
        key = m.group(1)
        if key not in PLACEHOLDER:
            sys.exit(f"Okänd markering <!--uppgift:{key}-->")
        value = values.get(key, "")
        body = html.escape(value) if value else f'<span class="ph">{html.escape(PLACEHOLDER[key])}</span>'
        return f"<!--uppgift:{key}-->{body}<!--/uppgift-->"

    def href(m):
        return f'href="{html.escape(href_for(m.group(2), values.get(m.group(2), "")))}"{m.group(1)}'

    for page in sorted(ROOT.glob("*.html")):
        s = page.read_text(encoding="utf-8")
        new = HREF_RE.sub(href, TEXT_RE.sub(text, s))
        count = len(TEXT_RE.findall(s)) + len(HREF_RE.findall(s))
        if new != s:
            page.write_text(new, encoding="utf-8", newline="\n")
        print(f"{page.name}: {count} ställen")

    for key in PLACEHOLDER:
        if not values.get(key):
            print(f"OBS: {key} är tomt i uppgifter.txt – sidan visar en platshållare")


if __name__ == "__main__":
    main()
