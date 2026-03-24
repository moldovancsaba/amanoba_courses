# Lesson 25 Quiz Pool

**Question:** Kwa nini signature verification ni muhimu kwenye webhooks?

A) Ili kuongeza latency kwa mazingira ya app ya AI ya kibiashara.
B) Ili kuhakikisha event inatoka Stripe kwa kweli.
C) Ili kupunguza logging kwa mazingira ya app ya AI ya kibiashara.
D) Ili kuongeza randomness kwa mazingira ya app ya AI ya kibiashara.

**Correct:** B

**Why correct:** Signature verification hulinda dhidi ya events bandia.
**Why others are wrong:**
- A: Latency si lengo.
- C: Logging bado inahitajika.
- D: Randomness si lengo.

**Tags:** #security #difficulty-easy #type-definition

---

**Question:** Webhook inapaswa kufanya nini baada ya kupokea event ya malipo?

A) Kusasisha status ya malipo kwenye database.
B) Kuaminisha client kutoa status.
C) Kuzima access kwa wote kwa mazingira ya app ya AI ya kibiashara.
D) Kuacha event bila hatua kwa mazingira ya app ya AI ya kibiashara.

**Correct:** A

**Why correct:** Status ya malipo lazima isasishwe kwa access control.
**Why others are wrong:**
- B: Client si chanzo cha ukweli.
- C: Hii ni hatua ya kupita kiasi.
- D: Kuacha event ni hatari.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Ni hatari gani ya kutotumia webhooks kwa access control?

A) Hakuna hatari kwa mazingira ya app ya AI ya kibiashara.
B) Wateja wanaweza kupata access bila kulipa.
C) App itakuwa haraka kwa mazingira ya app ya AI ya kibiashara.
D) Logging itapungua kwa mazingira ya app ya AI ya kibiashara.

**Correct:** B

**Why correct:** Bila webhooks, status inaweza kuwa si sahihi.
**Why others are wrong:**
- A: Hii si kweli.
- C: Kasi si faida ya usalama.
- D: Logging si faida ya usalama.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Ni hatua gani bora kwa webhook endpoint?

A) Kuacha endpoint wazi bila verification.
B) Kuthibitisha signature na kurekodi event.
C) Kuweka API key kwenye client.
D) Kuacha retries kwa mazingira ya app ya AI ya kibiashara.

**Correct:** B

**Why correct:** Verification na logging ni muhimu kwa usalama.
**Why others are wrong:**
- A: Endpoint wazi ni hatari.
- C: API key kwenye client ni hatari.
- D: Retries husaidia events zisipotee.

**Tags:** #security #difficulty-medium #type-scenario

---

**Question:** Ni dalili gani ya access control isiyo sahihi?

A) Wateja waliolipia wanapata access.
B) Wateja wasiokulipa wanapata access.
C) Webhook logs zipo kwa mazingira ya app ya AI ya kibiashara.
D) Signature verification imepita.

**Correct:** B

**Why correct:** Access ya wasiokulipa ni hitilafu.
**Why others are wrong:**
- A: Hii ni sahihi.
- C: Logs ni msaada.
- D: Verification ni msaada.

**Tags:** #payments #difficulty-medium #type-scenario

---

**Question:** Ni hatua gani nzuri kuhusu retries za webhook?

A) Kuzizima ili kupunguza events.
B) Kuziweka ili kuhakikisha events zinapokelewa.
C) Kuweka retries bila limits.
D) Kuweka retries kwenye client.

**Correct:** B

**Why correct:** Retries husaidia events zisipotee.
**Why others are wrong:**
- A: Hii huongeza hatari ya kupoteza data.
- C: Bila limits inaweza kuleta overload.
- D: Client si sehemu ya webhook.

**Tags:** #reliability #difficulty-medium #type-scenario

---

**Question:** Ni hatua gani ya mwisho baada ya webhook kufanya update ya status?

A) Kuweka access control kulingana na status.
B) Kuzima database kwa mazingira ya app ya AI ya kibiashara.
C) Kuweka status kwenye client tu.
D) Kuacha logging kwa mazingira ya app ya AI ya kibiashara.

**Correct:** A

**Why correct:** Access control inategemea status sahihi.
**Why others are wrong:**
- B: Hii ni hatari.
- C: Client si chanzo cha ukweli.
- D: Logging ni muhimu.

**Tags:** #payments #difficulty-easy #type-scenario
