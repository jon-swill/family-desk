---
name: failure-check
description: Check a family-desk plan or codebase against every entry in the failure library and report which controls exist and are tested. Use inside plan-review, phase-gate and red-team, or when the owner asks "are we protected against X".
---

# Failure check

1. Read `docs/research/FAILURE_LIBRARY.md` in full.
2. For each entry F-xx and each rule R-xx it defines, decide whether it applies to the work being checked (a plan or code). Not applicable needs a one-line reason.
3. Table: entry · rule · applies? · control present? (yes / partial / missing) · tested? (test name or "no") · evidence (plan section or file:line).
4. List any new failure pattern you noticed that the library lacks, written as a proposed F-xx entry with a proposed rule. Do not edit the library yourself; the owner approves additions.
