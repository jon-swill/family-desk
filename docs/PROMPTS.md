# Prompt pack (repo copy)

The project skills in `.claude/skills/` do the planning, scoring, running and closing. These prompts cover the gaps: independent review, weekly paper reviews, and the go-live gate. Prompt 0 is `docs/MASTER_BRIEF.md`.

| When | Use |
|---|---|
| Start of a phase | `phase-plan`, then `plan-review` |
| Run a phase | `/run-phase` |
| Check protections | `failure-check` |
| End of a phase | `phase-gate`, then `red-team` (or Prompt 3 below) in a fresh session, then your sign-off |

## Prompt 3: Independent red-team (fresh session, no prior context, different model from the author)

```text
You are an independent reviewer who did not write this. Your job is to find what will lose a family money or break the law.
[Attach the phase output: plan, SPEC, decision matrix, or evidence pack]

Check: (1) any path where an LLM, a bug or external text can place or enlarge a trade without passing the risk kernel; (2) any limit that can be raised quickly; (3) behavior when server, broker API, data feed or internet fails mid-trade; (4) crash response: failing to de-risk and de-risking into whipsaw; (5) tax-reserve correctness incl. losses, wash sales, NJ; (6) results that rely on contaminated or overfit backtests (docs/research/FAILURE_LIBRARY.md F-02, F-09); (7) whether costs fit the sleeve size; (8) security: key compromise, command spoofing, dev-pipeline/dependency tampering; (9) operations: partial fills, halts, corporate actions, extended hours, provider outages; (10) compliance against docs/COMPLIANCE.md; (11) fact-check claims about brokers, rules, taxes, prices with live primary sources; (12) every failure in FAILURE_LIBRARY.md: is its control present and tested?; (13) anything missing.

Output: ranked findings table (severity, scenario, evidence, fix), new failure-library entries if any, then a go/no-go verdict with conditions. Do not soften findings.
```

## Prompt 5: Weekly paper-trading review

```text
[Master brief]
[Attach this week's ledger export, decision log, cost report, alerts]

Review the week: P&L vs each baseline after all costs; every limit breach or near-miss; every order the risk kernel rejected or resized and whether that was right; reconciliation diffs; operational incidents; cost per strategy; tax reserve vs target; tax-lot and wash-sale events; any model-version change. Separate luck from evidence: with this few trades, what can and cannot be concluded? Add any new failure to FAILURE_LIBRARY.md. Recommend changes and classify each as safe-now vs needs-re-verification.
```

## Prompt 6: Go-live evidence pack

```text
[Master brief]
[Attach SPEC, all weekly reviews, red-team findings and fixes, fault-injection results]

Assemble the evidence on whether this system may trade real money. I make the go/no-go and allocation decision, not you. Check every gate criterion in docs/PRD.md §6; cite evidence or mark it unmet. If the evidence supports go: options for the initial live allocation with trade-offs, a ramp schedule, and the automatic conditions that return it to paper. If no-go: the shortest path to go.
```
