# Phase 1 eval

## Plan review, 2026-11-24

Reviewed: `docs/phases/phase_1/phase_1_plan.md` (and `phase_1_tasks.md`) against `docs/PRD.md` v0.1, `docs/RETRO.md`, `docs/MASTER_BRIEF.md`, `docs/COMPLIANCE.md`, `docs/research/FAILURE_LIBRARY.md`, `docs/HANDOFF.md` "Phase 1 definition", and `CLAUDE.md`.

**Verdict: FIX FIRST.** Critical coverage is 78.6% (it must be 100%) and overall coverage is 83.3% (it must be at least 85%). No applicable failure-check row is `missing`. Everything needed is a small edit; the plan does not have to be rewritten.

### 1. Coverage table

This table includes the PRD requirements in scope for Phase 1. It also includes the binding RETRO, HANDOFF and CLAUDE.md items that the phase must satisfy, and labels each one with its source. Requirements the plan defers explicitly and correctly are left out of the score: FR-1/2, FR-4/5, FR-7, FR-9, FR-11–26, the NFR-3 secrets manager and NFR-8.

| # | Requirement | Severity | Coverage | Evidence (plan section) | Gap |
|---|---|---|---|---|---|
| 1 | PRD §6 Phase 1 gate: decision matrix reviewed (plan-evaluation + independent review), owner sign-off | critical | full | §1 G-1, G-11; §4 G1–G3 | none |
| 2 | PRD §5 / §6: execution/backtest engine **chosen** in Phase 1 | critical | partial | D6, A5–A8 | G-1 passes no matter how many cells are `unverified`, so the recommendation could rest mostly on unverified scores. Windows fit is checked "by reading docs only". Nothing requires the winner to hold up once unverified cells are assumed bad |
| 3 | NFR-1 / inv. 1 / CLAUDE.md hard stop: no route to an order | critical | full | §1 G-7; D8, D12; B2; §5 row 1; Do-not | Minor inconsistency, see the detail gaps: B2 limits the non-GET scan to "the broker module", while G-7 says all of `src/`. No runtime test shows the allowlisted client refusing `/v2/orders` |
| 4 | NFR-3 / inv. 17: paper endpoint asserted at startup | critical | full | G-8; D9; B3 (wrong host, live host, missing flag all refuse); B10 refusal demo | none |
| 5 | CLAUDE.md hard stop / NFR-3: secrets never read out, printed or committed | critical | partial | G-10; D9 masked types; D10 redaction; B11 scan; Do-not | The G-10 scan searches for "the key's first 6 characters". It does not say which key, and it does not scan the full values of **both** `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY`. The scanning script has no deliverable or test, and `tests/test_redaction.py` appears in G-10 but not in §3 |
| 6 | CLAUDE.md "never start the next phase without a recorded owner sign-off in RETRO"; PRD §6 Phase 0 gate | critical | partial | §4 note under O5 | RETRO has no Phase 0 sign-off and no recorded waiver. The plan makes O3–O5 non-blocking on the strength of HANDOFF, but that decision is not in RETRO's closed-decisions table |
| 7 | RETRO debt: regenerate Alpaca paper keys before the spike | critical | full | O1 blocks B10; §5 row 4 | none |
| 8 | COMPLIANCE C-3 / R-40: restricted list | important | full | O2 blocks B10; §6 | none |
| 9 | FR-3: broker adapters behind one interface; live-broker candidates compared | important | full | D12 `ReadOnlyBroker` Protocol; D6 broker ranking; non-goal keeps the live choice open (RETRO) | none |
| 10 | PRD §6 Phase 1 goal: "engine/broker/**data** choice" | important | partial | D3 (terms verified only) | The matrix scores engines and brokers but not the data source. Free IEX quotes versus SIP, news-feed alternatives and iNAV availability (R-27) are never compared, and Phase 3 collars and the liquidity floor depend on that answer |
| 11 | FR-6: strategy evidence re-verified (prerequisite for Phase 4) | important | full | D5, A3, G-3 | none |
| 12 | FR-8: news and filings ingestion for watched symbols | important | partial | D13–D15, G-9 | Live proof can pass vacuously. G-9 accepts a "no news" heartbeat and "≥1 EDGAR poll cycle", and AAPL/MSFT 8-Ks are rare enough that a 35-minute window will almost certainly contain no matching filing. The CIK filter and the news subscription are therefore never shown working on a real positive case |
| 13 | FR-10: data-staleness monitoring | important | full | D13 per-symbol staleness and stall detection; §5 | none for this phase |
| 14 | NFR-4: outages and disconnects handled, never silent | important | full | B6–B8 backoff, connection-limit handling, stall detection; §5 | Windows Ctrl+C is a detail gap (see §4) |
| 15 | NFR-6 / C-10: append-only, reproducible log | important | partial | D10, B4, G-9 | The hash chain has no external anchor. Anyone can rewrite the file and recompute the chain, and dropping the last N records leaves a valid chain, so the "truncation detection" test in D10 cannot catch tail truncation. Nothing records the final `seq` and hash anywhere outside the log |
| 16 | NFR-7 / C-7: data terms and rate limits | important | full | A2, D15 token bucket with a 1,000-poll proof, UA required, metadata-only news storage, §6 | The polling cadence is a detail gap (see §4) |
| 17 | C-6: official APIs only, no scraping | important | full | §6; Do-not | none |
| 18 | NFR-3 / rule 11: pinned, hashed dependencies | important | full | D7 `--require-hashes`; B2 scans the lock file | none |
| 19 | R-13 / inv. 17: version + config-hash self-check; refuse if not the approved release | important | partial | D9, B3 | `config/spike.toml.sha256` is committed beside the file it hashes, so it catches drift but not a deliberate edit. The version is printed but never compared with anything |
| 20 | HANDOFF Track A: resolve every `[verify]` in `docs/research/*.md` | important | partial | D1, D2, D3, A1, A2, G-2 | **The count is wrong.** The repo has 11 markers (7 in FAILURE_LIBRARY, 4 in NEWS_AND_DATA_STACK); G-2 and D1 say 12. **The grep is wrong.** `\[verify\]` misses F-15's `[verify: Barber & Odean]` and still matches the explanatory text on FAILURE_LIBRARY lines 3 and 97, so G-2 cannot pass as written and could also pass falsely. Weak sources on entries without `[verify]` are only "listed", never fixed: the F-14 SSRN link is visibly truncated, and the NEWS_AND_DATA_STACK citation for the EDGAR Atom feed is a dev.to post |
| 21 | HANDOFF Track A: extend FAILURE_LIBRARY with post-mortems and broker-API incidents | important | full | D4, A4, O6, A9, G-4 | none |
| 22 | RETRO debt: re-verify Alpaca free-tier news terms | important | full | A2, G-5, D3 | none |
| 23 | MASTER_BRIEF working rules: check alternatives, use a skeptic's framing, cite or say `unverified` | important | full | A5 freezes weights before scoring; A8 ±50% sensitivity and dissent; §5 anti-anchoring row | none |
| 24 | Rule 6 / inv. 6: external text is data | important | full | B7, D14, defusedxml, field size caps, no LLM calls, §5 | none |
| 25 | CLAUDE.md engineering stance and quality gates (fakes over mocks, tests, gates defined in Phase 1) | important | full | D7, D17, G-6; guard forbids `unittest.mock` | none |
| 26 | NFR-5: cost under budget | detail | full | Do-not: no paid services, no new accounts | none |
| 27 | Deferred items recorded as debt (C-10 7-year retention, NFR-3 secrets manager) | detail | partial | §2 non-goals, §6 C-10 "noted as debt" | No task writes these rows into RETRO "Known debt" |
| 28 | C-1, C-2, C-4, C-8, C-11 recorded as broker facts | detail | full | §6; A7 | none |
| 29 | HANDOFF owner rows (decisions table, statements, CPA) tracked | detail | full | O3–O5 | Blocking status depends on row 6 |
| 30 | Live-run timing (inv. 14 / R-24 analogue) | detail | partial | B10, §5 market-closed row | The runner only checks that the market is open. It does not check that the 35-minute run ends before `next_close` − 5 min, so a half-day (e.g. 27 Nov 2026, close at 13:00 ET) or a late start breaks the window |

### 2. Failure check

Nothing has been built yet, so "tested?" shows the planned test, or `no` where none is planned.

| Entry | Rule | Applies? | Control present? | Tested? | Evidence |
|---|---|---|---|---|---|
| F-01 Knight | R-13 deploy/version/config-hash check | yes | partial | planned: `tests/test_startup.py` | D9, B3. The hash file sits beside its config, and the version is never compared (row 19) |
| F-01 | R-14 no dead code / repurposed flags | yes | partial | no | The plan never says whether the spike code is thrown away or becomes the base for Phase 3. `--allow-closed` is a bypass flag that could carry into Phase 3 |
| F-01 | R-15 self-halt on aberrant behaviour | partly: no orders, but there is a request-rate analogue | yes (analogue) | planned: `tests/test_ratelimit.py`, `tests/test_iex_stream.py` | B8 token bucket; B6 capped backoff, "never hot-loop reconnect" |
| F-01 | R-16 page a human | no: there is no alert channel until Phase 3 | n/a | n/a | §5 "Not applicable" |
| F-02 Quantopian | R-17/18/19 | no for code (no backtests); research only | n/a | n/a | A3 records out-of-sample results and decay |
| F-03 decay | R-20 | yes (research) | yes | gate count G-3 | D5 records publication year |
| F-04 3Commas | R-21 keys in our own store, 90-day rotation, IP allowlist | yes | partial | planned: `tests/test_config.py`, redaction tests | O1 regenerates the keys. There is no rotation date or reminder. IP allowlist is only a matrix criterion (A5). The paper key can trade, so nothing at the broker side enforces read-only |
| F-04 | R-22 allowlist/liquidity floor in the kernel | no: no kernel, no orders | n/a (the GET path allowlist is the analogue) | planned: `tests/test_alpaca_readonly.py` | D12 |
| F-05 broker outages | R-23 | yes | yes (for read-only scope) | planned: `tests/test_iex_stream.py`, `tests/test_news_stream.py`, `tests/test_edgar.py` | B6–B8; §5 rows 6–8 |
| F-06 Flash Crash | R-24 session-edge rule | yes (run window) | partial | no | B10 window 10:00–15:30 ET; no check that the run ends before the close (row 30) |
| F-07 24 Aug 2015 | R-25/26/27 | no orders; R-26 stop-limit support is an A7 criterion | n/a (A7 records the facts) | n/a | A7; the iNAV data question for R-27 is missing from the matrix (row 10) |
| F-08 LLM contests | R-28/29/30 | no: no LLM in code, no orders | n/a | n/a | Non-goals |
| F-09 look-ahead | R-31 | yes (research) | yes | n/a (document review) | §5 "LLM backtest results never count" |
| F-10 leverage | R-32 | no | n/a | n/a | A1 verifies the entry |
| F-11 Volmageddon | R-33 | no | n/a | n/a | A1 verifies the entry |
| F-12 momentum crash | R-34 | no | n/a | n/a | A1 verifies the entry |
| F-13 regime | R-35 | no | n/a | n/a | No strategies |
| F-14/15/16 behavioural | R-36/37/38 | no | n/a | n/a | No trading, no rule changes |
| F-17 custody | R-39 | yes (broker scoring) | yes | n/a | A5 "SIPC/regulation" criterion |
| F-18 tax | R-12 | no (only cost-basis export as a broker criterion) | n/a | n/a | A7 |
| F-19 MNPI/conflicts | R-40 | yes | yes | owner check O2 | O2 blocks B10 |

No applicable row is `missing`.

**Proposed new failure entries.** These are for the owner to approve. They are not added to the library.

- **Proposed F-xx: an unanchored audit trail.** A hash chain that is verified only against itself can be rewritten end to end or cut short at the tail and still verify. *Proposed rule:* each log's final `seq` and head hash is recorded somewhere independent, such as committed evidence or the daily owner digest. The verifier takes the expected head as an input and fails on any mismatch.
- **Proposed F-xx: vacuous liveness ("silent equals fine").** A monitoring path that is broken (wrong subscription, filter that never matches, CIK zero-padding mismatch) produces the same "nothing happened" output as a healthy, quiet one. *Proposed rule:* every data path must prove it is alive on a known positive before its silence counts as evidence. Examples: a logged subscription ack, an unfiltered sample count, or a read-only REST cross-check.
- **Proposed F-xx: spike code promoted to production.** Prototype code, including its bypass flags, ends up in the production path without design review, much like Knight's Power Peg. *Proposed rule:* spike code lives in a quarantined package. Phase 3 may import from it only after a spec and review, and bypass flags such as `--allow-closed` are removed before Phase 3.
- **Proposed F-xx: a trade-capable key doing read-only work.** Read-only intent is enforced only by our own code, because the key itself can trade. *Proposed rule:* use a read-only or least-privilege key wherever the broker offers one. Where it doesn't, record this as accepted risk in RETRO and keep code guards on both code and dependencies.

### 3. Scores

Formula: score = (full + 0.5 × partial) / total × 100.

| Severity | Rows | Full | Partial | Missing | Arithmetic | Score |
|---|---|---|---|---|---|---|
| Critical | 7 | 4 | 3 | 0 | (4 + 0.5 × 3) / 7 = 5.5 / 7 | **78.6%** |
| Important | 18 | 13 | 5 | 0 | (13 + 0.5 × 5) / 18 = 15.5 / 18 | **86.1%** |
| Detail | 5 | 3 | 2 | 0 | (3 + 0.5 × 2) / 5 = 4 / 5 | **80.0%** |
| Overall | 30 | 20 | 10 | 0 | (20 + 0.5 × 10) / 30 = 25 / 30 | **83.3%** |

### 4. Top five gaps (critical first)

1. **Phase 0 has no recorded sign-off or waiver (row 6, critical).** CLAUDE.md forbids starting a phase without an owner sign-off row in RETRO, and RETRO still lists the Phase 0 items as open debt. *Fix:* the owner adds one RETRO row. It can either close Phase 0 with the decisions table, statements and CPA carried as debt, or record a decision that this Phase 0 homework runs alongside Phase 1 and must be finished before the Phase 2 gate.
2. **The secret scan checks the wrong thing (row 5, critical).** A 6-character prefix of an unnamed key does not show that the secret key never leaked. *Fix:* G-10 should scan the full values of `APCA_API_KEY_ID` **and** `APCA_API_SECRET_KEY`, and treat the `SEC_USER_AGENT` contact as personal data. It should cover `git log -p --all`, `logs/`, `docs/`, and pytest output captured with `-rA`. The scanner gets its own deliverable (for example `src/family_desk/tools/secret_scan.py`) and a test that uses a planted fake value. Add `tests/test_redaction.py` to §3.
3. **The engine choice has no evidence threshold (row 2, critical).** *Fix:* add to G-1 that the recommendation must not change when every `unverified` cell is set to its worst plausible score, and report the unverified share per candidate. Then either install and run a hello-world for the top engine in a git-ignored venv inside the repo (outside `src/` and the lock files, so the guard does not apply), or label the engine choice "provisional, install-confirmed in Phase 2" and have the owner accept that label at G3.
4. **The live data-path proof can pass vacuously (row 12, important).** *Fix:* G-9 should also require three things. First, a logged subscription ack for the quotes and news streams. Second, the count of parsed EDGAR Atom entries **before** the watchlist filter (expected > 0), plus a unit test that matches a real feed CIK in 10-digit zero-padded form to `company_tickers.json`'s integer `cik_str`. Third, if the stream is quiet, a read-only REST news history GET for the watchlist, with its host and path added to the D12 allowlist, so that real payloads are parsed at least once.
5. **The hash chain has no anchor (row 15, important).** *Fix:* `verify_log` prints `seq_last` and `head_hash`, and D18 records them. The verifier accepts `--expect-head`. D10's test list should replace "truncation detection" with "mid-file gap detection", and tail truncation should be stated as detectable only against the anchor.

**Remaining gaps, all small:**
- Fix the `[verify]` count to 11 and the G-2 pattern to `\[verify` (it must also catch `[verify:`). Reword FAILURE_LIBRARY lines 3 and 97. Fix links found dead, not just list them, starting with F-14 SSRN. Replace the dev.to citation for the EDGAR feed with an SEC page.
- Add a data-source section to the matrix: IEX versus SIP (including delayed SIP on the free plan), news alternatives and iNAV. Have the spike log quote update rate and spread per symbol as input to it.
- Make B2 match G-7: block non-GET verbs to the trading host anywhere in `src/`. Add a runtime test that the D12 client refuses `/v2/orders` and every non-GET verb. Exclude `tests/fixtures` from the literal scan, or allowlist it, so that test can exist.
- R-13: state that the config hash detects drift, not tampering, until Phase 3 signing exists, and compare the version with a tagged commit or the `pyproject` version.
- State the spike code's fate (throwaway or quarantined) and remove `--allow-closed` before Phase 3.
- Windows shutdown: `asyncio` `add_signal_handler` does not work on Windows. Specify `KeyboardInterrupt` handling and add a test that drives the runner's shutdown path.
- Run window: refuse to start unless now + duration ≤ `next_close` − 5 min, as reported by `/v2/clock`.
- EDGAR cadence: set a poll interval (for example 30–60 s) separate from the 1 req/s ceiling. At the ceiling, 35 minutes is about 2,100 requests for no benefit.
- Add a task to write the deferred-debt rows (C-10 retention, secrets manager, key rotation date) into RETRO.

### 5. Narrative

**Posture.** This is a careful, safety-first plan with a real, testable gate. The read-only boundary is enforced three ways: no trading SDK, a GET-only client with a path allowlist, and a guard over both code and lock files. Owner rows block where they should, and the Do-not list matches CLAUDE.md. Its weakness is the quality of its proof, not its design.

**Strengths.**
- Every deliverable traces to a requirement ID.
- Decision weights are frozen before scoring, with a ±50% sensitivity check and a written dissent. That is a sound defence against anchoring.
- The assumptions table states its verification status honestly.
- Fakes are everywhere, and the guard rules out `unittest.mock`.
- EDGAR is held to 1 req/s and proven over 1,000 simulated polls.
- Evidence files contain counts only, never content.
- The guard has to be shown failing on a planted violation before anyone trusts it passing.

**Weaknesses (the pattern).** Several gate checks pass without proving their claim:
- G-1 passes with any share of `unverified` cells.
- G-2's grep has the wrong pattern and count.
- G-9 accepts silence, a filter that never matches, and a self-verified chain.
- G-10 scans a prefix of one key.
- R-13's hash file vouches for itself.

The process gap has the same shape. The owner's choice to run Phase 0 alongside Phase 1 is clear from HANDOFF, but it is not recorded where the rules say it must be.

**Most likely failure if run as written.** The EDGAR path is "proven" with zero real matches. The Atom feed gives 10-digit zero-padded CIKs, while `company_tickers.json` gives integers, so a padding mismatch would make the watchlist filter match nothing. On a 35-minute window with no AAPL/MSFT 8-K, that result looks exactly like a correct one. G-9 then passes on "≥1 poll cycle", and `verify_log` prints `chain OK`. Phase 3 would be built on a filings path that has never matched a real filing. The news stream carries the same risk through the heartbeat clause.

**Kind of remediation needed.** Small, targeted edits to the gate criteria and about six tasks, plus one RETRO row from the owner. No re-scoping, no new deliverables beyond the secret scanner, and no change to the sequence. After the five top gaps are fixed, rows 2, 5, 6, 12 and 15 move to full. That brings critical to 100% and overall to about 91.7% ((25 + 0.5 × 5) / 30), so a re-review should return READY.

## Plan re-review (revision 2), 2026-11-25

Reviewed: `docs/phases/phase_1/phase_1_plan.md` revision 2 (and `phase_1_tasks.md`) against `docs/PRD.md` v0.2, `docs/RETRO.md` (now with the Phase 0 sign-off and the owner corrections of 2026-11-24), `docs/MASTER_BRIEF.md`, `docs/COMPLIANCE.md`, `docs/research/FAILURE_LIBRARY.md`, `docs/HANDOFF.md` (with its supersession note), `CLAUDE.md` and `.claude/rules/trading-invariants.md`.

Plan claims checked against the repo: there are 11 `[verify` markers (7 in FAILURE_LIBRARY, 4 in NEWS_AND_DATA_STACK). The explanatory mentions are on FAILURE_LIBRARY lines 3 and 97. `.gitattributes` pins `eol=lf`, so config hashes are stable on Windows. A `pre-push` hook is present. The `.env` variable names in TONIGHT.md step 7 match the four that B3 reads. All commit author emails are noreply addresses, so the G-10 history scan will not trip on commit headers. There is no `src/`, `tests/` or `config/` yet, and pytest is not installed (AS-1).

**Verdict: READY.** Critical coverage is 100%, overall coverage is 92.9% (≥ 85%), and no applicable failure-check row is `missing`. Revision 2 closes all five top gaps from the first review and nearly all of the small ones. What remains are seam gaps between documents and process. Gap 1 below must be fixed before the phase makes its first commit. The other four can be folded into the first tasks.

### 1. Coverage table

Rows 1–30 keep the numbering of the first review so the two can be compared. Rows 31–35 are new findings. Requirements deferred correctly are again left out of the score: FR-1/2, FR-4/5, FR-7, FR-9, FR-11–26, the NFR-3 secrets manager and NFR-8.

| # | Requirement | Severity | Coverage | Evidence (plan section) | Gap |
|---|---|---|---|---|---|
| 1 | PRD §6 Phase 1 gate | critical | full | G-1, G-11; §4 G1–G3 | none |
| 2 | PRD §5: engine chosen in Phase 1 | critical | full | G-1 (unverified share, worst-case robustness, provisional label accepted at G3); D6; A5–A8; R6 | The plan doesn't say what happens if the robustness check blocks a recommendation (see small gaps) |
| 3 | NFR-1 / inv. 1 / hard stop: no route to an order | critical | full | G-7; D8 (code + locks, non-GET anywhere in `src/`); D12 runtime refusal before send; B2 | The EDGAR client (`www.sec.gov`) has no (host, path) allowlist and is covered only by the static scan (see small gaps) |
| 4 | NFR-3 / inv. 17: paper endpoint asserted | critical | full | G-8; D9; B3 refusal cases; B10 demo | The live wrong-host demo trips the config-hash check first (see small gaps) |
| 5 | Hard stop / NFR-3: secrets never read out, printed or committed | critical | full | G-10 full-value scan of both Alpaca secrets + the UA contact over history, files, logs, docs, pytest `-rA`; D20; `test_secret_scan.py`, `test_redaction.py` | G-10's wording ("personal value") is broader than what it checks (see small gaps) |
| 6 | No phase starts without an owner sign-off in RETRO | critical | full | RETRO row 2026-11-24 "Phase 0 signed off"; §4 note | none |
| 7 | RETRO debt: regenerate paper keys before the spike | critical | full | O1 blocks B10; A11 records the date | none |
| 8 | C-3 / R-40 / inv. 18: restricted list | important | full | §6 C-3; RETRO 2026-11-24 (list starts empty, owner-maintained) | none |
| 9 | FR-3: one broker interface; candidates compared | important | full | D12 `ReadOnlyBroker`; D6; non-goal keeps the live choice open | none |
| 10 | PRD §6: data choice | important | full | D6 data-source section (IEX, delayed SIP, paid SIP ranked only, news options, iNAV); A10 uses spike measurements | none |
| 11 | FR-6: strategy evidence re-verified | important | full | D5, A3, G-3 | none |
| 12 | FR-8: news and filings ingestion | important | full | G-9 subscription acks, REST news GET ≥ 1 item, EDGAR pre-filter count > 0; D15 CIK padding test | ETF-specific gap in row 32 |
| 13 | FR-10: data staleness | important | full | D13; B6 stall detection | none |
| 14 | NFR-4: outages and disconnects never silent | important | full | B6–B8; D16 Windows-safe shutdown tested in e2e | none |
| 15 | NFR-6 / C-10: append-only, reproducible log | important | full | D10 `seq_last`/`head_hash`/`--expect-head`; D18 anchor; G1 re-verifies | none |
| 16 | NFR-7 / C-7: data terms and rate limits | important | full | 60 s cadence under a ≤ 1 rps ceiling; A2; metadata-only news | none |
| 17 | C-6: official APIs only | important | full | §6; Do-not | none |
| 18 | NFR-3 / rule 11: pinned, hashed dependencies | important | full | D7; B2 scans the locks | none |
| 19 | R-13 / inv. 17: version + config self-check | important | full | G-8 (pyproject version, clean tree, commit hash; drift-only limit stated); A11 signing debt | The version check compares the package with its own pyproject. That is weak, but the limit is stated and the clean tree plus commit hash do the real binding |
| 20 | Resolve every `[verify]` | important | full | G-2 (11 markers, `\[verify` pattern, rewording, link fixes incl. F-14 and dev.to) | none |
| 21 | Extend FAILURE_LIBRARY | important | full | D4, A4, O6, A9 | See row 35 |
| 22 | Re-verify Alpaca free-tier terms | important | full | A2, G-5, D3 | none |
| 23 | MASTER_BRIEF working rules (alternatives, skeptic, cite) | important | full | A5 frozen weights + worst-case definitions; A8 robustness, sensitivity, dissent | none |
| 24 | Rule 6 / inv. 6: external text is data | important | full | B7, D14, defusedxml, field caps | none |
| 25 | Engineering stance (fakes, tests, gates) | important | full | D7, D17, G-6 | See row 31 |
| 26 | NFR-5: cost | detail | full | Do-not | none |
| 27 | Deferred items written as RETRO debt | detail | full | A11 / D21 | See row 34 |
| 28 | C-1/2/4/8/11 as broker facts | detail | full | §6; A7 | none |
| 29 | Owner rows tracked | detail | full | O1–O3; O4/O5 moved to RETRO debt | none |
| 30 | Run window (inv. 14 / R-24 analogue) | detail | full | G-9; D16; `test_run_window.py` (half-day) | none |
| 31 | CLAUDE.md: "`python -m pytest -q` must pass before any commit" | important | partial | A1/A2 "one commit per closed marker", with no dependency on B1 | A1 and A2 start on day one and commit per marker. pytest isn't installed until B1 (AS-1), and once it is, an empty suite exits with code 5. Every Track A commit made before B1 therefore breaks CLAUDE.md, or the agent stalls |
| 32 | FR-8 correctness: watchlist-to-CIK mapping for ETFs | important | partial | B8 (CIK map from `company_tickers.json`); §2 FR-8 row ("each proven on a real positive case") | Three of the five symbols (SPY, QQQ, IWM) are fund trusts, not operating companies. Fund trusts rarely or never file 8-Ks, may be missing from `company_tickers.json` (not checked in this review), or share one trust CIK across many funds. iShares Trust is the obvious case, so any iShares Trust 8-K would be logged as an IWM match. The plan doesn't define behaviour for missing or shared CIKs, and the §2 claim overstates EDGAR's proof, which is feed liveness plus a synthetic filter test |
| 33 | FR-3 / G-9: positions read proven on a real payload | detail | partial | G-9 "Recorded: … positions"; D11 fixtures | A paper account that nothing can trade holds no positions. The live read returns `[]`, so the Position parser never meets a real non-empty payload, and the evidence looks the same whether the parser is right or wrong |
| 34 | R-21 / first-review proposal: trade-capable key recorded as accepted risk | detail | partial | §5 row 2 "noted as accepted risk for the spike" | A11's list of RETRO rows doesn't include it, so the accepted risk lives only in the plan |
| 35 | FAILURE_LIBRARY growth from reviews | detail | partial | D4 sources: post-mortems, broker incidents, "spike-found patterns" | The four failure entries proposed in the first review (unanchored audit trail, vacuous liveness, spike code promoted, trade-capable key) drove half of revision 2. They are not routed into D4, so O6 never decides them and the library never learns them |

### 2. Failure check

Nothing is built yet. "Tested?" names the planned test.

| Entry | Rule | Applies? | Control present? | Tested? | Evidence |
|---|---|---|---|---|---|
| F-01 Knight | R-13 version/config self-check | yes | yes (drift-only, stated) | planned: `tests/test_startup.py` | G-8, D9, B3; A11 signing debt |
| F-01 | R-14 no dead code / bypass flags | yes | yes | planned: `tests/test_no_order_paths.py` (outside-import guard) | AS-14 throwaway package, no bypass flag, A11 deletion row |
| F-01 | R-15 self-halt on aberrant behaviour | analogue (request rate, reconnects) | yes (analogue) | planned: `tests/test_ratelimit.py`, `tests/test_iex_stream.py` | B6, B8 |
| F-01 | R-16 page a human | no: no alert channel until Phase 3 | n/a | n/a | §5 "Not applicable" |
| F-02 | R-17/18/19 | no for code (no backtests) | n/a | n/a | A3 out-of-sample notes |
| F-03 | R-20 | yes (research) | yes | G-3 count | D5 publication year |
| F-04 3Commas | R-21 keys, rotation, IP allowlist | yes | partial | planned: `test_config.py`, `test_redaction.py`, `test_secret_scan.py` | O1 + A11 rotation date; IP allowlist is a matrix criterion only; trade-capable key not recorded in RETRO (row 34); secrets manager is Phase 3 debt |
| F-04 | R-22 kernel allowlist/floor | no kernel; path allowlist is the analogue | analogue | planned: `tests/test_alpaca_readonly.py` | D12 (EDGAR client not covered, see small gaps) |
| F-05 | R-23 outages → halt, log | yes | yes | planned: stream and EDGAR tests | B6–B8, §5 |
| F-06 | R-24 session edges | yes (run window) | yes | planned: `tests/test_run_window.py` | D16, G-9 |
| F-07 | R-25/26/27 | no orders; R-26 support and R-27 iNAV are matrix criteria | n/a | n/a | D6, A7 |
| F-08 | R-28/29/30 | no (no LLM in code) | n/a | n/a | Non-goals |
| F-09 | R-31 | yes (research) | yes | document review | §5 |
| F-10–F-13 | R-32–R-35 | no (no positions or strategies); A1 verifies the entries | n/a | n/a | A1 |
| F-14–F-16 | R-36–R-38 | no | n/a | n/a | — |
| F-17 | R-39 | yes (broker scoring) | yes | n/a | A5 SIPC criterion |
| F-18 | R-12 | no (cost-basis export is a broker criterion only) | n/a | n/a | A7 |
| F-19 | R-40 | no: no orders; mechanism kept, list empty | n/a | n/a | §6 C-3 |

No applicable row is `missing`. R-21 is the only partial.

**Proposed new failure entries.** These are for the owner to approve. The library has not been edited. The four from the first review should go into D4 as well (row 35).

- **Proposed F-xx: shared-identifier attribution.** One issuer identifier can cover many instruments: a fund trust's CIK spans dozens of ETFs, and a ticker maps to the trust. Matching on it attributes an event to the wrong symbol, and the wrong match is welcomed as the positive case everyone was waiting for. *Proposed rule:* every symbol-to-identifier map records cardinality (unique, shared, none). Shared or missing identifiers never attribute an event to a single symbol unless a second key, such as a series or class ID, also matches.
- **Proposed F-xx: a shadowed safety check.** A demo or test meant to show check X trips check Y first. X is then never shown working live, yet the evidence reads as if it were. *Proposed rule:* every refusal reports a specific reason code (or the full list of failed checks), and every refusal demo asserts the code it intends to prove.

### 3. Scores

Formula: score = (full + 0.5 × partial) / total × 100.

| Severity | Rows | Full | Partial | Missing | Arithmetic | Score |
|---|---|---|---|---|---|---|
| Critical | 7 | 7 | 0 | 0 | (7 + 0.5 × 0) / 7 = 7 / 7 | **100.0%** |
| Important | 20 | 18 | 2 | 0 | (18 + 0.5 × 2) / 20 = 19 / 20 | **95.0%** |
| Detail | 8 | 5 | 3 | 0 | (5 + 0.5 × 3) / 8 = 6.5 / 8 | **81.3%** |
| Overall | 35 | 30 | 5 | 0 | (30 + 0.5 × 5) / 35 = 32.5 / 35 | **92.9%** |

On the first review's 30 rows alone, the score is 30 / 30 = 100%. The partial rows are all new findings.

### 4. Top five gaps (none critical)

1. **Track A commits come before the quality gate exists (row 31, important).** *Fix:* make B1 the phase's first commit. A1/A2 research can start at once, but their per-marker commits wait until B1's skeleton passes all four gates, including at least one real test so pytest doesn't exit with code 5. The alternative is for the owner to record a docs-only commit exception in RETRO. Fix this before the first commit.
2. **ETF symbols in the 8-K CIK filter (row 32, important).** *Fix:* in B8, the CIK map records each symbol as unique operating-company CIK, shared trust CIK, or none. Only unique CIKs drive the 8-K match. SPY, QQQ and IWM are logged as `no 8-K filter (fund)`, and the plan doesn't fail on them. Add tests for a shared CIK and a missing ticker. Reword the §2 FR-8 row: news is proven on a real positive case; EDGAR is proven by feed liveness plus a unit-tested filter.
3. **The first review's failure proposals are not routed (row 35, detail).** *Fix:* add those four entries, plus the two above, to D4 so O6 decides them and A9 merges the approved ones.
4. **The accepted risk of the trade-capable paper key is not in RETRO (row 34, detail).** *Fix:* add a row to A11: "paper key can trade; read-only enforced by code guards only; revisit when A7 finds a read-only key option".
5. **The positions read is vacuous (row 33, detail).** *Fix:* D18 states that the Position parser is proven on fixtures only, and A11 adds a Phase 3 debt row to re-verify it on a real payload. Optionally, the owner can place one small manual paper buy in Alpaca's web dashboard before B10 to give a real non-empty payload. That is the owner's call; no code is involved.

**Remaining gaps, all small:**
- **Robustness has no fallback branch.** G-1 says that if the robustness check changes the winner, no recommendation is made, but not what follows. State it: G-1 then fails (HOLD), or the owner records at G3 that the engine choice moves to the Phase 2 install-check. Also say what happens if the ±50% sensitivity check flips the winner: it is reported in the dissent and the recommendation stays labelled provisional.
- **The wrong-host demo is shadowed.** The host lives in `config/spike.toml`, because only four env vars exist. Editing it trips the config-hash and dirty-tree checks before the host check, so B10's demo never shows the host check live. Have the startup check report every failed check with a reason code, and make the evidence show `host` among them. Restore the config with `git checkout -- config` before the real run. The clean-tree check enforces this.
- **The EDGAR client has no runtime allowlist.** Route EDGAR and `company_tickers.json` through the same GET-only (host, path) allowlisted client as D12, with a refusal test, so G-7's runtime guarantee covers every outbound client.
- **G-10 claims more than it checks.** It says "no secret or personal value", but it scans three values, and tracked docs name the owner and spouse by design. Narrow the wording to the three values. Specify how the email is taken out of `SEC_USER_AGENT`, and test that step.
- **G-9 has no rerun rule.** If the REST news GET returns 0 items or the EDGAR pre-filter count is 0, the fix is a new run on another session, never a relaxed criterion.

### 5. Narrative

**Posture.** Revision 2 is a well-executed fix pass. Every top gap from the first review is closed with a check that proves its claim:
- The log is anchored, and the anchor is re-verified at the gate.
- The secret scan checks full values.
- The engine recommendation must survive a worst-case pass over its unverified cells.
- The run window is derived from `next_close`.
- Silence on the data paths no longer counts as proof.

The read-only boundary is now enforced in four places: no SDK, a guard over code and locks, a runtime refusal before send, and an isolated throwaway package.

**Strengths.**
- The plan is honest about its limits. It calls the config hash drift-only, labels the engine choice provisional, and calls the spike code throwaway.
- No bypass flag exists, and off-hours behaviour lives only in tests.
- Windows-specific failure modes (Proactor signals, LF hashing, OneDrive) are anticipated.
- Owner corrections from RETRO are carried consistently through the plan, the tasks and the assumptions.
- Evidence holds counts only.

**Weaknesses (the pattern).** The remaining gaps sit at the seams. Some are between documents: review proposals not routed into D4, an accepted risk not written into RETRO, CLAUDE.md's commit rule against Track A's sequencing. Others are between the plan and its own inputs: the final watchlist is 60% ETFs, and the filings path was designed for operating companies. In a few places a claim still slightly outruns its check: the §2 "real positive case" wording, G-10's "personal value", and the wrong-host demo.

**Most likely failure if run as written.** On day one, A1 closes its first marker and goes to commit. pytest isn't installed, so the agent either commits in breach of CLAUDE.md or stops. The more consequential failure comes later, in B8. IWM resolves to the iShares Trust CIK, and during the live run some iShares Trust 8-K arrives. The spike logs it as an IWM match, and the evidence reports a positive EDGAR match. Reviewers would welcome that as the real case the first review asked for, though it is a misattribution. If the lookup instead misses SPY or QQQ, the poller fails or silently drops them, depending on code the plan doesn't specify.

**Kind of remediation needed.** Wording and sequencing edits plus two small test additions (the CIK cardinality tests and the EDGAR client refusal test). There is no re-scoping and no new deliverable. Fix gap 1 before the first commit. Gaps 2–5 can be the first edits made under run-phase, with the plan and tasks updated to match.

## Phase gate (G1), 2026-11-25

Run by the agent at commit `b8752b2` with the `phase-gate` skill. The gate reports and fixes nothing. Code fixes made earlier in the same session, before this gate, are listed in the summary.

**Verdict: HOLD.** Four gate criteria are not met: G-9 (the live spike failed on EDGAR, so a rerun is required), G-1 (the robustness check changes the engine winner, so there is no engine recommendation), G-4 (21 proposals await the owner) and G-11 (red-team and sign-off are not done). None of them can be closed by more agent work this session. Each needs an owner action, listed under "To reach ADVANCE".

### 1. Quality gates (G-6)

| Command | Result |
|---|---|
| `python -m ruff check .` | All checks passed! |
| `python -m ruff format --check .` | 84 files already formatted |
| `python -m mypy --strict src` | Success: no issues found in 33 source files |
| `python -m pytest -q` | 259 passed |

### 2. Exit criteria

| # | Criterion | Status | Evidence |
|---|---|---|---|
| G-1 | Decision matrix: frozen weights, all candidates scored and cited, unverified share, robustness, sensitivity, recommendation + dissent | **partial: fails as written** | `decision_matrix.md` §6–9 (A6 `fa6e25b`, A7, A10 `66f749f`, A8 `ab9285c`; totals by script, reproduced by the gate). Engines: base NautilusTrader 332 > LEAN 310 > vectorbt 283 (near-tie, 4.4 pp). In the robustness check both unverified E-1 cells go to 0, NautilusTrader and LEAN are excluded (KO E-1) and vectorbt leads, so **no recommendation** is made. Per G-1 this is a HOLD unless the owner records at G3 that the engine choice moves to the Phase 2 install-check. Brokers: Alpaca rank 1 in base and robustness. Price feeds: IEX rank 1, provisional (two sensitivity flips to paid SIP). Company events: EDGAR rank 1 in both. Dissent present (§9.5) |
| G-2 | Zero `[verify` markers; 11 resolved; links fixed | delivered | `grep -rn "\[verify" docs/research/*.md` → 0 lines; `verification_log.md` (A1, A2, A10 rows) |
| G-3 | Every Evidence cell cited or `unverified (reason)` | delivered | gate count: 57 Evidence cells, 0 without a link or `unverified (` |
| G-4 | Every proposal approved or rejected, approved ones merged | **partial** | P-01..P-06 approved and merged as F-20..F-25 / R-41..R-46 (`7cc4f7a`). P-07..P-27 (21 rows; P-26 and P-27 from this gate's failure-check) are `proposed`: **O6 open** |
| G-5 | Alpaca free-tier terms verified | delivered | A2 rows; NEWS_AND_DATA_STACK. Still not stated by Alpaca: whether the free plan streams news, and the delayed-SIP stream on Basic (cited as unverifiable) |
| G-6 | Quality gates green | delivered | §1 above |
| G-7 | Guard test + runtime refusal before send | delivered, with limits | `test_no_order_paths.py`, `test_readonly_http.py` green; planted-violation demo (B2, `ede8078`). Limits found by the failure-check: WebSocket URLs are outside the allowlist, and the guard doesn't confine network libraries to one module (P-27) |
| G-8 | Startup refuses with reason codes; refusal demo shows `host` | delivered | demo at `1e9f906`: `codes=host,config_hash,dirty_tree`, exit 2; config restored, tree clean (`spike_evidence.md`) |
| G-9 | Live spike run | **missing: FAIL, rerun required** | Run 1 (`7c8205e`): account, positions (O7 SPY), both acks, quotes for 5 symbols, REST news 6 passed. EDGAR: 0 completed cycles (poller died; fixed in `1e9f906` and `383adf8`), so the rerun rule applies. News stream: 0 items and REST agrees (0 watchlist items in the window), but delivery is unproven (P-02); cross-check added in `785c383`. The gate re-ran `verify_log --expect-head 33ef7973…c2ff`: `chain OK`, exit 0 (a wrong anchor gives `chain FAILED`, exit 1) |
| G-10 | Secret scan: not found everywhere | delivered | scan after the `pytest -rA` capture: `RESULT: all not found` (12 value × location pairs) |
| G-11 | plan-review READY, phase-gate ADVANCE, red-team, owner sign-off | **partial** | plan-review READY (2026-11-25); this gate HOLD; red-team (G2) and sign-off (G3) not done |

### 3. Coverage re-scored on delivered work

The 35 rows of the 2026-11-25 re-review are re-scored here against what was delivered, not what was planned. Rows whose status changed:

| # | Requirement | Severity | Plan re-review | Delivered | Why |
|---|---|---|---|---|---|
| 1 | PRD §6 Phase 1 gate | critical | full | partial | Red-team and sign-off pending; this gate is HOLD |
| 2 | PRD §5 engine chosen | critical | full | partial | Robustness check changed the winner; no recommendation |
| 12 | FR-8 news and filings | important | full | partial | EDGAR feed not shown live (run 1 bug); news stream has no live positive case |
| 14 | NFR-4 never silent | important | full | partial | Run 1's dead EDGAR poller was silent for 35 min. Fixed in code (`1e9f906`, `e032bb4`); not yet proven live |
| 19 | R-13 self-check | important | full | partial | Clean-tree check excludes `pyproject.toml` and the lock files; stream URLs not asserted (failure-check) |
| 21 | Extend FAILURE_LIBRARY | important | full | partial | O6 open for P-07..P-27 |
| 31 | B1 first commit / gates before commits | important | partial | full | `b610433` was the first Phase 1 commit; gates run before every commit |
| 32 | ETF CIK mapping | important | partial | partial | Shared multi-fund trusts are rejected, but single-ticker trusts (SPY, QQQ) classify as `unique`; only the pinned AAPL/MSFT list keeps them out (failure-check) |
| 33 | Positions on a real payload | detail | partial | full | O7 filled; run 1 parsed the 1-share SPY position |
| 34 | Trade-capable key in RETRO | detail | partial | full | RETRO 2026-11-25 row |
| 35 | Library growth from reviews | detail | partial | full | P-01..P-06 in D4, approved and merged |

All other rows keep their re-review status (full).

| Severity | Rows | Full | Partial | Missing | Arithmetic | Score |
|---|---|---|---|---|---|---|
| Critical | 7 | 5 | 2 | 0 | (5 + 0.5 × 2) / 7 = 6 / 7 | **85.7%** |
| Important | 20 | 15 | 5 | 0 | (15 + 0.5 × 5) / 20 = 17.5 / 20 | **87.5%** |
| Detail | 8 | 8 | 0 | 0 | 8 / 8 | **100.0%** |
| Overall | 35 | 28 | 7 | 0 | (28 + 0.5 × 7) / 35 = 31.5 / 35 | **90.0%** |

### 4. Failure check on delivered work

A separate reviewer agent ran it against the code and docs at `3a0c6c1`; the gate then checked its findings against later commits. Library rules R-13..R-46: 15 apply, 8 yes, 7 partial, 0 missing. Master-brief rules 1–12: 3 apply, 2 yes, 1 partial (rule 10). No applicable row is `missing`.

| Rule | Finding at `3a0c6c1` | Status at `b8752b2` |
|---|---|---|
| R-13 | Clean-tree check covers `src` and `config` only (not `pyproject.toml` or the locks); the version check compares two strings in one tree; stream URLs not asserted | open |
| R-21 | Redaction runs after `str(exc)[:200]` truncation; console lines are not redacted (theoretical today) | open |
| R-22 | WebSocket URLs (which receive the key and secret) have no scheme or host check; the guard doesn't confine `httpx`/`urllib` to one module | open; proposed as P-27 |
| R-23 | httpx and websockets errors are not `OSError`, so EDGAR died on its first timeout (probe) and a stream on a refused handshake; positions, news REST and the CIK fetch are unguarded | **fixed** for EDGAR and stream handshakes (`383adf8`; tests drive the real adapters). Unguarded startup reads still crash the run, loudly and before the streams start: open |
| R-24 staleness | Measured as the gap between arrivals, not data age; age uses the unsynced clock | open (P-12, P-25) |
| R-42 | A stream that returns on a fatal code is not reported, and the exit code stays 0; heartbeat without a subscription; G-9 FAIL | **fixed**: a task ending before stop is reported (`e032bb4`), and the news stream is cross-checked against REST (`785c383`). Heartbeat wording and the G-9 rerun: open |
| R-45 | Single-ticker trust CIKs (SPY, QQQ) classify as `unique` and pass the filter | open (the config pin holds) |
| Rule 10 | G-9 FAIL; error-path tests used exception types the real adapters never raise | partly fixed (`383adf8`); G-9 open |

New patterns found: **P-26** (fakes raise different errors from the real adapter) and **P-27** (the egress allowlist covers HTTP only), both added to D4 as `proposed` (`b8752b2`). The library itself was not edited.

### 5. To reach ADVANCE

1. **B10 run 2** (owner): sync the PC clock, then rerun in another session. The run must show EDGAR cycles with `pre_filter_min` > 0, `mean_rps` ≤ 1, no `ERROR: source task` line, and a news cross-check verdict. The agent then adds the run 2 section and the new anchor to D18 and re-scores EDGAR DE-4 and DE-5, and phase-gate re-runs.
2. **O6** (owner): approve or reject P-07..P-27; A9 then merges the approved ones.
3. **G-1** (owner, at G3): either record that the engine choice moves to the Phase 2 install-check, or supply verified evidence for NautilusTrader's or LEAN's E-1 (kernel in front of every order path).
4. **G2** red-team in a fresh session, with findings resolved; **G3** owner sign-off in RETRO.
