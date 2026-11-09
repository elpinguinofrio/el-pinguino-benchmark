"""Build page/index.html for the penguin e-foil benchmark from the run list below."""
import html, os, re

def esc(s): return html.escape(s, quote=True)

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

# ---- Russian translation. English stays in the HTML; Russian rides along in data-ru* attributes. ----
FAMILY_RU = {"open": "Открытые веса"}

def ru_plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11: return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return few
    return many

GROUP_RU = {  # group id -> (harness, note)
 "opus-55": ("субагент Claude Code",
  "Самая стабильная модель в тесте. В каждом прогоне на среднем уровне есть полный электрофойл: одна мачта, мотор с пропеллером, крыло под водой и пульт в ласте у пингвина. Все четыре рисунка почти неотличимы."),
 "sonnet-55": ("субагент Claude Code",
  "Каждый раз один и тот же плоский стиль: мачта и крыло, доска скользит по воде. Ни в одном прогоне нет ни пропеллера, ни пульта; в первом прогоне вместо пульта из ласта свисает трос, как у кайта."),
 "haiku-55": ("субагент Claude Code",
  "Самый слабый Claude. Сомбреро превращаются в ковбойские шляпы и панамы, в двух прогонах доска стоит в воде, а в первом весь фойл поднят над морем."),
 "opus-46": ("Antigravity (agy)",
  "Маленький пингвин, простая сцена, тонкая мачта с крылом. Ни пропеллера, ни пульта. Рядом с Opus 5.5 это самый заметный разрыв между поколениями в тесте."),
 "sonnet-46": ("Antigravity (agy)",
  "Разнообразнее, чем Sonnet 5.5: один динамичный кадр в повороте, один с мотором. Сомбреро выходят похожими на абажуры или чепчики. В третьем прогоне модель вызвала генератор изображений вместо того, чтобы написать SVG, поэтому он не показан."),
 "grok-47": ("grok CLI",
  "Самые амбициозные иллюстрации: закаты, освещение, брызги и текстуры. С техникой как повезёт: в третьем прогоне под водой есть мотор с пропеллером, а во втором мачта пропала совсем."),
 "grok-47bf": ("grok CLI",
  "Второй прогон — самый полный электрофойл во всём наборе: наклонная мачта, фюзеляж, пропеллер и пульт в руке. В первом и третьем прогонах пингвин обрезан краем кадра."),
 "grok-46": ("grok CLI",
  "Тёплые живописные сцены, и каждый раз есть мачта и крыло под водой. Первый прогон — один из немногих рисунков, кроме Opus 5.5, где есть пульт."),
 "grok-45": ("grok CLI",
  "Плоский клипарт. Доска нарисована овалом сверху, а море — сбоку; эта путаница с перспективой повторяется во всех трёх прогонах."),
 "gemini": ("Antigravity (agy), изменённый промпт",
  "Живые позы в движении, доски наклонены в повороте, каждый раз одна мачта и очень стабильный стиль на низком, среднем и высоком уровне. С обычным промптом модель сначала пыталась запускать команды в терминале и ничего не нарисовала, поэтому здесь к промпту добавлено: «Output the SVG code as text in your reply; do not use any tools.»"),
 "gpt-oss": ("Antigravity (agy)",
  "Две симпатичные иллюстрации с яркими узорчатыми сомбреро, но фойла почти не видно. Третий прогон развалился: пингвин в сером прямоугольнике и никакой воды."),
 "qwen": ("локально, MTPLX на этом Mac",
  "На среднем уровне электрофойл меняет форму в каждом прогоне: две мачты, доска утоплена по ватерлинию, крыло над поверхностью. На очень высоком уровне получается чистый фойл с одной мачтой над водой — через 29 минут и 29 587 токенов размышлений."),
}
EFFORT_RU = {"low": "низкий", "medium": "средний", "high": "высокий", "xhigh": "очень высокий", "default": "по умолчанию"}
RUN_RU = {"Run": "Прогон", "Earlier": "Ранее", "Low": "Низкий", "Medium": "Средний", "High": "Высокий", "Extra-high": "Очень высокий"}

def run_ru(run):
    head, _, num = run.partition(" ")
    return (RUN_RU[head] + (" " + num if num else ""))

def time_ru(t):
    return t.replace(" min", " мин").replace(" s", " с").replace("n/a", "н/д")

def drawings_ru(n): return f"{n} {ru_plural(n, 'рисунок', 'рисунка', 'рисунков')}"

def ru_attr(name, value): return f' data-ru{"-" + name if name else ""}="{esc(value)}"'



cards = []
nav = []
total = 0
for gid, name, harness, fam, note, runs in GROUPS:
    total += len(runs)
    h_ru, note_ru = GROUP_RU[gid]
    nav.append(f'<a class="chip" href="#{gid}" data-fam="{fam}">{esc(name)}</a>')
    figs = []
    for key, run, effort, t in runs:
        alt = f"{name}, {run}: penguin in a sombrero on an e-foil"
        r_ru, e_ru, t_ru = run_ru(run), EFFORT_RU[effort], time_ru(t)
        meta_ru = f'{esc(e_ru)} · <span class="t">{esc(t_ru)}</span>'
        figs.append(
            f'<figure class="shot"><button class="zoom" type="button" data-src="img/{key}.jpg" data-cap="{esc(name)} · {esc(run)} · {esc(effort)} ({esc(t)})"'
            f'{ru_attr("cap", f"{name} · {r_ru} · {e_ru} ({t_ru})")} aria-label="Enlarge {esc(name)} {esc(run)}"{ru_attr("label", f"Увеличить: {name}, {r_ru}")}>'
            f'<img src="img/{key}.jpg" alt="{esc(alt)}"{ru_attr("alt", f"{name}, {r_ru}: пингвин в сомбреро на электрофойле")} loading="lazy"></button>'
            f'<figcaption><span class="run"{ru_attr("", esc(r_ru))}>{esc(run)}</span><span class="meta"{ru_attr("", meta_ru)}>{esc(effort)} · <span class="t">{esc(t)}</span></span></figcaption></figure>')
    fam_ru = FAMILY_RU.get(fam, FAMILY[fam])
    cards.append(
        f'<section class="model" id="{gid}" data-fam="{fam}"><header class="mh"><div class="mh-top"><h3>{esc(name)}</h3>'
        f'<span class="fam fam-{fam}"{ru_attr("", esc(fam_ru))}>{esc(FAMILY[fam])}</span></div>'
        f'<p class="harness"{ru_attr("", esc(h_ru) + " · " + drawings_ru(len(runs)))}>{esc(harness)} · {len(runs)} drawings</p>'
        f'<p class="note"{ru_attr("", esc(note_ru))}>{esc(note)}</p></header><div class="shots">{"".join(figs)}</div></section>')

# Static page text. Values are HTML (they replace innerHTML), attributes get escaped on insert.
RU = {
 "doc_title": "Бенчмарк El Pinguino",
 "doc_desc": "Один промпт, 12 моделей ИИ: пингвин в сомбреро на электрофойле, нарисованный в SVG.",
 "title": "Бенчмарк El Pinguino",
 "hero_eyebrow": "Мой собственный пеликан · 9 ноября 2026",
 "hero_lead": "Промпт «пеликан на велосипеде» стал настолько известным, что модели, скорее всего, уже обучались на нём. Это свежая замена, которую раньше никто не видел. <strong>Пингвин, сомбреро и электрическая доска на подводном крыле</strong>: легко представить, но трудно нарисовать правильно, если не знаешь, как устроен электрофойл.",
 "prompt_label": "Промпт дословно",
 "copy": "Скопировать промпт",
 "stat_models": "моделей",
 "stat_drawings": ru_plural(total, "рисунок", "рисунка", "рисунков"),
 "stat_prompt": "промпт",
 "diagram": "Схема электрофойла: доска над водой, одна мачта уходит к фюзеляжу с передним и задним крылом и пропеллером, райдер держит пульт в руке",
 "lbl_remote": "пульт", "lbl_board": "доска", "lbl_one_mast": "одна мачта", "lbl_propeller": "пропеллер",
 "lbl_front_wing": "переднее крыло", "lbl_rear_wing": "заднее крыло", "lbl_waterline": "ватерлиния",
 "diagram_cap": "Что нужно для правильного рисунка. Доска летит над водой, всё, что под ней, остаётся под водой.",
 "find_eyebrow": "Что показывают рисунки",
 "find_h2": "Пингвина рисуют все. Разницу делает электрофойл.",
 "find_lead": "Каждая модель ставит пингвина на доску и надевает ему сомбреро. Разница — в технике под доской и в том, может ли модель нарисовать её одинаково дважды.",
 "f1_t": "Opus 5.5 знает устройство",
 "f1_p": "Во всех трёх прогонах на среднем уровне есть одна мачта, мотор с пропеллером, крыло под водой и пульт в руке. Ни одна другая модель не собрала всё это даже дважды.",
 "f2_t": "Grok рисует лучшие картинки",
 "f2_p": "Grok 4.6 и 4.7 делают настоящие иллюстрации со светом, брызгами и закатами. Техника то появляется, то пропадает, но второй прогон Grok 4.7 Build Fast — самый полный электрофойл в наборе.",
 "f3_t": "От старого Claude к новому — большой скачок",
 "f3_p": "Opus 4.6 рисует крошечного пингвина на голой палке. Opus 5.5 каждый раз рисует мотор и пульт. Sonnet 4.6 живее, чем Sonnet 5.5, но не точнее.",
 "f4_t": "Маленькие модели ошибаются с доской",
 "f4_p": "Haiku 5.5, Grok 4.5 и прогоны Qwen на среднем уровне топят доску, поднимают крыло из воды или рисуют доску не под тем углом.",
 "f5_t": "Размышления помогают локальному Qwen, но медленно",
 "f5_p": "На среднем уровне фойл у Qwen меняет форму в каждом прогоне. На очень высоком он рисует чистый и правильный фойл, но тратит 29 минут на одну картинку.",
 "f6_t": "Агентные оболочки мешают",
 "f6_p": "Gemini 3.8 Flash запускал команды в терминале вместо того, чтобы рисовать, поэтому понадобилась лишняя строка «без инструментов». Sonnet 4.6 однажды вызвал генератор изображений. В третьем прогоне GPT-OSS забыл про воду.",
 "nav_label": "Перейти к модели",
 "method_eyebrow": "Метод и ограничения",
 "method_h2": "Как проводился тест",
 "m1": "<b>Один промпт, одна попытка.</b> Без системного промпта и подсказок по стилю с моей стороны, без повторов, кроме случаев, когда прогон вообще не дал SVG.",
 "m2": "<b>Средний уровень усилий, где модель это позволяет.</b> Antigravity не принимает настройку усилий для Opus 4.6 и Sonnet 4.6, поэтому они работали со значением по умолчанию.",
 "m3": "<b>Разные оболочки.</b> Claude 5.5 работал как субагенты Claude Code, Grok — через grok CLI, Gemini, GPT-OSS и Claude 4.6 — через Antigravity, а Qwen — на этом Mac. Grok и Antigravity добавляют собственные системные промпты агента, которые нельзя отключить.",
 "m4": "<b>Время — реальное, по часам</b>, включает запуск, а для пакета в VM — ещё и параллельные прогоны. Это не тест скорости.",
 "m5": "<b>Gemini нельзя сравнивать напрямую.</b> В его промпте было одно дополнительное предложение с просьбой ответить текстом без инструментов.",
 "m6": "<b>Три пробы на модель — это подсказка, а не рейтинг.</b> Один локальный прогон Qwen уже выглядел совсем не так, как следующий.",
 "m7": "<b>Безопасность.</b> Перед рендерингом каждый SVG проверялся на скрипты, обработчики событий и ссылки. Ничего такого не нашлось.",
 "lightbox": "Увеличенный рисунок",
 "close": "Закрыть",
}
I18N_ATTR = {"": "", "-label": "label", "-content": "content"}

page = open(os.path.join(HERE, "page_template.html")).read()
page = page.replace("{{NAV}}", "".join(nav)).replace("{{MODELS}}", "".join(cards)).replace("{{TOTAL}}", str(total))
used = set()
def tag(m):
    used.add(m[2]); return ru_attr(I18N_ATTR[m[1]], RU[m[2]]).lstrip()
page = re.sub(r'data-i18n(|-label|-content)="(\w+)"', tag, page)
assert used == set(RU), sorted(set(RU) - used)
open(OUT, "w").write(page)
print("wrote", OUT, "drawings:", total)
