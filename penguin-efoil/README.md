# Penguin E-Foil Benchmark

[Русская версия](README.ru.md)

> Generate an SVG of a penguin wearing a sombrero riding an e-foil.

An alternative to Simon Willison's [pelican riding a bicycle](https://github.com/simonw/pelican-bicycle): same idea, a prompt models haven't seen yet. 12 models, 44 drawings, all shown.

<table>
<tr><td align="center"><img src="runs/opus-5.5/medium_run1.jpg" width="240" alt="Claude Opus 5.5"><br><sub><b>Claude Opus 5.5</b> · medium</sub></td><td align="center"><img src="runs/sonnet-5.5/medium_run1.jpg" width="240" alt="Claude Sonnet 5.5"><br><sub><b>Claude Sonnet 5.5</b> · medium</sub></td><td align="center"><img src="runs/haiku-5.5/medium_run1.jpg" width="240" alt="Claude Haiku 5.5"><br><sub><b>Claude Haiku 5.5</b> · medium</sub></td></tr>
<tr><td align="center"><img src="runs/opus-4.6/default_run1.jpg" width="240" alt="Claude Opus 4.6"><br><sub><b>Claude Opus 4.6</b> · default</sub></td><td align="center"><img src="runs/sonnet-4.6/default_run1.jpg" width="240" alt="Claude Sonnet 4.6"><br><sub><b>Claude Sonnet 4.6</b> · default</sub></td><td align="center"><img src="runs/grok-4.7/medium_run1.jpg" width="240" alt="Grok 4.7"><br><sub><b>Grok 4.7</b> · medium</sub></td></tr>
<tr><td align="center"><img src="runs/grok-4.7-build-fast/medium_run1.jpg" width="240" alt="Grok 4.7 Build Fast"><br><sub><b>Grok 4.7 Build Fast</b> · medium</sub></td><td align="center"><img src="runs/grok-4.6/medium_run1.jpg" width="240" alt="Grok 4.6"><br><sub><b>Grok 4.6</b> · medium</sub></td><td align="center"><img src="runs/grok-4.5/medium_run1.jpg" width="240" alt="Grok 4.5"><br><sub><b>Grok 4.5</b> · medium</sub></td></tr>
<tr><td align="center"><img src="runs/gemini-3.8-flash/low_run1.jpg" width="240" alt="Gemini 3.8 Flash"><br><sub><b>Gemini 3.8 Flash</b> · low</sub></td><td align="center"><img src="runs/gpt-oss-120b/medium_run1.jpg" width="240" alt="GPT-OSS 120B"><br><sub><b>GPT-OSS 120B</b> · medium</sub></td><td align="center"><img src="runs/qwen3.8-27b-abliterated/medium_run1.jpg" width="240" alt="Qwen3.8-27B abliterated"><br><sub><b>Qwen3.8-27B abliterated</b> · medium</sub></td></tr>
</table>

## Rules

- Prompt sent verbatim, one shot, no system prompt from us.
- Medium reasoning effort where a model has the setting. Three runs per model.
- Every drawing is published. Failed attempts stay in `runs/_failures/`.
- Every SVG is scanned for scripts and links before rendering.

## Add a model

```bash
python3 scripts/run_openai_compat.py --slug <model> --base-url http://127.0.0.1:8000/v1 --model <id> --run 1
python3 scripts/scan_svg.py
python3 scripts/render.py        # macOS
python3 scripts/build_site.py
```

Or save `runs/<model>/medium_run1.svg` plus a `.json` by hand. Add `model.json` and the slug to `model_order` in `benchmark.json`.

## Files

```
benchmark.json        prompt, model order, page text (EN/RU)
runs/<model>/         SVG, render, metadata, raw reply per run
docs/                 generated gallery (GitHub Pages)
```

MIT License. Inspired by [simonw/pelican-bicycle](https://github.com/simonw/pelican-bicycle).
