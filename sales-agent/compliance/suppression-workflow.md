# Suppression Workflow

Store: Notion *Suppression List* (`collection://d86016e5-612a-4ce9-8bf7-fc7e5cd09afa`).
Fields: Email or domain (title) · Company name · Date added · Reason (Opt-out / Bounce / Complaint / Sole trader/partnership / Other) · Source.

## Before any draft — all four checks, every time

1. **Suppression list:** query for the exact email **and** the bare domain.
   ```sql
   SELECT * FROM "collection://d86016e5-612a-4ce9-8bf7-fc7e5cd09afa"
   WHERE lower("Email or domain") IN (lower(?), lower(?))
   ```
2. **CRM:** search tracker for same domain or company name (status Sent, Bounced, Opted out, Closed – no → stop).
3. **Gmail history:** `search_threads` with `to:<domain> OR from:<domain>` including sent. Any prior contact → stop unless it's an approved follow-up.
4. **Compliance basis** = cleared (see compliance-policy.md).

Tick "Suppression checked" in the CRM only after all four pass.

## Adding entries (no approval needed)

| Trigger | Reason | Also do |
|---|---|---|
| Reply objecting / unsubscribing | Opt-out | CRM Status → Opted out, tick Opted out, cancel follow-up |
| Hard bounce | Bounce | CRM Status → Bounced |
| Complaint / spam report | Complaint | CRM Status → Opted out; tell George |
| Verified sole trader / E&W partnership | Sole trader/partnership | CRM Status → Closed – no |
| Business asks via any channel | Opt-out | as above |

Suppress at **domain** level for opt-outs and complaints (the whole business said no). Suppress at **address** level for bounces.

Entries are never removed without George's written approval.
