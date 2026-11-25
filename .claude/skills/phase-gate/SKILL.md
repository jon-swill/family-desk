---
name: phase-gate
description: Decide with evidence whether a family-desk phase is done, and record it. Use when the owner asks to close, advance or gate a phase, or whether a phase is done.
---

# Phase gate

You report; you fix nothing.

1. Read the plan, tasks, eval, PRD gate for this phase and RETRO.
2. Run every quality gate; report totals and each failure. A failing test the plan requires = HOLD.
3. Exit-criteria table: deliverable or gate criterion · status (delivered / partial / missing / waived) · evidence (file, passing test, command output, log). "Looks implemented" is not evidence. A missing critical deliverable = HOLD.
4. Re-score coverage as `plan-review` does and append a dated completion section to the eval file.
5. Run `failure-check` against the delivered work (not the plan).
6. Write `docs/phases/phase_{N}/phase_{N}_summary.md`: what was built, how to run it, known issues, what the next phase inherits.
7. Recommend ADVANCE or HOLD. ADVANCE still needs (a) a `red-team` review in a fresh session with its findings resolved and (b) the owner's sign-off recorded in `docs/RETRO.md`. Name whichever is missing.
