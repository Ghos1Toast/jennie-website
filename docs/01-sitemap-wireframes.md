# Fas 1 – Sitemap, wireframes och granskning av nuvarande utkast

Status: utkast för diskussion. Inget här är godkänt av Jennie.

## 1. Granskning av nuvarande `index.html`

Utkastet i repot är en bra start rent tekniskt (statisk HTML, `lang="sv"`, labels i
formuläret), men det **får inte publiceras i nuvarande skick**. Problemen i
prioritetsordning:

| # | Problem | Var | Varför det är ett problem |
|---|---------|-----|---------------------------|
| 1 | Påhittade sakuppgifter: "lång erfarenhet", "linoljefärg", "Osmo är ett av våra specialområden", "tapetsering", "kunniga målare", "följer branschens riktlinjer" | Om oss | Inget av detta finns i Jennies svar. Kan vara sant, men är obekräftat. Felaktiga påståenden i marknadsföring strider mot marknadsföringslagen (2008:486). |
| 2 | Fel kontaktuppgifter: `info@jennies-maleri.se`, `070-000 00 00` | Kontakt | Loggan anger `info@jenniesfargsattning.se`, `0735 019 247`. |
| 3 | "AB" i title och footer | `<title>`, footer | Bolagsform och registrerat namn är obekräftade. Står det AB och det är en enskild firma blir det fel. |
| 4 | "Stockholm med omnejd" | Kontakt | Obekräftat. ChatGPT-förslaget säger "Värmdö, Nacka och Stockholmsområdet" – också obekräftat. |
| 5 | "Vi"-form genom hela texten | Överallt | Vi vet inte om Jennie har anställda. |
| 6 | Tomma fraser: "hög finish", "kvalitet, estetik och hållbarhet", "kunden i centrum" | Hero, Om oss, footer | Säger inget som skiljer henne från Tamsi Måleri eller någon annan. |
| 7 | Formuläret saknar länk till integritetspolicy och honeypot | Kontakt | GDPR art. 13 kräver information vid insamlingen. Utan spamskydd fylls inkorgen. |
| 8 | Formspree-endpoint `mgobnqen` ligger redan i koden | Kontakt | Vems konto? Formspree är ett amerikanskt bolag → tredjelandsöverföring som måste stå i integritetspolicyn. Tas upp i fas 4. |
| 9 | Google Fonts laddas från Googles CDN | `<head>` | Besökarens IP skickas till Google. LG München I (3 O 17493/20, 2022-01-20) bedömde detta som GDPR-brott. Lösning: ladda ner och självhosta typsnitten. |
| 10 | Kontrastfel | CSS | Rost `#B5562C` på cream = 4,2:1 (kräver 4,5:1 för 13px eyebrow-text). Platshållartext `#8a8479` på `#EDE1CB` = 2,87:1. Inputramar `rgba(…,0.12)` når inte 3:1 (WCAG 1.4.11). |
| 11 | Mobilmenyn: `onclick` utan `aria-expanded`/`aria-controls`, ikon "☰" utan synlig fokusstil | Header | Skärmläsare vet inte om menyn är öppen. |
| 12 | Allt på en sida med `#ankare` | Struktur | Scope är fyra sidor. En sida ger bara en `<title>`/meta description → sämre lokal SEO, och galleriet blir tungt på startsidan. |
| 13 | Färgerna i CSS (`#2D5A4A`, `#1F3F33`, `#F6EEDF`) är gissade | `:root` | Loggans faktiska värden är `#366865` och `#F8E0C4` (uppmätta, se fas 2). |
| 14 | `Profilbild.jpeg` är 1546×1986 px, 612 kB, ingen WebP/srcset | Hero | Onödigt tung på mobil. |
| 15 | Kommentaren `<!-- test test test test -->` och dubblerade media queries | HTML/CSS | Städas i fas 3. |

**Rekommendation:** Om GitHub Pages redan är påslaget för `main` ligger påhittade
uppgifter och fel telefonnummer publikt just nu. Kontrollera under
*Settings → Pages* och stäng av tills fas 3 är klar.

## 2. Sitemap

```
/                       Startsida
├── /om-oss.html        Om Jennie / Om oss  (rubrik beror på svar om anställda)
├── /inspiration.html   Galleri – kärnan i sajten
├── /kontakt.html       Formulär + kontaktuppgifter
├── /integritetspolicy.html   (krav, länkas från formulär + footer)
└── /404.html           (GitHub Pages och de flesta webbhotell stödjer detta)
```

Medvetet **inte** med:

- **Tjänstesida / paket** (Färgkoll, Färg & Måleri, Helhetslyft). Inte i scope, och
  paketen är inte bekräftade. Kan läggas till senare utan att strukturen ändras.
- **Separata projektsidor per uppdrag.** Det skulle vara bra för SEO, men kräver text
  per projekt som Jennie inte har skrivit. Galleriet byggs så att det går att lägga
  till senare.
- **Blogg, offertkalkylator, bokning.** Utanför scope.

Varför flera sidor och inte en lång sida: egna `<title>` och meta description per
sida, en lätt startsida, och ett galleri som kan växa utan att startsidan blir tyngre.

## 3. Globala delar

**Header (mobil):**
```
┌─────────────────────────────────────┐
│ [Logga 48px]   [0735 019 247]  [☰]  │  ← telefonnumret är en tel:-länk
└─────────────────────────────────────┘
  Meny öppen:
  Startsida / Om oss / Inspiration / Kontakt
  [ Skicka en förfrågan ]  ← primär knapp
```
**Header (≥ 900px):** logga vänster · meny mitten/höger · telefon + knappen
"Skicka en förfrågan".

Problem med loggan: badgen är hexagonal (640×567). I 48 px höjd blir texten
"FÄRGSÄTTNING & MÅLERI" ca 5 px hög och oläslig. Två alternativ:
1. Använd badgen liten och skriv företagsnamnet bredvid i HTML-text.
2. Be om en liggande variant av loggan (bara "Jennies" + rad under). Det är bättre, men
   är ett designjobb som Jennie själv måste beställa eller godkänna.

**Footer:**
```
Logga
Jennies Färgsättning & Måleri [PLATSHÅLLARE: registrerat namn]
Org.nr [PLATSHÅLLARE]  ·  [F-skatt: endast om bekräftat]
info@jenniesfargsattning.se · 0735 019 247
[PLATSHÅLLARE: verksamhetsområde]
Instagram · Facebook  [PLATSHÅLLARE: vilka konton finns?]
Integritetspolicy
```

## 4. Wireframes per sida (mobil först)

### Startsida `/`
```
┌─────────────────────────────┐
│ HERO: helbreddsbild av ett  │  ← bästa projektbilden, inte profilbilden
│ färdigt projekt             │
│                             │
│ H1: [PLATSHÅLLARE: rubrik]  │  förslag "Måleri med känsla för färg" – kräver
│ 1 mening om vad hon gör     │  godkännande + krockar nästan med Tamsi Måleris
│ och var                     │  tagline, se öppna frågor
│ [Skicka en förfrågan]       │
│ [Se tidigare projekt →]     │
├─────────────────────────────┤
│ TVÅ TJÄNSTER (2 kort)       │
│ Färgsättning – 2 meningar   │  ← det som skiljer henne från andra målare
│ Måleri inne/ute – 2 meningar│
├─────────────────────────────┤
│ URVAL UR GALLERIET          │
│ 4–6 bilder, 2 kolumner      │
│ [Se alla projekt →]         │
├─────────────────────────────┤
│ KORT OM JENNIE              │
│ Porträtt + 2–3 meningar     │
│ [Läs mer om mig/oss →]      │
├─────────────────────────────┤
│ CTA-band                    │
│ "Berätta om ditt projekt"   │
│ [Skicka en förfrågan] [Ring]│
└─────────────────────────────┘
```
Medvetet utelämnat: kundomdömen (finns inga bekräftade), "4 skäl att välja oss"-kort
(utfyllnad utan sakinnehåll), siffror ("X år", "Y projekt").

### Om oss `/om-oss.html`
```
H1: [Om Jennie / Om oss]
Porträtt (Profilbild, beskuren och komprimerad)
Text: [PLATSHÅLLARE: Jennies bakgrund – utbildning, hur länge hon målat,
       varför färgsättning. Måste skrivas av eller med Jennie.]
Så går ett uppdrag till: 3–4 steg   ← bara om Jennie beskriver sin faktiska process
  1. Kontakt  2. Besök/färgsättning  3. Offert  4. Utförande
Verksamhetsområde: [PLATSHÅLLARE]
[Skicka en förfrågan]
```

### Inspiration `/inspiration.html` – kärnan
```
H1: Inspiration
1 mening intro
Filter (endast om ≥ 15 bilder):  Alla | Inomhus | Utomhus
┌──────┬──────┐
│ bild │ bild │   2 kolumner mobil, 3 på surfplatta, 4 på desktop
├──────┼──────┤   Varje bild: <figure> + kort bildtext
│ bild │ bild │   ("Vardagsrum, Värmdö – kulör [NCS-kod]" om Jennie vill)
└──────┴──────┘
Klick → helskärmsvisning (native <dialog>, pilar + Esc + tangentbord)
Avslut: "Gillar du det du ser?" [Skicka en förfrågan]
```
Kulörnamn/NCS-koder i bildtexterna är det enklaste sättet att visa
färgsättningskompetens konkret. Kräver att Jennie har koderna.

Inga bilder visas utan att Jennie bekräftat att kunden godkänt publicering
(särskilt om adress, hus eller personer går att känna igen).

### Kontakt `/kontakt.html`
```
H1: Kontakt
Ring 0735 019 247  ·  info@jenniesfargsattning.se
Formulär:
  Namn*            E-post*
  Telefon*         Adress (där jobbet ska göras)
  Meddelande*
  [honeypot, dold]
  "Vi använder uppgifterna bara för att svara på din förfrågan.
   Läs vår integritetspolicy."  ← länk
  [Skicka förfrågan]
  Status-meddelande (aria-live)
Verksamhetsområde, sociala medier
```
Inget kryssruta-samtycke: den rättsliga grunden är troligen avtal/åtgärd före avtal
(art. 6.1 b), inte samtycke. Det bekräftas i fas 4.

## 5. Inspirationssajterna

Endast Tamsi Måleri (måleristockholm.nu) är analyserad. Wolfbuilder, elektroshields-4
och demo-lks-1 är inte analyserade. HTML-filerna som bifogades ligger på Max dator
(`C:\Users\maxni\Downloads\…`) och har inte laddats upp hit, så jag har inte kunnat
läsa dem. Två av dem är JS-renderade demos – en sparad HTML-fil visar troligen inte
heller deras innehåll. **Skärmdumpar behövs**, och framför allt Jennies svar på
*vad* hon gillar med varje sajt.
