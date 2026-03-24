# Lecke 13: Hibák, hallucinációk kezelése

**Egy mondatban:** Hallucináció ellen csak módszeres ellenőrzés működik.  
**Idő:** 20-30 perc  
**Kézzelfogható kimenet:** forrásellenőrzési protokoll

## Tanulási cél

Piaci adatokat tartalmazó összefoglaló készítése. Ebben a helyzetben te vagy piackutató, és gyors, de megbízható döntést kell hoznod.
A mai gyakorlati feladat végére kézben lesz forrásellenőrzési protokoll, amit holnap is újra tudsz használni.
Aha pont: tényellenőrzés akkor kezd működni, amikor a kimenetet már induláskor mérhetővé teszed.

A lecke végén képes leszel: **AI-állításokat megbízhatóan validálni**

### Sikerkritériumok (megfigyelhető)
- [ ] Elkészült a konkrét napi kimenet: **forrásellenőrzési protokoll**.
- [ ] A kimenethez rögzítve van legalább egy mérhető mutató: **5 állításból 5 forrással alátámasztott**.
- [ ] A fő kockázat kezelésére van külön ellenőrzési lépés: **hibás információ továbbadása**.

### Kimenet, amit ma elkészítesz
- **Név:** forrásellenőrzési protokoll
- **Formátum:** szerkeszthető tábla és rövid döntési jegyzet
- **Hova mented:** `ai-rutin/nap-13-hibak-hallucinaciok-kezelese.md`

## Kinek szól

**Elsődleges szerep:** piackutató  
**Másodlagos szerep:** tartalomfelelős  
**Érintett döntéshozó:** stratégiai vezető

## Miről szól

### Mi ez?
Ez a lecke gyakorlatban mutatja meg, hogyan alkalmazd **tényellenőrzés** módszert valós munkaszituációban.
A cél nem elmélet, hanem egy olyan kimenet, amit tényleg használhatsz a következő munkanapodon.

### Mi nem ez?
Nem általános AI-bemutató, és nem olyan feladat, amit csak bemutató kedvéért érdemes megcsinálni.

### 2 perces elmélet
- A magabiztos hangnem nem bizonyíték. A bizonyíték a forrás és az ellenőrzés.
- A kulcs az, hogy a feladatot mindig egyértelmű kimenetre fordítod.
- A minőséget itt az adja, hogy forrásellenőrzési protokoll ellenőrizhető és megismételhető.

### Kulcsfogalmak
- **Munkakeret:** rövid útmutató, ami leírja a cél, formátum, korlát hármast.
- **Minőségkapu:** gyors ellenőrzés a kimenet elfogadása előtt.

## Hol használod

### Itt működik jól
- piaci adatokat tartalmazó összefoglaló készítése típusú helyzetekben, amikor gyors és tiszta döntés kell
- amikor forrásellenőrzési protokoll több embernek ad át egyértelmű következő lépést

### Itt ne ezt használd
- ha hibás információ továbbadása kockázatot nem tudod emberi ellenőrzéssel lefedni

### Kapcsolódási pontok
- piackutató és tartalomfelelős közti napi átadások
- rövid státuszok és döntés-előkészítő jegyzetek
- ismétlődő feladatok, ahol 5 állításból 5 forrással alátámasztott számít

## Mikor használd

### Akkor használd, ha
- piaci adatokat tartalmazó összefoglaló készítése feladattal találkozol, és kevés az idő
- forrásellenőrzési protokoll alapján több szereplőnek kell azonosan cselekednie

### Gyakoriság
Munkanaponként legalább egyszer, visszatérő feladatnál minden alkalommal.

### Későn észlelt jelek
- forrásellenőrzési protokoll minden alkalommal újraírásra szorul
- gyakran visszakapod, hogy a tartalom nem kezeli hibás információ továbbadása problémát

## Miért számít

### Gyakorlati előnyök
- gyorsabban elkészül forrásellenőrzési protokoll, kevesebb körrel
- mérhetőbb lesz a minőség 5 állításból 5 forrással alátámasztott mutatóval
- csökken az utómunka, mert korán kiszűröd hibás információ továbbadása hibát

### Mi történik, ha kihagyod
- nő a félreértések száma piaci adatokat tartalmazó összefoglaló készítése helyzetben
- nehezebb tartani 5 állításból 5 forrással alátámasztott célt

### Reális elvárás
- Javulni fog: tényellenőrzés gyakorlati alkalmazása és az átadható kimenet minősége.
- Nem garantált: emberi ellenőrzés nélküli tévedhetetlen válasz minden futásban.

## Hogyan csináld

### Lépésről lépésre
1. Pontosan nevezd meg a munkaszituációt és a várt eredményt.
2. Írd le a kötelező korlátokat (időkeret, terjedelem, stílus, tiltások).
3. Kérd ki az első AI-verziót konkrét formátumban.
4. Futtass 3 pontos minőségkaput, külön figyelve **hibás információ továbbadása** kockázatra.
5. Javítsd a kimenetet, majd mentsd le használható sablonként.

### Tedd / Ne tedd
**Tedd**
- Rövid, konkrét feladatleírást adj meg úgy, hogy forrásellenőrzési protokoll formátuma már az elején tiszta legyen.
- A véglegesítés előtt ellenőrizd, hogy teljesült-e 5 állításból 5 forrással alátámasztott mérési pont.

**Ne tedd**
- Ne hagyd a háttérben hibás információ továbbadása témát, még akkor sem, ha a válasz elsőre jónak tűnik.
- Ne kérj általános szöveget, ha konkrét döntéshez kell anyag piaci adatokat tartalmazó összefoglaló készítése feladathoz.

### Gyakori hibák és javításuk
- **Hiba:** túl általános kérés indul piaci adatokat tartalmazó összefoglaló készítése helyzetre. **Javítás:** nevezd meg az érintettet, a határidőt és a döntési célpontot.
- **Hiba:** nincs kapcsolat a kimenet és 5 állításból 5 forrással alátámasztott mérés között. **Javítás:** minden futás végén rögzíts 1 bináris megfelelt/nem felelt meg eredményt.

### Akkor kész, ha
- [ ] Elkészült és lementetted **forrásellenőrzési protokoll** kimenetet.
- [ ] Ellenőrizted a kimenetet legalább 3 minőségkritérium szerint.
- [ ] A **5 állításból 5 forrással alátámasztott** mutatót dokumentáltad.

## Vezetett gyakorlat (10-15 perc)

### Inputok
- egy valós feladat rövid leírása a következő helyzetről: **Piaci adatokat tartalmazó összefoglaló készítése**
- egy rövid saját minta, ami mutatja, nálatok mi számít jó tényellenőrzés kimenetnek
- ellenőrzési lista hibás információ továbbadása kockázat kizárására

### Lépések
1. Írd le 4 sorban a helyzetet, a célt és azt, hogyan fogod mérni 5 állításból 5 forrással alátámasztott eredményt.
2. Készíts kérésmintát forrásellenőrzési protokoll előállításához, majd kérj két eltérő változatot.
3. Hasonlítsd össze a változatokat a táblában, és jelöld, melyik mehet tovább valós használatra.

### Várt kimenet formátuma
| Elem | Mit írsz be | Elvárt eredmény |
| --- | --- | --- |
| Helyzet | Piaci adatokat tartalmazó összefoglaló készítése | Minden érintett érti egy olvasásból |
| Kérésváz | Cél + kontextus + formátum + korlát | Minimum 2 használható változat |
| Minőségkapu | Pontosság + kockázat + következő lépés | Egyértelmű javítási döntés |
| Végleges kimenet | forrásellenőrzési protokoll | Mentve, újrahasználható sablon |

> **Pro tipp:** forrásellenőrzési protokoll akkor lesz stabil, ha minden futás után ugyanazzal a 3 kérdéssel ellenőrzöd.

## Önálló gyakorlat (5-10 perc)

### Feladat
Válassz egy saját, holnapi feladatot, ahol ugyanilyen típusú döntés kell, mint piaci adatokat tartalmazó összefoglaló készítése esetben. Alkalmazd a mai keretet úgy, hogy a végeredmény ugyanúgy mérhető legyen: 5 állításból 5 forrással alátámasztott.

### Kimenet
Egy rövid jegyzet 3 blokkal: helyzet, kérésminták, minőségkapu. A végére írj egy mondatot arról, mit változtattál forrásellenőrzési protokoll pontosabbá tételéhez.

## Gyors önellenőrzés (igen/nem)

- [ ] forrásellenőrzési protokoll elkészült és megosztható.
- [ ] 5 állításból 5 forrással alátámasztott mérési pont rögzítve van.
- [ ] hibás információ továbbadása kockázatra külön megelőző lépést futtattál.
- [ ] Van egy rövid döntési jegyzeted arról, miért az adott változatot választottad.

### Kiinduló mérőszám
- **Eredmény:** 5 állításból 5 forrással alátámasztott
- **Dátum:** 2026-02-11
- **Használt eszköz:** ChatGPT vagy más LLM

## Források

1. **OpenAI dokumentáció - Útmutatók**. OpenAI. 2026.  
   Olvasd: https://platform.openai.com/docs/guides
2. **NIST AI kockázatkezelési keretrendszer**. NIST. 2023.  
   Olvasd: https://www.nist.gov/itl/ai-risk-management-framework

## Továbbolvasás

1. **OpenAI - Kérésírási útmutató**  
   Miért: gyakorlati példákat ad azonnal átvehető mintákkal.  
   Olvasd: https://platform.openai.com/docs/guides/prompt-engineering
2. **Nielsen Norman Group - Felületi szövegírás**  
   Miért: segít megerősíteni a módszert valós munkaszituációkban.  
   Olvasd: https://www.nngroup.com/articles/writing-for-ui/

<!-- source-lesson-file: /Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/lessons/lesson-13-hibak-hallucinaciok-kezelese.md -->
