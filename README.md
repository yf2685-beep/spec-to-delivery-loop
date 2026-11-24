# Spec to Delivery Loop

**把需求规格变成可检查、可修复、可审核的工程交付过程。**

A small, runnable portfolio framework for a specification-driven development loop: observe → plan → generate → verify → reflect → repair → human review → delivery.

The example implements a **fictional workshop seat-booking policy**. A deliberately incomplete first draft fails two real acceptance checks; structured feedback drives a second, passing draft. The run then waits for a separate approval decision. Everything runs locally with Python 3.10+ and the standard library.

**Scope:** generation and reflection use a deterministic demonstration adapter, not a live LLM. Compilation, syntax checks and acceptance execution are real. This is a newly written public example of the workflow, not an enterprise code release or evidence of a production autonomous deployment.

## Try the complete loop

~~~bash
git clone https://github.com/yf2685-beep/spec-to-delivery-loop.git
cd spec-to-delivery-loop
python3 -m looplab run --output runs/demo
~~~

The expected status is **awaiting_review**, after two attempts. Open **runs/demo/report.html** in a browser to compare the source versions, see which criteria failed, and inspect the execution trace. The HTML is standalone and needs no server.

After inspecting the result, record the local demo decision:

~~~bash
python3 -m looplab review runs/demo --decision approve
# Or reject the candidate:
# python3 -m looplab review runs/demo --decision reject
~~~

Approval reruns the checks, verifies the artifact and spec hashes, and writes **runs/demo/delivery/booking_policy.py**. It does not deploy, push or merge anything. Choose a new output directory for each run; existing runs are preserved.

[Recorded sample report](docs/sample-run/report.html) · [Sample trace](docs/sample-run/trace.jsonl) · [Product and delivery rationale](docs/product.md) · [Architecture](docs/architecture.md)

## The loop

~~~mermaid
flowchart TD
    S[Spec and acceptance criteria] --> M{Work mode}
    M -->|Isolated feature| O[Observe and plan]
    M -->|Legacy change| H[Human compatibility context]
    H --> O
    O --> G[Generate candidate artifact]
    G --> V[Compile / restricted syntax / acceptance checks]
    V -->|Fail, budget remains| R[Structured failure and reflection]
    R --> G
    V -->|Fail, budget exhausted| X[Stop with diagnostic trace]
    V -->|Pass| A[Explicit human review]
    A -->|Reject| N[Rejected]
    A -->|Approve and recheck| D[Local delivery artifact]
~~~

## What this demonstrates

| Product / engineering question | Implementation |
| --- | --- |
| What counts as done? | Named acceptance criteria, passing gates, and an explicit review decision |
| Why did the draft fail? | Criterion IDs, observed results, a diagnosis and the next corrective action |
| Does the loop retry blindly? | It supplies failed-gate feedback to the next generation attempt |
| How is autonomy bounded? | A 1–10 iteration budget, a legacy-context checkpoint, and separate approval |
| Can a reviewer inspect the result? | Candidate source snapshots, JSON/JSONL trace, hashes and an HTML comparison report |
| What becomes reusable? | Spec format, adapter interface, gate result structure, state transitions and review flow |

The bundled specification contains ten checks: normal bookings, exact capacity, overflow, zero/negative requests, invalid counts and empty/already-full workshops. It contains no real people, organizations, accounts or customer records.

## Explore alternative outcomes

~~~bash
# Stop after the intentionally failing first draft (exit code 1).
python3 -m looplab run --output runs/one-attempt --max-iterations 1

# Pause before generation when legacy context is absent.
python3 -m looplab run --output runs/legacy-paused --mode legacy

# Proceed using the fictional compatibility note.
python3 -m looplab run --output runs/legacy-informed --mode legacy \
  --context examples/legacy-context.txt

# Run regression tests.
python3 -m unittest discover -s tests -v
~~~

## Repository map

| File | Responsibility |
| --- | --- |
| examples/workshop-booking.json | Fictional requirement and acceptance cases |
| looplab/engine.py | Bounded state transitions, feedback, review and delivery |
| looplab/demo_agent.py | Adapter contract and deliberately scripted repair behavior |
| looplab/checks.py | Real compiler, restricted Python syntax check and acceptance runner |
| looplab/report.py | Readable HTML walkthrough of actual trace data |
| tests/test_loop.py | Repair, budget, review, legacy context and change-detection regressions |
| docs/ | Product rationale, architecture and one recorded local run |

## Public portfolio boundary

Created for Yuxuan Feng's portfolio. All code, prose and fixtures here were written as an independent, generic demonstration. No company repository/history, internal specification, customer case, enterprise object name, system address, credential, source code or original internal presentation is included. No corporate connection is required.

The current adapter only solves the bundled booking example; this is not a general coding agent or an LLM benchmark. The subprocess is **not a general sandbox for untrusted code**: the demo permits a very small expression-only function, and adding a model adapter requires a proper isolated execution service. Local hashes detect accidental artifact/spec changes; they are not tamper-proof audit signatures. Review records model a workflow and do not authenticate a reviewer.
