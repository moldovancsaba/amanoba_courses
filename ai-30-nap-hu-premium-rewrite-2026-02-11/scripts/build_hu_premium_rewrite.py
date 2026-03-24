#!/usr/bin/env python3
import ast
import json
import re
from datetime import datetime
from pathlib import Path

BASE_DIR = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11')
LESSONS_DIR = BASE_DIR / 'lessons'
QUIZZES_DIR = BASE_DIR / 'quizzes'
SOURCE_JSON = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11/source-AI_30_NAP_export_2026-02-11.json')
PREV_SCRIPT = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11/scripts/generate_lesson_by_lesson_course.py')
OUT_JSON_PRIMARY = BASE_DIR / 'AI_30_NAP_export_2026-02-11_hu-premium-rewrite.json'
OUT_JSON_ALIAS = BASE_DIR / 'AI_30_NAP_export_2026-02-11_premium_rewrite.json'

PERSONAS = [
    ('ügyfélszolgálati koordinátor', 'adatvédelmi felelős', 'ügyvezető'),
    ('junior marketinges', 'értékesítési vezető', 'kulcsügyfél'),
    ('projektkoordinátor', 'csapatvezető', 'megrendelő'),
    ('szabadúszó szövegíró', 'márkamenedzser', 'ügyfélkapcsolati vezető'),
    ('HR adminisztrátor', 'jogi tanácsadó', 'HR vezető'),
    ('ügyfélkapcsolati menedzser', 'értékesítés-támogatási munkatárs', 'partnerkapcsolati vezető'),
    ('csapatvezető', 'projektasszisztens', 'osztályvezető'),
    ('működési specialista', 'projektmenedzser', 'üzemeltetési vezető'),
    ('beszerzési munkatárs', 'pénzügyi elemző', 'beszerzési vezető'),
    ('termékmenedzser', 'projektkoordinátor', 'termékigazgató'),
    ('értékesítés-támogatási specialista', 'értékesítési képviselő', 'értékesítési vezető'),
    ('CRM felelős', 'marketingautomatizációs munkatárs', 'marketingigazgató'),
    ('piackutató', 'tartalomfelelős', 'stratégiai vezető'),
    ('irodavezető', 'csapatasszisztens', 'cégvezető'),
    ('tartalomfelelős', 'szerkesztő', 'marketingvezető'),
    ('ügyfélsiker-menedzser', 'új csapattag', 'ügyfélszolgálati vezető'),
    ('belső értékesítő', 'ügyféltámogatási munkatárs', 'értékesítési menedzser'),
    ('pénzügyi elemző', 'operációs vezető', 'vezérigazgató'),
    ('toborzó', 'felvételi vezető', 'HR igazgató'),
    ('kisvállalkozó', 'virtuális asszisztens', 'ügyfél'),
    ('induló vállalkozás alapítója', 'termékfejlesztő', 'befektető'),
    ('termékmarketinges', 'értékesítési csapat', 'marketingigazgató'),
    ('webshop tulajdonos', 'hirdetési specialista', 'üzletpartner'),
    ('tanácsadó', 'pénzügyi adminisztrátor', 'ügyfél'),
    ('termékfejlesztő', 'fejlesztő', 'projekt szponzor'),
    ('egyéni vállalkozó', 'asszisztens', 'saját magad'),
    ('üzletfejlesztő', 'projektkoordinátor', 'döntéshozó'),
    ('pályakezdő szakember', 'mentor', 'interjúztató'),
    ('középvezető', 'csapattag', 'közvetlen vezető'),
    ('újrakezdő tanuló', 'elszámoltatható társ', 'jövőbeli éned'),
]

THEORY_EXTRA = [
    'A kulcs az, hogy a feladatot mindig egyértelmű kimenetre fordítod.',
    'A kevesebb, de pontosabb instrukció jellemzően jobb eredményt ad.',
    'A minőséghez két dolog kell: jó feladatleírás és következetes ellenőrzés.',
    'A valós munkában a gyors javítás fontosabb, mint a tökéletes első kör.',
]

CALL_OUTS = [
    '> **Pro tipp:** Kezdés előtt 30 másodpercben írd le pontosan, mi lesz a kész eredmény.',
    '> **Gyakori hiba:** A kérés túl hamar megy ki, és kimarad a formátum vagy a határidő.',
]

READ_MORE = [
    ('OpenAI - Kérésírási útmutató', 'https://platform.openai.com/docs/guides/prompt-engineering'),
    ('Nielsen Norman Group - Felületi szövegírás', 'https://www.nngroup.com/articles/writing-for-ui/'),
    ('NIST - AI kockázatkezelési keretrendszer', 'https://www.nist.gov/itl/ai-risk-management-framework'),
    ('Atlassian - Csapatmunka játékkönyv', 'https://www.atlassian.com/team-playbook'),
]

BIBLIO = [
    ('OpenAI dokumentáció - Útmutatók', 'OpenAI', '2026', 'https://platform.openai.com/docs/guides'),
    ('NIST AI kockázatkezelési keretrendszer', 'NIST', '2023', 'https://www.nist.gov/itl/ai-risk-management-framework'),
    ('Nielsen Norman Group - UX szövegírás', 'NN/g', '2024', 'https://www.nngroup.com/articles/writing-for-ui/'),
    ('Atlassian csapatmunka játékkönyv', 'Atlassian', '2025', 'https://www.atlassian.com/team-playbook'),
]


def load_core() -> list[dict]:
    script_text = PREV_SCRIPT.read_text(encoding='utf-8')
    start = script_text.index('profiles = [') + len('profiles = ')
    end = script_text.index('\n\nif len(profiles)')
    profiles = ast.literal_eval(script_text[start:end])

    src = json.loads(SOURCE_JSON.read_text(encoding='utf-8'))
    titles = [lesson['title'] for lesson in src['lessons']]

    core = []
    for profile, title in zip(profiles, titles):
        profile = dict(profile)
        profile['title'] = title.replace('–', '-').replace('&', 'és')
        for k, v in list(profile.items()):
            if isinstance(v, str):
                profile[k] = localize_hu(v)
        core.append(profile)
    return core


def localize_hu(text: str) -> str:
    replacements = [
        ('prompt-debug', 'kérés-hibakeresés'),
        ('Skill-check', 'Készségmérés'),
        ('skill-check', 'készségmérés'),
        ('Workflow', 'Munkafolyamat'),
        ('workflow', 'munkafolyamat'),
        ('use case', 'használati eset'),
        ('Use case', 'Használati eset'),
        ('landing', 'céloldal'),
        ('Landing', 'Céloldal'),
        ('pitch', 'rövid bemutató'),
        ('Pitch', 'Rövid bemutató'),
        ('scorecard', 'értékelőlap'),
        ('Scorecard', 'Értékelőlap'),
        ('persona', 'vevőprofil'),
        ('Persona', 'Vevőprofil'),
        ('brief', 'feladatleírás'),
        ('Brief', 'Feladatleírás'),
        ('tagelt', 'címkézett'),
        ('Prompt', 'Kérés'),
        ('prompt', 'kérés'),
        ('debug', 'hibakeresés'),
        ('Debug', 'Hibakeresés'),
        ('support', 'ügyféltámogatási'),
        ('Support', 'Ügyféltámogatási'),
    ]

    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def slugify(text: str) -> str:
    text = text.lower().replace('&', 'es').replace('+', ' plusz ')
    text = text.replace('→', ' ').replace('"', ' ').replace('?', ' ')
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ö', 'o').replace('ő', 'o').replace('ú', 'u').replace('ü', 'u').replace('ű', 'u')
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return re.sub(r'-+', '-', text).strip('-')


def opening_paragraph(core: dict, persona: str) -> str:
    line1 = f"{core['scenario']}. Ebben a helyzetben te vagy {persona}, és gyors, de megbízható döntést kell hoznod."
    line2 = f"A mai gyakorlati feladat végére kézben lesz {core['deliverable']}, amit holnap is újra tudsz használni."
    line3 = f"Aha pont: {core['focus']} akkor kezd működni, amikor a kimenetet már induláskor mérhetővé teszed."
    return f"{line1}\n{line2}\n{line3}"


def lesson_markdown(day: int, core: dict, lesson_path: Path) -> str:
    persona, secondary, stakeholder = PERSONAS[day - 1]
    b1 = BIBLIO[(day - 1) % len(BIBLIO)]
    b2 = BIBLIO[(day) % len(BIBLIO)]
    r1 = READ_MORE[(day - 1) % len(READ_MORE)]
    r2 = READ_MORE[(day) % len(READ_MORE)]
    extra = THEORY_EXTRA[(day - 1) % len(THEORY_EXTRA)]
    callout_text = (
        f"> **Pro tipp:** {core['deliverable']} akkor lesz stabil, ha minden futás után ugyanazzal a 3 kérdéssel ellenőrzöd."
        if day % 2 == 1
        else f"> **Gyakori hiba:** {core['risk']} kockázatát sokan csak a végén nézik meg, pedig már a feladatleírásban jelezni kell."
    )

    where_good_1 = f"- {core['scenario'].lower()} típusú helyzetekben, amikor gyors és tiszta döntés kell"
    where_good_2 = f"- amikor {core['deliverable']} több embernek ad át egyértelmű következő lépést"
    where_not = f"- ha {core['risk']} kockázatot nem tudod emberi ellenőrzéssel lefedni"

    touch_1 = f"- {persona} és {secondary} közti napi átadások"
    touch_2 = f"- rövid státuszok és döntés-előkészítő jegyzetek"
    touch_3 = f"- ismétlődő feladatok, ahol {core['metric']} számít"

    use_when_1 = f"- {core['scenario'].lower()} feladattal találkozol, és kevés az idő"
    use_when_2 = f"- {core['deliverable']} alapján több szereplőnek kell azonosan cselekednie"
    late_signal_1 = f"- {core['deliverable']} minden alkalommal újraírásra szorul"
    late_signal_2 = f"- gyakran visszakapod, hogy a tartalom nem kezeli {core['risk']} problémát"

    benefit_1 = f"- gyorsabban elkészül {core['deliverable']}, kevesebb körrel"
    benefit_2 = f"- mérhetőbb lesz a minőség {core['metric']} mutatóval"
    benefit_3 = f"- csökken az utómunka, mert korán kiszűröd {core['risk']} hibát"
    risk_if_skip_1 = f"- nő a félreértések száma {core['scenario'].lower()} helyzetben"
    risk_if_skip_2 = f"- nehezebb tartani {core['metric']} célt"
    expect_improve = f"- Javulni fog: {core['focus']} gyakorlati alkalmazása és az átadható kimenet minősége."
    expect_not = "- Nem garantált: emberi ellenőrzés nélküli tévedhetetlen válasz minden futásban."

    do_1 = f"- Rövid, konkrét feladatleírást adj meg úgy, hogy {core['deliverable']} formátuma már az elején tiszta legyen."
    do_2 = f"- A véglegesítés előtt ellenőrizd, hogy teljesült-e {core['metric']} mérési pont."
    dont_1 = f"- Ne hagyd a háttérben {core['risk']} témát, még akkor sem, ha a válasz elsőre jónak tűnik."
    dont_2 = f"- Ne kérj általános szöveget, ha konkrét döntéshez kell anyag {core['scenario'].lower()} feladathoz."
    mistake_1 = f"- **Hiba:** túl általános kérés indul {core['scenario'].lower()} helyzetre. **Javítás:** nevezd meg az érintettet, a határidőt és a döntési célpontot."
    mistake_2 = f"- **Hiba:** nincs kapcsolat a kimenet és {core['metric']} mérés között. **Javítás:** minden futás végén rögzíts 1 bináris megfelelt/nem felelt meg eredményt."

    guided_input_2 = f"- egy rövid saját minta, ami mutatja, nálatok mi számít jó {core['focus']} kimenetnek"
    guided_input_3 = f"- ellenőrzési lista {core['risk']} kockázat kizárására"
    guided_step_1 = f"1. Írd le 4 sorban a helyzetet, a célt és azt, hogyan fogod mérni {core['metric']} eredményt."
    guided_step_2 = f"2. Készíts kérésmintát {core['deliverable']} előállításához, majd kérj két eltérő változatot."
    guided_step_3 = "3. Hasonlítsd össze a változatokat a táblában, és jelöld, melyik mehet tovább valós használatra."

    independent_task = (
        f"Válassz egy saját, holnapi feladatot, ahol ugyanilyen típusú döntés kell, mint {core['scenario'].lower()} esetben. "
        f"Alkalmazd a mai keretet úgy, hogy a végeredmény ugyanúgy mérhető legyen: {core['metric']}."
    )
    independent_output = (
        f"Egy rövid jegyzet 3 blokkal: helyzet, kérésminták, minőségkapu. "
        f"A végére írj egy mondatot arról, mit változtattál {core['deliverable']} pontosabbá tételéhez."
    )

    self_1 = f"- [ ] {core['deliverable']} elkészült és megosztható."
    self_2 = f"- [ ] {core['metric']} mérési pont rögzítve van."
    self_3 = f"- [ ] {core['risk']} kockázatra külön megelőző lépést futtattál."
    self_4 = f"- [ ] Van egy rövid döntési jegyzeted arról, miért az adott változatot választottad."

    return f"""# Lecke {day}: {core['title']}

**Egy mondatban:** {core['hook']}  
**Idő:** 20-30 perc  
**Kézzelfogható kimenet:** {core['deliverable']}

## Tanulási cél

{opening_paragraph(core, persona)}

A lecke végén képes leszel: **{core['goal']}**

### Sikerkritériumok (megfigyelhető)
- [ ] Elkészült a konkrét napi kimenet: **{core['deliverable']}**.
- [ ] A kimenethez rögzítve van legalább egy mérhető mutató: **{core['metric']}**.
- [ ] A fő kockázat kezelésére van külön ellenőrzési lépés: **{core['risk']}**.

### Kimenet, amit ma elkészítesz
- **Név:** {core['deliverable']}
- **Formátum:** szerkeszthető tábla és rövid döntési jegyzet
- **Hova mented:** `ai-rutin/nap-{day:02d}-{slugify(core['title'])}.md`

## Kinek szól

**Elsődleges szerep:** {persona}  
**Másodlagos szerep:** {secondary}  
**Érintett döntéshozó:** {stakeholder}

## Miről szól

### Mi ez?
Ez a lecke gyakorlatban mutatja meg, hogyan alkalmazd **{core['focus']}** módszert valós munkaszituációban.
A cél nem elmélet, hanem egy olyan kimenet, amit tényleg használhatsz a következő munkanapodon.

### Mi nem ez?
Nem általános AI-bemutató, és nem olyan feladat, amit csak bemutató kedvéért érdemes megcsinálni.

### 2 perces elmélet
- {core['theory']}
- {extra}
- A minőséget itt az adja, hogy {core['deliverable']} ellenőrizhető és megismételhető.

### Kulcsfogalmak
- **Munkakeret:** rövid útmutató, ami leírja a cél, formátum, korlát hármast.
- **Minőségkapu:** gyors ellenőrzés a kimenet elfogadása előtt.

## Hol használod

### Itt működik jól
{where_good_1}
{where_good_2}

### Itt ne ezt használd
{where_not}

### Kapcsolódási pontok
{touch_1}
{touch_2}
{touch_3}

## Mikor használd

### Akkor használd, ha
{use_when_1}
{use_when_2}

### Gyakoriság
Munkanaponként legalább egyszer, visszatérő feladatnál minden alkalommal.

### Későn észlelt jelek
{late_signal_1}
{late_signal_2}

## Miért számít

### Gyakorlati előnyök
{benefit_1}
{benefit_2}
{benefit_3}

### Mi történik, ha kihagyod
{risk_if_skip_1}
{risk_if_skip_2}

### Reális elvárás
{expect_improve}
{expect_not}

## Hogyan csináld

### Lépésről lépésre
1. Pontosan nevezd meg a munkaszituációt és a várt eredményt.
2. Írd le a kötelező korlátokat (időkeret, terjedelem, stílus, tiltások).
3. Kérd ki az első AI-verziót konkrét formátumban.
4. Futtass 3 pontos minőségkaput, külön figyelve **{core['risk']}** kockázatra.
5. Javítsd a kimenetet, majd mentsd le használható sablonként.

### Tedd / Ne tedd
**Tedd**
{do_1}
{do_2}

**Ne tedd**
{dont_1}
{dont_2}

### Gyakori hibák és javításuk
{mistake_1}
{mistake_2}

### Akkor kész, ha
- [ ] Elkészült és lementetted **{core['deliverable']}** kimenetet.
- [ ] Ellenőrizted a kimenetet legalább 3 minőségkritérium szerint.
- [ ] A **{core['metric']}** mutatót dokumentáltad.

## Vezetett gyakorlat (10-15 perc)

### Inputok
- egy valós feladat rövid leírása a következő helyzetről: **{core['scenario']}**
{guided_input_2}
{guided_input_3}

### Lépések
{guided_step_1}
{guided_step_2}
{guided_step_3}

### Várt kimenet formátuma
| Elem | Mit írsz be | Elvárt eredmény |
| --- | --- | --- |
| Helyzet | {core['scenario']} | Minden érintett érti egy olvasásból |
| Kérésváz | Cél + kontextus + formátum + korlát | Minimum 2 használható változat |
| Minőségkapu | Pontosság + kockázat + következő lépés | Egyértelmű javítási döntés |
| Végleges kimenet | {core['deliverable']} | Mentve, újrahasználható sablon |

{callout_text}

## Önálló gyakorlat (5-10 perc)

### Feladat
{independent_task}

### Kimenet
{independent_output}

## Gyors önellenőrzés (igen/nem)

{self_1}
{self_2}
{self_3}
{self_4}

### Kiinduló mérőszám
- **Eredmény:** {core['metric']}
- **Dátum:** 2026-02-11
- **Használt eszköz:** ChatGPT vagy más LLM

## Források

1. **{b1[0]}**. {b1[1]}. {b1[2]}.  
   Olvasd: {b1[3]}
2. **{b2[0]}**. {b2[1]}. {b2[2]}.  
   Olvasd: {b2[3]}

## Továbbolvasás

1. **{r1[0]}**  
   Miért: gyakorlati példákat ad azonnal átvehető mintákkal.  
   Olvasd: {r1[1]}
2. **{r2[0]}**  
   Miért: segít megerősíteni a módszert valós munkaszituációkban.  
   Olvasd: {r2[1]}

<!-- source-lesson-file: {lesson_path} -->
"""


def quiz_questions(day: int, core: dict) -> list[dict]:
    persona, secondary, _ = PERSONAS[day - 1]
    tag = f'day-{day:02d}'

    return [
        {
            'hashtags': [tag, 'application'],
            'question': (
                f"{persona.capitalize()}ként ezt kapod reggel 8:30-kor: {core['scenario']}. "
                f"A határidő 45 perc, és a cél {core['deliverable']} elkészítése. "
                "Mi legyen az első döntésed?"
            ),
            'options': [
                f"Rögzítem a kimenet pontos formátumát ({core['deliverable']}), és mellé a mérési pontot ({core['metric']}), majd erre építem a kérést.",
                f"Rögtön hosszú választ kérek {core['scenario'].lower()} feladatra, formátum és korlát nélkül.",
                f"Csak a stílust adom meg, mert {core['focus']} részleteit majd kitalálja a modell.",
                f"A minőségellenőrzést kihagyom, még akkor is, ha {core['risk']} kockázata ismert.",
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'application',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'application'],
            'question': (
                f"A cél {core['deliverable']} elkészítése, a kockázat pedig {core['risk']}. "
                "Melyik kérésindítás adja a legnagyobb esélyt használható első változatra?"
            ),
            'options': [
                f"Készíts két változatot max 140 szóban, célközönségre szabva, és mindkettő végén mutasd meg, hogyan teljesül {core['metric']} mérés.",
                f"Írj valamit röviden {core['scenario'].lower()} témáról, a formátum és a minőségkapu most nem fontos.",
                f"Adj kreatív választ bármilyen stílusban, és {core['deliverable']} részleteit majd később pontosítjuk.",
                f"Fogalmazd újra szebben a feladatot, de ne kezeljük külön {core['risk']} kockázatát.",
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'application',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'diagnostic'],
            'question': (
                f"A következő visszajelzést kapod ettől a szereplőtől ({secondary}) \"{core['scenario']}\" feladatra: "
                "a kimenet túl általános, és nem lehet belőle azonnal dolgozni. "
                "Melyik javítás a legerősebb következő lépés?"
            ),
            'options': [
                f"Újrafuttatom a kérést konkrét formátummal, célközönséggel, döntési határidővel és {core['deliverable']} elvárt szerkezetével.",
                f"Még egyszer lefuttatom ugyanazt a kérést, mert hátha most véletlenül jobb lesz {core['focus']} eredmény.",
                f"Kiveszem a korlátokat, és csak a sebességre megyek, még ha {core['risk']} esélye nő is.",
                f"Átadom változtatás nélkül, és a mérési pontot ({core['metric']}) sem rögzítem külön.",
            ],
            'correctIndex': 0,
            'difficulty': 'HARD',
            'category': 'Course Specific',
            'questionType': 'diagnostic',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'metric'],
            'question': (
                f"A munkafolyamat javulásának bizonyításához melyik mérés a legalkalmasabb, "
                f"ha a célmutató ez: {core['metric']}?"
            ),
            'options': [
                f"Valós feladaton mérem, hogy ténylegesen teljesült-e {core['metric']} minőségmutató.",
                f"Azt nézem, hogy hosszabb lett-e a szöveg, mint korábban, függetlenül {core['deliverable']} használhatóságától.",
                f"Azt számolom, hányszor futott le a kérés, még akkor is, ha {core['risk']} továbbra is fennáll.",
                f"Csak benyomást kérek a csapattól, de {core['focus']} eredményt adat nélkül értékelem.",
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'metric',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'best-practice'],
            'question': (
                f"Melyik ellenőrzési szokás csökkenti a legjobban ezt a kockázatot: {core['risk']}?"
            ),
            'options': [
                f"Küldés előtt futtatom a 3 pontos minőségkaput: pontosság, {core['risk']} kezelése, következő lépés.",
                f"Csak nyelvhelyességet nézek, {core['deliverable']} tényleges használhatóságát nem ellenőrzöm.",
                f"A modell első válaszát tekintem véglegesnek, akkor is, ha {core['metric']} cél még nem teljesült.",
                f"Minden feladatra ugyanazt a sablont használom, {core['scenario'].lower()} kontextusának figyelmen kívül hagyásával.",
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'best_practice',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'critical-thinking'],
            'question': (
                f"A csapatodban sok az újramunka {core['focus']} témában. "
                "Melyik sorrend adja a legkisebb újramunka-kockázatot?"
            ),
            'options': [
                f"Cél és kimenet-meghatározás ({core['deliverable']}) -> konkrét kérés -> minőségkapu -> javítás és mentés.",
                f"Gyors kérés {core['scenario'].lower()} feladatra -> azonnali küldés -> utólagos átírás, ha gond van.",
                f"Hosszú általános kérés -> több véletlenszerű újrafuttatás -> választás érzésre, {core['metric']} mérés nélkül.",
                f"Sablon bemásolása -> {core['risk']} kockázat kihagyása -> teljes kézi újraírás.",
            ],
            'correctIndex': 0,
            'difficulty': 'HARD',
            'category': 'Course Specific',
            'questionType': 'critical-thinking',
            'isActive': True,
        },
        {
            'hashtags': [tag, 'application'],
            'question': (
                f"Holnaptól napi rutinba építenéd: {core['deliverable']}. "
                "Melyik bevezetési terv a legreálisabb kezdőként?"
            ),
            'options': [
                f"Egy visszatérő feladattal kezdek, fix 20 perces idősávval, és minden futás után ellenőrzöm {core['metric']} mutatót.",
                f"Minden feladatra egyszerre vezetem be, még {core['scenario'].lower()} helyzetben is, mérés és jegyzetelés nélkül.",
                f"Csak akkor használom, ha már gond van, és {core['risk']} kockázatot sem dokumentálom külön.",
                f"Egy hétig csak olvasok a témáról, de {core['deliverable']} elkészítését valós feladaton nem próbálom ki.",
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
    out = [f"# Lecke {day} kvíz: {title}", '', '## Kérdésbank']
    for i, q in enumerate(questions, start=1):
        out.extend([
            '',
            '---',
            f"### {i}. kérdés",
            f"**Question:** {q['question']}",
            f"A) {q['options'][0]}",
            f"B) {q['options'][1]}",
            f"C) {q['options'][2]}",
            f"D) {q['options'][3]}",
            f"**Correct:** {letters[q['correctIndex']]}",
            f"**Question Type:** {q['questionType']}",
            f"**Difficulty:** {q['difficulty']}",
        ])
    return '\n'.join(out) + '\n'


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    QUIZZES_DIR.mkdir(parents=True, exist_ok=True)
    for old in LESSONS_DIR.glob('lesson-*.md'):
        old.unlink()
    for old in QUIZZES_DIR.glob('lesson-*-quiz.md'):
        old.unlink()

    core = load_core()
    if len(core) != 30:
        raise ValueError(f'Expected 30 lesson cores, got {len(core)}')

    src = json.loads(SOURCE_JSON.read_text(encoding='utf-8'))

    lessons = []
    seen_questions = set()

    for day, item in enumerate(core, start=1):
        title = item['title']
        slug = slugify(title)
        lesson_path = LESSONS_DIR / f'lesson-{day:02d}-{slug}.md'
        quiz_path = QUIZZES_DIR / f'lesson-{day:02d}-{slug}-quiz.md'

        lesson_content = lesson_markdown(day, item, lesson_path)
        questions = quiz_questions(day, item)

        for q in questions:
            key = re.sub(r'\s+', ' ', q['question'].strip().lower())
            if key in seen_questions:
                raise ValueError(f'Duplicate question detected: {q["question"]}')
            seen_questions.add(key)

        lesson_path.write_text(lesson_content, encoding='utf-8')
        quiz_path.write_text(quiz_markdown(day, title, questions), encoding='utf-8')

        lessons.append({
            'lessonId': f'AI_30_NAP_DAY_{day:02d}',
            'dayNumber': day,
            'language': 'hu',
            'title': title,
            'content': lesson_path.read_text(encoding='utf-8'),
            'emailSubject': f'AI 30 Nap - {day}. nap: {title}',
            'emailBody': '# {{courseName}}\n\n## {{dayNumber}}. nap: {{lessonTitle}}\n\n{{lessonContent}}\n\n[Olvasd el a teljes leckét ->](http://localhost:3000/courses/AI_30_NAP/day/{{dayNumber}})',
            'quizConfig': {
                'enabled': True,
                'successThreshold': 80,
                'questionCount': 5,
                'poolSize': 7,
                'required': True,
            },
            'unlockConditions': {
                'requirePreviousLesson': day != 1,
                'requireCourseStart': True,
            },
            'pointsReward': 50,
            'xpReward': 25,
            'isActive': True,
            'displayOrder': day,
            'metadata': {
                'estimatedMinutes': 25,
                'focus': item['focus'],
                'sourceLessonFile': str(lesson_path),
                'sourceQuizFile': str(quiz_path),
            },
            'translations': {},
            'quizQuestions': questions,
        })

    course = dict(src['course'])
    course['language'] = 'hu'
    course['description'] = '30 napos AI felzárkóztató kezdőknek és újrakezdőknek. Minden nap önálló, valós munkaszituációra épülő mini-termék.'
    course['durationDays'] = 30
    course['defaultLessonQuizQuestionCount'] = 5
    if isinstance(course.get('metadata'), dict):
        course['metadata']['tags'] = ['ai', 'hatékonyság', 'munkafolyamatok', 'üzlet']

    package = {
        'packageVersion': '2.0',
        'version': '2.0',
        'exportedAt': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'exportedBy': 'codex-hu-premium-rewrite',
        'course': course,
        'lessons': lessons,
        'canonicalSpec': src.get('canonicalSpec'),
        'courseIdea': src.get('courseIdea'),
    }

    payload = json.dumps(package, ensure_ascii=False, indent=2)
    OUT_JSON_PRIMARY.write_text(payload, encoding='utf-8')
    OUT_JSON_ALIAS.write_text(payload, encoding='utf-8')

    print(f'generated_lessons={len(lessons)}')
    print(f'lesson_files={len(list(LESSONS_DIR.glob("lesson-*.md")))}')
    print(f'quiz_files={len(list(QUIZZES_DIR.glob("lesson-*-quiz.md")))}')
    print(str(OUT_JSON_PRIMARY))


if __name__ == '__main__':
    main()
