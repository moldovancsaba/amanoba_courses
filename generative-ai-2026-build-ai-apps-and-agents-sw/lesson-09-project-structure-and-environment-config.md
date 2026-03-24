# Lesson 9: Muundo wa mradi na mazingira ya config

**One-liner:** Sanidi folders, config, na secrets kwa usalama.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Muundo wa Mradi na Env Template

## Learning goal

You will be able to: **Kuunda muundo wa mradi na mazingira salama ya config.**

### Success criteria (observable)
- [ ] Muundo wa folders unaendana na workflow ya app.
- [ ] Env template ina keys zinazohitajika.
- [ ] Secrets hazija-commit.

### Output you will produce
- **Deliverable:** Muundo wa Mradi na Env Template
- **Format:** Folder tree na .env.example
- **Where saved:** Repo na noti za kozi

## Who

**Primary persona:** Digital nomad anayejenga msingi wa app
**Secondary persona(s):** Washirika wa ujenzi
**Stakeholders (optional):** Watumiaji wa awali

## What

### What it is
Muundo mdogo wa folders pamoja na env template inayolinda secrets.
Inafanya setup ya local na deployment kuwa thabiti.

### What it is not
Si mabadiliko makubwa ya architecture.
Si mpango wa usalama kamili.

### 2-minute theory
- Muundo wazi huongeza kasi ya maendeleo.
- Env templates hupunguza missing keys.
- Secrets nje ya code hupunguza hatari.

### Key terms
- **Env template:** Faili ya kuonyesha keys zinazohitajika.
- **Project skeleton:** Muundo wa msingi wa mradi.

## Where

### Applies in
- Local development
- Deployment setup

### Does not apply in
- Maamuzi ya UI design

### Touchpoints
- .env.example
- .gitignore
- Muundo wa folders

## When

### Use it when
- Unaanza development
- Unajiandaa kwa deployment

### Frequency
Mara moja kwa mradi, rekebisha ukiongeza services

### Late signals
- Missing env vars husababisha crash
- Code na config zimechanganywa

## Why it matters

### Practical benefits
- Setup ya haraka
- Ulinzi wa secrets
- Onboarding safi

### Risks of ignoring
- Deployment kushindwa
- API keys kuvuja

### Expectations
- Improves: uthabiti na usalama
- Does not guarantee: security kamili

## How

### Step-by-step method
1. Tengeneza folder tree ya msingi.
2. Ongeza .env.example na keys.
3. Update .gitignore ili kuzuia .env.
4. Hakiki local run kwa values za mfano.

### Do and don't

**Do**
- Tenganisha config na code
- Andika keys zinazohitajika

**Don't**
- Commit API keys halisi
- Ficha keys ndani ya code

### Common mistakes and fixes
- **Mistake:** Hakuna env template. **Fix:** Ongeza .env.example.
- **Mistake:** Secrets zimo repo. **Fix:** Badilisha keys na ondoa history.

### Done when
- [ ] Folder tree ipo na iko wazi.
- [ ] .env.example ina keys.
- [ ] .gitignore imezuia .env.

## Guided exercise (10 to 15 min)

### Inputs
- Orodha ya MVP
- Stack uliochagua

### Steps
1. Tengeneza folder tree.
2. Ongeza .env.example.
3. Thibitisha .gitignore.

### Output format
| Field | Value |
|---|---|
| Folder tree | |
| Env keys | |
| Gitignore status | |
| Local run result | |

> **Pro tip:** Tumia env templates kama sehemu ya onboarding.

## Independent exercise (5 to 10 min)

### Task
Ongeza key moja mpya kwenye template.

### Output
.env.example iliyosasishwa.

## Self-check (yes/no)

- [ ] Je, keys zote zimeorodheshwa?
- [ ] Je, secrets zimezuiwa kwenye git?
- [ ] Je, muundo wa mradi ni wazi?
- [ ] Je, app ina-run na values za mfano?

### Baseline metric (recommended)
- **Score:** Vigezo 3 kati ya 4 vimetimia
- **Date:** 2026-02-07
- **Tool used:** Terminal

## Bibliography (sources used)

1. **12 Factor App Config**. 2024-01-01.
   Read: https://12factor.net/config

2. **GitHub Secrets Guide**. 2024-01-01.
   Read: https://docs.github.com/en/actions/security-guides/encrypted-secrets

## Read more (optional)

1. **Vercel Environment Variables**
   Why: Miongozo ya env vars kwenye deployment.
   Read: https://vercel.com/docs/projects/environment-variables
