# Lesson 12: Tool calling and actions

**One-liner:** Connect the model to tools and enforce safe actions.  
**Time:** 20 to 30 min  
**Deliverable:** Tool Schema and Action Example

## Learning goal

You will be able to: **Define a tool schema and run a safe tool call.**

### Success criteria (observable)
- [ ] Tool schema includes name, inputs, and output shape.
- [ ] The tool call runs with a real example.
- [ ] Unsafe actions are blocked.

### Output you will produce
- **Deliverable:** Tool Schema and Action Example
- **Format:** JSON schema plus test log
- **Where saved:** Repo and course folder notes

## Who

**Primary persona:** Digital nomad building tool enabled AI features
**Secondary persona(s):** Users who trigger actions
**Stakeholders (optional):** Collaborators

## What

### What it is
A tool definition that tells the model what it can call and how.
A small example that proves the tool call works as intended.

### What it is not
It is not a full automation platform or a permission system.
It is a controlled first step to reliable actions.

### 2-minute theory
- Tool calling makes AI useful beyond text output.
- Clear schemas reduce errors and unexpected inputs.
- Guardrails prevent unsafe or unintended actions.

### Key terms
- **Tool schema:** A structured definition of inputs and outputs.
- **Guardrail:** A rule that blocks unsafe actions.

## Where

### Applies in
- Agent workflows
- Backend services

### Does not apply in
- Static content generation only

### Touchpoints
- Tool definitions
- Action logs
- Permission checks

## When

### Use it when
- You want the AI to trigger actions
- You need predictable inputs

### Frequency
Whenever you add a new tool

### Late signals
- Tool calls fail with bad inputs
- Unexpected actions occur

## Why it matters

### Practical benefits
- More useful AI features
- Fewer failures in automation
- Better safety and trust

### Risks of ignoring
- Broken workflows
- Unsafe actions

### Expectations
- Improves: reliability and safety
- Does not guarantee: perfect decisions

## How

### Step-by-step method
1. Define the tool name and purpose.
2. Specify input fields and types.
3. Define the output shape.
4. Add guardrails for unsafe actions.
5. Run a test call and log results.

### Do and don't

**Do**
- Validate inputs before execution
- Log every action

**Don't**
- Allow tools to run without checks
- Expose dangerous actions by default

### Common mistakes and fixes
- **Mistake:** Loose schema. **Fix:** Add required fields and types.
- **Mistake:** No guardrails. **Fix:** Block unsafe parameters.

### Done when
- [ ] Tool schema is defined and tested.
- [ ] Guardrails block unsafe inputs.
- [ ] Logs show a successful call.

## Guided exercise (10 to 15 min)

### Inputs
- One tool idea
- Example input values

### Steps
1. Write the tool schema.
2. Add guardrails for unsafe inputs.
3. Run a test call and log the output.

### Output format
| Field | Value |
|---|---|
| Tool name | |
| Input schema | |
| Guardrails | |
| Test result | |

> **Pro tip:** If a tool can change data, add a confirmation step.

## Independent exercise (5 to 10 min)

### Task
Add one additional guardrail and rerun the test.

### Output
Updated schema and test log.

## Self-check (yes/no)

- [ ] Is the schema explicit and typed?
- [ ] Are unsafe actions blocked?
- [ ] Is a test call recorded?
- [ ] Are logs stored?

### Baseline metric (recommended)
- **Score:** 1 tool call succeeds with guardrails
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **OpenAI Tools Guide**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs/guides/tools

2. **OWASP API Security Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-api-security/

## Read more (optional)

1. **Function Calling Best Practices**
   Why: Safe patterns for tool calling.
   Read: https://platform.openai.com/docs/guides/tools
