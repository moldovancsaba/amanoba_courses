# Lecke 19: Tipikus csapdák az adott szerepben

**Egy mondatban:** A csapdák listája gyorsabban javít, mint az utólagos tűzoltás.  
**Idő:** 20-30 perc  
**Kézzelfogható kimenet:** hiba-ellenlépés mátrix

## Tanulási cél

Sűrű határidős környezetben végzett AI-támogatott munka. Ebben a helyzetben te vagy toborzó, és gyors, de megbízható döntést kell hoznod.
A mai gyakorlati feladat végére kézben lesz hiba-ellenlépés mátrix, amit holnap is újra tudsz használni.
Aha pont: szerepspecifikus hibák megelőzése akkor kezd működni, amikor a kimenetet már induláskor mérhetővé teszed.

A lecke végén képes leszel: **tipikus hibákhoz megelőző rutint rendelni**

### Sikerkritériumok (megfigyelhető)
- [ ] Elkészült a konkrét napi kimenet: **hiba-ellenlépés mátrix**.
- [ ] A kimenethez rögzítve van legalább egy mérhető mutató: **5 hibatípushoz 5 konkrét megelőző lépés**.
- [ ] A fő kockázat kezelésére van külön ellenőrzési lépés: **ismétlődő hibák és késések**.

### Kimenet, amit ma elkészítesz
- **Név:** hiba-ellenlépés mátrix
- **Formátum:** szerkeszthető tábla és rövid döntési jegyzet
- **Hova mented:** `ai-rutin/nap-19-tipikus-csapdak-az-adott-szerepben.md`

## Kinek szól

**Elsődleges szerep:** toborzó  
**Másodlagos szerep:** felvételi vezető  
**Érintett döntéshozó:** HR igazgató

## Miről szól

### Mi ez?
Ez a lecke gyakorlatban mutatja meg, hogyan alkalmazd **szerepspecifikus hibák megelőzése** módszert valós munkaszituációban.
A cél nem elmélet, hanem egy olyan kimenet, amit tényleg használhatsz a következő munkanapodon.

### Mi nem ez?
Nem általános AI-bemutató, és nem olyan feladat, amit csak bemutató kedvéért érdemes megcsinálni.

### 2 perces elmélet
- A megelőzés olcsóbb, mint az utómunka. A minták felismerése kulcs.
- A minőséghez két dolog kell: jó feladatleírás és következetes ellenőrzés.
- A minőséget itt az adja, hogy hiba-ellenlépés mátrix ellenőrizhető és megismételhető.

### Kulcsfogalmak
- **Munkakeret:** rövid útmutató, ami leírja a cél, formátum, korlát hármast.
- **Minőségkapu:** gyors ellenőrzés a kimenet elfogadása előtt.

## Hol használod

### Itt működik jól
- sűrű határidős környezetben végzett ai-támogatott munka típusú helyzetekben, amikor gyors és tiszta döntés kell
- amikor hiba-ellenlépés mátrix több embernek ad át egyértelmű következő lépést

### Itt ne ezt használd
- ha ismétlődő hibák és késések kockázatot nem tudod emberi ellenőrzéssel lefedni

### Kapcsolódási pontok
- toborzó és felvételi vezető közti napi átadások
- rövid státuszok és döntés-előkészítő jegyzetek
- ismétlődő feladatok, ahol 5 hibatípushoz 5 konkrét megelőző lépés számít

## Mikor használd

### Akkor használd, ha
- sűrű határidős környezetben végzett ai-támogatott munka feladattal találkozol, és kevés az idő
- hiba-ellenlépés mátrix alapján több szereplőnek kell azonosan cselekednie

### Gyakoriság
Munkanaponként legalább egyszer, visszatérő feladatnál minden alkalommal.

### Későn észlelt jelek
- hiba-ellenlépés mátrix minden alkalommal újraírásra szorul
- gyakran visszakapod, hogy a tartalom nem kezeli ismétlődő hibák és késések problémát

## Miért számít

### Gyakorlati előnyök
- gyorsabban elkészül hiba-ellenlépés mátrix, kevesebb körrel
- mérhetőbb lesz a minőség 5 hibatípushoz 5 konkrét megelőző lépés mutatóval
- csökken az utómunka, mert korán kiszűröd ismétlődő hibák és késések hibát

### Mi történik, ha kihagyod
- nő a félreértések száma sűrű határidős környezetben végzett ai-támogatott munka helyzetben
- nehezebb tartani 5 hibatípushoz 5 konkrét megelőző lépés célt

### Reális elvárás
- Javulni fog: szerepspecifikus hibák megelőzése gyakorlati alkalmazása és az átadható kimenet minősége.
- Nem garantált: emberi ellenőrzés nélküli tévedhetetlen válasz minden futásban.

## Hogyan csináld

### Lépésről lépésre
1. Pontosan nevezd meg a munkaszituációt és a várt eredményt.
2. Írd le a kötelező korlátokat (időkeret, terjedelem, stílus, tiltások).
3. Kérd ki az első AI-verziót konkrét formátumban.
4. Futtass 3 pontos minőségkaput, külön figyelve **ismétlődő hibák és késések** kockázatra.
5. Javítsd a kimenetet, majd mentsd le használható sablonként.

### Tedd / Ne tedd
**Tedd**
- Rövid, konkrét feladatleírást adj meg úgy, hogy hiba-ellenlépés mátrix formátuma már az elején tiszta legyen.
- A véglegesítés előtt ellenőrizd, hogy teljesült-e 5 hibatípushoz 5 konkrét megelőző lépés mérési pont.

**Ne tedd**
- Ne hagyd a háttérben ismétlődő hibák és késések témát, még akkor sem, ha a válasz elsőre jónak tűnik.
- Ne kérj általános szöveget, ha konkrét döntéshez kell anyag sűrű határidős környezetben végzett ai-támogatott munka feladathoz.

### Gyakori hibák és javításuk
- **Hiba:** túl általános kérés indul sűrű határidős környezetben végzett ai-támogatott munka helyzetre. **Javítás:** nevezd meg az érintettet, a határidőt és a döntési célpontot.
- **Hiba:** nincs kapcsolat a kimenet és 5 hibatípushoz 5 konkrét megelőző lépés mérés között. **Javítás:** minden futás végén rögzíts 1 bináris megfelelt/nem felelt meg eredményt.

### Akkor kész, ha
- [ ] Elkészült és lementetted **hiba-ellenlépés mátrix** kimenetet.
- [ ] Ellenőrizted a kimenetet legalább 3 minőségkritérium szerint.
- [ ] A **5 hibatípushoz 5 konkrét megelőző lépés** mutatót dokumentáltad.

## Vezetett gyakorlat (10-15 perc)

### Inputok
- egy valós feladat rövid leírása a következő helyzetről: **Sűrű határidős környezetben végzett AI-támogatott munka**
- egy rövid saját minta, ami mutatja, nálatok mi számít jó szerepspecifikus hibák megelőzése kimenetnek
- ellenőrzési lista ismétlődő hibák és késések kockázat kizárására

### Lépések
1. Írd le 4 sorban a helyzetet, a célt és azt, hogyan fogod mérni 5 hibatípushoz 5 konkrét megelőző lépés eredményt.
2. Készíts kérésmintát hiba-ellenlépés mátrix előállításához, majd kérj két eltérő változatot.
3. Hasonlítsd össze a változatokat a táblában, és jelöld, melyik mehet tovább valós használatra.

### Várt kimenet formátuma
| Elem | Mit írsz be | Elvárt eredmény |
| --- | --- | --- |
| Helyzet | Sűrű határidős környezetben végzett AI-támogatott munka | Minden érintett érti egy olvasásból |
| Kérésváz | Cél + kontextus + formátum + korlát | Minimum 2 használható változat |
| Minőségkapu | Pontosság + kockázat + következő lépés | Egyértelmű javítási döntés |
| Végleges kimenet | hiba-ellenlépés mátrix | Mentve, újrahasználható sablon |

> **Pro tipp:** hiba-ellenlépés mátrix akkor lesz stabil, ha minden futás után ugyanazzal a 3 kérdéssel ellenőrzöd.

## Önálló gyakorlat (5-10 perc)

### Feladat
Válassz egy saját, holnapi feladatot, ahol ugyanilyen típusú döntés kell, mint sűrű határidős környezetben végzett ai-támogatott munka esetben. Alkalmazd a mai keretet úgy, hogy a végeredmény ugyanúgy mérhető legyen: 5 hibatípushoz 5 konkrét megelőző lépés.

### Kimenet
Egy rövid jegyzet 3 blokkal: helyzet, kérésminták, minőségkapu. A végére írj egy mondatot arról, mit változtattál hiba-ellenlépés mátrix pontosabbá tételéhez.

## Gyors önellenőrzés (igen/nem)

- [ ] hiba-ellenlépés mátrix elkészült és megosztható.
- [ ] 5 hibatípushoz 5 konkrét megelőző lépés mérési pont rögzítve van.
- [ ] ismétlődő hibák és késések kockázatra külön megelőző lépést futtattál.
- [ ] Van egy rövid döntési jegyzeted arról, miért az adott változatot választottad.

### Kiinduló mérőszám
- **Eredmény:** 5 hibatípushoz 5 konkrét megelőző lépés
- **Dátum:** 2026-02-11
- **Használt eszköz:** ChatGPT vagy más LLM

## Források

1. **Nielsen Norman Group - UX szövegírás**. NN/g. 2024.  
   Olvasd: https://www.nngroup.com/articles/writing-for-ui/
2. **Atlassian csapatmunka játékkönyv**. Atlassian. 2025.  
   Olvasd: https://www.atlassian.com/team-playbook

## Továbbolvasás

1. **NIST - AI kockázatkezelési keretrendszer**  
   Miért: gyakorlati példákat ad azonnal átvehető mintákkal.  
   Olvasd: https://www.nist.gov/itl/ai-risk-management-framework
2. **Atlassian - Csapatmunka játékkönyv**  
   Miért: segít megerősíteni a módszert valós munkaszituációkban.  
   Olvasd: https://www.atlassian.com/team-playbook

<!-- source-lesson-file: /Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/lessons/lesson-19-tipikus-csapdak-az-adott-szerepben.md -->
