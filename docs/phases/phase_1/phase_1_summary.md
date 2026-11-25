# Phase 1 summary (phase-gate G1, 2026-11-25)

**Verdict: HOLD.** The full gate record is in `phase_1_eval.md` ("Phase gate (G1), 2026-11-25"). Commit at the gate: `b8752b2`. Gates: ruff, format, `mypy --strict` and pytest (259 passed) are all green.

## What was built

**Track A: research (documents only)**
- `docs/research/verification_log.md`: every verify marker resolved (G-2: 0 left); dead links fixed; A10 source rows.
- `docs/research/FAILURE_LIBRARY.md`: primary sources for F-05..F-17; new section E with F-20..F-25 / R-41..R-46 (owner-approved P-01..P-06).
- `docs/research/failure_library_proposals.md`: P-07..P-27 awaiting the owner (O6). The spike added P-23 (schema drift), P-24 (silent worker death), P-25 (unsynced host clock). The gate added P-26 (fake/real error mismatch) and P-27 (egress allowlist covers HTTP only).
- `docs/research/STRATEGY_ENCYCLOPEDIA.md`: 57 Evidence cells, each cited or marked `unverified (reason)`.
- `docs/research/decision_matrix.md`: criteria frozen before scoring; engines, brokers and data sources scored; totals, robustness, sensitivity and dissent (§9, computed by script).
  - **Engine:** no recommendation. Base NautilusTrader 332 > LEAN 310 > vectorbt 283 (near-tie). Neither packaged engine documents a kernel choke point in front of every order path (E-1, a knock-out), so at worst-plausible scores both are excluded and the winner changes.
  - **Brokers:** Alpaca rank 1 in both base and robustness. This decides nothing (RETRO: live broker stays open).
  - **Price feeds:** free IEX rank 1, provisional (two single-weight moves put paid SIP first). No documented free iNAV source for SPY, QQQ, IWM (R-27).
  - **Company events:** EDGAR rank 1 in both.

**Track B: read-only spike (`src/family_desk_spike/`, throwaway, import-guarded)**
- Startup self-check with reason codes (paper host, paper flag, config hash, version, clean tree, UA, keys); refusal before any network call.
- One GET-only (host, path) allowlisted HTTP client for Alpaca and SEC; guard test over code and lock files; no order path anywhere.
- IEX quote stream, Alpaca news stream (with a REST cross-check since `785c383`), startup REST news GET, EDGAR 8-K poller under a ≤1 req/s token bucket, AAPL/MSFT CIK filter with cardinality.
- Append-only hash-chained JSONL log with an external anchor (`verify_log --expect-head`); redaction; full-value secret scanner.

## How to run it

From the repo root with the venv active:
```powershell
python -m family_desk_spike --duration-min 35        # refuses outside 10:00 ET .. next_close - 30 min
python -m family_desk_spike.verify_log logs\spike\<YYYY-MM-DD>.jsonl [--expect-head <hash>]
python -m family_desk_spike.tools.secret_scan
```

## Live run 1 (2026-11-25, `7c8205e`): what it showed

Evidence: `spike_evidence.md`. Anchor: seq_last 1535455, head_hash `33ef7973c568a40260ee1a3493bb969fc9df2d0f0574d46e7ca522c4ca37c2ff` (re-verified by the gate).
- **Passed:** account; the O7 1-share SPY position parsed from a real payload; subscription acks on both streams; 1.54 million IEX quotes on all 5 symbols with no stale events; 6 REST news items, all on the watchlist.
- **Failed: EDGAR.** The poller died on its first poll: a Windows asyncio timer woke early and the token bucket raised. The runner only reported it at shutdown. G-9's rerun rule applies.
- **News stream:** 0 items in 35 minutes. REST shows 0 watchlist items in that window but 19 other items, so nothing was missed. The stream still never had a positive case: under P-02 its silence is unproven, not healthy.
- **Clock:** −510 ms quote skew on every symbol. The PC's Windows Time service has never synced and the clock runs about 0.52 s slow (`w32tm`; two NTP servers).

## Fixes made in this session (before the gate)

| Commit | Fix |
|---|---|
| `1e9f906` | Token wait re-checks after every sleep (floored at 20 ms) and gives up on stop; a source task that raises is logged at once, printed, and exits 4 |
| `383adf8` | httpx and websockets errors mapped to `OSError` subclasses at the I/O edge, so EDGAR and the streams back off instead of dying (tests drive the real adapters) |
| `785c383` | News stream cross-checked against REST every 5 min and at shutdown; `news.stall` when REST has watchlist items the stream never delivered; `no_positive_case` instead of "ok" when there is nothing to compare |
| `e032bb4` | A source task that ends before stop without raising (e.g. a stream stopped by a fatal 402) is reported as an error |

## Known issues (open)

- G-9: B10 run 2 needed. The clock is unsynced (owner fix, admin shell).
- R-13: the clean-tree check excludes `pyproject.toml` and the lock files; stream URLs are not asserted (P-27).
- R-21: redaction runs after exception-text truncation; console lines are not redacted (theoretical).
- R-23: errors in the startup reads (positions, news REST, CIK map) crash the run before the streams start. This is loud, but the positions parse error text could echo values (P-23 exposure).
- R-24: staleness is measured as the gap between arrivals, not data age (P-12, P-25).
- R-45: single-ticker trust CIKs classify as `unique`; only the pinned AAPL/MSFT list keeps them out of the filter.
- The free plan's news-stream entitlement and delay are not stated by Alpaca. This key's REST news looks delayed by at least 15 minutes.

## What Phase 2 inherits

- The engine choice is open: either the owner moves it to a Phase 2 install-check (needs explicit approval; engines bundle order adapters), or E-1 evidence is verified first.
- RETRO debt from A11: secrets manager, 90-day key rotation (due 2027-02-22), C-10 retention, config signing, spike deletion at Phase 3 start, clock sync.
- Rules to carry into the Phase 2 spec once O6 decides them: supervised workers (P-24), clock check at startup (P-25), declared adapter errors with shared contract tests (P-26), one egress allowlist for every transport (P-27), boundary models that require only decision fields (P-23).
- Nothing from `family_desk_spike` may be imported by later phases (R-43).
