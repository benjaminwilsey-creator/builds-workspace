Step 0
Based on the ReelForge Technical Guide v2, here is your Phase 0 — Pre-Build Setup step-by-step guide:

Phase 0: Pre-Build Setup Checklist
1. Supabase (Database + Auth)
    • [ ] Create Supabase project at supabase.com
    • [ ] Note connection strings and anon key (save to secure location)
    • [ ] Set up GitHub Actions keep-alive workflow — pings Supabase twice/week to prevent free-tier project pause (7-day inactivity policy)
2. Cloudflare R2 (File Storage)
    • [ ] Create R2 bucket
    • [ ] Configure CORS for Vercel frontend
    • [ ] Confirm signed URL expiry is set to at least 24h (so download links don’t expire between generation and partner action)
3. AWS Account (Lambda + SQS + SES)
    • [ ] Register AWS account
    • [ ] Configure Lambda execution role with SQS + R2 permissions
    • [ ] Note: SES will be used for alert emails on pipeline failures
4. API Keys & Accounts
    • [ ] NYT Books API — apply at developer.nytimes.com — free, takes 24–48 hours
    • [ ] Google Cloud APIs — enable in same project:
        ◦ Books API
        ◦ Cloud TTS API
        ◦ Cloud Vision API
        ◦ Gmail API (for outreach drafts — see step 9)
    • [ ] Gemini API — create API key at aistudio.google.com — free tier, 15 RPM, 1M tokens/day
    • [ ] Hardcover.app — create account (required for GraphQL API access)
    • [ ] Reddit API — create app at reddit.com/prefs/apps — for r/RomanceBooks and r/Fantasy monitoring
5. Amazon Associates (Revenue)
    • [ ] Apply for Amazon Associates account — get your associate tag
    • [ ] ⚠️ Apply immediately — account requires 3 qualifying sales within 180 days of application
6. Vercel (Frontend Hosting)
    • [ ] Create Vercel project
    • [ ] Connect to GitHub repo (will be created in Phase 1)
7. Music Library Seed
    • [ ] Seed music_library table with 20+ tracks from:
        ◦ Pixabay Music (CC0 or Pixabay commercial license)
        ◦ YouTube Audio Library (tracks marked “No attribution required”)
    • [ ] ⚠️ Reject any CC-BY tracks — attribution cannot be automated at scale
8. Gmail API Setup (Outreach Drafts)
    • [ ] Enable Gmail API in your Google Cloud project
    • [ ] Configure OAuth consent screen:
        ◦ User type: External
        ◦ Scope: gmail.compose only (create drafts — cannot read/send/delete)
    • [ ] Add authorized domain (Vercel app domain, once known)
    • [ ] Add partner’s Gmail as a test user
    • [ ] Create OAuth 2.0 Client ID (Web application type)
    • [ ] Store GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in Vercel env vars
    • [ ] Add placeholders to .env.example
    • [ ] ⚠️ Apply for Google app verification early — review takes 1–4 weeks, blocks production use beyond test users
9. Meta Business Suite (Distribution)
    • [ ] Confirm Meta Business account exists
    • [ ] Familiarize with native scheduling workflow (no API posting used)

Blocking Items Before Phase 1
Before starting Phase 1 (Database & Auth), these must be complete:
Item	Owner	Notes
Supabase project created	You	Connection strings documented
Google app verification submitted	You	1–4 week lead time
Amazon Associates application submitted	You	180-day clock starts on approval
Partner UI framework selection	Partner	From Framework Review doc — needed for Publisher Licenses screen design

Estimated time: 2–3 hours for setup tasks, plus waiting periods for API approvals (NYT: 24–48h, Google verification: 1–4 weeks, Amazon: variable).

