---
name: crm-management
description: Create and update Formivane lead records in the Notion Prospect & Project Tracker without duplicates. Use whenever a lead's data or status changes.
---

# CRM management

Database: Notion "Prospect & Project Tracker", data source `collection://e24b4b54-44d5-43f5-a359-bf7e41ba2b76`. Field mapping and statuses: `sales-agent/crm/notion-schema.md`.

## Rules
- **Dedup first**: search by domain, then Companies House number, then company name. Update the existing record if found.
- IDs: next `FD-00NN` after the highest existing ID (query `MAX("userDefined:ID")`).
- Owner: "Lead Researcher" during research, "Outreach and Sales" once drafting, "George" when awaiting approval.
- Write facts with their source. Mark unverified things as unverified.
- Never set Status = Sent from a draft. Sent requires a Gmail sent message ID.
- Opted out / Bounced are terminal unless George says otherwise.
- UK English, GBP, dates as YYYY-MM-DD.
