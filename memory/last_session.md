---
date: 2026-03-23
project: Booksmut — TikTok Integration Setup
---

## What we did
- Spiked TikTok Content Posting API — chose file upload (draft/inbox) approach, no custom domain needed
- Created Terms of Service, Privacy Policy, and OAuth callback pages on GitHub Pages for TikTok app registration
- Benjamin submitted TikTok developer app for review

## Next up
- Get Client Key + Client Secret from TikTok once app is approved (or sandbox credentials appear)
- Do one-time OAuth browser login to connect the BookTok TikTok account and store tokens in GCP Secret Manager
- Build tiktok-poster Cloud Function + "Post to TikTok" button in Delivery tab

## Watch out for
- Token refresh trap: every TikTok token refresh returns a NEW refresh token — old one dies immediately; must save to Secret Manager before function exits
- Draft mode has no caption pre-fill — caption added manually in TikTok app before publishing
- TikTok app review may flag no mobile app — internal tool argument should resolve it
