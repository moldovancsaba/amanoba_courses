# Lesson 24: Stripe checkout integration

**One-liner:** Weka Stripe checkout ili uanze kupokea malipo kwa usalama.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Stripe Checkout Flow

## Learning goal

You will be able to: **Kuweka Stripe checkout flow inayofanya kazi.**

### Success criteria (observable)
- [ ] Checkout session inaundwa kwa bei sahihi.
- [ ] Mtumiaji anamaliza malipo na kurudi kwenye app.
- [ ] Receipt au status inaonekana.

### Output you will produce
- **Deliverable:** Stripe Checkout Flow
- **Format:** Flow steps na test log
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayejenga malipo ya app ya AI
**Secondary persona(s):** Wateja wanaolipia
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Muunganiko wa Stripe checkout unaomruhusu mtumiaji kulipa na kurudi kwenye app.
Inahakikisha malipo yanafanyika kwa njia salama na iliyo rahisi.

### What it is not
Si mfumo wa billing wa enterprise.
Si ujenzi wa payment UI kutoka sifuri.

### 2-minute theory
- Stripe checkout hupunguza kazi ya ulinzi na compliance.
- Flow rahisi hupunguza kuacha kulipa.
- Test mode hukuwezesha kujaribu bila hatari.

### Key terms
- **Checkout session:** Session ya malipo inayoanzishwa na Stripe.
- **Success URL:** URL ambayo mtumiaji anarudi baada ya malipo.

## Where

### Applies in
- Backend payment routes
- Checkout page

### Does not apply in
- App bila malipo

### Touchpoints
- Stripe dashboard
- Webhook logs
- Success page

## When

### Use it when
- Uko tayari kuanza kutoza malipo
- Unahitaji flow ya haraka ya malipo

### Frequency
Kila unapoongeza product mpya

### Late signals
- Checkout inarudi bila status
- Malipo yanashindwa bila maelezo

## Why it matters

### Practical benefits
- Malipo yanafanyika kwa urahisi
- Compliance ni rahisi
- Uaminifu wa wateja unaongezeka

### Risks of ignoring
- Malipo kukwama
- Uzoefu wa mtumiaji mbaya

### Expectations
- Improves: uwezo wa kutoza
- Does not guarantee: conversion kubwa

## How

### Step-by-step method
1. Tengeneza product na price kwenye Stripe.
2. Unda checkout session kwenye server.
3. Weka success URL na cancel URL.
4. Endesha test mode na kadi ya majaribio.
5. Thibitisha status ya malipo kwenye app.

### Do and don't

**Do**
- Tumia test mode kwanza
- Thibitisha status kwa server

**Don't**
- Kuamini status kutoka kwa client pekee
- Kuacha success URL bila ulinzi

### Common mistakes and fixes
- **Mistake:** Success URL hairejei kwenye app. **Fix:** Rekebisha URL na routes.
- **Mistake:** Bei si sahihi. **Fix:** Thibitisha price id na currency.

### Done when
- [ ] Checkout flow inaendeshwa kwa test mode.
- [ ] Success page inaonyesha status.
- [ ] Mtumiaji anarudi kwenye app bila makosa.

## Guided exercise (10 to 15 min)

### Inputs
- Stripe account
- Price id

### Steps
1. Unda product na price.
2. Unda checkout session.
3. Jaribu malipo kwenye test mode.

### Output format
| Field | Value |
|---|---|
| Product name | |
| Price id | |
| Success URL | |
| Test result | |

> **Pro tip:** Tumia Stripe test cards kwa majaribio.

## Independent exercise (5 to 10 min)

### Task
Badilisha checkout kwa bei nyingine na uthibitishe.

### Output
Price id mpya na test log.

## Self-check (yes/no)

- [ ] Je, checkout session inaundwa?
- [ ] Je, success URL inafanya kazi?
- [ ] Je, status ya malipo inathibitishwa?
- [ ] Je, test mode imepita?

### Baseline metric (recommended)
- **Score:** Hatua 3 kati ya 4 zimekamilika
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Stripe Checkout Guide**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/checkout

2. **Payment Security Basics**. PCI SSC. 2024-01-01.
   Read: https://www.pcisecuritystandards.org/

## Read more (optional)

1. **Stripe Testing**
   Why: Test mode kabla ya kwenda production.
   Read: https://stripe.com/docs/testing
