# Setup Report — 2026-11-15

## Environment
Claude Code on the web (cloud container, Default environment, **limited network**). Repo: Formivane/Formivane, branch `claude/formivane-sales-agent-setup-0rh7ra`.

## Connections (read-only tests)

| Service | Status | Test |
|---|---|---|
| Gmail | ✅ Working | Listed labels, drafts (0), sent (10). Account: George Meyer <formivanedigital@gmail.com> |
| Notion | ✅ Working | Workspace "formivanedigital's Space"; read Agency HQ, tracker (36 rows), suppression list (2 rows) |
| WebSearch | ✅ Working | Search returned results |
| Railway | ✅ Working | Project `formivane-website`, service `web`, custom domain formivanedigital.co.uk, last deploy SUCCESS 01:26 today |
| Supabase, Claude Docs | ✅ Connected | Not needed for this workflow |
| **Web page fetching** (WebFetch, curl, Playwright) | ❌ Blocked | Proxy refuses any host not on the allowlist — couldn't even load formivanedigital.co.uk or google.com |
| PageSpeed Insights API | ⚠️ Reachable, rate-limited | HTTP 429 without an API key |
| Apify, HubSpot, Ahrefs, Similarweb, Canva, Slack, etc. | ❌ Failed to connect | Same network policy (403 on tunnel) |

## What already exists (important)
- **Notion CRM is already built** — "Formivane Digital – Agency HQ" with Prospect & Project Tracker (FD-0001–FD-0036) and Suppression List. I'm reusing it, not creating a duplicate "Sales Pipeline" database. Mapping in `sales-agent/crm/notion-schema.md`.
- **10 emails were sent on 10 Nov** to Ltd companies with "coming soon" holding pages. 2 hard bounces (both already suppressed). 8 delivered, **0 replies** after 5 days.
- 13 more leads (FD-0024–0036) sit at "Research — ready to draft". Same strategy: holding pages, mostly outside Yorkshire.
- Previous rules already applied correctly: Ltd/LLP only, Companies House verified, no webmail addresses.

## Problems found in the existing outreach
1. **Subject lines are bare domains** (e.g. the prospect's own domain name as the whole subject). Reads like spam or phishing. Fix: real subject lines.
2. **The privacy link goes to `my-5311gzgyu9.brewpage.app`**: a random third-party domain in a cold email from a gmail.com address. That hurts trust and deliverability. Fix: put the privacy notice on formivanedigital.co.uk.
3. **Sending from @gmail.com** while you own formivanedigital.co.uk. That's weaker for credibility and deliverability. Recommend Google Workspace (or similar) on the domain and moving outreach to george@formivanedigital.co.uk. That needs your decision and a new Gmail connection.

## Pushback on the brief
- **Target sectors and PECR clash.** Most cafés, barbers, cleaners and sole tradespeople are sole traders or partnerships, which count as *individual subscribers*. You can't cold-email them without consent. Expect most discovered businesses in those sectors to be filtered out. The pilot will look for Ltd companies in those sectors; the yield will be low and that's correct.
- **"Has a weak website" is a weaker hook than "has no website".** The 10 Nov batch went the holding-page route. Both are valid, but weak-site outreach needs real audit evidence, which needs network access (below).

## Missing capabilities → recommendations

| # | Need | Recommendation | Needs you |
|---|---|---|---|
| 1 | **Open web access** (audits, Companies House, business sites) | Set this environment's network to unrestricted. Alternatively, run the agent in Claude Code on your own machine. Can't be done with an allowlist because prospect domains are unknown in advance. | Approve the environment change |
| 2 | PageSpeed data | Free Google Cloud API key for PageSpeed Insights, saved as a network secret (never in chat) | Create key; approve secure form |
| 3 | Companies House | Free Companies House API key (api.company-information.service.gov.uk), saved the same way | Create key; approve secure form |
| 4 | Lighthouse / screenshots | Already available: Playwright + Chromium preinstalled; Lighthouse via npx | Nothing, once #1 is done |
| 5 | Domain email | Google Workspace on formivanedigital.co.uk | Your call (costs money) |

Not recommended: Apify/Google Maps scraping (terms-of-service risk), Instantly/Gojiberry-style automated sequencers (they conflict with per-email approval).

## Built today (in repo)
- `sales-agent/README.md`: operating manual and approval matrix
- `sales-agent/compliance/`: PECR/UK GDPR policy and suppression workflow
- `sales-agent/config/`: scoring rubric (/100) and Formivane facts sheet (mostly blanks for you to fill)
- `sales-agent/crm/notion-schema.md`: field/status mapping and proposed additive properties
- `.claude/skills/`: 8 skills (discovery, audit, qualification, email writing, Gmail drafts, CRM, reply classification, reporting)

## Approval needed
See approval matrix in `sales-agent/README.md`. In short: drafting, research and CRM updates run freely. Sending, deleting, schema/network/credential changes and anything about price need you.

## Decisions for George
1. Approve unrestricted network for this environment (or say you'll run it locally).
2. Approve adding 9 properties to the Notion tracker (additive, listed in notion-schema.md).
3. Fill the blanks in `sales-agent/config/formivane-profile.md`, especially legal entity, services, privacy URL and portfolio.
4. Fix the privacy link and subject lines before any more sends.
5. The 8 delivered emails: one manual follow-up from 17 Nov, each approved by you? Or leave them?
