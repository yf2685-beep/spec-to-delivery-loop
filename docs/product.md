# Product and delivery rationale

## User problem

A product owner needs to know whether a generated feature satisfies its requirements. An engineer needs to diagnose failures and review a small artifact. A reviewer needs to distinguish “tests passed” from “approved for delivery.” A chat transcript alone makes these decisions difficult to repeat.

## Smallest useful vertical slice

This project turns a fictional booking requirement into one Python function, checks it, feeds specific failures back, and presents a candidate for review. It intentionally covers the whole delivery path before expanding to multiple files, tools or model providers.

The first draft allows a zero-person booking and a negative existing-booking count. Two named checks expose those omissions. The demo adapter supplies a repair and all ten acceptance checks run again. This creates an observable failure-and-repair example without requiring a paid model.

## Acceptance rubric

| Dimension | Evidence | Decision |
| --- | --- | --- |
| Scope and contract | Named specification and input/output contract | A spec with no acceptance cases is rejected |
| Structural validity | Compilation and restricted syntax results | Unsupported code cannot proceed to execution |
| Functional behavior | Ten expected/actual comparisons | Every bundled case must pass |
| Diagnosis | Failed criterion IDs and next action | Feedback is retained in the next iteration |
| Reviewability | Source snapshots, hashes and report | Reviewer can compare the failing and passing draft |
| Delivery control | Separate decision after all gates pass | Reject, stop and pause never become delivered |

## Human and agent responsibilities

Product work defines the intended behavior, examples, scope and acceptance criteria. The adapter proposes a candidate and responds to feedback. The harness applies the checks, limits iterations and records results. The human reviews the candidate and decides whether to deliver it.

The legacy route requires a human compatibility note before generation. In this small demo the note is stored in the trace; the scripted adapter does not interpret arbitrary legacy semantics. A real integration should turn those constraints into additional tests and include them in the model context.

## What to measure next

For a real provider, measure criterion pass rate, failed-gate types, repair rounds, review rejection reasons, human intervention count, cost and wall time on a fixed task set. Version the specs and tests with the artifacts. Do not infer real-world accuracy, development time savings or model quality from this deterministic example.

## Deliberate scope

Included: requirement, single-file candidate, feedback loop, quality gates, explicit approval and local artifact delivery. Future extensions: model-backed adapter, isolated executor, multi-file dependency planning, durable multi-user state and authenticated reviews. These extensions are not presented as completed features.
