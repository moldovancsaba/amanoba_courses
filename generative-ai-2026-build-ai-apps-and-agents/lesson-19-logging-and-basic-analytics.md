# Lesson 19: Logging and basic analytics

**One-liner:** Track usage and outcomes without overcomplicating analytics.  
**Time:** 20 to 30 min  
**Deliverable:** Logging Plan and Basic Event Capture

## Learning goal

You will be able to: **Define basic logging and analytics that support debugging and product decisions.**

### Success criteria (observable)
- [ ] Core events are listed.
- [ ] Each event has a purpose.
- [ ] A simple dashboard or log view exists.

### Output you will produce
- **Deliverable:** Logging Plan and Basic Event Capture
- **Format:** Event list plus sample logs
- **Where saved:** Repo and course folder notes

## Who

**Primary persona:** Digital nomad setting up basic analytics
**Secondary persona(s):** Users affected by reliability
**Stakeholders (optional):** Collaborators

## What

### What it is
A short list of events and logs that show how users use the product.
It supports debugging and early product decisions.

### What it is not
It is not a complex analytics pipeline or data warehouse.
It is a light setup for a small app.

### 2-minute theory
- A few key events provide most of the insight you need.
- Good logs make failures diagnosable.
- Over tracking wastes time and adds risk.

### Key terms
- **Event:** A logged action like request sent or output generated.
- **Dashboard:** A place to view key metrics quickly.

## Where

### Applies in
- Backend logs
- Product analytics

### Does not apply in
- Visual design tasks

### Touchpoints
- Log viewer
- Analytics dashboard
- Alerting rules

## When

### Use it when
- You ship a feature to users
- You need evidence of usage

### Frequency
Set once, review monthly

### Late signals
- You cannot answer basic usage questions
- Debugging takes too long

## Why it matters

### Practical benefits
- Faster debugging
- Clearer product insights
- Better reliability monitoring

### Risks of ignoring
- Blind spots in usage
- Slow incident response

### Expectations
- Improves: clarity and control
- Does not guarantee: full analytics accuracy

## How

### Step-by-step method
1. List 5 to 8 core events.
2. Define why each event matters.
3. Add a simple log viewer or dashboard.
4. Review logs weekly.

### Do and don't

**Do**
- Start with a short event list
- Tie events to product questions

**Don't**
- Track everything
- Ignore privacy concerns

### Common mistakes and fixes
- **Mistake:** Too many events. **Fix:** Keep only core events.
- **Mistake:** No review cadence. **Fix:** Add weekly review.

### Done when
- [ ] Core events are listed.
- [ ] Events have clear purposes.
- [ ] Logs are reviewable.

## Guided exercise (10 to 15 min)

### Inputs
- Product promise
- Key user actions

### Steps
1. List core events.
2. Add a reason for each.
3. Choose a log view.

### Output format
| Field | Value |
|---|---|
| Event | |
| Purpose | |
| Log location | |
| Owner | |

> **Pro tip:** If you cannot explain why an event matters, remove it.

## Independent exercise (5 to 10 min)

### Task
Remove one event and confirm you still answer key questions.

### Output
Revised event list.

## Self-check (yes/no)

- [ ] Are core events defined?
- [ ] Are purposes clear?
- [ ] Is a log view available?
- [ ] Is privacy considered?

### Baseline metric (recommended)
- **Score:** 6 events defined
- **Date:** 2026-02-06
- **Tool used:** Notes app

## Bibliography (sources used)

1. **Google Analytics Academy**. Google. 2024-01-01.
   Read: https://analytics.google.com/analytics/academy/

2. **Logging Best Practices**. Grafana. 2024-01-01.
   Read: https://grafana.com/docs/grafana/latest/fundamentals/logs/

## Read more (optional)

1. **Event Tracking Guide**
   Why: Examples of useful events.
   Read: https://segment.com/docs/connections/spec/track/
