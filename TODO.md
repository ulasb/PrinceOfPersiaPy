# Prince of Persia Python Port - Status & TODO

## Done — the game is playable end to end

- [x] Level extraction from original binaries (MAP room links, guard data,
      LINKLOC/LINKMAP button wiring) — all 14 levels + demo
- [x] Graphics extraction with NTSC artifact color (chtab sprites, bgtab
      background pieces)
- [x] FRAMEDEF.S / SEQTABLE.S machine-translated to Python data; original
      sequence bytecode interpreter drives all animation & movement
- [x] Player: run, turn, careful step, jumps, climb up/down, hang, falls
      with original damage thresholds, crouch
- [x] Tile machinery: pressure plates, gates (raise/drop/jam/timed close),
      exit doors, loose floors (shake/detach/fall/rubble/crush), spikes,
      slicers, potions (heal/life/float/poison), sword pickup
- [x] Guards: per-level enemy types, combat AI, strikes/blocks/damage
- [x] Game flow: title, HUD (health/level/time), death & restart, level
      progression, victory (level 14), 60-minute limit, quicksave/load
- [x] Synthesized sound effects
- [x] Headless harness + pytest suite (31 tests)

## Known gaps / future polish

- [ ] Level 12 shadow-merge sequence (shadow currently a normal guard)
- [ ] Level 3 skeleton resurrection ("arise" sequence exists, unused)
- [ ] Mirror reflection on level 4/12
- [ ] Cutscenes between levels (princess scenes)
- [ ] Crouch-roll under closing gates
- [ ] Fine-tune guard AI skill table against original AUTO.S
- [ ] Music (original had none on Apple II besides effects; optional)
- [ ] Gamepad support
- [ ] Background piece masks (AND-layer) for pixel-perfect room rendering

## Regenerating data

Clone the original source first (not committed):

    git clone https://github.com/jmechner/Prince-of-Persia-Apple-II.git source_reference
    python src/tools/export_levels.py     # levels -> assets/levels
    python src/tools/extract_images.py    # images -> assets/graphics
    python src/tools/parse_anim.py        # anim data -> src/data
