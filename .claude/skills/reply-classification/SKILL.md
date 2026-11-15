---
name: reply-classification
description: Check the Formivane Gmail inbox for replies to outreach, classify them and update CRM and suppression list. Use at the start of each session and when asked about replies.
---

# Reply classification

1. Build the list of contacted domains from CRM (Status in Sent, Follow-up due, Replied).
2. `search_threads` for `from:(<domain1> OR <domain2> …)` and `from:mailer-daemon newer_than:14d`. Read each thread in full with `get_thread` (search previews miss newer messages).
3. Classify the latest prospect message:

| Class | Signals | Action |
|---|---|---|
| Interested | asks for mock-up, price, call, "tell me more" with intent | Status → Enquiry; **flag to George at top of report**; draft nothing that commits to price/dates |
| Needs more information | questions, no commitment yet | Status → Replied; draft a factual answer from formivane-profile.md for approval |
| Not interested | "not for us", "we have someone" | Status → Closed – no; no reply |
| Unsubscribe | "remove", "no thanks", "stop", any objection | Suppression (Opt-out, domain level); Status → Opted out; tick Opted out; no reply |
| Out of office | auto-reply | No change; note return date |
| Unclear | anything else | Status → Replied; ask George |

When in doubt between Not interested and Unsubscribe, treat as Unsubscribe.

4. Update `Last reply`, `Reply class`, `Email history`. Never negotiate, quote, promise dates or accept payment.
