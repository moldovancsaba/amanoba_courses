# Lesson 11: Prompt design for reliability

**One-liner:** Design prompts that produce stable, testable outputs.  
**Time:** 20 to 30 min  
**Deliverable:** Prompt Spec and Test Set

## Learning goal

You will be able to: **Write a prompt spec and a small test set that improves reliability.**

### Success criteria (observable)
- [ ] The prompt includes role, task, and output format.
- [ ] The test set has at least 5 representative inputs.
- [ ] At least 4 of 5 tests meet the expected output.

### Output you will produce
- **Deliverable:** Prompt Spec and Test Set
- **Format:** Prompt doc plus test table
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad designing prompts for a commercial AI app
**Secondary persona(s):** Users who expect consistent output
**Stakeholders (optional):** Collaborators

## What

### What it is
A clear prompt spec that tells the model what to do and how to format the output.
A small test set that reveals weak spots before users do.

### What it is not
It is not a long, complex prompt that tries to solve every edge case.
It is not a replacement for product logic or validation.

### 2-minute theory
- Prompts are product interfaces that must be reliable.
- Clear structure reduces output drift and surprises.
- Small test sets catch errors early with low effort.

### Key terms
- **Prompt spec:** A structured instruction with role, task, and format.
- **Test set:** A handful of inputs used to validate output quality.

## Where

### Applies in
- System prompts
- Feature specific prompts

### Does not apply in
- UI copy or marketing content

### Touchpoints
- Prompt files
- Test cases
- Output logs

## When

### Use it when
- You add a new AI feature
- Output quality is inconsistent

### Frequency
Whenever prompts change

### Late signals
- Users report inconsistent results
- Outputs break formatting

## Why it matters

### Practical benefits
- More consistent outputs
- Faster debugging
- Better user trust

### Risks of ignoring
- Unpredictable output
- Higher support burden

### Expectations
- Improves: reliability and clarity
- Does not guarantee: perfect accuracy

## How

### Step-by-step method
1. Write a role and task in one sentence.
2. Define the output format with an example.
3. Add constraints like tone or length.
4. Create a 5 input test set.
5. Run the tests and record pass rate.

### Do and don't

**Do**
- Use explicit output formats
- Keep prompts short and focused

**Don't**
- Mix multiple tasks in one prompt
- Skip testing on real inputs

### Common mistakes and fixes
- **Mistake:** Vague format. **Fix:** Provide a structured template.
- **Mistake:** No tests. **Fix:** Add a small test set.

### Done when
- [ ] Prompt includes role, task, and format.
- [ ] Test set has 5 inputs.
- [ ] Pass rate is recorded.

## Guided exercise (10 to 15 min)

### Inputs
- Your feature description
- 5 representative user inputs

### Steps
1. Write a prompt spec with role, task, and format.
2. Define expected output for each input.
3. Record pass or fail.

### Output format
| Field | Value |
|---|---|
| Prompt spec | |
| Input set | |
| Expected output | |
| Pass rate | |

> **Pro tip:** Use real user inputs, not ideal examples.

## Independent exercise (5 to 10 min)

### Task
Shorten your prompt by 20 percent without losing clarity.

### Output
Revised prompt spec and updated test results.

## Self-check (yes/no)

- [ ] Does the prompt define role, task, and format?
- [ ] Are inputs realistic and varied?
- [ ] Is the pass rate recorded?
- [ ] Is the prompt easy to read?

### Baseline metric (recommended)
- **Score:** 4 of 5 tests pass
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Prompt Engineering Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/prompt-engineering

2. **Prompting Best Practices**. Anthropic. 2026-02-06.
   Read: https://docs.anthropic.com/claude/docs/prompting

## Read more (optional)

1. **System Prompt Best Practices**
   Why: Guidelines for stable outputs.
   Read: https://platform.openai.com/docs/guides/prompt-engineering
