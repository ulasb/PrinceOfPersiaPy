# Quick Start Guide

## Getting Started with Prince of Persia Python Port

### Installation

1. **Check Python version** (must be 3.10+):
```bash
python3 --version
```

2. **Clone the repository**:
```bash
cd /Users/ulasb/git/PrinceOfPersiaPy
```

3. **Install dependencies**:
```bash
pip3 install -r requirements.txt
```

### Running the Game

From the project root:
```bash
cd src
python3 main.py
```

### Current Status

**✓ Completed:**
- Project structure established
- Core constants ported from assembly
- Basic PyGame framework setup
- Game state management system
- Title screen with basic navigation
- Build system verified

**🔄 In Progress:**
- Asset extraction from original source
- Level data format conversion
- Character sprite rendering

**📋 Next Steps:**
1. Extract graphics from Apple II format
2. Convert level data to JSON
3. Implement basic character rendering
4. Add player movement physics

### Development Commands

**Test syntax:**
```bash
cd src
python3 -m py_compile main.py game/*.py
```

**Run tests:**
```bash
pytest tests/
```

**Format code:**
```bash
black src/
isort src/
```

### Project Files

Key files to understand:

- `src/main.py` - Entry point, game loop
- `src/game/constants.py` - All game constants (ported from assembly)
- `src/game/state.py` - Game state management
- `PROJECT_PLAN.md` - Complete development roadmap
- `source_reference/` - Original Apple II source code for reference

### Exploring the Original Source

The original Apple II assembly source is in `source_reference/01 POP Source/Source/`:

- `MASTER.S` - Main game controller
- `CTRL.S` - Player control
- `AUTO.S` - Guard AI
- `COLL.S` - Collision detection
- `MOVER.S` - Movement system
- `FRAMEADV.S` - Animation system
- `EQ.S` / `GAMEEQ.S` - Constants (already ported)

### Next Development Session

To continue development:

1. **Asset Extraction**: 
   - Study `01 POP Source/Images/` directory
   - Extract sprite data from Apple II format
   - Convert to PNG or similar modern format

2. **Level Data**:
   - Study `01 POP Source/Levels/` directory
   - Understand blueprint format (BLUETYPE, BLUESPEC)
   - Create JSON representation

3. **Character System**:
   - Port frame definitions from `FRAMEDEF.S`
   - Port animation sequences from `SEQTABLE.S`
   - Create sprite animation system

### Useful References

- Original source: `source_reference/01 POP Source/`
- Technical docs: Check Jordan Mechner's website for technical documentation
- PyGame docs: https://www.pygame.org/docs/

### Development Tips

1. **Reference the Assembly**: When implementing a feature, always check the original assembly code for the exact logic
2. **Test Frequently**: Run the game often to catch issues early
3. **Document as You Go**: Add comments explaining assembly->Python translations
4. **Maintain Timing**: The original game ran at 12 FPS for game logic - keep this in mind

### Getting Help

- Check `PROJECT_PLAN.md` for overall architecture
- Read assembly source in `source_reference/`
- Consult PyGame documentation for rendering questions
- Look at constants in `src/game/constants.py` for game values

### Architecture Overview

```
Main Loop (main.py)
    ↓
GameStateManager (game/state.py)
    ↓
┌───────────────┬──────────────┬─────────────┐
│   Graphics    │  Animation   │   Physics   │
└───────┬───────┴──────┬───────┴──────┬──────┘
        │              │              │
    ┌───┴────┐    ┌────┴────┐    ┌────┴────┐
    │ Player │    │ Guards  │    │ Objects │
    └────────┘    └─────────┘    └─────────┘
```

Happy coding! 🎮
