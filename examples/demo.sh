#!/usr/bin/env bash
cd "$(dirname "$0")/.."
run() { printf '$ %s\n' "$*"; "$@"; printf '[exit %s]\n\n' "$?"; }
tmp=.demo-tmp; rm -rf "$tmp"; mkdir "$tmp"; trap 'rm -rf "$tmp"' EXIT
python3 - "$tmp" <<'PY'
import sys
from PIL import Image
im = Image.new("RGB", (200, 100), (255, 0, 0)); ex = Image.Exif(); ex[0x0112] = 6      # stored landscape, tag says "rotate 90"
im.save(sys.argv[1] + "/photo.png", exif=ex)
PY
echo "# The file is stored 200x100 but tag-aware viewers show it 100x200 (tag-ignoring tools still see 200x100). Find such files:"
run python3 scripts/normalize.py --check "$tmp"
echo "# Bake the orientation into the pixels and drop the tag:"
run python3 scripts/normalize.py "$tmp/photo.png" "$tmp/fixed.png"
rm "$tmp/photo.png"
run python3 scripts/normalize.py --check "$tmp"
