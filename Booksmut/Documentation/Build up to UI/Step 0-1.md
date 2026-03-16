Step 1: Supabase Setup Walkthrough
1. Create Your Supabase Project
    1. Go to supabase.com and click Start your project (or Sign In if you have an account)
    2. Sign in with GitHub (recommended) or email
    3. Click New Project
    4. Fill in the form:
        ◦ Name: reelforge (or your preferred name)
        ◦ Database Password: Generate a strong password — save this to your password manager
        ◦ Region: Choose the closest to you (e.g., East US (N. Virginia) for US East)
        ◦ Pricing Plan: Free (Hobby)
    5. Click Create new project
    6. Wait 2–3 minutes for provisioning to complete

2. Get Your Connection Strings
Once the project is ready:
    1. Click Settings (gear icon in left sidebar)
    2. Click API in the settings menu
    3. Copy and save these values to a secure location (password manager or encrypted notes):
Project URL: https://xxxxx.supabase.co
Anon/Public Key: eyJhbG... (starts with eyJhbG)
Service Role Key: eyJhbG... (starts with eyJhbG — KEEP THIS SECRET)
Database Password: (what you set during creation)
    4. Also note your Database Host for direct connections:
        ◦ Click Database in left sidebar
        ◦ Click Settings tab
        ◦ Click Connect at top of page
        ◦ Note the host: db.xxxxx.supabase.co

3. Create the GitHub Actions Keep-Alive Workflow
Supabase pauses free-tier projects after 7 days of inactivity. This workflow pings your project twice/week to keep it alive.
    1. In your Booksmut project folder, create this file:
Booksmut/.github/workflows/supabase-keepalive.yml
    2. Add this content:
name: Supabase Keep-Alive

on:
  schedule:
    # Runs every Monday and Thursday at 3 AM UTC
    - cron: '0 3 * * 1,4'
  workflow_dispatch: # Allows manual trigger

jobs:
  ping-supabase:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Supabase REST API
        run: |
          curl -X GET \
            "${{ secrets.SUPABASE_URL }}/rest/v1/" \
            -H "apikey: ${{ secrets.SUPABASE_ANON_KEY }}" \
            -H "Authorization: Bearer ${{ secrets.SUPABASE_ANON_KEY }}" \
            --fail
    3. Add the secrets to your GitHub repo:
        ◦ Go to your Booksmut GitHub repo
        ◦ Click Settings → Secrets and variables → Actions
        ◦ Click New repository secret
        ◦ Add these two secrets:
Name	Value
SUPABASE_URL	https://xxxxx.supabase.co (your Project URL)
SUPABASE_ANON_KEY	Your Anon/Public Key from Step 2
    4. Commit and push the workflow file
    5. Verify it works:
        ◦ Go to Actions tab in your GitHub repo
        ◦ Click Supabase Keep-Alive workflow
        ◦ Click Run workflow → Run workflow
        ◦ Confirm it completes successfully (green checkmark)

4. Verify Your Setup
Run this quick test to confirm everything is connected:
    1. Go to SQL Editor in Supabase dashboard
    2. Click New query
    3. Paste this test query:
-- Test query: create a simple table
CREATE TABLE IF NOT EXISTS test_connection (
  id SERIAL PRIMARY KEY,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO test_connection (message) VALUES ('Supabase is connected!');

SELECT * FROM test_connection;
    4. Click Run
    5. You should see one row with your test message
    6. Clean up (optional):
DROP TABLE IF EXISTS test_connection;

5. What You Have Now
Item	Status
Supabase project	✅ Active
Connection strings	✅ Saved securely
GitHub keep-alive workflow	✅ Running (Mon/Thu 3 AM UTC)
Database access	✅ Verified

Next Step
Once Supabase is set up and verified, move to Step 2: Cloudflare R2 for file storage.

