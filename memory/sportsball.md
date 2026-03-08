# Sportsball — Project Memory

## Purpose
Build a college football content pipeline that grows Ricky's brand to $150k+/year.
Ricky has deep football knowledge but zero existing audience. Starting from scratch.

## Ricky's Content Angle
- **Sport:** College football (not NFL, not soccer)
- **Pillars:** Fantasy analysis, scheme breakdowns (X's and O's), statistics, current events (transfer portal, recruiting, NIL)
- **Differentiator:** Deep expertise in a niche other creators cover superficially
- **Comparable creator:** Cody Alexander (MatchQuarters) — built paid audience on technical film study

## Revenue Model (from spike, 2026-03-07)
Three-layer stack:
1. **YouTube** — audience foundation. NFL/college CPMs are high ($15–$30). NFL actively supports independent creators.
2. **Paid newsletter** (Substack or Beehiiv) — primary revenue. Target ~1,700 paid subs at $7–$10/month = $150k/year.
3. **Sportsbook affiliates** (FanDuel/DraftKings) — passive layer once audience hits 10k+ YouTube subs. Legal in 38 states.

Timeline to $150k: 3–5 years from zero. Brand sponsorships kick in at 100k YouTube subscribers.

## Platform Strategy
- **Primary:** YouTube + Substack/Beehiiv
- **Amplifier:** X/Twitter (promote content, not primary revenue)
- **Skip for now:** TikTok (low pay, uncertain US legal status)

## Pipeline Architecture (planned, not yet built)
Four stages: **Fetch → Generate → Review → Publish**

| Stage | What it does |
|-------|-------------|
| Fetch | Pulls today's top college football stories from news/stats APIs |
| Generate | Claude API drafts 3 content types: newsletter article, social post, video script |
| Review | Ricky approves/rejects each draft (method TBD — see open decisions) |
| Publish | Twitter/X auto-posts; newsletter + video script formatted for copy-paste |

Storage: SQLite (`drafts` table with status: pending / approved / rejected / published)
Framework: Flask (minimal local web UI for review queue)

## Tech Stack
- Python 3.12
- Claude API (content generation)
- Flask (review UI)
- SQLite (draft storage)
- Twitter/X API (auto-posting)
- Deploy target: EC2 or Google Cloud (TBD)

## Project Location
- Local: `c:\Users\benja\OneDrive\Documents\Builds\Sportsball\`
- Git: initialized locally, no GitHub remote yet
- CLAUDE.md: `Sportsball/CLAUDE.md`

## Open Decisions
1. **Review method** — local web UI (localhost:5000) proposed in /think but not confirmed. Alternatives: email, Telegram bot, folder + manual.
2. **Publish method** — Twitter auto-post assumed; Substack/YouTube script as copy-paste. Needs sign-off.
3. **Deploy target** — EC2 or Google Cloud (cost comparison not done yet)
4. **Data source** — college football news/stats API not confirmed. ESPN unofficial API is the candidate but could break.

## Legal Notes
- Sportsbook affiliate links: disclose explicitly adjacent to every link (FTC requirement, enforcement increased 2025)
- Legal in 38 states — California, Texas, Florida excluded. Geo-disclaim links.
- Picks content: frame as analysis/entertainment, never guarantee outcomes

## Status
Scaffolded (2026-03-07). /think plan presented, not yet signed off. No code written yet.

## Next Steps (start of next Sportsball session)
1. Confirm open decisions (review method, publish method)
2. Confirm college football data source
3. Run /think sign-off, then begin Phase 1 (fetcher)
