---
name: website-audit
description: Audit a prospect's website for verifiable problems that affect enquiries or bookings. Use after discovery, before scoring.
---

# Website audit

Needs open network access. If a fetch fails because of the sandbox network policy, say so — never audit from memory or search snippets alone.

## Tools
- Playwright (preinstalled Chromium): load desktop (1366×768) and mobile (iPhone 13 device preset). Save screenshots under `sales-agent/reports/evidence/<FD-id>/`.
- Lighthouse: `npx lighthouse <url> --chrome-flags="--headless --no-sandbox" --only-categories=performance,accessibility,seo,best-practices --output=json` with `CHROME_PATH=/opt/pw-browsers/chromium`, or the PageSpeed Insights API if a key is configured. Record URL, date, form factor, scores.
- Link check: collect `<a href>` on the homepage + contact/booking pages; HEAD/GET each internal link; record 4xx/5xx.

## Checklist
Verified (objective): no site / holding page · HTTPS errors · broken links/images · missing title/meta description · no viewport meta / horizontal scroll on mobile · tap targets too small · contact details missing or only in an image · booking/menu link broken or only a PDF · Lighthouse scores · form errors.
Subjective (label as opinion): dated look, weak hierarchy, unclear CTA, thin service descriptions.

## Write-up (to CRM `Findings`)
For each issue: **Observation** (with evidence) → **Likely effect on customers** → **Suggested improvement**. Example: "Book a table link sits in the footer on mobile (screenshot) → harder for mobile visitors to book → fixed 'Book' button in the header."

Never claim slow/broken/insecure/poorly ranked without a recorded test. Never invent conversion or revenue figures.
