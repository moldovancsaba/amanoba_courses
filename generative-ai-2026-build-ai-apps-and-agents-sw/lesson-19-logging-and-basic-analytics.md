# Lesson 19: Logging na basic analytics

**One-liner:** Rekodi matukio muhimu ili uone matumizi na makosa mapema.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Mpango wa Logging na Vipimo vya Msingi

## Learning goal

You will be able to: **Kuchagua events muhimu za ku-log na vipimo vya msingi vya bidhaa.**

### Success criteria (observable)
- [ ] Events 5 muhimu zimeainishwa.
- [ ] Kila event ina purpose na mfano.
- [ ] Vipimo 2 vya msingi vimeandikwa.

### Output you will produce
- **Deliverable:** Mpango wa Logging na Vipimo vya Msingi
- **Format:** Jedwali la events na vipimo
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayepima afya ya bidhaa
**Secondary persona(s):** Timu inayotegemea data
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Orodha ya events muhimu unazorekodi ili uone matumizi na makosa.
Vipimo vya msingi vinavyoonyesha kama bidhaa inafanya kazi.

### What it is not
Si mfumo mkubwa wa analytics.
Si logging ya kila kitu bila mpangilio.

### 2-minute theory
- Logging inakupa mwanga wa matumizi ya kweli.
- Vipimo vya msingi vinaonyesha kama bidhaa inasimama.
- Logging ndogo, sahihi, ni bora kuliko nyingi zisizo muhimu.

### Key terms
- **Event:** Kitendo kinachorekodiwa kwenye mfumo.
- **Metric:** Kipimo kinachoonyesha afya ya bidhaa.

## Where

### Applies in
- Backend events
- Product usage

### Does not apply in
- Demos za ndani bila data ya kweli

### Touchpoints
- Event logs
- Analytics dashboard
- Alerts

## When

### Use it when
- Unataka kufuatilia matumizi
- Unahitaji kupima afya ya bidhaa

### Frequency
Kila release mpya ya feature

### Late signals
- Hujui ni wapi watumiaji wanaacha
- Hujui wapi errors hutokea

## Why it matters

### Practical benefits
- Uamuzi bora wa bidhaa
- Debugging ya haraka
- Uelewa wa matumizi ya wateja

### Risks of ignoring
- Maamuzi bila data
- Makosa yasiyoonekana mapema

### Expectations
- Improves: uelewa wa matumizi na uthabiti
- Does not guarantee: growth ya moja kwa moja

## How

### Step-by-step method
1. Chagua events 5 muhimu zaidi.
2. Andika purpose ya kila event.
3. Ongeza mfano wa wakati event itatokea.
4. Chagua vipimo 2 vya msingi.
5. Weka alerts kwa spikes za errors.

### Do and don't

**Do**
- Rekodi events zinazoathiri bidhaa
- Weka majina ya event yaliyo wazi

**Don't**
- Ku-log kila kitu bila mpangilio
- Kuacha data bila maana

### Common mistakes and fixes
- **Mistake:** Events nyingi zisizo muhimu. **Fix:** Punguza hadi muhimu.
- **Mistake:** Hakuna metric ya msingi. **Fix:** Chagua metrics mbili rahisi.

### Done when
- [ ] Events 5 zimeandikwa na kusudi.
- [ ] Metrics mbili zimeainishwa.
- [ ] Alerts zimewekwa.

## Guided exercise (10 to 15 min)

### Inputs
- Orodha ya features
- Matukio muhimu

### Steps
1. Chagua events 5.
2. Andika purpose na mfano.
3. Chagua metrics 2.

### Output format
| Field | Value |
|---|---|
| Event | |
| Purpose | |
| Example | |
| Metric | |

> **Pro tip:** Rekodi event ya “request failed” kwa ufuatiliaji wa errors.

## Independent exercise (5 to 10 min)

### Task
Punguza events hadi 3 ikiwa ni lazima na ueleze kwanini.

### Output
Orodha mpya ya events na maelezo.

## Self-check (yes/no)

- [ ] Je, events muhimu zimeainishwa?
- [ ] Je, metrics za msingi zimeandikwa?
- [ ] Je, mfano wa kila event upo?
- [ ] Je, alerts zimewekwa?

### Baseline metric (recommended)
- **Score:** Events 4 kati ya 5 zimekamilika
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Product Analytics Basics**. Amplitude. 2024-01-01.
   Read: https://amplitude.com/blog/product-analytics

2. **Logging Best Practices**. Google. 2024-01-01.
   Read: https://cloud.google.com/logging/docs

## Read more (optional)

1. **Event Design Guide**
   Why: Kubuni event zinazopimika.
   Read: https://amplitude.com/blog
