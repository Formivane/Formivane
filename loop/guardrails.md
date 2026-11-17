# Guardrails: the improver may never change these

- `sales-agent/README.md`: the approval matrix and hard rules. Sending always needs George's per-recipient approval on the final text. Loops never send.
- `sales-agent/compliance/*`: PECR and UK GDPR policy, and the suppression workflow. Corporate subscribers only.
- Never guess an email address. Suppression and history checks happen before every draft.
- `sales-agent/config/formivane-profile.md`: only George adds facts.
- No invented testimonials, results, pricing, portfolio, stats or mock-ups.
- Hard checks in `loop/rubrics/write.json` can only get stricter.
- No scheduled or unattended run sends email or changes Notion schema.

## Where human edits are found (the improver's best signal)
- Gmail: compare the draft text recorded in the CRM (`Gmail draft ID`, `Email history`) with the message actually in Sent for the same recipient. Any difference is George's edit.
- Record it with `python loop/loopkit.py outcome --ref FD-#### --node write approved_unedited=0 edit_words=<n>` (or `approved_unedited=1` when nothing changed).

## This repo is public
Prospect names, emails, findings and drafts never go into committed files. `loop/out/` is gitignored, so keep them there or in Notion and Gmail. In `runs.jsonl`, use FD IDs and numbers only. Notes must not name a business or a person.
