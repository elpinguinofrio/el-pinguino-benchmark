"""Render SVGs to trimmed JPEGs next to them (runs/<model>/<effort>_runN.jpg).

macOS only: uses Quick Look (qlmanage) to rasterize, Pillow to trim and compress.
Only renders SVGs that pass scripts/scan_svg.py. Skips SVGs that already have a .jpg
unless --force is given.

Usage: python3 scripts/render.py [--force] [paths...]
"""
import glob, os, subprocess, sys, tempfile
from PIL import Image, ImageChops

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_svg import scan

def render(svg, tmp):
    subprocess.run(["qlmanage", "-t", "-s", "800", "-o", tmp, svg],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    png = os.path.join(tmp, os.path.basename(svg) + ".png")
    im = Image.open(png).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
    if box:
        im = im.crop(box)
    im.thumbnail((720, 720))
    out = svg[:-4] + ".jpg"
    im.save(out, quality=82, optimize=True)
    return out

def main(argv):
    force = "--force" in argv
    paths = [a for a in argv if a != "--force"] or sorted(glob.glob("runs/**/*.svg", recursive=True))
    with tempfile.TemporaryDirectory() as tmp:   # intermediates removed on success and failure
        for svg in paths:
            if not force and os.path.exists(svg[:-4] + ".jpg"):
                continue
            hits = scan(svg)
            if hits:
                print(f"SKIP {svg}: flagged ({', '.join(hits)})")
                continue
            print("rendered", render(svg, tmp))

if __name__ == "__main__":
    main(sys.argv[1:])
