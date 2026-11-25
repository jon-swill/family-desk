# Phase 1 spike evidence (D18)

Written 2026-11-25 by the agent (B11) from the run's summary record and `verify_log` output only: counts, rates and the anchor. No news text, no secrets, no personal values. The log itself (`logs/spike/2026-11-25.jsonl`, 587 MB) is git-ignored and stays on the owner's PC.

## Verdict on G-9: **FAIL, rerun required (EDGAR)**

A dry run on the afternoon of 25 Nov (section "Dry run" below) is not run 2 and doesn't change this verdict.

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

**Superseded 2026-11-25 by the dry run** (below), which appended to the same file. Run 1's last record (seq 1535455) still carries `33ef7973…c2ff` inside the verified chain, but the file's head is now `0248516c…6890` at seq 2378936, so `--expect-head 33ef…` now fails by design. Use the dry-run anchor.

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

## Dry run, 2026-11-25 (not run 2; G-9 still needs run 2)

The owner ran the spike once more on 25 Nov to try the `"*"` news subscription and the clock sync before run 2. It is **not** the G-9 rerun and doesn't change the G-9 verdict. Written by the agent from the log records and the Windows event log only (counts, times, settings; no news text, no secrets).

### Identity and anchor

| Field | Value |
|---|---|
| Command | `python -m family_desk_spike --duration-min 35` |
| Commit / config sha256 | `96575405770657e8fad0257641a294b443f3ad9f` / `6954a056…0616` (same config as run 1) |
| Log | `logs/spike/2026-11-25.jsonl`, appended after run 1: seq 1535456–2378936 |
| Started (log time) | 12:21:03 ET (17:21:03.47Z); `clock` is_open true, `next_close` 16:00 ET; `run_window` refused `[]` |
| Live data until | **12:43:12 ET** (last quote received 17:43:11.94Z). Only **22.1 minutes** of the 35 were live |
| Summary written | **14:00:08 ET** (19:00:08.18Z), not 12:56 |

`python -m family_desk_spike.verify_log logs\spike\2026-11-25.jsonl`, run by the agent 2026-11-25 after the dry run:

```
chain OK
seq_last=2378936
head_hash=0248516c96948fdcad33a7d32d222d8183932289f42875b521066d7f057c6890
records=2378936
count[account]=2
count[clock]=3
count[edgar.cik_map]=2
count[edgar.cycle]=23
count[error]=1
count[iex.ack]=2
count[iex.event]=9
count[iex.staleness]=7
count[news.ack]=2
count[news.cross_check]=6
count[news.event]=9
count[news.heartbeat]=54
count[news.rest]=11
count[positions]=2
count[quote]=2378792
count[run_window]=3
count[schema_drift]=2
count[startup]=3
count[summary]=3
```

phase-gate now re-runs it with `--expect-head 0248516c96948fdcad33a7d32d222d8183932289f42875b521066d7f057c6890`.

### What worked

- Chain OK; account and positions read (1, SPY); quote ack for all 5 symbols.
- **News stream `"*"` on the free plan works.** The ack (seq 1535473) is `news: ["*"]`; the stream delivered **32 items**, so `delivery_proven` is true (none was a watchlist symbol, which the REST cross-check agrees with: 6 × `no_positive_case`, 0 missed). Startup REST: 5 items, 5 on the watchlist.
- EDGAR: every cycle ok, `pre_filter_entries` 40 in all 23 (min = max = 40), `max_requests_in_any_1s` 1, no errors, no `task_failures`.

### The cause of everything odd: the PC went into Modern Standby at 12:41

Windows System log (Kernel-Power), read by the agent:

| Local time (ET) | Event |
|---|---|
| 12:41:26 | 506 "entering Modern Standby", reason **Idle Timeout** |
| 12:43:17 | 172 "Connectivity state in standby: Disconnected", reason Adaptive Connected Standby |
| 14:00:01 | 507 "exiting Modern Standby" (battery-drain budget), then 14:00:02 exit on mouse input |

This PC only supports `Standby (S0 Low Power Idle)` (`powercfg /a`), where turning the display off *is* standby. `Turn off display after` is 1200 s (20 min) on both AC and battery, and the PC was on battery (`Win32_Battery` status 1, 59 %). The run started at 12:21, so with no input the screen went off 20 minutes later and Windows suspended the process. The network dropped at 12:43:17; the last quote arrived at 12:43:12. When the PC woke at 14:00, Python's monotonic clock (`GetTickCount64()`, which keeps counting through standby) showed the 35-minute timer long expired, so the run processed what was buffered and shut down.

### (1) EDGAR: 23 cycles, not ~35

- 22 cycles ran live, 12:21:04 to 12:42:24 ET, at a mean spacing of **60.97 s** (60 s poll + request time). The 23rd ran at 14:00:04, right after wake-up. None ran during the 77-minute standby.
- With that spacing, an uninterrupted 35-minute run gives 1 + ⌊2100 / 60.97⌋ = **35 cycles**, so the "≈ 35" pass rule is right; this run was simply live for 22 minutes.
- `mean_rps` 0.0037 is (23 − 1) requests / 5,940 s (first to last request, standby included). A normal run gives about 1/61 ≈ **0.016**. It is still ≤ 1, but here it only measures the gap.
- Not a code bug: the poller was frozen with the rest of the process and resumed cleanly.

### (2) The simultaneous stale event on every symbol

The seven `iex.staleness` records (seq 2378915–2378925) are all stamped 19:00:04.50–.51Z (14:00:04 ET), the first moment the process ran again:

| Symbol | State | `gap_s` |
|---|---|---|
| SPY, QQQ, IWM | stale | 4,612.563 |
| AAPL | stale | 4,612.641 |
| MSFT | stale | 4,612.782 |
| QQQ, AAPL | fresh | 4,612.563 / 4,612.641 |

4,612.56 s = 14:00:04.50 − 12:43:11.94 ET, the last quote before standby. On wake-up the first staleness check saw every symbol 77 minutes silent and flagged all five at once (one event each, the `stale_events: 1` per symbol). Then 8 quotes still sitting in the socket buffer were read (exchange times 12:43:12 ET), which made QQQ and AAPL fresh again, and the IEX socket reported `StreamClosedError` (the server had dropped it during standby). The stale detector worked as designed: one host-wide silence, not a feed problem.

**Bug found and fixed.** The summary's `max_gap_s` said SPY 0.5 s, IWM 0.407 s and MSFT 3.516 s although all three were silent for 4,612 s. The tracker only recorded a gap when the next quote closed it; symbols that never recovered kept their last short gap, so the summary contradicted the log (P-02, "silent equals fine"). The summary now uses `StalenessTracker.max_gaps(now)`, which includes the gap still open at the end and counts never-seen symbols from the start (`src/family_desk_spike/core/staleness.py`, `src/family_desk_spike/data/iex_stream.py`). Tests: `test_max_gaps_counts_a_gap_still_open` and a new assertion in `test_silent_stall_marks_every_symbol_stale_then_fresh`. Both fail on the previous code (`AttributeError` and a `max_gap_s` holding only AAPL) and pass now.

Side effects of the standby in this run's numbers: `updates_per_min` is divided by the 99-minute run length, not the 22.1 live minutes (live rates are roughly SPY 10,990, QQQ 8,420, IWM 14,620, AAPL 2,180, MSFT 1,900 per minute), and the 8 buffered quotes carry a +77-minute skew (too few to move the medians).

### (3) The clock offset hasn't corrected

Skew medians in this run were −474.7 to −478.1 ms (p95 −376 to −397 ms), against about −510 ms in run 1. `w32tm /stripchart /computer:time.cloudflare.com` at 14:25 ET: **+0.353 to +0.356 s** (5 samples). So the PC is still slow; the offset is shrinking slowly (≈ 0.51 s at 12:16, ≈ 0.48 s during the run, 0.35 s at 14:25).

Why, from `w32tm /query /status /verbose`, `/query /peers`, the W32Time registry and the event log (all read without admin):

1. **The 12:15 sync didn't step the clock.** The Kernel-General "system time has changed" event at 12:14:59 shows `Time Delta: 0 ms`. On a standalone PC `MaxAllowedPhaseOffset` is **1** s: an offset below that is removed by slowly changing the clock rate (slewing), not by setting the time. 0.51 s < 1 s.
2. **The slew is slow.** `UpdateInterval` is **360000** (the standalone default) with `PhaseCorrectRate` 1, so the rate is adjusted rarely and the correction takes hours (about 0.16 s in 2 h 10 min here).
3. **It won't poll again for hours.** The peer is `time.cloudflare.com,0x9`. Flag `0x1` means "use `SpecialPollInterval`", which is **32768 s** (9.1 h); `/query /peers` shows `Time Remaining: 24943.97 s` (6.9 h). With one sample the service never settles: status shows `Leap Indicator: 3 (not synchronized)` and `Last Sync Error: … no time data was available` (the standby also cut the network).
4. The earlier hand-off command `w32tm /resync /force` is wrong: `/resync` has no `/force` switch (`/rediscover`, `/nowait`, `/soft` exist).

Fix (owner, **admin** PowerShell: right-click PowerShell → Run as administrator). It polls two servers every 64 s in client mode (flag `0x8` uses `Min/MaxPollInterval`, in powers of 2 seconds, instead of the 9-hour special interval) and applies corrections far more often (`UpdateInterval` 100, the value Windows uses on domain controllers):

```powershell
w32tm /config /manualpeerlist:"time.cloudflare.com,0x8 time.windows.com,0x8" /syncfromflags:manual /update
$c = 'HKLM:\SYSTEM\CurrentControlSet\Services\W32Time\Config'
Set-ItemProperty -Path $c -Name MinPollInterval      -Value 6   -Type DWord   # 2^6 = 64 s
Set-ItemProperty -Path $c -Name MaxPollInterval      -Value 6   -Type DWord
Set-ItemProperty -Path $c -Name UpdateInterval       -Value 100 -Type DWord
Set-ItemProperty -Path $c -Name FrequencyCorrectRate -Value 2   -Type DWord
Restart-Service w32time
w32tm /resync /rediscover
w32tm /query /status          # expect Leap Indicator 0, Source time.cloudflare.com,0x8
```

Check 15 minutes later, no admin needed:

```powershell
w32tm /stripchart /computer:time.cloudflare.com /samples:5 /dataonly   # want every offset within ±0.050 s
```

If the offset is still above 0.05 s, step it once by hand (admin). The stripchart sign is the amount to add, so for `+00.3540000s`:

```powershell
Set-Date -Adjust ([TimeSpan]::FromSeconds(0.354))
```

then run the stripchart again. To undo the poll settings later: `MinPollInterval` 10, `MaxPollInterval` 15, `UpdateInterval` 360000, `FrequencyCorrectRate` 4 (today's values), then `Restart-Service w32time`.

### Before run 2: keep the PC awake

The screen-off timeout will suspend run 2 the same way. Plug the PC in, and before starting (no admin needed):

```powershell
powercfg /change monitor-timeout-ac 0      # never turn the display off on AC
powercfg /change standby-timeout-ac 0      # already 0 on AC today
```

Afterwards restore the display timeout with `powercfg /change monitor-timeout-ac 20` (today's value). The spike itself doesn't detect a host suspend; candidate failure pattern **P-28** (below and in `failure_library_proposals.md`).

### New failure proposal

- **P-28** Host suspend freezes the process; timers count the suspended time and every stream looks stale at once.

## Rerun (owner, B10 run 2)

Valid windows: Fri 27 Nov is a half-day (close 13:00 ET), so start between 10:00 and 11:55 ET. From Mon 30 Nov, start between 10:00 and 14:55 ET. Fix the clock and keep the PC awake first (dry-run section above), then:

```powershell
git status --porcelain -- src config      # must print nothing
python -m family_desk_spike --duration-min 35
python -m family_desk_spike.verify_log logs\spike\<YYYY-MM-DD>.jsonl
```

Pass needs `edgar cycles` ≈ 35 with `pre_filter_min` > 0, `mean_rps` a number ≤ 1, `news_rest_watchlist` ≥ 1, `news_stream.delivery_proven` true (the stream subscribes to `"*"` since `6fe8044`, owner decision), a news cross-check verdict, and no `ERROR: source task` or `STALL:` line. Paste both outputs to the agent, which adds a "Run 2" section here and updates the anchor.
