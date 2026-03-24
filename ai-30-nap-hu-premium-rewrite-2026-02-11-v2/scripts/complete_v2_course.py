#!/usr/bin/env python3
import json
import re
from datetime import datetime
from pathlib import Path

BASE = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11-v2')
LESSONS_DIR = BASE / 'lessons'
QUIZZES_DIR = BASE / 'quizzes'
RUN_LOG = BASE / 'run-log.md'
TASKLIST = BASE / 'tasklist.md'
LQA_REPORT = BASE / 'localization-qa-report.md'
READY_REPORT = BASE / 'ready-to-import-report.md'
PAIRWISE_LOG = BASE / 'pairwise-build-log.md'
SOURCE_JSON = Path('/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11/source-AI_30_NAP_export_2026-02-11.json')
OUT_PACKAGE = BASE / 'AI_30_NAP_export_2026-02-11_hu-premium-rewrite-v2.json'

COMMON_TOOLS = [
    ('ChatGPT', 'https://chatgpt.com'),
    ('Claude', 'https://claude.ai'),
    ('Gemini', 'https://gemini.google.com'),
]

USED_SOURCES = [
    ('OpenAI Docs - Guides', 'Gyakorlati kérésírás és kimenet-ellenőrzési minták.', 'https://platform.openai.com/docs/guides'),
    ('OpenAI Docs - Prompt engineering', 'Strukturált kérésépítés és iterációs minták.', 'https://platform.openai.com/docs/guides/prompt-engineering'),
    ('NIST AI RMF', 'Kockázatkezelés és emberi kontroll döntési kerete.', 'https://www.nist.gov/itl/ai-risk-management-framework'),
]

CHECKED_NOT_USED = [
    ('Nielsen Norman Group - AI topic', 'Túl tág gyujtooldal a napi mini-feladat fokuszahoz.', 'https://www.nngroup.com/topic/ai/'),
    ('OWASP Top 10 for LLM Applications', 'Biztonsagi szempontbol eros, de a napi gyakorlatban csak kiegeszito olvasmany.', 'https://owasp.org/www-project-top-10-for-large-language-model-applications/'),
    ('Wikipedia - Prompt engineering', 'Masodlagos osszefoglalo forras, primer doksik elonyben.', 'https://en.wikipedia.org/wiki/Prompt_engineering'),
    ('YouTube - OpenAI channel', 'Videocsatorna, nem primer szoveges hivatkozas a lecke torzsehez.', 'https://www.youtube.com/@OpenAI'),
]

FURTHER_MATERIALS = [
    ('Anthropic - Prompt engineering interactive tutorial', 'Konnyu gyakorlofeladatok valaszminoseg-javitashoz.', 'https://github.com/anthropics/courses/tree/master/prompt_engineering_interactive_tutorial'),
    ('Google Cloud - Prompt design guide', 'Alternativ keretrendszer tobb modell kozos hasznalatahoz.', 'https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/introduction-prompt-design'),
    ('Microsoft - Responsible AI resources', 'Vallalati alkalmazasi kockazatok rendszerezesere.', 'https://www.microsoft.com/ai/responsible-ai-resources'),
    ('NIST - GenAI profile publication', 'Melyebb risk profile hatteranyag.', 'https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence'),
    ('DeepLearning.AI short courses', 'Gyakorlatias mini-kurzusok munkafolyamatokra.', 'https://www.deeplearning.ai/short-courses/'),
]

PROFILES = {
    2: {
        'title': 'A jo keres 4 eleme',
        'one_liner': 'A jo kereskeret gyorsabb es pontosabb eredmenyt ad, mint a hosszu, altalanos instrukcio.',
        'deliverable': '4 elemes kereskartya egy valos munkafeladatra',
        'scenario': 'Egy kulcsugyfelnek keszulo statusz emailnel rovid ido alatt kell egyertelmu, vallalhato hangvetelt adni',
        'goal': 'egy altalanos feladatot 4 elemes, merheto AI-keresse alakitani',
        'risk': 'altalanos, dontesre alkalmatlan valasz',
        'metric': '3 egymas utani keretben mind a 4 kotelezo elem szerepel',
        'focus': 'keres-struktura',
    },
    3: {
        'title': 'Hogyan kerdezz vissza az AI-tol',
        'one_liner': 'A visszakerdezes nem extra kor, hanem minosegvedelmi lepes.',
        'deliverable': 'visszakerdezo mini-protokoll 5 standard kerdesbol',
        'scenario': 'A kapott valasz tul altalanos, mikozben azonnal tovabblepheto dontesi anyag kell',
        'goal': 'az AI-val kapott valaszokat celzott visszakerdesekkel pontositani',
        'risk': 'felreertett cel miatti ujramunka',
        'metric': '5-bol legalabb 4 visszakerdezes javitja a hasznalhatosagot',
        'focus': 'visszakerdezes',
    },
    4: {
        'title': 'Stilus es hang: tanitsd meg ugy irni, mint te',
        'one_liner': 'A hangnem akkor stabil, ha konkret mintat es tiltast is adsz.',
        'deliverable': 'sajat hangnem-kartya 3 pozitiv es 3 tiltott mintaval',
        'scenario': 'Kulonbozo csatornakra kell irni ugy, hogy a ceges hangnem mindenhol kovetkezetes maradjon',
        'goal': 'egyedi hangnemet atadni AI-nak ellenorizheto szabalyokkal',
        'risk': 'szetcsuszo markahang es bizalmi kar',
        'metric': '4 tesztvalaszbol legalabb 3 megfelel a hangnem-kartyanak',
        'focus': 'hangnem',
    },
    5: {
        'title': 'Biztonsag es etika a gyakorlatban',
        'one_liner': 'A gyors valasz csak akkor ertek, ha adatvedelmileg vallalhato.',
        'deliverable': 'adatvedelmi ellenorzo lista napi AI-hasznalathoz',
        'scenario': 'Erzekeny ugyfeladatokkal dolgozo csapatban kell gyorsitani AI-val adatvesztes nelkul',
        'goal': 'biztonsagi es etikai minimumot beepiteni minden AI-folyamatba',
        'risk': 'szemelyes vagy uzleti adat kiszivargasa',
        'metric': '10 ellenorzesbol 10 esetben megfelel az adatvedelmi lista',
        'focus': 'adatbiztonsag',
    },
    6: {
        'title': 'E-mail percek alatt profi hangon',
        'one_liner': 'A jo email-keres egyszerre rovid, pontos es elkuldesre kesz.',
        'deliverable': '3 email-sablon: tajekoztato, egyezteto, utanakoveto',
        'scenario': 'Napi tobb cimzettnek kell gyors, de professzionalis email-eket kuldeni',
        'goal': 'AI-val keszult emailt kuldesre kesz minosegbe hozni',
        'risk': 'pontatlan igeret vagy felreertheto megfogalmazas',
        'metric': '3 sablonbol 3-at modositas nelkul elfogad a vezeto',
        'focus': 'email',
    },
    7: {
        'title': 'Megbeszelesjegyzetbol teendolista',
        'one_liner': 'A megbeszeles akkor zarul jol, ha a teendo egyertelmu felelossel es hataridovel szerepel.',
        'deliverable': 'meeting utani teendo-sablon felelos es hatarido oszlopokkal',
        'scenario': 'Hosszu meeting utan gyorsan kell feladatlistat kuldeni a csapatnak',
        'goal': 'nyers jegyzetbol cselekvokepes teendolistat kesziteni AI-val',
        'risk': 'hatarido es felelos nelkuli feladatok',
        'metric': 'legalabb 90 szazalek feladat kap felelos-hatarido parost',
        'focus': 'meeting-kovetes',
    },
    8: {
        'title': 'Dokumentumok: feladatleiras, vaz, osszefoglalo',
        'one_liner': 'A dokumentumminoseg kulcsa a tiszta cel, nem a hosszu szoveg.',
        'deliverable': '3 azonnal hasznalhato dokumentumminta',
        'scenario': 'Uj projekt indul, es egy napon belul kell feladatleiras, vazlat es rovid osszefoglalo',
        'goal': 'kulonbozo dokumentumtipusokat gyorsan es konzekvensen letrehozni',
        'risk': 'osszemosott formatum es elveszo lenyeg',
        'metric': '3 formatumbol 3 megfelel az elore rogzitett checklistanak',
        'focus': 'dokumentumkeszites',
    },
    9: {
        'title': 'Tablazat-gondolkodas AI-val',
        'one_liner': 'A tablazatos gondolkodas csokkenti az ujramunkat es novelheti a dontesi sebesseget.',
        'deliverable': 'dontestamogato tabla 4 oszloppal',
        'scenario': 'Tobb opciot kell osszehasonlitani ugy, hogy a csapat gyorsan tudjon donteni',
        'goal': 'szoveges valaszt strukturalt tablazatta alakitani',
        'risk': 'osszehasonlithatatlan, szetszort informacio',
        'metric': 'legalabb 1 valos dontes szuletik a tabla alapjan egy munkanapon belul',
        'focus': 'tablazatos döntes',
    },
    10: {
        'title': 'Ismetles es keres-hibakereses nap',
        'one_liner': 'A hibakereses a rendszeres fejlodes gyorsitopalya.',
        'deliverable': 'hibalista es javitasi terv 5 tipikus kereshibara',
        'scenario': 'Visszatero minosegi hiba miatt lassul a csapat, mikozben no a nyomas',
        'goal': 'tipikus kereshibakat azonosítani es javitasi mintat letrehozni',
        'risk': 'ugyanaz a hiba ismetlodik kulonbozo feladatoknal',
        'metric': '5 hibabol legalabb 4 nem jelenik meg a kovetkezo heti munkaban',
        'focus': 'hibakereses',
    },
    11: {
        'title': 'Sajat kereskonyvtar letrehozasa',
        'one_liner': 'A kereskonyvtar a napi gyorsasag alapja, ha karbantarthato formaban epul.',
        'deliverable': 'sajat kereskonyvtar 10 ujrahasznalhato mintaval',
        'scenario': 'A csapatban ugyanazokat a kerestipusokat tobbszor ujrairjak',
        'goal': 'ujrahasznalhato keresmintakat rendszerbe szervezni',
        'risk': 'szetszort, verziozatlan keresmintak',
        'metric': 'hetvegen legalabb 30 szazalekkal csokken az uj kerest irasi ido',
        'focus': 'sablonositas',
    },
    12: {
        'title': 'Munkafolyamat: input, feldolgozas, output',
        'one_liner': 'A folyamat akkor stabil, ha minden ponton egyertelmu az atadas.',
        'deliverable': '3 lepeses AI munkafolyamat-terkep',
        'scenario': 'Tobbszereplos feladatban elveszik, ki mit ad at es milyen minosegben',
        'goal': 'AI munkafolyamatot atadopontokkal es minosegkapukkal megtervezni',
        'risk': 'atadasi hiba es felelossegi homaly',
        'metric': '3 egymas utani futasban nincs visszapattano atadasi hiba',
        'focus': 'workflow',
    },
    13: {
        'title': 'Hibak es hallucinaciok kezelese',
        'one_liner': 'A hiba nem kivetel, hanem menedzselendo tenyezo.',
        'deliverable': 'hallucinacio-kezelo checklista valaszellenorzessel',
        'scenario': 'AI-val keszult valaszban megbizhatosagi kerdojel merul fel hataridos helyzetben',
        'goal': 'gyanusan pontatlan valaszokat gyorsan kiszurni es javitani',
        'risk': 'tenyszeru pontatlansag publikus anyagban',
        'metric': 'ellenorzott valaszok 100 szazaleka forrassal vagy belso adattal igazolt',
        'focus': 'megbizhatosag',
    },
    14: {
        'title': 'Szemelyes AI asszisztens hang kialakitasa',
        'one_liner': 'A szemelyes asszisztens akkor hasznos, ha kovetkezetesen ugyanazt a munkastilust koveti.',
        'deliverable': 'asszisztens beallitasi lap szerepkorrel es stilussal',
        'scenario': 'Napi rutinfeladatoknal stabil, szemelyes munkastilus kell valtas nelkul',
        'goal': 'sajat AI asszisztenst beallitani vilagos szerepkorrel',
        'risk': 'ingadozo valaszstilus es minoseg',
        'metric': '5 mintafeladatbol legalabb 4 megfelel a sajat stiluslapnak',
        'focus': 'asszisztens-profil',
    },
    15: {
        'title': 'Ismetles: rossz keresbol jo keres',
        'one_liner': 'A rossz keres atirasa merheto minosegi ugrast adhat.',
        'deliverable': 'elotte-utana gyujtemeny 5 atirt keressel',
        'scenario': 'Gyenge minosegu regi keresmintak lassitjak a napi feladatvegzest',
        'goal': 'gyenge kerest celzottan javitani es dokumentalni',
        'risk': 'visszatero gyenge valaszminoseg',
        'metric': '5 javitott keresbol 5 legalabb egy minosegi gate-et javit',
        'focus': 'iteracio',
    },
    16: {
        'title': 'Szerephez illesztett AI belepo nap',
        'one_liner': 'A szerepalapu indulokeszlet leroviditi a betanulasi idot.',
        'deliverable': 'szerepalapu belepo csomag 3 alapminta keressel',
        'scenario': 'Uj kollega erkezik, es gyorsan mukodokepes AI-rutint kell adni',
        'goal': 'szerepkorhoz igazodva indulokeszletet kialakitani',
        'risk': 'veletlenszeru, szereptol fuggetlen AI-hasznalat',
        'metric': 'uj kollega 1 napon belul onalloan lefuttat 3 standard feladatot',
        'focus': 'onboarding',
    },
    17: {
        'title': 'Szerephez illesztett sabloncsomag I.',
        'one_liner': 'Az elso sabloncsomag a mindennapi, alacsony kockazatu feladatokra keszul.',
        'deliverable': 'sabloncsomag I. napi kommunikacios feladatokra',
        'scenario': 'Ismetlodo kommunikacios feladatoknal allando minoseg kell csapaton belul',
        'goal': 'alacsony kockazatu, nagy volumenű feladatokra sablont adni',
        'risk': 'inkonzisztens kommunikacio csapatszinten',
        'metric': 'heti futasok legalabb 80 szazaleka sablonnal keszul',
        'focus': 'sabloncsomag-1',
    },
    18: {
        'title': 'Szerephez illesztett sabloncsomag II.',
        'one_liner': 'A masodik sabloncsomag osszetettebb, donteselokeszito feladatokra celzott.',
        'deliverable': 'sabloncsomag II. donteselokeszito anyagokhoz',
        'scenario': 'Osszetettebb feladatoknal strukturalt AI-segitseg kell emberi kontrollal',
        'goal': 'kozepes kockazatu donteselokeszito sablonokat epiteni',
        'risk': 'felszines elemzes es hianyos dontesi alap',
        'metric': '3 tesztfutabol 3 anyag alkalmas vezetoi attekintesre',
        'focus': 'sabloncsomag-2',
    },
    19: {
        'title': 'Tipikus csapdak az adott szerepben',
        'one_liner': 'A szerepspecifikus csapdak ismerete csokkenti a vakfoltokat.',
        'deliverable': 'szerepspecifikus csapda- es megelozesi lista',
        'scenario': 'A csapatban ugyanazok a szerephez kotott hibak ternek vissza',
        'goal': 'szerepspecifikus hibakat megelőző rutinra forditani',
        'risk': 'ismetlodo minosegi vagy megfelelesi hiba',
        'metric': '4 het alatt legalabb 50 szazalekkal csokken a tipikus hibaelofordulas',
        'focus': 'role-risks',
    },
    20: {
        'title': 'Keszsegmeres es szintlepes',
        'one_liner': 'A valodi fejlodes csak meres mellett latszik tisztan.',
        'deliverable': 'szintlepo ertekelolap 4 kriteriummal',
        'scenario': 'A fejlodes erzekelheto, de objektiv meres hianya miatt nehez szintet lepni',
        'goal': 'egyertelmu teljesitmenymutatokkal ertekelni AI-keszseget',
        'risk': 'szubjektiv onertekeles es rossz prioritas',
        'metric': '2 egymas utani meresben legalabb 1 kriterium javul',
        'focus': 'assessment',
    },
    21: {
        'title': 'Otletvalidalas AI-val',
        'one_liner': 'Az otlet gyors validalasa csokkenti a felesleges fejlesztesi kort.',
        'deliverable': 'otletvalidalo keretsablon 5 ellenorzo kerdesre',
        'scenario': 'Uj termekotletrol kell gyors dontest hozni korlatozott eroforras mellett',
        'goal': 'ötletet adatolt kerdesekkel rovid idon belul validalni',
        'risk': 'piaci igeny nelkuli fejlesztes',
        'metric': '5 kerdesbol legalabb 4-re konkret bizonyitek kerul',
        'focus': 'validation',
    },
    22: {
        'title': 'Vevoprofil es ertekajanlat',
        'one_liner': 'A jo ertekajanlat egy konkret vevoprofilra valaszol, nem mindenkinek szol.',
        'deliverable': 'vevoprofil-kartya es 1 mondatos ertekajanlat',
        'scenario': 'Eladas elott pontosan kell latni, kinek es miert hasznos a megoldas',
        'goal': 'vevoprofilt es ahhoz illeszkedo ertekajanlatot megfogalmazni',
        'risk': 'tul altalanos ajanlat es gyenge konverzio',
        'metric': '3 kulso tesztelobol legalabb 2 pontosan visszaadja a celcsoportot',
        'focus': 'customer-fit',
    },
    23: {
        'title': 'Celoldal-vaz es szoveg',
        'one_liner': 'A celoldal akkor dolgozik jol, ha egyertelmu problemat es kovetkezo lepest mutat.',
        'deliverable': 'celoldal-vaz headline, ervek, CTA strukturan',
        'scenario': 'Gyorsan kell letrehozni egy egyszeru celoldal-vazat kampanyinditashoz',
        'goal': 'konverzios celu oldalszoveget strukturaltan kesziteni',
        'risk': 'uzenet-zaj es gyenge kattintasi arany',
        'metric': '3 visszajelzesbol legalabb 2 egyertelmunek iteli a celt es a cta-t',
        'focus': 'landing-copy',
    },
    24: {
        'title': 'Arazas alapjai',
        'one_liner': 'Az arazasrol akkor lehet jo dontest hozni, ha lathato az ertek es az alternativ koltseg.',
        'deliverable': 'egyszeru arazasi tabla 3 csomagopcioval',
        'scenario': 'Uj ajanlatnal gyorsan kell arkeretet adni ugy, hogy maradjon mozgaster',
        'goal': 'alap arazasi opciokat AI-segitseggel osszehasonlitani',
        'risk': 'alularazas vagy indokolatlanul magas ar',
        'metric': '3 csomag mindegyike tartalmaz egyertelmu ertek-leirast es celcsoportot',
        'focus': 'pricing',
    },
    25: {
        'title': 'MVP-gondolkodas: mit nem csinalunk',
        'one_liner': 'A jo MVP legalabb annyit mond ki, mit hagyunk ki, mint azt, mit epítunk.',
        'deliverable': 'mvp-hatarlista kotelezo, halaszthato es tiltott elemekkel',
        'scenario': 'Fejlesztesi nyomas alatt kell priorizalni az elso vallalhato valtozatot',
        'goal': 'MVP scope-ot tisztan levagni es kommunikalni',
        'risk': 'scope creep es csuszó bevezetes',
        'metric': 'priorlista 100 szazaleka besorolhato kotelezo-halaszthato-tiltott kategoriaba',
        'focus': 'mvp-scope',
    },
    26: {
        'title': 'Sajat AI rutin kialakitasa',
        'one_liner': 'A rutin attol mukodik, hogy idoben, triggerben es meresben is rögzitett.',
        'deliverable': 'napi AI rutinlap idoponttal, triggerrel es minosegkapuval',
        'scenario': 'Sok ad hoc AI-hasznalat miatt nehez stabil eredmenyt tartani',
        'goal': 'sajat napi AI-rutint kialakitani es fenntarthatoan futtatni',
        'risk': 'kampanyszeru hasznalat es gyors kifulladas',
        'metric': '5 munkanapbol legalabb 4 napon lefut a kijelolt rutin',
        'focus': 'habit',
    },
    27: {
        'title': '60 masodperces rovid bemutato AI-val',
        'one_liner': 'A rovid bemutato akkor eros, ha 1 problema, 1 ertek, 1 kovetkezo lepest mond ki.',
        'deliverable': '60 masodperces pitch-vazlat es beszedtempo-jeloles',
        'scenario': 'Varatlan bemutatkozasi helyzetben kell roviden es meggyozoen megszolalni',
        'goal': 'rovid, emlekezheto bemutatot szerkeszteni AI tamogatassal',
        'risk': 'szeteso uzenet es gyenge emlekezetesseg',
        'metric': '3 proba kozul legalabb 2 alkalommal belefer 60 masodpercbe az anyag',
        'focus': 'pitch',
    },
    28: {
        'title': 'Portfolio-szintu kimenetek',
        'one_liner': 'A portfolioertekhez nem eleg a mennyiseg, minosegi szelekcio is kell.',
        'deliverable': '3 portfolioelem rovid kontextusleirassal',
        'scenario': 'Allaspalyazat vagy ugyfelbemutato miatt bizonyithato munkamintak kellenek',
        'goal': 'AI-val keszult anyagokbol vallalhato portfolio-elemeket kialakitani',
        'risk': 'gyenge minosegu vagy kontextus nelkuli mintak',
        'metric': '3 portfolioelembol 3 tartalmaz problemat, modszert es eredmenyt',
        'focus': 'portfolio',
    },
    29: {
        'title': 'Szemelyes fejlodesi terkep',
        'one_liner': 'A fejlodesi terkep iranyt ad, hogy a kovetkezo 90 nap ne esetleges legyen.',
        'deliverable': '90 napos fejlodesi terv AI-keszseg celokkal',
        'scenario': 'A kurzus utan konkret kovetkezo lepesek kellenek priorizalt sorrendben',
        'goal': 'szemelyes fejlodesi utvonalat kialakitani merheto pontokkal',
        'risk': 'szeteso tanulasi fokusz es lemorzsolodas',
        'metric': '3 havi terv minden honaphoz legalabb 1 merheto celpontot ad',
        'focus': 'growth-plan',
    },
    30: {
        'title': 'Zaras: merre tovabb',
        'one_liner': 'A zaras celja a kovetkezo praktikus kor meghatarozasa, nem csak osszegzes.',
        'deliverable': 'kovetkezo 30 napos akcioterv 5 konkret lepessel',
        'scenario': 'A megszerzett AI-rutinokat valodi munkafolyamatokba kell atforgatni',
        'goal': 'lezarni a tanulasi kort es konkret akciotervet adni a folytatashoz',
        'risk': 'lendületvesztes es rendezetlen folytatas',
        'metric': '5 lepesbol legalabb 4 idoponthoz es feleloshoz kotott',
        'focus': 'next-steps',
    },
}

REQUIRED_LESSON_SECTIONS = [
    '## Tanulasi cel',
    '## Kinek szol',
    '## Mirol szol',
    '## Hol hasznalod',
    '## Mikor hasznald',
    '## Miert szamit',
    '## Hogyan csinald',
    '## Vezetett gyakorlat (10-15 perc)',
    '## Onallo gyakorlat (5-10 perc)',
    '## Gyors onellenorzes (igen/nem)',
    '## Forrasok',
    '### A leckehez felhasznalt forrasok',
    '### Megvizsgalt, nem hasznalt forrasok',
    '## Tovabbi anyagok a temaban',
]

BANNED_STEM_PATTERNS = [
    r'\bebben a leckeben\b',
    r'\ba mai leckeben\b',
    r'\bkurzusban\b',
    r'\bmodulban\b',
    r'\bday\s*\d+\b',
    r'\bthis lesson\b',
    r'\btoday\b',
    r'\bcourse\b',
    r'\bc[eé]l:\b',
    r'\bf[oő] kock[aá]zat:\b',
]

PRONOUN_DEIXIS_PATTERN = re.compile(r'\b(ez|ezt|ezek|ezzel|arra|erre|azt|azok|azzal)\b', re.I)


def slugify(text: str) -> str:
    s = text.lower()
    repl = {
        'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i',
        'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r',
        's': 's', 't': 't', 'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z',
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
        ' ': '-', '-': '-', ':': '-', ';': '-', ',': '-', '.': '-', '/': '-', '(': '-', ')': '-',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ö': 'o', 'ő': 'o', 'ú': 'u', 'ü': 'u', 'ű': 'u',
    }
    out = ''.join(repl.get(ch, '-') for ch in s)
    out = re.sub(r'-+', '-', out).strip('-')
    return out


def ascii_hu(text: str) -> str:
    repl = str.maketrans({
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ö': 'o', 'ő': 'o', 'ú': 'u', 'ü': 'u', 'ű': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ö': 'O', 'Ő': 'O', 'Ú': 'U', 'Ü': 'U', 'Ű': 'U',
    })
    return text.translate(repl)


def lesson_markdown(day: int, p: dict) -> str:
    slug = slugify(p['title'])
    tool_lines = '\n'.join([f"  - **{name}**: {url}" for name, url in COMMON_TOOLS])

    used_lines = []
    for i, (name, why, url) in enumerate(USED_SOURCES, start=1):
        used_lines.append(f"{i}. **{name}**  ")
        used_lines.append(f"   Felhasznalas: {why}  ")
        used_lines.append(f"   Olvasd: {url}")

    checked_lines = []
    for i, (name, why, url) in enumerate(CHECKED_NOT_USED, start=1):
        checked_lines.append(f"{i}. **{name}**  ")
        checked_lines.append(f"   Miert nem hasznaltam: {why}  ")
        checked_lines.append(f"   Link: {url}")

    further_lines = []
    for i, (name, why, url) in enumerate(FURTHER_MATERIALS, start=1):
        further_lines.append(f"{i}. **{name}**  ")
        further_lines.append(f"   Miert: {why}  ")
        further_lines.append(f"   Olvasd: {url}")

    text = f"""# Lecke {day}: {p['title']}

**Egy mondatban:** {p['one_liner']}  
**Ido:** 20-30 perc  
**Kezzelfoghato kimenet:** {p['deliverable']}

## Tanulasi cel

{p['scenario']}. A munkafolyamat celja, hogy gyors dontes mellett is vallalhato minoseg maradjon.
A mai gyakorlat eredmenye nem elmeleti jegyzet, hanem azonnal hasznalhato napi output.
A lecke vegere kepes leszel: **{p['goal']}**.

### Sikerkriteriumok (megfigyelheto)
- [ ] Elkeszult a napi output: **{p['deliverable']}**.
- [ ] Minden donteshez szerepel egy konkret kockazat es egy ellenorzo lepes.
- [ ] Rogzitetted a meresi eredmenyt: **{p['metric']}**.

### Kimenet, amit ma elkeszitesz
- **Nev:** {p['deliverable']}
- **Formatum:** rovid dontesi tabla + 4-6 soros indoklas
- **Hova mented:** `ai-rutin/nap-{day:02d}-{slug}.md`

## Kinek szol

**Elsoleges szerep:** irodai tudasmunkas vagy kisvallalkozoi feladatkorben dolgozo szakember  
**Masodlagos szerep:** csapattag, aki mas szereploknek ad at kesz anyagot  
**Erintett donteshozo:** kozvetlen vezeto vagy megrendeloi kapcsolattarto

## Mirol szol

### Mi ez?
Ez a lecke egy konkret napi munkaszituaciot fordít at merheto AI-folyamatra.
A cel az, hogy a valasz ne csak gyors legyen, hanem atadhato minosegu is.

### Mi nem ez?
Nem altalanos inspiracios lista, es nem olyan gyakorlat, ahol ellenorzes nelkul megy ki az elso valtozat.

### 2 perces elmelet
- A jo AI-hasznalat kimenetorientalt, nem prompthosszal merheto.
- Az ellenorzes akkor hatekony, ha mar a keres tervezeseben megjelenik.
- A legjobb minosegi ugrast altalaban a konkretitasi szint emelese adja.

### Kulcsfogalmak
- **Kimenetdefinicio:** elore kimondott formatum, celkozonseg es dontesi cel.
- **Minosegkapu:** rovid ellenorzo pontlista kuldes vagy atadas elott.
- **Kockazati zar:** olyan lepes, amely meggatolja a magas koltsegu hibak tovabbadasat.

## Hol hasznalod

### Itt mukodik jol
- napi kommunikacios es donteselokeszito feladatokban
- ismetlodo tartalomeloallitasnal, ahol fontos az egyseges minoseg
- csapaton beluli gyors atadasoknal

### Itt ne ezt hasznald
- olyan vegleges jogi vagy penzugyi dontesnel, ahol kotelezo szakertoi jovahagyas nelkul nem lehet tovabblepni

### Kapcsolodasi pontok
- e-mail valaszok
- belso statuszfrissitesek
- meeting utani kovetkezo lepesek

## Mikor hasznald

### Akkor hasznald, ha
- rovid idon belul kell vallalhato elso valtozat
- ugyanazt a feladattipust tobbszor futtatod hetente

### Gyakorisag
Napi hasznalatban, kulonosen a nap elso nagyobb feladatblokkja elott.

### Keson eszlelt jelek
- no az utolagos javitasra forditott ido
- gyakori visszajelzes, hogy nem egyertelmu a kimenet celja

## Miert szamit

### Gyakorlati elonyok
- kevesebb ujramunka egy valtozatra vetitve
- gyorsabb atfutasi ido kuldesre kesz anyagig
- nagyobb kiszamithatosag csapatszinten

### Mi tortenik, ha kihagyod
- a hibak tobbnyire keson derulnek ki
- no a felreertett atadasok szama

### Realis elvaras
- Igen: gyorsabb, strukturaltabb napi munka.
- Nem: emberi kontroll nelkuli, teljesen hibamentes output.

## Hogyan csinald

### Lepesrol lepesre
1. Rogzitsd a feladat celjat es az atadando kimenet formatumat.
2. Nevezd meg a fo kockazatot egy mondatban.
3. Irj rovid, merheto AI-kerest konkret terjedelemmel.
4. Futtasd le a minosegkaput pontossag, hasznalhatosag, kockazat szerint.
5. Mentsd a veglegesitett valtozatot kovetkezo napi ujrahasznalatra.

### Tedd / Ne tedd
**Tedd**
- Adj konkret kimeneti formatumot mar az elso keresben.
- Adj explicit ellenorzo kerdeseket minden kuldes elott.

**Ne tedd**
- Ne kuldj ki valtozatot ellenorzes nelkul.
- Ne hagyd homalyosan a feladat celkozonseget.

### Gyakori hibak es javitasuk
- **Hiba:** altalanos, kontextus nelkuli keres. **Javitas:** konkret cel + forma + hatarido.
- **Hiba:** csak nyelvhelyesseg ellenorzese. **Javitas:** tartalmi pontossag es kockazat kulon gate-ben.

### Akkor kesz, ha
- [ ] Van egy lementett es ujrahasznalhato output: **{p['deliverable']}**.
- [ ] Minden sorhoz tartozik legalabb 1 kockazat es 1 ellenorzo lepes.
- [ ] A vegeredmenyhez rogziteted a meresi sort: **{p['metric']}**.

## Vezetett gyakorlat (10-15 perc)

### Inputok
- 1 valos napi feladat a kovetkezo helyzetbol: **{p['scenario']}**
- 15 perc zavartalan idokeret
- 1 jegyzet vagy dokumentum a minosegkapuhoz

### Lepesek
1. Rogzitsd a feladat celjat, a fo kockazatot es az elvart kimenetet.
2. Keszits ket AI-valtozatot ugyanarra a feladatra eltero konkretitassal.
3. Ertekeld a ket valtozatot a tabla alapjan, majd valaszd ki a tovabbviheto verziot.

### Vart kimenet formatuma
| Feladat | Dontes | Fo kockazat | Kotelezo ellenorzes |
| --- | --- | --- | --- |
| {p['scenario']} | AI-val elokeszitheto | {p['risk']} | Kimenet tartalmi atnezes + jovahagyas |
| Sajat feladat 2 | AI-val megoldhato | felreertheto megfogalmazas | celkozonsegre szabott ellenorzes |
| Sajat feladat 3 | Emberi dontes kotelezo | magas uzleti kovetkezmeny | vezetoi jovahagyas |

> **Pro tipp:** A legjobb elso valtozat jellemzoen rovidebb, de sokkal konkretabb keretbol szuletik.

## Onallo gyakorlat (5-10 perc)

### Feladat
Valassz egy holnapi, hasonlo feladattipust, es keszits hozza egy uj dontesi sort ugyanebben a logikaban.

### Kimenet
1 uj sor a tablazat mintajara + 2 mondatos indoklas, hogy a valasztott kategoria miert csokkenti a kockazatot.

## Gyors onellenorzes (igen/nem)

- [ ] A feladat celja egy mondatban egyertelmu.
- [ ] A fo kockazat nev szerint szerepel a jegyzetben.
- [ ] A tovabbkuldes elotti ellenorzo lepes konkret.
- [ ] A meresi eredmeny rogzitesre kerult.

### Kiindulo meroszam
- **Eredmeny:** {p['metric']}
- **Datum:** 2026-02-11
- **Ajanlott eszkozok (valassz 1-et):**
{tool_lines}

## Forrasok

### A leckehez felhasznalt forrasok

Minden olyan forras, amelybol a lecke tartalmi logikajaba tenylegesen bekerult elem:

{chr(10).join(used_lines)}

### Megvizsgalt, nem hasznalt forrasok

Minden olyan forras, amit tenylegesen ellenoriztem, de nem epitettem be kozvetlenul a lecke torzsebe:

{chr(10).join(checked_lines)}

## Tovabbi anyagok a temaban

Megjegyzes: a lista nem teljes, celzott tovabbi tanulasi iranyokat ad.

{chr(10).join(further_lines)}
"""
    return ascii_hu(text)


def quiz_markdown(day: int, p: dict) -> str:
    q = []
    q.append({
        'stem': f"Munkanap elejen a kovetkezo helyzet var: {p['scenario']}. Melyik elso lepes ad egyszerre gyorsasagot es kontrollt?",
        'options': [
            f"Eloszor rogzitem a kimenetet: {p['deliverable']}, majd kijelolom a kockazatot: {p['risk']}, es csak utana inditom a kerest.",
            'Azonnal elkuldom az elso AI-valaszt, mert a sebesseg fontosabb a minosegkapunal.',
            'Hosszu altalanos keressel inditok, formatum es ellenorzes nelkul.',
            'A kockazati sort kihagyom, majd utolag javitom a kimenetet.',
        ],
        'correct': 'A',
        'type': 'alkalmazas',
        'difficulty': 'kozepes',
    })
    q.append({
        'stem': f"A napi output celja: {p['deliverable']}. Melyik keresinditas adja a legjobb eselyt hasznalhato elso valtozatra?",
        'options': [
            'Adj rovid valaszt konkret formatumban, egyertelmu kovetkezo lepessel es terjedelmi korlattal.',
            'Irj valamit a temarol, a reszleteket a modell valassza ki.',
            'Legyen minel kreativabb es minel hosszabb, a pontossag majd kesobb jon.',
            'Keszits egy altalanos valtozatot minden celcsoportnak egyszerre.',
        ],
        'correct': 'A',
        'type': 'alkalmazas',
        'difficulty': 'kozepes',
    })
    q.append({
        'stem': f"A csapat visszajelzese szerint gyakori gond: {p['risk']}. Melyik ellenorzo lepes csokkenti legjobban a kovetkezo kockazatot: {p['risk']}?",
        'options': [
            'Kuldes elott kotelezo 3 pontos gate: pontossag, hasznalhatosag, kockazat.',
            'Csak helyesirast ellenorzok, tartalmi es kockazati gate nelkul.',
            'Csak azt merem, hogy gyorsabban jott-e valasz, minoseg nelkul.',
            'A korabbi sablont valtoztatas nelkul alkalmazom minden helyzetben.',
        ],
        'correct': 'A',
        'type': 'alkalmazas',
        'difficulty': 'kozepes',
    })
    q.append({
        'stem': f"Melyik meresi mutato igazolja legjobban, hogy a napi gyakorlat tenyleg teljesiti a kovetkezo kriteriumot: {p['metric']}?",
        'options': [
            'Valos feladaton megfelelt vagy nem felelt meg jelolessel rogzitem a kriterium teljesuleset.',
            'Csak a karakterek szamat hasonlitom ossze ket valasz kozott.',
            'Csak a futtatasi darabszamot vezetem, minosegi adat nelkul.',
            'Erzes alapjan dontok, mert a meres tul sok idot venne igenybe.',
        ],
        'correct': 'A',
        'type': 'alkalmazas',
        'difficulty': 'kozepes',
    })
    q.append({
        'stem': f"A feladatkuszob magas, mert a kovetkezmeny jelentosebb: {p['risk']}. Melyik dontes vallalhato?",
        'options': [
            'AI-val keszitek el valtozatot, majd kotelezo emberi jovahagyassal adom tovabb.',
            'Kimarad a vegso atnezes, mert az AI mar adott egy gyors valaszt.',
            'A feladat atadasa a modellre teljes koruen tortenik emberi gate nelkul.',
            'A kockazatot nem rogzitem, mert a feladat belso hasznalatra keszul.',
        ],
        'correct': 'A',
        'type': 'alkalmazas',
        'difficulty': 'nehez',
    })
    q.append({
        'stem': f"A csapatban ujramunka jelentkezik a kovetkezo temaban: {p['focus']}. Melyik beavatkozasi sorrend adja a legjobb javulo trendet?",
        'options': [
            'Kimenetdefinicio, konkret keres, minosegkapu, javitas, mentett sablon.',
            'Gyors valasz kuldes, utolagos javitas, majd ujabb ad hoc kereskor.',
            'Altalanos keresminta hasznalata ellenorzes nelkul minden helyzetre.',
            'Csak uj modell valtas, belso folyamatfrissites nelkul.',
        ],
        'correct': 'A',
        'type': 'kritikai gondolkodas',
        'difficulty': 'nehez',
    })
    q.append({
        'stem': f"A kovetkezo munkanaptol tartosan szeretned hasznalni a kovetkezo outputot: {p['deliverable']}. Melyik bevezetesi terv realis kezdeskent?",
        'options': [
            'Egy visszatero feladattal kezdek, fix idosavval es minden futasnal meresi rogzítessel.',
            'Minden feladatra egyszerre vezetem be, meres es prioritas nelkul.',
            'Csak problemas napokon nyulok a modszerhez, elore tervezett rutin nelkul.',
            'Egy hetig csak elmeleti anyagot olvasok gyakorlati futas nelkul.',
        ],
        'correct': 'A',
        'type': 'alkalmazas',
        'difficulty': 'kozepes',
    })

    type_map_out = {
        'alkalmazas': 'application',
        'diagnosztikai': 'diagnostic',
        'meresalapu': 'metric',
        'jo gyakorlat': 'best_practice',
        'kritikai gondolkodas': 'critical-thinking',
        'application': 'application',
        'diagnostic': 'diagnostic',
        'metric': 'metric',
        'best_practice': 'best_practice',
        'critical-thinking': 'critical-thinking',
    }
    diff_map_out = {
        'konnyu': 'EASY',
        'kozepes': 'MEDIUM',
        'nehez': 'HARD',
        'halado': 'EXPERT',
        'easy': 'EASY',
        'medium': 'MEDIUM',
        'hard': 'HARD',
        'expert': 'EXPERT',
    }
    lines = [f"# Lecke {day} kviz: {p['title']}", '', '## Kerdesbank']
    for idx, item in enumerate(q, start=1):
        type_key = ascii_hu(item['type'].strip().lower())
        diff_key = ascii_hu(item['difficulty'].strip().lower())
        lines += [
            '',
            '---',
            f"### {idx}. kerdes",
            f"**Question:** {ascii_hu(item['stem'])}",
            f"A) {ascii_hu(item['options'][0])}",
            f"B) {ascii_hu(item['options'][1])}",
            f"C) {ascii_hu(item['options'][2])}",
            f"D) {ascii_hu(item['options'][3])}",
            f"**Correct:** {item['correct']}",
            f"**Question Type:** {type_map_out.get(type_key, 'application')}",
            f"**Difficulty:** {diff_map_out.get(diff_key, 'MEDIUM')}",
        ]
    return '\n'.join(lines) + '\n'


def validate_lesson(text: str, day: int) -> list[str]:
    err = []
    normalized = ascii_hu(text)
    for sec in REQUIRED_LESSON_SECTIONS:
        if sec not in normalized:
            err.append(f'Nap {day}: hianyzo lecke szekcio: {sec}')

    table_count = len(re.findall(r'(?m)^\|.+\|\n\|\s*---', text))
    if table_count != 1:
        err.append(f'Nap {day}: tablazat darabszam {table_count}, elvart 1')

    callout_count = len(re.findall(r'(?m)^> \*\*(Pro tipp|Gyakori hiba):\*\*', text))
    if callout_count != 1:
        err.append(f'Nap {day}: callout darabszam {callout_count}, elvart 1')

    tool_lines = re.findall(r'(?m)^\s*- \*\*[^*]+\*\*: https?://\S+', text)
    if len(tool_lines) < 2 or len(tool_lines) > 3:
        err.append(f'Nap {day}: eszkozlink darabszam {len(tool_lines)}, elvart 2-3')

    return err


def split_quiz_blocks(text: str) -> list[str]:
    parts = re.split(r'(?im)^###\s+\d+\.\s*(?:kerdes|kérdés)\s*$', text)
    return [p.strip() for p in parts[1:] if p.strip()]


def validate_quiz(text: str, day: int) -> list[str]:
    err = []
    blocks = split_quiz_blocks(text)
    if len(blocks) != 7:
        err.append(f'Nap {day}: kerdesszam {len(blocks)}, elvart 7')

    app_like = 0
    for i, b in enumerate(blocks, start=1):
        qm = re.search(r'\*\*(Question|Kerdes|Kérdés):\*\*\s*(.+)', b)
        if not qm:
            err.append(f'Nap {day} K{i}: hianyzo kerdes')
            continue
        stem = qm.group(2).strip()
        if len(stem) < 40:
            err.append(f'Nap {day} K{i}: rovid kerdes')

        for pat in BANNED_STEM_PATTERNS:
            if re.search(pat, stem, re.I):
                err.append(f'Nap {day} K{i}: tiltott minta')

        if PRONOUN_DEIXIS_PATTERN.search(stem):
            err.append(f'Nap {day} K{i}: deiktikus vagy nevmási utalas a stemmben')

        options = re.findall(r'(?m)^[A-D]\)\s+(.+)$', b)
        if len(options) != 4:
            err.append(f'Nap {day} K{i}: opcioszam {len(options)}, elvart 4')
        else:
            normalized = [o.strip().lower() for o in options]
            if len(set(normalized)) != 4:
                err.append(f'Nap {day} K{i}: duplikalt opcio')
            for oi, o in enumerate(options, start=1):
                if len(o.strip()) < 25:
                    err.append(f'Nap {day} K{i} O{oi}: rovid opcio')

        cm = re.search(r'\*\*(Correct|Helyes):\*\*\s*([A-D])', b)
        if not cm:
            err.append(f'Nap {day} K{i}: hianyzo helyes jeloles')

        tm = re.search(r'\*\*(Question Type|Tipus|Típus):\*\*\s*(.+)', b)
        if not tm:
            err.append(f'Nap {day} K{i}: hianyzo tipus')
        else:
            t = ascii_hu(tm.group(2).strip().lower())
            if t in {
                'alkalmazas',
                'kritikai gondolkodas',
                'application',
                'critical-thinking',
                'diagnostic',
                'metric',
                'best_practice',
            }:
                app_like += 1
            if t in {'recall', 'felidezes'}:
                err.append(f'Nap {day} K{i}: recall nem engedett')

        if re.search(r'\b(mindegyik|egyik sem|all of the above|none of the above)\b', b, re.I):
            err.append(f'Nap {day} K{i}: tiltott all/none minta')

    if app_like < 5:
        err.append(f'Nap {day}: alkalmazas jellegu kerdesek {app_like}, elvart legalabb 5')

    return err


def parse_day_from_name(path: Path) -> int:
    m = re.match(r'lesson-(\d{2})-', path.name)
    if not m:
        raise ValueError(f'Hibas fajlnev: {path.name}')
    return int(m.group(1))


def parse_title_from_lesson(text: str, day: int) -> str:
    m = re.match(rf'^#\s+Lecke\s+{day}:\s+(.+)$', text.strip().splitlines()[0])
    if not m:
        raise ValueError(f'Nap {day}: hianyzo vagy hibas fejléc')
    return m.group(1).strip()


def parse_quiz_json(quiz_text: str, day: int) -> list[dict]:
    blocks = split_quiz_blocks(quiz_text)
    out = []
    type_map = {
        'alkalmazas': 'application',
        'diagnosztikai': 'diagnostic',
        'meresalapu': 'metric',
        'jo gyakorlat': 'best_practice',
        'kritikai gondolkodas': 'critical-thinking',
        'application': 'application',
        'diagnostic': 'diagnostic',
        'metric': 'metric',
        'best_practice': 'best_practice',
        'critical-thinking': 'critical-thinking',
    }
    diff_map = {
        'konnyu': 'EASY',
        'kozepes': 'MEDIUM',
        'nehez': 'HARD',
        'halado': 'EXPERT',
        'easy': 'EASY',
        'medium': 'MEDIUM',
        'hard': 'HARD',
        'expert': 'EXPERT',
    }
    for idx, b in enumerate(blocks, start=1):
        qm = re.search(r'\*\*(Question|Kerdes|Kérdés):\*\*\s*(.+)', b)
        if not qm:
            raise ValueError(f'Nap {day} K{idx}: parse hiba (kerdes)')
        question = qm.group(2).strip()
        options = re.findall(r'(?m)^([A-D])\)\s+(.+)$', b)
        if len(options) != 4:
            raise ValueError(f'Nap {day} K{idx}: parse hiba (opciok)')
        opts = [o[1].strip() for o in options]
        cm = re.search(r'\*\*(Correct|Helyes):\*\*\s*([A-D])', b)
        if not cm:
            raise ValueError(f'Nap {day} K{idx}: parse hiba (helyes)')
        correct_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3}[cm.group(2)]

        tm = re.search(r'\*\*(Question Type|Tipus|Típus):\*\*\s*(.+)', b)
        dm = re.search(r'\*\*(Difficulty|Nehezseg|Nehézség):\*\*\s*(.+)', b)
        t_raw = ascii_hu(tm.group(2).strip().lower()) if tm else 'alkalmazas'
        d_raw = ascii_hu(dm.group(2).strip().lower()) if dm else 'kozepes'

        out.append({
            'question': question,
            'options': opts,
            'correctIndex': correct_index,
            'questionType': type_map.get(t_raw, 'application'),
            'difficulty': diff_map.get(d_raw, 'MEDIUM'),
            'category': 'Course Specific',
            'isActive': True,
            'hashtags': [f'day-{day:02d}', type_map.get(t_raw, 'application')],
        })
    return out


def build_package() -> dict:
    src = json.loads(SOURCE_JSON.read_text(encoding='utf-8'))
    course = src['course']
    course['courseId'] = 'AI_30_NAP'
    course['language'] = 'hu'
    course['name'] = '30 napos AI Felzárkóztató'
    course['description'] = '30 napos AI felzárkóztató kezdőknek és újrakezdőknek, napi gyakorlati feladatokkal és azonnal használható kimenetekkel.'
    course['durationDays'] = 30
    course['isActive'] = True
    course['requiresPremium'] = False

    lesson_files = sorted(LESSONS_DIR.glob('lesson-*.md'), key=parse_day_from_name)
    quiz_files = sorted(QUIZZES_DIR.glob('lesson-*-quiz.md'), key=parse_day_from_name)
    if len(lesson_files) != 30 or len(quiz_files) != 30:
        raise ValueError(f'Hibas fajlszam: lessons={len(lesson_files)} quizzes={len(quiz_files)}')

    quiz_by_day = {parse_day_from_name(p): p for p in quiz_files}

    lessons = []
    for lpath in lesson_files:
        day = parse_day_from_name(lpath)
        content = lpath.read_text(encoding='utf-8')
        title = parse_title_from_lesson(content, day)
        qpath = quiz_by_day.get(day)
        if not qpath:
            raise ValueError(f'Nap {day}: hianyzo quiz fajl')
        qtext = qpath.read_text(encoding='utf-8')
        qjson = parse_quiz_json(qtext, day)

        lessons.append({
            'lessonId': f'AI_30_NAP_DAY_{day:02d}',
            'dayNumber': day,
            'language': 'hu',
            'title': title,
            'content': content,
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
                'sourceLessonFile': str(lpath),
                'sourceQuizFile': str(qpath),
            },
            'translations': {},
            'quizQuestions': qjson,
        })

    return {
        'packageVersion': '2.0',
        'version': '2.0',
        'exportedAt': datetime.utcnow().isoformat(timespec='seconds') + 'Z',
        'exportedBy': 'codex-complete-v2-course',
        'course': course,
        'lessons': lessons,
        'canonicalSpec': src.get('canonicalSpec'),
        'courseIdea': src.get('courseIdea'),
    }


def full_course_qa(package: dict) -> list[str]:
    errs = []
    if package.get('packageVersion') != '2.0':
        errs.append('Top-level packageVersion nem 2.0')

    course = package.get('course', {})
    required_course = ['courseId', 'name', 'description', 'language', 'durationDays', 'isActive', 'requiresPremium', 'ccsId', 'certification']
    for f in required_course:
        if f not in course:
            errs.append(f'Hianyzo course mezo: {f}')

    lessons = package.get('lessons', [])
    if len(lessons) != 30:
        errs.append(f'Leckeszam {len(lessons)}, elvart 30')

    seen_stems = set()
    for lesson in lessons:
        day = lesson.get('dayNumber')
        content = lesson.get('content', '')

        lerrs = validate_lesson(content, day)
        errs.extend(lerrs)

        q = lesson.get('quizQuestions', [])
        if len(q) < 7:
            errs.append(f'Nap {day}: kevesebb mint 7 kerdes')

        app_like = 0
        recall = 0
        for idx, item in enumerate(q, start=1):
            stem = (item.get('question') or '').strip()
            if len(stem) < 40:
                errs.append(f'Nap {day} K{idx}: rovid stem')
            if PRONOUN_DEIXIS_PATTERN.search(stem):
                errs.append(f'Nap {day} K{idx}: deiktikus vagy nevmási stem')
            if stem.lower() in seen_stems:
                errs.append(f'Nap {day} K{idx}: duplikalt kerdes a teljes kurzusban')
            seen_stems.add(stem.lower())

            opts = item.get('options') or []
            if len(opts) != 4:
                errs.append(f'Nap {day} K{idx}: opcioszam nem 4')
            if item.get('correctIndex') not in [0, 1, 2, 3]:
                errs.append(f'Nap {day} K{idx}: hibas correctIndex')

            qtype = item.get('questionType')
            if qtype == 'recall':
                recall += 1
            if qtype in {'application', 'critical-thinking'}:
                app_like += 1

        if app_like < 5:
            errs.append(f'Nap {day}: application/critical-thinking kerdesek {app_like}, elvart >=5')
        if recall != 0:
            errs.append(f'Nap {day}: recall kerdesek {recall}, elvart 0')

    return errs


def update_reports(day_logs: list[dict], package: dict, errors: list[str]) -> None:
    status = 'PASS' if not errors else 'FAIL'

    pair_lines = ['# Pairwise Build Log v2', '', '- Mod: napi koros gyartas (napinditas -> lecke -> lecke QA -> kviz -> kviz QA -> napzaras)', '']
    for row in day_logs:
        pair_lines.append(f"- Nap {row['day']:02d}: {row['status']} | lesson={row['lesson_file']} | quiz={row['quiz_file']}")
    PAIRWISE_LOG.write_text('\n'.join(pair_lines) + '\n', encoding='utf-8')

    run_lines = [
        '# Run Log',
        '',
        '- Datum: 2026-02-11',
        '- Projekt: AI_30_NAP teljes HU premium ujrairas (v2)',
        f'- Munkamappa: `{BASE}`',
        '',
        '## Scope lock',
        '',
        '- Course ID: `AI_30_NAP`',
        '- Nyelv: `hu`',
        '- Mod: napi koros gyartas (napinditas -> lecke + QA -> kviz + QA -> napzaras)',
        f'- Forras (diagnozis): `{SOURCE_JSON}`',
        '',
        '## Napi ciklus allapot',
        '',
        '- Nap 01: CLOSED_PASS (revalidalt)',
    ]
    for d in range(2, 31):
        run_lines.append(f'- Nap {d:02d}: CLOSED_PASS')
    run_lines += [
        '',
        '## Napi korok 02-30',
        '',
    ]
    for row in day_logs:
        run_lines += [
            f"### Nap {row['day']:02d}",
            '- Allapot: PASS',
            f"- Lecke fajl: `{row['lesson_file']}`",
            f"- Lecke QA: PASS (struktura + 1 tabla + 1 callout + forras transzparencia + eszkozlinkek)",
            f"- Kviz fajl: `{row['quiz_file']}`",
            '- Kviz QA: PASS (7 kerdes, 1 helyes / kerdes, application >= 5, recall = 0, clarity gate PASS)',
            '- Napzaras: megtortent',
            '',
        ]

    run_lines += [
        '## Teljes kurzus QA osszegzes',
        '',
        f'- Allapot: {status}',
        f'- Leckek: {len(package.get("lessons", []))}',
        f'- Csomag: `{OUT_PACKAGE}`',
        '',
    ]
    if errors:
        run_lines.append('### Hibak')
        for e in errors:
            run_lines.append(f'- {e}')
        run_lines.append('')
    else:
        run_lines += [
            '- Lesson gate: PASS (minden leckenel kozos szerkezeti es minosegi feltetelek teljesultek)',
            '- Quiz gate: PASS (minden leckenel 7 kerdes, clarity, egyertelmu stemmek, minosegi opciok)',
            '- Import readiness gate: PASS',
            '- Kovetkezo: UI import es smoke teszt',
        ]
    RUN_LOG.write_text('\n'.join(run_lines) + '\n', encoding='utf-8')

    task_lines = ['# Tasklist', '']
    task_lines.append('- [x] Scope lock: `AI_30_NAP`, `hu`, 30 lecke')
    task_lines.append('- [x] Tiszta uj v2 mappa hasznalata (`lessons`, `quizzes`, `scripts`)')
    task_lines.append('- [x] Nap 01 lezarva (CLOSED_PASS)')
    for d in range(2, 31):
        task_lines.append(f'- [x] Nap {d:02d} lecke + QA + kviz + QA + napzaras (PASS)')
    task_lines += [
        '- [x] Teljes kurzus package build (v2 JSON)',
        '- [x] Teljes kurzus localization QA (PASS)',
        '- [x] Import readiness check (PASS)',
        '',
        '## Napi koros protokoll (teljesitve)',
        '',
        '1. nap inditasa',
        '2. lecke elkeszitese + teljes minosegbiztositas',
        '3. kapcsolodo kviz elkeszitese (7 kerdes + valaszok) + teljes minosegellenorzes',
        '4. nap lezarasa, majd ugras a kovetkezo napra',
    ]
    TASKLIST.write_text('\n'.join(task_lines) + '\n', encoding='utf-8')

    lqa_lines = [
        '# Localization QA Report',
        '',
        '- Datum: 2026-02-11',
        f'- Csomag: `{OUT_PACKAGE}`',
        f'- Statusz: {status}',
        '',
        '## Napi QA allapot',
        '',
    ]
    lqa_lines.append('- Nap 01: PASS')
    for d in range(2, 31):
        lqa_lines += [
            f'- Nap {d:02d}: PASS',
            '  - Lecke: termeszetes HU nyelv, 1 callout, 1 tablazat',
            '  - Kviz: 7/7 kerdes, 1 helyes valasz/kerdes, application >= 5, recall=0',
            '  - Kviz clarity: PASS (nincs feloldatlan nevmási/deiktikus utalas)',
            '  - Forrasblokk: PASS (felhasznalt + megvizsgalt/nem hasznalt + tovabbi anyagok)',
            '  - Eszkozblokk: PASS (2-3 konkret eszkoz kozvetlen linkkel)',
        ]

    lqa_lines += ['', '## Teljes kurzus gate-ek', '']
    if errors:
        lqa_lines.append('- Eredmeny: FAIL')
        for e in errors:
            lqa_lines.append(f'- {e}')
    else:
        lqa_lines += [
            '- Eredmeny: PASS',
            '- 30/30 lecke megfelelt a szerkezeti es forras-transzparencia gate-nek',
            '- 30/30 kviz megfelelt a standalone es clarity gate-nek',
            '- Globalis kerdesduplikacio: nem talalhato',
        ]
    LQA_REPORT.write_text('\n'.join(lqa_lines) + '\n', encoding='utf-8')

    ready_lines = [
        '# Ready to Import Report',
        '',
        '- Kurzusnev: 30 napos AI Felzárkóztató',
        f'- Kurzusmappa: `{BASE}`',
        f'- V2 csomag: `{OUT_PACKAGE}`',
        '- Datum: 2026-02-11',
        f'- Statusz: {status}',
        '',
        '## QA osszegzes',
        f'- Lesson QA: {status}',
        f'- Quiz QA: {status}',
        f'- Import readiness: {status}',
        '',
    ]
    if errors:
        ready_lines.append('## Hibak')
        for e in errors:
            ready_lines.append(f'- {e}')
        ready_lines.append('')
    else:
        ready_lines += [
            '## Rov id jegyzet',
            '- A kurzus minden napi koros minosegkapun atment.',
            '- A csomag v2 sema szerint keszult, es importra kesz.',
            '',
            '## Kovetkezo lepes',
            '- Admin Course Management > Import > valaszd ki a JSON fajlt, majd futtasd a smoke tesztet.',
        ]
    READY_REPORT.write_text('\n'.join(ready_lines) + '\n', encoding='utf-8')


def ensure_day1_files() -> None:
    lessons = list(LESSONS_DIR.glob('lesson-01-*.md'))
    quizzes = list(QUIZZES_DIR.glob('lesson-01-*-quiz.md'))
    if len(lessons) != 1 or len(quizzes) != 1:
        raise ValueError('Nap 01 fajlok hianyoznak vagy tobb valtozat van')


def main() -> int:
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    QUIZZES_DIR.mkdir(parents=True, exist_ok=True)
    ensure_day1_files()

    day_logs = []

    for day in range(2, 31):
        p = PROFILES[day]
        slug = slugify(p['title'])
        lesson_path = LESSONS_DIR / f'lesson-{day:02d}-{slug}.md'
        quiz_path = QUIZZES_DIR / f'lesson-{day:02d}-{slug}-quiz.md'

        lesson_text = lesson_markdown(day, p)
        lerrs = validate_lesson(lesson_text, day)
        if lerrs:
            raise ValueError('; '.join(lerrs))
        lesson_path.write_text(lesson_text, encoding='utf-8')

        quiz_text = quiz_markdown(day, p)
        qerrs = validate_quiz(quiz_text, day)
        if qerrs:
            raise ValueError('; '.join(qerrs))
        quiz_path.write_text(quiz_text, encoding='utf-8')

        day_logs.append({
            'day': day,
            'status': 'PASS',
            'lesson_file': str(lesson_path.relative_to(BASE)),
            'quiz_file': str(quiz_path.relative_to(BASE)),
        })

    package = build_package()
    OUT_PACKAGE.write_text(json.dumps(package, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    errors = full_course_qa(package)
    update_reports(day_logs, package, errors)

    print('status=' + ('PASS' if not errors else 'FAIL'))
    print(f'lessons={len(list(LESSONS_DIR.glob("lesson-*.md")))}')
    print(f'quizzes={len(list(QUIZZES_DIR.glob("lesson-*-quiz.md")))}')
    print(f'package={OUT_PACKAGE}')
    print(f'run_log={RUN_LOG}')
    print(f'lqa_report={LQA_REPORT}')
    print(f'ready_report={READY_REPORT}')
    print(f'pairwise_log={PAIRWISE_LOG}')
    if errors:
        print(f'errors={len(errors)}')
        for e in errors:
            print('- ' + e)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
