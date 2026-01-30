# Prince of Persia Python Port - TODO List

## Immediate Next Steps (Priority 1)

### Asset Extraction & Conversion

- [x] **Study Apple II Graphics Format** ✅
  - [x] Research Apple II Double Hi-Res format (560x192, 16 colors)
  - [x] Understand pixel encoding in source files
  - [x] Find or create decoder for Apple II image format
  - [x] Test decoder on one sprite

- [x] **Extract Character Sprites** ✅
  - [x] Locate sprite data in `source_reference/01 POP Source/Images/`
  - [x] Extract Prince character frames
  - [x] Extract Guard character frames
  - [x] Convert to PNG format
  - [x] Create sprite sheets or individual frames
  - [x] Save to `assets/graphics/dump/` (602 sprites extracted)

- [ ] **Extract Environment Graphics** 🔄
  - [ ] Extract floor tiles
  - [ ] Extract walls and pillars
  - [ ] Extract gates and doors
  - [ ] Extract traps (spikes, chompers)
  [ ] Extract potions
  - [ ] Save to `assets/graphics/tiles/`

- [x] **Parse Level Data** ✅
  - [x] Study blueprint format in `source_reference/01 POP Source/Levels/`
  - [x] Understand BLUETYPE and BLUESPEC arrays
  - [x] Understand LINKLOC and LINKMAP for room connections
  - [x] Understand INFO structure for start positions
  - [x] Create Python parser for binary level format
  - [x] Convert all 15 levels to JSON
  - [x] Save to `assets/levels/level_XX.json`

## Core Systems (Priority 2)

### Graphics System

- [x] **Create Renderer** (`src/graphics/renderer.py`) ✅
  - [x] Implement sprite loading from PNG
  - [x] Create sprite caching system
  - [x] Implement sprite rendering with opacity
  - [x] Add coordinate scaling/transformation
  - [x] Test sprite rendering
  - [x] Add pre-rendered tile surfaces with gradients
  - [x] Enhance visual effects (borders, decorations)

- [ ] **Display Management** (`src/graphics/display.py`)
  - [ ] Implement screen setup
  - [ ] Add resolution scaling
  - [ ] Create viewport/camera system
  - [ ] Implement double buffering
  - [ ] Add fullscreen toggle

- [x] **Sprites** (`src/graphics/sprites.py`) ✅
  - [x] Create SpriteManager class
  - [x] Implement sprite loading and caching
  - [x] Add transparency support (colorkey)
  - [x] Create sprite scaling functions
  - [x] Add character sprite lookup by table/index

### Level System

- [x] **Level Loader** (`src/levels/loader.py`) ✅
  - [x] JSON level file reader
  - [x] Blueprint data structures
  - [x] Room/tile mapping
  - [x] Object placement
  - [x] Guard initialization from level data
  - [x] Binary format parser (original)

- [x] **Room Management** (`src/levels/room.py`) ✅
  - [x] Room class
  - [x] Tile grid system
  - [x] Room connections (left/right/up/down)
  - [x] Room rendering
  - [ ] Collision map generation

- [x] **Tile System** (`src/levels/data.py`) ✅
  - [x] Tile type definitions
  - [x] Tile properties (solid, trap, special)
  - [x] Tile rendering
  - [ ] Tile collision data

### Animation System

- [ ] **Port Animation Data**
  - [ ] Study SEQTABLE.S and SEQDATA.S
  - [ ] Create sequences.py with all animation sequences
  - [ ] Port frame definitions from FRAMEDEF.S
  - [ ] Convert to Python data structures

- [ ] **Animation Controller** (`src/animation/animator.py`)
  - [ ] Implement frame advancement (from FRAMEADV.S)
  - [ ] Sequence playback
  - [ ] Frame timing
  - [ ] Animation blending/transitions
  - [ ] Looping and one-shot animations

- [ ] **Frame Definitions** (`src/animation/frames.py`)
  - [ ] Frame data structure
  - [ ] Image references
  - [ ] Collision bounds
  - [ ] Movement offsets (dx, dy)
  - [ ] Frame flags

### Physics System

- [ ] **Movement** (`src/physics/movement.py`)
  - [ ] Port movement code from MOVER.S
  - [ ] Implement velocity and acceleration
  - [ ] Add position updates
  - [ ] Handle edge cases from original

- [ ] **Collision** (`src/physics/collision.py`)
  - [ ] Port collision code from COLL.S
  - [ ] Tile collision detection
  - [ ] Character-to-character collision
  - [ ] Sword combat collision
  - [ ] Barrier detection

- [ ] **Gravity** (`src/physics/gravity.py`)
  - [ ] Implement gravity system
  - [ ] Fall damage calculation
  - [ ] Landing detection
  - [ ] Hanging/climbing physics

## Character Systems (Priority 3)

### Player Character

- [ ] **Player Entity** (`src/entities/player.py`)
  - [ ] Character data structure (from GAMEEQ.S Char/Kid)
  - [ ] State machine
  - [ ] Input handling
  - [ ] Animation state selection
  - [ ] Health management

- [ ] **Player Actions**
  - [ ] Standing and turning
  - [ ] Walking and running
  - [ ] Jumping (standing and running)
  - [ ] Crouching
  - [ ] Climbing up/down
  - [ ] Hanging and dropping
  - [ ] Sword fighting
  - [ ] Taking damage
  - [ ] Dying

### Guards/Enemies

- [ ] **Guard Entity** (`src/entities/guard.py`)
  - [ ] Guard data structure
  - [ ] Port AI from AUTO.S
  - [ ] Guard behavior states
  - [ ] Combat AI
  - [ ] Death sequence

- [ ] **Shadow** (Level 12)
  - [ ] Shadow character variant
  - [ ] Mirror mechanics
  - [ ] Merging sequence

### Objects

- [ ] **Interactive Objects** (`src/entities/objects.py`)
  - [ ] Doors and gates
  - [ ] Pressure plates
  - [ ] Raising/lowering gates
  - [ ] Spikes (retractable)
  - [ ] Chompers
  - [ ] Loose floors
  - [ ] Potions
  - [ ] Swords
  - [ ] Exit doors

## Input System (Priority 4)

- [ ] **Keyboard Input** (`src/input/keyboard.py`)
  - [ ] Key mapping from original
  - [ ] Directional controls
  - [ ] Action buttons
  - [ ] Special keys (save, load, pause)
  - [ ] Debug keys (if enabled)

- [ ] **Gamepad Support** (`src/input/gamepad.py`)
  - [ ] Gamepad detection
  - [ ] Button mapping
  - [ ] Analog stick support
  - [ ] Configuration UI

## Audio System (Priority 5)

- [ ] **Sound Effects** (`src/audio/sound.py`)
  - [ ] Study SOUND.S
  - [ ] Extract or recreate sounds
  - [ ] Sound effect loading
  - [ ] Sound playback
  - [ ] Volume control

- [ ] **Music System** (`src/audio/music.py`)
  - [ ] Background music support
  - [ ] Track loading
  - [ ] Crossfading
  - [ ] Music triggers

## UI System (Priority 6)

- [ ] **HUD** (`src/ui/hud.py`)
  - [ ] Health meter (Kid)
  - [ ] Health meter (Opponent)
  - [ ] Time remaining
  - [ ] Level number
  - [ ] Message display

- [ ] **Menus** (`src/ui/menu.py`)
  - [ ] Title screen
  - [ ] Pause menu
  - [ ] Options menu
  - [ ] Load/save menu

## Game Logic (Priority 7)

- [ ] **Game Controller**
  - [ ] Level progression
  - [ ] Timer system (60 minute limit)
  - [ ] Death and respawn
  - [ ] Save game system
  - [ ] Load game system
  - [ ] Victory conditions

- [ ] **Special Mechanics**
  - [ ] Potion effects (health, poison, float, invert)
  - [ ] Mirror level mechanics
  - [ ] Gate/button interactions
  - [ ] Falling floor crumble
  - [ ] Skeleton resurrection

## Testing (Priority 8)

- [ ] **Unit Tests** (`tests/`)
  - [ ] Test constants
  - [ ] Test coordinate scaling
  - [ ] Test collision detection
  - [ ] Test animation sequencing
  - [ ] Test state transitions

- [ ] **Integration Tests**
  - [ ] Test level loading
  - [ ] Test player movement
  - [ ] Test combat system
  - [ ] Test save/load

- [ ] **Playtesting**
  - [ ] Test all 15 levels
  - [ ] Verify timing matches original
  - [ ] Check for bugs
  - [ ] Performance testing

## Polish (Priority 9)

- [ ] **Graphics Polish**
  - [ ] Smooth animations
  - [ ] Visual effects
  - [ ] Particle effects
  - [ ] Screen transitions

- [ ] **Gameplay Polish**
  - [ ] Fine-tune controls
  - [ ] Match original timing
  - [ ] Balance difficulty
  - [ ] Fix edge cases

- [ ] **Audio Polish**
  - [ ] Sound mixing
  - [ ] Volume balance
  - [ ] Audio triggers timing

## Documentation (Priority 10)

- [ ] **Code Documentation**
  - [ ] Complete all docstrings
  - [ ] Add inline comments for complex logic
  - [ ] Document assembly->Python translations

- [ ] **User Documentation**
  - [ ] User manual
  - [ ] Controls reference
  - [ ] Troubleshooting guide

- [ ] **Developer Documentation**
  - [ ] Architecture overview
  - [ ] API reference
  - [ ] Contributing guide

## Future Enhancements (Post-Release)

- [ ] HD graphics option
- [ ] New character skins
- [ ] Level editor
- [ ] Custom level support
- [ ] Achievements
- [ ] Speedrun mode
- [ ] Multiplayer/co-op
- [ ] Mod support

## Current Blockers

- **Graphics Extraction**: Need to decode Apple II image format
- **Level Format**: Need to fully understand binary level structure
- **Animation Data**: Need to extract frame definitions and sequences

## Quick Wins (Easy Tasks to Start)

1. ✅ Project setup - DONE
2. ✅ Constants ported - DONE
3. ✅ Basic game loop - DONE
4. Research Apple II graphics format
5. Create simple tile renderer (even just colored squares)
6. Load and display one level (with placeholder graphics)
7. Implement basic player movement (WASD)
8. Add simple collision with tile edges

## Notes

- Focus on getting something playable quickly, even with placeholder graphics
- Port game logic accurately first, polish later
- Test frequently to catch issues early
- Reference assembly source for exact behavior
- Keep commits atomic and well-documented

---

**Last Updated**: January 22, 2026
**Current Focus**: Asset extraction and level format analysis
