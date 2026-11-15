# CRM Structure

Decision: **reuse the existing Notion "Prospect & Project Tracker"** rather than create a new "Formivane Digital — Sales Pipeline" database. It already holds 36 leads, 8 live sends and 2 bounces; a second database would split history and invite duplicate outreach. (Renaming it is optional.)

## Brief field → existing property

| Brief field | Existing property | Notes |
|---|---|---|
| Business Name | `Company name` (+ `ID` title, FD-0001…) | |
| Industry | `Sector` | |
| Location | `Location` | |
| Website URL | — | **add** `Website` (url) |
| Contact Email | `Business email` + `Email source URL` | |
| Lead Score | `Score` (/10, legacy) | **add** `Lead score` (number, /100) |
| Website Issues | `Findings` | |
| Proposed Improvement | — | **add** `Proposed improvement` (text) |
| Research Sources | `Email source URL` (partial) | **add** `Research sources` (text) |
| Research Date | `Date checked` | |
| Compliance Status | `Company type`, `Companies House number`, `Companies House verified` | **add** `Compliance basis` (select) |
| Outreach Status | `Status` | mapping below |
| Date Contacted | `Email history` (text) | **add** `Date contacted` (date) |
| Last Reply | — | **add** `Last reply` (date) + `Reply class` (select) |
| Next Action | `Next action` + `Next action due` | |
| Notes | page body | |
| — | — | **add** `Gmail draft ID` (text) |

## Status mapping

| Brief status | Existing `Status` option |
|---|---|
| Discovered / Researching | Research |
| Qualified | Shortlisted |
| Draft Ready | Outreach drafted |
| Awaiting Approval | Awaiting George approval |
| Contacted | Sent |
| Replied | Replied |
| Interested | Enquiry |
| Not Interested | Closed – no |
| Suppressed | Opted out / Bounced |

Existing extras kept: Mockup, Quality review, Follow-up due, Held, and project-delivery statuses.

## Proposed additions (awaiting approval — additive only, nothing removed)

`Website` url · `Lead score` number · `Proposed improvement` text · `Research sources` text · `Compliance basis` select [Cleared – corporate subscriber, Blocked – individual subscriber, Unverified, Consent held] · `Date contacted` date · `Last reply` date · `Reply class` select [Interested, Needs more information, Not interested, Unsubscribe, Out of office, Unclear] · `Gmail draft ID` text

## Dedup rule

Before creating a record: search by domain, then by Companies House number, then by company name. If found, update that record. One business = one record.
