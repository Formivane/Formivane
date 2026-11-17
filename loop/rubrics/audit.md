# Rubric: website audit (node `audit`)

Output: the Findings write-up for one lead, following `.claude/skills/website-audit/SKILL.md`.

| Criterion | 10 | 5 | 0 |
|---|---|---|---|
| **evidenced** | Every "verified" issue links to a screenshot, a test result or a URL, with a date | Some evidence missing | Issues asserted with no test |
| **labelled** | Objective and subjective issues are clearly separated | Mixed in places | Opinion presented as fact |
| **relevant** | Issues sit on the path a customer takes to book, order or call | Some relevance | Cosmetic only |
| **actionable** | Each issue has Observation → likely effect → suggested fix | Partly | A list of complaints |
| **no_inventions** | No conversion or revenue figures, and nothing from memory or search snippets alone | n/a | Any invented figure or untested claim |

Pass rule: `evidenced` ≥ 8, `no_inventions` = 10, all others ≥ 6.
