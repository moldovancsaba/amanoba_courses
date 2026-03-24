# Lesson 13 Quiz Pool

**Question:** Why are multi step workflows preferred for agents?

A) They look more complex for a solo builder shipping an MVP
B) They are easier to test and debug
C) They use more tokens when validating a paid AI workflow
D) They make output random for a first release with limited time

**Correct:** B

**Why correct:** Smaller steps make testing and debugging easier.
**Why others are wrong:**
- A: Complexity is not the goal.
- B: This is correct.
- C: Not a benefit.
- D: Not true.

**Tags:** #workflow #difficulty-easy #type-definition

---

**Question:** A workflow step has no defined output. What is the risk?

A) Faster development for a solo builder shipping an MVP
B) Unclear state and hard to validate results
C) Lower cost when validating a paid AI workflow
D) Better UX for a first release with limited time

**Correct:** B

**Why correct:** Without outputs, you cannot validate progress.
**Why others are wrong:**
- A: Not true.
- B: This is correct.
- C: Not related.
- D: Not related.

**Tags:** #workflow #difficulty-medium #type-scenario

---

**Question:** A builder combines data cleanup and final response in one step. What is the best fix?

A) Keep it combined for a solo builder shipping an MVP
B) Split into two steps with separate outputs
C) Add more text to the prompt
D) Remove logging for a first release with limited time

**Correct:** B

**Why correct:** Splitting improves testing and control.
**Why others are wrong:**
- A: Hard to debug.
- B: This is correct.
- C: Not a fix.
- D: Not related.

**Tags:** #workflow #difficulty-medium #type-scenario

---

**Question:** Which failure path is best? in a small commercial AI app scenario

A) "If step fails, do nothing"
B) "If step fails, return a clear error and a next action"
C) "If step fails, retry forever"
D) "If step fails, hide the error"

**Correct:** B

**Why correct:** Users need clear outcomes and next steps.
**Why others are wrong:**
- A: Not helpful.
- B: This is correct.
- C: Risky.
- D: Not transparent.

**Tags:** #failure-path #difficulty-medium #type-scenario

---

**Question:** A workflow has 12 steps. What is the best guidance?

A) Keep all steps to be thorough
B) Reduce to the core 3 to 6 steps
C) Add more steps when validating a paid AI workflow
D) Remove failure paths for a first release with limited time

**Correct:** B

**Why correct:** Short workflows are easier to test and ship.
**Why others are wrong:**
- A: Too complex.
- B: This is correct.
- C: Worse.
- D: Not related.

**Tags:** #workflow #difficulty-easy #type-scenario

---

**Question:** A workflow does not match the product promise. What should happen?

A) Keep the workflow as is for a solo builder shipping an MVP
B) Update steps to align with the promise outcome
C) Remove the promise when validating a paid AI workflow
D) Add more features for a first release with limited time

**Correct:** B

**Why correct:** Workflows should deliver the promised outcome.
**Why others are wrong:**
- A: Misalignment leads to poor outcomes.
- B: This is correct.
- C: Not a fix.
- D: Adds scope.

**Tags:** #alignment #difficulty-medium #type-scenario

---

**Question:** Why log outputs at each step? in a small commercial AI app scenario

A) To increase tokens for a solo builder shipping an MVP
B) To make debugging possible
C) To reduce errors automatically
D) To replace tests for a first release with limited time

**Correct:** B

**Why correct:** Logs allow tracing what went wrong.
**Why others are wrong:**
- A: Not a benefit.
- B: This is correct.
- C: Not guaranteed.
- D: Not a replacement.

**Tags:** #logging #difficulty-easy #type-definition
