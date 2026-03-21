---
date: 2026-03-16
project: Booksmut / ReelForge
---

## What we did
- Completed Steps 2-3 through 4: queue-selector, script-generator, and moderation UI all deployed and working
- Script-generator calls Gemini 2.5-flash and writes scripts for 5 campaigns — confirmed SCRIPTED in Supabase
- Built and deployed a moderation web page (GitHub Pages) where scripts can be reviewed, edited, approved, or sent back for regeneration with tone notes
- Fixed three issues along the way: Gemini SDK deprecation, retired model names, and an exposed service_role key (rotated and cleaned up)

## Next up
- Step 5: TTS voiceover function — reads MODERATION_SCRIPT campaigns, generates audio per campaign part using Google Cloud Text-to-Speech

## Watch out for
- Moderation UI anon key lives in browser localStorage only — if it stops working, clear with localStorage.removeItem('rf-anon-key') in browser console and re-enter
- tone_note column was added to campaigns table this session — new migrations may need to account for it
