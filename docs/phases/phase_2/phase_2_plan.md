# Phase 2 plan: spec, hazard analysis, interface contracts, safety-spine cut

Status: revision 1 · Written 2026-11-25 · Traces to `docs/PRD.md` v0.4 (incl. proposed FR-27 to FR-30) · Inputs: `docs/phases/phase_0/decisions.md` (D-01 to D-23, E-1 §2), `docs/RETRO.md`, `docs/research/FAILURE_LIBRARY.md` (F-01 to F-47, R-13 to R-68), `docs/research/decision_matrix.md` §9, `docs/phases/phase_1/` (summary, hand-off, eval).

**Entry condition: Phase 1 is on HOLD** for B10 run 2 (Fri 27 Nov or from Mon 30 Nov), G2 red-team and G3 owner sign-off. No unit below starts before the G3 sign-off row is in RETRO (CLAUDE.md: one phase at a time) and this plan's `plan-review` says READY. §7 lists what depends on each held item.

**Phase 2 writes documents, not code.** Nothing changes in `src/`, `tests/`, `pyproject.toml` or the lock files. The only install is the engine install-check (E2): an isolated, git-ignored venv, one engine at a time, each needing the owner's explicit written approval.

**Speed principle.** The goal is Phase 5 paper trading as fast as it is safe. Phase 2 therefore fixes a **small spine**: the minimum Phase 3 must build before the first automated paper order. Everything else gets a "must exist by" phase and an interim control. An item may leave the spine only if the hazard analysis (H1) shows no hazard of severity 3 or 4 relies on it before that phase.

## 1. Goal and gate

**Goal:** a reviewed, traceable specification that a Phase 3 session can build without questions. It covers the system spec, the signed limits config, interface contracts, the tax model, report formats, a hazard analysis and the fault-injection suite that becomes the Phase 3 gate. Phase 2 also closes the open owner parameters, freezes E-1 and runs the engine install-check.

**PRD §6 gate (Phase 2):** "SPEC.md, FMEA, interface contracts: samd-design-review style graded review; owner sign-off. The tax model is built from published federal and NJ rules and labelled 'not CPA-reviewed' until the CPA signs off before the Phase 6 gate." The graded review uses this repo's `red-team` skill with the rubric in G-11 (no HSS skills; CLAUDE.md).

**Testable gate. Every item must hold.** PowerShell checks run from the repo root.

| # | Criterion | How it is checked |
|---|---|---|
| G-1 | **Spec complete.** `docs/spec/SPEC.md` gives every spine requirement (§2.2) at least one numbered clause `SP-nnn` with an acceptance criterion. Every deferred requirement has a "must exist by" phase and an interim control. No `TBD`, `TODO` or `??` in `docs/spec/` | `Select-String -Path docs\spec\*.md -Pattern 'TBD|TODO|\?\?'` returns nothing; TRACE.md has no blank cell (G-8) |
| G-2 | **Hazards cover the library.** `docs/spec/HAZARDS.md` has a row for every invariant 1–18, every rule R-13 to R-68 and every compliance item C-1 to C-12. Each row names a control (an `SP-` clause) and a verification (an `FI-` test or a named Phase 3 unit test), or gives a one-line not-applicable reason | `13..68 \| ? { -not (Select-String docs\spec\HAZARDS.md -Pattern "R-$_\b" -Quiet) }` returns nothing; the same loop for `INV-1..18` and `C-1..12`; `failure-check` on the spec set shows 0 `missing` |
| G-3 | **Limits config fixed.** `docs/spec/LIMITS_CONFIG.md` maps every D-01 to D-23 to a field with type, unit, domain, risk-up direction and source. The loss-limit definitions are fixed with worked examples (RETRO debt row). Every owner-set parameter is filled by the owner (RETRO debt row "Parameters still unset" closed). Every agent-proposed operational value is approved or amended by the owner | `1..23 \| % { 'D-{0:D2}' -f $_ } \| ? { -not (Select-String docs\spec\LIMITS_CONFIG.md -Pattern $_ -Quiet) }` returns nothing; `docs/phases/phase_2/owner_parameters.md` has no blank owner cell; RETRO rows dated |
| G-4 | **Interfaces versioned.** `docs/spec/INTERFACES.md` defines a contract for each layer: data, clock and calendar, strategy, kernel, broker, ledger, notifier and command channel, LLM, backtest engine. Each has a version, typed signatures, the domain errors it may raise (R-66) and its contract-test list. The kernel contract is pure (no I/O types in any signature) | phase-gate reads each section; a grep for `Version:` returns one line per layer |
| G-5 | **Fault-injection suite defined.** `docs/spec/FAULT_INJECTION.md` gives at least one `FI-nn` test for every hazard of severity 3 or 4. Each FI states the fault, the injection point (which fake), the precondition, and the expected end state with its reason code (R-46). It includes every test the library names in R-47 to R-68 | trace check: each S3/S4 hazard row in HAZARDS.md cites an FI that exists in FAULT_INJECTION.md |
| G-6 | **Tax model.** `docs/spec/TAX_MODEL.md` gives the reserve formula (tax with minus tax without, federal and NJ, floored at zero), short/long-term rules, wash-sale handling, lot method and the estimated-payment schedule. Each rule cites a published IRS or NJ Division of Taxation source with an access date. The label "not CPA-reviewed" appears in the doc header and in every output format it specifies. Worked examples double as Phase 3 test vectors | the label grep finds the header and each output spec; every rule row has a URL |
| G-7 | **Reports and check-ins.** `docs/spec/REPORTS.md` fixes the daily push, weekly report and form, monthly review and quarterly form, each with a line or field budget for "under 2 minutes" (D-19). `docs/checkins/README.md` carries the final front-matter schema. Answers never trigger a trade or mode change (FR-26) | phase-gate reads both; the schema example parses as YAML by eye (no code this phase) |
| G-8 | **Traceability.** `docs/spec/TRACE.md` maps every FR-1 to FR-31, NFR-1 to NFR-8, invariant, R-13 to R-68 and C-1 to C-12 to SP clauses, hazards and FI or test IDs, with "spine" or "deferred: must exist by Phase N" | `1..31 \| ? { -not (Select-String docs\spec\TRACE.md -Pattern "FR-$_\b" -Quiet) }` returns nothing; same for NFR-1..8 |
| G-9 | **Engine install-check done** for every engine the owner approved, with each check result and its command output in `docs/phases/phase_2/engine_install_check.md`, the matrix amendment rows in `decision_matrix.md`, and the owner's engine choice (or "none yet", with the fallback) recorded in RETRO. Lock files and `pyproject.toml` are unchanged | report and RETRO row exist; `git diff --exit-code <baseline> -- pyproject.toml requirements.lock requirements-dev.lock` exits 0 |
| G-10 | **Owner records.** E-1 frozen in `decisions.md` §2 (third name, cited sector classification, remaining definitions) with an attestation that no price data was viewed first; FR-27 to FR-30 accepted, narrowed or rejected and the PRD bumped to v0.5; the spine cut (§2.2) accepted or amended; the owner choices in S1 answered | RETRO rows dated; PRD header says v0.5 |
| G-11 | **Graded design review** in a fresh session with the `red-team` skill. Eight dimensions, each scored 0–3: (1) completeness against the PRD and spine, (2) verifiability of every clause, (3) hazard and FI coverage, (4) consistency across the spec files, (5) safety (red-team items 1, 2, 4, 8), (6) operations and data (items 3, 9), (7) tax and compliance (items 5, 10), (8) cost and scope (item 7, and whether the spine is the smallest safe one). **GO** = no dimension below 2 and no open critical or high finding | `docs/phases/phase_2/phase_2_redteam.md` with the score table and go/no-go; every finding closed or owner-accepted in G3 |
| G-12 | **Process.** plan-review READY, phase-gate ADVANCE, the four quality gates green with no change under `src/` or `tests/`, the owner's sign-off row in RETRO | `phase_2_eval.md`, `phase_2_summary.md`; `git diff --stat <baseline> -- src tests` is empty; RETRO row |

`<baseline>` is the commit recorded by S0.

## 2. Scope

### 2.1 Requirement IDs covered

| ID | Coverage this phase |
|---|---|
| PRD §6 Phase 2 gate | Full |
| PRD §5 engine choice | Full: install-check (backtest-only scope, RETRO 2026-11-25) and owner choice |
| FR-1 to FR-26 | Specified: spine items to build depth (clauses with acceptance criteria), deferred items to interface depth plus "must exist by" |
| FR-27 to FR-30 (proposed) | Disposition proposed (S1), decided by the owner (O1), then specified to the agreed scope |
| FR-31 (E-1) | Full for Phase 2: remaining definitions frozen (S2, O2); runs in Phase 4 and 5 |
| NFR-1 to NFR-8 | Specified; NFR-1 and NFR-2 shape the kernel contract |
| Invariants 1–18, R-13 to R-68 | Every one carried into a spec clause and a hazard row (G-2) |
| C-1 to C-12 | Every one carried (§6) |
| RETRO debt | Loss-limit definitions (agent); unset parameters (owner); E-1 third name (owner) and cited sectors (agent); engine install-check; C-10 retention proposal; config-signing design; secrets-manager design; key-scope revisit "before Phase 3" |

### 2.2 Proposed spine cut (S1 refines it; the owner accepts it at O1)

**Spine** = what Phase 3 builds and its fault-injection gate proves before the first automated paper order.

| # | Spine component | Requirements | Why it can't wait |
|---|---|---|---|
| 1 | Preflight: paper host and config signature, version, clean tree, single-instance lock, `no_shorting` asserted, clock check, keep-awake, credential expiry | INV-17, R-13, R-48, R-51, R-57, R-65, R-68 | Refuse to run before anything can go wrong |
| 2 | Signed limits config, 24-hour delay for risk-up, risk-mode state machine with UPGRADE | INV-2, INV-3, FR-2, FR-12, FR-28 | Limits must exist before the kernel can enforce them |
| 3 | One egress layer and our own thin Alpaca client, shared request budget, declared errors | R-53, R-56, R-66, R-67 | The only route to the broker |
| 4 | Boundary parsers: required decision fields only, value domains | R-58, R-63 | Bad data must fail closed |
| 5 | Market data: IEX quotes, per-symbol data age, REST cross-check, trading status and halts, exchange calendar | INV-14, R-24, R-50, R-52 | No entry on stale data or in a halt |
| 6 | Pure risk kernel with reason codes: invariant 11 list, sleeve limits D-07 to D-13, trade caps, sellable quantity, regular-session only, `unknown`-order block, restricted list, options and shorts rejected, Tier A/B/C routing, settled cash, opposite-side window | INV-1, 11, 13, 16, 18; FR-11, FR-15 to FR-17; R-28, R-32, R-46, R-47, R-51, R-62; C-1, C-3, C-4, C-8 | The heart of the system |
| 7 | Own execution loop and order manager: idempotent IDs, `unknown` state, protective stop-limits read back and coverage-checked, partial fills, replace rules | FR-18, FR-19, R-47, R-49, R-51, R-54, RETRO engine scope | Orders behave predictably |
| 8 | Append-only, anchored ledger: intents, decisions incl. rejected and skipped, orders, fills, fees, lots, cost re-score, run ID, manual options-track entries | INV-9, NFR-6, FR-5, FR-21 (lots), R-41, R-48, R-54, R-55, R-61 | Reconciliation and the honest scorecard need it |
| 9 | Reconciler before every order and daily; foreign-order detection | INV-9, R-48, R-55 | Catches broker and ledger disagreement |
| 10 | Supervisor, dead-man watchdog (entries only), loop-lag watchdog, kill switch, self-halt on aberrant rates | INV-4, INV-15, FR-20, R-15, R-64, R-68 | Safety moves when something breaks |
| 11 | Paging and a fixed-grammar command channel: kill, status, approve and deny with expiry, mode down, mode up with TOTP and delay | FR-16, FR-25, R-16, D-22 | Tier B approvals and the kill switch |
| 12 | Daily one-line push and weekly report, paper-scaled to $35k | FR-24 (push), FR-26 (weekly), D-02, D-19 | Weekly check-in runs from Phase 5 week 1 |
| 13 | Tax reserve estimate from ledger lots (federal and NJ, "not CPA-reviewed"), wash-sale detection inside the automated accounts | INV-12, FR-21, FR-22 (estimate), C-5 | After-tax scorecard in Phase 5 |
| 14 | Core band check (D-23) producing Tier B proposals only | FR-13, D-23 | The paper core exists from Phase 5 day 1 |
| 15 | Test-weakening guard (test manifest checked before every commit) | R-59 | Phase 3 writes most of the tests |

**Deferred, with must-exist-by and interim control (H1 checks each one):**

| Item | Requirements | Must exist by | Interim control |
|---|---|---|---|
| Full dashboard | FR-24 (full) | Phase 6 gate | Daily push, weekly report, `status` command |
| News alerts and "why is it moving" briefs; adjacent symbols | FR-8, FR-9 | Phase 6 gate | News never triggers trades (INV-6); halts come from trading status |
| Market-wide monitors (breadth, credit, volatility), regime-anomaly detection, automatic de-risking breakers | FR-10, FR-13 (breakers), FR-29 | Phase 6 gate | Sleeve entry halts D-07 to D-10, resting stops, kill switch, owner mode-down |
| Estimated-payment schedule, CPA export, household-wide wash sales across other accounts, real reserve sweep | FR-22 (sweep), FR-23, FR-21 (household) | Phase 6 gate | Restricted list in the kernel; paper reserve is a ledger figure |
| Monthly review and quarterly form generators, decay alarm | FR-26, R-60 | Phase 5 start (built in Phase 4) | None needed before the first month ends |
| LLM adapter and consistency check | FR-4 (LLM part), R-29, R-31 | When the owner approves LLM spend (D-16) | Kernel rejects LLM-origin proposals until R-29 exists |
| iNAV check for ETFs | R-27 | Owner choice at O1 (no documented free source) | Collars against a REST snapshot, no first/last 5 minutes, halt on trading-status code "V" (S4 verifies) |
| Improvement loop beyond PR-only changes | FR-30 | Its own phase-plan | PR-only workflow and R-59 |

### 2.3 Non-goals (explicit)
- Any code in `src/` or `tests/`, any new dependency, any change to `pyproject.toml` or the lock files.
- Any order, cancel or account-config write by code or agent, paper included. O7's optional GTC stop-limit test, if the owner chooses it, is placed **by hand** in the Alpaca paper dashboard.
- Building any spine component (Phase 3). Writing the Phase 3 plan (after the Phase 2 gate).
- Strategy backtests or any look at E-1 price data (Phase 4). The install-check uses synthetic data only.
- Choosing the live broker, buying data, creating cloud resources, signing up for a notifier service. S1 documents options; the owner acts.
- Runtime LLM calls or spend (D-16).
- Options automation (Phase 8). The interfaces have no option or short order types.
- Reopening any closed owner decision in RETRO.

## 3. Deliverables

| # | Deliverable | Path | Requirement ID | Proven by |
|---|---|---|---|---|
| D1 | Phase 2 inputs: baseline commit, Phase 1 inherits (B10 run 2 result, G2 findings, known issues, open questions) | `docs/phases/phase_2/inputs.md` | G-12, R-41 | each inherited item has a source line; baseline hash recorded |
| D2 | Scope memo: FR-27 to FR-30 dispositions, spine cut, owner choices with facts, costs and citations, owner decision column | `docs/phases/phase_2/scope_memo.md` | FR-27 to FR-30, NFR-5, INV-5 | every FR/NFR row says spine or deferred; owner column filled (O1) |
| D3 | E-1 remaining definitions and cited sector classification, with a no-price-data attestation | `docs/phases/phase_2/e1_definitions.md`, then `decisions.md` §2 | FR-31, R-17, R-18 | O2 decision recorded; attestation line |
| D4 | Alpaca and calendar facts for the spec, each cited with an access date or marked `unverified` | `docs/research/verification_log.md` §10 | FR-3, FR-18, FR-19, R-49, R-50, R-56 | row count matches S4's fact list; 0 rows without URL or `unverified` |
| D5 | Limits config schema and loss-limit definitions | `docs/spec/LIMITS_CONFIG.md` | INV-2, INV-11, FR-11, FR-12, D-01 to D-23 | G-3 checks |
| D6 | Owner-parameter worksheet | `docs/phases/phase_2/owner_parameters.md` | RETRO debt "Parameters still unset" | no blank owner cell (O4) |
| D7 | Interface contracts | `docs/spec/INTERFACES.md` | FR-3, FR-27, R-56, R-63, R-66, R-67, NFR-1 | G-4 checks |
| D8 | System spec | `docs/spec/SPEC.md` | spine rows in §2.2; NFR-1 to NFR-8 | G-1 checks |
| D9 | Tax model ("not CPA-reviewed") | `docs/spec/TAX_MODEL.md` | INV-12, FR-21 to FR-23, C-5 | G-6 checks |
| D10 | Report formats and check-in schema | `docs/spec/REPORTS.md`, `docs/checkins/README.md` | FR-24, FR-26, D-19 | G-7 checks |
| D11 | Hazard analysis (FMEA) and new failure proposals P-29 onward | `docs/spec/HAZARDS.md`, `docs/research/failure_library_proposals.md` | NFR-1, PRD §6 Phase 2 | G-2 checks; O6 decision column |
| D12 | Fault-injection catalogue (the Phase 3 gate suite) | `docs/spec/FAULT_INJECTION.md` | PRD §6 Phase 3 gate, R-47 to R-68 tests | G-5 checks |
| D13 | Traceability matrix | `docs/spec/TRACE.md` | all | G-8 checks |
| D14 | Engine install-check protocol and report; matrix amendment rows | `docs/phases/phase_2/engine_install_check.md`, `docs/research/decision_matrix.md` | PRD §5, RETRO 2026-11-25 engine row | G-9 checks |
| D15 | Records: PRD v0.5, `decisions.md` D-24 onward, approved P-29+ merged into FAILURE_LIBRARY, RETRO rows and debt closures | `docs/PRD.md`, `docs/phases/phase_0/decisions.md`, `docs/research/FAILURE_LIBRARY.md`, `docs/RETRO.md` | G-10 | dated rows; PRD header |
| D16 | Eval, summary, red-team review | `docs/phases/phase_2/phase_2_eval.md`, `phase_2_summary.md`, `phase_2_redteam.md` | G-11, G-12 | files exist with verdicts |

**What each spec file must contain** (so a run-phase session needs no questions):

- **LIMITS_CONFIG (S3):** one row per field: name, type, unit, domain, paper value, source (D-xx, owner, or agent-proposed with evidence), risk-up direction, who may change it and how (instant for risk-down; owner review plus 24 hours for risk-up). Loss-limit definitions: the day baseline (prior-close sleeve equity), the week baseline (equity at the week's first open), the peak (running high-water mark; whether and when it resets), realized vs unrealized, how deposits and withdrawals adjust the baselines, each with a worked example. Config signing: what is signed, who holds the key (never the bot), how the bot verifies, what a failed check does. Fields for every invariant-11 check and every configurable value in R-15, R-24, R-28, R-32, R-33, R-47, R-52, R-53, R-54, R-57, R-60, R-62, R-65, R-68 and C-1.
- **Owner worksheet (S3):** the RETRO "still unset" parameters, each with facts and trade-offs and no recommendation: risk-mode entry and exit thresholds outside the sleeve; the core-rebalance size above which approval is needed; the delay for a risk-up mode change. Then the agent-proposed operational values (staleness threshold, clock bound, `unknown` timeout, collar widths, liquidity floor, ADV cap, IPO age, order-rate ceilings, slippage model), each with its evidence (Phase 1 measurements, docs), for the owner to approve or amend.
- **INTERFACES (I1):** per layer: version string; typed signatures as Python-style pseudo-code inside the doc (no `.py` files); the boundary models with their required decision fields (R-63); declared domain errors (R-66); which side owns retries; the contract tests that run against both the real adapter and its fake. The egress layer's (scheme, host, path) allowlist and credential attachment (R-67). An order model that cannot express options, shorts, market orders or a time-in-force other than DAY, except a protective stop-limit with GTC (INV-13, INV-16, R-49, R-62). An order taxonomy (entry, exit, protective) that the watchdog uses so it can cancel entries only (INV-4). The LLM layer returns proposals only and has no route to the broker (INV-1, NFR-1). The backtest engine sits behind a `BacktestRunner` contract; the execution package may never import the engine package (guard test listed), and strategies are written once against our strategy contract (E-2 parity).
- **SPEC (SP1):** numbered clauses. State machines as transition tables: risk modes incl. UPGRADE (who may trigger each transition, delay, code), order lifecycle incl. `unknown`, approval request (created, approved, denied, expired at 15 minutes or at the close), session (closed, pre-open, no-trade window, open, halted). The kernel check order and every reason code. Startup and daily sequences. Reconciliation rules and tolerances. Ledger record types and the anchor procedure. Command grammar. Paging levels and the unacknowledged-alert rule (R-16). Core band check. Release rule (R-13, R-14, R-59). Secrets handling for the chosen host (NFR-3, R-21). The C-10 retention proposal. The spine cut as accepted at O1.
- **TAX_MODEL (T1):** as in G-6, plus the paper-period simplifications stated as such.
- **HAZARDS (H1):** method first (severity 1–4, where 4 = loss beyond a hard limit, core sold, live money touched, or a legal breach; likelihood 1–4; detection 1–4). Then rows from: each invariant, each F/R entry, each interface boundary, each state-machine transition, host and network faults, command spoofing, owner error, tax error, Phase 1 known issues (clean-tree scope, redaction order, staleness as gap not age, shared CIKs, positions and clock models ignoring unknown keys), and G2's findings. Each row: cause, effect, S/L/D, control (`SP-`), verification (`FI-` or test), residual risk. A "deferred control" column checks every §2.2 deferral.

## 4. Sequence

Parallel work uses **at most 2 agents at once** (owner instruction). Owner units can run at any time; they are batched into four sittings (A: O1–O3 after wave 1; B: O4 after S3; C: O5–O6 after E2 and H1; D: G2 and G4).

| # | Unit of work | Depends on | Parallel? | Owner | Check that ends it |
|---|---|---|---|---|---|
| S0 | Start check: Phase 1 G3 row in RETRO, this plan READY, four gates green, baseline commit recorded; collect Phase 1 inherits into D1 | Phase 1 G3; plan-review READY | no | agent | D1 lists every inherit with source; baseline hash recorded |
| S1 | Scope memo (D2): FR-27 to FR-30 dispositions; refine the §2.2 spine cut; owner choices with facts, costs vs D-15 and citations: (a) separate core and sleeve paper accounts (INV-5), (b) Phase 5 host (PC vs small cloud host), (c) notifier and command channel, (d) R-27 substitute, (e) the key-scope revisit RETRO asks for before Phase 3 | S0 | yes, with S4 | agent | every FR/NFR row says spine or deferred with must-exist-by |
| S4 | Alpaca and calendar facts (D4), docs only: order fields, `client_order_id` uniqueness and lookup, status enum, stop-limit, time-in-force and `extended_hours`, replace, the trade-updates stream, account configurations, rate limits, clock and calendar, trading-status and halt messages, corporate actions, fee activities | S0 | yes, with S1 | agent | every fact cited with access date or marked unverified |
| S2 | E-1 remaining definitions (D3): entry fill price and timing, size per entry and capital per arm, overlapping entries, re-entry, gap fills on stops and targets, close vs intraday checks, ATR method, dividends and splits (incl. GOOG 2014), cost model, how losses offset in the tax figure, positions open at window end, the forward-run start; cited sector classification (for example SEC SIC codes) for AAPL, MSFT, XOM, WMT, GOOG, JNJ. No price data viewed | S0 | yes, with E1 | agent | each open item has a proposal; sectors cited; attestation written |
| E1 | Engine install-check protocol (D14 §1): candidates in matrix base order; the matrix §9.5 checks re-scoped to backtest-only use (engine unreachable from execution, order-capable modules on disk, Windows 11, Python version, `mypy --strict` at the boundary, deterministic replay, point-in-time and corporate actions with free data); isolated venv `.venv-engine-<name>/` added to `.gitignore`; synthetic data only; no `.env` in that venv; time box; uninstall steps; one approval line per engine | S0 | yes, with S2 | agent | protocol complete; approval lines blank for the owner |
| S3 | Limits config schema and loss-limit definitions (D5); owner worksheet (D6) | S1, S4 | no | agent | every D-01..D-23 mapped; every field has domain and direction |
| O1 | Decide FR-27 to FR-30, the spine cut and S1's owner choices; record the key-scope revisit | S1 | owner sitting A | owner | owner column of D2 filled; RETRO rows dated |
| O2 | E-1: choose the third name; approve or amend the open definitions | S2 | owner sitting A | owner | decisions.md §2 frozen; RETRO row |
| O3 | Approve or decline each engine install, in writing | E1, O2 | owner sitting A | owner | dated approval line per engine in D14 |
| O4 | Fill the owner worksheet; approve or amend agent-proposed values | S3 | owner sitting B | owner | no blank owner cell; RETRO debt row closed |
| I1 | Interface contracts (D7) | S1, S4, O1 | yes, with T1 or E2 | agent | each layer versioned, errors declared, contract tests listed |
| T1 | Tax model (D9) | S3 | yes, with I1 | agent | formula, cited rules, worked examples, label present |
| E2 | Run the install-check for each approved engine; record results and command output; matrix amendment rows; propose the engine choice and a fallback | O3 | yes, with any one agent unit | agent | each check pass or fail with output; lock files unchanged |
| SP1 | System spec (D8) | I1, S3, O1 | yes, with R1 | agent | every spine requirement has a clause with acceptance criterion |
| R1 | Reports and check-in schema (D10) | O1 | yes, with SP1 | agent | four formats, schema, two-minute budgets present |
| H1 | Hazard analysis (D11); new patterns written as P-29 onward | SP1, I1, T1, R1, S0 (G2 inherits) | no | agent | every INV, R-13..R-68, C-1..C-12 row has control and verification |
| O5 | Record the engine choice (or "none yet" and the fallback) in RETRO | E2 | owner sitting C | owner | dated RETRO engine row |
| O6 | Approve or reject each P-29+ proposal | H1 | owner sitting C | owner | no proposal left `proposed` |
| H2 | Fault-injection catalogue (D12) | H1 | no | agent | every severity 3–4 hazard has an FI with reason code |
| TR1 | Traceability (D13); run `failure-check` on the spec set | H2 | no | agent | no blank trace cell; failure-check 0 missing |
| P1 | Records (D15): PRD v0.5, decisions.md D-24 onward, merge approved P-29+, RETRO debt closures | O1, O2, O4, O5, O6, TR1 | no | agent | PRD v0.5; debt rows closed with links |
| G1 | phase-gate with `failure-check` on the delivered spec | P1, E2 | no | agent | eval completion section and summary; ADVANCE or HOLD |
| G2 | Graded design review: `red-team` in a fresh session with the G-11 rubric | G1 | no | owner | redteam file with scores and go/no-go |
| G3 | Resolve G2 findings in the spec; each finding closed or owner-accepted | G2 | no | agent | no open critical or high finding |
| G4 | Owner sign-off row in RETRO | G3 | no | owner | dated RETRO sign-off row |
| O7 | Optional, non-blocking: settle whether an Alpaca GTC stop-limit elects outside regular hours, by a hand-placed paper test or a written Alpaca support answer | S4 | any time | owner | verification_log §8 updated, or the spec keeps the worst case |

**Critical path:** S0 → S1 → O1 → I1 → SP1 → H1 → H2 → TR1 → P1 → G1 → G2 → G3 → G4. The engine path (S0 → S2 → O2 → E1/O3 → E2 → O5) runs beside it and joins at P1 and G1. **26 units: 17 agent, 9 owner.**

**Run-phase notes.** Each agent unit commits locally with its ID in the message; no unit pushes. Spec files are written fresh from this plan and the PRD; `family_desk_spike` is cited as evidence, never as a design to copy (R-43).

## 5. Failure modes and edge cases

### 5.1 Failures in doing Phase 2 itself

| Failure | Library entry | Control in this plan |
|---|---|---|
| The spec quietly drops a rule, so Phase 3 never builds it | F-21 (silence read as fine), all R-xx | G-2 loops over every R, INV and C ID; `failure-check` on the spec in TR1 and G1 |
| A spine item is deferred although a severe hazard depends on it | F-01 (missing control), F-28 | H1's deferred-control column; deferral only if no severity 3–4 hazard relies on it before its phase |
| The engine install pulls order-capable code into an importable path, or touches the repo venv or lock files | F-22, R-43, R-14, F-23, R-44 | Isolated git-ignored venv; never on `PYTHONPATH` for `src/`; no `.env`; lock-file diff check (G-9); per-engine owner approval |
| The install-check shows E-1 prices, contaminating the pre-registration or the 2025+ holdout | F-02, R-17, R-18, F-38, R-59 | E2 depends on O2 (selection frozen first); synthetic data only; no E-1 symbols or windows |
| Spec facts about Alpaca or tax law are wrong | F-35, R-56, F-45, F-18 | S4 and T1 cite primary sources with access dates or mark `unverified`; Phase 3 runs paper contract tests (R-56) |
| The agent invents a hard-limit number, or sets one to chase the $1M goal | Rule 2, R-38, decisions.md §3 | Owner-only fields carry trade-offs, no recommendation; agent-proposed operational values are marked `proposed` until O4 |
| Loss limits are ambiguous and get read the loose way under stress | F-16, R-38 | S3 fixes baselines, peak and reset with worked examples (G-3) |
| A clause can't be tested, so Phase 3 "looks done" | rule 10 | Every clause has an acceptance criterion (G-1); G-11 dimension 2 |
| Review evidence says a check works when a different check fired | F-25, R-46 | Every FI names the exact reason code it proves (G-5) |
| A review finding from Phase 1 G2 is lost between phases | F-21 | S0 collects G2 findings into D1; H1 must cite each one |

### 5.2 Failures the spec must design against (H1 turns each into rows)

| Group | Entries and rules | Spec home |
|---|---|---|
| Deploy and release | F-01 (R-13 to R-16), F-22 (R-43), F-38 (R-59) | SPEC release rule, preflight, self-halt, paging |
| Keys, egress, dependencies | F-04 (R-21, R-22), F-23 (R-44), F-46 (R-67), F-35 (R-56) | INTERFACES egress; SPEC secrets; LIMITS_CONFIG allowlist and floor |
| Broker unavailable, ambiguous or wrong | F-05 (R-23), F-26 (R-47), F-27 (R-48), F-30 (R-51), F-32 (R-53), F-34 (R-55), F-36 (R-57), F-42 (R-63), F-45 (R-66) | Order lifecycle, reconciliation, request budget, boundary models |
| Market events and stops | F-06 (R-24), F-07 (R-25 to R-27), F-28 (R-49), F-41 (R-62), F-37 (R-58) | Kernel, protective-stop rules, session machine, domains |
| Data and time | F-29 (R-50), F-31 (R-52), F-43 (R-64), F-44 (R-65), F-47 (R-68), F-21 (R-42), F-24 (R-45), F-20 (R-41) | Calendar, staleness, supervisor, clock check, keep-awake, ledger anchors |
| Strategy and model | F-02, F-03 (R-17 to R-20), F-08 (R-28 to R-30), F-09 (R-31), F-12, F-13 (R-34, R-35), F-33 (R-54), F-39 (R-60), F-40 (R-61) | Strategy contract, forward ledger, cost re-score, kernel trade caps; most strategy rules land in Phase 4 |
| Leverage, instruments, custody | F-10 (R-32), F-11 (R-33), F-17 (R-39) | Kernel blocklist, no margin or shorts asserted, broker choice rule |
| Behaviour | F-14 (R-36), F-15 (R-37), F-16 (R-38) | Exit rules carried at entry, cooling-off, post-mortem rule |
| Tax and compliance | F-18 (rule 12), F-19 (R-40) | TAX_MODEL, restricted list |

**Edge cases the spec must state explicitly:** an approval that expires at 15 minutes or at the close, whichever is first (D-22); a partial fill when the kernel limit is hit mid-fill; a protective-stop re-place while another order on the symbol is `unknown` (still blocked: RETRO, R-47 kept as written); deposits or withdrawals moving the loss baselines; a broker paper balance different from $35k (D-02 scaling); a half-day close (Fri 27 Nov is one) inside the last-5-minutes rule; both DST changes; a symbol halted with a resting stop; host suspend during the session; a manual options-track entry pushing the sleeve over D-11 or D-12.

## 6. Compliance items touched

| ID | How Phase 2 carries it |
|---|---|
| C-1 | Kernel opposite-side window across household accounts; no order without intent to fill; no trading in the last minutes (R-24); order-to-fill ratio in self-halt (R-15) |
| C-2 | Cash accounts only, margin off, asserted at startup; broker-specific rules in the broker config |
| C-3 | Restricted list in signed config, blocked in the kernel; starts empty, owner-maintained |
| C-4 | Settled-cash check before every buy (T+1) |
| C-5 | TAX_MODEL: every sale reported, wash sales, estimated payments; household scope deferred to the Phase 6 gate with the restricted list as the interim control |
| C-6 | Official APIs only; our own thin client, no SDK, no scraping |
| C-7 | Rate limits in the request budget; personal use; no redistribution in reports; notifier messages carry no third-party content beyond links |
| C-8 | No short-sale path; `no_shorting` asserted |
| C-9 | Household-only accounts in config; no external users in the command allowlist |
| C-10 | Retention proposal (7 years, append-only, monthly statement archive) for owner approval at O4 |
| C-11 | No option order type in any automated contract; the manual track is ledger entry only |
| C-12 | Out of scope; noted in TRACE |

## 7. What depends on the Phase 1 hold (B10 run 2, G2, G3)

| Phase 2 item | Depends on | Why |
|---|---|---|
| Every unit (S0 first) | G3 sign-off row | CLAUDE.md: never start the next phase without it |
| E1, E2, O3, O5 | G3 row confirming the engine decision | RETRO 2026-11-25: "to be confirmed in the G3 sign-off row"; any install needs explicit approval |
| S4 and I1 company-event and news contracts | B10 run 2 | EDGAR DE-4 and DE-5 re-score (and the A8 totals if they move); proof that the `"*"` news stream works on the free plan in a full run |
| S3 proposed values for staleness (R-52), clock bound (R-65), loop lag (R-68) | B10 run 2 | Quote inter-arrival and clock offset after the owner's clock fix are the evidence for those values |
| H1 hazard rows | G2 findings and any P-xx from run 2 | The FMEA must include them (S0 collects them) |
| Owner's new paper account at $35k, if chosen | B10 run 2 finished | decisions.md §4 timing; affects keys and config in Phase 3, not Phase 2 documents |

Nothing else in Phase 2 depends on Phase 1 output beyond what is already committed.

## 8. Risks, assumptions, "Do not"

### Risks
| # | Risk | Mitigation |
|---|---|---|
| RK1 | Spec scope grows and Phase 5 slips | The spine cut (§2.2) and the deferral rule; G-11 dimension 8 scores the spine's size |
| RK2 | No engine passes the install-check | E2 proposes a fallback (matrix robustness rank: custom on vectorbt, or our own minimal backtester on the strategy contract); Phase 3 does not depend on the engine |
| RK3 | Nine owner units stall the critical path | Four batched sittings; O7 optional; agent units continue around owner units where dependencies allow |
| RK4 | A document-only spec is wrong in ways only code shows | Contract tests against real adapters offline (R-66) and paper contract tests in Phase 3 (R-56); spec changes after sign-off go through owner review when they touch the kernel, limits or modes |
| RK5 | No strategy passes Phase 4, so Phase 5 trades only the core and baselines | The spine is still exercised by core rebalancing and pre-registered baselines; stated now so Phase 5's scorecard reads honestly |
| RK6 | The tax model is wrong | "Not CPA-reviewed" label; CPA sign-off before the Phase 6 gate (RETRO) |

### Assumptions
| # | Assumption | Status |
|---|---|---|
| AS-1 | Phase 1 signs off at G3 without findings that change Phase 2's scope | unverified |
| AS-2 | Alpaca lets the owner create more paper accounts (for core vs sleeve, and options) | verified: Alpaca paper-trading docs, accessed 2026-11-25 (`decisions.md` §4) |
| AS-3 | Alpaca offers no read-only key, so automation keys are trade-capable | verified: decision_matrix A7 |
| AS-4 | Free IEX stays the paper price feed | verified: decision_matrix 9.6 (paper-only account) |
| AS-5 | vectorbt's base install contains no broker SDK; NautilusTrader needs Python 3.13+ while the repo pins 3.12 | verified from documentation only (matrix §6); not installed |
| AS-6 | An Alpaca GTC stop-limit can elect on an extended-hours print | unverified; the spec assumes it can (R-49) until O7 settles it |
| AS-7 | No documented free iNAV source exists for SPY, QQQ, IWM | verified as "none documented" (matrix §8.1); the substitute is an O1 choice |
| AS-8 | A notifier and a Phase 5 host fit inside $0–25/month | unverified until S1 prices the options |
| AS-9 | No runtime LLM spend during the paper phases | verified: owner decision D-16 |

### Needing the owner during Phase 2 (all listed above as units)
O1 dispositions and choices (accounts, host, notifier, R-27 substitute, key scope); O2 E-1 third name and definitions; O3 engine install approvals; O4 the unset parameters (risk-mode thresholds outside the sleeve, core-rebalance approval size, risk-up mode delay) and the agent-proposed values; O5 engine choice; O6 new failure proposals; G2 review; G4 sign-off; O7 optional GTC test.

### Do not
- Start any unit before the Phase 1 G3 sign-off row exists and this plan is READY.
- Write or change code in `src/` or `tests/`, or change `pyproject.toml` or the lock files.
- Import or call any order-placing endpoint, or place, cancel or replace any order by code or agent, paper included (CLAUDE.md hard stop before the Phase 3 gate).
- Use live (non-paper) keys or endpoints, ever.
- Push, create remotes, change GitHub settings, create cloud resources, sign up for paid or free third-party services, or spend money. S1 documents options; the owner acts.
- Install any package without the owner's written per-engine approval; install only into the git-ignored engine venv; never load `.env` there.
- Read or print secrets. `.env` is read only by code, and Phase 2 runs none that reads it.
- Change hard limits, risk modes or kernel rules without the owner reviewing the diff. LIMITS_CONFIG and the kernel and mode clauses of SPEC are owner-reviewed at O4 and G4, and again on any later change.
- View price data for any E-1 symbol or window before O2, or any 2025-onward data for E-1 at any time (R-18 holdout).
- Use HSS repositories, skills (including `samd-design-review`), accounts or credentials. The graded review uses this repo's `red-team` skill.
- Copy `family_desk_spike` code into the design, or plan for Phase 3 to import it (R-43).
- Reopen closed owner decisions in RETRO or list them as risks.
- Run more than 2 agents at once.
