# Lesson 22: Vercel deployment na env variables

**One-liner:** Deploy app kwa Vercel na weka env variables kwa usalama.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Vercel Deploy Checklist na Env Map

## Learning goal

You will be able to: **Kuweka deployment ya Vercel na kusanidi env variables salama.**

### Success criteria (observable)
- [ ] App ime-deploy kwa Vercel kwa mazingira ya production.
- [ ] Env variables muhimu zimewekwa.
- [ ] Deployment inaendeshwa bila error za siri.

### Output you will produce
- **Deliverable:** Vercel Deploy Checklist na Env Map
- **Format:** Checklist na jedwali la env
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayedeploy app ya AI
**Secondary persona(s):** Watumiaji wa kwanza wa bidhaa
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Mchakato wa kupeleka app kwenye Vercel na kusanidi env variables kwa usalama.
Inakuhakikisha app inaweza kuendeshwa katika production.

### What it is not
Si mchakato wa kuhamisha database kubwa.
Si mfumo wa CI/CD wa kiwango cha enterprise.

### 2-minute theory
- Deployment thabiti hupunguza errors na muda wa kuzima huduma.
- Env variables hulinda siri kama API keys.
- Checklist husaidia kuhakikisha hatua muhimu hazikosekwi.

### Key terms
- **Deployment:** Uwekaji wa app kwenye server ya production.
- **Env variables:** Vigezo vya mazingira vinavyobeba secrets.

## Where

### Applies in
- Vercel dashboard
- Project settings

### Does not apply in
- Apps zisizo na backend

### Touchpoints
- Build logs
- Env settings
- Deployment URL

## When

### Use it when
- Uko tayari kuonyesha app kwa watumiaji
- Unahitaji URL ya production

### Frequency
Kila release mpya

### Late signals
- Build failures za env
- API key kuonekana kwenye client

## Why it matters

### Practical benefits
- App inapatikana kwa watumiaji
- Siri zinabaki salama
- Rahisi kurudia deploy

### Risks of ignoring
- Build failures
- Secrets kuvuja

### Expectations
- Improves: uthabiti wa deploy
- Does not guarantee: performance kamili

## How

### Step-by-step method
1. Unganisha repo yako na Vercel.
2. Weka env variables kwenye Vercel.
3. Deploy kwenye production.
4. Pitia build logs kwa errors.
5. Jaribu endpoint muhimu.

### Do and don't

**Do**
- Tumia env variables kwa secrets
- Hakikisha build inaendeshwa bila errors

**Don't**
- Ku-hardcode secrets kwenye code
- Kupuuza build logs

### Common mistakes and fixes
- **Mistake:** Env variables hazipo. **Fix:** Ziweke kwenye Vercel settings.
- **Mistake:** API key iko kwenye client. **Fix:** Hamisha kwenye server.

### Done when
- [ ] Deploy ya production imefanikiwa.
- [ ] Env variables muhimu zimewekwa.
- [ ] App inajibu kwa URL ya production.

## Guided exercise (10 to 15 min)

### Inputs
- Repo ya app
- Orodha ya env variables

### Steps
1. Unganisha repo na Vercel.
2. Weka env variables kwenye settings.
3. Deploy na jaribu URL.

### Output format
| Field | Value |
|---|---|
| Vercel project | |
| Env variables set | |
| Deployment URL | |
| Test result | |

> **Pro tip:** Weka env variables tofauti kwa staging na production.

## Independent exercise (5 to 10 min)

### Task
Ongeza env variable ya test na uhakikishe inafanya kazi.

### Output
Jedwali la env lililoboreshwa.

## Self-check (yes/no)

- [ ] Je, repo imeunganishwa na Vercel?
- [ ] Je, env variables muhimu zimewekwa?
- [ ] Je, build logs ni safi?
- [ ] Je, production URL inafanya kazi?

### Baseline metric (recommended)
- **Score:** Hatua 3 kati ya 4 zimekamilika
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Vercel Deployment Guide**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs

2. **Env Variables Best Practices**. GitHub. 2024-01-01.
   Read: https://docs.github.com/en/actions/security-guides/encrypted-secrets

## Read more (optional)

1. **Vercel Environment Variables**
   Why: Mpangilio wa secrets kwa deploy.
   Read: https://vercel.com/docs/projects/environment-variables
