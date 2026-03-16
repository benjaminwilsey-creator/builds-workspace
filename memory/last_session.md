---
date: 2026-03-15
project: Booksmut / ReelForge
---

## What we did
- Deployed the nyt-fetcher Cloud Function — it now fetches NYT Best Sellers and enriches each book via Hardcover automatically, all in one function
- Fixed two bugs along the way: Windows line endings corrupting the Hardcover API token, and a wrong GraphQL query format for the Hardcover search endpoint
- Confirmed end-to-end: 34 books discovered and fully enriched (genre, description, tags) in Supabase
- Updated the Step 2-1 deployment doc to match the simpler single-function architecture

## Next up
- Cleanup: delete defunct hardcover-enricher Cloud Function + book-discovered Pub/Sub topic (two gcloud commands)
- Step 2-2: build the Scorer function — reads ENRICHED books, calculates a score, sets status to SCORED

## Watch out for
- allUsers IAM binding on nyt-fetcher resets on every redeploy — re-run the add-iam-policy-binding command after any future deploy
