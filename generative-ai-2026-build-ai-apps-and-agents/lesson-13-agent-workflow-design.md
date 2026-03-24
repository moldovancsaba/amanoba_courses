# Lesson 13: Agent workflow design

**One-liner:** Define a clear multi step agent workflow.  
**Time:** 20 to 30 min  
**Deliverable:** Agent Workflow Diagram and Steps

## Learning goal

You will be able to: **Design a multi step agent workflow that is easy to test.**

### Success criteria (observable)
- [ ] The workflow has 3 to 6 steps.
- [ ] Each step has a clear input and output.
- [ ] A failure path is defined.

### Output you will produce
- **Deliverable:** Agent Workflow Diagram and Steps
- **Format:** Diagram plus step list
- **Where saved:** Course folder under `/generative-ai-2026-build-ai-apps-and-agents/`

## Who

**Primary persona:** Digital nomad building an agent workflow
**Secondary persona(s):** Users who depend on predictable results
**Stakeholders (optional):** Collaborators

## What

### What it is
A clear sequence of steps an agent follows to produce an outcome.
Each step has a defined input, action, and output.

### What it is not
It is not a black box that tries to do everything in one step.
It is not a replacement for product logic.

### 2-minute theory
- Small steps are easier to test than one large step.
- Defined inputs and outputs reduce errors.
- Failure paths prevent user confusion.

### Key terms
- **Workflow:** A sequence of steps that leads to an outcome.
- **Failure path:** A planned response when a step fails.

## Where

### Applies in
- Agent pipelines
- Task automation

### Does not apply in
- Simple single step prompts

### Touchpoints
- Workflow diagrams
- Logs and traces
- Output validation

## When

### Use it when
- A task has multiple stages
- You need predictable outputs

### Frequency
Whenever you add a new agent feature

### Late signals
- Hard to debug failures
- Users see partial results

## Why it matters

### Practical benefits
- Easier testing
- More stable output
- Better user trust

### Risks of ignoring
- Random behavior
- Hard to troubleshoot issues

### Expectations
- Improves: reliability and testability
- Does not guarantee: perfect results

## How

### Step-by-step method
1. Define the final outcome.
2. Split the task into 3 to 6 steps.
3. Define inputs and outputs for each step.
4. Add a failure response for each step.

### Do and don't

**Do**
- Keep steps small and testable
- Log outputs at each step

**Don't**
- Combine unrelated tasks in one step
- Skip failure handling

### Common mistakes and fixes
- **Mistake:** Too many steps. **Fix:** Merge or remove non essential steps.
- **Mistake:** No failure path. **Fix:** Add a fallback response.

### Done when
- [ ] Steps are defined and sequenced.
- [ ] Inputs and outputs are clear.
- [ ] Failure paths are written.

## Guided exercise (10 to 15 min)

### Inputs
- Your product promise
- A target user task

### Steps
1. Write the final outcome.
2. List 3 to 6 steps.
3. Add inputs and outputs.

### Output format
| Field | Value |
|---|---|
| Final outcome | |
| Steps | |
| Inputs and outputs | |
| Failure paths | |

> **Pro tip:** If a step is hard to test, split it into two.

## Independent exercise (5 to 10 min)

### Task
Remove one step and see if the outcome still holds.

### Output
Updated workflow steps and notes.

## Self-check (yes/no)

- [ ] Are steps short and testable?
- [ ] Does each step have input and output?
- [ ] Are failure paths defined?
- [ ] Does the workflow match the promise?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Designing Agentic Workflows**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/agents

2. **Workflow Patterns**. Martin Fowler. 2024-01-01.
   Read: https://martinfowler.com/articles/workflow-patterns.html

## Read more (optional)

1. **Agent Design Patterns**
   Why: Practical workflow structure ideas.
   Read: https://platform.openai.com/docs/guides/agents
