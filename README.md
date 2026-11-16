# Jennies Färgsättning & Måleri – hemsida

Statisk sajt (HTML, CSS, vanilla JS). Inget byggsteg. Öppna `index.html` i webbläsaren, eller använd Live Server i VS Code.

## Struktur

| Sökväg | Innehåll |
|---|---|
| `index.html`, `inspiration.html`, `om-oss.html`, `kontakt.html`, `integritetspolicy.html` | Sidorna. Header och footer är kopierade i varje fil – ändra på alla ställen (utom kontaktuppgifterna, se nedan). |
| `css/tokens.css` | Färger, typsnitt, avstånd. **Paletten** står överst. Ändrar du en färg: kör `python tools/kontrast.py` för att se att texten går att läsa. |
| `css/main.css` | All övrig stil, mobil först |
| `js/main.js` | Mobilmeny, galleri-ljusbox, filmer, formulärsändning |
| `fonts/` | Självhostade typsnitt (Young Serif, Barlow, Barlow Condensed – SIL OFL) |
| `images/brand/`, `images/om/` | Logga, favicon, porträtt i AVIF/WebP/JPEG |

## Innehåll som byggs med skript

Delarna mellan `<!-- …:START -->` och `<!-- …:SLUT -->` i HTML-filerna skrivs av skripten i `tools/`. Ändra inte dem för hand – ändra i filen till vänster och kör skriptet.

| Ändra här | Kör | Vad som uppdateras |
|---|---|---|
| `galleri.csv` + bilder i `bilder-original/` | `python tools/bilder.py` | Galleriet på Inspiration och urvalet på startsidan |
| filmer i `filmer-original/`, kulörer i `filmer.csv` | `python tools/filmer.py` | Filmerna i galleriet och filmen överst på startsidan |
| `instagram.csv` (bilder ur `bilder-original/`) | `python tools/instagram.py` | Instagram-rutan på startsidan |
| `partner.csv` + loggor i `partner-original/` | `python tools/partner.py` | Samarbetspartner på startsidan och Om oss |
| `uppgifter.txt` | `python tools/uppgifter.py` | Telefon, e-post, Instagram, företagsnamn och org.nr på alla sidor |

Mer om varje del står i `LÄSMIG.txt` i mapparna `bilder-original/`, `filmer-original/` och `partner-original/`. Originalen i de mapparna laddas inte upp (GPS-position i bilderna) – bara webbversionerna i `images/` och `videos/`.

Skripten kräver Python med Pillow (`python -m pip install pillow pillow-heif`) och, för filmer, ffmpeg (`python -m pip install imageio-ffmpeg`).

## Före lansering

- Gul markering med `[SAKNAS: …]`, `[FRÅGA: …]` eller `[PLATSHÅLLARE: …]` = text som Jennie måste leverera eller bekräfta. Inget av det får finnas kvar.
- Sidorna har `noindex` – ta bort raden i varje sidas `<head>`.
- Integritetspolicyn är ett utkast och inte juridiskt granskad. Formulärtjänsten (nu Formspree) är inte bestämd.

Texterna kommer från Jennies textdokument (2026-10-26).
Inga cookies och ingen kod från andra tjänster: typsnitt, bilder och filmer ligger på sajten själv.
