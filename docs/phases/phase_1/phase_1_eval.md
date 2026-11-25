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
