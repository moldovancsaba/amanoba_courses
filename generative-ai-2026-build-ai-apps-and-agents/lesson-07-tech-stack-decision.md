# Lesson 7: Tech stack decision

**One-liner:** Confirm a practical stack that supports fast delivery.  
**Time:** 20 to 30 min  
**Deliverable:** Stack Decision Doc

## Learning goal

You will be able to: **Select a stack that supports your MVP and constraints.**

### Success criteria (observable)
- [ ] The stack includes frontend, backend, hosting, and payments.
- [ ] The choice is justified with three reasons.
- [ ] The stack aligns with the time budget.

### Output you will produce
- **Deliverable:** Stack Decision Doc
- **Format:** One page doc
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad choosing a stack
**Secondary persona(s):** Contributors or collaborators
**Stakeholders (optional):** Early users

## What

### What it is
A practical choice of tools you can ship with now.
It balances speed, simplicity, and the required capabilities.

### What it is not
It is not a future proof architecture plan.

### 2-minute theory
- Simple stacks ship faster and break less often.
- Fewer services reduce setup and maintenance overhead.
- The best stack is the one you can deploy today.

### Key terms
- **Stack:** The set of tools used to build and run the product.
- **Constraint:** A limit like time, budget, or skills.

## Where

### Applies in
- Technical planning
- Build setup

### Does not apply in
- Long term scaling plans

### Touchpoints
- Repo README
- Deployment config
- Billing setup

## When

### Use it when
- You are ready to build
- You must decide the core tools

### Frequency
Once per product idea, revisit after launch

### Late signals
- You keep switching tools
- The project stalls due to setup

## Why it matters

### Practical benefits
- Faster development
- Clearer onboarding
- Easier debugging

### Risks of ignoring
- Tool churn
- Slow progress

### Expectations
- Improves: shipping speed
- Does not guarantee: scalability

## How

### Step-by-step method
1. List required capabilities.
2. Choose tools that match your skills.
3. Confirm hosting and payments.
4. Write three reasons for the choice.

### Do and don't

**Do**
- Prefer tools with clear docs and tutorials
- Minimize custom infrastructure

**Don't**
- Choose tools only for hype
- Add services you cannot maintain

### Common mistakes and fixes
- **Mistake:** Too many tools. **Fix:** Remove non essential services.
- **Mistake:** Stack does not support payments. **Fix:** Add Stripe from the start.

### Done when
- [ ] Frontend, backend, hosting, and payments are defined.
- [ ] Reasons are written and specific.
- [ ] The stack matches the time budget.

## Guided exercise (10 to 15 min)

### Inputs
- MVP scope
- Skills and constraints

### Steps
1. List required capabilities.
2. Pick tools for each capability.
3. Write three reasons for the stack.

### Output format
| Field | Value |
|---|---|
| Capability | Tool |
| Reason 1 | |
| Reason 2 | |
| Reason 3 | |

> **Pro tip:** A boring stack you can ship beats a perfect stack you cannot.

## Independent exercise (5 to 10 min)

### Task
Remove one tool and explain why the stack still works.

### Output
Updated stack decision doc.

## Self-check (yes/no)

- [ ] Does the stack cover frontend, backend, hosting, payments?
- [ ] Are the reasons tied to speed and simplicity?
- [ ] Can you build it with your current skills?
- [ ] Does it fit the time budget?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **The Pragmatic Programmer**. Andrew Hunt and David Thomas. 2024-01-01.
   Read: https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/

2. **Stripe Docs**. Stripe. 2024-01-01.
   Read: https://stripe.com/docs

## Read more (optional)

1. **Vercel Docs**
   Why: Practical hosting for fast MVPs.
   Read: https://vercel.com/docs
