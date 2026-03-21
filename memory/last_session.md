---
date: 2026-03-21
project: Booksmut / ReelForge
---

## What we did
- Built and deployed the TTS voicer (Step 5) — reads approved campaigns,
  generates one MP3 per part via Google TTS, uploads to Cloudflare R2
- Fixed three bugs along the way: missing updated_at column, PowerShell
  env var merging, and corrupted GCP_PROJECT value
- All 10 campaigns successfully voiced — audio confirmed in R2

## Next up
- Step 6: video composer — FFmpeg renders 30s MP4 per campaign part
- First decision needed: backdrop videos in R2, or use solid color
  background while covers are null?

## Watch out for
- All book cover images are null — backdrop fallback required for all videos
- Music library tracks are loaded in Supabase — ready for Step 6
