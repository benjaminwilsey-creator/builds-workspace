# 0003 — Semi-Automated Publisher Outreach with Accuracy-Gated Full Automation

**Date:** 2026-03-01
**Status:** Accepted
**Project:** Booksmut / ReelForge

## Decision

Publisher outreach will be semi-automated: the system discovers the contact email and
generates a personalised Gmail draft via Gemini; the partner confirms the contact and
clicks Send from her Gmail inbox. Contact discovery accuracy is logged per run, and the
system gates to fully automated contact discovery when it achieves ≥98% accuracy across
50 confirmed runs. The Gmail integration is architected from day one to support Option C
(auto-detect sent emails from Gmail Sent folder) without a schema rewrite.

## Context

The publisher licensing workflow was the most manual, friction-heavy step in the entire
pipeline. The partner must find a publisher contact, write a personalised outreach email,
send it, and track responses — all by hand. This was identified during the FigJam pipeline
review as a candidate for automation. However, fully automated commercial email sending
carries CAN-SPAM and deliverability risks, and publisher response rates depend on emails
feeling genuinely human. A semi-automated approach — system does the research and writing,
human clicks Send — removes the bulk of the friction while keeping legal compliance and
response quality intact. The Claude AI Gmail integration (which creates drafts) was already
in use by the partner and confirmed as the correct delivery mechanism.

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Fully manual (current design) | Too much friction. Partner must write every email from scratch, look up every contact, and manually track follow-ups. High cognitive load for irregular use. |
| In-UI draft preview only (copy-paste) | Removes writing effort but still requires partner to open Gmail and paste manually. No tracking of whether she actually sent it. |
| Fully automated send from day one | CAN-SPAM compliance risk. Deliverability risk — automated bulk outreach triggers spam filters. Publisher response rates lower for obvious template emails. No human gate. |
| Option C (batch + Sent folder auto-tracking) from day one | More complex to build. Requires broader Gmail scopes (read Sent folder). Unnecessary at MVP scale. Designed as the upgrade path, not the starting point. |

## Reasoning

Option B (semi-automated) achieves the core goal — reducing the partner's outreach effort
to reviewing a draft and clicking Send — without the legal and deliverability risks of
fully automated sending. The accuracy-gating approach for contact discovery is the right
pattern: start with human confirmation to build a ground-truth dataset, measure accuracy
against it, and only remove the human gate when the system has earned it (98% over 50 runs).
This avoids the common mistake of automating a step before confirming the automation works.

The `gmail_thread_id` and `sent_at_detected` schema fields are added now at zero build cost
to make Option C a configuration change rather than a schema migration later.

## Architecture

**Contact Discovery (accuracy-gated):**
- Given `publisher_domain`, Gemini searches the publisher's Contact/Rights page for the
  marketing or permissions email address.
- Result shown to partner with "Confirm" / "Correct it" buttons.
- Each run logged to `contact_discovery_log` with `was_correct` outcome.
- Accuracy = `was_correct / total` over rolling last 50 runs.
- When accuracy ≥ 98%, `contact_discovery_method` defaults to `AUTO_AUTO` — confirmation
  step skipped, contact used directly.

**Draft Generation and Delivery:**
- Gemini generates a personalised email (publisher name, contact name, 1–2 specific book
  titles from their catalog in pipeline, partner name).
- Gmail API (`gmail.compose` scope only) pushes draft to partner's inbox.
- `outreach_draft_id` saved to `publisher_licenses` — UI shows direct link to draft.
- Partner reviews in Gmail, personalises if needed, clicks Send.
- "Mark as Sent" in ReelForge UI sets `outreach_date` and `status = IN_DISCUSSION`.

**Follow-Up Automation:**
- Daily job checks: `status = IN_DISCUSSION` + `outreach_date < now() - 7 days` + no
  `followup_draft_sent_at`.
- Generates follow-up draft, pushes to Gmail, sets `followup_draft_sent_at`.
- One follow-up per publisher — does not repeat.

**Prompt Versioning:**
- Each generated email logs which `prompt_version` was used.
- When partner marks a publisher as `IN_DISCUSSION` (i.e. they replied), that version
  gets a response tick.
- After 20+ sends, response rates per version are visible in Settings.
- The better-performing prompt becomes the active default.

## New Schema

### publisher_licenses — additional fields
| Field | Type | Purpose |
|---|---|---|
| `contact_discovery_method` | text ENUM | `MANUAL` \| `AUTO_CONFIRMED` \| `AUTO_AUTO` |
| `partner_corrected_contact` | boolean | Did partner change the auto-found email? |
| `outreach_draft_id` | text | Gmail draft ID for direct link from UI |
| `followup_draft_sent_at` | timestamptz | Prevents follow-up from re-firing |
| `gmail_thread_id` | text | Reserved for Option C reply thread tracking |
| `sent_at_detected` | timestamptz | Null in Option B; auto-filled in Option C |

### contact_discovery_log — new table
| Field | Type | Purpose |
|---|---|---|
| `id` | uuid PK | |
| `publisher_domain` | text | Publisher being looked up |
| `discovered_email` | text | What the system found |
| `was_correct` | boolean | Set when partner confirms or corrects |
| `corrected_to` | text | What partner changed it to (if wrong) |
| `run_number` | int | Cumulative counter across all runs |
| `created_at` | timestamptz | |

### prompt_versions — new table
| Field | Type | Purpose |
|---|---|---|
| `id` | uuid PK | |
| `prompt_text` | text | Full Gemini prompt template |
| `send_count` | int | How many emails used this version |
| `response_count` | int | How many got a reply (partner marked IN_DISCUSSION) |
| `response_rate` | float | response_count / send_count |
| `active` | boolean | Currently the default prompt |
| `created_at` | timestamptz | |

## Gmail OAuth Setup Summary

Scope required: `gmail.compose` only (create drafts — cannot read, send, or delete).
Provider: Google OAuth 2.0 via `next-auth` in the Next.js app.
Token storage: refresh token stored encrypted in Supabase `users` table.
Setup: done during Phase 0 alongside other Google Cloud API configuration.
Full step-by-step: see Technical Guide v2, Section 08, Phase 0.

## Tradeoffs Accepted

- Partner must manually click "Mark as Sent" after sending from Gmail in Option B. Minor
  friction, but keeps the publisher record accurate without needing Sent folder access.
- Contact discovery accuracy gate means the confirmation step persists until 50 runs
  complete — this could take weeks at low volume. Acceptable: it's a one-time cost that
  produces a reliable automation.
- Prompt versioning tracking only starts from when this feature is built — no historical
  baseline. First 20 sends establish the baseline.
- Gmail OAuth requires Google to approve the app for production use beyond test users.
  App verification can take 1–4 weeks. Apply during Phase 0 to avoid blocking Phase 6.

## Revisit If

- Publisher response rate drops below 10% — may indicate the generated emails feel too
  automated and the prompt needs a human review pass.
- Contact discovery accuracy fails to reach 98% after 100+ runs — may indicate the
  publisher website scraping approach is too inconsistent and a contacts database
  (e.g. Hunter.io) should be evaluated instead.
- Volume scales to multi-tenant — batch processing (Option C) and rate limiting become
  necessary at that point.
- Google rejects app verification — will need to evaluate SES-based outreach as fallback.
