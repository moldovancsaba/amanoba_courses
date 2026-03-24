# Lesson 15: Udhibiti wa gharama na rate limits

**One-liner:** Ongeza guardrails za kufanya gharama za AI zitabirike.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Orodha ya Ulinzi wa Gharama na Vikomo

## Learning goal

You will be able to: **Kuweka vikomo vya gharama na rate limits vinavyolinda bidhaa yako ya AI.**

### Success criteria (observable)
- [ ] Orodha ya ulinzi wa gharama imekamilika.
- [ ] Rate limits zimefafanuliwa kwa endpoints muhimu.
- [ ] Kikomo cha gharama za mwezi kimeandikwa.

### Output you will produce
- **Deliverable:** Orodha ya Ulinzi wa Gharama na Vikomo
- **Format:** Checklist na jedwali la limits
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayedhibiti gharama za AI
**Secondary persona(s):** Wateja wanaolipia wanaotegemea huduma thabiti
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Seti ndogo ya sheria zinazoweka mipaka ya matumizi na kulinda bajeti.
Inachanganya kikomo cha gharama na rate limits ili mtumiaji mmoja asichome bajeti.

### What it is not
Si mfumo kamili wa fedha wala mbadala wa mkakati wa bei.
Ni safu ya ulinzi kwa bidhaa za hatua za mwanzo.

### 2-minute theory
- Gharama za AI zinaweza kukua haraka kwa matumizi makubwa.
- Rate limits hulinda uthabiti na bajeti kwa pamoja.
- Vikomo wazi hufanya majaribio ya bei kuwa salama.

### Key terms
- **Rate limit:** Sheria ya kuzuia idadi ya requests kwa mtumiaji au muda.
- **Cost cap:** Kiasi cha juu unachokubali kutumia kwa kipindi.

## Where

### Applies in
- API routes
- Billing logic

### Does not apply in
- Majaribio ya mkono ya mara moja

### Touchpoints
- Usage logs
- Billing dashboard
- Alerting rules

## When

### Use it when
- Unafungua app kwa watumiaji halisi
- Unaanza kutoza malipo

### Frequency
Weka mara moja, rekebisha kadri matumizi yanavyokua

### Late signals
- Spikes zisizo za kawaida za matumizi
- Bili kubwa kuliko ulivyotarajia

## Why it matters

### Practical benefits
- Gharama zinatabirika
- Outages chache
- Udhibiti bora wa matumizi ya bure

### Risks of ignoring
- Bili za kushangaza
- Matumizi mabaya na heavy users

### Expectations
- Improves: uthabiti wa gharama na usalama
- Does not guarantee: margin kamili

## How

### Step-by-step method
1. Chagua kikomo cha gharama za mwezi.
2. Fafanua rate limits kwa kila mtumiaji.
3. Ongeza kikomo cha kila siku kwa watumiaji wa bure.
4. Weka alerts kwa spikes.
5. Pitia matumizi kila wiki.

### Do and don't

**Do**
- Anza na limits za tahadhari
- Rekodi matumizi kwa mtumiaji

**Don't**
- Toa matumizi ya bure bila controls
- Kusubiri bili ndipo uanze kuchukua hatua

### Common mistakes and fixes
- **Mistake:** Hakuna cost cap. **Fix:** Weka kikomo kidogo cha mwezi.
- **Mistake:** Hakuna per user limits. **Fix:** Ongeza rate limits kwa mtumiaji.

### Done when
- [ ] Kikomo cha gharama za mwezi kimeandikwa.
- [ ] Rate limits zimefafanuliwa.
- [ ] Alerts zimesanidiwa.

## Guided exercise (10 to 15 min)

### Inputs
- Matumizi yanayotarajiwa kwa mtumiaji
- Dhana ya bei ya sasa

### Steps
1. Kadiria gharama kwa request.
2. Weka bajeti ya mwezi.
3. Fafanua limits kwa mtumiaji.

### Output format
| Field | Value |
|---|---|
| Cost per request | |
| Monthly cap | |
| Rate limits | |
| Alert trigger | |

> **Pro tip:** Anza na cap ndogo kisha ongeza baada ya kuona matumizi halisi.

## Independent exercise (5 to 10 min)

### Task
Tengeneza sheria ya heavy user na uandike hatua ya kuchukua.

### Output
Sheria ya heavy user na response yake.

## Self-check (yes/no)

- [ ] Je, kikomo cha mwezi kimefafanuliwa?
- [ ] Je, per user limits zimefafanuliwa?
- [ ] Je, alerts zimesanidiwa?
- [ ] Je, matumizi yanapitiwa kila wiki?

### Baseline metric (recommended)
- **Score:** Ukaguzi 3 kati ya 4 umetimia
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Pricing**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/pricing

2. **API Rate Limiting Guide**. Cloudflare. 2024-01-01.
   Read: https://developers.cloudflare.com/rate-limits/

## Read more (optional)

1. **Usage Based Pricing**
   Why: Linganisha gharama na mipango ya bei.
   Read: https://www.profitwell.com/recur/all/usage-based-pricing
