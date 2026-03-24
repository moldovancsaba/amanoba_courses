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
    ('ügyfélszolgálati koordinátor', 'adatvédelmi felelős', 'csapatvezető'),
    ('junior marketinges', 'értékesítési vezető', 'kulcsügyfél-menedzser'),
    ('projektkoordinátor', 'csapatvezető', 'megrendelői kapcsolattartó'),
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
    ('kisvállalkozó', 'virtuális asszisztens', 'ügyfélkapcsolati tanácsadó'),
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

BANNED_QUIZ = [
    'Egy új gyakorlatot vezetsz be',
    'Gyakorlat (vezetett)',
    'Gyakorlat (önálló)',
    'ebben a leckében',
    'a mai leckében',
    'a kurzusban',
    'ebben a modulban',
]


def slugify(text: str) -> str:
    text = text.lower().replace('&', 'es').replace('+', ' plusz ')
    text = text.replace('→', ' ').replace('"', ' ').replace('?', ' ')
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ö', 'o').replace('ő', 'o').replace('ú', 'u').replace('ü', 'u').replace('ű', 'u')
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return re.sub(r'-+', '-', text).strip('-')


def localize_hu(text: str) -> str:
    replacements = [
        ('prompt-debug', 'kérés-hibakeresés'),
        ('Prompt-debug', 'Kérés-hibakeresés'),
        ('prompt', 'kérés'),
        ('Prompt', 'Kérés'),
        ('workflow', 'munkafolyamat'),
        ('Workflow', 'Munkafolyamat'),
        ('skill-check', 'készségmérés'),
        ('Skill-check', 'Készségmérés'),
        ('landing', 'céloldal'),
        ('Landing', 'Céloldal'),
        ('pitch', 'rövid bemutató'),
        ('Pitch', 'Rövid bemutató'),
        ('scorecard', 'értékelőlap'),
        ('Scorecard', 'Értékelőlap'),
        ('persona', 'vevőprofil'),
        ('Persona', 'Vevőprofil'),
        ('use case', 'használati eset'),
        ('Use case', 'Használati eset'),
        ('support', 'ügyféltámogatási'),
        ('Support', 'Ügyféltámogatási'),
        ('review-val', 'felülvizsgálattal'),
        ('review', 'felülvizsgálat'),
        ('brieftől', 'feladatleírástól'),
        ('brief', 'feladatleírás'),
        ('CTA', 'cselekvési kérés'),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def load_core() -> list[dict]:
    script_text = PREV_SCRIPT.read_text(encoding='utf-8')
    start = script_text.index('profiles = [') + len('profiles = ')
    end = script_text.index('\n\nif len(profiles)')
    profiles = ast.literal_eval(script_text[start:end])

    src = json.loads(SOURCE_JSON.read_text(encoding='utf-8'))
    titles = [lesson['title'] for lesson in src['lessons']]

    core = []
    for profile, title in zip(profiles, titles):
        row = dict(profile)
        row['title'] = title.replace('–', '-').replace('&', 'és')
        for k, v in list(row.items()):
            if isinstance(v, str):
                row[k] = localize_hu(v)
        core.append(row)
    return core


def render_lesson(day: int, core: dict, lesson_path: Path) -> str:
    persona, secondary, stakeholder = PERSONAS[day - 1]
    b1 = BIBLIO[(day - 1) % len(BIBLIO)]
    b2 = BIBLIO[(day) % len(BIBLIO)]
    r1 = READ_MORE[(day - 1) % len(READ_MORE)]
    r2 = READ_MORE[(day) % len(READ_MORE)]
    callout = (
        f"> **Pro tipp:** Ha bizonytalan vagy, előbb készíts ellenőrizhető vázlatot, és csak utána véglegesítsd a kimenetet."
        if day % 2 == 1
        else f"> **Gyakori hiba:** A kimenet gyors, de ellenőrzés nélkül marad. {core['risk'].capitalize()} kockázatát mindig nézd át külön."
    )

    return f"""# Lecke {day}: {core['title']}

**Egy mondatban:** {core['hook']}  
**Idő:** 20-30 perc  
**Kézzelfogható kimenet:** {core['deliverable']}

## Tanulási cél

{core['scenario']}. Ebben a helyzetben te vagy {persona}, és olyan döntést kell hoznod, ami egyszerre gyors és biztonságos.
A mai feladat végére kész lesz egy valóban használható anyag, nem csak egy gyors próbaválasz.
A lecke végén képes leszel: **{core['goal']}**.

### Sikerkritériumok (megfigyelhető)
- [ ] Elkészült a konkrét napi kimenet: **{core['deliverable']}**.
- [ ] A kimenethez rögzítve van legalább egy mérhető mutató: **{core['metric']}**.
- [ ] A fő kockázatra külön ellenőrzési lépés szerepel: **{core['risk']}**.

### Kimenet, amit ma elkészítesz
- **Név:** {core['deliverable']}
- **Formátum:** rövid döntési tábla + 4-6 soros összegzés
- **Hova mented:** `ai-rutin/nap-{day:02d}-{slugify(core['title'])}.md`

## Kinek szól

**Elsődleges szerep:** {persona}  
**Másodlagos szerep:** {secondary}  
**Érintett döntéshozó:** {stakeholder}

## Miről szól

### Mi ez?
Ez a lecke egy gyakorlati döntési keret. Abban segít, hogy gyors helyzetben is lásd, mire jó az AI, és hol kell emberi kontroll.

### Mi nem ez?
Nem elméleti összefoglaló, és nem "egy gombos" megoldás minden problémára.

### 2 perces elmélet
- {core['theory']}
- A jó eredményhez konkrét cél és ellenőrizhető kimenet kell.
- A kockázatos helyzeteknél az AI leginkább előkészítésre való, nem végső döntésre.

### Kulcsfogalmak
- **Kimenet-meghatározás:** pontosan leírod, mit kell átadni.
- **Minőségkapu:** 2-3 gyors kérdés, ami eldönti, küldhető-e az anyag.

## Hol használod

### Itt működik jól
- ismétlődő kommunikációs feladatoknál
- rövid döntés-előkészítő összefoglalóknál

### Itt ne ezt használd
- végső jogi, pénzügyi vagy adatvédelmi döntésnél emberi jóváhagyás nélkül

### Kapcsolódási pontok
- email- és chatválaszok
- státuszjelentések
- meeting utáni teendők

## Mikor használd

### Akkor használd, ha
- kevés idő alatt kell vállalható első változat
- több hasonló feladatot kell egységes minőségben kezelni

### Gyakoriság
Napi szinten, minden visszatérő feladatnál.

### Későn észlelt jelek
- nő az utólagos javítások száma
- gyakori visszajelzés: "ezt nem így értettük"

## Miért számít

### Gyakorlati előnyök
- gyorsabban kapsz használható első változatot
- kevesebb újramunka keletkezik
- tisztább lesz, hol szükséges emberi döntés

### Mi történik, ha kihagyod
- a hibák későn derülnek ki
- nő a félreértés és a kockázat

### Reális elvárás
- Javulni fog: tempó, tisztaság, átadhatóság.
- Nem garantált: hibátlan eredmény emberi ellenőrzés nélkül.

## Hogyan csináld

### Lépésről lépésre
1. Válassz ki 3 valós feladatot a saját munkádból.
2. Írd le mindegyikhez a célt és a kockázatot.
3. Döntsd el: AI-val megoldható, AI-val előkészíthető, vagy emberi döntés.
4. Adj minden feladathoz 1 kötelező ellenőrzési lépést.
5. Röviden indokold, melyik döntés miért született.

### Tedd / Ne tedd
**Tedd**
- Adj konkrét kimeneti formátumot.
- Jelöld ki előre az ellenőrzési pontot.

**Ne tedd**
- Ne tekintsd véglegesnek az első AI-választ.
- Ne hagyd figyelmen kívül a kockázati jeleket.

### Gyakori hibák és javításuk
- **Hiba:** túl általános kérés. **Javítás:** pontosítsd a célt, közönséget és formátumot.
- **Hiba:** kimarad az ellenőrzés. **Javítás:** legyen kötelező minőségkapu minden küldés előtt.

### Akkor kész, ha
- [ ] Elkészült és lementetted **{core['deliverable']}** kimenetet.
- [ ] Minden sorban szerepel legalább 1 kockázat + 1 ellenőrzési pont.
- [ ] A mérési eredményt röviden dokumentáltad: **{core['metric']}**.

## Vezetett gyakorlat (10-15 perc)

### Inputok
- 3 valós feladat a mai munkádból
- 15 perc zavartalan idő
- egy rövid jegyzet a döntési indoklásokhoz

### Lépések
1. Vidd fel a 3 feladatot a táblázatba.
2. Soronként dönts kategóriát, majd adj meg 1 kockázatot.
3. Írd mellé a kötelező ellenőrzést, és válaszd ki a továbbvihető változatot.

### Várt kimenet formátuma
| Feladat | Döntés | Kockázat | Kötelező ellenőrzés |
| --- | --- | --- | --- |
| {core['scenario']} | AI-val előkészíthető | {core['risk']} | Kimenet kézi átnézése küldés előtt |
| Saját feladat 2 | AI-val megoldható | félreérthető hangnem | célközönség szerinti átolvasás |
| Saját feladat 3 | emberi döntés | magas üzleti kockázat | vezetői jóváhagyás |

{callout}

## Önálló gyakorlat (5-10 perc)

### Feladat
Válassz egy holnapi feladatot, és készíts hozzá 1 soros döntési bejegyzést ugyanebben a formátumban.

### Kimenet
1 sor a táblázat mintájára + 2 mondat indoklás arról, miért ezt a kategóriát választottad.

## Gyors önellenőrzés (igen/nem)

- [ ] Van legalább 3 valós feladat a döntési táblában.
- [ ] Minden feladathoz tartozik konkrét kockázat.
- [ ] Minden feladathoz tartozik konkrét ellenőrzés.
- [ ] Legalább 1 helyen külön jelezted az emberi döntés szükségességét.

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
   Miért: gyakorlati mintákat ad gyors, ellenőrizhető kimenetekhez.  
   Olvasd: {r1[1]}
2. **{r2[0]}**  
   Miért: segít tisztábban és félreérthetőség nélkül fogalmazni.  
   Olvasd: {r2[1]}
"""


def quiz_questions(day: int, core: dict) -> list[dict]:
    persona, secondary, _ = PERSONAS[day - 1]
    tag = f'day-{day:02d}'

    q = [
        {
            'hashtags': [tag, 'application'],
            'question': (
                f"{persona.capitalize()}ként 40 perc alatt kell rendbe tenned ezt a feladatot: {core['scenario']}. "
                "Melyik első lépés ad gyors és biztonságos indulást?"
            ),
            'options': [
                f"Először rögzítem a kimenet formátumát ({core['deliverable']}), a mérési pontot ({core['metric']}), és csak ezután kérek AI-változatot.",
                "Azonnal kérek hosszú választ formátum és ellenőrzés nélkül.",
                "Előbb elküldöm az első AI-választ, majd később javítok rajta.",
                "Kihagyom a döntési szempontokat, mert az lassítaná a munkát.",
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
                f"A cél: {core['deliverable']}. A fő kockázat: {core['risk']}. "
                "Melyik kérésindítás ad legjobb esélyt használható első változatra?"
            ),
            'options': [
                "Adj két rövid változatot, jelöld a célközönséget, és írd le a következő konkrét lépést.",
                "Írj valamit erről, a részletek most nem fontosak.",
                "Legyen hosszú és kreatív, de kötött forma nélkül.",
                "A tartalom maradjon általános, majd később pontosítjuk.",
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
                f"{secondary.capitalize()} azt jelzi a \"{core['scenario']}\" feladatnál, hogy a kimenet nem használható, mert túl általános. "
                "Melyik javítás a legerősebb következő lépés?"
            ),
            'options': [
                "Újrafuttatom a kérést konkrét céllal, formátummal és döntési határidővel.",
                "Változtatás nélkül újra elküldöm ugyanazt a szöveget.",
                "Kiveszem a korlátokat, hogy gyorsabban jöjjön válasz.",
                "Átadom így is, majd más javítja később.",
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
                f"Melyik mérés mutatja meg legjobban, hogy a módszer valóban működik, ha ezt követed: {core['metric']}?"
            ),
            'options': [
                "Valós feladaton mérem, hogy teljesült-e a kijelölt minőségi feltétel.",
                "Azt nézem, hosszabb lett-e a szöveg, mint korábban.",
                "A futtatások számát nézem, minőségi ellenőrzés nélkül.",
                "Szubjektív benyomás alapján döntök adat nélkül.",
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
                f"Melyik ellenőrzési rutin csökkenti leghatékonyabban ezt a kockázatot: {core['risk']}?"
            ),
            'options': [
                "Küldés előtt kötelezően végigmegyek a 3 pontos minőségkapun: pontosság, kockázat, következő lépés.",
                "Csak nyelvhelyességet ellenőrzök, a tartalmi kockázatot nem.",
                "Az első AI-választ automatikusan véglegesnek tekintem.",
                "Ugyanazt a sablont használom minden helyzetre kontextus nélkül.",
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
                f"A csapatodban nő az újramunka {core['focus']} témában. "
                "Melyik sorrend adja a legkisebb újramunka-kockázatot?"
            ),
            'options': [
                "Cél és kimenet rögzítése -> konkrét kérés -> minőségkapu -> javítás és mentés.",
                "Gyors kérés -> azonnali küldés -> utólagos javítás.",
                "Általános kérés -> többszöri véletlen újrafuttatás -> választás érzésre.",
                "Sablon bemásolása -> kontextus kihagyása -> teljes kézi újraírás.",
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
                f"Holnaptól rendszeresen használnád ezt a kimenetet: {core['deliverable']}. "
                "Melyik bevezetési terv a legreálisabb kezdőként?"
            ),
            'options': [
                "Egy visszatérő feladaton kezdek, fix idősávval, és minden futás után mérek és jegyzetelek.",
                "Minden feladatra egyszerre vezetem be mérés nélkül.",
                "Csak akkor használom, ha már gond van.",
                "Elméletben felkészülök rá, de valós helyzetben nem próbálom ki.",
            ],
            'correctIndex': 0,
            'difficulty': 'MEDIUM',
            'category': 'Course Specific',
            'questionType': 'application',
            'isActive': True,
        },
    ]
    return q


def quiz_markdown(day: int, title: str, questions: list[dict]) -> str:
    letters = ['A', 'B', 'C', 'D']
    lines = [f"# Lecke {day} kvíz: {title}", '', '## Kérdésbank']
    for i, qu in enumerate(questions, start=1):
        lines.extend([
            '',
            '---',
            f"### {i}. kérdés",
            f"**Question:** {qu['question']}",
            f"A) {qu['options'][0]}",
            f"B) {qu['options'][1]}",
            f"C) {qu['options'][2]}",
            f"D) {qu['options'][3]}",
            f"**Correct:** {letters[qu['correctIndex']]}",
            f"**Question Type:** {qu['questionType']}",
            f"**Difficulty:** {qu['difficulty']}",
        ])
    return '\n'.join(lines) + '\n'


def validate_pair(lesson_text: str, questions: list[dict], all_q: set[str], day: int) -> None:
    required = [
        '## Tanulási cél', '## Kinek szól', '## Miről szól', '## Hol használod', '## Mikor használd',
        '## Miért számít', '## Hogyan csináld', '## Vezetett gyakorlat (10-15 perc)',
        '## Önálló gyakorlat (5-10 perc)', '## Gyors önellenőrzés (igen/nem)', '## Források', '## Továbbolvasás'
    ]
    for token in required:
        if token not in lesson_text:
            raise ValueError(f'Nap {day}: hiányzó lecke-szekció: {token}')

    table_count = len(re.findall(r'\n\|[^\n]+\|\n\|\s*[-:| ]+\|', lesson_text))
    if table_count != 1:
        raise ValueError(f'Nap {day}: táblaszám {table_count}, elvárt 1')

    callouts = lesson_text.count('> **Pro tipp:**') + lesson_text.count('> **Gyakori hiba:**')
    if callouts != 1:
        raise ValueError(f'Nap {day}: callout darabszám {callouts}, elvárt 1')

    if len(questions) != 7:
        raise ValueError(f'Nap {day}: kérdésszám {len(questions)}, elvárt 7')

    app_like = 0
    for i, qu in enumerate(questions, start=1):
        q = qu['question'].strip()
        if len(q) < 40:
            raise ValueError(f'Nap {day} K{i}: kérdés túl rövid')
        for bad in BANNED_QUIZ:
            if bad.lower() in q.lower():
                raise ValueError(f'Nap {day} K{i}: tiltott minta: {bad}')

        if qu.get('questionType') in {'application', 'critical-thinking', 'diagnostic', 'best_practice', 'metric'}:
            app_like += 1
        if qu.get('questionType') == 'recall':
            raise ValueError(f'Nap {day} K{i}: recall nem engedett')

        opts = qu.get('options', [])
        if len(opts) != 4:
            raise ValueError(f'Nap {day} K{i}: opciószám {len(opts)}')
        if qu.get('correctIndex') not in (0, 1, 2, 3):
            raise ValueError(f'Nap {day} K{i}: hibás correctIndex')

        key = re.sub(r'\s+', ' ', q.lower()).strip()
        if key in all_q:
            raise ValueError(f'Nap {day} K{i}: duplikált kérdés globálisan')
        all_q.add(key)

    if app_like < 5:
        raise ValueError(f'Nap {day}: app-like kérdések száma {app_like}, elvárt legalább 5')


def main() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    QUIZZES_DIR.mkdir(parents=True, exist_ok=True)

    for f in LESSONS_DIR.glob('lesson-*.md'):
        f.unlink()
    for f in QUIZZES_DIR.glob('lesson-*-quiz.md'):
        f.unlink()

    core = load_core()
    if len(core) != 30:
        raise ValueError(f'core size invalid: {len(core)}')

    src = json.loads(SOURCE_JSON.read_text(encoding='utf-8'))
    lessons = []
    all_questions: set[str] = set()
    run_lines = ['# Pairwise Build Log', '', '- Mód: 1 lecke -> ellenőrzés -> 1 kvíz -> ellenőrzés', '']

    for day, item in enumerate(core, start=1):
        title = item['title']
        slug = slugify(title)
        lesson_path = LESSONS_DIR / f'lesson-{day:02d}-{slug}.md'
        quiz_path = QUIZZES_DIR / f'lesson-{day:02d}-{slug}-quiz.md'

        lesson_text = render_lesson(day, item, lesson_path)
        questions = quiz_questions(day, item)

        validate_pair(lesson_text, questions, all_questions, day)

        lesson_path.write_text(lesson_text, encoding='utf-8')
        quiz_path.write_text(quiz_markdown(day, title, questions), encoding='utf-8')

        lessons.append({
            'lessonId': f'AI_30_NAP_DAY_{day:02d}',
            'dayNumber': day,
            'language': 'hu',
            'title': title,
            'content': lesson_text,
            'emailSubject': f'AI 30 Nap - {day}. nap: {title}',
            'emailBody': '# {{courseName}}\n\n## {{dayNumber}}. nap: {{lessonTitle}}\n\n{{lessonContent}}\n\n[Olvasd el a teljes leckét ->](http://localhost:3000/courses/AI_30_NAP/day/{{dayNumber}})',
            'quizConfig': {'enabled': True, 'successThreshold': 80, 'questionCount': 5, 'poolSize': 7, 'required': True},
            'unlockConditions': {'requirePreviousLesson': day != 1, 'requireCourseStart': True},
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

        run_lines.append(f'- Nap {day:02d}: PASS (lecke + kvíz)')

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
        'exportedBy': 'codex-pairwise-builder',
        'course': course,
        'lessons': lessons,
        'canonicalSpec': src.get('canonicalSpec'),
        'courseIdea': src.get('courseIdea'),
    }

    payload = json.dumps(package, ensure_ascii=False, indent=2)
    OUT_JSON_PRIMARY.write_text(payload, encoding='utf-8')
    OUT_JSON_ALIAS.write_text(payload, encoding='utf-8')

    (BASE_DIR / 'pairwise-build-log.md').write_text('\n'.join(run_lines) + '\n', encoding='utf-8')

    print(f'generated_lessons={len(lessons)}')
    print(f'lesson_files={len(list(LESSONS_DIR.glob("lesson-*.md")))}')
    print(f'quiz_files={len(list(QUIZZES_DIR.glob("lesson-*-quiz.md")))}')
    print(str(OUT_JSON_PRIMARY))


if __name__ == '__main__':
    main()
