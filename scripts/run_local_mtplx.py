"""Run penguin e-foil prompts A/B x3 against the local MTPLX server. Progress -> log."""
import json, os, re, time, urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "penguin")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.expanduser("~/.mtplx/logs/penguin_run.log")
KEY = os.environ.get("MTPLX_API_KEY", "")
URL = os.environ.get("MTPLX_URL", "http://localhost:8000/v1/chat/completions")
MODEL = "qwen3.8-27b-abliterated-mtplx-optimized-speed"
BASE = "Generate an SVG of a penguin wearing a sombrero riding an e-foil."
PROMPTS = {
    "A": BASE,
    "B": BASE + " An e-foil is a board on a vertical mast with an underwater wing"
               " and electric propeller; the board flies above the water.",
}
RUNS = 3

def log(msg):
    with open(LOG, "a") as f:
        f.write(time.strftime("%H:%M:%S ") + msg + "\n")

open(LOG, "w").close()
jobs = [(k, i) for i in range(1, RUNS + 1) for k in PROMPTS]
for n, (k, i) in enumerate(jobs, 1):
    log(f"[{n}/{len(jobs)}] start {k}{i}")
    body = {"model": MODEL, "messages": [{"role": "user", "content": PROMPTS[k]}],
            "reasoning_effort": "medium", "max_tokens": 16000, "seed": 100 + i}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {
        "Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
    t = time.time()
    try:
        r = json.load(urllib.request.urlopen(req, timeout=3600))
    except Exception as e:
        log(f"[{n}/{len(jobs)}] {k}{i} ERROR {e}"); continue
    dt = time.time() - t
    msg = r["choices"][0]["message"]
    text = msg.get("content") or ""
    json.dump(r, open(f"{OUT}/{k}{i}.json", "w"), indent=1)
    m = re.search(r"<svg[\s\S]*?</svg>", text)
    if m:
        open(f"{OUT}/{k}{i}.svg", "w").write(m.group(0))
    u = r.get("usage", {})
    log(f"[{n}/{len(jobs)}] done {k}{i} {dt:.0f}s finish={r['choices'][0].get('finish_reason')} "
        f"usage={json.dumps(u)} svg={'yes' if m else 'NO'}")
log("ALL DONE")
