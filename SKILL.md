---
name: exif-orientation-guard
description: Fix image-pipeline bugs caused by EXIF orientation - screenshots that "are landscape" by file size but display portrait, OCR boxes that crop the wrong area, store-screenshot size checks that disagree between tools, or generated images that look rotated 90 degrees only in some tools. Use when measuring, cropping, validating or uploading images produced by simulators, phones, or AI image tools.
---

# exif-orientation-guard

**Stored size and displayed size can differ.** A PNG with an `eXIf` Orientation tag may store
2752x2064 but display 2064x2752.

Tools disagree:
- honour the tag: Apple Vision (OCR) - and its coordinates are in *displayed* space
- ignore the tag: PIL `Image.size`, `sips -g pixelWidth/pixelHeight`

Consequences: OCR-coordinate crops hit empty areas; a "landscape" guard that checked stored size accepted screenshots that were never actually landscape; size validation done with `sips` went wrong.

## Rules

1. Decide orientation from the **displayed** size: `ImageOps.exif_transpose(im).size`.
2. When saving captures, **bake the rotation into pixels and strip the tag** (`scripts/normalize.py`).
   Leaving the tag means each tool sees a different picture.
3. If orientation is still wrong after normalizing, **do not rotate to make it pass.** A portrait UI
   turned sideways is a fake landscape that tricks the gate. Record a failure.
4. A gate that measures the *symptom* ("crop looked empty") cannot be forged in tests. Find the
   cause (the tag) and gate on that - deterministic, no thresholds, no false positives.

## Use

```bash
python3 scripts/normalize.py in.png out.png        # bakes orientation, strips tag, prints stored->displayed
python3 scripts/normalize.py --check dir/          # exit 1 if any file has a non-trivial orientation tag
python3 tests/test_normalize.py                    # builds a tagged fixture and verifies
```

Runtime dependency: install `requirements.txt` with `python3 -m pip install -r requirements.txt`. Pillow must be at least 12.3.0; optional model dependencies listed above are separate.
