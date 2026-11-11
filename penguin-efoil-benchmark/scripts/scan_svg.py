"""Check SVGs for anything that could run or load content when opened.

Usage: python3 scripts/scan_svg.py [paths...]   (default: every SVG under runs/)
Exit code 1 if any file has a finding.
"""
import glob, re, sys

PATTERNS = {
    "script tag": re.compile(r"<\s*script", re.I),
    "event handler": re.compile(r"\son[a-z]+\s*=", re.I),   # onload=, onclick= ... (not maskContentUnits=)
    "link": re.compile(r"\b(xlink:)?href\s*=", re.I),
    "foreignObject": re.compile(r"<\s*foreignObject", re.I),
    "javascript: URL": re.compile(r"javascript:", re.I),
    "external url()": re.compile(r"url\(\s*['\"]?\s*https?:", re.I),
}

def scan(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    return [name for name, rx in PATTERNS.items() if rx.search(text)]

def main(argv):
    paths = argv or sorted(glob.glob("runs/**/*.svg", recursive=True))
    bad = 0
    for p in paths:
        hits = scan(p)
        if hits:
            bad += 1
            print(f"FLAG {p}: {', '.join(hits)}")
    print(f"scanned {len(paths)} SVGs, {bad} flagged")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
