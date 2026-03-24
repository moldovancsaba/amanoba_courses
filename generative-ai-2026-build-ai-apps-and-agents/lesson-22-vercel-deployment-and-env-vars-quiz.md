# Lesson 22 Quiz Pool

**Question:** Where should env vars be set for a Vercel deployment?

A) In the client side code for a solo builder shipping an MVP
B) In the Vercel project settings
C) In a public gist when validating a paid AI workflow
D) In a README for a first release with limited time

**Correct:** B

**Why correct:** Vercel env vars are set in project settings.
**Why others are wrong:**
- A: Exposes secrets.
- B: This is correct.
- C: Not safe.
- D: Not safe.

**Tags:** #vercel #difficulty-easy #type-definition

---

**Question:** Why use a staging deployment? in a small commercial AI app scenario

A) To replace production for a solo builder shipping an MVP
B) To test a live version safely
C) To increase costs when validating a paid AI workflow
D) To avoid testing for a first release with limited time

**Correct:** B

**Why correct:** Staging helps test without risking production.
**Why others are wrong:**
- A: Not correct.
- B: This is correct.
- C: Not a benefit.
- D: Not a benefit.

**Tags:** #deployment #difficulty-easy #type-definition

---

**Question:** A deployment fails due to missing env vars. What is the fix?

A) Ignore it for a solo builder shipping an MVP
B) Add the missing env vars in Vercel settings
C) Remove the vars from code
D) Redeploy without changes for a first release with limited time

**Correct:** B

**Why correct:** Missing env vars must be added to the platform.
**Why others are wrong:**
- A: Not acceptable.
- B: This is correct.
- C: Not a fix.
- D: Not sufficient.

**Tags:** #vercel #difficulty-medium #type-scenario

---

**Question:** Why label staging clearly? in a small commercial AI app scenario

A) It looks nicer for a solo builder shipping an MVP
B) To avoid confusing it with production
C) To increase speed when validating a paid AI workflow
D) To reduce costs for a first release with limited time

**Correct:** B

**Why correct:** Clear labels prevent mistakes.
**Why others are wrong:**
- A: Not the main reason.
- B: This is correct.
- C: Not related.
- D: Not related.

**Tags:** #deployment #difficulty-easy #type-scenario

---

**Question:** Which action best validates a staging deploy?

A) Only open the homepage for a solo builder shipping an MVP
B) Run a real test input end to end
C) Change the logo when validating a paid AI workflow
D) Share the URL without testing

**Correct:** B

**Why correct:** End to end tests catch real issues.
**Why others are wrong:**
- A: Not enough.
- B: This is correct.
- C: Not a validation.
- D: Risky.

**Tags:** #deployment #difficulty-medium #type-scenario

---

**Question:** A developer puts secrets in the repo for convenience. What is the risk?

A) Faster deployment for a solo builder shipping an MVP
B) Secret leaks and compromised access
C) Better documentation when validating a paid AI workflow
D) Improved UX for a first release with limited time

**Correct:** B

**Why correct:** Secrets in code can leak publicly.
**Why others are wrong:**
- A: Not worth the risk.
- B: This is correct.
- C: Not related.
- D: Not related.

**Tags:** #security #difficulty-medium #type-scenario

---

**Question:** Which practice improves staging reliability?

A) Use different env vars than production
B) Use the same env vars as production without review
C) Avoid env vars when validating a paid AI workflow
D) Hard code secrets for a first release with limited time

**Correct:** A

**Why correct:** Separate env vars reduce risk and allow safe tests.
**Why others are wrong:**
- A: This is correct.
- B: Risky.
- C: Not possible.
- D: Not safe.

**Tags:** #deployment #difficulty-medium #type-scenario
