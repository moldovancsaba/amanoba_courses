# Lesson 23: Domain and production readiness

**One-liner:** Prepare the app for a production release.  
**Time:** 20 to 30 min  
**Deliverable:** Production Readiness Checklist

## Learning goal

You will be able to: **Prepare a basic production readiness checklist.**

### Success criteria (observable)
- [ ] Domain and SSL status are confirmed.
- [ ] Key pages work on production.
- [ ] A release checklist is completed.

### Output you will produce
- **Deliverable:** Production Readiness Checklist
- **Format:** Checklist
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad preparing for launch
**Secondary persona(s):** Users who will test the live app
**Stakeholders (optional):** Collaborators

## What

### What it is
A short checklist that confirms the app is ready for production use.
It covers domain setup, SSL, and key user flows.

### What it is not
It is not a full scale release engineering process.
It is a practical launch gate for a small app.

### 2-minute theory
- Production readiness reduces launch day surprises.
- Simple checklists catch the most common issues.
- A clear go or no go step prevents rushed releases.

### Key terms
- **Domain:** The public URL users will visit.
- **SSL:** Secure connection that protects user data.

## Where

### Applies in
- Domain setup
- Production deployment

### Does not apply in
- Local only testing

### Touchpoints
- DNS settings
- SSL status
- Production URL

## When

### Use it when
- You are ready to launch
- You want to reduce risk before going live

### Frequency
Once per release

### Late signals
- Broken pages after launch
- Users report SSL warnings

## Why it matters

### Practical benefits
- Safer launches
- Fewer user trust issues
- Clear release decisions

### Risks of ignoring
- Broken first impressions
- Security warnings

### Expectations
- Improves: launch quality and trust
- Does not guarantee: zero bugs

## How

### Step-by-step method
1. Connect the domain and confirm SSL.
2. Test the main user flow in production.
3. Check login, payment, and output.
4. Sign off on the checklist.

### Do and don't

**Do**
- Test the core flow end to end
- Confirm SSL before launch

**Don't**
- Launch without a final check
- Ignore broken links

### Common mistakes and fixes
- **Mistake:** No SSL. **Fix:** Wait until SSL is active.
- **Mistake:** Only tested locally. **Fix:** Test the production URL.

### Done when
- [ ] Domain is connected and SSL is active.
- [ ] Core flow works in production.
- [ ] Checklist is signed off.

## Guided exercise (10 to 15 min)

### Inputs
- Production URL
- Release checklist template

### Steps
1. Verify domain and SSL.
2. Test the main flow.
3. Mark each checklist item.

### Output format
| Field | Value |
|---|---|
| Domain | |
| SSL status | |
| Core flow test | |
| Sign off | |

> **Pro tip:** Do one test on mobile and one on desktop before launch.

## Independent exercise (5 to 10 min)

### Task
Test the checkout flow and record the result.

### Output
Checkout test note.

## Self-check (yes/no)

- [ ] Is SSL active?
- [ ] Does the main flow work?
- [ ] Is the checklist complete?
- [ ] Is a release decision made?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Browser

## Bibliography (sources used)

1. **Vercel Domains**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs/projects/domains

2. **Google HTTPS Guidelines**. Google. 2024-01-01.
   Read: https://developers.google.com/search/docs/advanced/security/https

## Read more (optional)

1. **Launch Checklist**
   Why: Common items for production readiness.
   Read: https://www.atlassian.com/incident-management/devops/release-checklist
