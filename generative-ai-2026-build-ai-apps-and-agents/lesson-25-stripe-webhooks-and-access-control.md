# Lesson 25: Stripe webhooks and access control

**One-liner:** Grant access when payment succeeds and revoke when it does not.  
**Time:** 20 to 30 min  
**Deliverable:** Webhook Handler and Access Gate

## Learning goal

You will be able to: **Handle Stripe webhooks and gate paid features.**

### Success criteria (observable)
- [ ] Webhook handler validates the event signature.
- [ ] Paid users are granted access.
- [ ] Failed payments do not grant access.

### Output you will produce
- **Deliverable:** Webhook Handler and Access Gate
- **Format:** Code snippet plus test log
- **Where saved:** Repo and course folder notes

## Who

**Primary persona:** Digital nomad adding payment gating
**Secondary persona(s):** Paying users who expect access
**Stakeholders (optional):** Collaborators

## What

### What it is
A webhook endpoint that listens for payment events and updates access.
It ensures only paid users can use paid features.

### What it is not
It is not a full billing portal or complex subscription management.
It is a clean access gate for the first paid plan.

### 2-minute theory
- Payments and access must be linked to prevent leaks.
- Webhooks are the source of truth for payment events.
- Signature checks prevent spoofed events.

### Key terms
- **Webhook:** A server endpoint that receives Stripe events.
- **Access gate:** Logic that allows paid features only for eligible users.

## Where

### Applies in
- Backend webhooks
- Access checks

### Does not apply in
- Marketing content

### Touchpoints
- Webhook endpoint
- User access flags
- Payment logs

## When

### Use it when
- You add paid access
- You need to grant or revoke features

### Frequency
Once per product, update with pricing changes

### Late signals
- Users report paying but no access
- Free users access paid features

## Why it matters

### Practical benefits
- Reliable paid access
- Fewer support tickets
- Clear payment status

### Risks of ignoring
- Revenue loss
- User distrust

### Expectations
- Improves: payment reliability
- Does not guarantee: no billing edge cases

## How

### Step-by-step method
1. Create a webhook endpoint on the server.
2. Validate the Stripe signature.
3. Handle payment success and failure events.
4. Update user access status.

### Do and don't

**Do**
- Validate signatures on every webhook
- Log webhook events

**Don't**
- Trust client side payment status
- Grant access without verification

### Common mistakes and fixes
- **Mistake:** No signature check. **Fix:** Validate signature.
- **Mistake:** Access updated on client. **Fix:** Update on server.

### Done when
- [ ] Webhook verifies signatures.
- [ ] Access is granted on payment success.
- [ ] Access is denied on failure.

## Guided exercise (10 to 15 min)

### Inputs
- Stripe webhook secret
- Payment success event

### Steps
1. Create the webhook handler.
2. Verify signature.
3. Update access and log result.

### Output format
| Field | Value |
|---|---|
| Webhook endpoint | |
| Signature check | |
| Access update | |
| Test result | |

> **Pro tip:** Use Stripe CLI to trigger test events.

## Independent exercise (5 to 10 min)

### Task
Add handling for a payment failure event.

### Output
Updated webhook logic.

## Self-check (yes/no)

- [ ] Are webhook signatures verified?
- [ ] Is access granted only on success?
- [ ] Are failures handled?
- [ ] Are events logged?

### Baseline metric (recommended)
- **Score:** 1 successful test event handled
- **Date:** 2026-02-06
- **Tool used:** Stripe CLI

## Bibliography (sources used)

1. **Stripe Webhooks Docs**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/webhooks

2. **Stripe CLI**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/stripe-cli

## Read more (optional)

1. **Webhook Security**
   Why: How to validate and secure webhooks.
   Read: https://stripe.com/docs/webhooks/signatures
