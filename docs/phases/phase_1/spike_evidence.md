# Phase 1 spike evidence (D18)

Written 2026-11-25 by the agent (B11) from the run's summary record and `verify_log` output only: counts, rates and the anchor. No news text, no secrets, no personal values. The log itself (`logs/spike/2026-11-25.jsonl`, 587 MB) is git-ignored and stays on the owner's PC.

## Verdict on G-9: **FAIL, rerun required (EDGAR)**

The run proved account, positions, both stream acks, quotes for all 5 symbols and the REST news path. But the EDGAR poller died on its first poll, so no EDGAR cycle completed and the pre-filter entry count is missing for every cycle. G-9's rerun rule ("the EDGAR pre-filter count is 0 in every cycle") applies. The criterion is not relaxed. The fix is commit `1e9f906`. The owner must do a new run in another session (see "Rerun" below), and this file gets a "Run 2" section from that run's output.

| G-9 item | Result | Field |
|---|---|---|
| ≥30 min, market open, start ≥ 10:00 ET, end ≤ next_close − 30 min | **pass**: started 10:09:35 ET, ran 35 min to 10:44:39 ET; `next_close` 16:00 ET; run-window `refused: []` | records `clock`, `run_window` (seq 6–7) |
| Account read | **pass**: status ACTIVE, USD, trading_blocked false, account_blocked false, pattern_day_trader null (field absent, logged as `schema_drift`, see P-23) | seq 8–9 |
| Positions include the O7 1-share SPY position, parsed into a `Position` | **pass**: count 1, SPY, qty 1, long, us_equity | seq 10 |
| Subscription ack, quote stream | **pass**: quotes AAPL, IWM, MSFT, QQQ, SPY | seq 23 |
| Subscription ack, news stream | **pass**: news SPY, QQQ, IWM, AAPL, MSFT | seq 28 |
| Quotes for all 5 symbols with update rate and spread | **pass**: table below | summary `quotes.per_symbol` |
| ≥1 watchlist item from the startup REST news GET | **pass**: 6 items, 6 on the watchlist | summary `news_rest_items`, `news_rest_watchlist` |
| Stream news or a logged "no news" heartbeat | **pass as written, but unproven under P-02**: 0 stream items, 34 heartbeats, 0 disconnects. REST shows 0 watchlist items in the window (19 non-watchlist), so nothing was missed, but the stream never had a positive case (see News) | summary `news_stream` |
| EDGAR cycles with pre-filter entry count > 0 | **FAIL**: cycles 1, ok_cycles 0, pre_filter min/max `null`; poller died (see below) | summary `edgar`; record `error` stage `edgar` (seq 1535454) |
| EDGAR post-filter AAPL/MSFT match count, labelled "feed live + filter tested offline" | **not shown** (no completed cycle) | summary `edgar.matches_total` 0 |
| Measured EDGAR request rate ≤ 1/s | **pass but vacuous**: 1 request in total (company_tickers.json), max 1 in any 1 s, `mean_rps` null (needs ≥ 2 requests) | summary `edgar` |
| `verify_log` prints chain OK, seq_last, head_hash | **pass**: below | |

## Run identity

| Field | Value |
|---|---|
| Command | `python -m family_desk_spike --duration-min 35` |
| Date | Wed 2026-11-25 (regular session) |
| Commit | `7c8205edd1694cb8678ff0b497c9ebdbf27e3323` (B10 schema-drift fix) |
| Config sha256 | `6954a056c7b97aa1f085e0cba5bbd3fb700ddd331b03ec476b667deec2eb0616` |
| Package version | 0.1.0 |
| Start / end (log time, UTC) | 15:09:35.42Z / 15:44:39.97Z |
| Earlier attempt in the same file | seq 1–4, 10:01 ET, commit `55fbcbf`: stopped after the run-window check because `/v2/account` lacked `pattern_day_trader` (P-23); fixed in `7c8205e`. Its summary record has no streams |

## verify_log (anchor)

`python -m family_desk_spike.verify_log logs/spike/2026-11-25.jsonl`, run by the agent 2026-11-25:

```
chain OK
seq_last=1535455
head_hash=33ef7973c568a40260ee1a3493bb969fc9df2d0f0574d46e7ca522c4ca37c2ff
records=1535455
count[account]=1
count[clock]=2
count[edgar.cik_map]=1
count[error]=1
count[iex.ack]=1
count[iex.event]=4
count[news.ack]=1
count[news.event]=4
count[news.heartbeat]=34
count[news.rest]=6
count[positions]=1
count[quote]=1535392
count[run_window]=2
count[schema_drift]=1
count[startup]=2
count[summary]=2
```

phase-gate re-runs it with `--expect-head 33ef7973c568a40260ee1a3493bb969fc9df2d0f0574d46e7ca522c4ca37c2ff`.

## Quotes (IEX, free plan)

From the summary record. Skew = local receive time − exchange timestamp, **not corrected** for the PC clock offset (see "Clock" below).

| Symbol | Quotes | Updates / min | Spread median (bps) | Spread p95 (bps) | Max gap (s) | Skew median (ms) | Skew p95 (ms) |
|---|---|---|---|---|---|---|---|
| SPY | 428,862 | 12,250.83 | 1.139 | 4.860 | 2.188 | −509.594 | −466.015 |
| QQQ | 311,142 | 8,888.05 | 4.733 | 9.265 | 2.172 | −511.952 | −472.228 |
| IWM | 616,399 | 17,608.00 | 0.764 | 1.146 | 2.313 | −509.515 | −469.182 |
| AAPL | 99,506 | 2,842.48 | 2.857 | 39.651 | 2.984 | −508.647 | −459.164 |
| MSFT | 79,483 | 2,270.50 | 5.377 | 80.508 | 3.891 | −511.418 | −464.146 |

Stale events: none (threshold 60 s). Unexpected symbols: 0. IEX stream: 1 connect, 0 disconnects, 0 reconnects, 0 errors, 455,025 frames, 0 malformed. News stream: 1 connect, 0 disconnects, 3 frames, 0 malformed.

## Clock (explains the −510 ms skew)

A negative skew means the PC's clock reads earlier than the exchange's. The skew is the same on all 5 symbols, which points to the PC clock rather than the feed. Checked by the agent on 2026-11-25, about 30 minutes after the run:

- `w32tm /query /status`: `Leap Indicator: 3 (not synchronized)`, `Source: Local CMOS Clock`, `Last Successful Sync Time: unspecified`. The Windows Time service is running but has never synced.
- `w32tm /stripchart` against time.windows.com: offset +0.513 to +0.534 s (5 samples); against time.cloudflare.com: +0.518 to +0.523 s. The PC clock is about 0.52 s slow.
- Cross-check inside the log: Alpaca's `/v2/clock` timestamp was 0.47 s later than our receive time (seq 6).

Corrected for a +0.52 s offset, the median receive delay is about 8 to 12 ms after the exchange timestamp. This is an estimate: the offset was measured after the run, not during it. Fixing the clock is an owner action (admin PowerShell; see the hand-off). New failure proposal **P-25**.

## News

The owner asked (2026-11-25) for the stream's 0 items to be treated as a suspected P-02 failure, not a quiet market. The checks below were made after the run with read-only REST GETs from the spike's own client (metadata only; no headline text printed or stored).

**Startup REST GET** (24 h lookback, limit 50): 6 items, all 6 tagged with a watchlist symbol (AAPL 2, MSFT 4), all with source `fiscal.ai`, newest created 14:31:27Z (09:31 ET).

**REST count for the run window** (explicit `start`/`end`, `sort=asc`, every page fetched):

| Window | Filter | Items | Pages | Created in window | Tagged with a watchlist symbol | Sources |
|---|---|---|---|---|---|---|
| Owner's window, 10:12–10:47 ET (15:12–15:47Z) | watchlist (5 symbols) | 0 | 1 | 0 | 0 | none |
| Owner's window | no symbol filter | 19 | 1 | 19 | 0 | `fiscal.ai` 19 |
| Run window, 10:09:36–10:44:39 ET | watchlist | 0 | 1 | 0 | 0 | none |
| Run window | no symbol filter | 19 | 1 | 19 | 0 | `fiscal.ai` 19 |

**Subscribe message and ack.** The client sends `{"action":"subscribe","news":["SPY","QQQ","IWM","AAPL","MSFT"]}` (`src/family_desk_spike/data/news_stream.py`, `subscribe={"news": list(monitor.symbols)}`), not `"*"`. The logged ack (seq 28) is `{"T":"subscription","news":["SPY","QQQ","IWM","AAPL","MSFT"]}`, so the server accepted the 5-symbol list. Stream counters: 1 connect, 0 disconnects, 0 errors, 3 frames (connected, authenticated, subscription), 0 news frames.

**What Alpaca's documentation says** (all accessed 2026-11-25):
- The real-time news page gives the stream URL `wss://stream.data.alpaca.markets/v1beta1/news`. Its example subscribes with `{"action":"subscribe","news":["*"]}` and shows the ack `[{"T":"subscription","news":["*"]}]`. It says nothing about which plans include the news stream or about any delay ([Alpaca: Real-time news](https://docs.alpaca.markets/us/docs/streaming-real-time-news), page updated 2026-11-24).
- The market-data overview describes the Basic (free) plan as "limited real-time data: for equities only the IEX exchange". Its plan tables have no news row ([Alpaca: About market data API](https://docs.alpaca.markets/us/docs/about-market-data-api), updated 2026-11-24). The FAQ doesn't cover news either ([Alpaca: Market data FAQ](https://docs.alpaca.markets/us/docs/market-data-faq)).
- REST news: the default `end` is "the current time if the user has a real-time access for the feed, otherwise 15 minutes before the current time". A 403 means "the subscription does not cover the requested data". The page doesn't say whether `start`/`end` filter on `created_at` or `updated_at`; sorting is "by updated date" ([Alpaca: News reference](https://docs.alpaca.markets/us/reference/news-3), updated 2026-05-27).
- None of the five pages documents an error code for a plan that isn't entitled to the news stream. So **whether the free plan streams news in real time, with a delay, or at all is not stated by Alpaca.** NEWS_AND_DATA_STACK had already marked this unverifiable (A2).

**Probe of this key's news delay.** A REST GET with no `end` and no symbol filter (newest first, 16:53:58Z) returned 10 items, the newest 21.1 minutes old. At the roughly 0.5 items/min seen above, an empty last 15 minutes is unlikely. The result fits the documented 15-minute default `end` for keys without real-time access. It suggests this key's REST news is delayed by at least 15 minutes; it doesn't prove it.

**Conclusion.** REST shows **no watchlist news created in the window**, while the same API returned 19 non-watchlist items in it. So the REST news path was live, and REST agrees with the stream's 0. That rules out "REST had items the stream missed". It **does not prove the stream delivers**: the run never had a positive case on the stream, and only the subscription ack and the heartbeats (which show the socket is open) support it. Under P-02 / R-42, the stream's silence in run 1 is **unproven, not healthy**. The cross-check added in `785c383` would have recorded run 1 as `no_positive_case`, not `ok`.

**Check added (commit `785c383`).** Every 5 minutes and once at shutdown, the runner compares REST watchlist items created since the stream started (up to now minus a 16-minute grace, to allow for the REST delay above) with the ids the stream delivered. It logs `news.cross_check` with a verdict: `ok`, `partial`, `stall` (REST has items, the stream delivered none) or `no_positive_case`. On `stall` or `partial` it also logs `news.stall` (ids only) and prints a `STALL:` line. The summary reports `news_stream.cross_check`. Limit: with a 16-minute grace, a 35-minute run only judges items created in its first ~19 minutes.

**Owner option for run 2: decided 2026-11-25 and done in `6fe8044`.** To give the stream a real positive case, subscribe with `"*"` (the documented example) and count unfiltered items as liveness, keeping only watchlist items' metadata. That is the same pattern as EDGAR's pre-filter count. It changes what the stream receives, so it is the owner's call.

## EDGAR: what failed and the fix

- The CIK map was fetched from SEC (`company_tickers.json`): AAPL `0000320193` unique, MSFT `0000789019` unique, 1 ticker per CIK.
- The first `getcurrent` poll ran right after that request. The token bucket (1 req/s, capacity 1) returned a wait just under 1 s. On Windows an asyncio timer can fire up to one clock tick (~15.6 ms) early, so after the sleep the bucket held about 0.98 of a token and `take()` raised `RuntimeError('no token available; call wait_time first')`. That exception is not an `OSError`, so the poller task died.
- The runner reported a failed task only at shutdown, so the `error` record (seq 1535454) is stamped 15:44:36Z, 35 minutes after the failure. Nothing showed the dead poller during the run, which is the "silent equals fine" pattern of P-02.
- Fix, commit `1e9f906`: the token wait re-checks the bucket after every sleep, floors each sleep at 20 ms so it cannot spin, and gives up without sending when the run is stopping. A dead source task is now logged and printed when it dies, appears in the summary as `task_failures`, and sets exit code 4. Regression tests: an early-waking timer (50 back-to-back requests, never more than 1 in any 1 s, no exception); a stop during the token wait sends nothing; an end-to-end run where the EDGAR task dies logs the error while the streams are still running. The early-wake reproduction raises the same `RuntimeError` on the pre-fix code, and the end-to-end test fails on the old runner (exit 0, expected 4).
- New failure proposal **P-24**.

## Startup refusal demo (G-8)

Run by the agent 2026-11-25 at commit `1e9f906`, wrong host substituted in `config/spike.toml`, before any network call:

```
version=0.1.0
commit=1e9f9067ac3b500b9b3d7fa5a5bcdfea6b71e71e
config_sha256=829753a912267d0c6ec250433683cdb215941c7cbf0383e095138f497a46c0c9
startup REFUSED codes=host,config_hash,dirty_tree
  [host] trading_base_url is not exactly https://paper-api.alpaca.markets
  [config_hash] config sha256 does not match committed hash
  [dirty_tree] 1 uncommitted change(s) under src/ or config/
exit=2
```

Then `git checkout -- config`; `git status --porcelain -- src config` printed nothing.

## Planted-violation demo (G-7)

From B2 (commit `ede8078`): planting `src/family_desk_spike/_planted.py` with an order path made `test_real_repo_is_clean` fail ("order endpoint path"). With the file removed, all 27 tests passed. Recorded in `phase_1_tasks.md`.

## Tests and secret scan (G-6, G-10)

- `python -m pytest -rA > logs/pytest_output.txt`: exit 0, `246 passed` at commit `1e9f906`.
- `python -m family_desk_spike.tools.secret_scan`, run after the pytest capture:

```
APCA_API_KEY_ID @ docs: not found
APCA_API_KEY_ID @ git_history: not found
APCA_API_KEY_ID @ logs: not found
APCA_API_KEY_ID @ tracked_files: not found
APCA_API_SECRET_KEY @ docs: not found
APCA_API_SECRET_KEY @ git_history: not found
APCA_API_SECRET_KEY @ logs: not found
APCA_API_SECRET_KEY @ tracked_files: not found
SEC_USER_AGENT_EMAIL @ docs: not found
SEC_USER_AGENT_EMAIL @ git_history: not found
SEC_USER_AGENT_EMAIL @ logs: not found
SEC_USER_AGENT_EMAIL @ tracked_files: not found
RESULT: all not found
```

## New failure patterns added to D4

- **P-24** Background worker dies silently; its rate limiter assumes the timer wakes on time.
- **P-25** Host clock not synchronised, so data-age and skew checks are off by the offset.

Both are `proposed`; O6 decides them.

## Rerun (owner, B10 run 2)

Valid windows: Fri 27 Nov is a half-day (close 13:00 ET), so start between 10:00 and 11:55 ET. From Mon 30 Nov, start between 10:00 and 14:55 ET. Sync the PC clock first (hand-off), then:

```powershell
git status --porcelain -- src config      # must print nothing
python -m family_desk_spike --duration-min 35
python -m family_desk_spike.verify_log logs\spike\<YYYY-MM-DD>.jsonl
```

Pass needs `edgar cycles` ≈ 35 with `pre_filter_min` > 0, `mean_rps` a number ≤ 1, `news_rest_watchlist` ≥ 1, `news_stream.delivery_proven` true (the stream subscribes to `"*"` since `6fe8044`, owner decision), a news cross-check verdict, and no `ERROR: source task` or `STALL:` line. Paste both outputs to the agent, which adds a "Run 2" section here and updates the anchor.
