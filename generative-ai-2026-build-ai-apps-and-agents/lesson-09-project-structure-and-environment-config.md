# Lesson 9: Project structure and environment config

**One-liner:** Set up folders, configs, and environment secrets safely.  
**Time:** 20 to 30 min  
**Deliverable:** Project Skeleton and Env Template

## Learning goal

You will be able to: **Create a clean project structure and safe environment setup.**

### Success criteria (observable)
- [ ] Project folders match the app workflow.
- [ ] Env template lists required variables.
- [ ] Secrets are not committed.

### Output you will produce
- **Deliverable:** Project Skeleton and Env Template
- **Format:** Folder tree and .env.example
- **Where saved:** Repo plus course folder notes

## Who

**Primary persona:** Digital nomad building the app foundation
**Secondary persona(s):** Collaborators
**Stakeholders (optional):** Early users

## What

### What it is
A minimal folder structure plus an env template that keeps secrets safe.
It makes local setup and deployment consistent.

### What it is not
It is not a full security program or architecture overhaul.

### 2-minute theory
- Clear structure speeds development and reduces confusion.
- Env templates prevent missing keys and broken deployments.
- Keeping secrets out of code avoids expensive mistakes.

### Key terms
- **Env template:** A file listing required environment variables.
- **Project skeleton:** The minimum folder structure to build the app.

## Where

### Applies in
- Local development
- Deployment setup

### Does not apply in
- UI design decisions

### Touchpoints
- .env.example
- .gitignore
- Project folders

## When

### Use it when
- Starting development
- Preparing for deployment

### Frequency
Once per project, update when adding services

### Late signals
- Missing env vars cause crashes
- Code and configs are mixed together

## Why it matters

### Practical benefits
- Faster setup
- Fewer secrets leaks
- Cleaner onboarding

### Risks of ignoring
- Broken deployments
- Exposed API keys

### Expectations
- Improves: reliability and safety
- Does not guarantee: security

## How

### Step-by-step method
1. Create a basic folder tree.
2. Add a .env.example with required keys.
3. Update .gitignore to exclude real secrets.
4. Validate local run with dummy values.

### Do and don't

**Do**
- Keep configuration separate from code
- Document required variables

**Don't**
- Commit real API keys
- Hide required variables inside code

### Common mistakes and fixes
- **Mistake:** Missing env template. **Fix:** Add .env.example.
- **Mistake:** Secrets in repo. **Fix:** Rotate keys and remove from history.

### Done when
- [ ] Folder tree exists and is clear.
- [ ] .env.example lists required variables.
- [ ] .gitignore excludes .env files.

## Guided exercise (10 to 15 min)

### Inputs
- MVP feature list
- Stack choices

### Steps
1. Create the folder tree.
2. Add .env.example.
3. Confirm .gitignore includes .env.

### Output format
| Field | Value |
|---|---|
| Folder tree | |
| Env template keys | |
| Gitignore status | |
| Local run result | |

> **Pro tip:** Treat env templates as part of onboarding documentation.

## Independent exercise (5 to 10 min)

### Task
Add one new required variable and update the template.

### Output
Updated .env.example entry.

## Self-check (yes/no)

- [ ] Are required env vars listed?
- [ ] Are secrets excluded from git?
- [ ] Is the folder structure clear?
- [ ] Can the app run with dummy values?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Terminal

## Bibliography (sources used)

1. **12 Factor App Config**. 2024-01-01.
   Read: https://12factor.net/config

2. **GitHub Secrets Guide**. 2024-01-01.
   Read: https://docs.github.com/en/actions/security-guides/encrypted-secrets

## Read more (optional)

1. **Vercel Environment Variables**
   Why: Practical deployment setup.
   Read: https://vercel.com/docs/projects/environment-variables
