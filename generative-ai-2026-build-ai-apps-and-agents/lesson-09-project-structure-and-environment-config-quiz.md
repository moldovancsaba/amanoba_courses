# Lesson 9 Quiz Pool

**Question:** Which file should list required env variables without secrets?

A) .env for a solo builder shipping an MVP
B) .env.example in a small commercial AI app context
C) package.json when validating a paid AI workflow
D) README only for a first release with limited time

**Correct:** B

**Why correct:** The template lists required keys without real values.
**Why others are wrong:**
- A: .env contains real secrets.
- B: This is correct.
- C: Not for env vars.
- D: Not enough by itself.

**Tags:** #env #difficulty-easy #type-definition

---

**Question:** A developer commits real API keys. What is the best fix?

A) Ignore it for a solo builder shipping an MVP
B) Rotate keys and remove secrets from history
C) Add more keys when validating a paid AI workflow
D) Change the README for a first release with limited time

**Correct:** B

**Why correct:** Keys must be rotated and removed.
**Why others are wrong:**
- A: Security risk.
- B: This is correct.
- C: Adds risk.
- D: Not enough.

**Tags:** #security #difficulty-medium #type-scenario

---

**Question:** Which folder layout best supports a simple AI app?

A) All files in one folder for a solo builder shipping an MVP
B) Separate folders for app, api, and docs
C) Only a docs folder when validating a paid AI workflow
D) A folder per UI color for a first release with limited time

**Correct:** B

**Why correct:** Separation improves clarity and maintainability.
**Why others are wrong:**
- A: Hard to maintain.
- B: This is correct.
- C: Missing app code.
- D: Not useful.

**Tags:** #structure #difficulty-easy #type-scenario

---

**Question:** A project has no .gitignore for .env files. What is the risk?

A) Faster builds for a solo builder shipping an MVP
B) Secrets may be committed in a small commercial AI app context
C) Better onboarding when validating a paid AI workflow
D) Cleaner code for a first release with limited time

**Correct:** B

**Why correct:** Secrets could be exposed.
**Why others are wrong:**
- A: Not relevant.
- B: This is correct.
- C: Not true.
- D: Not related.

**Tags:** #env #difficulty-easy #type-error

---

**Question:** Why should env variables be documented? in a small commercial AI app scenario

A) To increase code size for a solo builder shipping an MVP
B) To help onboarding and deployment
C) To replace tests when validating a paid AI workflow
D) To avoid using the API for a first release with limited time

**Correct:** B

**Why correct:** Documented env vars reduce setup issues.
**Why others are wrong:**
- A: Not a goal.
- B: This is correct.
- C: Not true.
- D: Not relevant.

**Tags:** #env #difficulty-medium #type-scenario

---

**Question:** A team adds a new service but does not update .env.example. What happens?

A) Nothing for a solo builder shipping an MVP
B) New developers will miss required variables
C) Tests run faster when validating a paid AI workflow
D) Users see a new feature for a first release with limited time

**Correct:** B

**Why correct:** Missing templates cause setup failures.
**Why others are wrong:**
- A: Not true.
- B: This is correct.
- C: Not true.
- D: Not related.

**Tags:** #env #difficulty-medium #type-scenario

---

**Question:** Which practice best prevents accidental secret leaks?

A) Store keys in README for a solo builder shipping an MVP
B) Use .env locally and add it to .gitignore
C) Commit keys for convenience
D) Put keys in code comments

**Correct:** B

**Why correct:** .gitignore and local env files prevent leaks.
**Why others are wrong:**
- A: Not safe.
- B: This is correct.
- C: Not safe.
- D: Not safe.

**Tags:** #security #difficulty-easy #type-scenario
