# Formivane Digital — Sales Agent Operating Manual

Research-led outreach for Formivane Digital (owner: George Meyer). This folder is the agent's source of truth for rules. Skills live in `.claude/skills/`.

## Systems

| System | Use | Location |
|---|---|---|
| Notion | CRM + suppression list (source of truth) | "Formivane Digital – Agency HQ" → *Prospect & Project Tracker* (`collection://e24b4b54-44d5-43f5-a359-bf7e41ba2b76`) and *Suppression List* (`collection://d86016e5-612a-4ce9-8bf7-fc7e5cd09afa`) |
| Gmail | Drafts, sent history, replies | George Meyer <formivanedigital@gmail.com> — the only authorised sender |
| Web | Discovery, audits, Companies House checks | Needs open network access (see setup report) |

## Pipeline (skills, in order)

1. `business-discovery` → find candidates
2. `website-audit` → evidence of a real website problem
3. `lead-qualification` → company type + contact + score /100
4. `cold-email-writing` → only for score ≥ 70 and compliance = cleared
5. `gmail-drafts` → create draft, never send without approval
6. `crm-management` → one record per business, kept current
7. `reply-classification` → triage replies, suppress opt-outs at once
8. `outreach-reporting` → daily report

## Approval matrix

| Action | Needs George's approval? |
|---|---|
| Web research, reading Gmail/Notion | No |
| Creating/updating Notion lead records | No |
| Adding an entry to the suppression list | No (always allowed, never blocked) |
| Creating a Gmail draft | No |
| **Sending any email** (first touch, follow-up or reply) | **Yes — per recipient, on the final text** |
| Removing anyone from the suppression list | Yes |
| Deleting records or drafts | Yes |
| Notion schema changes, new databases | Yes |
| Network/environment changes, credentials, installs | Yes |
| Anything about price, scope, dates, contracts, payment | Yes — flag to George, don't answer |
| Scheduled/unattended runs | Yes — not authorised yet |

General permission to "operate autonomously" is **not** permission to send.

## Agent graph, loops and self-improvement

The pipeline above now runs as a graph of agents: see `loop/README.md` and `loop/graph.json`.

- **Agents** (`.claude/agents/`): lead-scout → site-auditor → qualifier → email-writer → *George approves + sends* → reply-classifier → reporter → improver.
- **Loops**: each output must pass hard checks (`loop/rubrics/*.json`) and an independent `critic` (`loop/rubrics/*.md`) before it moves on. 3 attempts maximum.
- **Graph**: run it with the `run-graph` skill. Dashboard: `python loop/loopkit.py dashboard loop/dashboard.html`.
- **Self-improvement**: run the `self-improve` skill weekly. It A/B tests one prompt change at a time and only promotes a change with evidence, as a pull request George merges. Until volume builds up, it learns from George's edits to drafts.
- The approval matrix above is unchanged. Loops research and draft; only George sends. `loop/guardrails.md` lists what the improver can never touch.

## Hard rules

- Never guess an email address. Only addresses published by the business itself (own website or own verified listing), on the business's own domain.
- Corporate subscribers only (Ltd, LLP, PLC, Scottish partnership) unless documented consent exists. See `compliance/compliance-policy.md`.
- Check the suppression list and Gmail sent history before every draft.
- A draft is not a send. Mark "Sent" only after Gmail confirms a sent message ID.
- No invented testimonials, results, pricing, portfolio, stats or mockups.
- British English.
