# Lesson 21: Security and privacy essentials

**One-liner:** Add minimal security and privacy practices for a commercial AI app.  
**Time:** 20 to 30 min  
**Deliverable:** Security Checklist and Privacy Notes

## Learning goal

You will be able to: **Apply basic security and privacy safeguards suitable for an early stage product.**

### Success criteria (observable)
- [ ] A basic security checklist is completed.
- [ ] Sensitive data and secrets are identified.
- [ ] A short privacy note is written for users.

### Output you will produce
- **Deliverable:** Security Checklist and Privacy Notes
- **Format:** Checklist plus short policy note
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad shipping a commercial AI app
**Secondary persona(s):** Users who care about safety and privacy
**Stakeholders (optional):** Collaborators

## What

### What it is
A short set of practical security and privacy steps that reduce obvious risks.
It focuses on secrets, access, and user data handling.

### What it is not
It is not a full compliance program or enterprise security audit.
It is a starter layer that prevents avoidable mistakes.

### 2-minute theory
- Small apps still face real security risks.
- Clear privacy notes build trust and reduce confusion.
- A few basic controls cover most early stage risks.

### Key terms
- **Secret:** A key or token that grants access.
- **Privacy note:** A short summary of what data is stored and why.

## Where

### Applies in
- API routes
- Admin access
- Data storage

### Does not apply in
- Visual design tasks

### Touchpoints
- Env variables
- Access controls
- Privacy note

## When

### Use it when
- You prepare for public use
- You handle user data

### Frequency
Once per product, revisit with new features

### Late signals
- Secrets appear in logs
- Users ask how data is handled

## Why it matters

### Practical benefits
- Reduced risk of leaks
- Clear user trust signals
- Fewer emergency fixes

### Risks of ignoring
- Leaked keys or data
- Loss of user trust

### Expectations
- Improves: safety and trust
- Does not guarantee: full compliance

## How

### Step-by-step method
1. List all secrets and where they are stored.
2. Add access rules for admin and data.
3. Write a short privacy note.
4. Remove any sensitive data you do not need.

### Do and don't

**Do**
- Store secrets in env variables
- Limit admin access

**Don't**
- Commit secrets to git
- Store data you do not need

### Common mistakes and fixes
- **Mistake:** Secrets in code. **Fix:** Move to env and rotate keys.
- **Mistake:** No privacy note. **Fix:** Write a short summary for users.

### Done when
- [ ] Secrets are inventoried and secured.
- [ ] Access is limited for admin actions.
- [ ] Privacy note is written.

## Guided exercise (10 to 15 min)

### Inputs
- Current codebase
- List of data collected

### Steps
1. Identify secrets and where they live.
2. Write a short privacy note.
3. Remove one unnecessary data item.

### Output format
| Field | Value |
|---|---|
| Secrets list | |
| Access rules | |
| Privacy note | |
| Removed data | |

> **Pro tip:** If you do not need the data to deliver the outcome, do not store it.

## Independent exercise (5 to 10 min)

### Task
Review one API route and ensure it checks access.

### Output
Access check note.

## Self-check (yes/no)

- [ ] Are secrets secured and not in code?
- [ ] Is admin access limited?
- [ ] Is a privacy note written?
- [ ] Is unnecessary data removed?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OWASP Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-top-ten/

2. **NIST Privacy Framework**. NIST. 2024-01-01.
   Read: https://www.nist.gov/privacy-framework

## Read more (optional)

1. **API Security Checklist**
   Why: Quick safeguards for small apps.
   Read: https://cheatsheetseries.owasp.org/
