---
date: 2026-03-15
project: Booksmut / ReelForge
---

## What we did
- Completed all Phase 0 account setup (Supabase, R2, Vercel, Google Cloud, Gemini, Associates, music library)
- Created Google Cloud Service Account (reelforge-api-runner) with TTS, Vision, Books permissions
- Added partner as Google OAuth test user — no Workspace needed
- Ran all 16 Phase 1 database migrations in Supabase SQL Editor, RLS enabled
- Created first tenant (ReelForge / thesecretpic-20) and linked owner user

## Next up
- Seed `seed_books` table with 20 known BookTok titles (Supabase SQL Editor)
- Start Phase 2: discovery pipeline — Cloud Functions for NYT fetcher + Hardcover GraphQL fetcher

## Watch out for
- Google app verification still pending — blocks Gmail OAuth for non-test users in production (Phase 6)
- Amazon Associates 180-day clock is running — need 3 qualifying sales before account closes
