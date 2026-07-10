# BrainOS retrieval evaluation scenarios

This file defines the small canonical scenario set that BrainOS currently treats as its bounded retrieval evaluation surface.

Use it for three things:
- keeping retrieval claims tied to a stable, reviewable scenario set
- distinguishing seeded-fixture evidence from small real-sample evidence
- making regression review less impressionistic

This is intentionally small. If the set grows without a strong reason, it becomes harder to review and easier to overclaim.

## Scenario classes

### 1. Exact-ish operational recall
Goal: verify that direct or near-direct wording retrieves the expected operational episode and semantic anchor.

Current canonical queries:
- `sqlite wal durability`
- `azure embedding model`
- `how to repair stale vectors`
- `disabled vector runtime`
- `policy version explain`

Expected behavior:
- the top ranked episode should align to the expected seeded operational fact
- the top semantic hit should align to the expected concept/capability/procedure anchor
- failure should be inspected before any claim of retrieval-quality improvement or regression

### 2. Paraphrased operational recall
Goal: verify that bounded paraphrase still lands on the same intended evidence rather than only exact token overlap.

Current canonical queries:
- `what helps BrainOS keep local writes safe?`
- `what is the current BrainOS embedding path?`
- `what should I do after runtime changes to vectors?`
- `what does disabled vector state usually point to?`
- `what should retrieval explain show?`

Expected behavior:
- top results should remain aligned to the same seeded target as the paired exact-ish query
- any change in this behavior should be treated as a real review event, not waved away as prompt variance

### 3. Real-sample probe
Goal: verify that retrieval still produces interpretable output on a small available live sample without pretending to prove broad corpus quality.

Current probe queries:
- `brainos initialized with wal`
- `store semantic fact`

Expected behavior:
- the probe should return an interpretable result on the chosen session sample when one exists
- the probe should be read as a small real-sample signal only
- absence of a strong hit is evidence of limited sample coverage, not automatic proof of broken code

### 4. Low-evidence and degraded-runtime interpretation
Goal: keep failure semantics explicit.

Expected behavior:
- runtime misconfiguration should be distinguishable from low evidence
- degraded vector readiness should not be reported as broad retrieval failure
- fallback behavior should stay operator-readable and not look like silent success

### 5. Explainability and ranking interpretation
Goal: make ranking behavior inspectable instead of magical.

Expected behavior:
- explain output should expose the scoring policy version
- explain output should expose top-hit evidence, comparison hint, and diagnostic hint
- when available, the retrieval trace should show candidate generation, ranking inputs, and why the top result won

## Evidence interpretation rules

- The retrieval benchmark is seeded-fixture evidence. It is useful for regression detection, not for broad relevance claims.
- The real-corpus probe is small real-sample evidence. It is stronger than a pure fixture but still bounded.
- A green run means the current bounded scenario set still behaves coherently. It does not prove general retrieval quality.
- A red run means either runtime drift, benchmark seed drift, or a real quality regression. Inspect before concluding which.

## Review posture

Before describing BrainOS retrieval as healthier, stronger, or improved, check:
1. did the canonical scenario set still pass?
2. did the real-sample probe remain interpretable?
3. did explain/trace output make the result understandable?
4. are docs still describing the current evidence honestly?

If any answer is no, the project may still be coherent, but the claim needs to stay bounded.