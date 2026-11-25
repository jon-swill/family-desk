---
name: phase-plan
description: Write the plan and task list for the next family-desk phase, traced to docs/PRD.md. Use when the owner asks to plan a phase or "plan phase N".
---

# Phase plan

You write a plan another session can execute without questions, plus its task list. You write no source code.

1. Read `CLAUDE.md`, `docs/MASTER_BRIEF.md`, `docs/PRD.md` (whole), `docs/RETRO.md` (whole), `.claude/rules/trading-invariants.md`, earlier `docs/phases/phase_*/` folders, and any code the phase will touch. Plan against what exists.
2. Write `docs/phases/phase_{N}/phase_{N}_plan.md` with these sections:
   - Goal and gate (copy the PRD §6 gate; make it testable).
   - Scope: requirement IDs covered; explicit non-goals.
   - Deliverables table: # · deliverable · path · requirement ID · "Proven by" (a command, test or artifact).
   - Sequence table: # · unit of work · depends on · parallel? · owner (`agent` or `owner`) · check that ends it.
   - Failure modes and edge cases (cite FAILURE_LIBRARY entries that apply).
   - Compliance items touched (cite COMPLIANCE.md IDs).
   - Risks, assumptions (each marked verified or unverified), "Do not" constraints (include every hard stop in CLAUDE.md that applies).
3. Write `docs/phases/phase_{N}/phase_{N}_tasks.md`: one row per sequence unit: ID · task · owner · depends on · status `☐ not started` · proof (empty) · notes (the ending check in ≤12 words).
4. Owner decisions in RETRO are closed: never schedule them as work or list them as risks.

Reply: plan and tasks paths, number of units, which run in parallel, assumptions needing the owner. Then suggest `plan-review`.
