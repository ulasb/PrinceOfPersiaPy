"""
Game constants for the Prince of Persia Python port.

Geometry and timing follow the original Apple II source (EQ.S, TABLES.S):
rooms are 10 blocks wide x 3 high; a block is 14 game-pixels wide and 63
tall on a 140x192 screen (rendered at 280x192 hi-res). Game logic runs at
~12 ticks per second like the original.
"""

from typing import Final

# --- geometry (140-res game pixels) ---
TILE_W: Final[int] = 14
ROW_H: Final[int] = 63
ROOM_W: Final[int] = 10          # blocks per room
ROOM_H: Final[int] = 3           # rows per room
SCREEN_W: Final[int] = 140
SCREEN_H: Final[int] = 192

# canvas is hi-res (280 wide = 2x game pixels) plus an 8px HUD strip
CANVAS_W: Final[int] = 280
CANVAS_H: Final[int] = 200
HUD_Y: Final[int] = 192
DISPLAY_SCALE: Final[int] = 4

VERT_DIST: Final[int] = 10       # feet above block bottom (TABLES.S)


def floor_y(row: int) -> int:
    """Feet y-coordinate when standing on the given row (FloorY table)."""
    return 55 + ROW_H * row


def block_top(row: int) -> int:
    return 3 + ROW_H * row


def block_bot(row: int) -> int:
    return 65 + ROW_H * row


def row_from_y(y: int) -> int:
    """Logical row for a feet y-coordinate (row r spans floor_y(r)-62..+0)."""
    return (y + 7) // ROW_H


# --- timing ---
FPS: Final[int] = 60
TICKS_PER_SECOND: Final[int] = 12
FRAMES_PER_TICK: Final[int] = FPS // TICKS_PER_SECOND
TIME_LIMIT_TICKS: Final[int] = 60 * 60 * TICKS_PER_SECOND  # 60 minutes

# --- physics (COLL.S / MOVER.S) ---
GRAVITY: Final[int] = 3
TERMINAL_VELOCITY: Final[int] = 33
OOF_VELOCITY: Final[int] = 22    # falling speed that costs 1 hp
DEATH_VELOCITY: Final[int] = 33  # falling speed that kills

# --- traps (MOVER.S) ---
PP_TIMER: Final[int] = 5         # ticks a pressplate stays down
SPIKE_TIMER: Final[int] = 15     # ticks spikes stay extended
SPIKE_RET: Final[int] = 9        # retraction animation end state
SLICE_TIMER: Final[int] = 15     # ticks between slicer cycles
GATE_MAX: Final[int] = 188       # gmaxval: fully-open gate position
GATE_TIMER: Final[int] = GATE_MAX + 50  # open-state countdown start
GATE_JAMMED: Final[int] = 255
GATE_RISE: Final[int] = 4        # per-tick rise while opening (gateinc)
GATE_DROP: Final[int] = 50       # fast close per tick (drop button)
GATE_CLOSE: Final[int] = 1       # slow creak shut per tick (gateinc -1)
GATE_PASSABLE: Final[int] = 112  # min position the kid can walk through
GATE_KNOCK: Final[int] = 5       # CHECKGATE: closing gate shoves the kid
LOOSE_WIGGLE: Final[int] = 4     # wiggling ticks before detach
LOOSE_DETACH: Final[int] = 10    # ticks until floor falls
FF_ACCEL: Final[int] = 3
FF_TERMVEL: Final[int] = 29

# --- combat (AUTO.S strike/block windows, 140-res pixels) ---
STRIKE_NEAR: Final[int] = 12     # strikerange1: closer and the blade
STRIKE_FAR: Final[int] = 29      # strikerange2  passes behind the body
BLOCK_FAR: Final[int] = 29       # blockrange2
# offguardthres is 8 in the original; _char_separation keeps the kid
# 10px from a guard, so the lunge window starts just past that
OFFGUARD_RANGE: Final[int] = 11
BLOCK_TIME: Final[int] = 4       # guard block impaired after being parried

# --- characters ---
INITIAL_HP: Final[int] = 3
CHAR_KID: Final[int] = 0
CHAR_SHADOW: Final[int] = 1
CHAR_GUARD: Final[int] = 2

# actions (CharAction)
ACT_STAND: Final[int] = 0
ACT_MOVE: Final[int] = 1
ACT_HANG: Final[int] = 2
ACT_MIDAIR: Final[int] = 3
ACT_FREEFALL: Final[int] = 4
ACT_BUMPED: Final[int] = 5
ACT_HANG_STRAIGHT: Final[int] = 6
ACT_TURN: Final[int] = 7

# --- levels ---
FIRST_LEVEL: Final[int] = 1
LAST_LEVEL: Final[int] = 14

# per-level guard sprite table (CHTAB4 variant) and background set
GUARD_TABLE = {3: "SKEL", 6: "FAT", 12: "SHAD", 13: "VIZ", 14: "GD"}
# levels using the palace background set (BGTAB .PAL)
PALACE_LEVELS = {4, 5, 6, 10, 11, 14}

GAME_TITLE: Final[str] = "Prince of Persia"
GAME_VERSION: Final[str] = "Python Port v1.0"
