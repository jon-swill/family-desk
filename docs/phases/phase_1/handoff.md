# Phase 1 hand-off (updated 2026-11-25, after B10 run 1 and the G1 phase-gate)

Gate result: **HOLD** (`phase_1_eval.md`, `phase_1_summary.md`). Gates green at hand-off: ruff, format, `mypy --strict`, pytest 259 passed. Stop before G2 (owner instruction 2026-11-25).

## Done (agent)
B1–B9, B12, A1–A8, A10, A11, G1. B11 run-1 evidence is written (`spike_evidence.md`). A9 merged the six approved proposals. Proof for each task is in `phase_1_tasks.md`.

## Waits on the owner, in order

1. **Sync the PC clock** (admin PowerShell: right-click PowerShell → Run as administrator). Windows Time has never synced, and the clock is about 0.52 s slow:
   ```powershell
   w32tm /config /manualpeerlist:"time.windows.com,0x9 time.cloudflare.com,0x9" /syncfromflags:manual /update
   Restart-Service w32time
   w32tm /resync /force
   w32tm /query /status          # expect a real Source and a Last Successful Sync Time
   w32tm /stripchart /computer:time.cloudflare.com /samples:3 /dataonly   # offsets within about ±0.05 s
   ```
   If `/resync` fails, open Settings → Time & language → Date & time, turn on "Set time automatically", and click "Sync now".

2. **B10 run 2** (another session; the G-9 rerun rule applies because EDGAR failed in run 1). Fri 27 Nov is a half-day, so start between 10:00 and 11:55 ET. From Mon 30 Nov, start between 10:00 and 14:55 ET. From the repo root with the venv active:
   ```powershell
   git pull                                   # if run from a fresh clone
   git status --porcelain -- src config       # must print nothing
   python -m family_desk_spike --duration-min 35
   python -m family_desk_spike.verify_log logs\spike\<YYYY-MM-DD>.jsonl
   ```
   A pass shows `edgar cycles` near 35 with `pre_filter_min` > 0, a numeric `mean_rps` ≤ 1, `news_rest_watchlist` ≥ 1, a `news_stream` cross-check entry, and no `ERROR: source task` or `STALL:` line. Paste both outputs to the agent.

3. **O6:** approve or reject P-07 to P-27 in `docs/research/failure_library_proposals.md`. The new ones from today are P-23 (schema drift), P-24 (silent worker death), P-25 (unsynced clock), P-26 (fakes raise different errors from the real adapter) and P-27 (egress allowlist covers HTTP only).

4. **Engine choice (G-1, decided at G3).** The robustness check excludes NautilusTrader and LEAN, because neither documents a kernel choke point in front of every order path (E-1, a knock-out). So the matrix makes no engine recommendation. Choose one: (a) record that the engine choice moves to the Phase 2 install-check (an install needs your explicit approval), or (b) ask for E-1 to be verified first.

5. **G2 red-team** in a fresh session, then **G3 sign-off** in RETRO.

## Decisions the agents raised (owner's call)
- **News stream:** to give the stream a real positive case in run 2, it could subscribe with `"*"` and count unfiltered items as liveness, keeping only watchlist metadata. This changes what the stream receives. It is not done.
- **A10:** do you hold a live Alpaca account? Alpaca's IEX-only rule is worded for "Paper Only Account" holders, and it decides the delayed-SIP DP-1 and both SIP DP-9 cells. Also: where R-27's indicative values should come from (no documented free source), and whether polling Apple's newsroom RSS is acceptable under Apple's site terms.
- **Earlier, still open:** the A5 matrix method choices, and the A3/A6/A7 notes in the previous hand-off (git history of this file, commit `839fca9`).

## Next agent tasks once the above is done
B11 run 2 section and new anchor → re-score EDGAR DE-4/DE-5 (and A8 if a total moves) → A9 for O6-approved rows → re-run G1.
