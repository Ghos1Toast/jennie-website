# Jennies Färgsättning & Måleri – hemsida (UTKAST D "Kulörkarta")

Fjärde visuella riktningen, byggd på utkast B (branch `claude/jennies-draft-b`) med samma innehåll, verktyg och platshållare. Stil: mjukt, vänligt och professionellt – varm ljus bakgrund, mjukt rundade hörn, filmen i en stor rundad ruta med rubriken på ett kort bredvid, tjänsterna som färgprovsplattor i dämpade toner, collage på startsidan och mosaik på Inspiration (Figtree).

Statisk sajt (HTML, CSS, vanilla JS). Inget byggsteg. Öppna `index.html` i webbläsaren.

## Struktur

| Sökväg | Innehåll |
|---|---|
| `index.html`, `inspiration.html`, `kontakt.html`, `integritetspolicy.html` | Sidorna. Header och footer är kopierade i varje fil – ändra på alla ställen (utom kontaktuppgifterna, se nedan). |
| `css/tokens.css` | Färger, typsnitt, avstånd. **Paletten** (sex färger: bg, surface, text, brand, accent, chip) står överst – byt dem för att prova en annan färgsättning, kör sedan `python tools/kontrast.py` för att se att texten går att läsa. |
| `css/main.css` | All övrig stil, mobil först |
| `js/main.js` | Mobilmeny, galleri-ljusbox, formulärsändning |
| `fonts/` | Självhostade typsnitt (Figtree, SIL OFL) |
| `images/brand/`, `images/om/` | Logga, favicon, porträtt i AVIF/WebP/JPEG |
| `bilder-original/` | Originalbilder till galleriet. Laddas inte upp (GPS i bilderna). Se `LÄSMIG.txt` där. |
| `filmer-original/` | Släpp filmer här och kör `python tools/filmer.py` – de komprimeras och läggs ut på Inspiration. Laddas inte upp. Se `LÄSMIG.txt` där. |
| `filmer.csv` | Kulören för varje film (fil;farg;hex). Nya filmer läggs till automatiskt av `tools/filmer.py`. |
| `galleri.csv` | En rad per galleribild: fil, bildtext, färg, hex, alt-text, startsida, fokus (se `bilder-original/LÄSMIG.txt`) |
| `tools/bilder.py` | Bygger galleriet: `python tools/bilder.py` |
| `partner-original/`, `partner.csv` | Loggor och namn för Samarbetspartner på startsidan. Kör `python tools/partner.py`. Se `LÄSMIG.txt` i mappen. |
| `uppgifter.txt` | Telefon, e-post, företagsnamn, org.nr. Ändra här och kör `python tools/uppgifter.py` – då uppdateras alla sidor. |

Gul markering med `[PLATSHÅLLARE: …]` = text som Jennie måste leverera eller bekräfta.
Inget av det får finnas kvar vid lansering.

Sidorna har `noindex` tills sajten lanseras.

Texterna kommer från Jennies textdokument (2026-10-26). `[SAKNAS: …]` och `[FRÅGA: …]` i gult är frågor till Jennie.
Filmer läggs ut med `tools/filmer.py` som egna MP4-filer i `videos/`, inte inbäddade från Instagram/YouTube (cookies).
