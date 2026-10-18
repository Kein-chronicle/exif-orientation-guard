import os, subprocess, sys, tempfile
from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(here, "..", "scripts", "normalize.py")
d = tempfile.mkdtemp()
src = os.path.join(d, "tagged.png")
im = Image.new("RGB", (200, 100), (255, 0, 0))     # stored landscape 200x100
ex = Image.Exif(); ex[0x0112] = 6                   # tag: rotate 90 -> displays 100x200
im.save(src, exif=ex)

ok = True
def expect(name, cond):
    global ok; ok &= bool(cond); print(("ok   " if cond else "FAIL ") + name)

r = subprocess.run([sys.executable, script, "--check", d], capture_output=True, text=True)
expect("detects tagged file (exit 1)", r.returncode == 1)
out = os.path.join(d, "fixed.png")
r = subprocess.run([sys.executable, script, src, out], capture_output=True, text=True)
expect("normalize prints stored->displayed", "stored (200, 100) -> displayed (100, 200)" in r.stdout)
with Image.open(out) as f:
    expect("output pixels are 100x200 and untagged", f.size == (100, 200) and f.getexif().get(0x0112, 1) == 1)
os.remove(src)
r = subprocess.run([sys.executable, script, "--check", d], capture_output=True, text=True)
expect("clean directory passes (exit 0)", r.returncode == 0)
# palette image keeps its colours, ICC profile survives, other EXIF survives, missing dir is not "clean"
pal = Image.new("P", (4, 2)); pal.putpalette([10, 200, 30] + [0, 0, 0] * 255); pal.putpixel((0, 0), 0)
pe = Image.Exif(); pe[0x0112] = 6; pe[0x010F] = "TestMaker"; pp = os.path.join(d, "pal.png"); pal.save(pp, exif=pe)
po = os.path.join(d, "pal_out.png"); subprocess.run([sys.executable, script, pp, po], capture_output=True)
with Image.open(po) as q:
    rgb = q.convert("RGB"); expect("palette colours survive the rotation", (10, 200, 30) in {rgb.getpixel((x, y)) for x in range(rgb.width) for y in range(rgb.height)})
    expect("other EXIF fields survive, orientation tag is gone", q.getexif().get(0x010F) == "TestMaker" and q.getexif().get(0x0112, 1) == 1)
jp = os.path.join(d, "icc.jpg"); icc = b"\0" * 128
try:
    Image.new("RGB", (8, 4), (1, 2, 3)).save(jp, icc_profile=icc, exif=pe); jo = os.path.join(d, "icc_out.jpg")
    subprocess.run([sys.executable, script, jp, jo], capture_output=True)
    with Image.open(jo) as q: expect("ICC profile is carried over", q.info.get("icc_profile") == icc)
except Exception as e: print("skip icc test:", e)
r = subprocess.run([sys.executable, script, "--check", os.path.join(d, "nope")], capture_output=True, text=True)
expect("--check on a missing directory is exit 2, not clean", r.returncode == 2)
open(os.path.join(d, "broken.png"), "wb").write(b"not an image")
r = subprocess.run([sys.executable, script, "--check", d], capture_output=True, text=True)
expect("a corrupt image is exit 2 (UNREADABLE), not 'tagged'", r.returncode == 2 and "UNREADABLE" in r.stdout)
r = subprocess.run([sys.executable, script, pp, os.path.join(d, "noext")], capture_output=True, text=True)
expect("output without a known extension is exit 2, not a traceback", r.returncode == 2 and "Traceback" not in r.stderr)
empty = tempfile.mkdtemp()
r = subprocess.run([sys.executable, script, "--check", empty], capture_output=True, text=True)
expect("empty image set is unmeasured (exit 3)", r.returncode == 3)
sys.exit(0 if ok else 1)
