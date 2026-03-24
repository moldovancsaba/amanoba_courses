# Lesson 15: Cost control and rate limits

**One-liner:** Add guardrails that keep AI costs predictable.  
**Time:** 20 to 30 min  
**Deliverable:** Cost Guard Checklist and Limits

## Learning goal

You will be able to: **Set cost and rate limits that protect your AI product.**

### Success criteria (observable)
- [ ] A cost guard checklist is complete.
- [ ] Rate limits are defined for key endpoints.
- [ ] A monthly cost cap is written.

### Output you will produce
- **Deliverable:** Cost Guard Checklist and Limits
- **Format:** Checklist plus limits table
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad managing AI costs
**Secondary persona(s):** Paying users who expect stable service
**Stakeholders (optional):** Collaborators

## What

### What it is
A small set of rules that limit usage, protect your budget, and keep the service stable.
It combines a cost cap with rate limits so one user cannot burn the budget.

### What it is not
It is not a full finance system or a replacement for pricing strategy.
It is a safety layer for early stage products.

### 2-minute theory
- AI costs can grow quickly with heavy use.
- Rate limits protect both stability and budget.
- Clear caps make it safe to test pricing.

### Key terms
- **Rate limit:** A rule that limits requests per user or per time window.
- **Cost cap:** A maximum amount you are willing to spend per period.

## Where

### Applies in
- API routes
- Billing logic

### Does not apply in
- One off manual tests

### Touchpoints
- Usage logs
- Billing dashboard
- Alerting rules

## When

### Use it when
- You open the app to real users
- You start charging money

### Frequency
Set once, adjust as usage grows

### Late signals
- Unusual spikes in usage
- Bills higher than expected

## Why it matters

### Practical benefits
- Predictable costs
- Fewer outages
- Better control of free usage

### Risks of ignoring
- Surprise bills
- Abuse by heavy users

### Expectations
- Improves: cost stability and safety
- Does not guarantee: perfect margins

## How

### Step-by-step method
1. Choose a monthly cost cap.
2. Define per user rate limits.
3. Add a daily limit for free users.
4. Set alerts for spikes.
5. Review usage weekly.

### Do and don't

**Do**
- Start with conservative limits
- Log usage per user

**Don't**
- Offer unlimited free usage without controls
- Wait for a bill to react

### Common mistakes and fixes
- **Mistake:** No cap. **Fix:** Set a small monthly cap.
- **Mistake:** No per user limits. **Fix:** Add rate limits per user.

### Done when
- [ ] A monthly cost cap is written.
- [ ] Rate limits are defined.
- [ ] Alerts are configured.

## Guided exercise (10 to 15 min)

### Inputs
- Expected usage per user
- Current pricing hypothesis

### Steps
1. Estimate cost per request.
2. Set a monthly budget.
3. Define per user limits.

### Output format
| Field | Value |
|---|---|
| Cost per request | |
| Monthly cap | |
| Rate limits | |
| Alert trigger | |

> **Pro tip:** Start with a low cap and increase after you see real usage.

## Independent exercise (5 to 10 min)

### Task
Create a rule for heavy users and document the action.

### Output
A heavy user rule and response.

## Self-check (yes/no)

- [ ] Is a monthly cap defined?
- [ ] Are per user limits defined?
- [ ] Are alerts configured?
- [ ] Is usage reviewed weekly?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Pricing**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/pricing

2. **API Rate Limiting Guide**. Cloudflare. 2024-01-01.
   Read: https://developers.cloudflare.com/rate-limits/

## Read more (optional)

1. **Usage Based Pricing**
   Why: Align costs with pricing plans.
   Read: https://www.profitwell.com/recur/all/usage-based-pricing
