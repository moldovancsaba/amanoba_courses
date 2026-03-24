# Lesson 25 Quiz Pool

**Question:** Why validate Stripe webhook signatures? in a small commercial AI app scenario

A) To make requests slower for a solo builder shipping an MVP
B) To ensure events are real and not spoofed
C) To avoid using Stripe when validating a paid AI workflow
D) To reduce billing for a first release with limited time

**Correct:** B

**Why correct:** Signature checks ensure authenticity.
**Why others are wrong:**
- A: Not a goal.
- B: This is correct.
- C: Not true.
- D: Not related.

**Tags:** #stripe #difficulty-easy #type-definition

---

**Question:** Where should access be granted after payment?

A) On the client for a solo builder shipping an MVP
B) On the server after webhook confirmation
C) In a public file when validating a paid AI workflow
D) In a README for a first release with limited time

**Correct:** B

**Why correct:** Server side verification is required.
**Why others are wrong:**
- A: Not secure.
- B: This is correct.
- C: Not appropriate.
- D: Not related.

**Tags:** #stripe #difficulty-easy #type-definition

---

**Question:** A user says they paid but have no access. What should you check first?

A) The UI colors for a solo builder shipping an MVP
B) Webhook logs and event handling
C) Marketing copy when validating a paid AI workflow
D) Social media posts for a first release with limited time

**Correct:** B

**Why correct:** Webhook logs show payment events and access updates.
**Why others are wrong:**
- A: Not relevant.
- B: This is correct.
- C: Not relevant.
- D: Not relevant.

**Tags:** #stripe #difficulty-medium #type-scenario

---

**Question:** Which event should grant access? in a small commercial AI app scenario

A) payment_failed for a solo builder shipping an MVP
B) checkout.session.completed
C) random_event when validating a paid AI workflow
D) price.created for a first release with limited time

**Correct:** B

**Why correct:** Completed checkout indicates payment success.
**Why others are wrong:**
- A: Not success.
- B: This is correct.
- C: Not relevant.
- D: Not a payment event.

**Tags:** #stripe #difficulty-medium #type-scenario

---

**Question:** Why not trust client side payment status?

A) It is faster for a solo builder shipping an MVP
B) It can be spoofed or outdated
C) It reduces cost when validating a paid AI workflow
D) It improves UX for a first release with limited time

**Correct:** B

**Why correct:** Client signals are not secure.
**Why others are wrong:**
- A: Not a benefit.
- B: This is correct.
- C: Not related.
- D: Not related.

**Tags:** #stripe #difficulty-medium #type-scenario

---

**Question:** A webhook handler does not log events. What is the risk?

A) Faster requests for a solo builder shipping an MVP
B) Harder to debug payment issues
C) Better security when validating a paid AI workflow
D) Lower costs for a first release with limited time

**Correct:** B

**Why correct:** Logs are needed to diagnose issues.
**Why others are wrong:**
- A: Not a reason.
- B: This is correct.
- C: Not true.
- D: Not related.

**Tags:** #stripe #difficulty-medium #type-scenario

---

**Question:** Which tool helps test Stripe webhooks locally?

A) Stripe CLI for a solo builder shipping an MVP
B) Git in a small commercial AI app context
C) npm when validating a paid AI workflow
D) Docker for a first release with limited time

**Correct:** A

**Why correct:** Stripe CLI can send test webhook events.
**Why others are wrong:**
- A: This is correct.
- B: Not for webhooks.
- C: Not relevant.
- D: Not necessary.

**Tags:** #stripe #difficulty-easy #type-definition
