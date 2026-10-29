# Jennies Färgsättning & Måleri – hemsida (UTKAST B "Kulörkort")

Alternativ visuell riktning. Samma sidor och innehåll som utkast A (branch `claude/jennies-fargsattning-site-qwp5jv`), annan stil: mörk teal, kondenserade versaler (Barlow Condensed), raka kanter, galleribilder som kulörkort.

Statisk sajt (HTML, CSS, vanilla JS). Inget byggsteg. Öppna `index.html` i webbläsaren.

## Struktur

| Sökväg | Innehåll |
|---|---|
| `index.html`, `inspiration.html`, `kontakt.html`, `integritetspolicy.html` | Sidorna. Header och footer är kopierade i varje fil – ändra på alla ställen (utom kontaktuppgifterna, se nedan). |
| `css/tokens.css` | Färger, typsnitt, avstånd (fas 2) |
| `css/main.css` | All övrig stil, mobil först |
| `js/main.js` | Mobilmeny, galleri-ljusbox, formulärsändning |
| `fonts/` | Självhostade typsnitt (Barlow, Barlow Condensed, SIL OFL) |
| `images/brand/`, `images/om/` | Logga, favicon, porträtt i AVIF/WebP/JPEG |
| `bilder-original/` | Originalbilder till galleriet. Laddas inte upp (GPS i bilderna). Se `LÄSMIG.txt` där. |
| `galleri.csv` | En rad per galleribild: fil, bildtext, färg, alt-text, startsida |
| `tools/bilder.py` | Bygger galleriet: `python tools/bilder.py` |
| `uppgifter.txt` | Telefon, e-post, företagsnamn, org.nr. Ändra här och kör `python tools/uppgifter.py` – då uppdateras alla sidor. |

Gul markering med `[PLATSHÅLLARE: …]` = text som Jennie måste leverera eller bekräfta.
Inget av det får finnas kvar vid lansering.

Sidorna har `noindex` tills sajten lanseras.

Texterna kommer från Jennies textdokument (2026-10-26). `[SAKNAS: …]` och `[FRÅGA: …]` i gult är frågor till Jennie.
Filmer på Inspiration ska ligga som MP4 i `videos/`, inte bäddas in från Instagram/YouTube (cookies).
