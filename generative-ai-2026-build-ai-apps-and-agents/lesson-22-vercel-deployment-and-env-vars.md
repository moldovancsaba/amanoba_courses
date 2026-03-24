# Lesson 22: Vercel deployment and env vars

**One-liner:** Deploy to Vercel and configure environment variables safely.  
**Time:** 20 to 30 min  
**Deliverable:** Live Staging Deployment

## Learning goal

You will be able to: **Deploy the app to Vercel and manage environment variables.**

### Success criteria (observable)
- [ ] A staging deployment is live.
- [ ] Env vars are set in Vercel.
- [ ] The app runs with a test input.

### Output you will produce
- **Deliverable:** Live Staging Deployment
- **Format:** Deployment URL plus notes
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad deploying a commercial AI app
**Secondary persona(s):** Users testing the app
**Stakeholders (optional):** Collaborators

## What

### What it is
A staged deployment that mirrors production and uses real environment variables.
It proves the app works outside your laptop.

### What it is not
It is not a production release or a scaling plan.
It is a safe staging step.

### 2-minute theory
- Staging catches errors before real users see them.
- Env variables must be set in the platform, not in code.
- A live URL makes testing easier and faster.

### Key terms
- **Staging deployment:** A live environment for testing.
- **Env vars:** Key values set in the platform.

## Where

### Applies in
- Vercel dashboard
- Deployment settings

### Does not apply in
- Local only development

### Touchpoints
- Vercel project settings
- Env variable list
- Preview URL

## When

### Use it when
- The app runs locally
- You need a shareable test link

### Frequency
Once per product, update on each release

### Late signals
- Deployments fail due to missing env vars
- Staging behaves differently than local

## Why it matters

### Practical benefits
- Faster testing and feedback
- Early detection of deployment issues
- More confidence before launch

### Risks of ignoring
- Broken production releases
- Hard to reproduce bugs

### Expectations
- Improves: reliability and speed of feedback
- Does not guarantee: zero deployment issues

## How

### Step-by-step method
1. Connect the repo to Vercel.
2. Set env vars in the Vercel dashboard.
3. Trigger a deployment.
4. Run a test input on the live URL.

### Do and don't

**Do**
- Keep staging and production env vars separate
- Test with real inputs

**Don't**
- Store secrets in the repo
- Skip staging tests

### Common mistakes and fixes
- **Mistake:** Missing env vars. **Fix:** Add them in Vercel settings.
- **Mistake:** Testing only locally. **Fix:** Use the staging URL.

### Done when
- [ ] A staging URL is live.
- [ ] Env vars are set.
- [ ] A test input works.

## Guided exercise (10 to 15 min)

### Inputs
- Vercel account
- Repo connected to Vercel

### Steps
1. Create a new Vercel project.
2. Add env vars.
3. Deploy and test.

### Output format
| Field | Value |
|---|---|
| Staging URL | |
| Env vars set | |
| Test input | |
| Result | |

> **Pro tip:** Add a staging banner so you never confuse it with production.

## Independent exercise (5 to 10 min)

### Task
Add a new env var and redeploy.

### Output
Updated deployment notes.

## Self-check (yes/no)

- [ ] Is the staging URL live?
- [ ] Are env vars set in Vercel?
- [ ] Does a test input work?
- [ ] Is staging clearly labeled?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Vercel

## Bibliography (sources used)

1. **Vercel Docs**. Vercel. 2024-01-01.
   Read: https://vercel.com/docs

2. **12 Factor App Config**. 2024-01-01.
   Read: https://12factor.net/config

## Read more (optional)

1. **Vercel Env Vars**
   Why: Best practices for environment config.
   Read: https://vercel.com/docs/projects/environment-variables
