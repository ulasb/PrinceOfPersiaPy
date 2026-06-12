"""
Assemble a gameplay recording (recordings/rec_*/frame_*.png) into an
animated GIF for sharing.

    python src/tools/make_gif.py recordings/rec_20260611_120000 [out.gif]
                                 [--scale N]
"""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("recording", type=Path)
    parser.add_argument("out", type=Path, nargs="?")
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()

    frames = sorted(args.recording.glob("frame_*.png"))
    if not frames:
        print(f"no frames in {args.recording}", file=sys.stderr)
        return 1
    meta = {}
    meta_path = args.recording / "meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    tps = meta.get("ticks_per_second", 12)

    images = []
    for f in frames:
        img = Image.open(f).convert("P", palette=Image.ADAPTIVE)
        if args.scale > 1:
            img = img.resize((img.width * args.scale,
                              img.height * args.scale), Image.NEAREST)
        images.append(img)

    out = args.out or args.recording.with_suffix(".gif")
    images[0].save(out, save_all=True, append_images=images[1:],
                   duration=int(1000 / tps), loop=0, optimize=True)
    print(f"wrote {out} ({len(images)} frames at {tps} fps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
