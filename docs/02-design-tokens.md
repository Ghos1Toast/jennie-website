# Fas 2 – Design tokens

Status: utkast. Tokens finns i `css/tokens.css`. De är ännu inte kopplade till
`index.html` (det görs i fas 3).

## Färg

### Uppmätt ur loggan

Värdena är avlästa pixel för pixel ur `Jennie_Logga.png` (versionen utan
kontaktuppgifter, 640×567). Jag har räknat de vanligaste helt opaka färgerna.

| Token | Hex | Var i loggan | Antal pixlar |
|---|---|---|---|
| `--color-teal` | `#366865` | bakgrund | 155 342 |
| `--color-cream` | `#F8E0C4` | text "Jennies" + undertext (y 190–362) | 18 974 |
| `--color-cream-frame` | `#F6E5C9` | ramen (y 18–548) | 11 879 |

Förbehåll: PNG:n kan vara en export från en vektorfil med andra värden (t.ex. CMYK
för tryck). **Fråga vem som gjorde loggan och be om originalfilen + färgkoder.**
Om tryckeriet har en NCS- eller Pantone-kod ska sajten följa den.

Det nuvarande utkastets `#2D5A4A`, `#1F3F33` och `#F6EEDF` stämmer inte med loggan.
De ersätts.

### Härledda (mitt förslag)

| Token | Hex | Användning |
|---|---|---|
| `--color-teal-deep` | `#1F3F3C` | rubriker, footer, primärknapp |
| `--color-paper` | `#FBF6EE` | sidbakgrund. Ljusare än loggans cream så att foton inte ser gulstickiga ut |
| `--color-paper-deep` | `#F3EADB` | alternerande sektioner |
| `--color-ink` | `#23211E` | brödtext (varm nästan-svart) |
| `--color-ink-muted` | `#5A554D` | sekundär text |
| `--color-border` | `#8C8478` | ramar på formulärfält |
| `--color-accent` | `#A35233` | **valfri** terrakotta. Används bara i små detaljer |

Om accentfärgen: den finns inte i loggan. Ett argument för den är att en sajt för en
färgsättare som bara är teal och beige kan kännas platt. Ett argument mot är att
fotona ska bära färgen och att varje extra kulör konkurrerar med dem. Jag lutar åt att
**börja utan** accent och lägga till den bara om sidorna känns livlösa med riktiga
bilder. Det är Jennies beslut, och hon har sannolikt en starkare åsikt om färg än vi.

### Kontrast (WCAG 2.1, uträknat)

| Förgrund | Bakgrund | Kvot | AA normal text (4,5) | AA stor text / UI (3,0) |
|---|---|---|---|---|
| ink `#23211E` | paper | 14,93 | ✅ | ✅ |
| ink-muted `#5A554D` | paper | 6,87 | ✅ | ✅ |
| ink-muted | paper-deep | 6,20 | ✅ | ✅ |
| teal-deep `#1F3F3C` | paper | 10,64 | ✅ | ✅ |
| teal `#366865` | paper | 5,87 | ✅ | ✅ |
| teal | paper-deep | 5,29 | ✅ | ✅ |
| paper | teal-deep | 10,64 | ✅ | ✅ |
| cream `#F8E0C4` | teal | 4,95 | ✅ (knappt) | ✅ |
| accent `#A35233` | paper | 5,12 | ✅ | ✅ |
| accent | paper-deep | 4,62 | ✅ (knappt) | ✅ |
| border `#8C8478` | paper | 3,43 | – | ✅ |
| *utkastets rost* `#B5562C` | `#F6EEDF` | 4,20 | ❌ | ✅ |
| *utkastets platshållare* `#8a8479` | `#EDE1CB` | 2,87 | ❌ | ❌ |

Formel: WCAG 2.1 relativ luminans, (L1 + 0,05) / (L2 + 0,05).

## Typografi

**Typsnitten i loggan är okända.** Skriptet "Jennies" och de smala versalerna liknar
kända Google Fonts, men det är gissningar och jag använder dem inte. Be om
typsnittsnamnen från den som gjorde loggan.

Förslag tills vidare (behålls från utkastet, det fungerar):

- **Rubriker: Fraunces** (serif med mjuk karaktär, SIL OFL-licens). Varm och
  "hantverksmässig" utan att bli rustik. Den krockar inte med loggans skript.
- **Brödtext: Work Sans** (OFL). Bred, läsbar på mobil, har å/ä/ö.
- **Skript används inte i webbtext.** Det finns bara i loggan. Två skriptstilar på
  samma sida ser billigt ut.
- **Självhosta** typsnitten (woff2 i `/fonts`, `font-display: swap`, bara de vikter
  som används: Fraunces 500/600, Work Sans 400/500/600). Då skickas inga
  IP-adresser till Google och ingen tredjepart behöver nämnas i integritetspolicyn.

Skala: se `--text-*` i `tokens.css`. Brödtext 17 px på mobil (inte 15–16), eftersom
målgruppen sannolikt är villaägare i alla åldrar. Radlängd max 62 tecken.

## Avstånd, rutnät och form

- 4 px-bas (`--space-1` … `--space-9`). Sektionsavstånd skalar med `clamp()`.
- Container max 72 rem (1152 px) med flytande sidomarginal.
- Hörnradie 2 px. Nästan rakt ger ett lugnare och mer arkitektoniskt intryck. Runda
  "app-knappar" drar åt mallhållet.
- Klickytor minst 44 × 44 px.
- Fokusmarkering: 2 px solid `--color-focus` med 2 px offset på allt interaktivt.
  Den får aldrig tas bort med `outline: none`.

## Bilder (kort, detaljer i fas 3)

- Galleribilder: AVIF + WebP + JPEG-fallback via `<picture>`, bredder 480/960/1600.
  `loading="lazy"` på allt utom första bilden ovanför vecket.
  Ange `width`/`height` så att sidan inte hoppar (CLS).
- `Profilbild.jpeg` (612 kB, 1546×1986) ska ner till cirka 60–120 kB per storlek.
- Ingen bildöverlagring med text över projektfoton. Fotona ska synas som de är.
