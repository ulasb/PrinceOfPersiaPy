# Prince of Persia - Python Port

A playable port of the classic Prince of Persia (Apple II, 1989) by Jordan
Mechner, built in Python with PyGame — driven by the **original game data**:
levels, sprites, frame definitions and animation sequences are all extracted
or machine-translated from the released 6502 source.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/status-Playable-green.svg)

![Level 1](docs/screenshots/level1_start.png)
![Combat](docs/screenshots/combat.png)

## What works

- **All 14 levels + demo level**, loaded from the original binary blueprints
  (room tiles, room links, gate/button wiring, guards, start positions)
- **Authentic animation**: the original SEQTABLE bytecode runs in a small
  interpreter; frame definitions (FRAMEDEF) map every frame to the original
  sprite images, including per-frame movement deltas — so the rotoscoped
  feel survives
- **Original graphics**: sprites and background pieces extracted from the
  Apple II image tables with NTSC artifact color decoding; rooms composed
  with the original piece tables (BGDATA)
- Running, turning, careful steps, standing/running jumps, climbing up and
  down, hanging, falling with the original damage thresholds
- Pressure plates, gates, exit doors, loose floors, spikes, slicers,
  potions, sword pickup
- Guards with sword combat (advance/retreat/strike/block), per-level enemy
  types (guard, skeleton, fat guard, shadow, vizier)
- Health, level progression, 60-minute time limit, death/restart,
  quicksave/quickload, synthesized retro sound effects
- Headless test suite covering movement, traps, combat and progression

Not (yet) implemented: the level 12 shadow-merge sequence, level 3 skeleton
resurrection, mirror reflections and cutscenes; those levels still load and
play with standard mechanics.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Options: `--level N` start level, `--scale N` window scale (default 4),
`--mute` disable sound.

## Controls

| Key | Action |
| --- | ------ |
| ← / → | turn, run |
| Shift + ← / → | careful step |
| ↑ | jump, climb up, enter open exit |
| ↓ | crouch, climb down over an edge |
| Shift | grab ledge while falling, pick up / drink, **strike** in combat |
| ↑ in combat | parry |
| ↓ in combat | sheathe sword |
| R | restart level |
| F5 / F9 | quicksave / quickload |
| `[` / `]` | previous / next level (debug) |
| Esc | pause |

## How the port works

```
source_reference/          original Apple II source (clone of jmechner/
                           Prince-of-Persia-Apple-II; not committed)
src/tools/
  export_levels.py         binary blueprints -> assets/levels/*.json
  extract_images.py        image tables -> assets/graphics/**/*.png
  parse_anim.py            FRAMEDEF.S + SEQTABLE.S -> src/data/*.py
src/
  data/                    generated frame & sequence data
  entities/char.py         sequence interpreter (ANIMCHAR port)
  entities/player.py       input -> sequence decisions (CTRL layer)
  entities/guard.py        guard AI
  levels/level.py          tiles, links, gates/plates/spikes/loose floors
  graphics/                asset loading, BGDATA piece renderer, HUD
  game/game.py             per-tick simulation & game states
```

The original 2304-byte level format, the LINKLOC/LINKMAP button-to-gate
wiring, the sequence bytecode instructions (goto/chx/chy/act/setfall/...),
frame check-mark bits, and the geometry tables (14px blocks, 63px rows,
FloorY) were all reverse-confirmed against the assembly before porting.

To regenerate the data, clone the original source into `source_reference/`:

```bash
git clone https://github.com/jmechner/Prince-of-Persia-Apple-II.git source_reference
python src/tools/export_levels.py
python src/tools/extract_images.py
python src/tools/parse_anim.py
```

## Tests

```bash
pip install pytest
pytest tests/test_game.py
```

`tests/harness.py` also runs scripted scenarios headlessly:

```bash
python tests/harness.py --level 1 --script "16:, 30:r" --out /tmp/shot.png
```

For end-to-end verification of the real app (window, input, render
loop), use [pygame-pilot](https://github.com/ulasb/pygame-pilot), which
frame-steps the unmodified game and captures what a player would see:

```bash
python -m pygamepilot start --cwd . --python venv/bin/python -- src/main.py --mute
python -m pygamepilot adv 6 --tap return          # leave the title screen
python -m pygamepilot adv 60 --down right --shot running
python -m pygamepilot stop
```

## License & Legal

The original Prince of Persia source code is copyright © Jordan Mechner;
the franchise belongs to Ubisoft. This port is for educational and
preservation purposes only and must not be distributed commercially.

> "As the author and copyright holder of this source code, I personally
> have no problem with anyone studying it, modifying it, attempting to run
> it... This does NOT constitute a grant of rights of any kind in Prince of
> Persia." — Jordan Mechner

## Credits

- **Jordan Mechner** — the original game and the source release
- Python port built on PyGame
