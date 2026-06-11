"""
Extract Apple II hi-res images from POP IMG.* table files to RGBA PNGs.

Table format (HIRES.S setimage/GETWIDTH):
    pointer for image n (n >= 1) is at table offset n*2-1, little-endian,
    an absolute memory address. Image data: width (bytes), height (rows),
    then width*height bitmap bytes, rows stored bottom-up.

Each bitmap byte holds 7 pixels, LSB leftmost; bit 7 selects the hi-res
color palette for that byte (violet/green vs blue/orange). Colors are
decoded with the standard NTSC artifact rules:
    - a set bit with a set horizontal neighbor renders white
    - an isolated set bit renders a color from (x parity, palette bit)
    - clear bits are transparent (the game composites with masks/OR)

The CHTAB files are linked at $6000; BGTAB files at $A000. We detect the
base address automatically from the first pointer instead of hardcoding.
"""

import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
IMAGES_DIR = REPO / "source_reference" / "01 POP Source" / "Images"
OUT_DIR = REPO / "assets" / "graphics"

# Apple II hi-res artifact colors
WHITE = (255, 255, 255, 255)
COLORS = {
    # (palette bit, x parity): RGBA
    (0, 0): (255, 68, 253, 255),   # violet
    (0, 1): (20, 245, 60, 255),    # green
    (1, 0): (20, 207, 253, 255),   # blue
    (1, 1): (255, 106, 60, 255),   # orange
}

TABLES = {
    "chtab": [
        "IMG.CHTAB1", "IMG.CHTAB2", "IMG.CHTAB3",
        "IMG.CHTAB4.GD", "IMG.CHTAB4.SKEL", "IMG.CHTAB4.SHAD",
        "IMG.CHTAB4.VIZ", "IMG.CHTAB4.FAT",
        "IMG.CHTAB5", "IMG.CHTAB6.A", "IMG.CHTAB6.B", "IMG.CHTAB7",
    ],
    "bgtab": [
        "IMG.BGTAB1.DUN", "IMG.BGTAB1.PAL",
        "IMG.BGTAB2.DUN", "IMG.BGTAB2.PAL",
    ],
}


def count_valid(data: bytes, base: int) -> int:
    """Count pointers that resolve to plausible image headers for a base."""
    count = 0
    for n in range(1, 192):
        off = n * 2 - 1
        if off + 1 >= len(data):
            break
        ptr = data[off] | (data[off + 1] << 8)
        o = ptr - base
        if not (0 <= o < len(data) - 2):
            continue
        w, h = data[o], data[o + 1]
        if 1 <= w <= 40 and 1 <= h <= 192 and o + 2 + w * h <= len(data):
            count += 1
    return count


def detect_base(data: bytes) -> int:
    """The table's pointer entries are absolute addresses; the file's link
    base is unknown per file, so pick the candidate base that makes the
    most pointers resolve to plausible image headers."""
    candidates = [0x6000, 0xA000, 0x2000, 0x4000, 0x8000, 0xB000, 0x1000]
    return max(candidates, key=lambda b: count_valid(data, b))


def decode_image(data: bytes, offset: int, phase: int = 0,
                 blend: bool = False) -> Image.Image | None:
    """Decode one image.

    phase: parity of the screen x the image will be drawn at; artifact
    colors depend on absolute screen position, so callers blit the
    matching variant.
    blend: approximate composite-video blur by filling 1-2px gaps inside
    dithered areas with a darker neighbor color (used for background
    pieces, where the artwork relies on CRT blending to look solid).
    """
    width = data[offset]
    height = data[offset + 1]
    if not (1 <= width <= 40 and 1 <= height <= 192):
        return None
    size = width * height
    if offset + 2 + size > len(data):
        return None
    bitmap = data[offset + 2: offset + 2 + size]

    px_w = width * 7
    img = Image.new("RGBA", (px_w, height), (0, 0, 0, 0))
    put = img.putpixel
    for row in range(height):
        # rows are stored bottom-up; PNG row 0 is the top
        y = height - 1 - row
        bits = []
        pals = []
        for bx in range(width):
            byte = bitmap[row * width + bx]
            pal = (byte >> 7) & 1
            for b in range(7):
                bits.append((byte >> b) & 1)
                pals.append(pal)
        rowpix = [None] * px_w
        for x in range(px_w):
            left = bits[x - 1] if x > 0 else 0
            right = bits[x + 1] if x < px_w - 1 else 0
            par = (x + phase) & 1
            if bits[x]:
                if left or right:
                    rowpix[x] = WHITE
                else:
                    # an isolated bit is a color pixel two hires px wide
                    color = COLORS[(pals[x], par)]
                    rowpix[x] = color
                    if x + 1 < px_w and not right:
                        rowpix[x + 1] = color
            elif left and right and rowpix[x] is None:
                # a gap inside an alternating bit pattern shows the same
                # color as its neighbors (1010 reads as a solid run)
                rowpix[x] = COLORS[(pals[x], (x - 1 + phase) & 1)]
        if blend:
            _blend_row(rowpix, px_w)
        for x in range(px_w):
            if rowpix[x] is not None:
                put((x, y), rowpix[x])
    return img


def _blend_row(rowpix, px_w: int) -> None:
    """Fill 1-2px transparent gaps between lit pixels with a dimmed
    neighbor color, the way a composite CRT smears dithered fills."""
    x = 0
    while x < px_w:
        if rowpix[x] is not None:
            x += 1
            continue
        start = x
        while x < px_w and rowpix[x] is None:
            x += 1
        gap = x - start
        if gap <= 2 and start > 0 and x < px_w:
            left, right = rowpix[start - 1], rowpix[x]
            src = left if left != WHITE else right
            fill = tuple(int(c * 0.55) for c in src[:3]) + (255,)
            for g in range(start, x):
                rowpix[g] = fill


def extract_table(path: Path, out_dir: Path, blend: bool) -> int:
    data = path.read_bytes()
    base = detect_base(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = path.name.replace("IMG.", "")
    count = 0
    for n in range(1, 192):
        ptr_off = n * 2 - 1
        if ptr_off + 1 >= len(data):
            break
        ptr = data[ptr_off] | (data[ptr_off + 1] << 8)
        if ptr == 0:
            continue
        offset = ptr - base
        if not (0 <= offset < len(data) - 2):
            continue
        img = decode_image(data, offset, phase=0, blend=blend)
        if img is None:
            continue
        img.save(out_dir / f"{name}_{n:03d}.png")
        odd = decode_image(data, offset, phase=1, blend=blend)
        odd.save(out_dir / f"{name}_{n:03d}_p1.png")
        count += 1
    print(f"{path.name}: base ${base:04x}, {count} images")
    return count


def main() -> int:
    total = 0
    for sub, names in TABLES.items():
        for name in names:
            path = IMAGES_DIR / name
            if not path.exists():
                print(f"missing: {path}")
                continue
            total += extract_table(path, OUT_DIR / sub, blend=(sub == "bgtab"))
    print(f"total: {total} images (plus odd-phase variants)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
