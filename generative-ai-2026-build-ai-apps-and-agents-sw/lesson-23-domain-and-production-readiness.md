# Lesson 23: Domain na production readiness

**One-liner:** Andaa domain na hakikisha app iko tayari kwa production.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Checklist ya Production Readiness

## Learning goal

You will be able to: **Kuweka domain na kuthibitisha app iko tayari kwa production.**

### Success criteria (observable)
- [ ] Domain imeunganishwa na SSL iko active.
- [ ] Health check ya app imefanya kazi.
- [ ] Checklist ya readiness imekamilika.

### Output you will produce
- **Deliverable:** Checklist ya Production Readiness
- **Format:** Orodha ya ukaguzi
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayefanya app iwe tayari kwa production
**Secondary persona(s):** Watumiaji wa kwanza wa bidhaa
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Hatua za kuunganisha domain na kuhakikisha app iko salama kwa production.
Inajumuisha SSL, health check, na hatua za mwisho kabla ya uzinduzi.

### What it is not
Si mpango kamili wa SRE.
Si monitoring ya juu ya kiwango cha enterprise.

### 2-minute theory
- Domain ya kawaida inaongeza uaminifu.
- SSL inalinda data kwa transit.
- Checklist hupunguza makosa ya dakika ya mwisho.

### Key terms
- **SSL:** Ulinzi wa data wakati wa kusafiri kwenye mtandao.
- **Health check:** Ukaguzi wa haraka wa hali ya app.

## Where

### Applies in
- Domain provider
- Vercel settings

### Does not apply in
- Apps za ndani zisizo online

### Touchpoints
- DNS records
- SSL status
- Health endpoint

## When

### Use it when
- Uko tayari kufanya launch
- Unataka domain rasmi

### Frequency
Kila uzinduzi mkubwa

### Late signals
- SSL haijawashwa
- Health check inashindwa

## Why it matters

### Practical benefits
- Uaminifu wa mtumiaji unaongezeka
- Data inalindwa
- Uzinduzi unaenda vizuri

### Risks of ignoring
- Warnings za browser
- Uaminifu kupungua

### Expectations
- Improves: uaminifu na usalama
- Does not guarantee: uptime ya asilimia 100

## How

### Step-by-step method
1. Nunua au tumia domain uliyo nayo.
2. Weka DNS records kwa Vercel.
3. Thibitisha SSL inafanya kazi.
4. Endesha health check.
5. Kamilisha checklist ya readiness.

### Do and don't

**Do**
- Tumia domain rahisi kukumbuka
- Hakikisha SSL ni active

**Don't**
- Ku-launch bila health check
- Kuacha DNS records bila uhakiki

### Common mistakes and fixes
- **Mistake:** DNS imewekwa vibaya. **Fix:** Thibitisha records na subdomain.
- **Mistake:** SSL haijawashwa. **Fix:** Kamilisha verification ya domain.

### Done when
- [ ] Domain inaonyesha app.
- [ ] SSL ni active.
- [ ] Health check imepita.

## Guided exercise (10 to 15 min)

### Inputs
- Domain unayomiliki
- Vercel project

### Steps
1. Weka DNS records.
2. Thibitisha SSL.
3. Endesha health check.

### Output format
| Field | Value |
|---|---|
| Domain | |
| SSL status | |
| Health check | |
| Notes | |

> **Pro tip:** Tumia subdomain kwa staging ili production ibaki safi.

## Independent exercise (5 to 10 min)

### Task
Ongeza health check endpoint kwenye app.

### Output
URL ya health check na matokeo.

## Self-check (yes/no)

- [ ] Je, domain inaonyesha app?
- [ ] Je, SSL ni active?
- [ ] Je, health check imepita?
- [ ] Je, checklist imekamilika?

### Baseline metric (recommended)
- **Score:** Hatua 3 kati ya 4 zimekamilika
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Vercel Domains**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs

2. **SSL Basics**. Cloudflare. 2024-01-01.
   Read: https://www.cloudflare.com/learning/ssl/what-is-ssl/

## Read more (optional)

1. **Production Readiness Checklist**
   Why: Uhakiki wa mwisho kabla ya launch.
   Read: https://vercel.com/docs
