# Tasklist

- [x] Scope lock: `AI_30_NAP`, `hu`, 30 lecke
- [x] Célmappa létrehozása (`lessons`, `quizzes`, `scripts`)
- [x] Forráscsomag shape és SSOT szabályok beolvasása
- [x] Lecke-különfájl pipeline implementálása
- [x] Kvíz-különfájl pipeline implementálása
- [x] 30/30 lecke generálása egyedi szituáció + deliverable + mérőszám logikával
- [x] 30/30 kvízpool generálása (7 kérdés/lecke, 0 recall, standalone kérdések)
- [x] Végső v2 JSON assembly kizárólag a létrehozott lecke/kvíz forrásokra építve
- [x] Teljes-kurzus QA script futtatása
- [x] Import readiness gate futtatása
- [x] Kötelező riportok elkészítése (`run-log.md`, `tasklist.md`, `localization-qa-report.md`, `ready-to-import-report.md`)
- [x] Kiegészítő nyelvi QA szabály rögzítése: minden kvízkérdés önmagában is értelmezhető legyen
- [x] Tiltott kérdésstem minták rögzítése handover szinten (`A cél: ...`, `A fő kockázat: ...`)
- [x] Skill és memória frissítése a kérdésnyelvi szabályokkal
- [x] Native-speaker + familiar localized nyelvi minőség kötelezővé tétele skill és handover szinten
- [x] Körös gyártási protokoll kötelezővé tétele minden releváns dokumentumban (skill + handover + QA report)

## Következő parancs (ha újrafuttatás kell)

`python3 /Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/scripts/build_hu_premium_rewrite.py && python3 /Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/scripts/qa_hu_premium_rewrite.py && python3 /Users/moldovancsaba/Projects/amanoba_courses/ai-30-nap-hu-premium-rewrite-2026-02-11/scripts/import_readiness_check.py`

## Napi körös protokoll (kötelező)

1. nap indítása
2. lecke elkészítése + teljes minőségbiztosítás
3. kapcsolódó kvíz elkészítése (7 kérdés + válaszok) + teljes minőségellenőrzés
4. nap lezárása, majd ugrás a következő napra
