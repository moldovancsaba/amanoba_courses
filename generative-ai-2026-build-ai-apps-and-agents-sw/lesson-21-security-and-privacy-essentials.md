# Lesson 21: Misingi ya usalama na faragha

**One-liner:** Linda data na mfumo kwa hatua za msingi zinazotekelezeka.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Checklist ya Usalama na Faragha

## Learning goal

You will be able to: **Kutengeneza checklist ya usalama na faragha kwa app ya AI ya kibiashara.**

### Success criteria (observable)
- [ ] Checklist ina angalau vipengele 8 vya msingi.
- [ ] Kuna hatua ya kulinda API keys na data ya mtumiaji.
- [ ] Hatua 1 ya response kwa incident imeandikwa.

### Output you will produce
- **Deliverable:** Checklist ya Usalama na Faragha
- **Format:** Orodha ya ukaguzi na maelezo mafupi
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayeendesha app ya AI kwa watumiaji halisi
**Secondary persona(s):** Watumiaji wanaojali usalama
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Orodha ya hatua za msingi za kulinda mfumo, data, na upatikanaji.
Inakusaidia kuanza kwa usalama bila kuhitaji timu kubwa.

### What it is not
Si audit kamili ya usalama.
Si mbadala wa ushauri wa kisheria.

### 2-minute theory
- Hatua ndogo za usalama hupunguza hatari kubwa mapema.
- Faragha inaongeza uaminifu na kupunguza hatari za kisheria.
- Checklist husaidia kuepuka kusahau mambo muhimu.

### Key terms
- **Least privilege:** Kupa kila mtu kiwango cha ufikiaji kidogo kinachohitajika.
- **Incident response:** Hatua za kuchukua wakati hitilafu ya usalama inatokea.

## Where

### Applies in
- Access control
- Data storage

### Does not apply in
- Demos za ndani bila data ya watumiaji

### Touchpoints
- API keys
- Database
- Audit logs

## When

### Use it when
- Unazindua kwa watumiaji wa kwanza
- Unaanza kushika data ya mtumiaji

### Frequency
Kila release kubwa ya bidhaa

### Late signals
- API keys kuonekana kwenye repo
- Maombi ya kufuta data kuchelewa

## Why it matters

### Practical benefits
- Kupunguza hatari za uvujaji
- Uaminifu wa mtumiaji unaongezeka
- Response ya haraka kwa matukio

### Risks of ignoring
- Uvujaji wa data
- Kupoteza uaminifu

### Expectations
- Improves: usalama wa msingi
- Does not guarantee: ulinzi kamili

## How

### Step-by-step method
1. Weka MFA kwenye akaunti muhimu.
2. Tumia least privilege kwa timu.
3. Hifadhi API keys kwenye env variables.
4. Ficha data nyeti kwenye logs.
5. Weka retention ya data na hatua ya kufuta.
6. Andika hatua 1 ya incident response.

### Do and don't

**Do**
- Tumia secrets manager au env variables
- Rekodi access muhimu

**Don't**
- Kuweka keys kwenye client
- Kuacha data nyeti kwenye logs

### Common mistakes and fixes
- **Mistake:** Hakuna MFA. **Fix:** Weka MFA kwenye akaunti muhimu.
- **Mistake:** Logs zina data nyeti. **Fix:** Ficha au redaction.

### Done when
- [ ] Checklist ina vipengele 8.
- [ ] API keys zinalindwa.
- [ ] Hatua ya incident response imeandikwa.

## Guided exercise (10 to 15 min)

### Inputs
- Akaunti na huduma unazotumia
- Orodha ya data nyeti

### Steps
1. Andika checklist ya hatua 8.
2. Tambua hatua 2 za faragha.
3. Andika incident response ya hatua ya kwanza.

### Output format
| Field | Value |
|---|---|
| Security item | |
| Privacy item | |
| Owner | |
| Status | |

> **Pro tip:** Anza na MFA na ulinzi wa API keys.

## Independent exercise (5 to 10 min)

### Task
Ongeza hatua moja ya ukaguzi wa ulinzi wa data.

### Output
Kipengele kipya kwenye checklist.

## Self-check (yes/no)

- [ ] Je, MFA imewekwa?
- [ ] Je, API keys zinalindwa?
- [ ] Je, retention ya data imeandikwa?
- [ ] Je, incident response ya hatua 1 ipo?

### Baseline metric (recommended)
- **Score:** Vipengele 3 kati ya 4 vimetimia
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OWASP Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/

2. **NIST Privacy Framework**. NIST. 2024-01-01.
   Read: https://www.nist.gov/privacy-framework

## Read more (optional)

1. **Security Basics for Startups**
   Why: Hatua za msingi za kuanza.
   Read: https://owasp.org/
