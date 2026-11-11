# Vibe Coder Simulator Implementation Plan (compressed)
**Goal:** playable title -> run -> win/ban -> share card before 01:00 WITA. **Spec:** spec.md + docs/superpowers/specs/2026-11-11-vibe-coder-design.md
**Stack:** Three.js r160 (vendored), plain JS modules, Web Audio, python3 http.server.
- [ ] Task 1 (00:40-00:50): index.html, src/main.js (room, desk, 7 monitors, whack-a-ban, penguin, smashing, vices), src/audio.js, src/shareCard.js. Check: jsc parses every module. Commit.
- [ ] Task 2 (00:50 freeze): fix parse/runtime errors found. Commit.
- [ ] Task 3 (by 00:55): notes.md, DELTA.md, final commit.
Review focus: untested in a real browser unless a headless one exists (none found).
