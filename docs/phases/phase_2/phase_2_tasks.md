# Phase 2 tasks

Plan: `docs/phases/phase_2/phase_2_plan.md` (revision 1, 2026-11-25). **No task starts before the Phase 1 G3 sign-off row is in `docs/RETRO.md` and the plan's `plan-review` says READY.** Documents only: no change in `src/`, `tests/`, `pyproject.toml` or the lock files. At most 2 agents at once. Update status to `☑ done` with proof (commit hash + check output) as each task closes. Owner sittings: A = O1–O3, B = O4, C = O5–O6, D = G2 and G4.

| ID | Task | Owner | Depends on | Status | Proof | Notes |
|---|---|---|---|---|---|---|
| S0 | Start check; record baseline commit; collect Phase 1 inherits (B10 run 2, G2 findings, known issues) into `inputs.md` | agent | Phase 1 G3; plan-review READY | ☐ not started | | Inputs list every inherit with source; baseline hash recorded |
| S1 | Scope memo: FR-27..FR-30 dispositions, spine cut, owner choices (accounts, host, notifier, R-27 substitute, key scope) | agent | S0 | ☐ not started | | Every FR/NFR row: spine, or deferred with must-exist-by |
| S4 | Alpaca and calendar facts for the spec, docs only, in verification_log §10 | agent | S0 | ☐ not started | | Every fact cited with access date or unverified |
| S2 | E-1 remaining definitions and cited sector classification; no price data viewed | agent | S0 | ☐ not started | | Each open item proposed; sectors cited; attestation written |
| E1 | Engine install-check protocol: backtest-only checks, isolated venv, synthetic data | agent | S0 | ☐ not started | | Protocol complete; per-engine approval lines left blank |
| S3 | `LIMITS_CONFIG.md` with loss-limit definitions; `owner_parameters.md` worksheet | agent | S1, S4 | ☐ not started | | Every D-01..D-23 mapped; domains and risk direction present |
| O1 | Decide FR-27..FR-30, spine cut, S1 owner choices; record key-scope revisit | owner | S1 | ☐ not started | | Scope memo owner column filled; RETRO rows dated |
| O2 | E-1: pick the third name; approve or amend the open definitions | owner | S2 | ☐ not started | | decisions.md §2 frozen; RETRO row dated |
| O3 | Approve or decline each engine install in writing | owner | E1, O2 | ☐ not started | | Dated approval line per engine |
| O4 | Fill the owner worksheet; approve or amend agent-proposed values | owner | S3 | ☐ not started | | No blank owner cell; RETRO debt row closed |
| I1 | `INTERFACES.md`: versioned contracts for every layer | agent | S1, S4, O1 | ☐ not started | | Each layer versioned, errors declared, contract tests listed |
| T1 | `TAX_MODEL.md` from published federal and NJ rules, "not CPA-reviewed" | agent | S3 | ☐ not started | | Formula, cited rules, worked examples, label present |
| E2 | Run the install-check per approved engine; matrix amendment; propose choice and fallback | agent | O3 | ☐ not started | | Each check has output; lock files unchanged |
| SP1 | `SPEC.md`: numbered clauses, state machines, reason codes | agent | I1, S3, O1 | ☐ not started | | Every spine requirement has a testable clause |
| R1 | `REPORTS.md` and the final `docs/checkins/README.md` schema | agent | O1 | ☐ not started | | Four formats, schema, two-minute budgets present |
| H1 | `HAZARDS.md` FMEA; new patterns as P-29 onward | agent | SP1, I1, T1, R1 | ☐ not started | | Every INV, R-13..R-68, C-1..C-12 has control and verification |
| O5 | Record the engine choice (or "none yet" and fallback) in RETRO | owner | E2 | ☐ not started | | Dated RETRO engine row |
| O6 | Approve or reject each P-29+ proposal | owner | H1 | ☐ not started | | No proposal left `proposed` |
| H2 | `FAULT_INJECTION.md`: the Phase 3 gate suite | agent | H1 | ☐ not started | | Every severity 3–4 hazard has an FI with reason code |
| TR1 | `TRACE.md`; run failure-check on the spec set | agent | H2 | ☐ not started | | No blank trace cell; failure-check shows 0 missing |
| P1 | PRD v0.5, decisions.md D-24+, merge approved P-29+, RETRO debt closures | agent | O1, O2, O4, O5, O6, TR1 | ☐ not started | | PRD v0.5; debt rows closed with links |
| G1 | phase-gate with failure-check on the delivered spec | agent | P1, E2 | ☐ not started | | Eval completion section and summary; ADVANCE or HOLD |
| G2 | Graded design review: red-team in a fresh session, G-11 rubric | owner | G1 | ☐ not started | | Redteam file with scores and go/no-go |
| G3 | Resolve G2 findings; each closed or owner-accepted | agent | G2 | ☐ not started | | No open critical or high finding |
| G4 | Owner sign-off row in RETRO | owner | G3 | ☐ not started | | Dated RETRO sign-off row exists |
| O7 | Optional: settle GTC stop-limit extended-hours election (hand-placed paper test or Alpaca support) | owner | S4 | ☐ not started | | verification_log §8 updated, or spec keeps worst case |
