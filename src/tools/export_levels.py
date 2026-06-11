"""
Export original Apple II Prince of Persia level files to JSON.

Blueprint format (2304 bytes), from EQ.S `dum blueprnt`:

    BLUETYPE  ds 24*30   ; tile type byte per block (24 screens x 30 blocks)
    BLUESPEC  ds 24*30   ; tile spec/modifier byte per block
    LINKLOC   ds 256     ; gate/button link table (location byte)
    LINKMAP   ds 256     ; gate/button link table (screen/timer byte)
    MAP       ds 24*4    ; per-screen links: left, right, up, down (0 = none)
    INFO      ds 256     ; start positions & guards (offsets below)

INFO offsets (from EQ.S `dum INFO`):
    +64 KidStartScrn, +65 KidStartBlock, +66 KidStartFace
    +68 SwStartScrn, +69 SwStartBlock
    +71 GdStartBlock[24], +95 GdStartFace[24], +119 GdStartX[24],
    +143 GdStartSeqL[24], +167 GdStartProg[24], +191 GdStartSeqH[24]

Screens are numbered 1-24 (0 = no screen). Guard arrays are indexed by
screen-1: at most one guard per screen, block 30+ = no guard.

Tile ids (BGDATA.S "Indexed by PIECE ID#"):
    0 space, 1 floor, 2 spikes, 3 posts, 4 gate, 5 dpressplate,
    6 pressplate, 7 panelwif, 8 pillarbottom, 9 pillartop, 10 flask,
    11 loose, 12 panelwof, 13 mirror, 14 rubble, 15 upressplate,
    16 exit, 17 exit2, 18 slicer, 19 torch, 20 block, 21 bones,
    22 sword, 23 window, 24 window2, 25 archbot, 26-29 archtop1-4
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEVELS_DIR = REPO / "source_reference" / "01 POP Source" / "Levels"
OUT_DIR = REPO / "assets" / "levels"

BLUEPRINT_SIZE = 2304
BLUETYPE = 0
BLUESPEC = 720
LINKLOC = 1440
LINKMAP = 1696
MAP = 1952
INFO = 2048

TILE_NAMES = [
    "space", "floor", "spikes", "posts", "gate", "dpressplate",
    "pressplate", "panelwif", "pillarbottom", "pillartop", "flask",
    "loose", "panelwof", "mirror", "rubble", "upressplate",
    "exit", "exit2", "slicer", "torch", "block", "bones",
    "sword", "window", "window2", "archbot", "archtop1", "archtop2",
    "archtop3", "archtop4",
]


def signed_face(b: int) -> int:
    """Original: 0 = facing right, $FF = facing left."""
    return -1 if b == 0xFF else 1


def export_level(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) != BLUEPRINT_SIZE:
        raise ValueError(f"{path.name}: bad size {len(data)}")

    rooms = {}
    for scrn in range(1, 25):
        base = (scrn - 1) * 30
        tiles = [
            [data[BLUETYPE + base + row * 10 + col] for col in range(10)]
            for row in range(3)
        ]
        specs = [
            [data[BLUESPEC + base + row * 10 + col] for col in range(10)]
            for row in range(3)
        ]
        m = MAP + (scrn - 1) * 4
        rooms[str(scrn)] = {
            "links": {
                "left": data[m],
                "right": data[m + 1],
                "up": data[m + 2],
                "down": data[m + 3],
            },
            "tiles": tiles,
            "specs": specs,
        }

    info = data[INFO:INFO + 256]
    guards = []
    for i in range(24):
        block = info[71 + i]
        if block >= 30:
            continue
        guards.append({
            "room": i + 1,
            "block": block,
            "face": signed_face(info[95 + i]),
            "x": info[119 + i],
            "seq": info[143 + i] | (info[191 + i] << 8),
            "prog": info[167 + i],
        })

    level_number = int(path.name.replace("LEVEL", ""))
    return {
        "level_number": level_number,
        "rooms": rooms,
        "linkloc": list(data[LINKLOC:LINKLOC + 256]),
        "linkmap": list(data[LINKMAP:LINKMAP + 256]),
        "info": {
            "kid": {
                "room": info[64],
                "block": info[65],
                "face": signed_face(info[66]),
            },
            "sword": {"room": info[68], "block": info[69]},
            "guards": guards,
        },
    }


def validate(level: dict) -> list:
    """Check that room links are mutual; return list of warnings."""
    warnings = []
    opposite = {"left": "right", "right": "left", "up": "down", "down": "up"}
    for scrn, room in level["rooms"].items():
        for d, other in room["links"].items():
            if other == 0:
                continue
            if not 1 <= other <= 24:
                warnings.append(f"room {scrn} {d} -> invalid {other}")
                continue
            back = level["rooms"][str(other)]["links"][opposite[d]]
            if back != int(scrn):
                warnings.append(
                    f"room {scrn} {d} -> {other}, but {other} "
                    f"{opposite[d]} -> {back}"
                )
    return warnings


def ascii_map(level: dict) -> str:
    """Render room connectivity as a grid by walking links from kid start."""
    pos = {}  # room -> (gx, gy)
    start = level["info"]["kid"]["room"]
    stack = [(start, 0, 0)]
    seen = set()
    while stack:
        room, x, y = stack.pop()
        if room in seen or room == 0:
            continue
        seen.add(room)
        pos[room] = (x, y)
        links = level["rooms"][str(room)]["links"]
        stack += [
            (links["left"], x - 1, y), (links["right"], x + 1, y),
            (links["up"], x, y - 1), (links["down"], x, y + 1),
        ]
    if not pos:
        return "(no rooms)"
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    grid = [
        ["  ." for _ in range(min(xs), max(xs) + 1)]
        for _ in range(min(ys), max(ys) + 1)
    ]
    for room, (x, y) in pos.items():
        grid[y - min(ys)][x - min(xs)] = f"{room:3d}"
    return "\n".join("".join(row) for row in grid)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for n in range(15):
        path = LEVELS_DIR / f"LEVEL{n}"
        if not path.exists():
            print(f"missing: {path}")
            ok = False
            continue
        level = export_level(path)
        warnings = validate(level)
        out = OUT_DIR / f"level_{n:02d}.json"
        out.write_text(json.dumps(level))
        kid = level["info"]["kid"]
        print(
            f"level {n:2d}: kid room {kid['room']} block {kid['block']} "
            f"face {kid['face']:+d}, {len(level['info']['guards'])} guards"
            + (f", {len(warnings)} link warnings" if warnings else "")
        )
        for w in warnings:
            print(f"    {w}")
    print("\nLevel 1 room map (numbers = screen ids):")
    print(ascii_map(export_level(LEVELS_DIR / "LEVEL1")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
