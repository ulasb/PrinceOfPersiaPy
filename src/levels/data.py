"""
Prince of Persia - Level Data Structures

This module defines the data structures for level (blueprint) data.
Corresponds to the blueprint structures in EQ.S.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import IntEnum

from game.constants import BLUEPRINT_WIDTH, BLUEPRINT_HEIGHT


class TileType(IntEnum):
    """
    Tile type identifiers.
    
    These correspond to the tile IDs used in BLUETYPE array.
    Based on studying the original assembly and level data.
    """
    EMPTY = 0x00
    FLOOR = 0x01
    SPIKE = 0x02
    PILLAR = 0x03
    GATE = 0x04
    STUCK_BUTTON = 0x05
    DROP_BUTTON = 0x06
    TAPESTRY = 0x07
    TAPESTRY_TOP = 0x08
    POTION = 0x09
    LOOSE_FLOOR = 0x0A
    GATE_TOP = 0x0B
    MIRROR = 0x0C
    DEBRIS = 0x0D
    RAISE_BUTTON = 0x0E
    EXIT_LEFT = 0x0F
    EXIT_RIGHT = 0x10
    CHOMPER = 0x11
    TORCH = 0x12
    WALL = 0x13
    SKELETON = 0x14
    SWORD = 0x15
    BALCONY_LEFT = 0x16
    BALCONY_RIGHT = 0x17
    LATTICE_PILLAR = 0x18
    LATTICE_LEFT = 0x19
    LATTICE_RIGHT = 0x1A
    BIG_PILLAR_BOTTOM = 0x1B
    BIG_PILLAR_TOP = 0x1C
    SMALL_PILLAR = 0x1D
    LATTICE_DOWN = 0x1E
    TORCH_WITH_DEBRIS = 0x1F


class TileModifier(IntEnum):
    """Tile modifiers (upper bits of tile byte)"""
    NONE = 0x00
    OPENER = 0x20  # This tile opens/triggers something
    SWORD_MODIFIER = 0x40
    SPECIAL = 0x80


@dataclass
class Tile:
    """
    Represents a single tile in the level.
    
    In the original, this is stored as two bytes in BLUETYPE and BLUESPEC arrays.
    """
    tile_type: TileType
    modifier: int  # Tile-specific modifier (from BLUESPEC)
    
    @property
    def is_solid(self) -> bool:
        """Check if tile blocks movement"""
        solid_tiles = {
            TileType.WALL,
            TileType.PILLAR,
            TileType.BIG_PILLAR_BOTTOM,
            TileType.BIG_PILLAR_TOP,
            TileType.SMALL_PILLAR,
            TileType.GATE,
            TileType.GATE_TOP,
        }
        return self.tile_type in solid_tiles
    
    @property
    def is_dangerous(self) -> bool:
        """Check if tile can harm the player"""
        dangerous_tiles = {
            TileType.SPIKE,
            TileType.CHOMPER,
        }
        return self.tile_type in dangerous_tiles
    
    @property
    def is_floor(self) -> bool:
        """Check if tile acts as floor"""
        floor_tiles = {
            TileType.FLOOR,
            TileType.LOOSE_FLOOR,
            TileType.RAISE_BUTTON,
            TileType.DROP_BUTTON,
            TileType.STUCK_BUTTON,
        }
        return self.tile_type in floor_tiles


@dataclass
class Room:
    """
    Represents a single room (screen) in the level.
    
    A room is 10 tiles wide by 3 tiles high.
    In the original, rooms are stored in the BLUETYPE/BLUESPEC arrays.
    """
    room_number: int
    tiles: List[List[Tile]]  # [y][x] - 3 rows, 10 columns
    
    # Room connections (room numbers or None)
    left: Optional[int] = None
    right: Optional[int] = None
    up: Optional[int] = None
    down: Optional[int] = None
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position, returns None if out of bounds"""
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[y]):
            return self.tiles[y][x]
        return None


@dataclass
class GuardInfo:
    """
    Information about a guard's starting state.
    
    From the INFO structure in the original (GdStartBlock, GdStartFace, etc.)
    """
    block: int  # Starting block/tile position
    face: int  # Facing direction (0=left, 1=right)
    x: int  # X position within block
    seq_low: int  # Low byte of starting sequence
    seq_high: int  # High byte of starting sequence
    prog: int  # Guard AI program/behavior
    
    @property
    def sequence(self) -> int:
        """Get full 16-bit sequence number"""
        return (self.seq_high << 8) | self.seq_low
    
    @property
    def is_active(self) -> bool:
        """Check if guard is active (block != 0xFF means active)"""
        return self.block != 0xFF


@dataclass
class LevelInfo:
    """
    Level metadata from the INFO structure.
    
    This corresponds to the INFO array in the original blueprint data.
    """
    # Kid (player) starting position
    kid_start_screen: int
    kid_start_block: int
    kid_start_face: int
    
    # Sword starting position (if not carried)
    sword_start_screen: int
    sword_start_block: int
    
    # Guards (up to 24)
    guards: List[GuardInfo]


@dataclass
class Level:
    """
    Complete level data structure.
    
    Corresponds to the blueprint (BLUETYPE, BLUESPEC, LINKLOC, LINKMAP, INFO)
    in the original source.
    """
    level_number: int
    rooms: List[Room]  # All 24 rooms
    info: LevelInfo
    
    # Link maps for room connections
    # These map screen numbers to their connected neighbors
    link_locations: List[int]  # LINKLOC - 256 bytes
    link_map: List[int]  # LINKMAP - 256 bytes
    
    def get_room(self, room_number: int) -> Optional[Room]:
        """Get room by number (0-23)"""
        if 0 <= room_number < len(self.rooms):
            return self.rooms[room_number]
        return None
    
    def get_linked_room(self, from_room: int, direction: str) -> Optional[int]:
        """
        Get the room number linked in a direction.
        
        Args:
            from_room: Source room number
            direction: 'left', 'right', 'up', 'down'
        
        Returns:
            Destination room number or None
        """
        room = self.get_room(from_room)
        if room:
            return getattr(room, direction, None)
        return None


# Blueprint structure sizes (from EQ.S)
BLUETYPE_SIZE = BLUEPRINT_WIDTH * BLUEPRINT_HEIGHT  # 24 * 30 = 720 bytes
BLUESPEC_SIZE = BLUEPRINT_WIDTH * BLUEPRINT_HEIGHT  # 24 * 30 = 720 bytes
LINKLOC_SIZE = 256  # bytes
LINKMAP_SIZE = 256  # bytes
MAP_SIZE = BLUEPRINT_WIDTH * 4  # 24 * 4 = 96 bytes
INFO_SIZE = 256  # bytes

# Total blueprint size
BLUEPRINT_SIZE = (
    BLUETYPE_SIZE +
    BLUESPEC_SIZE +
    LINKLOC_SIZE +
    LINKMAP_SIZE +
    MAP_SIZE +
    INFO_SIZE
)  # = 2304 bytes (matches level file size!)

# Blueprint structure offsets
BLUETYPE_OFFSET = 0
BLUESPEC_OFFSET = BLUETYPE_SIZE
LINKLOC_OFFSET = BLUESPEC_OFFSET + BLUESPEC_SIZE
LINKMAP_OFFSET = LINKLOC_OFFSET + LINKLOC_SIZE
MAP_OFFSET = LINKMAP_OFFSET + LINKMAP_SIZE
INFO_OFFSET = MAP_OFFSET + MAP_SIZE

# INFO structure offsets (from EQ.S)
INFO_KID_START_SCRN = 64
INFO_KID_START_BLOCK = 65
INFO_KID_START_FACE = 66
INFO_SWORD_START_SCRN = 68
INFO_SWORD_START_BLOCK = 69
INFO_GD_START_BLOCK = 71  # 24 bytes
INFO_GD_START_FACE = 95   # 24 bytes
INFO_GD_START_X = 119     # 24 bytes
INFO_GD_START_SEQ_L = 143  # 24 bytes
INFO_GD_START_PROG = 167   # 24 bytes
INFO_GD_START_SEQ_H = 191  # 24 bytes

MAX_GUARDS = 24

# Tile dimensions
TILES_PER_ROOM_WIDTH = 10
TILES_PER_ROOM_HEIGHT = 3
TOTAL_ROOMS = 24
