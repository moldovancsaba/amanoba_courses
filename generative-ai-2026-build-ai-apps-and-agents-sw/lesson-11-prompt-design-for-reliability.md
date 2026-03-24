# Lesson 11: Muundo wa prompt kwa uthabiti

**One-liner:** Buni prompts zinazotoa output thabiti na inayoweza kupimwa.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Spec ya Prompt na Seti ya Majaribio

## Learning goal

You will be able to: **Kuandika spec ya prompt na seti ndogo ya majaribio inayoongeza uthabiti.**

### Success criteria (observable)
- [ ] Prompt ina role, task, na output format.
- [ ] Seti ya majaribio ina angalau inputs 5 zinazoonyesha matumizi halisi.
- [ ] Angalau 4 kati ya 5 ya majaribio yanatimiza output inayotarajiwa.

### Output you will produce
- **Deliverable:** Spec ya Prompt na Seti ya Majaribio
- **Format:** Hati ya prompt na jedwali la majaribio
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayetengeneza prompts kwa app ya AI ya kibiashara
**Secondary persona(s):** Watumiaji wanaotegemea output thabiti
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Spec iliyo wazi inayomwambia model nini ifanye na jinsi output iwekwe.
Seti ndogo ya majaribio inayofichua udhaifu kabla ya watumiaji kuuona.

### What it is not
Si prompt ndefu inayojaribu kusuluhisha kila edge case.
Si mbadala wa mantiki ya bidhaa au validation ya mfumo.

### 2-minute theory
- Prompt ni interface ya bidhaa, lazima iwe thabiti.
- Muundo wazi hupunguza drift ya output na mshangao.
- Seti ndogo ya majaribio hukamata makosa mapema kwa effort ndogo.

### Key terms
- **Prompt spec:** Maagizo yaliyopangwa yenye role, task, na format.
- **Test set:** Inputs chache zinazotumika kupima ubora wa output.

## Where

### Applies in
- System prompts
- Prompts maalum za feature

### Does not apply in
- Nakala ya UX pekee au maudhui ya masoko

### Touchpoints
- Faili za prompt
- Test cases
- Output logs

## When

### Use it when
- Unaongeza feature mpya ya AI
- Ubora wa output hauko thabiti

### Frequency
Kila prompt inapobadilika

### Late signals
- Watumiaji wanalalamika kuhusu output tofauti
- Muundo wa output unavunjika

## Why it matters

### Practical benefits
- Output thabiti zaidi
- Debugging ya haraka
- Uaminifu bora kwa mtumiaji

### Risks of ignoring
- Output isiyotabirika
- Mzigo mkubwa wa support

### Expectations
- Improves: uthabiti na uwazi
- Does not guarantee: usahihi kamili

## How

### Step-by-step method
1. Andika role na task katika sentensi moja.
2. Fafanua output format kwa mfano mfupi.
3. Ongeza constraints kama tone au urefu.
4. Tengeneza inputs 5 za majaribio.
5. Endesha tests na rekodi pass rate.

### Do and don't

**Do**
- Tumia output formats zilizo wazi
- Weka prompts fupi na zinazolenga jambo moja

**Don't**
- Changanya tasks nyingi kwenye prompt moja
- Kuruka majaribio ya inputs halisi

### Common mistakes and fixes
- **Mistake:** Format si wazi. **Fix:** Toa template iliyopangwa.
- **Mistake:** Hakuna tests. **Fix:** Ongeza seti ndogo ya majaribio.

### Done when
- [ ] Prompt ina role, task, na format.
- [ ] Seti ya majaribio ina inputs 5.
- [ ] Pass rate imeandikwa.

## Guided exercise (10 to 15 min)

### Inputs
- Maelezo ya feature yako
- Inputs 5 za mtumiaji

### Steps
1. Andika spec ya prompt yenye role, task, na format.
2. Andika output inayotarajiwa kwa kila input.
3. Rekodi pass au fail.

### Output format
| Field | Value |
|---|---|
| Prompt spec | |
| Input set | |
| Expected output | |
| Pass rate | |

> **Pro tip:** Tumia inputs halisi za watumiaji, sio mifano bora tu.

## Independent exercise (5 to 10 min)

### Task
Fupisha prompt kwa asilimia 20 bila kupoteza uwazi.

### Output
Spec ya prompt iliyorekebishwa na matokeo mapya ya tests.

## Self-check (yes/no)

- [ ] Je, prompt ina role, task, na format?
- [ ] Je, inputs ni halisi na mbalimbali?
- [ ] Je, pass rate imeandikwa?
- [ ] Je, prompt ni rahisi kusoma?

### Baseline metric (recommended)
- **Score:** Tests 4 kati ya 5 zimepita
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Prompt Engineering Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/prompt-engineering

2. **Prompting Best Practices**. Anthropic. 2026-02-06.
   Read: https://docs.anthropic.com/claude/docs/prompting

## Read more (optional)

1. **System Prompt Best Practices**
   Why: Mwongozo wa output thabiti.
   Read: https://platform.openai.com/docs/guides/prompt-engineering
