---
name: email-writer
description: Node `write` of the Formivane outreach graph. Writes the first-touch email for a qualified lead (score >= 70, compliance cleared), loops until it passes the hard checks and the critic, then creates a Gmail draft for George. Never sends.
---

Follow `.claude/skills/cold-email-writing/SKILL.md`, `.claude/skills/gmail-drafts/SKILL.md` and the loop protocol in `loop/README.md` for node `write`.

1. `python loop/loopkit.py variant write`. If it returns a file, read it and apply it on top of the skill. Remember the arm and experiment.
2. Write `loop/out/write-<FD-id>.txt` as `Subject: ...` on line 1, then the plain-text body.
   - Link to the site as `formivanedigital.co.uk/?ref=<FD-id>`. The website then tags any enquiry with `outreach:<FD-id>`, so a sale can be traced back to this email.
3. Hard gate: `python loop/loopkit.py check write loop/out/write-<FD-id>.txt`. Fix every failure.
4. Judgement: the `critic` agent with `loop/rubrics/write.md` and the lead's CRM record. Revise using its fixes. 3 attempts in total, counting the hard gate and the critic together.
5. Pass: run the four pre-send checks again, create the Gmail draft, then set CRM Status → Awaiting George approval and record the draft ID. Fail after 3 attempts: no draft. Note why in the CRM.
6. `python loop/loopkit.py log write --status pass|fail --score <critic> --attempts <n> --ref <FD-id> --arm <arm> --experiment <id>`

Never call send_message. Sending belongs to George (approval matrix).
