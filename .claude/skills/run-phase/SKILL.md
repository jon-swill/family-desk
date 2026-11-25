---
name: run-phase
description: Execute a reviewed family-desk phase plan one task at a time, with checks and commits after each. Use when the owner says run the phase, run the plan, or continue the tasks.
disable-model-invocation: true
---

# Run phase

You coordinate; do one task at a time from the tasks file, in order.

1. Confirm the plan's latest eval says READY. If not, stop and say so.
2. Run the quality gates first (`python -m pytest -q` until Phase 1 defines more). Stop on any failure you can't explain.
3. For each `agent` task: restate the task, the files you may touch, and the check that ends it. Do it. Keep the diff in scope; never weaken a test.
4. Run the check and the gates. Paste the real output as proof.
5. Commit locally with a message naming the task ID. Update the task row: status `☑ done`, proof (commit hash + check). Never push.
6. Stop and ask the owner before: any hard stop in CLAUDE.md, any `owner` task, an unclear spec, an unexpected failure, or anything touching keys, money, remotes or cloud.
7. After each task, give the owner a one-line status. When context runs low, write `docs/phases/phase_{N}/handoff.md` (done, next, open questions) and stop.
