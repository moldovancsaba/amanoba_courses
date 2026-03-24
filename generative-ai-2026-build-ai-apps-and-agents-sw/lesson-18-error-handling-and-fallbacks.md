# Lesson 18: Ushughulikiaji wa hitilafu na fallbacks

**One-liner:** Panga jinsi app itakavyojibu hitilafu bila kuvunja uaminifu.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Mpango wa Error Handling na Fallbacks

## Learning goal

You will be able to: **Kuunda mpango wa kushughulikia hitilafu na kutoa fallback salama.**

### Success criteria (observable)
- [ ] Aina 3 za hitilafu zimeainishwa.
- [ ] Kila hitilafu ina ujumbe wa mtumiaji na hatua inayofuata.
- [ ] Fallback moja imeandikwa kwa hali ya failure.

### Output you will produce
- **Deliverable:** Mpango wa Error Handling na Fallbacks
- **Format:** Jedwali la hitilafu na majibu
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayeshughulikia hitilafu za app ya AI
**Secondary persona(s):** Watumiaji wanaotaka majibu ya kueleweka
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Mpango unaoeleza aina za hitilafu, ujumbe wa mtumiaji, na hatua ya kuchukua.
Fallback salama inayomsaidia mtumiaji wakati mfumo unashindwa.

### What it is not
Si log ya kiufundi pekee.
Si utafutaji wa makosa bila ujumbe kwa mtumiaji.

### 2-minute theory
- Hitilafu zinaweza kutokea, lakini uzoefu bado unaweza kuwa mzuri.
- Ujumbe wazi hupunguza hasira na kusaidia hatua inayofuata.
- Fallback salama huokoa uzoefu wa mtumiaji.

### Key terms
- **Error handling:** Mpango wa kutambua na kujibu hitilafu.
- **Fallback:** Njia mbadala salama wakati mfumo unashindwa.

## Where

### Applies in
- API routes
- UI messages

### Does not apply in
- Maelezo ya masoko

### Touchpoints
- Error logs
- User messages
- Support tickets

## When

### Use it when
- Unaanza kuendesha app kwa watumiaji
- Unapata hitilafu zisizotarajiwa

### Frequency
Kila feature inapoongezwa

### Late signals
- Watumiaji wanalalamika bila maelezo
- Support inapata tickets nyingi

## Why it matters

### Practical benefits
- Uaminifu wa mtumiaji unabaki
- Support inakuwa rahisi
- Matokeo ya bidhaa yanabaki thabiti

### Risks of ignoring
- Watumiaji kukata tamaa
- Matumizi kushuka

### Expectations
- Improves: uaminifu na uzoefu
- Does not guarantee: sifuri hitilafu

## How

### Step-by-step method
1. Orodhesha aina 3 za hitilafu za kawaida.
2. Andika ujumbe wa mtumiaji kwa kila aina.
3. Ongeza hatua inayofuata kwa kila ujumbe.
4. Andika fallback salama kwa hitilafu kubwa.
5. Rekodi errors kwenye logs.

### Do and don't

**Do**
- Tumia lugha rahisi kwa mtumiaji
- Weka hatua inayofuata

**Don't**
- Kuonyesha stack trace kwa mtumiaji
- Kutoa ujumbe wa kulaumu

### Common mistakes and fixes
- **Mistake:** Ujumbe wa jumla. **Fix:** Ongeza maelezo na hatua.
- **Mistake:** Hakuna fallback. **Fix:** Andika fallback ya msingi.

### Done when
- [ ] Aina 3 za hitilafu zimeandikwa.
- [ ] Ujumbe wa mtumiaji upo kwa kila hitilafu.
- [ ] Fallback imeandikwa.

## Guided exercise (10 to 15 min)

### Inputs
- Orodha ya hitilafu unazotarajia
- Mfano wa mtumiaji

### Steps
1. Andika hitilafu 3.
2. Andika ujumbe wa mtumiaji kwa kila hitilafu.
3. Ongeza hatua inayofuata.

### Output format
| Field | Value |
|---|---|
| Error type | |
| User message | |
| Next step | |
| Fallback | |

> **Pro tip:** Ujumbe mfupi na wazi hupunguza hasira.

## Independent exercise (5 to 10 min)

### Task
Boresha ujumbe mmoja wa hitilafu ili uwe rafiki zaidi.

### Output
Ujumbe mpya na hatua inayofuata.

## Self-check (yes/no)

- [ ] Je, aina za hitilafu zimeainishwa?
- [ ] Je, kuna hatua inayofuata kwa mtumiaji?
- [ ] Je, fallback ipo?
- [ ] Je, logs zinarekodi errors?

### Baseline metric (recommended)
- **Score:** Hatua 3 kati ya 4 zimekamilika
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Error Handling UX**. NNGroup. 2024-01-01.
   Read: https://www.nngroup.com/articles/error-messages/

2. **Resilient Systems Basics**. AWS. 2024-01-01.
   Read: https://aws.amazon.com/builders-library/

## Read more (optional)

1. **Fallback Patterns**
   Why: Njia za kuokoa uzoefu wa mtumiaji.
   Read: https://aws.amazon.com/builders-library/
