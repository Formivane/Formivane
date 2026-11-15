---
name: lead-qualification
description: Verify company type and contact, check suppression, and score a lead out of 100. Use after a website audit and before any email is written.
---

# Lead qualification

1. **Legal entity**: find the company on Companies House. Record number, status (must be Active), type. Confirm the link to the website (company name/number on site, or matching address). Sole trader / E&W partnership / can't verify → Compliance basis = blocked/unverified, add to suppression list (reason "Sole trader/partnership") when confirmed, stop.
2. **Contact**: role address on the business's own domain, published on its own site. Record `Email source URL`. Webmail → stop. Never guess.
3. **Suppression + history**: follow `sales-agent/compliance/suppression-workflow.md` (all four checks). Tick "Suppression checked".
4. **Score** with `sales-agent/config/scoring.md`. Write a one-line justification per criterion in the record body.
5. **Status**: ≥70 and cleared → Shortlisted. 60–69 → Research (keep). <60 → Closed – no with reason.
