#!/usr/bin/env python3
"""Bake EXIF orientation into pixels. usage: normalize.py in out | --check dir"""
import os, sys
from PIL import Image, ImageOps

EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def orientation(im):
    return im.getexif().get(0x0112, 1)


def normalize(src, dst):
    """Rotate the pixels, drop ONLY the orientation tag, keep the ICC profile and the other EXIF fields. Palette images keep their palette."""
    with Image.open(src) as im:
        stored = im.size
        icc = im.info.get("icc_profile")
        exif = im.getexif()
        fixed = ImageOps.exif_transpose(im)       # returns a rotated copy (and for tag 1 a plain copy), palette preserved
        exif.pop(0x0112, None)
        kw = {}
        if icc: kw["icc_profile"] = icc
        if len(exif): kw["exif"] = exif
        if dst.lower().endswith((".jpg", ".jpeg")): kw["quality"] = 95        # JPEG must be re-encoded; do not silently drop to the default quality
        if getattr(im, "is_animated", False): raise ValueError("animated images are not supported (only the first frame would be kept)")
        fixed.save(dst, **kw)
        return stored, fixed.size


def check(root):
    """exit 0 clean, 1 at least one tagged file, 2 not a directory or a file could not be read (never reported as clean)."""
    if not os.path.isdir(root):
        print(f"not a directory: {root}"); return 2
    bad = unreadable = seen = 0
    def walk_error(error):
        nonlocal unreadable
        unreadable += 1
    for d, dirs, fs in os.walk(root, onerror=walk_error):
        for name in dirs[:]:
            if os.path.islink(os.path.join(d, name)):
                unreadable += 1; dirs.remove(name)
        for f in fs:
            if os.path.splitext(f)[1].lower() not in EXTS:
                continue
            p = os.path.join(d, f); seen += 1
            try:
                with Image.open(p) as im:
                    o = orientation(im)
                    if o != 1:
                        bad += 1
                        print(f"TAGGED  {p}: orientation={o} stored={im.size} displayed={ImageOps.exif_transpose(im).size}")
            except Exception as e:
                unreadable += 1; print(f"UNREADABLE  {p}: {type(e).__name__}")
    if unreadable: print(f"{unreadable} file(s) could not be read; {bad} tagged"); return 2
    if not seen: print("UNMEASURED: no supported images"); return 3
    print(f"clean ({seen} image(s) checked)" if not bad else f"{bad} file(s) carry an orientation tag")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        sys.exit(check(sys.argv[2]))
    if len(sys.argv) == 3:
        try:
            s, d = normalize(sys.argv[1], sys.argv[2])
        except (OSError, ValueError) as e:           # unreadable input, unknown output extension, animated image
            print(f"error: {e}"); sys.exit(2)
        print(f"stored {s} -> displayed {d}")
        sys.exit(0)
    print(__doc__); sys.exit(2)
