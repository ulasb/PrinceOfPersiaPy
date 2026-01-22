# Prince of Persia Python Port - Project Plan

## Overview
This project aims to port the classic Prince of Persia game from Apple II 6502 assembly language to Python using PyGame. We will create a faithful recreation of the original game mechanics while modernizing the codebase and removing the copy protection system.

## Source Material
- Original repository: https://github.com/jmechner/Prince-of-Persia-Apple-II
- Language: 6502 Assembly Language
- Platform: Apple II (with Double Hi-Res graphics)
- Source code created: 1985-1989

## Key Components to Port

### 1. Core Game Systems
- **MASTER.S** - Main game controller, disk I/O, level loading
- **CTRL.S** - Main control loop and input handling  
- **CTRLSUBS.S** - Control subroutines
- **TOPCTRL.S** - Top-level control flow

### 2. Graphics Systems
- **GRAFIX.S** - Graphics rendering routines
- **HIRES.S** - Hi-res graphics functions
- **HRTABLES.S** - Hi-res lookup tables
- **HRPARAMS.S** - Hi-res parameters
- **GAMEBG.S** - Game background rendering
- **BGDATA.S** - Background data

### 3. Animation & Movement
- **AUTO.S** - Character automation/AI
- **FRAMEADV.S** - Frame advancement
- **FRAMEDEF.S** - Frame definitions
- **MOVER.S** - Movement routines
- **MOVEDATA.S** - Movement data
- **SEQTABLE.S** - Animation sequence tables
- **SEQDATA.S** - Animation sequence data

### 4. Collision & Physics
- **COLL.S** - Collision detection
- **SUBS.S** - General subroutines
- **TABLES.S** - Lookup tables

### 5. Audio
- **SOUND.S** - Sound effects system
- **SOUNDNAMES.S** - Sound effect names

### 6. Special Features
- **SPECIALK.S** - Special keys and cheats

### 7. Data Files
- **Levels/** - Level data (15 levels)
- **Images/** - Graphics assets
- **UNPACK.S** - Data decompression routines

### 8. Game Data
- **EQ.S** - Equates/constants
- **GAMEEQ.S** - Game-specific equates

### 9. Copy Protection (TO BE REMOVED)
- **03 Disk Protection/** - Copy protection system
- BBund ID system in MASTER.S
- RW18 disk routines

## Port Strategy

### Phase 1: Foundation (Week 1-2)
1. **Project Setup**
   - Create Python/PyGame project structure
   - Set up version control
   - Create documentation
   
2. **Constants & Data Structures**
   - Port EQ.S and GAMEEQ.S constants
   - Define Python equivalents for assembly data structures
   - Create enumerations for game states, animation sequences, etc.

3. **Asset Extraction**
   - Extract and convert graphics from Apple II format
   - Extract level data
   - Extract sound effects (if possible)

### Phase 2: Core Systems (Week 3-4)
1. **Display System**
   - Create PyGame window and rendering pipeline
   - Port hi-res graphics system to modern resolution
   - Implement double buffering
   - Create sprite rendering system

2. **Level System**
   - Port level data format
   - Create level loader
   - Implement tile/room system
   - Create background rendering

3. **Input System**
   - Port keyboard controls
   - Add gamepad support (modern enhancement)

### Phase 3: Character & Animation (Week 5-6)
1. **Animation System**
   - Port SEQTABLE and SEQDATA
   - Create sprite animation framework
   - Implement frame definitions (FRAMEDEF)
   - Frame advancement system (FRAMEADV)

2. **Movement System**
   - Port movement routines (MOVER)
   - Implement physics and positioning
   - Character state machine

3. **Player Character**
   - Implement Prince character
   - Running, jumping, climbing mechanics
   - Sword fighting mechanics
   - Collision with environment

### Phase 4: Game Logic (Week 7-8)
1. **Collision System**
   - Port COLL.S collision detection
   - Implement tile-based collision
   - Character-to-character collision
   - Sword combat collision

2. **Enemy AI**
   - Port AUTO.S guard AI
   - Guard behavior states
   - Combat AI

3. **Special Mechanics**
   - Doors and gates
   - Pressure plates
   - Spikes and traps
   - Potions
   - Falling floors
   - Mirrors

### Phase 5: Game Flow (Week 9-10)
1. **Game States**
   - Title screen
   - Level progression
   - Game over
   - Victory conditions
   - Time limit system

2. **Save/Load System**
   - Save game data (without disk protection)
   - Load game data
   - Level checkpointing

3. **Audio System**
   - Port sound effects (SOUND.S)
   - Add music (may use MIDI or modern audio)
   - Sound triggers

### Phase 6: Polish & Testing (Week 11-12)
1. **Graphics Enhancement**
   - Smooth animations
   - Visual effects
   - Modern resolution support
   - Fullscreen/windowed modes

2. **Gameplay Tuning**
   - Match original timing
   - Control responsiveness
   - Difficulty balance

3. **Testing**
   - Playtest all 15 levels
   - Bug fixes
   - Performance optimization

### Phase 7: Documentation & Release (Week 13-14)
1. **Documentation**
   - User manual
   - Developer documentation
   - Code comments
   - Architecture overview

2. **Packaging**
   - Create installers
   - Cross-platform testing
   - Release builds

## Technical Architecture

### Directory Structure
```
PrinceOfPersiaPy/
├── source_reference/      # Original Apple II source (for reference)
├── src/
│   ├── main.py           # Entry point
│   ├── game/
│   │   ├── __init__.py
│   │   ├── constants.py  # Game constants (port of EQ.S, GAMEEQ.S)
│   │   ├── state.py      # Game state management
│   │   └── timing.py     # Frame timing
│   ├── graphics/
│   │   ├── __init__.py
│   │   ├── renderer.py   # Main rendering system
│   │   ├── sprites.py    # Sprite management
│   │   └── display.py    # Display setup
│   ├── animation/
│   │   ├── __init__.py
│   │   ├── sequences.py  # Animation sequences (SEQTABLE)
│   │   ├── frames.py     # Frame definitions (FRAMEDEF)
│   │   └── animator.py   # Animation controller (FRAMEADV)
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── movement.py   # Movement system (MOVER)
│   │   ├── collision.py  # Collision detection (COLL)
│   │   └── gravity.py    # Physics calculations
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── player.py     # Player character
│   │   ├── guard.py      # Enemy guards (AUTO)
│   │   └── objects.py    # Doors, gates, traps, etc.
│   ├── levels/
│   │   ├── __init__.py
│   │   ├── loader.py     # Level loading system
│   │   ├── room.py       # Room/tile management
│   │   └── data.py       # Level data structures
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── sound.py      # Sound effects (SOUND)
│   │   └── music.py      # Music system
│   ├── input/
│   │   ├── __init__.py
│   │   ├── keyboard.py   # Keyboard input (CTRL)
│   │   └── gamepad.py    # Gamepad support
│   └── ui/
│       ├── __init__.py
│       ├── menu.py       # Menus
│       └── hud.py        # In-game UI
├── assets/
│   ├── graphics/         # Converted graphics
│   ├── levels/           # Level data files
│   ├── sounds/           # Sound effects
│   └── music/            # Music files
├── tests/                # Unit tests
├── docs/                 # Documentation
├── README.md
├── requirements.txt      # Python dependencies
└── PROJECT_PLAN.md       # This file
```

### Key Technologies
- **Python 3.10+** - Modern Python with type hints
- **PyGame 2.x** - Game framework
- **Pillow** - Image processing (for asset conversion)
- **NumPy** - Numerical operations (if needed for physics)

### Design Principles
1. **Faithful Port** - Maintain original gameplay mechanics and feel
2. **Modern Code** - Use Python best practices, type hints, documentation
3. **Extensible** - Make it easy to add modern features later
4. **No Copy Protection** - Remove all disk protection code
5. **Cross-Platform** - Work on Windows, Mac, Linux

## Copy Protection Removal

The original game used several copy protection mechanisms:
1. **BBund ID System** - Disk identification bytes (POPside1 = $a9, POPside2 = $ad)
2. **RW18 Routines** - Custom disk read/write routines
3. **Track 22 Check** - Verification of correct disk
4. **Disk Protection Code** - In `03 Disk Protection/` directory

**Removal Strategy:**
- Skip all disk I/O code
- Load levels and assets from regular files
- Remove BBund ID checks
- Remove track verification
- Create simple file-based resource loading system

## Assets & Data Conversion

### Graphics
- Original: Apple II Double Hi-Res (560x192, 16 colors)
- Target: Modern resolution (e.g., 1280x720 or scalable)
- Need to extract and convert sprite data
- Maintain pixel art aesthetic

### Levels
- Extract level data from original files
- Convert to JSON or similar format
- Document level format

### Sounds
- Original: Apple II beep/click sounds
- May need to recreate or find modern equivalents
- Research if sound data can be extracted

## Testing Strategy

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test system interactions
3. **Gameplay Tests** - Playtest each level
4. **Regression Tests** - Ensure changes don't break existing functionality
5. **Performance Tests** - Maintain 60 FPS

## Success Criteria

1. All 15 levels playable
2. Player movement matches original feel
3. Combat system works correctly
4. All traps and mechanisms functional
5. Time limit system working
6. Game can be completed start to finish
7. Runs smoothly on modern systems
8. Cross-platform compatibility
9. No copy protection present
10. Well-documented code

## Future Enhancements (Post-Port)

1. **Enhanced Graphics** - HD sprites, effects
2. **Modern Controls** - Gamepad support, rebindable keys
3. **Level Editor** - Create custom levels
4. **Multiplayer** - Co-op or versus modes
5. **Achievements** - Track player accomplishments
6. **Speed Run Mode** - Timer, level select
7. **Difficulty Options** - Easy/Normal/Hard modes
8. **Save Anywhere** - Modern save system
9. **Sound Options** - Volume controls, modern music
10. **Accessibility** - Colorblind modes, control assists

## License & Legal

- Original source code is copyrighted by Jordan Mechner
- Prince of Persia is owned by Ubisoft
- This port is for educational/preservation purposes
- Should include proper attribution
- Not for commercial distribution

## References & Resources

1. Original source code: https://github.com/jmechner/Prince-of-Persia-Apple-II
2. Jordan Mechner's technical document at jordanmechner.com/library
3. Jordan Mechner's dev journals
4. PyGame documentation: https://www.pygame.org/docs/
5. Apple II technical references for understanding original implementation
6. Prince of Persia community resources and forums

## Timeline Summary

- **Weeks 1-2:** Foundation & setup
- **Weeks 3-4:** Core systems
- **Weeks 5-6:** Character & animation
- **Weeks 7-8:** Game logic
- **Weeks 9-10:** Game flow
- **Weeks 11-12:** Polish & testing
- **Weeks 13-14:** Documentation & release

**Total estimated time:** 14 weeks (3.5 months)

## Next Steps

1. Review and approve this project plan
2. Set up development environment
3. Begin Phase 1: Foundation work
4. Extract and analyze level data format
5. Create basic PyGame window and rendering pipeline
