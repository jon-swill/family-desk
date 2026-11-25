# Phase 1 hand-off (updated 2026-11-25, after B10 run 1, the G1 phase-gate and the afternoon dry run)

Gate result: **HOLD** (`phase_1_eval.md`, `phase_1_summary.md`). Gates green at hand-off: ruff, format, `mypy --strict`, pytest 262 passed (after the dry-run `max_gap_s` fix). Dry run 2026-11-25 12:21 ET (not run 2): `"*"` news stream proven (32 items); the PC went into Modern Standby at 12:41, so only 22 live minutes; new anchor `0248516c…6890` (`spike_evidence.md`). Stop before G2 (owner instruction 2026-11-25).

## Done (agent)
B1–B9, B12, A1–A8, A10, A11, G1. B11 run-1 evidence is written (`spike_evidence.md`). A9 merged the six approved proposals. Proof for each task is in `phase_1_tasks.md`.

## Waits on the owner, in order

1. **Fix the PC clock (still open).** The owner's 12:15 ET sync did not step the clock (`Time Delta: 0 ms`): the offset (0.51 s) is under the 1 s `MaxAllowedPhaseOffset`, so Windows slews it over hours, and the `0x9` peer won't poll again for about 9 hours. Measured +0.354 s slow at 14:25 ET. The earlier `w32tm /resync /force` line was wrong (no such switch). Exact admin commands, the 15-minute check and a one-time `Set-Date` fallback are in `spike_evidence.md`, "Dry run", part (3).

2. **B10 run 2** (another session; the G-9 rerun rule applies because EDGAR failed in run 1). Fri 27 Nov is a half-day, so start between 10:00 and 11:55 ET. From Mon 30 Nov, start between 10:00 and 14:55 ET. **Plug the PC in and stop the screen turning off** (this PC's standby is screen-off; the 25 Nov dry run was suspended after 20 minutes): `powercfg /change monitor-timeout-ac 0`, restore with `powercfg /change monitor-timeout-ac 20` afterwards. From the repo root with the venv active:
   ```powershell
   git pull                                   # if run from a fresh clone
   git status --porcelain -- src config       # must print nothing
   python -m family_desk_spike --duration-min 35
   python -m family_desk_spike.verify_log logs\spike\<YYYY-MM-DD>.jsonl
   ```
   A pass shows `edgar cycles` near 35 with `pre_filter_min` > 0, a numeric `mean_rps` ≤ 1, `news_rest_watchlist` ≥ 1, `news_stream` with `delivery_proven: True` and a cross-check verdict, and no `ERROR: source task` or `STALL:` line. The stream now subscribes to `"*"`. If Alpaca refuses that on the free plan (for example code 405 or 409), the run prints `ERROR: source task 'news' ended`; stop and tell the agent. Paste both outputs to the agent.

3. ~~**O6**~~ **Done by the owner 2026-11-25:** P-07 to P-28 approved, ten with amendments; A9 merged them as F-26 to F-47 / R-47 to R-68. Open from it: whether an Alpaca GTC stop-limit can elect outside regular hours (docs silent; R-49 assumes yes). Settle it with a paper test or Alpaca support before Phase 3.

4. ~~**Engine choice (G-1, decided at G3).**~~ **Decided by the owner 2026-11-25 (RETRO):** moved to the Phase 2 install-check, packaged engine for backtests only, own execution loop behind the kernel. Confirm it in the G3 sign-off row. Original text: The robustness check excludes NautilusTrader and LEAN, because neither documents a kernel choke point in front of every order path (E-1, a knock-out). So the matrix makes no engine recommendation. Choose one: (a) record that the engine choice moves to the Phase 2 install-check (an install needs your explicit approval), or (b) ask for E-1 to be verified first.

5. **G2 red-team** in a fresh session, then **G3 sign-off** in RETRO.

## Decisions the agents raised (owner's call)
- ~~**News stream `"*"`**~~ **Decided by the owner and done 2026-11-25 (`6fe8044`).**
- **A10:** do you hold a live Alpaca account? Alpaca's IEX-only rule is worded for "Paper Only Account" holders, and it decides the delayed-SIP DP-1 and both SIP DP-9 cells. Also: where R-27's indicative values should come from (no documented free source), and whether polling Apple's newsroom RSS is acceptable under Apple's site terms.
- **Earlier, still open:** the A5 matrix method choices, and the A3/A6/A7 notes in the previous hand-off (git history of this file, commit `839fca9`).

## Next agent tasks once the above is done
B11 run 2 section and new anchor → re-score EDGAR DE-4/DE-5 (and A8 if a total moves) → re-run G1 (G-4 should now pass).
