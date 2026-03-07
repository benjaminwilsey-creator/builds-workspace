# 0001 — Publisher Licenses UI: Framework B (Dashboard + Focus Mode)

**Date:** 2026-03-01
**Status:** Accepted
**Project:** Booksmut / ReelForge

## Decision

The Publisher Licenses screen will be built using Framework B — a calm dashboard overview
with a one-click Focus Mode toggle — augmented with inline mini-checklists per publisher
borrowed from Framework C.

## Context

The non-technical partner (publisher licensing lead) reviewed three UI framework options
designed around ADHD-friendly principles. Her role is the commercial layer of the product:
contacting publishers, tracking responses, and uploading licensed cover assets. The UI
must work well after breaks of several days without requiring her to remember where she
left off. Three frameworks were presented: A (card-by-card only), B (dashboard + focus
mode toggle), C (guided workflow / checklist-first).

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Framework A — Focus Mode only | No big-picture view. She wanted to know the overall state at a glance. Good for distraction-avoidance but too narrow for a workflow she manages over weeks. |
| Framework C — Guided Workflow | Too rigid. Works well when schedule is regular; less suited to variable-session work. Also lowest flexibility for jumping to a specific publisher. |
| Pure Framework B (no modification) | Status dots alone don't give enough at-a-glance detail. Mini-checklists from C add the progress granularity she values without requiring full Framework C. |

## Reasoning

Framework B was the only option offering both the overview (pipeline summary, "Due this
week" prioritisation) and the escape valve (Focus Mode) she said she needed. Her answer
to Q2 ("thinking of other things that need to be done") confirms that surfacing urgent
items at the top of the screen reduces the mental load of context-switching. Her answer
to Q4 ("checklists") shows she processes status through step completion, not colour dots —
so the mini-checklist per publisher card (`Found contact ✓ · Sent email ✓ · Got reply ○`)
from Framework C is incorporated as a design requirement.

Her one-word answer ("efficient") means the UI must minimise clicks to complete the
standard workflow — no buried menus, one obvious next action per publisher at all times.

## Tradeoffs Accepted

- Framework B is more complex to build than A or C — requires two view modes and a
  toggle mechanism.
- The Focus Mode transition (dashboard → single card) adds a UI state to manage.
- Mini-checklist per card increases data displayed on the dashboard; must be kept compact.

## Revisit If

- Partner finds the dashboard overwhelming after extended use and consistently defaults
  to Focus Mode — at that point consider simplifying to A with a summary header only.
- Publisher volume grows beyond ~100 active records — pagination and filtering
  requirements may change the dashboard design significantly.
