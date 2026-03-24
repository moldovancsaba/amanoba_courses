# Lesson 10: OpenAI API basics and safe patterns

**One-liner:** Make a reliable OpenAI API call with basic safeguards.  
**Time:** 20 to 30 min  
**Deliverable:** Working OpenAI Call with Error Handling

## Learning goal

You will be able to: **Implement a basic OpenAI API request with safe defaults and error handling.**

### Success criteria (observable)
- [ ] The request returns a response for a sample input.
- [ ] Errors are handled with a clear fallback message.
- [ ] The API key is stored in an environment variable.

### Output you will produce
- **Deliverable:** Working OpenAI Call with Error Handling
- **Format:** Code snippet plus test log
- **Where saved:** Repo and course folder notes

## Who

**Primary persona:** Digital nomad building an AI app
**Secondary persona(s):** Early users relying on stable output
**Stakeholders (optional):** Collaborators

## What

### What it is
A small, reliable server side call to the OpenAI API with safe defaults.
It returns a useful response and fails in a predictable way when something breaks.

### What it is not
It is not a full agent system or advanced orchestration.
It is the first stable building block you can trust.

### 2-minute theory
- Safe defaults reduce surprise behavior and cost spikes.
- Clear error handling protects user trust on bad days.
- Environment variables keep secrets out of the codebase.

### Key terms
- **API key:** The secret used to authenticate requests.
- **Fallback:** A safe response when the API fails.

## Where

### Applies in
- Server routes
- Backend services

### Does not apply in
- Client side secret storage

### Touchpoints
- API route
- Error logs
- Env configuration

## When

### Use it when
- You are adding AI features
- You need a stable first response

### Frequency
Once per product, revisit as features grow

### Late signals
- Frequent errors without clear messages
- Secrets committed to the repo

## Why it matters

### Practical benefits
- Faster debugging when something fails
- Safer deployments without leaked keys
- Better user experience when the API is slow

### Risks of ignoring
- Leaked keys and unexpected costs
- Unclear failures that erode trust

### Expectations
- Improves: stability and trust
- Does not guarantee: perfect outputs

## How

### Step-by-step method
1. Store the API key in an env variable.
2. Send a request with a short prompt.
3. Add a timeout and catch errors.
4. Return a fallback response on failure.
5. Log a request id for tracing.

### Do and don't

**Do**
- Keep prompts short and testable
- Log errors with request context

**Don't**
- Put API keys in the client
- Hide errors from logs

### Common mistakes and fixes
- **Mistake:** Key in code. **Fix:** Move to env and rotate the key.
- **Mistake:** No fallback. **Fix:** Add a safe default message.

### Done when
- [ ] Request succeeds with a sample input.
- [ ] Errors return a clear message.
- [ ] API key is stored in env.

## Guided exercise (10 to 15 min)

### Inputs
- OpenAI API key in env
- A sample input prompt

### Steps
1. Write a simple request function.
2. Add error handling and a fallback message.
3. Run a test input and record the result.

### Output format
| Field | Value |
|---|---|
| Input prompt | |
| Response sample | |
| Error handling | |
| Fallback message | |

> **Pro tip:** Log a request id so you can trace failures quickly.

## Independent exercise (5 to 10 min)

### Task
Change the prompt to a new input and verify output still works.

### Output
Test log with the new prompt and response.

## Self-check (yes/no)

- [ ] Is the API key stored in env variables?
- [ ] Do errors return a user safe message?
- [ ] Is a fallback response defined?
- [ ] Is a test run recorded?

### Baseline metric (recommended)
- **Score:** 3 of 4 checks met
- **Date:** 2026-02-06
- **Tool used:** Terminal

## Bibliography (sources used)

1. **OpenAI API Docs**. OpenAI. 2026-02-06.
   Read: https://platform.openai.com/docs

2. **OWASP API Security Top 10**. OWASP. 2024-01-01.
   Read: https://owasp.org/www-project-api-security/

## Read more (optional)

1. **OpenAI Safety Best Practices**
   Why: Defensive patterns for reliable AI features.
   Read: https://platform.openai.com/docs/guides/safety-best-practices
