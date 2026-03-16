# ADR 0004 — Replace AWS with Google Cloud for Backend Infrastructure

**Date:** 2026-03-15
**Status:** Accepted

## Decision

Replace AWS Lambda + SQS + SES with Google Cloud equivalents. All backend infrastructure
will run on Google Cloud, set up via Google CLI (gcloud). Reddit API integration is dropped
from this build.

## What changed from the original design

| Component | Original (AWS) | Replacement (GCP) |
|-----------|---------------|-------------------|
| Functions | AWS Lambda | Google Cloud Functions |
| Queuing | AWS SQS | Google Cloud Pub/Sub |
| Email alerts | AWS SES | Google Cloud (TBD / alternative) |
| Setup method | Console UI | Google CLI (gcloud) |

Reddit API — dropped entirely for this build. Reddit changed their API access process,
making it impractical to integrate. Signal that Reddit would have provided (community
mentions) is not replaced in v1.

## Why

- Google Cloud was already required for TTS, Vision, Gemini, Books API, Gmail API, and
  Gmail OAuth — consolidating all backend infrastructure on one platform reduces credential
  surface, simplifies billing, and avoids managing two cloud providers
- Google CLI (gcloud) setup completed in Phase 0 — infrastructure is already configured
- Reddit API access process changed and is no longer viable for this build

## Consequences

- Tech stack is now Google Cloud end-to-end (no AWS in this build)
- Lambda /tmp 2048 MB sizing note from Known Risks is no longer relevant
- EventBridge → Cloud Scheduler for cron triggers
- SQS inter-stage queuing → Pub/Sub
- Music library seed and all other Phase 0 items are unaffected
- Reddit mention signal is not available in v1 — book discovery relies on NYT, Hardcover,
  CoinGecko trending equivalent (NYT lists + Hardcover trending)
