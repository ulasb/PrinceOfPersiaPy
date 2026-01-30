# Level Viewer - User Guide

## Overview

The Level Viewer is an interactive tool for exploring Prince of Persia levels with enhanced graphics and sprite support.

## Features

✨ **Enhanced Graphics**
- Gradient-filled tiles for depth perception
- Pre-rendered tile surfaces for smooth performance
- Actual character sprites from extracted graphics
- Visual decorations on special tiles (spikes, buttons, gates, potions)

🎮 **Interactive Navigation**
- Navigate between connected rooms
- Jump to any level (0-14)
- View player and guard starting positions
- Toggle grid and info overlays

📊 **Information Display**
- Current level and room number
- Room connections (left/right/up/down)
- Player starting position marker
- Guard positions with actual sprites

## Running the Level Viewer

```bash
cd /Users/ulasb/git/PrinceOfPersiaPy
python3 src/view_levels.py
```

## Controls

### Navigation
- **Arrow Keys** (← → ↑ ↓): Navigate to connected rooms
- **Page Up / Page Down**: Cycle through all rooms (0-23)
- **S**: Jump to the starting room (where the player begins)

### Level Selection
- **0-9 Keys**: Switch to different levels
  - 0: Demo level
  - 1-9: Levels 1-9
  - (Use number keys for levels 10-14 not directly accessible)

### View Options
- **G**: Toggle grid overlay (shows tile boundaries)
- **I**: Toggle info panel (shows controls and instructions)

### Exit
- **ESC**: Quit the viewer

## Understanding the Display

### Tile Colors

The viewer uses color-coded tiles to represent different elements:

- **Dark Blue-Gray**: Empty space
- **Brown**: Floor tiles
- **Red**: Spikes (with triangle decorations)
- **Gray**: Walls, pillars, gates
- **Gold**: Buttons (raise/drop/stuck)
- **Purple**: Tapestries
- **Green**: Potions (with bottle icon)
- **Cyan**: Exit doors
- **Orange**: Torches
- **White**: Skeleton spawn points
- **Silver**: Swords

### Character Markers

- **Yellow/Prince Sprite**: Player starting position
- **Red/Guard Sprite**: Guard starting positions

### UI Elements

**Top Bar:**
- Level number and current room number
- Room connections (arrows showing available exits)

**Bottom Panel (when enabled with 'I'):**
- Control instructions
- Navigation help

## Tips

1. **Exploring Levels**: Use arrow keys to follow the natural room connections, or use Page Up/Down to see all rooms in sequence.

2. **Finding the Start**: Press 'S' to quickly jump to where the player begins the level.

3. **Grid Overlay**: Enable the grid (G key) to see exact tile boundaries - useful for understanding level layout.

4. **Performance**: The viewer runs at 60 FPS with pre-rendered tiles for smooth navigation.

## Sprite Viewer

For viewing individual character sprites, use the sprite viewer:

```bash
python3 src/sprite_viewer.py
```

**Sprite Viewer Controls:**
- **← →**: Switch between sprite sets (Prince, Guards, Skeleton, Shadow, etc.)
- **↑ ↓**: Scroll through sprites
- **ESC**: Quit

## Technical Details

### Graphics System

The level viewer uses:
- **SpriteManager**: Loads and caches sprite images
- **Pre-rendered tiles**: Created once at startup for performance
- **Gradient effects**: Subtle shading for visual depth
- **Sprite scaling**: 3x scaling for character sprites

### Level Data

Levels are loaded from JSON files in `assets/levels/`:
- `level_00.json` through `level_14.json`
- Contains room layouts, tile types, and entity positions
- Human-readable and editable

### Performance

- **Startup time**: ~100ms (includes tile pre-rendering)
- **Frame rate**: Solid 60 FPS
- **Memory usage**: ~50MB (with sprite cache)

## Troubleshooting

**Problem**: "Level file not found" error
- **Solution**: Ensure JSON level files exist in `assets/levels/`

**Problem**: No character sprites visible
- **Solution**: Check that PNG files exist in `assets/graphics/dump/`

**Problem**: Window doesn't open
- **Solution**: Ensure pygame is installed: `pip install pygame-ce`

**Problem**: Slow performance
- **Solution**: Close other applications, or reduce screen resolution

## Next Steps

After exploring levels, you might want to:

1. **View Animations**: Once the animation system is integrated, you'll see animated characters
2. **Edit Levels**: Modify the JSON files to create custom levels
3. **Extract Background Tiles**: Add authentic dungeon/palace graphics
4. **Play the Game**: Once the player controller is implemented

## Files

- `src/view_levels.py` - Main level viewer application
- `src/sprite_viewer.py` - Sprite browsing tool
- `src/graphics/renderer.py` - Enhanced rendering engine
- `src/graphics/sprites.py` - Sprite management system
- `src/levels/loader.py` - Level loading (JSON and binary)

---

**Enjoy exploring the dungeons of Prince of Persia!** 🏰⚔️
