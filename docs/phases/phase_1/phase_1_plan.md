# Phase 1 plan: research and read-only data spike

Status: revision 2 for `plan-review` re-review · Written 2026-11-24, revised 2026-11-24 after `phase_1_eval.md` (FIX FIRST) · Source of scope: `docs/HANDOFF.md` "Phase 1 definition" · Traces to `docs/PRD.md` v0.2 · Phase 0 signed off by the owner 2026-11-24 (`docs/RETRO.md`).

Two tracks run in parallel. **No order endpoint is imported, called or reachable anywhere in this phase.**
- **Track A, Research:** verify, extend and decide. Output is documents only.
- **Track B, Read-only data spike:** Python on Windows, **throwaway code** in its own package `family_desk_spike`, which Phase 3 must not import. Asserts the paper endpoint, reads the account and positions, streams IEX quotes and Alpaca News for a 5-symbol watchlist, polls the SEC EDGAR 8-K Atom feed on a fixed cadence under a ≤1 request/second ceiling, and writes everything to an append-only, anchored local log. Tested with fakes.

## 1. Goal and gate

**Goal:** choose the engine (provisionally, see G-1) and build the evidence for the broker and data-source candidates (PRD §5, §6, FR-3), using verified primary-source research. Prove that the data paths needed by Phase 3 (account, positions, quotes, news, filings) work read-only, on the owner's PC, on real positive cases, without any route to an order.

**PRD §6 gate (Phase 1):** "Decision matrix reviewed (plan-evaluation + independent review) and owner sign-off". HANDOFF refines it to: decision matrix and spike pass plan-review and phase-gate, red-team runs in a fresh session, and owner sign-off is recorded in RETRO.

**Testable gate. Every item must hold:**

| # | Criterion | How it is checked |
|---|---|---|
| G-1 | `docs/research/decision_matrix.md` exists with criteria and weights fixed before scoring; all 3 engines, all 4 broker candidates and the data-source options (see D6) scored; every score cell cited to a primary source or marked `unverified`; the **unverified share per candidate** reported; a **robustness check**: the recommendation does not change when every `unverified` cell is set to its worst plausible score (if it changes, the recommendation says so and is not made); a recommendation plus a skeptic's dissent. The engine choice is labelled **provisional, install-check in Phase 2** (engine packages bundle live order adapters, so installing one is a CLAUDE.md hard stop before the Phase 3 gate; the Phase 2 check needs explicit owner approval) | phase-gate reads the file; unverified share table and robustness table present; every row has a source column; the owner accepts the provisional label at G3 |
| G-2 | Zero verify markers remain in `docs/research/*.md`, searched with the pattern `\[verify` (which also catches `[verify: ...]`). Each of the **11** original markers (7 in FAILURE_LIBRARY: F-05, F-06, F-10, F-11, F-12, F-15, F-17; 4 in NEWS_AND_DATA_STACK) is resolved to confirmed, corrected or unverifiable, with a row in `docs/research/verification_log.md`. The two explanatory mentions in FAILURE_LIBRARY (line 3 intro, line 97 open question) are reworded so they no longer use the bracketed marker (wording only, no change in meaning). Every dead or truncated link in `docs/research/*.md` is replaced with a working primary source or marked `unverified (dead link)`; non-primary citations used as the only source for a factual claim are replaced with a primary source where one exists | `Select-String -Path docs\research\*.md -Pattern "\[verify"` returns nothing; the log has 11 marker rows plus one row per link fixed; F-14 SSRN link and the NEWS_AND_DATA_STACK dev.to citation for the EDGAR Atom feed are among the fixed rows |
| G-3 | Every "Evidence and decay" cell in STRATEGY_ENCYCLOPEDIA has a primary-source citation or is explicitly marked `unverified (reason)` | phase-gate script or manual count: cells without a link or `unverified` = 0 |
| G-4 | Retail-algo post-mortems and broker-API incidents (Alpaca, Schwab, Robinhood; IBKR if found) are written as proposed F-xx/R-xx entries; the owner has approved or rejected each; approved ones are merged into FAILURE_LIBRARY | `docs/research/failure_library_proposals.md` has a decision column with no blanks; merged entries appear in FAILURE_LIBRARY |
| G-5 | Alpaca free-tier news and market-data terms (rate limits, WebSocket connection limits, IEX scope, delayed-SIP availability, storage and redistribution terms) are verified against Alpaca's own pages and recorded | rows in verification_log; NEWS_AND_DATA_STACK updated |
| G-6 | Quality gates defined and green: `ruff check .`, `ruff format --check .`, `mypy --strict src`, `python -m pytest -q` | command output pasted in phase-gate |
| G-7 | A guard test proves that, anywhere in `src/` or the lock files, there is no order endpoint path, order method, HTTP verb other than GET, or trading SDK; that no module outside `family_desk_spike` imports it; and that `tests/` contains no `unittest.mock`. A runtime test proves the D12 client refuses `/v2/orders`, any path not on its (host, path) allowlist, and every non-GET verb, **before** any request is sent | `tests/test_no_order_paths.py` passes, and fails against a planted violation (shown once in evidence); `tests/test_alpaca_readonly.py` refusal cases pass |
| G-8 | The startup check refuses to run unless the endpoint is exactly the paper host, `APCA_PAPER=true`, the config hash matches the committed expected hash, and the package version equals the `pyproject.toml` version. For the live run only, it also refuses if `src/` or `config/` has uncommitted changes, and it records the commit hash. Stated limit: the config hash detects drift, not deliberate tampering, until Phase 3 adds signed config | tests in `tests/test_startup.py`; a live refusal is shown in the evidence with a deliberately wrong config |
| G-9 | Live spike run: ≥30 minutes, market open per `/v2/clock`, start ≥ 10:00 ET and planned end ≤ `next_close` − 30 minutes (15:30 ET on a full day, earlier on a half-day; the runner refuses otherwise). Recorded: account; positions; a logged **subscription ack** for the quote and news streams; quotes for all 5 symbols with update rate and spread per symbol; ≥1 watchlist news item parsed from the **startup REST news GET**, plus stream news messages or a logged "no news" heartbeat; EDGAR poll cycles with the **pre-filter Atom entry count > 0** and the post-filter match count reported; measured EDGAR request rate ≤1/s. `verify_log` prints `chain OK`, `seq_last` and `head_hash` | `python -m family_desk_spike.verify_log <file>` output in `docs/phases/phase_1/spike_evidence.md`; phase-gate re-runs it with `--expect-head` taken from that file |
| G-10 | No secret or personal value appears in git history, tracked files, logs, docs or test output. `python -m family_desk_spike.tools.secret_scan` loads values only through `family_desk_spike.config` (the only `.env` reader) and searches for the **full values** of `APCA_API_KEY_ID`, `APCA_API_SECRET_KEY` and the contact address in `SEC_USER_AGENT` across `git log -p --all`, all tracked files, `logs/`, `docs/`, and pytest output saved with `-rA` to `logs/pytest_output.txt`. It prints only `found`/`not found` per value name and location, never a value | scan output in evidence shows `not found` for every value and location; `tests/test_secret_scan.py` (planted fake value found, clean tree not found, output never contains the value) and `tests/test_redaction.py` pass |
| G-11 | plan-review READY, phase-gate ADVANCE, red-team in a fresh session with findings resolved, and the owner's sign-off row in `docs/RETRO.md` | files `phase_1_eval.md`, `phase_1_summary.md`, `phase_1_redteam.md`; RETRO row |

## 2. Scope

**Requirement IDs covered**

| ID | Coverage this phase |
|---|---|
| PRD §5 (engine choice) | Full, provisional: engine chosen in the decision matrix; install-check in Phase 2 with owner approval |
| PRD §6 Phase 1 gate | Full |
| PRD §6 data choice | Partial: data-source options ranked in the matrix with spike measurements; no purchase, no new account |
| FR-3 | Partial: read-only broker adapter `Protocol` (account, positions) with an Alpaca paper implementation; live-broker comparison evidence (the choice stays open per RETRO) |
| FR-6 | Partial: re-verify STRATEGY_ENCYCLOPEDIA evidence (prerequisite for Phase 4) |
| FR-8 | Partial: ingest Alpaca News (stream + REST history) and EDGAR 8-K for the watchlist, each proven on a real positive case; adjacent symbols out of scope |
| FR-10 | Partial: data-staleness detection on the quote and news streams (measured and logged; no halting logic, because nothing trades) |
| NFR-2 | Partial: parsing, rate limiting, staleness, run-window and log chaining are pure functions with tests |
| NFR-3 | Partial: paper endpoint asserted at startup, pinned and hashed dependencies, secrets only in `.env` read by code, masked in reprs and logs, full-value secret scan |
| NFR-4 | Partial: stream disconnect, reconnect, backoff, API errors and Windows Ctrl+C shutdown are handled and logged, never silent |
| NFR-6 | Partial: append-only, hash-chained local log with an external head anchor, reproducible counts from logs |
| NFR-7 | Partial: C-6, C-7, C-10 (see §6) |
| R-13 (inv. 17) | Partial: version + config-hash + clean-tree self-check at startup (drift detection, not tamper-proof) |
| R-14 | Partial: spike package is throwaway, isolated and import-guarded; no bypass flags in the runner |

**Non-goals (explicit)**
- Any order, order endpoint, order SDK class, cancel, replace, position close or account-config write. This also covers paper orders.
- Installing or importing any execution/backtest engine package (they bundle live order adapters). Engine evidence is from documentation only this phase.
- Choosing the live broker (RETRO: kept fluid). The matrix ranks and records; it does not decide.
- Buying any data plan. The data-source section ranks options only.
- Risk kernel, ledger of trades, tax logic, dashboard, command channel, alerts/paging (Phase 3).
- Halt feeds, FRED, macro calendars, Google News, IR RSS ingestion. These are verified in research only, not built.
- Adjacent-symbol expansion, "why is it moving" briefs (FR-9), any LLM call in code.
- Cloud hosting, secrets manager, EC2/Lightsail (NFR-3's secrets manager is Phase 3 debt, written to RETRO by A11).
- Backtests of any strategy (Phase 4).
- Values for the Phase 0 decisions table. The owner writes them; the agent does not propose numbers.
- Reusing spike code in later phases. `family_desk_spike` is deleted or left unimported; Phase 3 writes its own code from the Phase 2 spec.

## 3. Deliverables

All Track B code lives in the throwaway package `src/family_desk_spike/`. Later phases must not import it (D8 guard; RETRO debt row via A11).

| # | Deliverable | Path | Requirement ID | Proven by |
|---|---|---|---|---|
| D1 | Verification log (claim · original text · primary source URL · accessed date · verdict confirmed/corrected/unverifiable · change made), including link-fix rows | `docs/research/verification_log.md` | NFR-7, G-2 | one row per original verify marker (11) plus one per fixed link; the G-2 search returns nothing |
| D2 | FAILURE_LIBRARY with verify markers resolved (citations added; the two explanatory mentions reworded; substantive corrections go through D4) | `docs/research/FAILURE_LIBRARY.md` | G-2 | search + D1 rows F-05, F-06, F-10, F-11, F-12, F-15, F-17 |
| D3 | NEWS_AND_DATA_STACK updated with verified Alpaca free-tier terms (incl. delayed SIP), EDGAR fair-access terms (SEC page replacing the dev.to citation), endpoint URLs, and the 4 verify rows resolved | `docs/research/NEWS_AND_DATA_STACK.md` | FR-8, C-7, G-5 | D1 rows; each limit cites an Alpaca or SEC page |
| D4 | Proposed failure entries (retail-algo post-mortems; Alpaca/Schwab/Robinhood/IBKR API incidents; spike-found patterns), each with source, root cause, proposed rule, and an owner decision column | `docs/research/failure_library_proposals.md` | G-4, inv. 10 | owner decision column has no blanks; approved entries merged (D2) |
| D5 | STRATEGY_ENCYCLOPEDIA with every Evidence cell cited or marked `unverified (reason)`; publication year noted for decay (F-03/R-20) | `docs/research/STRATEGY_ENCYCLOPEDIA.md` | FR-6, G-3 | cell count check in phase-gate |
| D6 | Decision matrix: criteria + weights (frozen, dated, before scoring), engines (NautilusTrader, LEAN, custom on vectorbt), brokers (Alpaca, Schwab Trader API, Robinhood Agentic Trading, IBKR), **data sources** (Alpaca free IEX; Alpaca delayed SIP on the free plan; Alpaca paid SIP, ranked only; Alpaca/Benzinga news vs EDGAR-only vs IR RSS for company events; iNAV/indicative-value availability for R-27), scores with citations, unverified share per candidate, robustness check (unverified cells at worst plausible score), sensitivity check (does the winner change if any single weight moves ±50%?), provisional engine recommendation, broker ranking, data-source ranking, skeptic's dissent | `docs/research/decision_matrix.md` | PRD §5, §6, FR-3, G-1 | file review in phase-gate + red-team |
| D7 | Project tooling: `pyproject.toml`, `requirements.lock` + `requirements-dev.lock` (exact pins with `--hash`), ruff + mypy + pytest config; CLAUDE.md "Quality gates" section updated | repo root, `CLAUDE.md` | NFR-3, G-6 | `pip install --require-hashes -r requirements-dev.lock` then all four gate commands green |
| D8 | No-order-path and spike-isolation guard test | `tests/test_no_order_paths.py` | NFR-1, inv. 1, R-14, G-7 | passes; a planted violation fails it (evidence) |
| D9 | Config + startup self-check: settings parsed from env into a typed model with masked secrets; `assert_paper()`; config-hash check against `config/spike.toml.sha256`; version check against `pyproject.toml`; live-run clean-tree check and commit hash; version report | `src/family_desk_spike/config.py`, `src/family_desk_spike/startup.py`, `config/spike.toml`, `config/spike.toml.sha256` | NFR-3, R-13, inv. 17, G-8 | `tests/test_startup.py`, `tests/test_config.py` |
| D10 | Append-only hash-chained JSONL log + verifier CLI that prints `seq_last` and `head_hash` and accepts `--expect-head` | `src/family_desk_spike/applog.py`, `src/family_desk_spike/verify_log.py` | NFR-6, C-10 | `tests/test_applog.py` (append, chain, tamper detection, mid-file gap detection, tail truncation detected only against `--expect-head`, trailing partial line reported) and `tests/test_redaction.py` |
| D11 | Typed models + pure parsers (Account, Position, Quote, NewsItem, Filing8K, StreamEvent, SubscriptionAck) | `src/family_desk_spike/models.py`, `src/family_desk_spike/parse/*.py` | NFR-2 | `tests/test_parse_*.py` with recorded/synthetic payloads in `tests/fixtures/` |
| D12 | Read-only Alpaca REST adapter (`ReadOnlyBroker` Protocol; GET-only client with a (host, path) allowlist: trading host `/v2/account`, `/v2/positions`, `/v2/clock`; data host `/v1beta1/news`); refuses anything else before sending | `src/family_desk_spike/broker/readonly.py`, `src/family_desk_spike/broker/alpaca_readonly.py` | FR-3, FR-8, NFR-1 | `tests/test_alpaca_readonly.py` with `FakeHttp`, incl. refusal of `/v2/orders`, off-allowlist paths and every non-GET verb |
| D13 | IEX quote stream client (auth, subscribe 5 symbols, log subscription ack, parse, reconnect with capped exponential backoff, staleness per symbol, update rate and spread stats) | `src/family_desk_spike/data/iex_stream.py`, `src/family_desk_spike/core/staleness.py` | FR-8, FR-10, NFR-4 | `tests/test_iex_stream.py`, `tests/test_staleness.py` with `FakeWebSocket`, `FakeClock` |
| D14 | Alpaca News stream client (same pattern; logs subscription ack; dedupe by news id; stores id, headline, symbols, url, source timestamps only) plus a startup REST news GET for the watchlist (24-hour lookback, small limit, same metadata-only storage) | `src/family_desk_spike/data/news_stream.py`, `src/family_desk_spike/data/news_rest.py` | FR-8, inv. 6, C-7 | `tests/test_news_stream.py`, `tests/test_news_rest.py` |
| D15 | EDGAR 8-K Atom poller (poll cadence from config, default 60 s, under a token-bucket ceiling of ≤1 req/s; owner User-Agent from env; defusedxml parsing; logs pre-filter entry count and post-filter match count every cycle; dedupe by accession number; backoff on 403/429/5xx; watchlist CIK filter normalised to 10-digit zero-padded form) | `src/family_desk_spike/data/edgar.py`, `src/family_desk_spike/core/ratelimit.py` | FR-8, C-7 | `tests/test_edgar.py` (incl. feed CIK `0000320193` matching `company_tickers.json` integer `cik_str` 320193; pre-filter count logged when zero entries match), `tests/test_ratelimit.py` (FakeClock proves ≤1/s over 1,000 simulated polls) |
| D16 | Spike runner `python -m family_desk_spike --duration-min N` wiring D9–D15; run-window check (market open, start ≥ 10:00 ET, end ≤ `next_close` − 30 min) with **no bypass flag**; Windows-safe shutdown (Ctrl+C caught as `KeyboardInterrupt` around `asyncio.run`, no `loop.add_signal_handler`); cancels tasks, flushes and closes the log, prints the exit summary | `src/family_desk_spike/__main__.py`, `src/family_desk_spike/core/run_window.py` | all Track B, R-14, inv. 14 | `tests/test_spike_e2e.py` runs the whole runner against fakes, with a `FakeClock` set inside the window, and drives shutdown both by an injected stop event and by a `KeyboardInterrupt` raised from a fake source (log flushed, summary written, chain verifies); `tests/test_run_window.py` (closed market, before 10:00 ET, run crossing the half-day close all refuse) |
| D17 | Fakes package | `tests/fakes/` (`FakeHttp`, `FakeWebSocket`, `FakeClock`, `FakeEnv`, `FakeGit`) | engineering stance | used by D8–D16, D20 tests; no `unittest.mock` in `tests/` (guard asserts) |
| D18 | Live spike evidence: command, duration, commit hash, counts per source, subscription acks, REST news count, EDGAR pre-filter and match counts, quote update rate and spread per symbol, staleness stats, EDGAR measured rate, verify_log output including `seq_last` and `head_hash` (the anchor), startup refusal demo, planted-violation demo, secret-scan output. **No news text, no secrets, no personal values** | `docs/phases/phase_1/spike_evidence.md` | G-8, G-9, G-10 | file review; phase-gate re-runs `verify_log --expect-head` |
| D19 | Eval, summary, red-team reports | `docs/phases/phase_1/phase_1_eval.md`, `phase_1_summary.md`, `phase_1_redteam.md` | G-11 | the files exist with verdicts |
| D20 | Secret scanner (full values of the two Alpaca secrets and the SEC contact address; prints only `found`/`not found`) | `src/family_desk_spike/tools/secret_scan.py` | NFR-3, G-10 | `tests/test_secret_scan.py` |
| D21 | RETRO "Known debt" rows for items this phase defers | `docs/RETRO.md` | NFR-3, C-10, R-14, R-21 | rows present (see A11) |

## 4. Sequence

Track A (A*) and Track B (B*) run in parallel. Owner rows (O*) can run any time unless a dependency is listed.

| # | Unit of work | Depends on | Parallel? | Owner | Check that ends it |
|---|---|---|---|---|---|
| A1 | Verify the 7 verify-marked entries in FAILURE_LIBRARY (F-05, F-06, F-10, F-11, F-12, F-15 `[verify: Barber & Odean]`, F-17) against primary sources (SEC/CFTC reports, court filings, issuer notices, peer-reviewed papers); reword the two explanatory mentions (lines 3 and 97) without changing meaning; check every link in `docs/research/*.md` and **fix** dead or truncated ones (F-14 SSRN first) with a working primary source, or mark `unverified (dead link)`; start D1. One commit per closed marker or fixed link, with the source URL in the message (AS-13) | none | yes, with A2–A5, B* | agent | 7 marker rows + link rows in D1; one commit each; `\[verify` search on FAILURE_LIBRARY returns nothing |
| A2 | Verify Alpaca free-tier news and market-data terms (REST rate limit, WebSocket connection limits per stream, IEX scope, delayed-SIP availability on the free plan, news storage/redistribution/attribution terms, exact paper REST host, data REST host and news path, data/news stream URLs), EDGAR fair-access terms and the 8-K Atom URL (replace the dev.to citation with an SEC page), and the 4 verify rows in NEWS_AND_DATA_STACK; update D3. One commit per closed marker, with the source URL in the message (AS-13) | none | yes | agent | D1 rows for each; 4 marker commits; D3 updated; URLs used by B* recorded |
| A3 | Re-verify every Evidence cell in STRATEGY_ENCYCLOPEDIA (12 families), adding the publication year and an out-of-sample/decay note | none | yes, per family | agent | G-3 count = 0 uncited cells |
| A4 | Research retail-algo post-mortems (first-hand write-ups, r/algotrading threads with specifics, broker incident pages) and broker-API incidents (Alpaca, Schwab Trader API, Robinhood, IBKR status-page history, order bugs, outages); write D4 entries with recurring causes ranked by frequency | none | yes | agent | ≥1 sourced entry per broker or an explicit "none found, searched X"; recurring causes ranked |
| A5 | Freeze decision-matrix criteria and weights before any scoring, for engines, brokers and data sources (e.g. Windows support, Python fit, licence/cost, paper↔live parity, broker-side stop-limit/bracket support, key scoping/IP allowlist, rate limits, automation terms, SIPC/regulation, cost-basis/lot export, incident history, maintenance activity; for data: share of consolidated volume, quote update rate and spread on the watchlist, latency, iNAV availability, terms, cost); date-stamp them; define "worst plausible score" per criterion for the robustness check | none | yes | agent | criteria + weights section committed before A6/A7/A10 start |
| A6 | Score engines: NautilusTrader, LEAN, custom on vectorbt (Windows support from docs only, no installs; licence; live adapters; event-driven vs vectorised; point-in-time support; community health) | A5 | yes, with A7 | agent | every engine cell cited or `unverified` |
| A7 | Score brokers: Alpaca, Schwab Trader API, Robinhood Agentic Trading, IBKR (order types incl. stop-limit at broker, paper availability, API terms on automation, key controls incl. read-only key availability, rate limits, fractional, cost-basis export, incidents from A4) | A5, A2, A4 | yes, with A6 | agent | every broker cell cited or `unverified` |
| A10 | Score data sources (D6 list) using A2's verified terms and the spike's measured quote update rate and spread per symbol | A5, A2, B11 | yes, with A6/A7 | agent | every data cell cited, measured (D18 reference) or `unverified` |
| A8 | Matrix totals, unverified share per candidate, robustness check, sensitivity check (±50% per weight), provisional engine recommendation, broker ranking (no live-broker decision), data-source ranking (no purchase), skeptic's dissent; re-check from a skeptic's framing per MASTER_BRIEF | A6, A7, A10 | no | agent | D6 complete; unverified, robustness and sensitivity tables present |
| O6 | Owner approves or rejects each D4 proposed failure entry | A4, B11 | no | owner | decision column filled |
| A9 | Merge owner-approved D4 entries into FAILURE_LIBRARY with next F-/R- numbers; also merge corrections from A1 that changed meaning (owner-approved in D4) | O6 | no | agent | merged entries present; D4 rows reference final IDs |
| A11 | Write D21 RETRO debt rows: C-10 7-year retention policy (Phase 3); NFR-3 secrets manager (Phase 3); Alpaca paper key rotation due 90 days after O1 (R-21); engine install-check, provisional choice (Phase 2, owner approval needed); `family_desk_spike` must not be imported by Phase 3 and is deleted at Phase 3 start (R-14); config signing replaces the drift-only hash (Phase 3) | O1 | yes | agent | rows present in RETRO "Known debt" |
| B1 | Tooling: `pyproject.toml` (src layout, Python 3.12, package `family_desk_spike`), pinned + hashed lock files (pip-tools `--generate-hashes`), ruff, mypy `--strict`, pytest; update CLAUDE.md Quality gates | none | yes | agent | four gate commands green on skeleton |
| B2 | Guard test D8: AST + text scan of `src/` and the lock files. Fails on: `/v2/orders`, `orders` path segments, `submit_order`, `cancel_order`, `replace_order`, `close_position`, `alpaca-py`/`alpaca_trade_api`/`alpaca` trading packages, engine packages (`nautilus_trader`, `lean`, `vectorbt`), any HTTP method other than GET **anywhere in `src/`**, and any import of `family_desk_spike` from a module outside it. `tests/` is scanned only for `unittest.mock`, so refusal tests may name `/v2/orders` | B1 | no | agent | test passes; planted violation fails (pasted) |
| B3 | Config + startup D9: typed settings from env (`APCA_API_KEY_ID`, `APCA_API_SECRET_KEY`, `APCA_PAPER`, `SEC_USER_AGENT`) with secrets and the UA contact as masked types; `assert_paper()` requires host == exact paper host from A2 and `APCA_PAPER == "true"`; config sha256 must match committed file; package version must equal `pyproject.toml`; live run refuses if `git status --porcelain -- src config` is non-empty (via an injected git reader, `FakeGit` in tests) and records the commit hash; prints version, commit and config hash, never secrets | B1 | yes, with B4 | agent | `test_startup.py`, `test_config.py` green (wrong host, missing flag, live host, hash mismatch, version mismatch, dirty tree, missing UA all refuse) |
| B4 | Append-only log D10: one JSONL file per UTC day under `logs/spike/`; open in append mode only; each record = `seq`, `received_at_utc`, `source`, `source_ts`, `payload`, `prev_hash`, `hash`; redaction filter (secrets and UA contact); `verify_log` CLI prints `chain OK`, `seq_last`, `head_hash`, and fails on mismatch with `--expect-head` | B1 | yes, with B3 | agent | `test_applog.py` and `test_redaction.py` green incl. tamper, mid-file gap, tail truncation against the anchor, redaction |
| B5 | Models + parsers D11, read-only REST adapter D12 with `FakeHttp` (incl. refusal tests), and the startup REST news GET (D14 `news_rest.py`) | B2, B3, B4, A2 (URLs) | yes, with B6–B8 | agent | tests green; guard still green |
| B6 | IEX quote stream D13 with `FakeWebSocket`/`FakeClock`: auth, subscribe, subscription ack logged, parse, connection-limit error handling, reconnect backoff, per-symbol staleness, silent-stall detection (connected but no messages for T seconds = logged `stale`), update rate and spread stats | B2, B3, B4, A2 | yes | agent | tests green |
| B7 | News stream D14: same pattern; subscription ack logged; dedupe; store only id/headline/symbols/url/timestamps; content never parsed as instructions or evaluated | B2, B3, B4, A2 | yes | agent | tests green |
| B8 | EDGAR poller D15: poll cadence from config (default 60 s) under a token-bucket ceiling of ≤1 req/s (stricter than SEC 10/s, per HANDOFF), User-Agent from env, refuses to start without it, defusedxml, pre-filter and match counts logged every cycle, dedupe accession numbers, CIK map for the watchlist from SEC `company_tickers.json` normalised to 10-digit zero-padded strings (fetched once, cached in `data/`), backoff on 403/429/5xx | B2, B3, B4, A2 | yes | agent | tests green incl. 1,000-poll FakeClock rate proof and the CIK padding test |
| B9 | Spike runner D16 + run-window check + Windows-safe shutdown + offline end-to-end test against all fakes; no CLI bypass flag (off-hours behaviour is exercised only in tests through `FakeClock`); exit summary (counts, acks, staleness, rates, EDGAR pre-filter/match counts, `seq_last`, `head_hash`) | B5–B8 | no | agent | `test_spike_e2e.py` and `test_run_window.py` green; all gates green |
| B12 | Secret scanner D20 with `tests/test_secret_scan.py` | B3 | yes | agent | tests green |
| O1 | Confirm Alpaca paper keys were regenerated and `.env` holds the 4 variables; `git check-ignore .env` prints `.env`; tell the agent the regeneration date (for A11) | none | yes | owner | owner confirms in chat (no values pasted) |
| O2 | Watchlist is final: `SPY, QQQ, IWM, AAPL, MSFT` (owner decision 2026-11-24, RETRO). B3 commits it in `config/spike.toml` with its hash | none | n/a | owner | done: RETRO row |
| B10 | Live spike run during the regular session, starting at or after 10:00 ET with the run ending by `next_close` − 30 min (the runner refuses otherwise): `python -m family_desk_spike --duration-min 35`, then `python -m family_desk_spike.verify_log logs\spike\<date>.jsonl`; also run once with a deliberately wrong host to show the refusal | B9, O1 | no | owner | verify_log prints `chain OK`, `seq_last`, `head_hash` and the counts |
| B11 | Write D18 from the summary and verify_log output only (counts, rates, anchor, no news text, no secrets, no personal values); run `pytest -rA` to `logs/pytest_output.txt`, then the G-10 secret scan; add any new failure pattern seen to D4 | B10, B12 | no | agent | D18 committed; scan prints `not found` for every value and location |
| O3 | Phase 0 decisions table (bucket sizes, hard limits, $X/Y%/N minutes, budget) in `docs/phases/phase_0/decisions.md` (in git: limits and rules only, no balances or account numbers) | none | yes | owner | table committed; contains no balances or account numbers |
| G1 | `phase-gate` (includes `failure-check` on delivered work; re-runs `verify_log --expect-head` from D18) | A8, A9, A11, B11 | no | agent | `phase_1_summary.md` + eval completion section; ADVANCE or HOLD |
| G2 | `red-team` in a fresh session (ideally a different model) | G1 | no | owner | `phase_1_redteam.md` with go/no-go; findings resolved |
| G3 | Owner sign-off row in `docs/RETRO.md` (provisional engine choice accepted, spike accepted) | G2 | no | owner | RETRO row dated |

Phase 0 was signed off by the owner on 2026-11-24 (RETRO). O3 is RETRO debt due before the Phase 2 phase-plan; it does not block G1–G3. O4 (advisor statements) and O5 (CPA booking) left this plan: they are RETRO debt due before the Phase 6 real-money gate. The employer personal-trading policy check was removed by the owner; the restricted list starts empty and is owner-maintained; O2 records the final watchlist. CPA inputs and CPA sign-off on the tax model are RETRO debt due before the Phase 6 real-money gate; nothing in Phase 1 depends on them.

## 5. Failure modes and edge cases

| Failure / edge case | Library ref | Handling in this phase |
|---|---|---|
| An order path slips in through an SDK, a copied snippet or a later edit | F-01 (R-14), F-04 | No trading SDK or engine package at all; GET-only client with a (host, path) allowlist that refuses before sending; guard test B2 on code **and** lock files; runtime refusal tests |
| Paper key is trade-capable, so only our code prevents a paper order | F-04 (R-21) | Code guards above; A7 records whether each broker offers read-only keys; noted as accepted risk for the spike |
| Live endpoint or wrong config used by mistake | F-01 (R-13), inv. 17 | `assert_paper()` + config-hash + version check before any network call; live run refuses on a dirty tree; refusal demo in evidence |
| Keys or personal values leak into logs, test output, evidence or git | F-04 (R-21) | masked secret types; redaction filter on the log; full-value G-10 scan over history, files, logs, docs and test output; evidence holds counts only |
| Stolen/leaked keys from the earlier chat | F-04 | O1 blocks B10; rotation date recorded by A11 |
| Dependency tampering / unexpected transitive SDK | F-04, rule 11 | exact pins + hashes; `--require-hashes` install; guard scans lock |
| Spike code or a bypass flag carried into Phase 3 | F-01 (R-14) | separate `family_desk_spike` package; guard fails on any import of it from outside; no `--allow-closed` or other bypass flag (off-hours paths tested only via `FakeClock`); RETRO debt row (A11) to delete it at Phase 3 start |
| A data path is broken but looks quiet (wrong subscription, CIK filter never matches) | none in library | subscription acks logged; startup REST news GET must return ≥1 watchlist item; EDGAR pre-filter entry count must be > 0; CIK zero-padding unit test |
| Stream connected but silent (stall) | F-05 (R-23), inv. 14 | per-symbol and per-stream staleness; stall logged as `stale` event, never silently ignored |
| Alpaca free-tier connection limit (second connection rejected) | F-05 | A2 verifies the limit; B6/B7 handle the auth/limit error code, back off, log; never hot-loop reconnect |
| Broker/API outage or 5xx during the run | F-05 (R-23) | capped exponential backoff with jitter; every error logged with a source; spike keeps other sources running |
| EDGAR blocks the IP for missing UA or over-rate | C-7 | UA required at startup; 60 s default cadence under a ≤1 rps ceiling proven by test; 403/429 → back off ≥10 minutes and log |
| Hostile or odd external text (news headline, Atom XML) | rule 6, inv. 6 | defusedxml (no entity expansion); text stored as data, never evaluated, templated or sent to an LLM; size caps on fields |
| Market closed, holiday, half-day, pre/post market, run crossing the close | F-06 (R-24) | runner refuses unless the market is open per `/v2/clock`, start ≥ 10:00 ET and start + duration ≤ `next_close` − 30 min (covers half-days such as 27 Nov 2026); no bypass flag |
| Ctrl+C on Windows leaves the log unflushed or tasks running | NFR-4 | `KeyboardInterrupt` caught around `asyncio.run` (no `loop.add_signal_handler`, which Windows' Proactor loop lacks); flush per record; shutdown tested in `test_spike_e2e.py` |
| Clock skew / timezone bugs | red-team item 9 | all timestamps UTC ISO-8601; store both `source_ts` and `received_at_utc`; log skew stats; ET window computed with `zoneinfo` |
| Log tampering, truncation, partial write on crash | NFR-6 | hash chain + `seq`; flush per record; verifier detects mid-file gaps; tail truncation and wholesale rewrite detected against the `head_hash` anchor recorded in D18; a trailing partial line is reported, not silently dropped |
| Duplicate news/filings after reconnect | none | dedupe by news id / accession number within the run |
| Backtest-style overconfidence in research | F-02, F-03, F-09 | A3 notes out-of-sample/decay and publication year; LLM backtest results never count as evidence |
| Research anchoring (agreeing with the plan doc) or a recommendation resting on unverified cells | MASTER_BRIEF working rules | A5 freezes weights before scoring; A8 robustness check, sensitivity check and written dissent; red-team re-checks facts |
| Engine fails to install or run on Windows in Phase 2/3 | none | engine choice labelled provisional; install-check in Phase 2 with owner approval (A11 debt row) |
| OneDrive or cloud sync of `.env`/logs | F-04 | repo under `C:\Users\jonat\code` (outside OneDrive, verified by path); `logs/` and `data/` git-ignored |

Not applicable this phase (no orders): F-07 (R-25–27; R-26 broker support and R-27 iNAV data are matrix criteria only), F-08 (R-28–30), F-10 (R-32), F-11 (R-33), F-12 (R-34), F-13 (R-35), F-14–F-16 (R-36–38), F-17 (R-39 is relevant to A7 scoring only), F-18 (tax), F-19 (R-40: no orders; the restricted list starts empty and is owner-maintained, no employer-policy check, RETRO 2026-11-24), and R-15/R-16 (order-rate self-halt and paging; there are no orders and no paging channel yet; the request-rate ceiling and capped backoff are the analogue).

## 6. Compliance items touched

| ID | How this phase touches it |
|---|---|
| C-6 | Official APIs only (Alpaca REST/WebSocket, SEC EDGAR). No scraping. A7 records each broker's automation terms |
| C-7 | EDGAR polled every 60 s by default under a ≤1 req/s ceiling with the owner's User-Agent; Alpaca rate and connection limits respected (A2); news stored for personal use only, only metadata + headline, never redistributed; `logs/` git-ignored and never pushed; evidence holds counts, not content |
| C-10 | Append-only, hash-chained, anchored log. Spike logs are development data; the 7-year retention policy applies from Phase 3 (RETRO debt via A11) |
| C-3 | Not exercised (no orders). The restricted-list mechanism is kept (C-3, invariant 18); the list starts empty and is owner-maintained, with no employer-policy check (RETRO 2026-11-24). Kernel enforcement arrives in Phase 3 |
| C-1, C-2, C-4, C-8, C-11 | Not exercised (no orders); A7 records broker PDT/settlement/options handling as matrix facts |
| C-9 | Unchanged: household only |

## 7. Risks, assumptions, "Do not"

**Risks**
- R1: Alpaca's free tier may limit news history, WebSocket connections or storage, so the real terms could differ from NEWS_AND_DATA_STACK. Mitigation: A2 runs before B5–B8 bind URLs and limits; B* code reads limits from config.
- R2: Primary sources for some verify items (e.g. Barber & Odean, the 2009 momentum crash) may be paywalled. Mitigation: cite the abstract/DOI page plus a reputable secondary source and mark the verdict "confirmed via abstract".
- R3: STRATEGY_ENCYCLOPEDIA is large (~60 rows). A3 may need several sessions; it parallelises by family.
- R4: Robinhood Agentic Trading and Schwab Trader API documentation may need a login. Record what is public and mark the rest `unverified (login required)`; do not create accounts.
- R5: A single 35-minute run may hit a quiet news window. The startup REST news GET proves the news path on real payloads; the stream may then log a heartbeat. Red-team may still ask for a second run.
- R6: Docs-only engine evidence may be wrong about Windows support. Mitigation: provisional label, robustness check, Phase 2 install-check with owner approval.
- R7: A10 depends on the live spike (B11), so the matrix cannot close before the spike. Mitigation: A6/A7 proceed in parallel; only data scoring waits.

**Assumptions**

| # | Assumption | Status |
|---|---|---|
| AS-1 | Python 3.12.10 in `.venv`; only pip installed so far | verified (`.venv\Scripts\python.exe --version`; site-packages listing) |
| AS-2 | No source code exists yet; no `docs/phases/` folders before this one | verified (repo listing) |
| AS-3 | `.env` exists and is git-ignored; variable names per TONIGHT.md step 7 | verified that the file exists and is listed in `.gitignore`; contents not read (by design). Owner confirms in O1 |
| AS-4 | A pre-push hook restricts remotes to github.com/jon-swill | verified (`.git/hooks/pre-push` present) |
| AS-5 | Paper REST host is `https://paper-api.alpaca.markets`; data REST news is `https://data.alpaca.markets/v1beta1/news`; streams are `wss://stream.data.alpaca.markets/v2/iex` and `.../v1beta1/news` | unverified, confirmed in A2 before B5 |
| AS-6 | The EDGAR latest-filings Atom feed for 8-K (`browse-edgar?action=getcurrent&type=8-K&output=atom`) is still served and allowed for automated polling at a 60 s cadence | unverified, A2 |
| AS-7 | Free-tier Alpaca news is available over WebSocket and REST on a paper account | unverified, A2 |
| AS-8 | Libraries: `httpx`, `websockets`, `pydantic` v2, `defusedxml`, stdlib `tomllib` and `zoneinfo` (plus `tzdata` on Windows); dev: `pytest`, `ruff`, `mypy`, `pip-tools`; latest stable at install, exact pins with hashes. Installing from PyPI is free and allowed. No engine or trading SDK packages | unverified (versions picked in B1) |
| AS-9 | Watchlist is final: `SPY, QQQ, IWM, AAPL, MSFT` (O2) | verified (owner decision 2026-11-24, RETRO) |
| AS-10 | Limits and rules (bucket sizes as rules, hard limits, $X/Y%/N minutes, budget) go in `docs/phases/phase_0/decisions.md`, in git. Balances, holdings and account numbers go in the git-ignored `private/` folder | verified (owner decision 2026-11-24); `private/` added to `.gitignore` |
| AS-11 | Advisor statements, balances, holdings and account numbers never enter git | verified (owner confirmed 2026-11-24) |
| AS-12 | The owner starts the live 35-minute run (B10); the agent prepares the commands and writes evidence from the output | verified (owner agreed 2026-11-24) |
| AS-13 | Verify-marker closure: the agent may add citations and remove a marker when a claim is confirmed unchanged, and may fix dead links and reword the two explanatory mentions without changing meaning, **one commit per closed marker or fixed link, with its source URL in the commit message**. Any change in meaning and every new entry goes through D4 for owner approval | verified (owner agreed 2026-11-24; link fixes and rewording added in revision 2 per owner instruction to apply the eval fixes) |
| AS-14 | Spike code is throwaway and must not be imported by Phase 3; `--allow-closed` is removed (off-hours behaviour lives in tests only) | verified (owner decision 2026-11-24) |
| AS-15 | Phase 0 signed off; only O3 carried as debt, due before the Phase 2 phase-plan; O4 and O5 are debt due before the Phase 6 real-money gate; employer-policy check removed | verified (owner decision 2026-11-24, RETRO rows) |

**Do not**
- Do not import, reference or call any order-placing, cancelling, replacing or position-closing endpoint, method or SDK, including on paper (CLAUDE.md hard stop; Phase 3 gate not passed).
- Do not install or import any execution/backtest engine package this phase.
- Do not use live (non-paper) keys or endpoints, ever, until the Phase 6 gate.
- Do not push, create remotes, change GitHub settings, create cloud resources, sign up for paid services or spend money. No new broker or data accounts, no data-plan purchase.
- Do not change hard limits, risk modes or the kernel (none exist; none are created).
- Do not read, print, echo, log or paste secrets or the SEC contact address. `.env` is read only by `family_desk_spike/config.py` at runtime (the secret scanner goes through it); tests use `FakeEnv`.
- Do not commit `logs/`, `data/`, `private/`, advisor statements, balances, holdings, account numbers or news text. The agent does not read `private/`.
- Do not scrape websites; official APIs/feeds only. Do not exceed 1 EDGAR request per second.
- Do not use market data or news for anything but this household's personal use.
- Do not send external text to an LLM or treat it as instructions.
- Do not add a CLI flag that bypasses the run-window, paper or config checks.
- Do not import `family_desk_spike` from any later-phase code.
- Do not reopen RETRO closed decisions (Alpaca paper, live broker fluid, no X/Grok/paid news, options manual only, no margin/shorting, Windows PC only).
- Do not reference HSS repositories, organisations, accounts, Bedrock or HSS skills.
- Do not use `unittest.mock`; use fakes. Do not weaken a test to make it pass.
- Do not start Phase 2 without the owner's sign-off in RETRO.
