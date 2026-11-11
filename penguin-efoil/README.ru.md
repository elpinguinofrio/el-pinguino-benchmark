# Penguin E-Foil Benchmark

[English](README.md)

> Generate an SVG of a penguin wearing a sombrero riding an e-foil.

Альтернатива тесту Саймона Уиллисона [«пеликан на велосипеде»](https://github.com/simonw/pelican-bicycle): та же идея, но промпт, которого модели ещё не видели. 12 моделей, 44 рисунка, все без отбора.

<table>
<tr><td align="center"><img src="runs/opus-5.5/medium_run1.jpg" width="240" alt="Claude Opus 5.5"><br><sub><b>Claude Opus 5.5</b> · medium</sub></td><td align="center"><img src="runs/sonnet-5.5/medium_run1.jpg" width="240" alt="Claude Sonnet 5.5"><br><sub><b>Claude Sonnet 5.5</b> · medium</sub></td><td align="center"><img src="runs/haiku-5.5/medium_run1.jpg" width="240" alt="Claude Haiku 5.5"><br><sub><b>Claude Haiku 5.5</b> · medium</sub></td></tr>
<tr><td align="center"><img src="runs/opus-4.6/default_run1.jpg" width="240" alt="Claude Opus 4.6"><br><sub><b>Claude Opus 4.6</b> · default</sub></td><td align="center"><img src="runs/sonnet-4.6/default_run1.jpg" width="240" alt="Claude Sonnet 4.6"><br><sub><b>Claude Sonnet 4.6</b> · default</sub></td><td align="center"><img src="runs/grok-4.7/medium_run1.jpg" width="240" alt="Grok 4.7"><br><sub><b>Grok 4.7</b> · medium</sub></td></tr>
<tr><td align="center"><img src="runs/grok-4.7-build-fast/medium_run1.jpg" width="240" alt="Grok 4.7 Build Fast"><br><sub><b>Grok 4.7 Build Fast</b> · medium</sub></td><td align="center"><img src="runs/grok-4.6/medium_run1.jpg" width="240" alt="Grok 4.6"><br><sub><b>Grok 4.6</b> · medium</sub></td><td align="center"><img src="runs/grok-4.5/medium_run1.jpg" width="240" alt="Grok 4.5"><br><sub><b>Grok 4.5</b> · medium</sub></td></tr>
<tr><td align="center"><img src="runs/gemini-3.8-flash/low_run1.jpg" width="240" alt="Gemini 3.8 Flash"><br><sub><b>Gemini 3.8 Flash</b> · low</sub></td><td align="center"><img src="runs/gpt-oss-120b/medium_run1.jpg" width="240" alt="GPT-OSS 120B"><br><sub><b>GPT-OSS 120B</b> · medium</sub></td><td align="center"><img src="runs/qwen3.8-27b-abliterated/medium_run1.jpg" width="240" alt="Qwen3.8-27B abliterated"><br><sub><b>Qwen3.8-27B abliterated</b> · medium</sub></td></tr>
</table>

## Правила

- Промпт отправляется дословно, одна попытка, без нашего системного промпта.
- Средний уровень рассуждений (medium), где он настраивается. Три прогона на модель.
- Публикуется каждый рисунок. Неудачные попытки лежат в `runs/_failures/`.
- Каждый SVG проверяется на скрипты и ссылки до рендера.

## Добавить модель

```bash
python3 scripts/run_openai_compat.py --slug <model> --base-url http://127.0.0.1:8000/v1 --model <id> --run 1
python3 scripts/scan_svg.py
python3 scripts/render.py        # macOS
python3 scripts/build_site.py
```

Или положите `runs/<model>/medium_run1.svg` и `.json` вручную. Добавьте `model.json` и имя папки в `model_order` в `benchmark.json`.

## Файлы

```
benchmark.json        промпт, порядок моделей, тексты страницы (EN/RU)
runs/<model>/         SVG, рендер, метаданные и ответ модели для каждого прогона
docs/                 сгенерированная галерея (GitHub Pages)
```

Лицензия MIT. Вдохновлено [simonw/pelican-bicycle](https://github.com/simonw/pelican-bicycle).
