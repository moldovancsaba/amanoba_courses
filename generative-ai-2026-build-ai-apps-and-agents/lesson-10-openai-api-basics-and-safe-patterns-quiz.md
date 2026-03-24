# Lesson 10 Quiz Pool

**Question:** A developer stores the API key in client side code. What is the best fix?

A) Leave it, it speeds up requests
B) Move the key to server env variables and call from the server
C) Obfuscate the key in the UI
D) Put the key in local storage

**Correct:** B

**Why correct:** Keys should be kept on the server and read from env variables.
**Why others are wrong:**
- A: Exposes secrets.
- B: This is correct.
- C: Still exposed.
- D: Still exposed.

**Tags:** #security #difficulty-easy #type-scenario

---

**Question:** An API call fails due to a timeout. What response best protects user trust?

A) No response at all for a solo builder shipping an MVP
B) A clear fallback message and retry option
C) A stack trace shown to users
D) A message that blames the user

**Correct:** B

**Why correct:** Users need a clear, safe message and a path to continue.
**Why others are wrong:**
- A: Confusing.
- B: This is correct.
- C: Too technical for users.
- D: Poor experience.

**Tags:** #error-handling #difficulty-medium #type-scenario

---

**Question:** Which request pattern is safest for an AI feature?

A) Send user input directly with no validation
B) Validate input, set a timeout, and log errors
C) Disable error logs to reduce noise
D) Store the API key in the browser

**Correct:** B

**Why correct:** Validation, timeouts, and logging reduce risk.
**Why others are wrong:**
- A: Risky and unstable.
- B: This is correct.
- C: Hides issues.
- D: Exposes secrets.

**Tags:** #safety #difficulty-medium #type-scenario

---

**Question:** A developer wants to test the API call. What is the best test?

A) No test needed for a solo builder shipping an MVP
B) A sample prompt and a recorded response log
C) Only a UI screenshot when validating a paid AI workflow
D) A social media post for a first release with limited time

**Correct:** B

**Why correct:** A prompt and response log verifies behavior.
**Why others are wrong:**
- A: Not safe.
- B: This is correct.
- C: Not enough.
- D: Not a test.

**Tags:** #testing #difficulty-easy #type-scenario

---

**Question:** Which fallback message is best for a user?

A) "Error 500" for a solo builder shipping an MVP
B) "The AI could not complete the request. Please try again."
C) "Stack trace here" when validating a paid AI workflow
D) "Something broke, deal with it"

**Correct:** B

**Why correct:** It is clear and polite without technical noise.
**Why others are wrong:**
- A: Not helpful.
- B: This is correct.
- C: Too technical.
- D: Poor experience.

**Tags:** #fallback #difficulty-easy #type-scenario

---

**Question:** An app logs errors but no request id. What is the risk?

A) Faster responses for a solo builder shipping an MVP
B) Harder debugging and tracing
C) More revenue when validating a paid AI workflow
D) Better security for a first release with limited time

**Correct:** B

**Why correct:** Request ids help trace issues.
**Why others are wrong:**
- A: Not true.
- B: This is correct.
- C: Not related.
- D: Not related.

**Tags:** #logging #difficulty-medium #type-scenario

---

**Question:** A builder wants to reduce failures from user input. What is the best action?

A) Allow any input without checks
B) Add basic input validation before calling the API
C) Remove logging when validating a paid AI workflow
D) Remove fallback messages for a first release with limited time

**Correct:** B

**Why correct:** Validation reduces errors and abuse.
**Why others are wrong:**
- A: Risky.
- B: This is correct.
- C: Not related.
- D: Reduces safety.

**Tags:** #validation #difficulty-medium #type-scenario
