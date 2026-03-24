import json
from datetime import datetime
from pathlib import Path

source_path = Path('/Users/moldovancsaba/Downloads/AI_30_NAP_export_2026-02-11.json')
out_dir = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11')
out_path = out_dir / 'AI_30_NAP_export_2026-02-11_refactored.json'

with source_path.open('r', encoding='utf-8') as f:
    src = json.load(f)

lesson_blueprint = [
    {
        'title': 'Mi az AI valojaban es mire NEM valo?',
        'focus': 'AI szerepenek tisztazasa es biztonsagos keretezese',
        'deliverable': 'Sajat AI hasznalati terkep',
        'goal': 'biztonsagosan elvalasztani az AI-hoz illo es nem illo feladatokat',
        'scenario': 'egy napi munkafolyamat, ahol gyors valasz kell, de adatvedelmi kockazat is van',
        'risk': 'erzlekeny adat bekerul a promptba',
        'metric': '3 feladatbol legalabb 3 helyes kockazati besorolas'
    },
    {
        'title': 'A jo prompt 4 eleme',
        'focus': 'cel, kontextus, korlat, kimenet egyertelmu megadasa',
        'deliverable': '4-elemes prompt sablonlap',
        'goal': 'egyszeru feladatot strukturalt promptra atalakitani',
        'scenario': 'egy ugyfel email valasz elokeszitese idonyomas alatt',
        'risk': 'pontatlan brief miatt altalanos valasz szuletik',
        'metric': '3/3 prompt tartalmazza a 4 kotelezo elemet'
    },
    {
        'title': 'Hogyan kerdezz vissza az AI-tol?',
        'focus': 'pontosito kerdesekkel jobb output kialakitasa',
        'deliverable': 'Visszakerdezo promptlista',
        'goal': 'legalabb 5 pontosito kerdes megfogalmazasa egy feladatra',
        'scenario': 'hianyos megrendeloi briefbol kell hasznalhato tervet kesziteni',
        'risk': 'feltelezesekre epul a valasz',
        'metric': '5 visszakerdezesbol legalabb 4 csokkenti a bizonytalansagot'
    },
    {
        'title': 'Stilus es hang tanitsd meg ugy irni mint te',
        'focus': 'hangnem es stilusmintak atadasa az AI-nak',
        'deliverable': 'Szemelyes hangprofil kartya',
        'goal': 'sajat hangnemhez illeszkedo irasi utasitas keszitese',
        'scenario': 'ugyanazt az uzenetet kulonbozo celkozonsegnek kell megirni',
        'risk': 'tul formalis vagy tul laza hangvetel',
        'metric': '2 variansbol 2 megfelel a celkozonsegnek'
    },
    {
        'title': 'Biztonsag es etika a gyakorlatban',
        'focus': 'adatkezelesi es etikai hatarok beallitasa',
        'deliverable': 'AI biztonsagi ellenorzo lista',
        'goal': 'biztonsagi ellenorzo listat alkalmazni minden prompt elott',
        'scenario': 'ugyfelszolgalati adatokkal dolgozo csapat napi AI hasznalata',
        'risk': 'jogi es bizalmi problema egy rossz adatkezeles miatt',
        'metric': 'ellenorzo lista 100%-ban lefut 3 mintaeseten'
    },
    {
        'title': 'Email percek alatt profi hangon',
        'focus': 'gyors es professzionalis email keszites',
        'deliverable': '3-reszes email prompt csomag',
        'goal': 'kulonbozo helyzetekre konzisztens email valaszokat kesziteni',
        'scenario': 'panasz, ajanlatkeres es emlekezteto uzenet kezelese',
        'risk': 'hosszu es cel nelkuli email',
        'metric': '3 emailbol 3 tartalmaz celt, kovetkezo lepest es hataridot'
    },
    {
        'title': 'Meeting jegyzetbol teendolista',
        'focus': 'jegyzet strukturalt feladatsorra bontasa',
        'deliverable': 'Meeting action log sablon',
        'goal': 'meeting jegyzetbol egyertelmu felelos es hatarido listat kesziteni',
        'scenario': '60 perces meeting utan azonnali kovetes szukseges',
        'risk': 'feladatok felelos nelkul maradnak',
        'metric': 'minden teendohoz tartozik felelos es datum'
    },
    {
        'title': 'Dokumentumok brief vaz osszefoglalo',
        'focus': 'dokumentumokat kulonbozo melysegu kimenette alakitani',
        'deliverable': '3-szintu dokumentum atalakito workflow',
        'goal': 'ugyanabbol forrasbol briefet, vazlatot es rovid osszefoglalot kesziteni',
        'scenario': 'hosszu anyagot kell tobb stakeholdernek atadni',
        'risk': 'fontos reszletek elvesznek',
        'metric': 'mindharom kimenetben benne van az 5 kulcsinformacio'
    },
    {
        'title': 'Tablazat gondolkodas AI-val',
        'focus': 'strukturalt adat gondolkodas tablazatos formatumban',
        'deliverable': 'Dontesi tablazat minta',
        'goal': 'szoveges inputot osszehasonlithato tablazatta alakitani',
        'scenario': '3 beszallito ajanlatat kell osszevetni',
        'risk': 'szempontok keverednek es rossz dontes szuletik',
        'metric': 'legalabb 4 egyezo ertekelesi szempont szerepel'
    },
    {
        'title': 'Ismetles es prompt debug nap',
        'focus': 'gyenge promptok hibakeresese es javitasa',
        'deliverable': 'Prompt hibatar es javitasi terv',
        'goal': 'hibas promptot diagnosztizalni es javitott valtozatot adni',
        'scenario': 'visszateroen gyenge minosegu AI outputok egy csapatban',
        'risk': 'a valodi ok helyett tuneti javitas tortenik',
        'metric': '3 hibas promptbol 3 javitott verzio jobb eredmenyt ad'
    },
    {
        'title': 'Sajat prompt konyvtar letrehozasa',
        'focus': 'ujrahasznalhato prompt gyujtemeny epites',
        'deliverable': 'Prompt konyvtar v1',
        'goal': 'top feladatokra keresheto prompttar osszeallitasa',
        'scenario': 'hetente ugyanazok a feladatok jonnek vissza',
        'risk': 'minden alkalommal nullarol indul a munka',
        'metric': 'legalabb 10 prompt cimkevel es leirassal'
    },
    {
        'title': 'Workflow input feldolgozas output',
        'focus': 'haromlepeses AI workflow tervezes',
        'deliverable': 'Workflow tervlap',
        'goal': 'ismetlodofeladatot input-feldolgozas-output modellben tervezni',
        'scenario': 'bejovo leadek minositese naponta',
        'risk': 'kaotikus, nehezen reprodukalhato folyamat',
        'metric': 'workflow lepesek 100%-a egyertelmu bemenettel es kimenettel'
    },
    {
        'title': 'Hibak hallucinaciok kezelese',
        'focus': 'hallucinacio felismeres es tenyalapu ellenorzes',
        'deliverable': 'Tenyellenorzesi protokoll',
        'goal': 'AI allitasokat forrasalapu ellenorzessel validalni',
        'scenario': 'piaci adatokat tartalmazo osszefoglalo keszitese',
        'risk': 'hibas tenyek kerulnek tovabbitasra',
        'metric': '5 allitasbol legalabb 5 ellenorzott forrassal'
    },
    {
        'title': 'Szemelyes AI asszisztens hang kialakitasa',
        'focus': 'szerepkorre szabott AI instrukcio rendszer kialakitasa',
        'deliverable': 'Asszisztens rendszerprompt',
        'goal': 'allando szerepkoru AI instrukciot letrehozni',
        'scenario': 'tobb feladattipust kell egységes modon kezelni',
        'risk': 'inkonzisztens stilus es minoseg',
        'metric': '4 feladattipusnal konzisztens hangnem'
    },
    {
        'title': 'Ismetles rossz promptbol jo prompt',
        'focus': 'ujrairasi rutin kialakitasa gyenge promptokra',
        'deliverable': 'Prompt ujrairasi checklist',
        'goal': 'rossz promptot legalabb ket iteracioban javitani',
        'scenario': 'rossz briefbol indul egy gyors feladat',
        'risk': 'egy iteracio utan megall a javitas',
        'metric': '2 iteracio utan merheto minosegugras'
    },
    {
        'title': 'Szerephez illesztett AI belepo nap',
        'focus': 'munkakor specifikus AI rutin inditasa',
        'deliverable': 'Szerepkor-specifikus use case lista',
        'goal': 'sajat munkakorhoz illeszkedo 5 AI use case megfogalmazasa',
        'scenario': 'uj csapattag AI rutint epit a sajat szerepere',
        'risk': 'altalanos use case-ek miatt alacsony hatas',
        'metric': '5 use casebol legalabb 4 valos napi problema'
    },
    {
        'title': 'Szerephez illesztett sabloncsomag I',
        'focus': 'napi kommunikacios sablonok keszitese',
        'deliverable': 'Kommunikacios sabloncsomag',
        'goal': 'visszatero kommunikacios helyzetekre sablonokat epiteni',
        'scenario': 'ertekesitesi vagy support csapat gyors valaszai',
        'risk': 'szabalytalan, elt ero minosegu uzenetek',
        'metric': 'legalabb 6 sablon kulonbozo helyzetre'
    },
    {
        'title': 'Szerephez illesztett sabloncsomag II',
        'focus': 'elemzo es donteselokeszito sablonok keszitese',
        'deliverable': 'Elemzo sabloncsomag',
        'goal': 'adat- es donteselokeszito sablonokat tervezni',
        'scenario': 'heti riport keszitese kulonbozo vezetoi szinteknek',
        'risk': 'nem megfelelo melysegu riport',
        'metric': '3 riport formatum mindegyike hasznalhato'
    },
    {
        'title': 'Tipikus csapdak az adott szerepben',
        'focus': 'szerepspecifikus AI hibak megelozese',
        'deliverable': 'Csapda-elleni megelozesi terv',
        'goal': 'tipikus hibakhoz megelozesi lepest rendelni',
        'scenario': 'suru hataridos munkakornyezet',
        'risk': 'ismetlodnek ugyanazok a hibak',
        'metric': 'legalabb 5 hiba-ellenszer par'
    },
    {
        'title': 'Skill check es szintlepes',
        'focus': 'eddigi keszsegek merese valos feladaton',
        'deliverable': 'Egyeni skill scorecard',
        'goal': 'AI munkafolyamat teljesitmenyet merni es fejlesztesi pontot kijelolni',
        'scenario': 'mini projekt teljes folyamat vegrehajtasa',
        'risk': 'pontatlan onertekeles',
        'metric': 'scorecard legalabb 4 dimenzioban kitoltve'
    },
    {
        'title': 'Otletvalidalas AI-val',
        'focus': 'otlet gyors piaci tesztelese',
        'deliverable': 'Otletvalidalasi lap',
        'goal': 'egy otletet feltetelezesekre bontani es tesztelni',
        'scenario': 'uj szolgaltatas otlet gyors eloszurese',
        'risk': 'feltetelezes tenykent kezelese',
        'metric': 'legalabb 3 tesztelheto hipotézis'
    },
    {
        'title': 'Persona es ertekajanlat',
        'focus': 'celkozonseg es ertekajanlat pontositasa',
        'deliverable': 'Persona plusz ertekajanlat kartya',
        'goal': 'egy valos persona es hozza illo ertekajanlat megfogalmazasa',
        'scenario': 'uj termek kommunikacios iranyanak meghatarozasa',
        'risk': 'mindenkinek szolo, gyenge uzenet',
        'metric': 'persona fajdalompont es ajanlat pontosan parositva'
    },
    {
        'title': 'Landing vaz es szoveg',
        'focus': 'konverziora tervezett landing struktura',
        'deliverable': 'Landing page vazlat v1',
        'goal': 'egyszeru landing struktura es masolat keszitese',
        'scenario': 'kampanyinditas gyors hataridovel',
        'risk': 'nem egyertelmu ajanlat es CTA',
        'metric': 'hero, bizonyitek, ajanlat, CTA mind jelen van'
    },
    {
        'title': 'Arazas alapjai',
        'focus': 'ertekalapu arcsomagolas alaplogikaja',
        'deliverable': 'Arazasi opcio tabla',
        'goal': 'minimum 3 arazasi opcio osszehasonlitasa',
        'scenario': 'szolgaltatas piaci bevezetese',
        'risk': 'koltsegbol kepzett, ertek nelkuli ar',
        'metric': 'mindharom opciohoz celvevo es indoklas'
    },
    {
        'title': 'MVP gondolkodas mit NEM csinalunk',
        'focus': 'priorizalas es scope szukites',
        'deliverable': 'MVP dontesi matrix',
        'goal': 'must-have es nice-to-have elemek elvalasztasa',
        'scenario': 'szuk eroforras melletti induloprojekt',
        'risk': 'tulterhelt backlog es csuszas',
        'metric': 'minimum 5 elem priorizalva indoklassal'
    },
    {
        'title': 'Sajat AI rutin kialakitasa',
        'focus': 'napi, heti AI munkaritmus kialakitasa',
        'deliverable': 'Szemelyes AI rutin naptar',
        'goal': 'fenntarthato AI munkarutint tervezni',
        'scenario': 'szetszort AI hasznalat helyett rendszeres gyakorlat',
        'risk': 'ad hoc hasznalat miatt alacsony eredmeny',
        'metric': 'rutin legalabb 5 konkret idosavval'
    },
    {
        'title': '60 masodperces pitch AI-val',
        'focus': 'rovid, eros pitch struktura kialakitasa',
        'deliverable': '60 masodperces pitch script',
        'goal': 'egy mondanivalot 60 masodpercben atadni',
        'scenario': 'networking vagy vezetoi bemutatas',
        'risk': 'szetszort, hosszu pitch',
        'metric': 'pitch 60-75 masodperc kozott marad'
    },
    {
        'title': 'Portfolio szintu kimenetek',
        'focus': 'kurzus outputok bemutathato portfolio elemekke alakitasa',
        'deliverable': 'Portfolio csomag v1',
        'goal': 'korabbi anyagokbol 3 bemutathato portfolio elemet osszerakni',
        'scenario': 'allas- vagy ugyfelszerzes tamogatasa',
        'risk': 'nem bizonyithato eredmenyek',
        'metric': '3 portfolio elemhez merheto eredmeny kapcsolva'
    },
    {
        'title': 'Szemelyes fejlodesi terkep',
        'focus': 'tovabbfejlodesi terv keszitese a kurzus utan',
        'deliverable': '90 napos fejlodesi terv',
        'goal': 'kovetkezo 90 napra tanulasi es gyakorlasi tervet irni',
        'scenario': 'kurzus utani lendulet fenntartasa',
        'risk': 'visszaeses regi munkamodba',
        'metric': 'terv legalabb 12 heti checkpointtal'
    },
    {
        'title': 'Zaras merre tovabb?',
        'focus': 'eredmenyek osszegzese es kovetkezo lepesek kijelolese',
        'deliverable': 'Egyoldalas AI akcioterv',
        'goal': 'konkret kovetkezo lepeseket es meresi pontokat kijelolni',
        'scenario': 'kurzust lezaro onertekeles es celkituzes',
        'risk': 'ismeret marad, gyakorlat nem lesz belole',
        'metric': 'akciotervben 30 napra lebontott feladatok'
    }
]

bibliography = [
    ('OpenAI Usage Policies', 'https://openai.com/policies/usage-policies'),
    ('Google Prompting Guide', 'https://cloud.google.com/discover/what-is-prompt-engineering'),
    ('NIST AI Risk Management Framework', 'https://www.nist.gov/itl/ai-risk-management-framework'),
    ('Atlassian Team Playbook', 'https://www.atlassian.com/team-playbook'),
    ('HubSpot Email Writing', 'https://blog.hubspot.com/sales/sales-email-template'),
    ('NN Group Writing for Interfaces', 'https://www.nngroup.com/articles/writing-for-ui/')
]

read_more = [
    ('OpenAI Guides', 'https://platform.openai.com/docs/guides'),
    ('One Useful Thing', 'https://www.oneusefulthing.org/'),
    ('MindTools Decision Matrix', 'https://www.mindtools.com/ahwn4x6/decision-matrix-analysis')
]


def build_content(day, item):
    b1_name, b1_url = bibliography[day % len(bibliography)]
    b2_name, b2_url = bibliography[(day + 2) % len(bibliography)]
    r1_name, r1_url = read_more[day % len(read_more)]

    return f"""# Lesson {day}: {item['title']}

**One-liner:** A mai lecke segit stabil alapot epiteni a(z) {item['focus']} teruleten.  
**Time:** 20-30 perc  
**Deliverable:** {item['deliverable']}

## Learning goal

You will be able to: **{item['goal']}**

### Success criteria (observable)
- [ ] Egyertelmuen leirod a feladat celt, korlatait es elvart kimenetet.
- [ ] Letrehozol egy hasznalhato deliverable-t a napi temaban.
- [ ] Egy merheto mutatoval ellenorzod a minoseget.

## Who

- Kezdoknek es ujrakezdoknek, akik gyorsan szeretnenek biztos AI rutint.
- Olyan szakembereknek, akiknek fontos a valos munkaban azonnal hasznalhato kimenet.

## What

### What it is

A lecke gyakorlati utmutato a(z) {item['focus']} temaban, valos munkaszituacioval.

### What it is not

Nem elmeleti gyujtemeny es nem altalanos motivacios anyag. Konret outputot keszitunk.

### 2-minute theory

A jo AI workflow akkor stabil, ha a cel, a kontextus, a korlatok es a minosegmeres egyszerre jelenik meg.
A bizonytalansag csokkentheto pontos instrukcioval, ellenorzesi ponttal es iteracioval.

## Where

- Email iras, meeting utankovetes, dokumentum szerkesztes, riportkeszites.
- Olyan folyamatok, ahol gyorsasag mellett pontossag is kell.

## When

- Amikor rovid idon belul hasznalhato elso verziot kell kesziteni.
- Amikor tobbszereplos folyamatban egyertelmu kimenetre van szukseg.

## Why it matters

A(z) {item['focus']} keszseg javitja a fokuszt, csokkenti az ujramunkat, es novelheti a valos eredmenyt.
A meres nelkuli AI hasznalat gyorsnak tunhet, de gyakran minosegromlashoz vezet.

## How

1. Fogalmazd meg a konkret celt es elvart outputot.
2. Irj promptot a valos helyzethez illesztett korlatokkal.
3. Ellenorizd az eredmenyt es javits iteracioval.

### Guided exercise

Feladat: Keszits egy mini workflow-t erre a helyzetre: **{item['scenario']}**.
Hasznald az alabbi tablat, majd futtasd le egy AI eszkozzel.

| Lepes | Mit irsz be az AI-nak | Elvart kimenet |
| --- | --- | --- |
| 1. Cel | 1 mondat a feladat celjarol es kozonsegerol | Egyertelmu feladatdefinicio |
| 2. Korlatozas | Hangnem, hosszusag, adatvedelmi szabalyok | Kontrollalt, biztonsagos valasz |
| 3. Minosegteszt | Ellenorzo kerdesek es meresi kriterium | Javithato, merheto output |

> **Pro tip:** Minden prompt vegen kerj alternativ valtozatot es egy rovid onellenorzo listat.

### Independent exercise

- Keszits egy sajat valtozatot ugyanarra a celra mas kozonseggel.
- Adj meg legalabb 2 uj korlatot, majd hasonlitsd ossze az eredmenyt.
- Rogzitsd, hol javult a minoseg es hol maradt hiba.

### Self-check

- [ ] Elkeszult a(z) {item['deliverable']}.
- [ ] Kezelted ezt a kockazatot: {item['risk']}.
- [ ] Teljesult ez a meres: {item['metric']}.

## Bibliography

- {b1_name}: {b1_url}
- {b2_name}: {b2_url}

## Read more

- {r1_name}: {r1_url}
"""


def build_questions(day, item):
    q = []
    q.append({
        'hashtags': [f'day-{day:02d}', 'application'],
        'question': f"Egy csapattag a kovetkezo helyzetben dolgozik: {item['scenario']}. Mi a legjobb elso lepes, hogy a kimenet merheto legyen?",
        'options': [
            'Egy mondatban rogzitett cel es meresi kriterium megadasa a prompt elejen',
            'Azonnali vegleges szoveg kerese korlatok nelkul',
            'Minel hosszabb hattertortenet kerese strukturalt instrukcio nelkul',
            'A feladatot emberi ellenorzes nelkul automatikusan elkuldeni'
        ],
        'correctIndex': 0,
        'difficulty': 'MEDIUM',
        'category': 'Course Specific',
        'questionType': 'application',
        'isActive': True
    })
    q.append({
        'hashtags': [f'day-{day:02d}', 'prompt'],
        'question': f"Melyik prompt segit jobban a(z) {item['deliverable']} letrehozasaban?",
        'options': [
            f"Keszits egy rovid, strukturalt valaszt a(z) {item['focus']} temaban, 3 pontban, meresi kriteriummal.",
            'Irj valamit gyorsan errol a temarol.',
            'Adj egy hosszu altalanos esszet korlatok nelkul.',
            'Valaszolj ugy, ahogy szerinted jo lesz.'
        ],
        'correctIndex': 0,
        'difficulty': 'MEDIUM',
        'category': 'Course Specific',
        'questionType': 'application',
        'isActive': True
    })
    q.append({
        'hashtags': [f'day-{day:02d}', 'risk'],
        'question': f"Melyik ellenorzes csokkenti a legjobban ezt a kockazatot: {item['risk']}?",
        'options': [
            'Kimenet elotti adatvedelmi es tenyszerusegi checklist futtatasa',
            'A valasz azonnali tovabbitasa ellenorzes nelkul',
            'Csak a valasz hosszanak ellenorzese',
            'Csak helyesirasi javitas, tartalmi validalas nelkul'
        ],
        'correctIndex': 0,
        'difficulty': 'HARD',
        'category': 'Course Specific',
        'questionType': 'best_practice',
        'isActive': True
    })
    q.append({
        'hashtags': [f'day-{day:02d}', 'metric'],
        'question': f"Melyik mutato jelzi a legjobban, hogy a napi deliverable hasznalhato? ({item['metric']})",
        'options': [
            'A meresi kriteriumok teljesulese valos mintafeladaton',
            'Az, hogy gyorsan keszult el a valasz',
            'Az, hogy hosszabb lett a szoveg az elozo verzional',
            'Az, hogy tetszetos formatumot adott az AI'
        ],
        'correctIndex': 0,
        'difficulty': 'MEDIUM',
        'category': 'Course Specific',
        'questionType': 'metric',
        'isActive': True
    })
    q.append({
        'hashtags': [f'day-{day:02d}', 'workflow'],
        'question': f"Melyik sorrend adja a legstabilabb eredmenyt a(z) {item['focus']} feladatban?",
        'options': [
            'Cel es korlatok -> Prompt futtatasa -> Ellenorzes es javitas',
            'Prompt futtatasa -> Cel kitalalasa -> Kuldes',
            'Formatum valasztas -> Kuldes -> Ellenorzes kihagyasa',
            'Veglegesites -> Uj prompt -> Problemaazonositas'
        ],
        'correctIndex': 0,
        'difficulty': 'MEDIUM',
        'category': 'Course Specific',
        'questionType': 'application',
        'isActive': True
    })
    q.append({
        'hashtags': [f'day-{day:02d}', 'diagnostic'],
        'question': f"Egy output tullengzo es nem koveti a celt a(z) {item['scenario']} helyzetben. Mi a legerosebb javitasi lepes?",
        'options': [
            'Prompt ujrairasa konkret kimeneti formatummal es tiltott elemek listajaval',
            'Ugyanaz a prompt ujrafuttatasa tobbszor',
            'A valasz teljes torlese es manualis nullarol ujrairas AI nelkul',
            'Csak a bevezetes atirasaval probalkozni'
        ],
        'correctIndex': 0,
        'difficulty': 'HARD',
        'category': 'Course Specific',
        'questionType': 'diagnostic',
        'isActive': True
    })
    q.append({
        'hashtags': [f'day-{day:02d}', 'critical-thinking'],
        'question': f"Melyik dontes mutatja, hogy a csapat valoban erti a(z) {item['focus']} lenyeget?",
        'options': [
            'A gyorsasag mellett kotelezo minosegkaput es emberi review pontot tart fenn',
            'Csak a sebesseget meri es minden kimenetet automatikusan publikál',
            'Kizarolag az AI-ra hagyja a tenyellenorzest',
            'Minden promptot ugyanolyan sablonnal kezel kontextus nelkul'
        ],
        'correctIndex': 0,
        'difficulty': 'HARD',
        'category': 'Course Specific',
        'questionType': 'critical-thinking',
        'isActive': True
    })
    return q

lessons = []

for i, item in enumerate(lesson_blueprint, start=1):
    lesson_id = f"AI_30_NAP_DAY_{i:02d}"
    content = build_content(i, item)
    quiz_questions = build_questions(i, item)
    lesson = {
        'lessonId': lesson_id,
        'dayNumber': i,
        'language': 'hu',
        'title': item['title'],
        'content': content,
        'emailSubject': f"AI 30 Nap - {i}. nap: {item['title']}",
        'emailBody': "# {{courseName}}\n\n## {{dayNumber}}. nap: {{lessonTitle}}\n\n{{lessonContent}}\n\n[Olvasd el a teljes leckét ->](http://localhost:3000/courses/AI_30_NAP/day/{{dayNumber}})",
        'quizConfig': {
            'enabled': True,
            'successThreshold': 80,
            'questionCount': 5,
            'poolSize': 7,
            'required': True
        },
        'unlockConditions': {
            'requirePreviousLesson': False if i == 1 else True,
            'requireCourseStart': True
        },
        'pointsReward': 50,
        'xpReward': 25,
        'isActive': True,
        'displayOrder': i,
        'metadata': {
            'estimatedMinutes': 25,
            'focus': item['focus']
        },
        'translations': {},
        'quizQuestions': quiz_questions
    }
    lessons.append(lesson)

course = src['course']
course['description'] = '30 napos, gyakorlati AI felzarkoztato kezdoknek es ujrakezdoknek: tematikus, erdekes leckekkel, valos helyzetekre epulo gyakorlatokkal, es merheto fejlodesi pontokkal.'
course['defaultLessonQuizQuestionCount'] = 5
course['metadata']['estimatedHours'] = 12.5
course['metadata']['difficulty'] = 'beginner'

out = {
    'packageVersion': '2.0',
    'version': '2.0',
    'exportedAt': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
    'exportedBy': 'codex-refactor',
    'course': course,
    'lessons': lessons,
    'canonicalSpec': src.get('canonicalSpec'),
    'courseIdea': src.get('courseIdea')
}

with out_path.open('w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(out_path)
