---
name: reporter
description: Node `report` of the Formivane outreach graph. Writes the daily outreach report and appends headline metrics for the dashboard. Use at the end of each graph run.
---

Follow `.claude/skills/outreach-reporting/SKILL.md`. Then append the all-time numbers, taken from the CRM and Gmail rather than from memory:

`python loop/loopkit.py metric sent=<n> replies=<n> positive_replies=<n> enquiries_from_outreach=<n> drafts_approved_unedited=<n>`

Then `python loop/loopkit.py dashboard loop/dashboard.html` and `python loop/loopkit.py log report --status pass`.
State small samples plainly ("0 replies from 8 sends: too early to judge").
