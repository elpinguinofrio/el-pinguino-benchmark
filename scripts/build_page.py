"""Build page/index.html for the penguin e-foil benchmark from the run list below."""
import html, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "index.html")

# (group id, model name, harness, note, [(image key, run label, effort, time)])
GROUPS = [
 ("opus-55", "Claude Opus 5.5", "Claude Code subagent", "claude",
  "The most consistent model in the test. Every medium run has the full e-foil: one mast, a motor pod with a propeller, an underwater wing, and a throttle remote in the penguin's flipper. The four drawings look almost interchangeable.",
  [("opus-5.5_medium", "Run 1", "medium", "23 s"), ("opus-5.5_medium_run2", "Run 2", "medium", "36 s"),
   ("opus-5.5_medium_run3", "Run 3", "medium", "34 s"), ("opus-5.5_default", "Earlier", "default", "n/a")]),
 ("sonnet-55", "Claude Sonnet 5.5", "Claude Code subagent", "claude",
  "Same flat style every time: mast and wing, board skimming the water. No propeller and no remote in any run; run 1 hangs a kite-style cable from the flipper instead.",
  [("sonnet_medium", "Run 1", "medium", "14 s"), ("sonnet-5.5_medium_run2", "Run 2", "medium", "19 s"),
   ("sonnet-5.5_medium_run3", "Run 3", "medium", "17 s")]),
 ("haiku-55", "Claude Haiku 5.5", "Claude Code subagent", "claude",
  "The weakest Claude. The hats drift toward cowboy and sun hats, the board sits in the water in two runs, and run 1 lifts the whole foil out of the sea.",
  [("haiku_medium", "Run 1", "medium", "23 s"), ("haiku-5.5_medium_run2", "Run 2", "medium", "18 s"),
   ("haiku-5.5_medium_run3", "Run 3", "medium", "25 s")]),
 ("opus-46", "Claude Opus 4.6", "Antigravity (agy)", "claude-old",
  "Small penguin, simple scene, a thin mast with a wing. No propeller, no remote. Next to Opus 5.5 this is the clearest generation gap in the test.",
  [("claude-opus-4.6_default", "Run 1", "default", "48 s"), ("claude-opus-4.6_default_run2", "Run 2", "default", "38 s"),
   ("claude-opus-4.6_default_run3", "Run 3", "default", "41 s")]),
 ("sonnet-46", "Claude Sonnet 4.6", "Antigravity (agy)", "claude-old",
  "More varied than Sonnet 5.5: one dynamic carving shot, one with a motor pod. The sombreros come out as lampshades or bonnets. Run 3 called an image generator instead of writing SVG and is not shown.",
  [("claude-sonnet-4.6_default", "Run 1", "default", "57 s"), ("claude-sonnet-4.6_default_run2", "Run 2", "default", "235 s"),
   ("claude-sonnet-4.6_default_run4", "Run 4", "default", "52 s")]),
 ("grok-47", "Grok 4.7", "grok CLI", "grok",
  "The most ambitious illustrations: sunsets, lighting, spray and texture. The hardware is hit and miss: run 3 has a pod and propeller under water, run 2 loses the mast entirely.",
  [("grok-4.7_medium", "Run 1", "medium", "233 s"), ("grok-4.7_medium_run2", "Run 2", "medium", "383 s"),
   ("grok-4.7_medium_run3", "Run 3", "medium", "276 s")]),
 ("grok-47bf", "Grok 4.7 Build Fast", "grok CLI", "grok",
  "Run 2 is the single most complete e-foil in the whole set: angled mast, fuselage, propeller, and a remote in hand. Runs 1 and 3 crop the penguin at the edge of the frame.",
  [("grok-4.7-build-fast_medium", "Run 1", "medium", "276 s"), ("grok-4.7-build-fast_medium_run2", "Run 2", "medium", "139 s"),
   ("grok-4.7-build-fast_medium_run3", "Run 3", "medium", "302 s")]),
 ("grok-46", "Grok 4.6", "grok CLI", "grok",
  "Warm, painterly scenes with a mast and an underwater wing every time. Run 1 is one of the few drawings outside Opus 5.5 with a remote.",
  [("grok-4.6_medium", "Run 1", "medium", "98 s"), ("grok-4.6_medium_run2", "Run 2", "medium", "115 s"),
   ("grok-4.6_medium_run3", "Run 3", "medium", "116 s")]),
 ("grok-45", "Grok 4.5", "grok CLI", "grok",
  "Flat clip-art. The board is drawn as an oval seen from above while the sea is seen from the side, a perspective mix-up that repeats in all three runs.",
  [("grok-4.5_medium", "Run 1", "medium", "64 s"), ("grok-4.5_medium_run2", "Run 2", "medium", "65 s"),
   ("grok-4.5_medium_run3", "Run 3", "medium", "76 s")]),
 ("gemini", "Gemini 3.8 Flash", "Antigravity (agy), modified prompt", "gemini",
  "Lively action poses, boards tilted mid-carve, a single mast every time, and a very stable style across low, medium and high effort. With the plain prompt it tried to run shell commands first and produced nothing, so these used the prompt plus “Output the SVG code as text in your reply; do not use any tools.”",
  [("gemini-3.8-flash_low_textprompt", "Low 1", "low", "35 s"), ("gemini-3.8-flash_low_textprompt_run2", "Low 2", "low", "70 s"),
   ("gemini-3.8-flash_low_textprompt_run3", "Low 3", "low", "55 s"),
   ("gemini-3.8-flash_medium_textprompt", "Medium 1", "medium", "94 s"), ("gemini-3.8-flash_medium_textprompt_run2", "Medium 2", "medium", "96 s"),
   ("gemini-3.8-flash_medium_textprompt_run3", "Medium 3", "medium", "90 s"),
   ("gemini-3.8-flash_high_textprompt", "High 1", "high", "112 s"), ("gemini-3.8-flash_high_textprompt_run2", "High 2", "high", "153 s"),
   ("gemini-3.8-flash_high_textprompt_run3", "High 3", "high", "171 s")]),
 ("gpt-oss", "GPT-OSS 120B", "Antigravity (agy)", "open",
  "Two pleasant illustrations with bold, patterned sombreros, but the foil is barely there. Run 3 collapses: a penguin in a grey box with no water at all.",
  [("gpt-oss-120b_medium", "Run 1", "medium", "310 s"), ("gpt-oss-120b_medium_run2", "Run 2", "medium", "151 s"),
   ("gpt-oss-120b_medium_run3", "Run 3", "medium", "15 s")]),
 ("qwen", "Qwen3.8-27B abliterated", "local, MTPLX on this Mac", "open",
  "At medium the e-foil changes shape every run: two masts, a board sunk to the waterline, a wing above the surface. At extra-high effort it gets a clean single-mast foil flying over the water, after 29 minutes and 29,587 thinking tokens.",
  [("qwen3.8-27b-abliterated-local_medium", "Run 1", "medium", "113 s"), ("qwen3.8-27b-abliterated-local_medium_run2", "Run 2", "medium", "145 s"),
   ("qwen3.8-27b-abliterated-local_medium_run3", "Run 3", "medium", "159 s"), ("qwen3.8-27b-abliterated-local_xhigh", "Extra-high", "xhigh", "29 min")]),
]

FAMILY = {"claude": "Claude 5.5", "claude-old": "Claude 4.6", "grok": "Grok", "gemini": "Gemini", "open": "Open weights"}

def esc(s): return html.escape(s, quote=True)

cards = []
nav = []
total = 0
for gid, name, harness, fam, note, runs in GROUPS:
    total += len(runs)
    nav.append(f'<a class="chip" href="#{gid}" data-fam="{fam}">{esc(name)}</a>')
    figs = []
    for key, run, effort, t in runs:
        alt = f"{name}, {run}: penguin in a sombrero on an e-foil"
        figs.append(
            f'<figure class="shot"><button class="zoom" type="button" data-src="img/{key}.jpg" data-cap="{esc(name)} · {esc(run)} · {esc(effort)} ({esc(t)})" aria-label="Enlarge {esc(name)} {esc(run)}">'
            f'<img src="img/{key}.jpg" alt="{esc(alt)}" loading="lazy"></button>'
            f'<figcaption><span class="run">{esc(run)}</span><span class="meta">{esc(effort)} · <span class="t">{esc(t)}</span></span></figcaption></figure>')
    cards.append(
        f'<section class="model" id="{gid}" data-fam="{fam}"><header class="mh"><div class="mh-top"><h3>{esc(name)}</h3>'
        f'<span class="fam fam-{fam}">{esc(FAMILY[fam])}</span></div><p class="harness">{esc(harness)} · {len(runs)} drawings</p>'
        f'<p class="note">{esc(note)}</p></header><div class="shots">{"".join(figs)}</div></section>')

page = open(os.path.join(HERE, "page_template.html")).read()
page = page.replace("{{NAV}}", "".join(nav)).replace("{{MODELS}}", "".join(cards)).replace("{{TOTAL}}", str(total))
open(OUT, "w").write(page)
print("wrote", OUT, "drawings:", total)
