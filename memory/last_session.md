---
date: 2026-03-22
project: Workspace Migration + GitHub Sync
---

## What we did
- Fixed builds-workspace git remote on C drive — was accidentally pointing at model-specific-skills repo
- Completed E drive migration — E:\Builds - Copy is now primary workspace, all subprojects cloned as standalone repos
- Booksmut cloud functions (r2-presign, tts-voicer, video-composer) committed to reelforge; Booksmut untracked from builds-workspace
- builds-workspace .gitignore updated: Booksmut/, model-skills/, Architect/, Sportsball/ all excluded
- rapid2 v1.2 CLAUDE.md (RSI-14 signal, revised thresholds) pushed to openclaw v1.2 branch
- Developer Quick Reference updated: /test step added before /review in pre-deploy workflow
- catchup.skill updated to E drive paths and git pull at session start

## Next up
- Monitor v1.3 paper bot — check signals are firing and trades look sensible
- Once paper results look good, flip v1.3 to live trading

## Watch out for
- C drive builds-workspace is NOT primary — do not use for new work
- rapid2 v1.3 is on develop branch (not master)
- Sportsball folder on E drive cannot be deleted — GitKraken lock file holds it
