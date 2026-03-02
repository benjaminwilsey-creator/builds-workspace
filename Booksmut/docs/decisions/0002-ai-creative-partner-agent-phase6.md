# 0002 — AI Creative Partner Agent Added to Phase 6

**Date:** 2026-03-01
**Status:** Accepted
**Project:** Booksmut / ReelForge

## Decision

An AI creative partner chat widget will be added to the Phase 6 UI build — a Gemini-powered
in-app assistant seeded with the writing style and voice of the top 3 BookTok romance/romantasy
authors, available on the Publisher Licenses and Campaign Queue screens.

## Context

During the UI framework review, the partner answered Q3 ("Is there anything missing from all
three options that you'd want?") with: "A creative partner AI agent who is considered the top
three best authors of this style of books." This request was not in the original design. It
represents a desire for creative assistance within the tool itself — most likely to help
write or refine publisher outreach emails, review generated captions for tone, or brainstorm
campaign angles. This feature is small to add (a Gemini chat widget) but is a deliberate
scope addition and must be recorded before Phase 6 build begins.

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| No in-app AI assistant | Ignores an explicitly stated partner need. The outreach email and caption review workflow benefits directly from creative tone guidance. |
| External tool (ChatGPT tab, separate app) | Breaks the "everything in one place" principle of the tool. Partner would need to context-switch, which conflicts with the ADHD-friendly design goals. |
| Full autonomous AI agent (auto-sends emails, auto-edits scripts) | Out of scope and contrary to the human-in-the-loop moderation principle already locked in the design. Partner makes all final decisions. |

## Reasoning

A Gemini-powered chat widget embedded in the UI is the minimal viable implementation. It
requires no new infrastructure (Gemini API is already in the stack) and no new data model —
just a UI component and a system prompt. The system prompt seeds the assistant with:

1. The writing style and voice characteristics of the top 3 current BookTok romance/romantasy
   authors (to be identified and documented before Phase 6 — e.g. Emily Henry, Ana Huang,
   Rebecca Yarros or equivalent at build time).
2. The context of what ReelForge is and what the partner is trying to accomplish.
3. The specific task it should help with (outreach tone, caption review, campaign ideas).

The widget is read-only assistance — it does not write to the database or trigger any
pipeline actions. Partner copies suggestions manually.

## Tradeoffs Accepted

- "Top 3 authors" must be chosen and documented before Phase 6 — this is a content
  decision, not a technical one, and requires agreement between both partners.
- Author writing styles in the system prompt are approximate and static; they will not
  auto-update as the BookTok landscape changes. Plan to review annually.
- Adds Gemini API token usage per chat session. At free tier (1M tokens/day), this is
  negligible for single-tenant use but should be monitored.
- The widget is basic chat — not a full agent with memory or tool access. If the partner
  wants persistent conversation history across sessions, that is a future enhancement.

## Revisit If

- Partner requests the agent to take actions (draft and send emails directly, edit
  scripts automatically) — at that point this becomes a proper agentic feature requiring
  a separate design session.
- Token usage on Gemini free tier is consistently high — may need rate limiting or
  session caps.
- The "top 3 authors" framing proves too narrow — could be expanded to a style guide
  the partner maintains herself.
