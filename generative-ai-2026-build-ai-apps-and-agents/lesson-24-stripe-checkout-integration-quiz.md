# Lesson 24 Quiz Pool

**Question:** Why use Stripe hosted checkout for a first release?

A) It is slower for a solo builder shipping an MVP
B) It reduces compliance work and speeds integration
C) It removes the need for pricing
D) It hides taxes automatically

**Correct:** B

**Why correct:** Hosted checkout is faster and safer for early products.
**Why others are wrong:**
- A: Not true.
- B: This is correct.
- C: Not true.
- D: Not guaranteed.

**Tags:** #stripe #difficulty-easy #type-definition

---

**Question:** Where should Stripe secret keys be stored?

A) In the client app for a solo builder shipping an MVP
B) In server env variables in a small commercial AI app context
C) In a public gist when validating a paid AI workflow
D) In the UI config file for a first release with limited time

**Correct:** B

**Why correct:** Secret keys must be kept on the server.
**Why others are wrong:**
- A: Exposes secrets.
- B: This is correct.
- C: Not safe.
- D: Not safe.

**Tags:** #stripe #difficulty-easy #type-definition

---

**Question:** A test payment fails. What should you do first?

A) Ignore it for a solo builder shipping an MVP
B) Check the webhook logs and Stripe dashboard
C) Launch anyway when validating a paid AI workflow
D) Remove payments for a first release with limited time

**Correct:** B

**Why correct:** The dashboard shows the error and fix.
**Why others are wrong:**
- A: Not acceptable.
- B: This is correct.
- C: Not acceptable.
- D: Not a fix.

**Tags:** #stripe #difficulty-medium #type-scenario

---

**Question:** Why run a test payment? in a small commercial AI app scenario

A) To waste time for a solo builder shipping an MVP
B) To validate the checkout flow before users pay
C) To reduce revenue when validating a paid AI workflow
D) To avoid logging for a first release with limited time

**Correct:** B

**Why correct:** Testing prevents launch day payment issues.
**Why others are wrong:**
- A: Not true.
- B: This is correct.
- C: Not a goal.
- D: Not related.

**Tags:** #stripe #difficulty-easy #type-definition

---

**Question:** A builder puts price ids in code. What is the best fix?

A) Keep it for a solo builder shipping an MVP
B) Move price ids to env vars
C) Remove prices when validating a paid AI workflow
D) Hard code a different value

**Correct:** B

**Why correct:** Env vars make updates safer.
**Why others are wrong:**
- A: Not ideal.
- B: This is correct.
- C: Not a fix.
- D: Not a fix.

**Tags:** #stripe #difficulty-medium #type-scenario

---

**Question:** What should the pricing page button do? in a small commercial AI app scenario

A) Open an unrelated page for a solo builder shipping an MVP
B) Trigger the checkout session and redirect
C) Show a random error when validating a paid AI workflow
D) Hide the price for a first release with limited time

**Correct:** B

**Why correct:** It should start the checkout flow.
**Why others are wrong:**
- A: Not related.
- B: This is correct.
- C: Not acceptable.
- D: Not helpful.

**Tags:** #stripe #difficulty-easy #type-scenario

---

**Question:** Which plan is best for the first payment test?

A) Many complex plans for a solo builder shipping an MVP
B) One simple plan in a small commercial AI app context
C) No plan when validating a paid AI workflow
D) A plan with hidden fees for a first release with limited time

**Correct:** B

**Why correct:** Simplicity reduces errors.
**Why others are wrong:**
- A: Too complex.
- B: This is correct.
- C: Not possible.
- D: Not acceptable.

**Tags:** #stripe #difficulty-medium #type-scenario
