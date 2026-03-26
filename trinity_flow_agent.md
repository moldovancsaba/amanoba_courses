# {trinity} - A Three-Role Pipeline for Structured Intelligence

**Authors.** Moldovan, Csaba Zoltan and Agent Chappie  
**Date.** 2026-03-25  
**Document type.** Scientific note and implementation-oriented research paper

**Abstract.** {trinity} is a three-role local inference architecture for converting raw text into ranked, structured, and auditable artifacts. It separates the work into three specialists: **Drafter** for decomposition, **Writer** for enrichment, and **Judge** for validation. Each role emits structured output, explicit scores, and provenance metadata. Final usefulness is computed with a transparent fusion rule, and retries are bounded so the system can improve content without entering infinite loops. {trinity} is designed to be reproducible, inspectable, and extensible by other builders.

---

## 1. Introduction

Many practical AI systems fail for the same reason: they ask one model to do too much at once. A single prompt may produce fluent text, but it often mixes tasks, hides uncertainty, and makes errors hard to diagnose. {trinity} is the opposite approach. It splits the workflow into three distinct roles so that each one has a narrow job and a visible output contract.

The three roles are:

- **Drafter**: break input into atomic information units.
- **Writer**: rewrite those units into clearer, more useful text.
- **Judge**: decide whether the rewritten unit is good enough to keep.

The central claim behind {trinity} is simple:

> A role-separated pipeline with structured handoffs, explicit scoring, and bounded retries can produce more controllable and auditable text artifacts than a single undifferentiated generation step, especially under memory and latency constraints.

This paper presents the theory, algorithm, contracts, implementation pattern, and evaluation ideas needed to reproduce or improve {trinity}.

---

## 2. Core Theory

{trinity} is built on four ideas:

1. **Decomposition**  
   Raw text is easier to process when broken into atomic pieces.

2. **Enrichment**  
   Atomic pieces become more useful when rewritten for clarity and audience fit.

3. **Judgment**  
   Quality should be evaluated explicitly, not assumed from fluent wording.

4. **Bounded learning**  
   Failed outputs should generate feedback for the immediately upstream role, but retries must stop after a fixed limit.

The result is a pipeline that behaves more like a controlled scientific instrument than a single creative generator.

---

## 3. Design Principles

| Principle | Meaning |
| --- | --- |
| **Specialization** | Each role does one task well. |
| **Structured handoff** | Roles exchange parseable payloads. |
| **Explicit scores** | Each stage reports confidence and impact. |
| **Transparent fusion** | Final quality is computed from declared rules. |
| **Auditability** | Every transformation has provenance. |
| **Bounded retries** | Improvement is allowed; ping-pong is not. |
| **Local-first execution** | The reference design works on local hardware when possible. |

---

## 4. System Model

{trinity} operates on an artifact that moves through the following stages:

1. **Input assembly**
2. **Drafter**
3. **Writer**
4. **Judge**
5. **Fusion / decision**
6. **Storage / routing**

The system can be implemented as a loop over one artifact at a time or as a queue of artifacts processed sequentially.

### Workflow diagram

```mermaid
flowchart LR
  IN[Input] --> D[Drafter]
  D --> W[Writer]
  W --> J[Judge]
  J --> F[Fusion and policy]
  F --> OUT[Accepted or retained artifact]
  J -.->|fixable failure| W
  W -.->|structure failure| D
```

---

## 5. Role Definitions

### 5.1 Drafter

The Drafter converts raw input into atomic units.

Responsibilities:

- identify key claims, facts, or subtopics
- remove duplication
- preserve source meaning
- produce a first-pass estimate of confidence and impact

Non-responsibilities:

- final wording
- audience-specific rewriting
- quality acceptance

### 5.2 Writer

The Writer rewrites each atomic unit into clearer, more polished text.

Responsibilities:

- improve readability
- preserve meaning
- adapt tone and structure
- keep the correct language

Non-responsibilities:

- inventing new facts
- changing the task
- deciding final acceptability

### 5.3 Judge

The Judge evaluates whether the result should be accepted.

Responsibilities:

- check grounding
- check structure
- check language
- check usefulness
- generate a short rejection reason when needed

Non-responsibilities:

- silently accepting weak content
- hiding failure causes
- restarting the whole workflow unnecessarily

---

## 6. Output Contract

Every stage should return a structured artifact.

```json
{
  "artifactId": "uuid",
  "stage": "drafter",
  "role": {
    "name": "drafter",
    "model": "small-instruct-model",
    "provider": "local-runtime"
  },
  "inputHash": "sha256",
  "outputHash": "sha256",
  "scores": {
    "confidence": 0.82,
    "impact": 0.74
  },
  "status": "accepted",
  "reason": "Atomic split is complete.",
  "content": {
    "text": "normalized stage output",
    "atoms": []
  },
  "provenance": {
    "parentArtifactId": null,
    "attempt": 1,
    "timestamp": "2026-03-25T12:00:00Z"
  }
}
```

### Required properties

- The payload must be parseable.
- Status must be explicit.
- Scores must be numeric and normalized.
- Provenance must survive every stage.
- The downstream role must not guess what happened upstream.

---

## 7. Scoring Theory

Each role emits normalized scores in the range \([0,1]\):

- Drafter: \(d_{conf}, d_{impact}\)
- Writer: \(w_{conf}, w_{impact}\)
- Judge: \(j_{conf}, j_{impact}\)

The reference fusion rule is:

- **Final confidence**: \(C = d_{conf} \times w_{conf} \times j_{conf}\)
- **Final impact**: \(I = d_{impact} \times w_{impact} \times j_{impact}\)

Why multiplication?

- It is conservative.
- It is easy to inspect.
- It penalizes weak links in the chain.
- It is simple to benchmark against alternatives.

The product rule is not sacred. It is the default because it is explainable and easy to test.

---

## 8. Retry Policy

{trinity} supports learning through feedback, but it must avoid infinite ping-pong.

### Core rule

- A rejection is annotated to the immediately upstream role.
- The annotation includes the failure class and the corrective direction.
- Each atomic artifact has a hard safety cap of **5 total attempts** across the full process.
- If the artifact is still not good enough after that, the system stops and preserves the best partial version.

### Feedback chain

1. User rejection annotates the Judge.
2. Judge rejection annotates the Writer.
3. Writer rejection annotates the Drafter.

This chain is the learning path. The attempt cap is only the safety stop.

### Stop conditions

- no improvement between attempts
- same failure class repeated twice
- structural corruption
- attempt budget exhausted

---

## 9. Canonical Algorithm

The following is the algorithmic core of {trinity}.

```python
MAX_ATTEMPTS = 5

def trinity_pipeline(input_text):
    artifact = drafter(input_text)
    attempts = 1

    while attempts <= MAX_ATTEMPTS:
        artifact = writer(artifact)
        judge_result = judge(artifact)

        if judge_result["status"] == "accepted":
            return {
                "status": "accepted",
                "artifact": artifact,
                "judge": judge_result
            }

        reason_class = judge_result.get("reason_class", "unknown")
        artifact["provenance"]["lastReasonClass"] = reason_class

        if attempts == MAX_ATTEMPTS:
            return {
                "status": "rejected",
                "artifact": artifact,
                "judge": judge_result
            }

        if reason_class in {"language", "clarity", "style"}:
            artifact = rewrite_with_feedback(artifact, judge_result)
        elif reason_class in {"structure", "missing_fields"}:
            artifact = redraft_structure(artifact, judge_result)
        else:
            return {
                "status": "partial",
                "artifact": artifact,
                "judge": judge_result
            }

        attempts += 1

    return {
        "status": "rejected",
        "artifact": artifact
    }
```

### What this algorithm guarantees

- A weak item can improve.
- An improved item can still fail final acceptance.
- No artifact loops forever.
- Partial progress is preserved.
- Feedback is routed to the right role.

---

## 10. Minimal Implementation Pattern

The same logic can be implemented in any language or framework as long as the contracts are preserved.

```python
def stage_payload(role, model, provider, text, confidence, impact, status, reason, parent_id=None, attempt=1):
    return {
        "artifactId": new_uuid(),
        "stage": role,
        "role": {
            "name": role,
            "model": model,
            "provider": provider
        },
        "scores": {
            "confidence": confidence,
            "impact": impact
        },
        "status": status,
        "reason": reason,
        "content": {
            "text": text
        },
        "provenance": {
            "parentArtifactId": parent_id,
            "attempt": attempt,
            "timestamp": now_iso()
        }
    }
```

### Validation boundary

```python
def validate_stage(payload):
    assert payload["stage"] in {"drafter", "writer", "judge"}
    assert 0.0 <= payload["scores"]["confidence"] <= 1.0
    assert 0.0 <= payload["scores"]["impact"] <= 1.0
    assert payload["status"] in {"accepted", "revised", "rejected", "partial"}
    assert isinstance(payload["content"]["text"], str)
    return True
```

This kind of boundary is what makes {trinity} reproducible. Without it, the pipeline is just three prompts with no scientific structure.

---

## 11. Artifact Races and Elo Ranking

In many use cases, one final answer is not enough. The system may need to produce several small, self-contained artifacts for the same target and then choose the best one. A good human-facing metaphor for these small units is **flashcards**: each unit should be consumable in one step and memorable enough to be reused later. In the scientific framing, the more general term is **artifact**.

The pipeline can therefore be extended with a **race layer**:

- generate multiple candidate artifacts for the same target
- compare them pairwise or in small groups
- update a temporary Elo-style rating
- keep only the top fraction
- spend more compute only on the survivors

This is useful when the goal is not merely to produce *an* answer, but to progressively concentrate compute on the best artifacts.

### 11.1 Why Elo fits

Elo is a rating method created by **Arpad Elo**, a Hungarian-American physicist and chess master. It was originally designed for chess and later adapted to other competitive ranking problems. [8, 9]

It is a good fit for {trinity} because:

- it is pairwise and cheap
- it is easy to interpret
- it supports repeated comparison
- it works well when you want a temporary ranking, not a permanent truth score

### 11.2 Race loop

```python
def race_artifacts(artifacts, judge, rounds=3, keep_top_fraction=0.2):
    ratings = {a["artifactId"]: 1000 for a in artifacts}

    for _ in range(rounds):
        pairs = make_pairs(sorted(artifacts, key=lambda a: ratings[a["artifactId"]]))
        for left, right in pairs:
            winner = judge_compare(left, right, judge)
            ratings[winner["artifactId"]] += 16
            loser = right if winner["artifactId"] == left["artifactId"] else left
            ratings[loser["artifactId"]] -= 16

        artifacts = keep_top_percent(artifacts, ratings, keep_top_fraction)

    return sorted(artifacts, key=lambda a: ratings[a["artifactId"]], reverse=True), ratings
```

### 11.3 Elo update

```python
import math

def expected_score(r_a, r_b):
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400.0))

def elo_update(r_a, r_b, result_a, k=32):
    e_a = expected_score(r_a, r_b)
    new_a = r_a + k * (result_a - e_a)
    new_b = r_b + k * ((1.0 - result_a) - (1.0 - e_a))
    return new_a, new_b
```

### 11.4 Resource-aware selection

The race should not spend unlimited compute. A practical policy is:

- compare all artifacts once
- keep only the top x percent
- increase judge depth only for survivors
- stop when quality gain becomes too small

That gives a resource-cost-effective sorting mechanism rather than a brute-force search.

---

## 12. Failure Handling

{trinity} should distinguish content failures from infrastructure failures.

### Content failures

- wrong language
- missing structure
- too short
- insufficient grounding
- low usefulness
- placeholder-style output

### Infrastructure failures

- model unavailable
- runtime crash
- process freeze
- timeout
- invalid response format

### Policy

- Content failures go upstream in the chain.
- Infrastructure failures go to runtime supervision.
- Partial useful output should still be preserved.
- Unknown failure types should fail closed, not silently pass.

---

## 13. Reproducibility Notes

To reproduce {trinity}, a builder should implement:

- a Drafter stage that emits atomic units
- a Writer stage that rewrites those units
- a Judge stage that accepts or rejects them
- a shared schema for handoffs
- a score fusion rule
- a retry cap
- provenance tracking
- a storage model that preserves partial progress

### What should be measured

- parse success rate
- acceptance rate per stage
- retry count distribution
- score calibration
- improvement after feedback
- language purity
- structural completeness

### What should be compared

- {trinity} vs. single-model generation
- {trinity} vs. one-pass summarization
- product fusion vs. alternative fusion rules
- retry-enabled vs. no-retry systems

---

## 14. Example Deployment Shape

{trinity} can run on a local machine, a workstation, or a server. The reference shape is local-first:

- one local inference runtime
- one Drafter model
- one Writer model
- one Judge model
- one coordinator process
- one watchdog or supervisor

This is not a requirement of the theory. It is a practical deployment pattern that keeps cost and data exposure low.

---

## 15. How Others Can Extend {trinity}

Builders can improve {trinity} by:

- replacing the models with stronger local or hosted models
- swapping in a better retry policy
- changing the fusion rule
- adding a fourth role for entity linking or fact verification
- calibrating scores on a labeled dataset
- adding a cross-atom judge pass
- adding a user-feedback memory layer

What must stay the same is the scientific skeleton:

- roles are separated
- handoffs are structured
- scores are explicit
- retries are bounded
- provenance is preserved

---

## 16. Scientific Limitations

{trinity} is not a proof of universal superiority. Its limits are:

- it depends on the quality of role definitions
- it depends on the quality of the stage contracts
- it may underperform a large monolithic model on some tasks
- it requires evaluation data to justify score thresholds
- it still needs operational supervision

These limitations are strengths from a scientific point of view because they define where the hypothesis can be tested.

---

## 17. Conclusion

{trinity} is a three-role pipeline for controlled text transformation. Its contribution is a clear operational theory:

- decompose first
- rewrite second
- judge last
- score explicitly
- retry only when progress is real
- stop after a bounded number of attempts
- preserve partial work

That makes {trinity} easier to measure, easier to debug, and easier to reproduce than a one-shot generation workflow.

For builders, the important point is this: {trinity} is not just a prompt pattern. It is a full algorithmic structure with contracts, scores, retry policy, and provenance.

---

## 18. Methodology and Evaluation

{trinity} should be studied as a system, not as a prompt trick. The right methodology is to compare a role-separated pipeline against simpler baselines under the same input budget.

### 18.1 Methodology

The recommended study design is:

1. Choose a fixed corpus of raw text units.
2. Run {trinity} on the corpus with a fixed attempt cap.
3. Run one or more baselines on the same corpus.
4. Compare outputs using the same scoring rubric and the same human review protocol.

Suggested baselines:

- single-model generation
- two-stage pipeline without a judge
- rule-only rewriting
- judge-only filtering over raw drafts

### 18.2 Metrics

Use at least the following measures:

- **Acceptance rate**: how often the final artifact passes.
- **Parse success rate**: how often stage outputs are valid at the boundary.
- **Retry depth**: how many attempts each artifact needed.
- **Score calibration**: whether higher final scores match higher human acceptance.
- **Language purity**: whether the result stays in the intended language.
- **Structural completeness**: whether all required blocks are present.
- **Improvement delta**: how much better the final artifact is than the first draft.

### 18.3 Evaluation protocol

The protocol should separate three questions:

1. Did the artifact improve?
2. Was the artifact accepted?
3. Was the improvement worth the compute cost?

That separation matters because a system can be better than baseline but still not good enough for acceptance.

### 18.4 Hypotheses to test

- {trinity} improves auditability compared with a single-model baseline.
- {trinity} reduces silent failure by making stage decisions explicit.
- {trinity} improves final quality when the Judge has clear rejection categories.
- {trinity} performs best when retries are bounded and feedback is routed correctly.

---

## 19. Personalization and Digital Me Modeling

{trinity} can be extended into a user-specific system that learns how a particular person writes, decides, prefers structure, and accepts quality. The goal is not to impersonate the user in a deceptive sense. The goal is to model the user’s working style well enough that the system becomes a better assistant for that user over time.

This is best described as a **personalized artifact memory system** or a **digital me layer**.

The framing draws on research in personalized language modeling, feedback-based preference learning, explicit memory architectures, and the “digital me” metaphor. These sources are design inspiration, not evidence that a model can replicate a person exactly. [9][10][11][12][13]

### 19.1 Research question

> Can a {trinity}-style system improve output quality and response efficiency by learning a user-specific ranking over artifacts, stage behaviors, and role preferences?

This question is testable. It can be compared against a non-personalized baseline under the same compute budget.

### 19.2 What gets stored

The system should store only information that helps future ranking, reuse, or personalization.

Recommended stored items are:

- **Artifacts**
  - accepted outputs
  - partially improved outputs
  - rejected outputs with reason codes

- **Artifact metadata**
  - task type
  - language
  - topic
  - stage history
  - attempt count
  - final status

- **User preference signals**
  - preferred tone
  - preferred length
  - preferred structure
  - preferred detail level
  - preferred strictness
  - accepted vs rejected style patterns

- **Role behavior traces**
  - what the Drafter tends to produce for this user
  - what the Writer tends to improve well
  - what the Judge tends to reject or accept

### 19.3 How it gets ranked

Artifacts and behaviors can be ranked with an Elo-style system.

The ranking can be applied to:

- candidate artifacts
- stage templates
- rewrite patterns
- user-specific style memories

The practical update loop is:

1. Generate several artifacts or retrieve several memories.
2. Compare them pairwise.
3. Update ratings.
4. Keep the top fraction.
5. Spend more compute only on the survivors.

This concentrates compute on the most promising artifacts and the most useful remembered patterns.

### 19.4 How feedback updates the ranking

Feedback should update the nearest relevant item:

- user rejection updates the Judge-facing memory
- Judge rejection updates the Writer-facing memory
- Writer rejection updates the Drafter-facing memory

Repeated acceptance of a tone or structure should raise that style’s rank. Repeated rejection should lower it.

### 19.5 How the user profile changes stage behavior

A user profile should not be a single opaque embedding only. It should influence stage behavior in visible ways.

Examples:

- **Drafter**
  - prefers shorter or longer atomic units
  - prefers more or fewer splits
  - emphasizes certain topical boundaries

- **Writer**
  - prefers formal or informal tone
  - prefers direct or explanatory language
  - prefers compact or detailed output

- **Judge**
  - applies user-specific acceptance thresholds
  - favors the user’s preferred tone and structure
  - rejects outputs that are technically correct but stylistically misaligned

### 19.6 Practical recommendation

The recommended implementation is explicit:

- store user preferences as ranked memory entries
- keep flashcard-like artifacts as reusable atomic units
- use Elo only as a temporary ranking and selection mechanism
- do not replace the full trust model with Elo alone

This keeps the system scientifically interpretable while still adapting to user behavior.

### 19.8 Sources and caution

The personalization layer in {trinity} is informed by the following research directions:

- personalized language models that adapt to user-specific style, context, and preference profiles [9]
- personalized feedback learning for user-specific preferences [10]
- digital-me and human-digital-twin style conversational agents [11]
- critiques of the digital twin metaphor, which warn against treating personalization as literal human replication [12]
- memory-first architectures that treat memory as a first-class operational resource [13][14]

The interpretation should remain conservative:

- use these ideas to model user behavior, preference, and style
- do not claim the system is a true person
- do not treat metaphor as identity
- use the digital-me framing only as a controlled engineering analogy

### 19.7 Code sketch

```python
class UserProfile:
    def __init__(self):
        self.style_ratings = {}
        self.artifact_ratings = {}
        self.role_preferences = {
            "drafter": {},
            "writer": {},
            "judge": {}
        }

def update_profile(profile, artifact, feedback):
    key = artifact["artifactId"]
    current = profile.artifact_ratings.get(key, 1000)
    delta = feedback.get("rating_delta", 0)
    profile.artifact_ratings[key] = current + delta
    update_role_memory(profile, artifact["stage"], feedback)
    return profile

def adapt_stage_behavior(profile, stage_name, base_prompt):
    preferences = profile.role_preferences.get(stage_name, {})
    return apply_preferences(base_prompt, preferences)
```

---

## 20. Glossary

### Roles

- **Drafter**: The role that splits raw input into atomic information units.
- **Writer**: The role that rewrites atomic units into clearer and more usable text.
- **Judge**: The role that evaluates whether the rewritten unit should be accepted.

### Score fields

- **confidence**: A normalized estimate of correctness, grounding, or fit.
- **impact**: A normalized estimate of decision value or usefulness.
- **final confidence**: The fused confidence after all stages have been applied.
- **final impact**: The fused impact after all stages have been applied.

### Workflow fields

- **artifactId**: A stable identifier for a unit of work.
- **stage**: The current role in the pipeline.
- **status**: The current state of the artifact, such as accepted, revised, rejected, or partial.
- **reason**: A short explanation of why the stage accepted or rejected the artifact.
- **provenance**: The history of how the artifact was created and modified.

### Policy terms

- **attempt cap**: The hard limit on how many times a single atomic artifact may be generated or revised.
- **failure class**: The category of a rejection, such as language, structure, clarity, or infrastructure.
- **partial save**: Preserving an improved artifact even if final acceptance does not happen.

---

## 21. Research on Similar Ideas

{trinity} is not isolated. Similar ideas appear in several fields. The point of this section is not to claim direct lineage, but to show that the same structural patterns recur across disciplines.

### 21.1 Computer science

**Mixture-of-Experts and routing.**  
Sparse expert models route inputs to specialized submodels rather than forcing one monolithic model to process everything. This is close to {trinity}’s role separation: a router decides where a piece of work should go, and only a subset of specialized computation is activated for each input. Switch Transformer is a canonical example of this routing idea in large-scale neural systems. [1]

**Blackboard systems.**  
Blackboard architectures coordinate independent knowledge sources through a shared workspace. Hearsay-II is a classic example: multiple specialized processes cooperate by posting partial hypotheses and refining them through shared state. {trinity} resembles this pattern because the artifact is refined through stage-local contributions and explicit handoffs rather than a single hidden monolith. [2]

**Pipeline parallelism.**  
In systems and model-serving research, a pipeline divides work into stages to improve throughput and isolate responsibilities. {trinity} borrows the same logic at the algorithmic level: stage separation reduces entanglement, even if the stages run sequentially on one machine.

### 21.2 Mathematics and physics

**Divide-and-conquer.**  
{trinity} is structurally similar to divide-and-conquer: break a large problem into smaller subproblems, solve each subproblem, and combine the results. The difference is that {trinity} does not purely split by size; it splits by role. Drafter, Writer, and Judge are specialized transformations in a recursive-style correction loop.

**Controlled recurrence with bounded depth.**  
The retry cap makes {trinity} a bounded recurrence rather than an open-ended feedback loop. This is mathematically important because it keeps the process analyzable. The system’s cost can be treated as a recurrence with a fixed maximum depth.

From a physics perspective, this is closer to a controlled, dissipative process than to an unconstrained amplifier: each correction step consumes compute and either improves the state or terminates the loop.

### 21.3 Biology

**Kinetic proofreading.**  
Biological systems such as DNA replication and tRNA charging use extra checkpoints to improve fidelity beyond what simple binding affinity would allow. Hopfield’s kinetic proofreading showed that energy-consuming intermediate steps can greatly reduce errors. {trinity} is similar in spirit: the Judge acts as an explicit fidelity checkpoint, and failed items are not simply accepted because they look plausible. [3, 4, 5]

**Layered signaling and immune discrimination.**  
Immune systems often use multiple layers of screening before a signal is accepted. That pattern matches {trinity}’s feedback chain: a candidate artifact moves forward only when it survives successive checks.

### 21.4 Chemistry

**Cascade reactions.**  
Cascade chemistry chains multiple transformations so that the output of one step becomes the input of the next. {trinity} is analogous in workflow structure: a raw artifact is progressively transformed by distinct roles rather than one catch-all step. A useful chemical analogue is a reaction network that mimics adaptive immune response by staging recognition, amplification, and response. [6, 7]

**Reaction selectivity through staged intermediates.**  
Chemical cascades often rely on intermediates that are not final products but still matter for the end result. {trinity} likewise values partial artifacts: a weak draft may still be a useful intermediate if the next stage can improve it.

### 21.5 Practical interpretation

The common scientific theme across these fields is:

- **specialize**
- **checkpoint**
- **route feedback**
- **bound the number of correction steps**
- **preserve intermediate state**

That is the core {trinity} pattern.

---

## 22. References

[1] Fedus, W., Zoph, B., & Shazeer, N. (2021). *Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity.* arXiv preprint arXiv:2101.03961. <https://arxiv.org/abs/2101.03961>

[2] Erman, L. D., Hayes-Roth, F., Lesser, V. R., & Reddy, D. R. (1980). *The Hearsay-II Speech-Understanding System: Integrating Knowledge to Resolve Uncertainty.* In *Computational Models of Speech Pattern Processing*.

[3] Hopfield, J. J. (1974). Kinetic proofreading: A new mechanism for reducing errors in biosynthetic processes requiring high specificity. *Proceedings of the National Academy of Sciences*, 71(10), 4135-4139.

[4] McKeithan, T. W. (1995). Kinetic proofreading in T-cell receptor signal transduction. *Proceedings of the National Academy of Sciences*, 92(11), 5042-5046.

[5] *DNA-based artificial molecular signaling system that mimics basic elements of reception and response.* (2020). *Nature Communications*.

[6] Han, D., Wu, C., You, M., et al. (2015). A cascade reaction network mimicking the basic functional steps of adaptive immune response. *Nature Chemistry*.

[7] Elo, A. E. (1978). *The Rating of Chessplayers, Past and Present.* Arco.

[8] Fédération Internationale des Échecs (FIDE). *Rating Regulations and handbook materials on Elo-style ratings.* <https://www.fide.com/>

[9] Liu, J., Qiu, Z., Li, Z., Dai, Q., Zhu, J., Hu, M., Yang, M., & King, I. (2025). *A Survey of Personalized Large Language Models: Progress and Future Directions.* arXiv preprint arXiv:2502.11528. <https://arxiv.org/abs/2502.11528>

[10] Li, X., Zhou, R., Lipton, Z. C., & Leqi, L. (2024). *Personalized Language Modeling from Personalized Human Feedback.* arXiv preprint arXiv:2402.05133. <https://arxiv.org/abs/2402.05133>

[11] Coll, A., et al. (2025). *Towards the "Digital Me": A Vision of Authentic Conversational Agents Powered by Personal Human Digital Twins.* arXiv preprint arXiv:2506.23826. <https://arxiv.org/abs/2506.23826>

[12] *Personalised LLMs and the Risks of the Digital Twin Metaphor.* (2026). *AI & Society*. <https://link.springer.com/article/10.1007/s00146-026-02875-4>

[13] *MemOS: An Operating System for Memory-Augmented Generation (MAG) in Large Language Models.* (2025). arXiv preprint arXiv:2505.22101. <https://arxiv.org/abs/2505.22101>

[14] *MemGPT: Towards LLMs as Operating Systems.* (2023). arXiv preprint arXiv:2310.08560. <https://arxiv.org/abs/2310.08560>
