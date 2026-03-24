# Lesson 18: Error handling and fallbacks

**One-liner:** Add clear recovery paths when the AI fails.  
**Time:** 20 to 30 min  
**Deliverable:** Fallback Logic and Error Responses

## Learning goal

You will be able to: **Design fallback responses that keep users moving.**

### Success criteria (observable)
- [ ] At least 3 error types are handled.
- [ ] Each error has a user safe message.
- [ ] A retry path is defined.

### Output you will produce
- **Deliverable:** Fallback Logic and Error Responses
- **Format:** Error table plus messages
- **Where saved:** Repo and course folder notes

## Who

**Primary persona:** Digital nomad designing error recovery
**Secondary persona(s):** Users who need clarity
**Stakeholders (optional):** Collaborators

## What

### What it is
A small set of user friendly responses for common failure cases.
It keeps the user on track even when the AI fails.

### What it is not
It is not full incident response or SLA planning.
It is a practical layer for a small app.

### 2-minute theory
- Errors are inevitable, so recovery must be planned.
- Clear messages reduce frustration and support load.
- Retry paths help users succeed without leaving.

### Key terms
- **Fallback:** A safe response when the primary action fails.
- **Retry path:** A clear way for users to try again.

## Where

### Applies in
- API responses
- UI error states

### Does not apply in
- Marketing pages

### Touchpoints
- Error screens
- Logs
- Support messages

## When

### Use it when
- You ship a user facing AI feature
- You see error logs in testing

### Frequency
Once per feature, revise when new errors appear

### Late signals
- Users report being stuck
- Support tickets mention unclear errors

## Why it matters

### Practical benefits
- Better user trust
- Fewer rage quits
- Clearer debugging

### Risks of ignoring
- Confused users
- Higher support load

### Expectations
- Improves: resilience and trust
- Does not guarantee: zero errors

## How

### Step-by-step method
1. List the top 3 error cases.
2. Write a user safe message for each.
3. Add a retry path or alternate action.
4. Log each error with context.

### Do and don't

**Do**
- Be polite and specific
- Offer a next step

**Don't**
- Show stack traces to users
- Blame the user

### Common mistakes and fixes
- **Mistake:** Generic error text. **Fix:** Add a clear action.
- **Mistake:** No retry. **Fix:** Add a retry button or link.

### Done when
- [ ] Three error cases are defined.
- [ ] Messages are clear and polite.
- [ ] Retry paths are in place.

## Guided exercise (10 to 15 min)

### Inputs
- Error logs from tests
- Common failure cases

### Steps
1. Pick three error types.
2. Write a user message for each.
3. Add a retry path.

### Output format
| Field | Value |
|---|---|
| Error type | |
| User message | |
| Retry action | |
| Log field | |

> **Pro tip:** Short messages with a next action perform best.

## Independent exercise (5 to 10 min)

### Task
Rewrite one error message to be shorter and clearer.

### Output
Revised error message.

## Self-check (yes/no)

- [ ] Are top error types listed?
- [ ] Are messages user safe?
- [ ] Is there a retry action?
- [ ] Are errors logged?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Error Messages Best Practices**. NNGroup. 2024-01-01.
   Read: https://www.nngroup.com/articles/error-message-guidelines/

2. **Reliable Systems**. Google SRE. 2024-01-01.
   Read: https://sre.google/books/

## Read more (optional)

1. **Designing Error States**
   Why: Patterns for helpful error messages.
   Read: https://www.nngroup.com/articles/error-message-guidelines/
