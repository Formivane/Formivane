# Rubric: qualification (node `qualify`)

Output: the qualification block for one lead (`.claude/skills/lead-qualification/SKILL.md`, `sales-agent/config/scoring.md`).

| Criterion | 10 | 5 | 0 |
|---|---|---|---|
| **entity_verified** | Companies House number, Active status and type recorded, plus the link to the website | Number recorded but the link to the site is weak | Not checked, or a sole trader/partnership passed through |
| **contact_legit** | Role address on the business's own domain, with `Email source URL` | Named address with an LIA note | Guessed address or webmail. Fail. |
| **suppression_checked** | All four checks in suppression-workflow.md recorded | Some recorded | Not done. Fail. |
| **score_justified** | One line of evidence per scoring criterion, and the arithmetic adds up | Some lines missing | Score with no reasoning |
| **status_correct** | Status matches the score band and the gates | n/a | Wrong band, or a gate ignored |

Pass rule: `contact_legit` ≥ 5, `suppression_checked` = 10, `entity_verified` ≥ 8, `status_correct` = 10.
