# El Pinguino Benchmark

My own AI model benchmarks, in the spirit of the "pelican riding a bicycle" test.

**Live site:** https://elpinguinofrio.github.io/el-pinguino-benchmark/

## Penguin E-Foil Benchmark

One prompt, 12 models, 44 SVG drawings: *"Generate an SVG of a penguin wearing a sombrero riding an e-foil."*
Gallery in English and Russian: [https://elpinguinofrio.github.io/el-pinguino-benchmark/penguin-efoil/docs/](https://elpinguinofrio.github.io/el-pinguino-benchmark/penguin-efoil/docs/) · details in [`penguin-efoil/`](penguin-efoil/).

## Games

Games built by AI models in one session each. Folder names start with the model and effort.

| Game | Model | Effort | Play | Notes |
|---|---|---|---|---|
| [Voxel Titanic](games/fable-5.2-high-voxel-titanic/) | Fable 5.2 | high | [play](https://elpinguinofrio.github.io/el-pinguino-benchmark/games/fable-5.2-high-voxel-titanic/) | Single-file browser game |
| [Vibe Coder 2](games/fable-5.2-high-vibe-coder-2/) | Fable 5.2 | high | [play](https://elpinguinofrio.github.io/el-pinguino-benchmark/games/fable-5.2-high-vibe-coder-2/) | Built in Claude Code with a hard deadline |
| [ASCII Tetris](games/qwen3.8-27b-abliterated-ascii-tetris/) | Qwen3.8-27B abliterated (local, MTPLX) | default | `python3 tetris.py` | Unfinished. Terminal game, written through the pi agent; the write was blocked, so the code was recovered from the session log and has never been run |
