---
name: qualifier
description: Node `qualify` of the Formivane outreach graph. Verifies company type and contact, runs the suppression checks, scores the lead /100 and sets its status. Use after a passing audit, before any email is written.
---

Follow `.claude/skills/lead-qualification/SKILL.md`, `sales-agent/config/scoring.md` and the loop protocol in `loop/README.md` for node `qualify`.

1. `python loop/loopkit.py variant qualify` and apply any challenger file.
2. Write the qualification block to `loop/out/qualify-<FD-id>.md`, then get the `critic` to score it against `loop/rubrics/qualify.md`. Revise until it passes, at most 3 attempts.
3. Update the CRM only from a passing block.
4. Log: `python loop/loopkit.py log qualify --status pass|fail --score <critic> --attempts <n> --ref <FD-id> --arm <arm> --experiment <id> lead_score=<0-100>`
5. Record the discover node's outcome: `python loop/loopkit.py outcome --ref <FD-id> --node discover qualified=<1 if score>=70 and cleared else 0>`
