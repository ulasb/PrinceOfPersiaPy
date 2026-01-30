"""
Prince of Persia - Level Loader

This module loads and parses level data from the original binary format.
Corresponds to the blueprint loading code in MASTER.S.
"""

import struct
from pathlib import Path
from typing import List, Optional

from levels.data import (
    Level,
    Room,
    Tile,
    TileType,
    LevelInfo,
    GuardInfo,
    BLUEPRINT_SIZE,
    BLUETYPE_OFFSET,
    BLUESPEC_OFFSET,
    LINKLOC_OFFSET,
    LINKMAP_OFFSET,
    INFO_OFFSET,
    INFO_KID_START_SCRN,
    INFO_KID_START_BLOCK,
    INFO_KID_START_FACE,
    INFO_SWORD_START_SCRN,
    INFO_SWORD_START_BLOCK,
    INFO_GD_START_BLOCK,
    INFO_GD_START_FACE,
    INFO_GD_START_X,
    INFO_GD_START_SEQ_L,
    INFO_GD_START_PROG,
    INFO_GD_START_SEQ_H,
    MAX_GUARDS,
    TILES_PER_ROOM_WIDTH,
    TILES_PER_ROOM_HEIGHT,
    TOTAL_ROOMS,
)


class LevelLoader:
    """
    Loads level data from original Apple II binary format.
    
    The level files are 2304 bytes each, containing:
    - BLUETYPE: 720 bytes (tile types for 24 rooms)
    - BLUESPEC: 720 bytes (tile modifiers for 24 rooms)
    - LINKLOC: 256 bytes (room connection data)
    - LINKMAP: 256 bytes (room connection map)
    - MAP: 96 bytes (24 * 4 bytes, additional room data)
    - INFO: 256 bytes (level metadata, start positions, guards)
    """
    
    def __init__(self, levels_directory: str = "source_reference/01 POP Source/Levels", 
                 json_directory: str = "assets/levels"):
        """
        Initialize the level loader.
        
        Args:
            levels_directory: Path to directory containing binary level files
            json_directory: Path to directory containing JSON level files
        """
        self.levels_dir = Path(levels_directory)
        self.json_dir = Path(json_directory)
        
    def load_level(self, level_number: int) -> Optional[Level]:
        """
        Load a level from file (tries JSON first, then binary).
        
        Args:
            level_number: Level number (0-14, where 0 is demo level)
        
        Returns:
            Loaded Level object or None if file not found
        """
        # Try JSON first
        json_file = self.json_dir / f"level_{level_number:02d}.json"
        if json_file.exists():
            return self._load_from_json(json_file)
        
        # Fall back to binary format
        level_file = self.levels_dir / f"LEVEL{level_number}"
        
        if not level_file.exists():
            print(f"Error: Level file not found: {level_file}")
            return None
        
        # Read the entire level file
        with open(level_file, 'rb') as f:
            data = f.read()
        
        if len(data) != BLUEPRINT_SIZE:
            print(f"Error: Invalid level file size: {len(data)} (expected {BLUEPRINT_SIZE})")
            return None
        
        # Parse the level data
        return self._parse_level(level_number, data)
    
    def _load_from_json(self, json_file: Path) -> Optional[Level]:
        """
        Load a level from JSON format.
        
        Args:
            json_file: Path to JSON file
        
        Returns:
            Loaded Level object or None on error
        """
        import json
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Parse level info
            info_data = data['info']
            guards = []
            for g in info_data.get('guards', []):
                guard = GuardInfo(
                    block=g['block'],
                    face=g['face'],
                    x=g['x'],
                    seq_low=g.get('sequence', 0) & 0xFF,
                    seq_high=(g.get('sequence', 0) >> 8) & 0xFF,
                    prog=g['prog']
                )
                guards.append(guard)
            
            info = LevelInfo(
                kid_start_screen=info_data['kid_start_screen'],
                kid_start_block=info_data['kid_start_block'],
                kid_start_face=info_data['kid_start_face'],
                sword_start_screen=info_data['sword_start_screen'],
                sword_start_block=info_data['sword_start_block'],
                guards=guards
            )
            
            # Parse rooms
            rooms = []
            for room_data in data['rooms']:
                tiles = []
                for row_data in room_data['tiles']:
                    row = []
                    for tile_data in row_data:
                        tile_type = TileType[tile_data['type']]
                        tile = Tile(
                            tile_type=tile_type,
                            modifier=tile_data['modifier']
                        )
                        row.append(tile)
                    tiles.append(row)
                
                conn = room_data['connections']
                room = Room(
                    room_number=room_data['room_number'],
                    tiles=tiles,
                    left=conn['left'],
                    right=conn['right'],
                    up=conn['up'],
                    down=conn['down']
                )
                rooms.append(room)
            
            return Level(
                level_number=data['level_number'],
                rooms=rooms,
                info=info,
                link_locations=[],
                link_map=[]
            )
            
        except Exception as e:
            print(f"Error loading JSON level: {e}")
            return None
    
    def _parse_level(self, level_number: int, data: bytes) -> Level:
        """
        Parse raw level data into Level structure.
        
        Args:
            level_number: Level number
            data: Raw 2304 bytes of level data
        
        Returns:
            Parsed Level object
        """
        # Extract each section
        bluetype = data[BLUETYPE_OFFSET:BLUETYPE_OFFSET + 720]
        bluespec = data[BLUESPEC_OFFSET:BLUESPEC_OFFSET + 720]
        linkloc = list(data[LINKLOC_OFFSET:LINKLOC_OFFSET + 256])
        linkmap = list(data[LINKMAP_OFFSET:LINKMAP_OFFSET + 256])
        info_data = data[INFO_OFFSET:INFO_OFFSET + 256]
        
        # Parse rooms
        rooms = self._parse_rooms(bluetype, bluespec, linkmap)
        
        # Parse level info
        info = self._parse_info(info_data)
        
        return Level(
            level_number=level_number,
            rooms=rooms,
            info=info,
            link_locations=linkloc,
            link_map=linkmap
        )
    
    def _parse_rooms(self, bluetype: bytes, bluespec: bytes, linkmap: List[int]) -> List[Room]:
        """
        Parse room data from BLUETYPE and BLUESPEC.
        
        Each room is 30 tiles (10 wide x 3 high).
        Total 24 rooms = 720 tiles.
        
        Args:
            bluetype: 720 bytes of tile types
            bluespec: 720 bytes of tile modifiers
            linkmap: Room connection map
        
        Returns:
            List of 24 Room objects
        """
        rooms = []
        
        for room_num in range(TOTAL_ROOMS):
            # Calculate offset for this room
            # Each room is 30 tiles (10 width * 3 height)
            room_offset = room_num * (TILES_PER_ROOM_WIDTH * TILES_PER_ROOM_HEIGHT)
            
            # Parse tiles for this room
            tiles = []
            for y in range(TILES_PER_ROOM_HEIGHT):
                row = []
                for x in range(TILES_PER_ROOM_WIDTH):
                    tile_index = room_offset + (y * TILES_PER_ROOM_WIDTH) + x
                    
                    # Get tile type and modifier
                    tile_type_byte = bluetype[tile_index]
                    tile_modifier = bluespec[tile_index]
                    
                    # Extract tile type (lower 5 bits usually, but check for special cases)
                    # Note: The exact encoding may need adjustment after testing
                    tile_type = TileType(tile_type_byte & 0x1F)  # Lower 5 bits
                    
                    tile = Tile(
                        tile_type=tile_type,
                        modifier=tile_modifier
                    )
                    row.append(tile)
                
                tiles.append(row)
            
            # Determine room connections from linkmap
            # This is a simplified version - may need refinement
            left = None
            right = None
            up = None
            down = None
            
            # Room connections are typically encoded in the linkmap
            # For now, we'll use a simple adjacency assumption
            if room_num % 8 > 0:  # Not leftmost
                left = room_num - 1
            if room_num % 8 < 7:  # Not rightmost
                right = room_num + 1
            if room_num >= 8:  # Not top row
                up = room_num - 8
            if room_num < 16:  # Not bottom row
                down = room_num + 8
            
            room = Room(
                room_number=room_num,
                tiles=tiles,
                left=left,
                right=right,
                up=up,
                down=down
            )
            
            rooms.append(room)
        
        return rooms
    
    def _parse_info(self, info_data: bytes) -> LevelInfo:
        """
        Parse level INFO structure.
        
        Args:
            info_data: 256 bytes of INFO data
        
        Returns:
            Parsed LevelInfo object
        """
        # Parse kid starting position
        kid_start_screen = info_data[INFO_KID_START_SCRN]
        kid_start_block = info_data[INFO_KID_START_BLOCK]
        kid_start_face = info_data[INFO_KID_START_FACE]
        
        # Parse sword starting position
        sword_start_screen = info_data[INFO_SWORD_START_SCRN]
        sword_start_block = info_data[INFO_SWORD_START_BLOCK]
        
        # Parse guards
        guards = []
        for i in range(MAX_GUARDS):
            block = info_data[INFO_GD_START_BLOCK + i]
            face = info_data[INFO_GD_START_FACE + i]
            x = info_data[INFO_GD_START_X + i]
            seq_low = info_data[INFO_GD_START_SEQ_L + i]
            prog = info_data[INFO_GD_START_PROG + i]
            seq_high = info_data[INFO_GD_START_SEQ_H + i]
            
            guard = GuardInfo(
                block=block,
                face=face,
                x=x,
                seq_low=seq_low,
                seq_high=seq_high,
                prog=prog
            )
            
            guards.append(guard)
        
        return LevelInfo(
            kid_start_screen=kid_start_screen,
            kid_start_block=kid_start_block,
            kid_start_face=kid_start_face,
            sword_start_screen=sword_start_screen,
            sword_start_block=sword_start_block,
            guards=guards
        )
    
    def export_to_json(self, level: Level, output_path: str) -> None:
        """
        Export a level to JSON format for easier editing.
        
        Args:
            level: Level object to export
            output_path: Path to output JSON file
        """
        import json
        
        # Create a dictionary representation
        level_dict = {
            "level_number": level.level_number,
            "info": {
                "kid_start_screen": level.info.kid_start_screen,
                "kid_start_block": level.info.kid_start_block,
                "kid_start_face": level.info.kid_start_face,
                "sword_start_screen": level.info.sword_start_screen,
                "sword_start_block": level.info.sword_start_block,
                "guards": [
                    {
                        "block": g.block,
                        "face": g.face,
                        "x": g.x,
                        "sequence": g.sequence,
                        "prog": g.prog,
                        "active": g.is_active
                    }
                    for g in level.info.guards if g.is_active
                ]
            },
            "rooms": []
        }
        
        # Add room data
        for room in level.rooms:
            room_dict = {
                "room_number": room.room_number,
                "connections": {
                    "left": room.left,
                    "right": room.right,
                    "up": room.up,
                    "down": room.down
                },
                "tiles": []
            }
            
            # Add tiles (row by row)
            for y, row in enumerate(room.tiles):
                tile_row = []
                for x, tile in enumerate(row):
                    tile_row.append({
                        "type": tile.tile_type.name,
                        "type_id": tile.tile_type.value,
                        "modifier": tile.modifier
                    })
                room_dict["tiles"].append(tile_row)
            
            level_dict["rooms"].append(room_dict)
        
        # Write to JSON file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w') as f:
            json.dump(level_dict, f, indent=2)
        
        print(f"Exported level {level.level_number} to {output_path}")


def test_level_loader():
    """Test the level loader by loading and displaying Level 1"""
    loader = LevelLoader()
    
    print("Loading Level 1...")
    level = loader.load_level(1)
    
    if level:
        print(f"✓ Loaded Level {level.level_number}")
        print(f"  Kid starts at: Screen {level.info.kid_start_screen}, "
              f"Block {level.info.kid_start_block}, "
              f"Facing {'Right' if level.info.kid_start_face else 'Left'}")
        print(f"  Sword at: Screen {level.info.sword_start_screen}, "
              f"Block {level.info.sword_start_block}")
        
        active_guards = [g for g in level.info.guards if g.is_active]
        print(f"  Active guards: {len(active_guards)}")
        
        # Show first room
        print(f"\n  Room 0 tiles (top row):")
        room0 = level.rooms[0]
        for tile in room0.tiles[0]:  # Top row
            print(f"    {tile.tile_type.name:20s} (mod: {tile.modifier:02x})")
        
        # Export to JSON
        loader.export_to_json(level, "assets/levels/level_01.json")
    else:
        print("✗ Failed to load level")


if __name__ == "__main__":
    test_level_loader()
