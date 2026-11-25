---
name: plan-review
description: Score a family-desk phase plan against the PRD, the failure library and compliance before any work starts. Use when the owner asks to review, score or evaluate a plan.
---

# Plan review

Score honestly; interpret the gaps rather than restating them. Write nothing but the eval file.

1. Read the PRD, RETRO, MASTER_BRIEF, COMPLIANCE, FAILURE_LIBRARY and the plan.
2. Coverage table: one row per PRD requirement relevant to the phase: requirement · severity (critical / important / detail) · coverage (full / partial / missing) · evidence (plan section) · gap. Vague coverage is `partial`.
3. Run the `failure-check` skill on the plan and include its table.
4. Score: `score = (full + 0.5 × partial) / total × 100`, per severity and overall, arithmetic shown.
5. Top five gaps (critical first), then a five-part narrative: posture, strengths, weaknesses (the pattern), most likely failure if run as written, kind of remediation needed.
6. Verdict: READY if critical coverage is 100% and overall ≥ 85% and no failure-check row is `missing` for an applicable failure; otherwise FIX FIRST.
7. Write `docs/phases/phase_{N}/phase_{N}_eval.md` (append a dated section if it exists).
