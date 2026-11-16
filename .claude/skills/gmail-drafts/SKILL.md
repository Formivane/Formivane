---
name: gmail-drafts
description: Create, list and manage Gmail outreach drafts for Formivane and handle approved sends. Use whenever an email is to be drafted or sent.
---

# Gmail drafts

Authorised account: **formivanedigital@gmail.com** only. Confirm with `list_labels`/sent history that the connected account is this one before any write.

## Drafting (allowed without approval)
1. Re-run the four pre-send checks (`sales-agent/compliance/suppression-workflow.md`).
2. `create_draft` with to, subject, plain-text body. One recipient per draft. No CC/BCC.
3. Record the draft ID in CRM (`Gmail draft ID`), Status → Awaiting George approval.

## Sending (only with explicit approval)
- First-touch batches: George approves one sample draft; that covers the rest of the same batch (rules in `sales-agent/README.md` → Batch approval). Re-run every pre-send check on each draft right before sending; drop any that fail.
- Follow-ups and replies: approval must name the recipient and refer to the final text.
- If a draft's text changes after approval, it needs its own approval.
- "Go ahead and run outreach" with no sample draft approved is not approval.
- After `send_message`, confirm a sent message ID exists via `search_threads in:sent to:<address>`. Only then set Status → Sent, `Date contacted`, and append to `Email history`.
- Scheduled sends: allowed only for an approved first-touch batch, at the time George set. Never send follow-ups or replies in a scheduled/unattended run.

## Follow-ups
At most one, ≥7 days after first send, no reply/opt-out/bounce, drafted as a reply in the same thread, and approved like a first send.

## Bounces
Check for `mailer-daemon` replies within minutes of a send. Hard bounce → suppression (Bounce), Status → Bounced.
