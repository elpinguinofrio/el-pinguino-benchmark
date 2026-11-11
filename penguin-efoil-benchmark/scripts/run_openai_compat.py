"""Run the benchmark prompt once against any OpenAI-compatible server (MTPLX, LM Studio, llama.cpp ...).

Writes runs/<model-slug>/<effort>_run<N>.{svg,json,raw.json}.

Usage:
  BENCH_API_KEY=... python3 scripts/run_openai_compat.py \
      --slug qwen3.8-27b-abliterated \
      --base-url http://127.0.0.1:8000/v1 --model <served-model-id> --effort medium --run 4

The API key is read from the BENCH_API_KEY environment variable (optional).
"""
import argparse, datetime, json, os, re, time, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("--slug", required=True, help="folder name under runs/")
ap.add_argument("--base-url", required=True)
ap.add_argument("--model", required=True)
ap.add_argument("--effort", default="medium")
ap.add_argument("--run", type=int, required=True)
ap.add_argument("--seed", type=int)
ap.add_argument("--max-tokens", type=int, default=48000)
a = ap.parse_args()

prompt = json.load(open("benchmark.json", encoding="utf-8"))["prompt"]
out_dir = f"runs/{a.slug}"
base = f"{out_dir}/{a.effort}_run{a.run}"
if os.path.exists(base + ".json"):
    raise SystemExit(f"refusing to overwrite {base}.json")
os.makedirs(out_dir, exist_ok=True)

body = {"model": a.model, "messages": [{"role": "user", "content": prompt}],
        "reasoning_effort": a.effort, "max_tokens": a.max_tokens}
if a.seed is not None:
    body["seed"] = a.seed
headers = {"Content-Type": "application/json"}
if os.environ.get("BENCH_API_KEY"):
    headers["Authorization"] = "Bearer " + os.environ["BENCH_API_KEY"]

t = time.time()
resp = json.load(urllib.request.urlopen(
    urllib.request.Request(a.base_url.rstrip("/") + "/chat/completions", json.dumps(body).encode(), headers),
    timeout=7200))
secs = round(time.time() - t)

json.dump(resp, open(base + ".raw.json", "w"), indent=1)
text = resp["choices"][0]["message"].get("content") or ""
m = re.search(r"<svg[\s\S]*?</svg>", text)
if m:
    open(base + ".svg", "w").write(m.group(0))
usage = resp.get("usage") or {}
meta = {"benchmark": "penguin-efoil", "model_id": a.model, "harness": "openai-compatible", "effort": a.effort,
        "run": a.run, "wall_time_s": secs, "date": datetime.date.today().isoformat(), "prompt_variant": "plain",
        "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")}
if a.seed is not None:
    meta["seed"] = a.seed
if not m:
    meta["failed"] = "no SVG in reply"
json.dump(meta, open(base + ".json", "w"), indent=2)
print(f"{base}: {secs}s, svg={'yes' if m else 'NO'}")
