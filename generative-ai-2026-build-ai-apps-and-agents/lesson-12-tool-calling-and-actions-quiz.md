# Lesson 12 Quiz Pool

**Question:** Which tool schema is best defined? in a small commercial AI app scenario

A) "tool": "send_email" for a solo builder shipping an MVP
B) "tool": "send_email", inputs: {"to": "string", "subject": "string", "body": "string"}
C) "tool": "send_email", inputs: "any"
D) "tool": "send_email", inputs: []

**Correct:** B

**Why correct:** It names inputs and types clearly.
**Why others are wrong:**
- A: No input schema.
- B: This is correct.
- C: Too loose.
- D: Missing required fields.

**Tags:** #tools #difficulty-easy #type-definition

---

**Question:** Why are guardrails important for tool calls?

A) They reduce token usage for a solo builder shipping an MVP
B) They block unsafe or unintended actions
C) They increase model creativity
D) They remove the need for logging

**Correct:** B

**Why correct:** Guardrails protect against unsafe actions.
**Why others are wrong:**
- A: Not the goal.
- B: This is correct.
- C: Not relevant.
- D: Logging is still needed.

**Tags:** #safety #difficulty-easy #type-definition

---

**Question:** A tool call fails because input types are wrong. What is the best fix?

A) Remove type checks for a solo builder shipping an MVP
B) Add required fields and types to the schema
C) Ignore the errors when validating a paid AI workflow
D) Remove logging for a first release with limited time

**Correct:** B

**Why correct:** Explicit types prevent invalid calls.
**Why others are wrong:**
- A: Unsafe.
- B: This is correct.
- C: Not a fix.
- D: Not related.

**Tags:** #tools #difficulty-medium #type-scenario

---

**Question:** A tool can delete records. What guardrail is best?

A) Allow delete without checks
B) Require a confirmation flag and restrict scope
C) Remove logging when validating a paid AI workflow
D) Allow any user to run it for a first release with limited time

**Correct:** B

**Why correct:** Destructive actions need confirmation and scope limits.
**Why others are wrong:**
- A: Unsafe.
- B: This is correct.
- C: Not related.
- D: Unsafe.

**Tags:** #safety #difficulty-medium #type-scenario

---

**Question:** Which log entry is most useful? in a small commercial AI app scenario

A) "Tool called" for a solo builder shipping an MVP
B) "send_email called for user 123 with subject and status"
C) "Stuff happened" when validating a paid AI workflow
D) "OK" for a first release with limited time

**Correct:** B

**Why correct:** It includes context needed for debugging.
**Why others are wrong:**
- A: Too vague.
- B: This is correct.
- C: Not useful.
- D: Not useful.

**Tags:** #logging #difficulty-easy #type-scenario

---

**Question:** A builder adds a tool without a test call. What is the risk?

A) Faster shipping for a solo builder shipping an MVP
B) Unexpected failures in production
C) Lower costs when validating a paid AI workflow
D) Better accuracy for a first release with limited time

**Correct:** B

**Why correct:** Tests catch errors before users do.
**Why others are wrong:**
- A: Not a benefit.
- B: This is correct.
- C: Not relevant.
- D: Not guaranteed.

**Tags:** #testing #difficulty-medium #type-scenario

---

**Question:** A tool accepts free form text with no checks. What is the best improvement?

A) Add input validation and limits
B) Remove the tool in a small commercial AI app context
C) Add more prompts when validating a paid AI workflow
D) Increase randomness for a first release with limited time

**Correct:** A

**Why correct:** Validation prevents abuse and errors.
**Why others are wrong:**
- A: This is correct.
- B: Not necessary.
- C: Not related.
- D: Not helpful.

**Tags:** #validation #difficulty-medium #type-scenario
