# Lesson 10: Misingi ya OpenAI API na mbinu salama

**One-liner:** Tuma mwito wa OpenAI API unaotabirika na unaolindwa kwa hatua za msingi.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Mwito wa OpenAI unaofanya kazi na Ushughulikiaji wa Hitilafu

## Learning goal

You will be able to: **Kutekeleza mwito wa msingi wa OpenAI API wenye chaguo-msingi salama na ushughulikiaji wa hitilafu.**

### Success criteria (observable)
- [ ] Mwito unarudisha jibu kwa input ya mfano.
- [ ] Hitilafu zinashughulikiwa kwa ujumbe salama.
- [ ] API key imehifadhiwa kwenye env variable.

### Output you will produce
- **Deliverable:** Mwito wa OpenAI unaofanya kazi na Ushughulikiaji wa Hitilafu
- **Format:** Kipande cha code na log ya majaribio
- **Where saved:** Repo na noti za kozi ndani ya folda ya kozi

## Who

**Primary persona:** Digital nomad anayejenga app ya AI
**Secondary persona(s):** Watumiaji wanaotegemea output thabiti
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Ni mwito mdogo wa upande wa server kwenda OpenAI API wenye chaguo-msingi salama.
Unarudisha jibu linaloweza kutumiwa, na ukishindwa unatoa ujumbe unaoeleweka.

### What it is not
Si mfumo kamili wa agent wala orchestration ya hatua nyingi.
Ni kizuizi cha kwanza thabiti unachoweza kukitegemea.

### 2-minute theory
- Chaguo-msingi salama hupunguza tabia zisizotarajiwa na mshtuko wa gharama.
- Ushughulikiaji wa hitilafu unaoeleweka hulinda uaminifu wa mtumiaji kwenye siku mbaya.
- Env variables hulinda siri zisitoke kwenye codebase.

### Key terms
- **API key:** Siri ya kuthibitisha mwito.
- **Fallback:** Njia mbadala salama wakati API inashindwa.

## Where

### Applies in
- Njia za server
- Huduma za backend

### Does not apply in
- Uhifadhi wa siri kwenye client

### Touchpoints
- API route
- Kumbukumbu za hitilafu
- Mpangilio wa env

## When

### Use it when
- Unaongeza vipengele vya AI
- Unahitaji jibu la kwanza lililo thabiti

### Frequency
Mara moja kwa bidhaa, kisha rejea kadri vipengele vinavyoongezeka

### Late signals
- Hitilafu nyingi bila ujumbe wazi
- Siri kuingia kwenye repo

## Why it matters

### Practical benefits
- Ufuatiliaji wa matatizo kwa haraka
- Deployments salama bila key kuvuja
- Uzoefu bora kwa mtumiaji wakati API inachelewa

### Risks of ignoring
- API key kuvuja na gharama zisizotarajiwa
- Hitilafu zisizoeleweka zinazopunguza uaminifu

### Expectations
- Improves: uthabiti na uaminifu
- Does not guarantee: output kamili

## How

### Step-by-step method
1. Hifadhi API key kwenye env variable.
2. Tuma request yenye prompt fupi na inayoweza kupimwa.
3. Ongeza timeout na ushughulikiaji wa hitilafu.
4. Rudisha njia mbadala salama ikitokea hitilafu.
5. Rekodi request id kwa ufuatiliaji.

### Do and don't

**Do**
- Weka prompts fupi na zinazoweza kupimwa
- Rekodi hitilafu pamoja na muktadha wa request

**Don't**
- Kuweka API key kwenye client
- Kuficha hitilafu kwenye logs

### Common mistakes and fixes
- **Mistake:** Key iko kwenye code. **Fix:** Hamisha kwenye env na badilisha key.
- **Mistake:** Hakuna njia mbadala salama. **Fix:** Ongeza ujumbe salama wa fallback.

### Done when
- [ ] Mwito unafanikiwa kwa input ya mfano.
- [ ] Hitilafu zinatoa ujumbe wazi.
- [ ] API key iko kwenye env.

## Guided exercise (10 to 15 min)

### Inputs
- OpenAI API key kwenye env
- Prompt ya mfano

### Steps
1. Andika function ya request.
2. Ongeza ushughulikiaji wa hitilafu na ujumbe wa fallback.
3. Endesha test na uandike matokeo.

### Output format
| Field | Value |
|---|---|
| Input prompt | |
| Response sample | |
| Error handling | |
| Fallback message | |

> **Pro tip:** Tumia request id kwenye logs ili kufuatilia hitilafu.

## Independent exercise (5 to 10 min)

### Task
Badilisha prompt na uhakikishe output bado inafanya kazi.

### Output
Test log yenye prompt mpya na response.

## Self-check (yes/no)

- [ ] Je, API key iko kwenye env variables?
- [ ] Je, hitilafu zinatoa ujumbe salama kwa mtumiaji?
- [ ] Je, fallback response ipo?
- [ ] Je, test run imeandikwa?

### Baseline metric (recommended)
- **Score:** Vigezo 3 kati ya 4 vimetimia
- **Date:** 2026-02-07
- **Tool used:** Terminal

## Bibliography (sources used)

1. **OpenAI API Docs**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs

2. **OWASP API Security Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-api-security/

## Read more (optional)

1. **OpenAI Safety Best Practices**
   Why: Mbinu za ulinzi kwa AI features thabiti.
   Read: https://platform.openai.com/docs/guides/safety-best-practices
