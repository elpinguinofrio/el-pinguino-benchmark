"""Build the gallery for GitHub Pages from benchmark.json and runs/.

  docs/index.html      English
  docs/ru/index.html   Russian
  docs/img/*.jpg       renders copied from runs/
  README.md, README.ru.md  front pages for GitHub

Usage: python3 scripts/build_site.py [--repo-url URL]
The GitHub link defaults to the `origin` remote; it is left out when there is none.
"""
import glob, html, json, os, re, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TEMPLATE = open(os.path.join(ROOT, "scripts", "template.html"), encoding="utf-8").read()
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "default"]
OUT = os.path.join(ROOT, "docs")

def esc(s):
    return html.escape(str(s), quote=True)

def plural(n, forms, lang):
    if lang == "ru":
        if n % 10 == 1 and n % 100 != 11:
            return forms[0]
        if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
            return forms[1]
        return forms[2]
    return forms[0] if n == 1 else forms[1]

def fmt_time(s, t):
    if s is None:
        return "n/a"
    return f"{round(s / 60)} {t['time_min']}" if s >= 600 else f"{s} {t['time_s']}"

def repo_url():
    if "--repo-url" in sys.argv:
        return sys.argv[sys.argv.index("--repo-url") + 1]
    try:
        u = subprocess.run(["git", "-C", ROOT, "remote", "get-url", "origin"],
                           capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return ""
    m = re.match(r"(?:git@github\.com:|https://github\.com/)([^/]+/[^/]+?)(?:\.git)?$", u)
    return f"https://github.com/{m.group(1)}" if m else ""

def load_runs(cfg):
    models = []
    for slug in cfg["model_order"]:
        mdir = f"{ROOT}/runs/{slug}"
        model = json.load(open(f"{mdir}/model.json", encoding="utf-8"))
        runs = []
        for mpath in glob.glob(f"{mdir}/*_run*.json"):
            if mpath.endswith(".raw.json"):
                continue
            meta = json.load(open(mpath))
            jpg = mpath[:-5] + ".jpg"
            if meta.get("failed") or not os.path.exists(jpg):
                continue
            runs.append((meta, jpg))
        runs.sort(key=lambda r: (EFFORT_ORDER.index(r[0]["effort"]) if r[0]["effort"] in EFFORT_ORDER else 9, r[0]["run"]))
        if runs:
            models.append((slug, model, runs))
    return models

def build(cfg, models, lang, prefix, repo):
    t = cfg[lang]
    nav, sections, total = [], [], 0
    for slug, model, runs in models:
        mixed = len({m["effort"] for m, _ in runs}) > 1
        figs = []
        for meta, jpg in runs:
            name = f"{slug}_{os.path.basename(jpg)}"
            src = f"{prefix}img/{name}"
            label = f"{meta['effort']} {meta['run']}" if mixed else f"{t['run']} {meta['run']}"
            tm = fmt_time(meta.get("wall_time_s"), t)
            alt = f"{model['name']}, {label}: {cfg['prompt']}"
            figs.append(
                f'<figure class="shot"><button class="zoom" type="button" data-src="{esc(src)}" '
                f'data-cap="{esc(model["name"])} · {esc(label)} · {esc(meta["effort"])} ({esc(tm)})" '
                f'aria-label="{esc(model["name"])} {esc(label)}"><img src="{esc(src)}" alt="{esc(alt)}" loading="lazy"></button>'
                f'<figcaption><span class="run">{esc(label)}</span><span class="meta">{esc(meta["effort"])} · '
                f'<span class="t">{esc(tm)}</span></span></figcaption></figure>')
        total += len(runs)
        fam = model.get("family", "open")
        nav.append(f'<a class="chip" href="#{esc(slug)}">{esc(model["name"])}</a>')
        sections.append(
            f'<section class="model" id="{esc(slug)}"><header class="mh"><div class="mh-top"><h3>{esc(model["name"])}</h3>'
            f'<span class="fam fam-{esc(fam)}">{esc(t["family"].get(fam, fam))}</span>'
            f'<span class="harness">{esc(model.get("harness_label", ""))}</span></div>'
            f'<p class="note">{esc(model["note"][lang])}</p></header><div class="shots">{"".join(figs)}</div></section>')
    diagram = open(f"{ROOT}/diagram.svg", encoding="utf-8").read()
    for en, tr in t.get("diagram_labels", {}).items():
        diagram = diagram.replace(f'class="a-label">{en}</text>', f'class="a-label">{esc(tr)}</text>')
    n = len(sections)
    top = [f'<a class="pill" href="{t["other_href"]}" hreflang="{"ru" if lang == "en" else "en"}">{esc(t["other_lang"])}</a>']
    if repo:
        top.append(f'<a class="pill" href="{esc(repo)}">GitHub</a>')
    footer = [f'<span>{esc(t["source"])}: <a href="{esc(repo)}">{esc(repo.replace("https://", ""))}</a></span>'] if repo else []
    footer += ['<span>MIT License</span>',
               f'<span><a href="{esc(cfg["pelican_url"])}">simonw/pelican-bicycle</a></span>']
    vals = {
        "TITLE": esc(t["title"]), "DESC": esc(cfg["prompt"]),
        "EYEBROW": esc(cfg["first_run"]),
        "TOPLINKS": "".join(top),
        "TAGLINE": esc(t["tagline"].replace("{N_MODELS}", f"{n} {plural(n, t['models'], lang)}")),
        "PELICAN": t["pelican"].replace("{PELICAN}", esc(cfg["pelican_url"])),
        "PROMPT_LABEL": esc(t["prompt_label"]), "COPY": esc(t["copy"]), "COPIED": esc(t["copied"]),
        "PROMPT": esc(cfg["prompt"]),
        "MODELS_COUNT": str(n), "MODELS_WORD": esc(plural(n, t["models"], lang)),
        "TOTAL": str(total), "DRAWINGS_WORD": esc(plural(total, t["drawings"], lang)),
        "PROMPTS_WORD": esc(plural(1, t["prompts"], lang)),
        "DIAGRAM": diagram, "DIAGRAM_CAPTION": esc(t["diagram_caption"]),
        "TAKEAWAYS_HEAD": esc(t["takeaways_head"]),
        "TAKEAWAYS": "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in t["takeaways"]),
        "NAV": "".join(nav), "MODELS": "".join(sections),
        "METHOD_HEAD": esc(t["method_head"]), "METHOD": "".join(f"<li>{esc(x)}</li>" for x in t["method"]),
        "FOOTER": "".join(footer), "CLOSE": esc(t["close"]),
    }
    nowrap = '<span style="white-space:nowrap">e-foil</span>'
    vals["PROMPT"] = vals["PROMPT"].replace("e-foil", nowrap)
    page = TEMPLATE.replace("<h1>{{TITLE}}</h1>", "<h1>" + vals["TITLE"].replace("E-Foil", nowrap.replace("e-foil", "E-Foil")) + "</h1>")
    for k, v in vals.items():
        page = page.replace("{{" + k + "}}", v)
    assert "{{" not in page, re.findall(r"\{\{\w+\}\}", page)
    head, body = page.split('<div class="wrap">', 1)
    alt_lang = "ru" if lang == "en" else "en"
    doc = (f'<!doctype html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
           '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
           f'<link rel="alternate" hreflang="{alt_lang}" href="{t["other_href"]}">\n'
           + head + '</head>\n<body>\n<div class="wrap">' + body + "\n</body>\n</html>\n")
    return doc, n, total

README = {
 "en": """# Penguin E-Foil Benchmark

[Русская версия](README.ru.md){PAGES_LINK}

> {PROMPT}

An alternative to Simon Willison's [pelican riding a bicycle]({PELICAN}): same idea, a prompt models haven't seen yet. {N} models, {T} drawings, all shown.

{GRID}

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

MIT License. Inspired by [simonw/pelican-bicycle]({PELICAN}).
""",
 "ru": """# Penguin E-Foil Benchmark

[English](README.md){PAGES_LINK}

> {PROMPT}

Альтернатива тесту Саймона Уиллисона [«пеликан на велосипеде»]({PELICAN}): та же идея, но промпт, которого модели ещё не видели. {N} {N_WORD}, {T} {T_WORD}, все без отбора.

{GRID}

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

Лицензия MIT. Вдохновлено [simonw/pelican-bicycle]({PELICAN}).
""",
}

def pages_url(repo):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)$", repo or "")
    return f"https://{m.group(1).lower()}.github.io/{m.group(2)}/" if m else ""

def write_readmes(cfg, models, repo):
    cells = []
    for slug, model, runs in models:
        meta, jpg = runs[0]
        rel = os.path.relpath(jpg, ROOT)
        cells.append(f'<td align="center"><img src="{rel}" width="240" alt="{esc(model["name"])}"><br><sub><b>{esc(model["name"])}</b> · {esc(meta["effort"])}</sub></td>')
    rows = ["<tr>" + "".join(cells[i:i + 3]) + "</tr>" for i in range(0, len(cells), 3)]
    grid = "<table>\n" + "\n".join(rows) + "\n</table>"
    total = sum(len(r) for _, _, r in models)
    pages = pages_url(repo)
    for lang, name in [("en", "README.md"), ("ru", "README.ru.md")]:
        link = ""
        if pages:
            link = f" · **[{'Gallery' if lang == 'en' else 'Галерея'} →]({pages}{'' if lang == 'en' else 'ru/'})**"
        t = cfg[lang]
        text = (README[lang].replace("{PAGES_LINK}", link).replace("{PROMPT}", cfg["prompt"])
                .replace("{PELICAN}", cfg["pelican_url"]).replace("{GRID}", grid)
                .replace("{N_WORD}", plural(len(models), t["models"], lang)).replace("{T_WORD}", plural(total, t["drawings"], lang))
                .replace("{N}", str(len(models))).replace("{T}", str(total)))
        open(f"{ROOT}/{name}", "w", encoding="utf-8").write(text)
        print(name, "written", "(gallery link: " + (pages or "none") + ")")

def main():
    cfg = json.load(open(f"{ROOT}/benchmark.json", encoding="utf-8"))
    models = load_runs(cfg)
    repo = repo_url()
    if os.path.exists(OUT):
        shutil.rmtree(OUT)   # docs/ is generated output, rebuilt from runs/ every time
    os.makedirs(f"{OUT}/img")
    os.makedirs(f"{OUT}/ru")
    for slug, _, runs in models:
        for _, jpg in runs:
            shutil.copy2(jpg, f"{OUT}/img/{slug}_{os.path.basename(jpg)}")
    for lang, path, prefix in [("en", "index.html", ""), ("ru", "ru/index.html", "../")]:
        doc, n, total = build(cfg, models, lang, prefix, repo)
        open(f"{OUT}/{path}", "w", encoding="utf-8").write(doc)
        print(f"docs/{path}: {n} models, {total} drawings")
    open(f"{OUT}/.nojekyll", "w").close()
    write_readmes(cfg, models, repo)
    print("repo link:", repo or "(none)")

if __name__ == "__main__":
    main()
