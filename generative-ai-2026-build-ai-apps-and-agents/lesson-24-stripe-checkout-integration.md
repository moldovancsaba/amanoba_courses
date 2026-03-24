# Lesson 24: Stripe checkout integration

**One-liner:** Add a working Stripe checkout flow.  
**Time:** 20 to 30 min  
**Deliverable:** Working Checkout Session

## Learning goal

You will be able to: **Create a Stripe checkout session for a paid plan.**

### Success criteria (observable)
- [ ] Checkout session is created server side.
- [ ] User is redirected to Stripe successfully.
- [ ] A test payment completes.

### Output you will produce
- **Deliverable:** Working Checkout Session
- **Format:** Code snippet plus test log
- **Where saved:** Repo and course folder notes

## Who

**Primary persona:** Digital nomad adding payments
**Secondary persona(s):** Users ready to pay
**Stakeholders (optional):** Collaborators

## What

### What it is
A working checkout flow that lets a user pay for access.
It uses Stripe hosted checkout for speed and reliability.

### What it is not
It is not a full billing system or subscription management portal.
It is the first payment flow.

### 2-minute theory
- Hosted checkout reduces compliance burden.
- Fast payment flows increase conversion.
- Testing with Stripe test mode prevents mistakes.

### Key terms
- **Checkout session:** A Stripe hosted payment flow.
- **Test mode:** A safe environment for fake payments.

## Where

### Applies in
- Backend payment route
- Pricing page button

### Does not apply in
- Local only demos without payments

### Touchpoints
- Pricing page
- Stripe dashboard
- Payment success page

## When

### Use it when
- You are ready to take payments
- Pricing is defined

### Frequency
Once per product, update with pricing changes

### Late signals
- Users cannot pay
- Payment errors increase

## Why it matters

### Practical benefits
- You can charge money
- Fewer payment errors
- Faster path to revenue

### Risks of ignoring
- No monetization
- Manual payment work

### Expectations
- Improves: revenue readiness
- Does not guarantee: sales

## How

### Step-by-step method
1. Create a Stripe account and test keys.
2. Add a server endpoint to create a checkout session.
3. Redirect users to the checkout URL.
4. Complete a test payment.

### Do and don't

**Do**
- Use test mode for initial checks
- Keep price ids in env vars

**Don't**
- Put Stripe secrets in the client
- Skip a test payment

### Common mistakes and fixes
- **Mistake:** Client uses secret key. **Fix:** Move to server.
- **Mistake:** No test payment. **Fix:** Use Stripe test cards.

### Done when
- [ ] Checkout session is created server side.
- [ ] Redirect works.
- [ ] Test payment is successful.

## Guided exercise (10 to 15 min)

### Inputs
- Stripe test keys
- Product price id

### Steps
1. Create the checkout session endpoint.
2. Connect the pricing page button.
3. Run a test payment.

### Output format
| Field | Value |
|---|---|
| Checkout endpoint | |
| Test payment result | |
| Success URL | |
| Failure handling | |

> **Pro tip:** Start with one simple plan and add more later.

## Independent exercise (5 to 10 min)

### Task
Add a second price option in test mode.

### Output
Updated pricing notes.

## Self-check (yes/no)

- [ ] Does checkout create a session on the server?
- [ ] Does the redirect work?
- [ ] Does a test payment succeed?
- [ ] Are keys stored in env vars?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Stripe

## Bibliography (sources used)

1. **Stripe Checkout Docs**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/payments/checkout

2. **Stripe Testing Guide**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs/testing

## Read more (optional)

1. **Payments Best Practices**
   Why: Avoid common integration mistakes.
   Read: https://stripe.com/guides/payment-methods-guide
