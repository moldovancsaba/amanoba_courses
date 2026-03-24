# Run Log

- Dátum: 2026-02-11
- Projekt: AI_30_NAP teljes HU prémium újraírás
- Munkamappa: `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11`

## Scope lock

- Course ID: `AI_30_NAP`
- Nyelv: `hu`
- Cél: 30 lecke + 30 kvíz, teljesen magyar, kezdőbarát, egyedi mini-termék logikával
- Forrás: `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-refactor-2026-02-11/source-AI_30_NAP_export_2026-02-11.json` (diagnózis/reference)

## Végrehajtott lépések

1. Kötelező session context betöltve (`soul.md`, `user.md`, `memory/2026-02-11.md`; `memory/2026-02-10.md` és `MEMORY.md` nem létezett).
2. SSOT ellenőrizve:
   - `docs/amanoba-course-content-standard-v1-0.md`
   - `docs/course-package-format.md`
   - `docs/create-a-course-handover.md`
3. Új célmappa létrehozva: `lessons/`, `quizzes/`, `scripts/`.
4. Új generátor implementálva:
   - `scripts/build_hu_premium_rewrite.py`
   - külön lecke- és kvízfájl mentés
   - assembly a végső v2 JSON-ba
5. QA gate implementálva:
   - `scripts/qa_hu_premium_rewrite.py`
   - szekció-ellenőrzés, tábla/callout, tiltott minták, duplikáció, kérdésgate-ek
6. Import readiness gate implementálva:
   - `scripts/import_readiness_check.py`
7. Futtatás:
   - `python3 scripts/build_hu_premium_rewrite.py`
   - `python3 scripts/qa_hu_premium_rewrite.py`
   - `python3 scripts/import_readiness_check.py`

## Eredmények

- Generált leckefájlok: 30
- Generált kvízfájlok: 30
- Végső csomag: `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/AI_30_NAP_export_2026-02-11_hu-premium-rewrite.json`
- Alias csomag: `/Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/AI_30_NAP_export_2026-02-11_premium_rewrite.json`

## QA státusz

- Localization QA: PASS (`localization-qa-report.md`)
- Import readiness: PASS (`ready-to-import-report.md`)

## Megjegyzés

- Egy build iteration során duplikált kérdésszöveg hiba jelentkezett; javítva lett a kérdés kontextusának pontosításával, majd teljes újrafuttatás történt.

## Minőségfinomítás (második passz)

- Lecske sablonszöveg-deduplikálás: több blokkot lecke-specifikusra állítottam (`focus`, `scenario`, `deliverable`, `risk`, `metric` injektálással).
- Újragenerálás és teljes QA újrafuttatás megtörtént.
- Státusz a finomítás után is: PASS / PASS.
- Kvíz minőségfinomítás: az opciók is lecke-specifikusra lettek cserélve, így a 30 nap kérdései pedagógiailag kevésbé sablonosak.
- Finomítás után teljes újragenerálás + QA újrafuttatás történt (PASS).
- Teljes nyelvi clean-up futott az összes lecke/kvíz sablonon: eltávolítva az összes `a(z)` szerkezet és a nehézkes "napi rutinba tennéd ... használatát" mintázat.
- Újragenerálás + QA + import readiness ismét PASS.
- Teljes nyelvi magyarosítás futtatva: angolos szerepnevek, sablonkifejezések és magyartalan szerkezetek kiszedve a generátorból.
- További fordítások: kérés/kérésindítás, munkafolyamat, vevőprofil, bevezetési terv, kimenet-meghatározás, megfelelt/nem felelt meg.
- Forráscímkék magyar megnevezésre állítva (URL-ek változatlanok), metadata tagek magyarítva.
- A build előtti fájltisztítás bekerült a scriptbe, így nem maradnak bent régi slug-nevű állományok.
- Teljes rebuild + QA + import readiness: PASS.

## Handover kiegészítés (2026-02-11)

- Felhasználói visszajelzés alapján új minőségi szabály rögzítve: a kvízkérdésnek önmagában is érthető, természetes magyar mondatként kell működnie.
- Tiltott kérdésnyelv külön kiemelve: címkehalmozás (`A cél: ... A fő kockázat: ...`) és bármilyen adminisztratív, belső jegyzet-stílus.
- Kötelező kérdésmintázat handover szinten: valós helyzet + konkrét cél + egy döntési kérdés.
- A szabály beemelve a skill dokumentációba és a hosszú távú memóriába is, hogy következő futásokban alapértelmezett legyen.
- Új szigorítás: learner-facing szöveg csak native-speaker szintű, helyi használatú (familiar localized) nyelven fogadható el.
- Kötelező gyártási ciklus rögzítve: 1 nap indítás -> lecke + teljes QA -> kapcsolódó kvíz + teljes QA -> napzárás -> következő nap.
