# Owner check-ins

The owner's answers to the report check-in forms (PRD FR-26, decisions D-19). Later reviews and the system read them. Answers are input to reports and reviews only. They never trigger a trade or a mode change; those go through the command channel (FR-12, FR-25).

During paper trading these files may hold paper figures. From the Phase 6 live gate, reports with real balances go in the git-ignored `private/` folder, and only the answers stay here.

## Files

| Cadence | Path | Contents |
|---|---|---|
| Weekly (Sunday) | `weekly/YYYY-Www.md` (ISO week, e.g. `weekly/2026-W49.md`) | 3–5 yes/no or 1–5 answers, optional free text |
| Monthly | `monthly/YYYY-MM.md` | Settings confirmation (keep / change, per setting) and notes |
| Quarterly | `quarterly/YYYY-Qn.md` | Sleeve-size decision: grow / hold / shrink, with a link to the evidence |
| Options learning track | `options/YYYY-MM-DD-<symbol>.md` | One file per manual paper-options trade: structure, max loss at entry, outcome. The weekly "what I learned" note goes in the weekly file |

Each file starts with a front-matter block so it can be parsed. The exact schema is fixed in the Phase 2 SPEC. Until then, use this shape:

```yaml
---
date: 2026-11-29
cadence: weekly          # weekly | monthly | quarterly | options
answers:
  comfortable_with_drawdown: yes
  override_any_position: no
  keep_current_settings: yes
  surprise_level_1_to_5: 2
notes: optional free text
---
```
