# Lesson 25: Stripe webhooks na access control

**One-liner:** Tumia webhooks kuthibitisha malipo na kudhibiti upatikanaji.  
**Time:** 20 hadi 30 dakika  
**Deliverable:** Webhook Flow na Access Rules

## Learning goal

You will be able to: **Kuweka Stripe webhook na sheria za access kwa wateja waliolipia.**

### Success criteria (observable)
- [ ] Webhook endpoint inathibitisha signatures.
- [ ] Status ya malipo inaathiri access.
- [ ] Test event imepita.

### Output you will produce
- **Deliverable:** Webhook Flow na Access Rules
- **Format:** Mchoro wa flow na rules
- **Where saved:** Kwenye folda ya kozi ndani ya `/generative-ai-2026-build-ai-apps-and-agents-sw/`

## Who

**Primary persona:** Digital nomad anayehakikisha malipo na access
**Secondary persona(s):** Wateja wanaolipia
**Stakeholders (optional):** Washirika wa ujenzi

## What

### What it is
Webhook inayopokea events za Stripe na kuthibitisha status ya malipo.
Sheria zinazowezesha au kuzuia access kulingana na status.

### What it is not
Si mfumo kamili wa billing.
Si ulinzi wa juu bila user management.

### 2-minute theory
- Webhooks ni chanzo cha ukweli cha malipo.
- Signature verification huzuia events bandia.
- Access control inalinda bidhaa dhidi ya matumizi yasiyoruhusiwa.

### Key terms
- **Webhook:** Endpoint inayopokea event kutoka huduma ya nje.
- **Signature verification:** Uthibitisho wa kuwa event ni halali.

## Where

### Applies in
- Backend routes
- Access middleware

### Does not apply in
- Apps bila malipo

### Touchpoints
- Stripe dashboard
- Webhook logs
- Access checks

## When

### Use it when
- Unaanza kutoza malipo
- Unahitaji kudhibiti access

### Frequency
Kila unapoongeza plan mpya

### Late signals
- Wateja wanapata access bila kulipa
- Access inakatika baada ya malipo

## Why it matters

### Practical benefits
- Access sahihi kwa wateja waliolipia
- Kupunguza udanganyifu
- Uaminifu wa mfumo unaongezeka

### Risks of ignoring
- Upotevu wa mapato
- Wateja kukosa access isivyo sahihi

### Expectations
- Improves: uaminifu na udhibiti
- Does not guarantee: zero fraud

## How

### Step-by-step method
1. Unda webhook endpoint kwenye server.
2. Weka Stripe signing secret kwenye env.
3. Thibitisha signature ya event.
4. Sasisha status ya malipo kwenye database.
5. Tumia status kudhibiti access.

### Do and don't

**Do**
- Validate signature ya kila event
- Log events muhimu

**Don't**
- Kuamini client kwa status ya malipo
- Kuacha webhook bila retry

### Common mistakes and fixes
- **Mistake:** Signature haijathibitishwa. **Fix:** Tumia signing secret ya Stripe.
- **Mistake:** Access haijasasishwa. **Fix:** Tumia webhook kusasisha status.

### Done when
- [ ] Webhook endpoint inafanya kazi.
- [ ] Signature verification imepita.
- [ ] Access inaendana na status.

## Guided exercise (10 to 15 min)

### Inputs
- Stripe signing secret
- Orodha ya events muhimu

### Steps
1. Sanidi webhook endpoint.
2. Thibitisha signature.
3. Test event na uandike matokeo.

### Output format
| Field | Value |
|---|---|
| Webhook URL | |
| Event type | |
| Signature status | |
| Access change | |

> **Pro tip:** Weka retry logic kwa events zinazoshindwa.

## Independent exercise (5 to 10 min)

### Task
Ongeza event mpya na ueleze jinsi inavyoathiri access.

### Output
Event mpya na rule yake.

## Self-check (yes/no)

- [ ] Je, webhook inathibitisha signature?
- [ ] Je, status inasasishwa kwenye database?
- [ ] Je, access inafuatana na status?
- [ ] Je, test event imepita?

### Baseline metric (recommended)
- **Score:** Hatua 3 kati ya 4 zimekamilika
- **Date:** 2026-02-07
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Stripe Webhooks**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/webhooks

2. **Webhook Security**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/webhooks/signatures

## Read more (optional)

1. **Access Control Basics**
   Why: Msingi wa kudhibiti upatikanaji.
   Read: https://owasp.org/
