# Lesson 12 Quiz Pool

**Question:** Unabuni tool schema kwa AI action. Ni kipengele kipi ni lazima ili inputs ziwe thabiti na zinazoeleweka?

A) Jina la tool tu bila inputs.
B) Jina la tool, input fields, na output shape iliyo wazi.
C) Output pekee bila input schema.
D) Maelezo marefu ya masoko kuhusu tool.

**Correct:** B

**Why correct:** Schema lazima ifafanue inputs na outputs ili call iwe thabiti.
**Why others are wrong:**
- A: Haina inputs wala output format.
- C: Bila inputs model itatoa data isiyotabirika.
- D: Maelezo ya masoko si schema.

**Tags:** #tools #difficulty-easy #type-definition

---

**Question:** Tool inaweza kubadilisha data ya mtumiaji. Guardrail bora ni ipi?

A) Ruhusu action bila kuangalia ili iwe haraka.
B) Ongeza uthibitisho wa mtumiaji kabla ya action kutekelezwa.
C) Ficha action kwenye UI lakini uendelee kuiruhusu.
D) Ondoa logging ili kupunguza data.

**Correct:** B

**Why correct:** Hatua ya uthibitisho huzuia actions zisizotarajiwa.
**Why others are wrong:**
- A: Haina ulinzi wowote.
- C: Kuweka chini ya pazia si ulinzi.
- D: Kukosa logs hupunguza ufuatiliaji.

**Tags:** #guardrails #difficulty-medium #type-scenario

---

**Question:** Tool call inashindwa kwa sababu ya input isiyo sahihi. Hatua bora ni ipi?

A) Acha model ibashiri inputs bila validation.
B) Validate inputs kabla ya kuendesha tool call.
C) Ongeza randomness ili input ibadilike.
D) Futa schema na utumie free text.

**Correct:** B

**Why correct:** Validation hupunguza errors na inputs mbaya.
**Why others are wrong:**
- A: Kubashiri huongeza makosa.
- C: Randomness inaongeza kutotabirika.
- D: Free text huongeza hatari ya inputs chafu.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** Ni nini maana ya guardrail katika tool calling?

A) Kanuni zinazobadilisha output bila record.
B) Sheria za kuzuia actions zisizo salama au zisizoruhusiwa.
C) Njia ya kuongeza token usage kwa makusudi.
D) Hifadhi ya outputs za zamani.

**Correct:** B

**Why correct:** Guardrail ni sheria ya ulinzi dhidi ya actions hatari.
**Why others are wrong:**
- A: Hiyo si ulinzi.
- C: Haina uhusiano na guardrails.
- D: Huo ni uhifadhi wa data, sio ulinzi.

**Tags:** #guardrails #difficulty-easy #type-definition

---

**Question:** Ni dalili gani inayoonyesha tool calling imeundwa vibaya?

A) Logs zinaonyesha inputs na outputs kwa kila call.
B) Tool calls zinashindwa mara kwa mara kwa inputs zisizo sahihi.
C) Schema ina required fields na types.
D) Actions zinafanywa baada ya uthibitisho.

**Correct:** B

**Why correct:** Failures za mara kwa mara zinaonyesha schema au validation mbaya.
**Why others are wrong:**
- A: Hii ni ishara nzuri ya ufuatiliaji.
- C: Hii ni mazoea mazuri.
- D: Hii ni ulinzi mzuri.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** Unataka kuanza tool call salama katika toleo la kwanza. Hatua ipi ina kipaumbele?

A) Fungua tools zote bila mipaka ili kujaribu kila kitu.
B) Anza na tool moja, schema wazi, na guardrails za msingi.
C) Acha kuandika schema na tumia prompt tu.
D) Tumia tools bila logs ili kuepuka data.

**Correct:** B

**Why correct:** Tool moja, schema wazi, na guardrails hutoa uthabiti wa mwanzo.
**Why others are wrong:**
- A: Hii inaongeza hatari mapema.
- C: Bila schema inputs hutawanyika.
- D: Bila logs hutakujua kilichotokea.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** Kwa nini ni muhimu kurekodi action logs za tool calls?

A) Ili kuongeza latency kwa makusudi.
B) Ili uweze kufuatilia matukio na kurekebisha makosa.
C) Ili kuficha makosa kutoka kwa watumiaji.
D) Ili model isijifunze tena.

**Correct:** B

**Why correct:** Logs husaidia ufuatiliaji na utatuzi wa matatizo.
**Why others are wrong:**
- A: Latency si lengo.
- C: Kuzima uwazi ni hatari.
- D: Haina uhusiano na logging.

**Tags:** #logging #difficulty-easy #type-definition
