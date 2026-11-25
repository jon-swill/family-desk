# Phase 1 tasks

Plan: `docs/phases/phase_1/phase_1_plan.md` (revision 2, after `phase_1_eval.md`). Update status to `☑ done` with proof (commit hash + check output) as each task closes. Phase 0 signed off 2026-11-24 (RETRO); O3 is debt due before the Phase 2 phase-plan. Advisor statements (O4) and CPA booking (O5) are RETRO debt due before the Phase 6 real-money gate and are not tracked here. The employer-policy check was removed by the owner.

| ID | Task | Owner | Depends on | Status | Proof | Notes |
|---|---|---|---|---|---|---|
| A1 | Verify 7 FAILURE_LIBRARY verify-marked entries (incl. F-15 `[verify: ...]`); reword lines 3 and 97; fix dead links (F-14 SSRN first); start verification log | agent | none | ☐ not started | | 7 marker rows + link rows; one commit + URL each; `\[verify` search clean |
| A2 | Verify Alpaca free-tier terms (incl. delayed SIP), endpoint URLs (incl. data REST news), EDGAR terms (SEC page replaces dev.to), 4 data-stack verify rows | agent | none | ☐ not started | | Log rows; one commit + URL per marker; URLs recorded |
| A3 | Re-verify every STRATEGY_ENCYCLOPEDIA Evidence cell, add year and decay note | agent | none | ☐ not started | | Zero uncited Evidence cells remain |
| A4 | Research retail-algo post-mortems and broker-API incidents; write proposals | agent | none | ☐ not started | | Sourced entry per broker, or documented null search |
| A5 | Freeze matrix criteria and weights (engines, brokers, data sources) and worst-plausible scores before scoring | agent | none | ☐ not started | | Dated criteria/weights committed before A6/A7/A10 |
| A6 | Score NautilusTrader, LEAN, custom-on-vectorbt (docs only, no installs) | agent | A5 | ☐ not started | | Every engine cell cited or marked unverified |
| A7 | Score Alpaca, Schwab Trader API, Robinhood Agentic, IBKR (incl. read-only key availability) | agent | A5, A2, A4 | ☐ not started | | Every broker cell cited or marked unverified |
| A10 | Score data sources (IEX, delayed SIP, paid SIP ranked only, news options, iNAV) with spike measurements | agent | A5, A2, B11 | ☐ not started | | Every data cell cited, measured or marked unverified |
| A8 | Totals, unverified share, robustness check, ±50% sensitivity, provisional engine pick, broker and data rankings, dissent | agent | A6, A7, A10 | ☐ not started | | Unverified, robustness and sensitivity tables present |
| O6 | Approve or reject each proposed failure entry | owner | A4, B11 | ☐ not started | | Decision column has no blanks |
| A9 | Merge approved entries into FAILURE_LIBRARY with next IDs | agent | O6 | ☐ not started | | Approved entries present with final F/R IDs |
| A11 | Write RETRO debt rows: C-10 retention, secrets manager, key rotation date, engine install-check, spike package deletion, config signing | agent | O1 | ☐ not started | | Rows present in RETRO Known debt |
| B1 | pyproject (package `family_desk_spike`), hashed lock files, ruff/mypy/pytest; update CLAUDE.md gates | agent | none | ☐ not started | | Four gate commands green on skeleton |
| B2 | Guard test: no order paths, trading/engine SDKs, non-GET anywhere in `src/`, outside imports of `family_desk_spike`, mocks | agent | B1 | ☐ not started | | Passes; planted violation shown failing |
| B3 | Typed config, masked secrets, assert_paper, config-hash, version and clean-tree startup checks | agent | B1 | ☐ not started | | All refusal cases tested and green |
| B4 | Append-only hash-chained JSONL log; verify_log with `seq_last`, `head_hash`, `--expect-head` | agent | B1 | ☐ not started | | Tamper, gap, anchored-truncation, redaction tests green |
| B5 | Models, parsers, GET-only (host, path) allowlist adapter, startup REST news GET | agent | B2, B3, B4, A2 | ☐ not started | | FakeHttp tests green incl. refusals; guard still green |
| B6 | IEX quote stream: ack, reconnect, backoff, staleness, stall detection, rate/spread stats | agent | B2, B3, B4, A2 | ☐ not started | | FakeWebSocket/FakeClock tests green |
| B7 | News stream: ack, dedupe, metadata-only storage, text as data | agent | B2, B3, B4, A2 | ☐ not started | | FakeWebSocket tests green |
| B8 | EDGAR 8-K poller: 60 s cadence under ≤1 rps, UA, defusedxml, pre-filter/match counts, CIK padding, dedupe, backoff | agent | B2, B3, B4, A2 | ☐ not started | | 1,000-poll FakeClock rate proof; CIK padding test |
| B9 | Spike runner, run-window check (no bypass flag), Windows-safe shutdown, offline end-to-end test | agent | B5, B6, B7, B8 | ☐ not started | | e2e, run-window and shutdown tests and all quality gates green |
| B12 | Secret scanner (full values, found/not found only) | agent | B3 | ☐ not started | | `test_secret_scan.py` green |
| O1 | Confirm paper keys regenerated; `.env` set; check-ignore passes; give regeneration date | owner | none | ☐ not started | | Owner confirms without pasting any values |
| O2 | Watchlist final: SPY, QQQ, IWM, AAPL, MSFT | owner | none | ☑ done | RETRO row 2026-11-24 | B3 commits it in `config/spike.toml` with its hash |
| B10 | Live 35-minute session run (start ≥ 10:00 ET, end ≤ close − 30 min), verify_log, wrong-host refusal demo | owner | B9, O1 | ☐ not started | | verify_log prints chain OK, seq_last, head_hash, counts |
| B11 | Write spike evidence (counts, rates, anchor only); `pytest -rA` capture; secret scan; add new failures | agent | B10, B12 | ☐ not started | | Evidence committed; scan prints not found everywhere |
| O3 | Phase 0 decisions table in `docs/phases/phase_0/decisions.md` | owner | none | ☐ not started | | Limits and rules only; no balances; RETRO debt, due before Phase 2 phase-plan |
| G1 | phase-gate with failure-check on delivered work; re-run verify_log `--expect-head` | agent | A8, A9, A11, B11 | ☐ not started | | Summary written; ADVANCE or HOLD recorded |
| G2 | red-team in a fresh session | owner | G1 | ☐ not started | | Redteam file with go/no-go; findings resolved |
| G3 | Owner sign-off row in RETRO (provisional engine choice, spike) | owner | G2 | ☐ not started | | Dated RETRO sign-off row exists |
