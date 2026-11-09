# Penguin e-foil SVG benchmark

A fresh replacement for the saturated "pelican riding a bicycle" test. It checks spatial composition and whether the model knows what an e-foil is.

## Prompt (verbatim, nothing added)

```
Generate an SVG of a penguin wearing a sombrero riding an e-foil.
```

## Rules

- One attempt per model, no retries.
- Medium reasoning effort. Note it in the table if a model has no medium setting.
- No system prompt, no style hints, no tools.

## Safety

- Never open an SVG in a browser before checking it.
- Scan every SVG for `<script`, `on*=` handlers, `href=`, `<foreignObject` and `javascript:`.

## Rendering

1. Run `qlmanage -t -s 800` on the SVG.
2. Trim the white padding.
3. Stamp a bottom-left label: `model · effort (time)`.

Output folders:
- Raw SVGs: `svg/<model>_<effort>.svg`
- Labeled renders: `png/`

## Scoring checklist

| Item | What correct looks like |
|---|---|
| One mast | A single vertical mast under the board |
| Prop / motor | A motor pod with a propeller on the mast or fuselage |
| Remote | A hand-held throttle remote |
| Wing underwater | The foil wing is below the water surface |
| Board above water | The board flies clear of the water |
| Feet on board | The penguin's feet sit on the board |
| Hat on head | The sombrero sits on the penguin's head |

## Results

| Model | Effort | Time | One mast | Prop | Remote | Wing underwater | Board above water | Feet on board | Hat on head | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| Opus 5.5 | medium | 23 s* | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | Front and rear wings swapped |
| Sonnet 5.5 (`claude-sonnet-5-5`) | medium | 14 s* | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ | Kite-style cable instead of a remote |
| Haiku 5.5 (`claude-haiku-5-5`) | medium | 23 s* | ✅ | ❌ | ⚠️ | ❌ | ✅ | ✅ | ✅ | Whole foil drawn above the water; bottom third of the image blank |
| Qwen3.8-27B abliterated (local MTPLX) | medium | 113 s | ❌ two | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | 196 reasoning tokens |
| Qwen3.8-27B abliterated (local MTPLX), run 2 | medium | 145 s | | | | | | | | 977 reasoning tokens, seed 202 |
| Qwen3.8-27B abliterated (local MTPLX), run 3 | medium | 159 s | | | | | | | | 1,961 reasoning tokens, seed 303 |
| Qwen3.8-27B abliterated (local MTPLX), xhigh | xhigh | 1,765 s | | | | | | | | 29,587 reasoning tokens, seed 404 |
| Opus 5.5 (`claude-opus-5-5`), run 2 | medium | 36 s* | | | | | | | | |
| Opus 5.5 (`claude-opus-5-5`), run 3 | medium | 34 s* | | | | | | | | |
| Sonnet 5.5 (`claude-sonnet-5-5`), run 2 | medium | 19 s* | | | | | | | | |
| Sonnet 5.5 (`claude-sonnet-5-5`), run 3 | medium | 17 s* | | | | | | | | |
| Haiku 5.5 (`claude-haiku-5-5`), run 2 | medium | 18 s* | | | | | | | | |
| Haiku 5.5 (`claude-haiku-5-5`), run 3 | medium | 25 s* | | | | | | | | |
| Opus 5.5 | default | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ high | First drawing, before effort was fixed at medium |
| Grok 4.7 (`grok-4.7`, grok CLI) | medium | 233 s** | | | | | | | | SVG inline in reply. Tools disallowed except 4 read-only X-search tools the CLI would not remove. An earlier attempt in agent/plan mode (34 s) planned instead of drawing |
| Claude Opus 4.6 (Thinking) (`claude-opus-4-6-thinking`, agy) | default (agy rejects `--effort` for this model) | 48 s** | | | | | | | | SVG taken from its `write_file` tool call, which agy headless denied; reply text was one line |
| Claude Sonnet 4.6 (Thinking) (`claude-sonnet-4-6`, agy) | default (agy rejects `--effort` for this model) | 57 s** | | | | | | | | Saved the SVG as an agy artifact file instead of inline (tool use) |
| GPT-OSS 120B (Medium) (`gpt-oss-120b-medium`, agy) | medium | 310 s** | | | | | | | | Delegated to an agy sub-agent with `Model: inherit` (so still GPT-OSS), which saved the SVG as a file |
| Gemini 3.8 Flash (Medium) (`gemini-3.8-flash-medium`, agy) | medium | 10 s** | — | — | — | — | — | — | — | FAILED twice: first action was `ls -la`, auto-denied in headless mode, no output |
| Gemini 3.8 Flash (High) (`gemini-3.8-flash-high`, agy) | high | 12 s / 10 s** | — | — | — | — | — | — | — | FAILED twice: first action was `ls -la` / `date`, auto-denied, no output |
| Gemini 3.8 Flash (Low) (`gemini-3.8-flash-low`, agy) | low | 7 s / 5 s** | — | — | — | — | — | — | — | FAILED twice: first action was `date` / `ls -la`, auto-denied, no output |
| Grok 4.7 (`grok-4.7`), run 2 | medium | 383 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.7_medium_run2.svg` |
| Grok 4.7 (`grok-4.7`), run 3 | medium | 276 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.7_medium_run3.svg` |
| Grok 4.7 Build Fast (`grok-4.7-build-fast`), run 1 | medium | 276 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.7-build-fast_medium.svg` |
| Grok 4.7 Build Fast (`grok-4.7-build-fast`), run 2 | medium | 139 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.7-build-fast_medium_run2.svg` |
| Grok 4.7 Build Fast (`grok-4.7-build-fast`), run 3 | medium | 302 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.7-build-fast_medium_run3.svg` |
| Grok 4.6 (`grok-4.6`), run 1 | medium | 98 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.6_medium.svg` |
| Grok 4.6 (`grok-4.6`), run 2 | medium | 115 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.6_medium_run2.svg` |
| Grok 4.6 (`grok-4.6`), run 3 | medium | 116 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.6_medium_run3.svg` |
| Grok 4.5 (`grok-4.5`), run 1 | medium | 64 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.5_medium.svg` |
| Grok 4.5 (`grok-4.5`), run 2 | medium | 65 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.5_medium_run2.svg` |
| Grok 4.5 (`grok-4.5`), run 3 | medium | 76 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/grok-4.5_medium_run3.svg` |
| Claude Opus 4.6 (Thinking), agy, run 2 | default | 38 s*** |  |  |  |  |  |  |  | SVG from agy `write_file` tool call; `svg/claude-opus-4.6_default_run2.svg` |
| Claude Opus 4.6 (Thinking), agy, run 3 | default | 41 s*** |  |  |  |  |  |  |  | SVG from agy `write_file` tool call; `svg/claude-opus-4.6_default_run3.svg` |
| Claude Sonnet 4.6 (Thinking), agy, run 2 | default | 235 s*** |  |  |  |  |  |  |  | SVG from agy `write_file` tool call; `svg/claude-sonnet-4.6_default_run2.svg` |
| Claude Sonnet 4.6 (Thinking), agy, run 3 | default | 54 s*** | — | — | — | — | — | — | — | FAILED: used agy image generator, got a JPG not SVG; see svg/claude-sonnet-4.6_default_run3_FAILED.txt |
| Claude Sonnet 4.6 (Thinking), agy, run 4 | default | 52 s*** |  |  |  |  |  |  |  | SVG from agy `write_file` tool call; `svg/claude-sonnet-4.6_default_run4.svg` |
| GPT-OSS 120B (Medium), agy, run 2 | medium | 151 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gpt-oss-120b_medium_run2.svg` |
| GPT-OSS 120B (Medium), agy, run 3 | medium | 15 s*** |  |  |  |  |  |  |  | SVG from agy `write_file` tool call; `svg/gpt-oss-120b_medium_run3.svg` |
| Gemini 3.8 Flash (Medium), agy, TEXT PROMPT†, run 1 | medium | 94 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_medium_textprompt.svg` |
| Gemini 3.8 Flash (Medium), agy, TEXT PROMPT†, run 2 | medium | 96 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_medium_textprompt_run2.svg` |
| Gemini 3.8 Flash (Medium), agy, TEXT PROMPT†, run 3 | medium | 90 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_medium_textprompt_run3.svg` |
| Gemini 3.8 Flash (High), agy, TEXT PROMPT†, run 1 | high | 112 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_high_textprompt.svg` |
| Gemini 3.8 Flash (High), agy, TEXT PROMPT†, run 2 | high | 153 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_high_textprompt_run2.svg` |
| Gemini 3.8 Flash (High), agy, TEXT PROMPT†, run 3 | high | 171 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_high_textprompt_run3.svg` |
| Gemini 3.8 Flash (Low), agy, TEXT PROMPT†, run 1 | low | 35 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_low_textprompt.svg` |
| Gemini 3.8 Flash (Low), agy, TEXT PROMPT†, run 2 | low | 70 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_low_textprompt_run2.svg` |
| Gemini 3.8 Flash (Low), agy, TEXT PROMPT†, run 3 | low | 55 s*** |  |  |  |  |  |  |  | SVG inline in reply; `svg/gemini-3.8-flash_low_textprompt_run3.svg` |

\* Claude subagent wall time, including start-up overhead.
\** CLI wall time on the VM (`grok -p` / `agy -p`), including start-up; the 5 runs ran in parallel. agy and grok always add their own agent system prompt, and agy loads the user's rules files; there is no flag to turn that off. All 4 SVGs passed the safety grep (no `<script`, `on*=`, `href=`, `<foreignObject`, `javascript:`). Raw replies: `raw/<model>_<effort>.txt`.
\*** Batch of 2026-11-09 10:46–11:10 on the VM: the 4 Grok models ran in parallel, agy models ran one at a time (so each saved file maps to one run). Same CLI flags as \**. All 26 SVGs passed the safety grep. A model stopped after 2 failures; Sonnet 4.6 failed once (run 3) so run 4 replaced it.
† Gemini prompt variant (requested by the user): the benchmark prompt plus " Output the SVG code as text in your reply; do not use any tools." With the plain prompt every Gemini variant ran a shell command first and was blocked. Not directly comparable to the other rows.

### Not run yet

The Antigravity and Grok models, from the VM:
- Grok
- Gemini
- GPT-OSS 120B
- Sonnet 4.6
- Opus 4.6

## Related

`../pelican-public/` holds public pelican and voxel results downloaded from Simon Willison's blog, OpenRouter and ai-muninn. They are reference images only.

DONE (VM session "vm:temp call grok", 2026-11-09 10:17): 5 rows added (Grok 4.7, Opus 4.6, Sonnet 4.6, GPT-OSS 120B, Gemini 3.8 Flash = failed); 4 SVGs in svg/, raw replies in raw/, rubric columns left for scoring.
DONE 2 (10:20): all 6 models agy lists now were tried (no Flash Lite listed). Gemini 3.8 Flash high/low added, each failed twice, not retried further. GPT-OSS note corrected: its sub-agent inherited GPT-OSS.
DONE 3 (VM session "vm:temp call grok", 11:12): extra runs added, 26 SVGs + 1 failure note. Every agy and Grok model now has 3 SVGs (Grok 4.7 / Opus 4.6 / GPT-OSS: runs 2-3; Sonnet 4.6: runs 2 and 4; Grok 4.5 / 4.6 / 4.7 Build Fast and Gemini text-prompt variants: runs 1-3). Rubric columns empty for scoring.
