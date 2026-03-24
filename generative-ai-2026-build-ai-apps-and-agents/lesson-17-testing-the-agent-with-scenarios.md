# Lesson 17: Testing the agent with scenarios

**One-liner:** Validate the agent with real user scenarios.  
**Time:** 20 to 30 min  
**Deliverable:** Scenario Test Report

## Learning goal

You will be able to: **Test the agent with real scenarios and record results.**

### Success criteria (observable)
- [ ] At least 5 scenarios are written.
- [ ] Each scenario has expected outcomes.
- [ ] Results are recorded with pass or fail.

### Output you will produce
- **Deliverable:** Scenario Test Report
- **Format:** Scenario table plus notes
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad validating agent behavior
**Secondary persona(s):** Users relying on consistent output
**Stakeholders (optional):** Collaborators

## What

### What it is
A small set of realistic scenarios that test whether the agent behaves as expected.
It gives you evidence of what works and what fails.

### What it is not
It is not an automated test suite or a replacement for user feedback.
It is a practical check for early stage quality.

### 2-minute theory
- Scenarios mimic how real users will try the product.
- Expected outcomes make results measurable.
- Regular scenario tests reduce regressions.

### Key terms
- **Scenario:** A realistic input and context a user might provide.
- **Expected outcome:** The result you want the agent to produce.

## Where

### Applies in
- QA checks
- Feature validation

### Does not apply in
- UI color choices

### Touchpoints
- Test logs
- Output reviews
- Bug reports

## When

### Use it when
- You finish a new agent workflow
- Output quality is uncertain

### Frequency
Before each release

### Late signals
- Repeated user complaints about output
- Unexpected agent behavior

## Why it matters

### Practical benefits
- Fewer production surprises
- Faster debugging
- Better user trust

### Risks of ignoring
- Low quality releases
- Support overload

### Expectations
- Improves: reliability and confidence
- Does not guarantee: perfect accuracy

## How

### Step-by-step method
1. Write 5 realistic scenarios.
2. Define expected outcomes.
3. Run each scenario.
4. Record pass or fail with notes.

### Do and don't

**Do**
- Use real inputs from your niche
- Record failures clearly

**Don't**
- Only test ideal cases
- Skip documenting results

### Common mistakes and fixes
- **Mistake:** Ideal inputs only. **Fix:** Add messy inputs.
- **Mistake:** No expected outcome. **Fix:** Define one per scenario.

### Done when
- [ ] Five scenarios are documented.
- [ ] Expected outcomes are written.
- [ ] Results are recorded.

## Guided exercise (10 to 15 min)

### Inputs
- Your prompt spec
- Sample user inputs

### Steps
1. Write 5 scenarios.
2. Define expected outcomes.
3. Run and record results.

### Output format
| Field | Value |
|---|---|
| Scenario | |
| Expected outcome | |
| Result | |
| Notes | |

> **Pro tip:** Keep one scenario that is intentionally messy.

## Independent exercise (5 to 10 min)

### Task
Add one new scenario based on recent feedback.

### Output
Updated test report.

## Self-check (yes/no)

- [ ] Are scenarios realistic?
- [ ] Are outcomes clear?
- [ ] Are results recorded?
- [ ] Is there at least one messy input?

### Baseline metric (recommended)
- **Score:** 4 of 5 scenarios pass
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Software Testing Basics**. ISTQB. 2024-01-01.
   Read: https://www.istqb.org/

2. **Agent Evaluation Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/evals

## Read more (optional)

1. **Test Case Design**
   Why: Simple structures for manual testing.
   Read: https://www.guru99.com/test-case.html
