import json
import re
from datetime import datetime
from pathlib import Path

base = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11')
source = Path('/Users/moldovancsaba/Downloads/AI_30_NAP_export_2026-02-11.json')
lessons_dir = base / 'lessons'
quizzes_dir = base / 'quizzes'
out_json = base / 'AI_30_NAP_export_2026-02-11_refactored_lesson_by_lesson.json'

src = json.loads(source.read_text(encoding='utf-8'))
titles = [l['title'] for l in src['lessons']]

profiles = [
    {
        'hook': 'Tisztán indulunk: mit kérhetsz AI-tól, és mit nem szabad rábízni.',
        'focus': 'AI szerepének tisztázása',
        'deliverable': 'AI használati térkép 3 feladatra',
        'goal': 'különválasztani az AI-ra alkalmas és nem alkalmas feladatokat',
        'scenario': 'Napi ügyfélszolgálati feladatok gyorsítása adatvédelmi kockázat mellett',
        'risk': 'érzékeny adat véletlen megadása',
        'metric': '3/3 feladatnál helyes kockázati besorolás',
        'theory': 'Az AI eszköz, nem döntéshozó. A jó eredményhez tiszta cél és emberi ellenőrzés kell.',
    },
    {
        'hook': 'Egy jó prompt rövidebb, mint gondolnád, de sokkal pontosabb.',
        'focus': '4 elemes prompt szerkezet',
        'deliverable': 'promptkártya: cél, kontextus, forma, korlát',
        'goal': 'alapfeladatokat strukturált prompttá alakítani',
        'scenario': 'Határidőcsúszásról szóló email megírása kulcsügyfélnek',
        'risk': 'általános és használhatatlan kimenet',
        'metric': 'minden prompt tartalmazza a 4 kötelező elemet',
        'theory': 'A modell azt teljesíti, amit konkrétan kérsz. A formátum és korlát növeli a pontosságot.',
    },
    {
        'hook': 'A visszakérdezés nem hiba, hanem profi munkamódszer.',
        'focus': 'pontosító kérdések',
        'deliverable': '5 kérdéses visszakérdezési sablon',
        'goal': 'pontatlan briefből végrehajtható feladatot építeni',
        'scenario': 'Hiányos meeting-jegyzetből teendőlista készítése',
        'risk': 'rossz irányba induló munka',
        'metric': '5 kérdésből legalább 4 ténylegesen tisztázza az elvárást',
        'theory': 'A bizonytalanságot kérdésekkel csökkented. Minél tisztább a brief, annál kevesebb az utómunka.',
    },
    {
        'hook': 'A hangnem tartja egyben a márkaképet, ezért ezt is tanítani kell az AI-nak.',
        'focus': 'stílus és hang beállítása',
        'deliverable': 'személyes stílus-brief és tiltólista',
        'goal': 'saját hangnemre illesztett szövegeket létrehozni',
        'scenario': 'Ugyanaz az üzenet vezetőnek és ügyfélnek eltérő hangnemben',
        'risk': 'nem célközönségre illő kommunikáció',
        'metric': '2 célcsoportra 2 megfelelő hangvételű verzió',
        'theory': 'A stílus reprodukálható, ha adsz mintát, szabályt és ellenpéldát.',
    },
    {
        'hook': 'Biztonság nélkül nincs megbízható AI-rutin.',
        'focus': 'adatbiztonság és etika',
        'deliverable': 'AI biztonsági ellenőrzőlista',
        'goal': 'érzékeny adatot kiszűrni és anonimizálni',
        'scenario': 'Személyes adatot tartalmazó panaszkezelési eset feldolgozása',
        'risk': 'jogi és reputációs kár',
        'metric': '3 mintaanyagból 3 hibamentesen anonimizált',
        'theory': 'A sebesség nem írhatja felül a biztonságot. Az ellenőrzés kötelező része a folyamatnak.',
    },
    {
        'hook': 'Profi email 3 perc alatt is lehet pontos és emberi.',
        'focus': 'üzleti email-írás',
        'deliverable': '3 helyzetre használható email-sablon',
        'goal': 'különböző emailhelyzetekre konzisztens válaszokat írni',
        'scenario': 'Panaszkezelés, státuszjelentés és utánkövetés egy napon',
        'risk': 'túl hosszú vagy bizonytalan üzenet',
        'metric': 'mindhárom emailben egyértelmű CTA szerepel',
        'theory': 'Az email célja döntés vagy válasz kiváltása. Rövidség + egyértelmű kérés ad eredményt.',
    },
    {
        'hook': 'A meeting értéke az utókövetés minőségén múlik.',
        'focus': 'meetingből akcióterv',
        'deliverable': 'meeting action log felelőssel és határidővel',
        'goal': 'jegyzetből egyértelmű feladatlistát készíteni',
        'scenario': '45 perces státuszmeeting utáni teendők kiosztása',
        'risk': 'felelős nélküli feladatok',
        'metric': 'minden teendőhöz tartozik felelős és dátum',
        'theory': 'A jó összefoglaló döntést és felelőst rögzít, nem csak eseménytörténetet.',
    },
    {
        'hook': 'Egy hosszú anyagból többféle hasznos kimenet készülhet, ha jól kéred.',
        'focus': 'brief, vázlat, összefoglaló készítése',
        'deliverable': '3 szintű dokumentumcsomag',
        'goal': 'egy forrásból több célra alkalmas kimenetet készíteni',
        'scenario': '20 oldalas háttéranyag átadása vezetőnek és csapatnak',
        'risk': 'lényeg elvesztése',
        'metric': '5 kulcsinformáció mindhárom verzióban szerepel',
        'theory': 'A dokumentum mélysége célfüggő. Ugyanaz a tartalom más formában ad értéket.',
    },
    {
        'hook': 'A táblázat nem formai trükk, hanem döntéstámogató eszköz.',
        'focus': 'táblázatos gondolkodás',
        'deliverable': 'összehasonlító döntési tábla',
        'goal': 'szöveges inputot összehasonlítható táblává alakítani',
        'scenario': '3 beszállítói ajánlat összevetése',
        'risk': 'szempontok keveredése',
        'metric': 'legalább 4 közös értékelési szempont',
        'theory': 'A struktúra csökkenti a torzítást. Egységes szempontok nélkül nincs fair összehasonlítás.',
    },
    {
        'hook': 'A hibás prompt javítható, ha tudod, mit nézz.',
        'focus': 'prompt debug',
        'deliverable': 'prompt hibakatalógus javítással',
        'goal': 'tipikus prompthibákat felismerni és javítani',
        'scenario': 'Visszatérően gyenge AI-kimenet egy csapatban',
        'risk': 'ugyanaz a hiba ismétlődik',
        'metric': '3 hibás promptból 3 javított verzió',
        'theory': 'A hibát nem érzésre, hanem tünet alapján javítjuk: cél, kontextus, forma, korlát.',
    },
    {
        'hook': 'A jó prompt nem egyszeri ötlet, hanem újrahasznosítható eszköz.',
        'focus': 'prompt könyvtár',
        'deliverable': 'tagelt prompt könyvtár v1',
        'goal': 'visszatérő feladatokra gyorsan elővehető promptokat építeni',
        'scenario': 'Hetente ismétlődő ügyfélkommunikációs feladatok',
        'risk': 'mindig nulláról indulás',
        'metric': '10 címkézett prompt mentve és dokumentálva',
        'theory': 'A könyvtár a sebességet és a minőséget egyszerre növeli, ha karbantartod.',
    },
    {
        'hook': 'A workflow akkor stabil, ha bemenetet, feldolgozást és kimenetet külön kezeled.',
        'focus': 'input-feldolgozás-output modell',
        'deliverable': '3 lépéses workflow tervlap',
        'goal': 'ismétlődő feladatot reprodukálható folyamattá alakítani',
        'scenario': 'Bejövő leadek napi minősítése',
        'risk': 'ad hoc döntések',
        'metric': 'minden lépéshez egyértelmű bemenet és kimenet',
        'theory': 'A folyamat akkor skálázható, ha minden lépés ellenőrizhető és átadható másnak is.',
    },
    {
        'hook': 'Hallucináció ellen csak módszeres ellenőrzés működik.',
        'focus': 'tényellenőrzés',
        'deliverable': 'forrásellenőrzési protokoll',
        'goal': 'AI-állításokat megbízhatóan validálni',
        'scenario': 'Piaci adatokat tartalmazó összefoglaló készítése',
        'risk': 'hibás információ továbbadása',
        'metric': '5 állításból 5 forrással alátámasztott',
        'theory': 'A magabiztos hangnem nem bizonyíték. A bizonyíték a forrás és az ellenőrzés.',
    },
    {
        'hook': 'A személyes AI-asszisztens attól jó, hogy mindig ugyanazt a minőséget hozza.',
        'focus': 'asszisztens rendszerprompt',
        'deliverable': 'szerepkör-alapú rendszerutasítás',
        'goal': 'állandó minőségű AI-segítőt beállítani',
        'scenario': 'Több feladattípus kezelése egységes hangnemben',
        'risk': 'inkonzisztens válaszminőség',
        'metric': '4 feladattípusnál konzisztens kimenet',
        'theory': 'A rendszerprompt keretet ad. Ettől lesz kiszámítható az eredmény.',
    },
    {
        'hook': 'A rossz promptból is lehet jó, ha tudatos iterációt használsz.',
        'focus': 'prompt újraírás',
        'deliverable': '2 körös prompt újraírási keret',
        'goal': 'gyenge promptot lépésről lépésre javítani',
        'scenario': 'Elnagyolt kérésből használható draft készítése',
        'risk': 'első kör után megálló javítás',
        'metric': '2 iteráció után mérhető minőségjavulás',
        'theory': 'Az iteráció célja nem több szöveg, hanem jobb döntési minőség.',
    },
    {
        'hook': 'Most a saját szerepedre fordítjuk le az AI-t.',
        'focus': 'szerepkör-specifikus AI-használat',
        'deliverable': '5 use case-es szerepkör-kártya',
        'goal': 'saját munkakörre releváns AI-felhasználást tervezni',
        'scenario': 'Új csapattag AI-rutin bevezetése',
        'risk': 'általános, hatás nélküli használat',
        'metric': '5 use case-ből legalább 4 napi szinten hasznos',
        'theory': 'A relevancia adja az értéket. Nem minden eszköz jó minden feladatra.',
    },
    {
        'hook': 'Sablonokkal stabilabb lesz a kommunikációs minőség.',
        'focus': 'kommunikációs sabloncsomag',
        'deliverable': '6 helyzetre kész üzenetsablon',
        'goal': 'visszatérő kommunikációs helyzeteket szabványosítani',
        'scenario': 'Értékesítési és support válaszok egységesítése',
        'risk': 'széteső stílus és minőség',
        'metric': '6 sablon mindegyike használható teszthelyzetben',
        'theory': 'A sablon nem merevség, hanem gyors minőségbiztosítás.',
    },
    {
        'hook': 'Most az elemző és döntéselőkészítő sablonokat építjük fel.',
        'focus': 'riport és elemző sablonok',
        'deliverable': '3 riportformátum sablon',
        'goal': 'különböző vezetői szintekre eltérő riportot készíteni',
        'scenario': 'Heti riport készítése operatív és vezetői nézetben',
        'risk': 'nem megfelelő részletezettség',
        'metric': '3 célcsoporthoz 3 eltérő, használható riport',
        'theory': 'A jó riport a címzetthez igazodik. Ugyanaz az adat más nézetet igényel.',
    },
    {
        'hook': 'A csapdák listája gyorsabban javít, mint az utólagos tűzoltás.',
        'focus': 'szerepspecifikus hibák megelőzése',
        'deliverable': 'hiba-ellenlépés mátrix',
        'goal': 'tipikus hibákhoz megelőző rutint rendelni',
        'scenario': 'Sűrű határidős környezetben végzett AI-támogatott munka',
        'risk': 'ismétlődő hibák és késések',
        'metric': '5 hibatípushoz 5 konkrét megelőző lépés',
        'theory': 'A megelőzés olcsóbb, mint az utómunka. A minták felismerése kulcs.',
    },
    {
        'hook': 'Most mérjük, hol tartasz valós feladaton, nem csak érzésre.',
        'focus': 'skill-check',
        'deliverable': 'egyéni skill scorecard',
        'goal': 'saját AI-munkafolyamat minőségét mérni',
        'scenario': 'Mini projekt végigvitele brieftől kész anyagig',
        'risk': 'pontatlan önértékelés',
        'metric': 'scorecard 4 dimenzióban kitöltve',
        'theory': 'A fejlődéshez mérés kell. Amit nem mérsz, azon nehéz javítani.',
    },
    {
        'hook': 'Ötletből csak akkor lesz termék, ha validálod a feltételezéseket.',
        'focus': 'ötletvalidálás',
        'deliverable': 'hipotézis és tesztlap',
        'goal': 'ötletet mérhető hipotézisekké bontani',
        'scenario': 'Új szolgáltatás gyors előszűrése',
        'risk': 'feltételezés tényként kezelése',
        'metric': 'legalább 3 tesztelhető hipotézis',
        'theory': 'A validálás célja a tévedés gyors felismerése, nem a megerősítés keresése.',
    },
    {
        'hook': 'A jó értékajánlat nem mindenkinek szól, hanem valakinek nagyon.',
        'focus': 'persona és értékajánlat',
        'deliverable': 'persona + értékajánlat kártya',
        'goal': 'célcsoport és ajánlat pontos párosítása',
        'scenario': 'Új termék üzenetének megfogalmazása',
        'risk': 'túl általános üzenet',
        'metric': 'fájdalompont és ajánlat egyértelmű párosítása',
        'theory': 'A relevancia a konverzió alapja. A célzott üzenet erősebb, mint az általános.',
    },
    {
        'hook': 'A landing akkor működik, ha egy mondatban érthető, mit nyer a látogató.',
        'focus': 'landing struktúra és copy',
        'deliverable': 'landing vázlat hero-val és CTA-val',
        'goal': 'konverzióra alkalmas landing vázlatot készíteni',
        'scenario': 'Gyors kampányindítás minimál oldallal',
        'risk': 'nem egyértelmű ajánlat',
        'metric': 'hero, bizonyíték, ajánlat, CTA mind jelen van',
        'theory': 'A landing oldalon a sorrend dönt: probléma, megoldás, bizonyíték, cselekvés.',
    },
    {
        'hook': 'Az ár nem számkitalálás, hanem értékpozicionálás.',
        'focus': 'árazási alapok',
        'deliverable': '3 opciós árazási tábla',
        'goal': 'árazási opciókat célcsoporthoz illeszteni',
        'scenario': 'Szolgáltatás bevezetése különböző csomagokkal',
        'risk': 'alul- vagy túlárazás',
        'metric': 'mindhárom opcióhoz célvevő és indoklás',
        'theory': 'A jó ár a vevő által érzékelt értékhez igazodik, nem csak a költséghez.',
    },
    {
        'hook': 'Az MVP ereje abban van, amit tudatosan kihagysz.',
        'focus': 'MVP scope',
        'deliverable': 'must-have vs later mátrix',
        'goal': 'scope-ot szűkíteni és priorizálni',
        'scenario': 'Induló termék korlátozott erőforrással',
        'risk': 'scope creep',
        'metric': 'legalább 5 elem egyértelmű priorizálása',
        'theory': 'A fókusz gyorsítja a piacra jutást. A "nem most" lista stratégiai eszköz.',
    },
    {
        'hook': 'A rutin teszi tartóssá a tudást.',
        'focus': 'napi AI rutin',
        'deliverable': 'heti AI rutin naptár',
        'goal': 'fenntartható AI-gyakorlati ritmust kialakítani',
        'scenario': 'Ad hoc használat helyett tervezett napi blokkok',
        'risk': 'széteső használat és visszaesés',
        'metric': '5 konkrét idősáv és feladattípus rögzítve',
        'theory': 'A rendszeres kis lépések tartósabbak, mint az alkalmi nagy sprint.',
    },
    {
        'hook': 'A 60 másodperces pitch fegyelemre tanít: csak a lényeg marad.',
        'focus': 'pitch struktúra',
        'deliverable': '60 másodperces pitch script',
        'goal': 'rövid és meggyőző értékkommunikációt készíteni',
        'scenario': 'Bemutatkozás vezetőnek vagy partnernek rövid időablakban',
        'risk': 'széteső üzenet',
        'metric': 'pitch 60-75 másodperc között marad',
        'theory': 'A jó pitch probléma-megoldás-érték-CTA logikát követ.',
    },
    {
        'hook': 'Most a legjobb anyagaidból portfólió-képes csomagot készítünk.',
        'focus': 'portfólió szintű kimenetek',
        'deliverable': '3 elemes portfóliócsomag',
        'goal': 'kurzuskimeneteket bemutatható anyaggá alakítani',
        'scenario': 'Állásváltás vagy ügyfélszerzés támogatása',
        'risk': 'nem bizonyítható eredmény',
        'metric': '3 portfólióelem mindegyike tartalmaz mérhető hatást',
        'theory': 'A portfólióban nem a mennyiség, hanem a bizonyítható eredmény számít.',
    },
    {
        'hook': 'A fejlődés akkor marad meg, ha van terved a kurzus utánra is.',
        'focus': '90 napos fejlődési terv',
        'deliverable': '12 hetes fejlődési roadmap',
        'goal': 'kurzus utáni fejlődést ütemezni és mérni',
        'scenario': 'Tudásfenntartás munka melletti heti rutinban',
        'risk': 'visszaesés régi működésbe',
        'metric': '12 heti checkpoint és mérőszám rögzítve',
        'theory': 'A terv + mérés együtt ad lendületet. Az ismétlés és reflexió tartósítja a tudást.',
    },
    {
        'hook': 'Lezárásként konkrét 30 napos akciótervet készítesz, hogy a tudás azonnal használatba kerüljön.',
        'focus': 'akcióterv és következő lépések',
        'deliverable': '30 napos AI akcióterv',
        'goal': 'a tanult módszereket napi működésbe beépíteni',
        'scenario': 'Kurzus utáni első hónap célzott végrehajtása',
        'risk': 'ismeret marad, gyakorlat nem lesz',
        'metric': '30 napra bontott feladatlista, heti review-val',
        'theory': 'A lezárás akkor értékes, ha konkrét következő lépéshez kötődik.',
    },
]

if len(profiles) != 30:
    raise ValueError('profiles must have 30 entries')

bibliography = [
    ('OpenAI - Prompting guide', 'https://platform.openai.com/docs/guides/prompt-engineering'),
    ('Nielsen Norman Group - Writing for interfaces', 'https://www.nngroup.com/articles/writing-for-ui/'),
    ('NIST AI Risk Management Framework', 'https://www.nist.gov/itl/ai-risk-management-framework'),
    ('Atlassian Team Playbook', 'https://www.atlassian.com/team-playbook'),
]

read_more = [
    ('One Useful Thing', 'https://www.oneusefulthing.org/'),
    ('OpenAI - Guides', 'https://platform.openai.com/docs/guides'),
    ('MindTools - Decision matrix', 'https://www.mindtools.com/ahwn4x6/decision-matrix-analysis'),
]


def slugify(s: str) -> str:
    mapping = str.maketrans('áéíóöőúüűÁÉÍÓÖŐÚÜŰ', 'aeiooouuuAEIOOOUUU')
    s = s.translate(mapping)
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()


def lesson_markdown(day: int, title: str, p: dict) -> str:
    b1 = bibliography[day % len(bibliography)]
    b2 = bibliography[(day + 1) % len(bibliography)]
    r1 = read_more[day % len(read_more)]
    callout = 'Pro tip' if day % 2 else 'Common mistake'
    callout_text = (
        'Minden kimenet előtt nézd át: cél, pontosság, következő lépés.'
        if callout == 'Pro tip'
        else 'Ne hagyd ki a formátumot és a terjedelmi korlátot, mert ettől lesz használható a válasz.'
    )

    return f"""# Lesson {day}: {title}

**One-liner:** {p['hook']}  
**Time:** 20-30 perc  
**Deliverable:** {p['deliverable']}

## Learning goal

You will be able to: **{p['goal']}**

### Success criteria (observable)
- [ ] A cél és az elvárt kimenet egyértelmű.
- [ ] Elkészül a napi deliverable valós helyzetre.
- [ ] A minőséget konkrét mérőszámmal ellenőrzöd.

## Who

- Kezdőknek, akik stabil alapot építenek.
- Újrakezdőknek, akik rendszert szeretnének a gyakorlatban.

## What

### What it is

Ez a lecke gyakorlati egység a(z) {p['focus']} témában, valós szituációval és mérhető kimenettel.

### What it is not

Nem elméleti áttekintés és nem általános inspiráció. Célja az azonnal használható eredmény.

### 2-minute theory

{p['theory']}

## Where

- Napi kommunikációban, dokumentum- és feladatkezelésben.
- Olyan helyzetekben, ahol gyors döntés és pontos kimenet kell.

## When

- Ha rövid idő alatt használható első verzióra van szükség.
- Ha több opciót kell összehasonlítani és dönteni.

## Why it matters

A(z) {p['focus']} készség csökkenti az újramunkát és növeli a kimenet megbízhatóságát.
Kezdőként ez adja a legnagyobb időnyereséget és magabiztosságot.

## How

1. Rögzítsd a célt és a sikerfeltételt.
2. Adj konkrét formátumot, korlátot és kontextust.
3. Ellenőrizd a kész kimenetet a mérőszám szerint.

### Guided exercise

Szituáció: **{p['scenario']}**.
Készíts workflow-t az alábbi táblázat szerint.

| Lépés | Mit adsz meg | Várt eredmény |
| --- | --- | --- |
| Cél | Feladat + célközönség + elvárt hatás | Pontos brief |
| Kérés | Formátum + terjedelem + stílus + korlát | Használható első verzió |
| Ellenőrzés | 3 minőségi kérdés + 1 mérőszám | Javítható végleges változat |

> **{callout}:** {callout_text}

### Independent exercise

- Hozz egy saját, valós feladatot.
- Készíts rá 2 eltérő promptot.
- Válaszd ki a jobb verziót, és indokold röviden.

### Self-check

- [ ] Elkészült a deliverable: {p['deliverable']}.
- [ ] Kezelted a fő kockázatot: {p['risk']}.
- [ ] Teljesült a mérés: {p['metric']}.

## Bibliography

- {b1[0]}: {b1[1]}
- {b2[0]}: {b2[1]}

## Read more

- {r1[0]}: {r1[1]}
"""


def quiz_questions(title: str, p: dict, day: int):
    tag = f'day-{day:02d}'
    return [
        {
            'hashtags': [tag, 'application'],
            'question': f"{title}: A következő helyzetben dolgozol: {p['scenario']}. Mi az első lépés a mérhető kimenethez?",
            'options': [
                'A cél és az elfogadási kritérium rögzítése a prompt elején',
                'Azonnali hosszú válasz kérése korlátok nélkül',
                'Csak a sebességre optimalizálás',
                'Ellenőrzés kihagyása az első körben'
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'application',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'diagnostic'],
            'question': f"{title}: A kimenet túl általános lett. Melyik javítás adja a legnagyobb minőségugrást?",
            'options': [
                'Konkrét formátumot, terjedelmet és célközönséget adsz meg újrafuttatás előtt',
                'Ugyanazt a promptot ismét futtatod változtatás nélkül',
                'Az AI használatát teljesen elhagyod',
                'Csak a helyesírást javítod a tartalom helyett'
            ],
            'correctIndex': 0,
            'difficulty': 'HARD',
            'category': 'Course Specific',
            'questionType': 'diagnostic',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'best-practice'],
            'question': f"{title}: Melyik lépés csökkenti legjobban ezt a kockázatot: {p['risk']}?",
            'options': [
                'Kötelező minőségkapu futtatása küldés előtt',
                'Csak formai ellenőrzés tartalmi validálás nélkül',
                'Gyorsaság előnyben részesítése minden helyzetben',
                'Ugyanaz a sablon minden kontextusra'
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'best_practice',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'metric'],
            'question': f"{title}: Melyik mutató bizonyítja legjobban, hogy működik a napi módszer? ({p['metric']})",
            'options': [
                'A mérőszám teljesül valós próbafeladaton',
                'A válasz hosszabb lett az előzőnél',
                'A válasz gyorsan elkészült ellenőrzés nélkül',
                'A szöveg sok szakmai kifejezést tartalmaz'
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'metric',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'critical-thinking'],
            'question': f"{title}: Melyik döntés mutatja a legjobb kezdő szemléletet?",
            'options': [
                'Sebesség és minőség együtt, kötelező emberi ellenőrzéssel',
                'Csak sebességre fókusz, ellenőrzés később',
                'A modell válaszát bizonyíték nélkül elfogadod',
                'A kontextust kihagyod, mert úgyis kitalálja'
            ],
            'correctIndex': 0,
            'difficulty': 'HARD',
            'category': 'Course Specific',
            'questionType': 'critical-thinking',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'application'],
            'question': f"{title}: Melyik prompt ad legnagyobb eséllyel használható kimenetet első körben?",
            'options': [
                'Adj 2 verziót max 120 szóban, célközönségre szabva, konkrét következő lépéssel',
                'Írj valamit erről gyorsan',
                'Legyen hosszú szöveg, a formátum mindegy',
                'Bármilyen stílus jó, nincs elvárás'
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'application',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'application'],
            'question': f"{title}: Melyik sorrend adja a legkevesebb újramunkát?",
            'options': [
                'Cél -> Prompt -> Minőségellenőrzés -> Finomítás',
                'Prompt -> Küldés -> Utólagos javítás',
                'Korlátok kihagyása -> Többszöri vak újrafuttatás',
                'Részletes elvárás nélkül kérés -> Teljes kézi átírás'
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'application',
            'isActive': True,
        },
    ]


def quiz_markdown(day: int, title: str, questions: list[dict]) -> str:
    letters = ['A', 'B', 'C', 'D']
    out = [f"# Lesson {day} Quiz: {title}", '', '## Question pool']
    for i, q in enumerate(questions, start=1):
        out += ['', f"### Q{i}", q['question']]
        for oi, opt in enumerate(q['options']):
            out.append(f"- {letters[oi]}. {opt}")
        out.append(f"- Correct: {letters[q['correctIndex']]}")
        out.append(f"- Type: {q['questionType']}")
        out.append(f"- Difficulty: {q['difficulty']}")
    return '\n'.join(out) + '\n'


assembled = []
seen_q = set()
for i, title in enumerate(titles, start=1):
    p = profiles[i - 1]
    slug = slugify(title)
    content = lesson_markdown(i, title, p)
    questions = quiz_questions(title, p, i)

    for q in questions:
        key = re.sub(r'\s+', ' ', q['question'].strip().lower())
        if key in seen_q:
            raise ValueError(f'duplicate question: {q["question"]}')
        seen_q.add(key)

    lesson_file = lessons_dir / f'lesson-{i:02d}-{slug}.md'
    quiz_file = quizzes_dir / f'lesson-{i:02d}-{slug}-quiz.md'
    lesson_file.write_text(content, encoding='utf-8')
    quiz_file.write_text(quiz_markdown(i, title, questions), encoding='utf-8')

    assembled.append({
        'lessonId': f'AI_30_NAP_DAY_{i:02d}',
        'dayNumber': i,
        'language': 'hu',
        'title': title,
        'content': content,
        'emailSubject': f'AI 30 Nap - {i}. nap: {title}',
        'emailBody': '# {{courseName}}\n\n## {{dayNumber}}. nap: {{lessonTitle}}\n\n{{lessonContent}}\n\n[Olvasd el a teljes leckét ->](http://localhost:3000/courses/AI_30_NAP/day/{{dayNumber}})',
        'quizConfig': {
            'enabled': True,
            'successThreshold': 80,
            'questionCount': 5,
            'poolSize': 7,
            'required': True,
        },
        'unlockConditions': {
            'requirePreviousLesson': False if i == 1 else True,
            'requireCourseStart': True,
        },
        'pointsReward': 50,
        'xpReward': 25,
        'isActive': True,
        'displayOrder': i,
        'metadata': {
            'estimatedMinutes': 25,
            'focus': p['focus'],
            'sourceLessonFile': str(lesson_file),
            'sourceQuizFile': str(quiz_file),
        },
        'translations': {},
        'quizQuestions': questions,
    })

course = src['course']
course['description'] = '30 napos AI felzárkóztató kezdőknek és újrakezdőknek. Minden lecke önálló, gyakorlati mini-egység valós szituációval és mérhető kimenettel.'
course['defaultLessonQuizQuestionCount'] = 5
course['metadata']['estimatedHours'] = 12.5

pkg = {
    'packageVersion': '2.0',
    'version': '2.0',
    'exportedAt': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
    'exportedBy': 'codex-lesson-by-lesson-refactor',
    'course': course,
    'lessons': assembled,
    'canonicalSpec': src.get('canonicalSpec'),
    'courseIdea': src.get('courseIdea'),
}
out_json.write_text(json.dumps(pkg, ensure_ascii=False, indent=2), encoding='utf-8')

print(out_json)
print(f'lesson-files={len(list(lessons_dir.glob("lesson-*.md")))}')
print(f'quiz-files={len(list(quizzes_dir.glob("lesson-*-quiz.md")))}')
