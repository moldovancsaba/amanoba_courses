# Lesson 12: Tool calling na actions

**One-liner:** Unganisha model na tools na ulinde actions zisizo salama.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Tool Schema na Mfano wa Action

## Learning goal

You will be able to: **Kufafanua tool schema na kuendesha tool call salama.**

### Success criteria (observable)
- [ ] Tool schema ina name, inputs, na output shape.
- [ ] Tool call inaendeshwa kwa mfano halisi.
- [ ] Actions zisizo salama zimezuiwa.

### Output you will produce
- **Deliverable:** Tool Schema na Mfano wa Action
- **Format:** JSON schema na test log
- **Where saved:** Repo na noti za kozi ndani ya folda ya kozi

## Who

**Primary persona:** Digital nomad anayejenga AI features zenye tools
**Secondary persona(s):** Watumiaji wanaochochea actions
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Ufafanuzi wa tool unaoonyesha model nini inaweza kuita na vipi.
Mfano mdogo unaothibitisha tool call inafanya kazi kama ilivyokusudiwa.

### What it is not
Si mfumo kamili wa automation au permissions.
Ni hatua ya kwanza ya actions salama na zinazotabirika.

### 2-minute theory
- Tool calling huleta AI zaidi ya maandishi.
- Schema wazi hupunguza makosa ya input.
- Guardrails huzuia actions zisizotarajiwa.

### Key terms
- **Tool schema:** Ufafanuzi wa inputs na outputs kwa tool.
- **Guardrail:** Sheria ya kuzuia action zisizo salama.

## Where

### Applies in
- Agent workflows
- Backend services

### Does not apply in
- Uzalishaji wa maudhui pekee bila actions

### Touchpoints
- Tool definitions
- Action logs
- Permission checks

## When

### Use it when
- Unataka AI ichochee action
- Unahitaji inputs zinazotabirika

### Frequency
Kila unapoongeza tool mpya

### Late signals
- Tool calls kushindwa kwa inputs mbaya
- Actions zisizotarajiwa kutokea

## Why it matters

### Practical benefits
- AI feature zinakuwa na maana zaidi
- Failures chache kwenye automation
- Usalama na uaminifu bora

### Risks of ignoring
- Workflows kuvunjika
- Actions zisizo salama

### Expectations
- Improves: uthabiti na usalama
- Does not guarantee: maamuzi kamili

## How

### Step-by-step method
1. Fafanua jina la tool na kusudi lake.
2. Bainisha input fields na types.
3. Fafanua output shape.
4. Ongeza guardrails kwa actions hatari.
5. Endesha test call na rekodi matokeo.

### Do and don't

**Do**
- Validate inputs kabla ya utekelezaji
- Rekodi kila action

**Don't**
- Kuruhusu tools ziende bila checks
- Kufungua actions hatari bila control

### Common mistakes and fixes
- **Mistake:** Schema legevu. **Fix:** Ongeza required fields na types.
- **Mistake:** Hakuna guardrails. **Fix:** Zuia parameters hatari.

### Done when
- [ ] Tool schema imefafanuliwa na kupimwa.
- [ ] Guardrails zinazuia inputs hatari.
- [ ] Logs zinaonyesha call iliyofanikiwa.

## Guided exercise (10 to 15 min)

### Inputs
- Wazo la tool moja
- Mfano wa input values

### Steps
1. Andika tool schema.
2. Ongeza guardrails kwa inputs hatari.
3. Endesha test call na rekodi output.

### Output format
| Field | Value |
|---|---|
| Tool name | |
| Input schema | |
| Guardrails | |
| Test result | |

> **Pro tip:** Ikiwa tool inaweza kubadilisha data, ongeza hatua ya kuthibitisha.

## Independent exercise (5 to 10 min)

### Task
Ongeza guardrail moja zaidi na urudie test.

### Output
Schema iliyoboreshwa na test log mpya.

## Self-check (yes/no)

- [ ] Je, schema iko wazi na ina types?
- [ ] Je, actions zisizo salama zimezuiwa?
- [ ] Je, test call imeandikwa?
- [ ] Je, logs zimehifadhiwa?

### Baseline metric (recommended)
- **Score:** Tool call 1 imefanikiwa na guardrails
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Tools Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/tools

2. **OWASP API Security Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-api-security/

## Read more (optional)

1. **Function Calling Best Practices**
   Why: Mbinu salama kwa tool calling.
   Read: https://platform.openai.com/docs/guides/tools
