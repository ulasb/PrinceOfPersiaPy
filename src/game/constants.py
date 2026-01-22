"""
Prince of Persia - Game Constants

This module contains all game constants ported from the original Apple II assembly code.
Original files: EQ.S and GAMEEQ.S

Copyright Notice:
Original Prince of Persia source code by Jordan Mechner (1985-1989)
This Python port is for educational and preservation purposes.
"""

from enum import Enum, IntEnum
from typing import Final

# =============================================================================
# Screen Constants
# =============================================================================

# Original Apple II screen dimensions
APPLE_II_SCREEN_WIDTH: Final[int] = 140
APPLE_II_SCREEN_HEIGHT: Final[int] = 192

# Modern screen dimensions (scalable)
SCREEN_WIDTH: Final[int] = 1280
SCREEN_HEIGHT: Final[int] = 720

# Scale factors
SCALE_X: Final[float] = SCREEN_WIDTH / APPLE_II_SCREEN_WIDTH
SCALE_Y: Final[float] = SCREEN_HEIGHT / APPLE_II_SCREEN_HEIGHT

# Original screen bounds
SCRN_LEFT: Final[int] = 58
SCRN_RIGHT: Final[int] = SCRN_LEFT + APPLE_II_SCREEN_WIDTH - 1
SCRN_TOP: Final[int] = 0
SCRN_BOTTOM: Final[int] = SCRN_TOP + APPLE_II_SCREEN_HEIGHT - 1

# =============================================================================
# Display Constants
# =============================================================================

FPS: Final[int] = 60  # Target frames per second
SPEED_NORMAL: Final[int] = 1
SPEED_FAST: Final[int] = 2

# =============================================================================
# Game Constants
# =============================================================================

FLOOR_HEIGHT: Final[int] = 15
ANGLE: Final[int] = 7
VERT_DIST: Final[int] = 11

# Maximum entities
MAX_GUARDS: Final[int] = 24
MAX_TORCHES: Final[int] = 32
MAX_MOBS: Final[int] = 16

# Image list maximums
MAX_BACK: Final[int] = 200  # Background elements
MAX_FORE: Final[int] = 100  # Foreground elements
MAX_WIPE: Final[int] = 20   # Wipe effects
MAX_PEEL: Final[int] = 46   # Peel effects
MAX_MID: Final[int] = 46    # Mid-layer objects
MAX_OBJ: Final[int] = 20    # Objects
MAX_MSG: Final[int] = 32    # Messages
MAX_SFX: Final[int] = 32    # Sound effects

# Blueprint map dimensions
BLUEPRINT_WIDTH: Final[int] = 24
BLUEPRINT_HEIGHT: Final[int] = 30

# Time limit (in frames)
TIME_LIMIT_MINUTES: Final[int] = 60
FRAMES_PER_SECOND: Final[int] = 12  # Original game timing
TIME_LIMIT_FRAMES: Final[int] = TIME_LIMIT_MINUTES * 60 * FRAMES_PER_SECOND

# =============================================================================
# Character Constants
# =============================================================================

CHAR_DATA_SIZE: Final[int] = 16  # Size of character data structure

# Character offsets (zero-indexed)
CHAR_POSN: Final[int] = 0
CHAR_X: Final[int] = 1
CHAR_Y: Final[int] = 2
CHAR_FACE: Final[int] = 3
CHAR_BLOCK_X: Final[int] = 4
CHAR_BLOCK_Y: Final[int] = 5
CHAR_ACTION: Final[int] = 6
CHAR_X_VEL: Final[int] = 7
CHAR_Y_VEL: Final[int] = 8
CHAR_SEQ: Final[int] = 9  # 2 bytes
CHAR_SCRN: Final[int] = 11
CHAR_REPEAT: Final[int] = 12
CHAR_ID: Final[int] = 13
CHAR_SWORD: Final[int] = 14
CHAR_LIFE: Final[int] = 15

# =============================================================================
# Character Types
# =============================================================================

class CharType(IntEnum):
    """Character type identifiers"""
    KID = 0
    SHADOW = 1
    GUARD = 2
    SWORD = 3
    REFLECT = 4
    COMIX = 5
    FALLING_FLOOR = 0x80

# =============================================================================
# Facing Directions
# =============================================================================

class Direction(IntEnum):
    """Facing directions"""
    LEFT = 0
    RIGHT = 1
    
# =============================================================================
# Drawing Operations
# =============================================================================

class DrawOp(IntEnum):
    """Drawing operation types"""
    AND = 0
    ORA = 1
    STA = 2
    EOR = 3
    MASK = 4

# =============================================================================
# Layer Usage Types
# =============================================================================

class LayerType(IntEnum):
    """Layer rendering types"""
    USE_FAST_LAY = 0
    USE_LAY = 1
    USE_LAYRSAVE = 2

# =============================================================================
# Frame Definitions
# =============================================================================

# Frame check marks (bit flags)
F_CHECK_MARK: Final[int] = 0b01000000
F_THIN_MARK: Final[int] = 0b00100000
F_FOOT_MARK: Final[int] = 0b00011111

# =============================================================================
# Blueprint Constants
# =============================================================================

# Masks for tile data
SEC_MASK: Final[int] = 0b11000000
REQ_MASK: Final[int] = 0b00100000
ID_MASK: Final[int] = 0b00011111

# =============================================================================
# Tile/Block Types
# =============================================================================

class TileType(IntEnum):
    """Level tile/block types"""
    EMPTY = 0
    FLOOR = 1
    SPIKE = 2
    PILLAR = 3
    GATE = 4
    STUCK_BUTTON = 5
    DROP_BUTTON = 6
    TAPESTRY = 7
    TAPESTRY_TOP = 8
    POTION = 9
    LOOSE_FLOOR = 10
    GATE_TOP = 11
    MIRROR = 12
    DEBRIS = 13
    RAISE_BUTTON = 14
    EXIT_LEFT = 15
    EXIT_RIGHT = 16
    CHOMPER = 17
    TORCH = 18
    WALL = 19
    SKELETON = 20
    SWORD = 21
    BALCONY_LEFT = 22
    BALCONY_RIGHT = 23
    LATTICE_LEFT = 24
    LATTICE_RIGHT = 25
    LATTICE_PILLAR = 26
    LATTICE_DOWN = 27
    SMALL_PILLAR = 28
    BIG_PILLAR_BOTTOM = 29
    BIG_PILLAR_TOP = 30
    TORCH_WITH_DEBRIS = 31

# =============================================================================
# Input Constants
# =============================================================================

class GameInput(IntEnum):
    """Game input actions"""
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    SHIFT = 5  # Run/careful step
    RUN = 5    # Alias for shift

# =============================================================================
# Game States
# =============================================================================

class GameState(Enum):
    """Overall game states"""
    TITLE = "title"
    INTRO = "intro"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    CUTSCENE = "cutscene"

# =============================================================================
# Level Constants
# =============================================================================

FIRST_LEVEL: Final[int] = 1
LAST_LEVEL: Final[int] = 15  # Original game has 15 levels
DEMO_LEVEL: Final[int] = 0

# Level track/region identifiers
# Track 33, Region 0 = Demo level
# Track 33, Region 1 = Level 1
DEMO_TRACK: Final[int] = 33
DEMO_REGION: Final[int] = 0
FIRST_LEVEL_TRACK: Final[int] = 33
FIRST_LEVEL_REGION: Final[int] = 1

# =============================================================================
# Collision Constants
# =============================================================================

# Collision distances
SWORD_RANGE: Final[int] = 20  # Pixels
GUARD_DETECT_RANGE: Final[int] = 40  # Pixels
BUMP_DISTANCE: Final[int] = 1  # Pixels

# =============================================================================
# Health/Damage Constants
# =============================================================================

MAX_HEALTH: Final[int] = 10
INITIAL_HEALTH: Final[int] = 3
SPIKE_DAMAGE: Final[int] = 1
SWORD_DAMAGE: Final[int] = 1
FALL_DAMAGE_THRESHOLD: Final[int] = 2  # Blocks
FALL_DAMAGE: Final[int] = 1
FATAL_FALL_THRESHOLD: Final[int] = 4  # Blocks

# Potion effects
SMALL_POTION_HEALTH: Final[int] = 1
LARGE_POTION_HEALTH: Final[int] = 10  # Full health
POISON_DAMAGE: Final[int] = 1
FLOAT_POTION_DURATION: Final[int] = 100  # Frames
INVERT_POTION_DURATION: Final[int] = 100  # Frames

# =============================================================================
# Animation Sequence Constants
# =============================================================================

# These will be populated from SEQTABLE.S
# For now, define placeholders
SEQ_STAND: Final[int] = 0
SEQ_TURN: Final[int] = 1
SEQ_RUN: Final[int] = 2
SEQ_JUMP: Final[int] = 3
SEQ_CROUCH: Final[int] = 4
SEQ_STEP_FORWARD: Final[int] = 5
SEQ_CLIMB: Final[int] = 6
SEQ_HANG: Final[int] = 7
SEQ_FALL: Final[int] = 8

# Guard sequences (approximate)
SEQ_GUARD_STAND: Final[int] = 100
SEQ_GUARD_WALK: Final[int] = 101
SEQ_GUARD_STRIKE: Final[int] = 102
SEQ_GUARD_DEFEND: Final[int] = 103

# =============================================================================
# Sound Effect IDs
# =============================================================================

class SoundEffect(IntEnum):
    """Sound effect identifiers"""
    SILENCE = 0
    FOOTSTEP = 1
    SWORD_DRAWN = 2
    SWORD_HIT = 3
    SWORD_MISS = 4
    GATE_OPEN = 5
    GATE_CLOSE = 6
    SPIKE_UP = 7
    SPIKE_DOWN = 8
    POTION_DRINK = 9
    LOOSE_FLOOR = 10
    FALL_LAND = 11
    FALL_SPLAT = 12
    GUARD_HIT = 13
    GUARD_DEATH = 14
    KID_HIT = 15
    KID_DEATH = 16
    BUTTON_PRESS = 17
    TORCH_LIGHT = 18
    GLASS_BREAK = 19

# =============================================================================
# Special Key Constants (Cheats/Debug)
# =============================================================================

# Special keyboard keys (will be adapted to modern keyboard)
KEY_SAVE_GAME: Final[str] = 's'
KEY_LOAD_GAME: Final[str] = 'l'
KEY_RESTART: Final[str] = 'r'
KEY_PAUSE: Final[str] = 'p'
KEY_QUIT: Final[str] = 'q'

# Debug keys (if enabled)
KEY_DEBUG_LEVELSKIP: Final[str] = '+'
KEY_DEBUG_LEVEL_BACK: Final[str] = '-'
KEY_DEBUG_INVINCIBLE: Final[str] = 'i'
KEY_DEBUG_TIME_STOP: Final[str] = 't'

# =============================================================================
# Color Constants
# =============================================================================

# Standard colors (RGB tuples)
COLOR_BLACK: Final[tuple[int, int, int]] = (0, 0, 0)
COLOR_WHITE: Final[tuple[int, int, int]] = (255, 255, 255)
COLOR_RED: Final[tuple[int, int, int]] = (255, 0, 0)
COLOR_GREEN: Final[tuple[int, int, int]] = (0, 255, 0)
COLOR_BLUE: Final[tuple[int, int, int]] = (0, 0, 255)
COLOR_YELLOW: Final[tuple[int, int, int]] = (255, 255, 0)
COLOR_PURPLE: Final[tuple[int, int, int]] = (255, 0, 255)

# UI colors
COLOR_UI_BACKGROUND: Final[tuple[int, int, int]] = (20, 20, 30)
COLOR_UI_TEXT: Final[tuple[int, int, int]] = (220, 220, 220)
COLOR_UI_HIGHLIGHT: Final[tuple[int, int, int]] = (255, 180, 0)

# Health meter colors
COLOR_HEALTH_FULL: Final[tuple[int, int, int]] = (0, 255, 0)
COLOR_HEALTH_MEDIUM: Final[tuple[int, int, int]] = (255, 255, 0)
COLOR_HEALTH_LOW: Final[tuple[int, int, int]] = (255, 0, 0)

# =============================================================================
# File Paths
# =============================================================================

# Asset directories
PATH_ASSETS: Final[str] = "assets"
PATH_GRAPHICS: Final[str] = f"{PATH_ASSETS}/graphics"
PATH_LEVELS: Final[str] = f"{PATH_ASSETS}/levels"
PATH_SOUNDS: Final[str] = f"{PATH_ASSETS}/sounds"
PATH_MUSIC: Final[str] = f"{PATH_ASSETS}/music"

# Save game directory
PATH_SAVE: Final[str] = "saved_games"

# =============================================================================
# Development/Debug Flags
# =============================================================================

DEBUG_MODE: Final[bool] = True
SHOW_FPS: Final[bool] = True
SHOW_COLLISION_BOXES: Final[bool] = False
GOD_MODE: Final[bool] = False
INFINITE_TIME: Final[bool] = False

# =============================================================================
# Version Information
# =============================================================================

GAME_TITLE: Final[str] = "Prince of Persia"
GAME_VERSION: Final[str] = "Python Port v0.1.0"
ORIGINAL_VERSION: Final[str] = "Apple II v1.0 (1989)"
PORT_AUTHOR: Final[str] = "Python Port"
ORIGINAL_AUTHOR: Final[str] = "Jordan Mechner"

# =============================================================================
# Helper Functions
# =============================================================================

def scale_x(x: int) -> int:
    """Scale Apple II X coordinate to modern screen"""
    return int(x * SCALE_X)

def scale_y(y: int) -> int:
    """Scale Apple II Y coordinate to modern screen"""
    return int(y * SCALE_Y)

def unscale_x(x: int) -> int:
    """Convert modern X coordinate to Apple II coordinate"""
    return int(x / SCALE_X)

def unscale_y(y: int) -> int:
    """Convert modern Y coordinate to Apple II coordinate"""
    return int(y / SCALE_Y)
