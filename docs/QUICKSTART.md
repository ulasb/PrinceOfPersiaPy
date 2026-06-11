# Quickstart

## Play

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Press Enter on the title screen. Arrows move; Shift is the action button
(careful step, grab, pick up, strike). See README.md for the full control
table and CLI options (`--level`, `--scale`, `--mute`).

## Develop

The game logic runs at 12 ticks/second on a 280x192 virtual canvas
(original geometry: 10 blocks x 14px wide, 3 rows x 63px tall per room).

Run the tests:

```bash
pip install pytest
pytest tests/test_game.py
```

Drive scripted scenarios headlessly and capture screenshots:

```bash
python tests/harness.py --level 1 --script "16:, 30:r, 10:r+u" --out /tmp/s.png
```

Script segments are `ticks:keys` with keys `l r u d s` (shift).

## Regenerate data from the original source

```bash
git clone https://github.com/jmechner/Prince-of-Persia-Apple-II.git source_reference
python src/tools/export_levels.py
python src/tools/extract_images.py
python src/tools/parse_anim.py
```

Key generated artifacts:

- `assets/levels/level_NN.json` — tiles, specs, room links, button wiring
- `assets/graphics/chtab/` — character sprites (facing left)
- `assets/graphics/bgtab/` — background pieces (DUN/PAL variants)
- `src/data/framedefs.py`, `src/data/seqdata.py` — animation data
