---
date: 2026-03-23
project: Booksmut — ReelForge UI additions
---

## What we did
- Pushed Publisher Licenses tab live (Supabase RLS confirmed, GitHub Pages deployed)
- Added collapsible book description to Script Review cards so partner can read a plain-English summary of each book while reviewing the script

## Next up
- Compose the ~10 VOICED campaigns (Video Compose tab → Compose Now — no code needed)
- Build Gmail outreach button on publisher cards (ADR 0003)

## Watch out for
- publisher_licenses table has no tenant_id filter on RLS — fine for now, revisit if multi-tenant
- VOICED campaigns that errored stay VOICED and retry on next Compose Now (expected behaviour)
