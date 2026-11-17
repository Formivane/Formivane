# Rubric: cold email (node `write`)

Sources to check claims against: the lead's CRM record (Findings, evidence links) and `sales-agent/config/formivane-profile.md`. Hard checks are in `write.json`.

| Criterion | 10 | 5 | 0 |
|---|---|---|---|
| **specific** | The first two lines only work for this business: they name the actual page, button or element | Mentions their site, but generically | Passes the swap test: change the business name and it still works |
| **verified** | Every observation about their site is in the CRM Findings with evidence | One observation is soft or subjective but labelled as such | Any claim with no recorded evidence (slow, broken, insecure, ranking) |
| **one_idea** | One improvement and why it helps their customers, in plain words | Two ideas, or the benefit is vague | A list of problems, or a pitch for services |
| **honest_offer** | Only offers what formivane-profile.md lists (the free mock-up) and makes no result claims | Slight overstatement | Invented portfolio, mock-up, price, results or testimonial |
| **low_pressure** | Ends with one easy yes/no question | Mild push | Urgency, guilt, or several asks |
| **sounds_human** | Reads like George wrote it to one person, in British English. No AI tells (see the humanizer skill). | One stock phrase | Template voice |

Pass rule: every criterion ≥ 7 and `verified` = 10 and `honest_offer` = 10.
