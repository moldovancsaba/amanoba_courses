# Lesson 10 Quiz Pool

**Question:** Unajenga app ya AI na unahitaji kulinda API key. Mpangilio upi ni sahihi na salama zaidi kwa mazingira ya kibiashara?

A) Weka API key kwenye client na ufanye obfuscation ili isiweze kusomwa kirahisi.
B) Hifadhi API key kwenye env variable ya server na tuma maombi kupitia server route.
C) Tuma API key kwenye browser kupitia endpoint ya public ili iwe rahisi kuibadilisha.
D) Weka API key kwenye local storage kwa kila mtumiaji ili irahisishe cache.

**Correct:** B

**Why correct:** API key inapaswa kubaki kwenye server env variable na calls zipitie server.
**Why others are wrong:**
- A: Obfuscation haizuizi uvujaji wa siri.
- C: Kupewa client siri huongeza hatari ya kuvuja.
- D: Local storage ni ya client na si salama kwa siri.

**Tags:** #security #difficulty-easy #type-scenario

---

**Question:** Mwito wa OpenAI API unachelewa na unapata timeout. Ujumbe upi wa mtumiaji ni bora ili kulinda uaminifu na kutoa hatua inayofuata?

A) “Hitilafu ya ndani. Tafadhali usijaribu tena.”
B) “Hakuna majibu. Tumeondoa ujumbe wako.”
C) “Huduma ina ucheleweshaji. Jaribu tena baada ya dakika chache.”
D) “Tatizo ni la mtumiaji. Badilisha mtandao wako.”

**Correct:** C

**Why correct:** Ujumbe unaoeleweka na unaotoa hatua inayofuata hulinda uaminifu.
**Why others are wrong:**
- A: Unamzuia mtumiaji bila sababu na ni mkali.
- B: Unaondoa kazi ya mtumiaji bila maelezo.
- D: Unamlaumu mtumiaji bila ushahidi.

**Tags:** #error-handling #difficulty-medium #type-scenario

---

**Question:** Unataka kuzuia gharama zisizotarajiwa na tabia zisizo thabiti kwenye mwito wa kwanza wa OpenAI API. Ni mchanganyiko upi wa hatua ni bora?

A) Tumia prompt ndefu zaidi, zima logging, na ongeza max tokens bila kikomo.
B) Weka max tokens ndogo, timeout ya majaribio, na utumie fallback message.
C) Ruhusu client kutuma API key ili kupunguza latency na gharama za server.
D) Ondoa validation ya input ili kupunguza muda wa utekelezaji.

**Correct:** B

**Why correct:** Kikomo cha max tokens, timeout, na fallback hupunguza gharama na hulinda uthabiti.
**Why others are wrong:**
- A: Max tokens bila kikomo huongeza gharama na kutabirika kunapungua.
- C: Siri kwenye client huongeza hatari ya kuvuja.
- D: Kukosa validation huongeza hatari ya data chafu.

**Tags:** #safety #difficulty-medium #type-scenario

---

**Question:** Unahitaji kurekodi hitilafu bila kuvunja faragha ya mtumiaji. Ni njia ipi ni bora?

A) Log kila prompt kamili ya mtumiaji pamoja na data binafsi.
B) Tumia request id, error code, na muhtasari mfupi wa muktadha wa request.
C) Zima logs zote ili usihifadhi data yoyote.
D) Log API key ili iwe rahisi ku-trace matatizo.

**Correct:** B

**Why correct:** Request id na error code hutosha kwa ufuatiliaji bila data nyeti.
**Why others are wrong:**
- A: Huhifadhi data nyeti isiyohitajika.
- C: Hukosa taarifa muhimu za ufuatiliaji.
- D: Kuhifadhi API key ni hatari kubwa.

**Tags:** #logging #difficulty-medium #type-scenario

---

**Question:** Unapata error ya 429 rate limit kutoka OpenAI API. Hatua gani inafaa zaidi kwa app ya kibiashara?

A) Rudisha ujumbe wa fallback, log tukio, na jaribu tena kwa backoff.
B) Rudisha stack trace kwa mtumiaji ili ajitambue kilichotokea.
C) Rudisha 500 bila ujumbe na uache mtumiaji ajaribu mwenyewe.
D) Ongeza max tokens ili kupunguza idadi ya requests.

**Correct:** A

**Why correct:** Fallback, logging, na retry ya backoff hulinda uzoefu na husaidia ufuatiliaji.
**Why others are wrong:**
- B: Stack trace ni ya kiufundi sana na si salama.
- C: Kutokutoa ujumbe hupunguza uaminifu.
- D: Max tokens zaidi huongeza gharama na si suluhisho.

**Tags:** #rate-limit #difficulty-medium #type-scenario

---

**Question:** Unapoweka env variables kwa deployment, ni hatua ipi inasaidia kudumisha usalama wa API key?

A) Weka API key moja kwa moja kwenye README ili timu yote iweze kuiona.
B) Tumia `.env` ya ndani, ongeza kwenye `.gitignore`, na weka key kwenye mazingira ya production.
C) Weka API key kwenye client na uiweke kwa base64 ili isiweze kusomwa.
D) Weka API key kwenye test fixtures ili tests ziwe rahisi kuendesha.

**Correct:** B

**Why correct:** `.env` ya ndani haifai kuingia git, na key inabaki kwenye mazingira salama.
**Why others are wrong:**
- A: Hufichua siri kwa kila mtu na huongeza hatari.
- C: Base64 si ulinzi wa siri.
- D: Test fixtures zinaweza kuvuja kwenye repo.

**Tags:** #deployment #difficulty-easy #type-scenario

---

**Question:** Unahitaji fallback message inayosaidia mtumiaji bila kutoa ahadi za uongo. Ni ipi ni bora?

A) “Nimekamilisha kazi yako kikamilifu.” hata kama API ilishindwa.
B) “Sina majibu kwa sasa. Tafadhali jaribu tena baada ya muda mfupi.”
C) “Tatizo ni upande wako. Badilisha swali.”
D) “Hakuna kitu cha kufanya. Tunafunga.”

**Correct:** B

**Why correct:** Ujumbe unakiri tatizo na kutoa hatua inayofuata bila kutoa ahadi.
**Why others are wrong:**
- A: Hutoa taarifa ya uongo kwa mtumiaji.
- C: Inamlaumu mtumiaji bila msingi.
- D: Inakatisha tamaa na haina msaada.

**Tags:** #fallback #difficulty-easy #type-scenario
