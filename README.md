# exif-orientation-guard

**Find and fix images whose stored size differs from their displayed size because of an EXIF orientation tag.**

[![test](https://github.com/Kein-chronicle/exif-orientation-guard/actions/workflows/test.yml/badge.svg)](https://github.com/Kein-chronicle/exif-orientation-guard/actions/workflows/test.yml) ![license](https://img.shields.io/badge/license-MIT-blue.svg)

## Why

Stored size is not displayed size. Some tools honor the tag and others ignore it, so an uploaded photo is measured as landscape and shown as portrait. Bake the orientation into the pixels once and judge sizes on the displayed image.

## Install

**As a Claude Code skill** (Claude uses it when the task matches the skill description):

```sh
git clone https://github.com/Kein-chronicle/exif-orientation-guard.git ~/.claude/skills/exif-orientation-guard
```

For a single project, clone into `<project>/.claude/skills/exif-orientation-guard` instead, then start a new Claude Code session.

**As plain scripts:**

```sh
git clone https://github.com/Kein-chronicle/exif-orientation-guard.git
cd exif-orientation-guard
```

**Requires:** Python 3.10+, Pillow.

Use the security-patched Pillow runtime:

```sh
python3 -m pip install -r requirements.txt
```

## Quick start

Detect and fix a tagged photo:

```console
$ bash examples/demo.sh
# The file is stored 200x100 but tag-aware viewers show it 100x200 (tag-ignoring tools still see 200x100). Find such files:
$ python3 scripts/normalize.py --check .demo-tmp
TAGGED  .demo-tmp/photo.png: orientation=6 stored=(200, 100) displayed=(100, 200)
1 file(s) carry an orientation tag
[exit 1]

# Bake the orientation into the pixels and drop the tag:
$ python3 scripts/normalize.py .demo-tmp/photo.png .demo-tmp/fixed.png
stored (200, 100) -> displayed (100, 200)
[exit 0]

$ python3 scripts/normalize.py --check .demo-tmp
clean (1 image(s) checked)
[exit 0]
```

The output above is real: it is produced by the files in `examples/`.

## Use it on your own files

```sh
python3 scripts/normalize.py --check ./photos
python3 scripts/normalize.py photo.jpg photo-fixed.jpg
```

Sample inputs for every file format are in `examples/` and `tests/`; the details are in [SKILL.md](SKILL.md).

## What it checks

- `normalize.py in out` rotates the pixels, removes only the orientation tag, keeps the ICC profile and other EXIF fields, keeps palettes, and prints `stored -> displayed`.
- `normalize.py --check DIR` exits `1` if any file carries a non-trivial orientation, `2` if the path is not a directory or a file cannot be read (never reported as clean).

## Limits

- Needs Pillow.
- JPEGs are re-encoded (quality 95); XMP and other non-EXIF metadata are not carried over; animated images are refused (exit 2).
- Output format follows the output file extension.

## Related projects

These solve neighbouring problems; use them when they fit better.

- **Pillow `ImageOps.exif_transpose`, ImageMagick `-auto-orient`, `exiftran -a`**: do the same rotation; this adds a directory check you can put in CI

## More from the same collection

Small, tested tools that grew out of running AI agents and game/app pipelines for months:

- [**safe-delete-sole-copy-check**](https://github.com/Kein-chronicle/safe-delete-sole-copy-check): Before you delete a project folder: is any of it the only copy? Checks the live remote, unpushed commits and tags, untracked and ignored files, and verifies copies by hash.
- [**macos-tcc-automation-permissions**](https://github.com/Kein-chronicle/macos-tcc-automation-permissions): Make unattended macOS automation survive permission resets: AppleScript -1743/-1728, launchd jobs, screen recording, and real vs synthetic clicks.
- [**ios-simulator-ui-test-hygiene**](https://github.com/Kein-chronicle/ios-simulator-ui-test-hygiene): Keep iOS simulator UI tests and crash-fuzz runs from dying on a laptop: the 16 GB memory wall and the crash-report dialog that never goes away.

## Development

```sh
python3 tests/test_normalize.py
```

The tests include inputs that are supposed to be rejected, so a green run also shows the checks can fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).

If this saved you a debugging session, a star helps other people find it. Bug reports and failing test cases are even better.

<sub>Keywords: exif, image-processing, python, pillow, ios, photos, orientation, claude-skills</sub>
