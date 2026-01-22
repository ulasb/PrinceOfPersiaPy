# Prince of Persia - Python Port

A faithful port of the classic Prince of Persia game from Apple II 6502 assembly language to Python using PyGame.

![License](https://img.shields.io/badge/license-Educational-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Status](https://img.shields.io/badge/status-In%20Development-yellow.svg)

## About

This project aims to recreate the original Prince of Persia game (1989) by Jordan Mechner in Python, maintaining the gameplay mechanics and feel of the original while using modern programming practices.

### Original Game

- **Author**: Jordan Mechner
- **Platform**: Apple II
- **Language**: 6502 Assembly Language
- **Released**: 1989 by Broderbund Software
- **Source**: https://github.com/jmechner/Prince-of-Persia-Apple-II

### This Port

- **Language**: Python 3.10+
- **Framework**: PyGame 2.x
- **Purpose**: Educational and preservation
- **Status**: Early development

## Features (Planned)

- ✅ Faithful recreation of original gameplay mechanics
- ✅ All 15 original levels
- ✅ Character animations and physics
- ✅ Sword combat system
- ✅ Traps, gates, and puzzles
- ✅ Time limit system
- ✅ **No copy protection** (unlike original)
- 🔄 Modern resolution support (scalable)
- 🔄 Cross-platform (Windows, Mac, Linux)
- 🔄 Gamepad support
- 🔄 Save/load game functionality
- 🔄 Enhanced graphics option
- 🔄 Level editor (future)

Legend: ✅ Planned | 🔄 In Progress | ✓ Complete

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PrinceOfPersiaPy.git
cd PrinceOfPersiaPy
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the game:
```bash
cd src
python main.py
```

### Controls

**Keyboard:**
- Arrow Keys: Move left/right, climb up/down
- Shift: Run/careful step
- Space: Jump
- Shift+Space: Running jump
- ESC: Pause/Menu
- Enter: Start game

**Gamepad:** (To be implemented)
- D-Pad/Left Stick: Movement
- A/X: Jump
- B/O: Action
- Start: Pause

## Development

### Project Structure

```
PrinceOfPersiaPy/
├── source_reference/     # Original Apple II source code (for reference)
├── src/                  # Python source code
│   ├── main.py          # Entry point
│   ├── game/            # Core game logic
│   ├── graphics/        # Rendering systems
│   ├── animation/       # Animation systems
│   ├── physics/         # Movement and collision
│   ├── entities/        # Player, guards, objects
│   ├── levels/          # Level loading and management
│   ├── audio/           # Sound and music
│   ├── input/           # Input handling
│   └── ui/              # User interface
├── assets/              # Game assets
│   ├── graphics/        # Sprites and images
│   ├── levels/          # Level data files
│   ├── sounds/          # Sound effects
│   └── music/           # Music files
├── tests/               # Unit tests
├── docs/                # Documentation
└── PROJECT_PLAN.md      # Detailed development plan
```

### Development Roadmap

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for the complete development roadmap.

**Current Phase:** Phase 1 - Foundation & Setup

**Next Steps:**
1. Extract and convert graphics assets from original source
2. Implement level data loading system
3. Create basic character sprite rendering
4. Implement player movement physics

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows Python best practices:
- PEP 8 style guide
- Type hints throughout
- Comprehensive docstrings
- Modular architecture

Format code:
```bash
black src/
isort src/
```

Lint code:
```bash
pylint src/
flake8 src/
```

Type check:
```bash
mypy src/
```

## Differences from Original

This port intentionally differs from the original in the following ways:

1. **No Copy Protection**: All disk protection code has been removed
2. **Modern Resolution**: Supports scalable resolutions (original was 140x192)
3. **File-based Assets**: Uses standard file formats instead of disk sectors
4. **Save System**: Modern save file system instead of disk-sector saves
5. **Cross-platform**: Runs on Windows, Mac, and Linux (original was Apple II only)

The core gameplay, level design, and character mechanics remain faithful to the original.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License & Legal

**Important**: This is a fan recreation for educational and preservation purposes.

- Original Prince of Persia source code: Copyright © Jordan Mechner (1985-1989)
- Prince of Persia franchise: Owned by Ubisoft
- This Python port: Educational use only

**From Jordan Mechner's README:**
> "As the author and copyright holder of this source code, I personally have no problem with anyone studying it, modifying it, attempting to run it, etc. Please understand that this does NOT constitute a grant of rights of any kind in Prince of Persia, which is an ongoing Ubisoft game franchise. Ubisoft alone has the right to make and distribute Prince of Persia games."

This port is created with respect for the original work and is not intended for commercial distribution.

## Credits

### Original Game
- **Creator**: Jordan Mechner
- **Publisher**: Broderbund Software (1989)
- **Current Rights Holder**: Ubisoft

### This Port
- **Port Developer**: [Your Name]
- **Framework**: PyGame
- **Inspiration**: The incredible original source code and Jordan Mechner's development journals

### Special Thanks
- Jordan Mechner for releasing the source code
- The Internet Archive for preserving the original disks
- The retrocomputing community for keeping these classics alive

## Resources

- [Original Source Code](https://github.com/jmechner/Prince-of-Persia-Apple-II)
- [Jordan Mechner's Website](https://jordanmechner.com)
- [Jordan Mechner's Development Journals](https://jordanmechner.com/en/books/journals)
- [PyGame Documentation](https://www.pygame.org/docs/)
- [Prince of Persia Wiki](https://princeofpersia.fandom.com)

## Screenshots

*Coming soon*

## Frequently Asked Questions

**Q: Will this be exactly like the original?**  
A: The gameplay and level design will be faithful to the original, but with modern enhancements like better resolution, smoother controls, and quality-of-life improvements.

**Q: Can I use this commercially?**  
A: No. This is strictly for educational and preservation purposes. Prince of Persia is owned by Ubisoft.

**Q: Will you add new levels?**  
A: Initially, we're focusing on recreating the original 15 levels. A level editor may be added later for custom levels.

**Q: What about other platforms (DOS, Mac, etc.)?**  
A: This port is specifically based on the Apple II version. Other versions had differences in level design and mechanics.

**Q: How can I help?**  
A: Check the Issues tab for tasks, or contribute code, assets, documentation, or testing.

## Changelog

### Version 0.1.0 (Current)
- Initial project setup
- Basic PyGame framework
- Constants ported from assembly
- Project structure established
- Title screen placeholder

See [CHANGELOG.md](CHANGELOG.md) for complete version history (coming soon).

## Contact

For questions, suggestions, or discussions about this port, please open an issue on GitHub.

---

*"A running-jumping-swordfighting game"* - Jordan Mechner
