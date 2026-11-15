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

## Notion API quirks (learned 2026-11-15)
- Create pages with the title key `"title": "FD-00NN"`. Both `ID` and `userDefined:ID` are rejected on create.
- SQL across two data sources in one query needs a Notion Business plan. Query the tracker and the suppression list separately, or use notion-search.
- Store `Score` on the /100 scale from FD-0038 onwards. FD-0001–FD-0037 used /10.
