"""
Simple ASCII visualizer for Prince of Persia levels.
Shows the level layout using text characters.
"""

from levels.loader import LevelLoader
from levels.data import TileType


# ASCII representations for each tile type
TILE_CHARS = {
    TileType.EMPTY: '  ',
    TileType.FLOOR: '==',
    TileType.SPIKE: '^^',
    TileType.PILLAR: '||',
    TileType.GATE: '##',
    TileType.STUCK_BUTTON: 'SB',
    TileType.DROP_BUTTON: 'DB',
    TileType.TAPESTRY: 'TT',
    TileType.TAPESTRY_TOP: 'Tt',
    TileType.POTION: 'PP',
    TileType.LOOSE_FLOOR: '~~',
    TileType.GATE_TOP: '#^',
    TileType.MIRROR: '//',
    TileType.DEBRIS: '..', 
    TileType.RAISE_BUTTON: 'RB',
    TileType.EXIT_LEFT: '<E',
    TileType.EXIT_RIGHT: 'E>',
    TileType.CHOMPER: 'XX',
    TileType.TORCH: '🔥',
    TileType.WALL: '██',
    TileType.SKELETON: '💀',
    TileType.SWORD: '🗡️',
    TileType.BALCONY_LEFT: 'B<',
    TileType.BALCONY_RIGHT: 'B>',
    TileType.LATTICE_PILLAR: 'LP',
    TileType.LATTICE_LEFT: 'L<',
    TileType.LATTICE_RIGHT: 'L>',
    TileType.BIG_PILLAR_BOTTOM: 'Pb',
    TileType.BIG_PILLAR_TOP: 'Pt',
    TileType.SMALL_PILLAR: 'ps',
    TileType.LATTICE_DOWN: 'Ld',
    TileType.TORCH_WITH_DEBRIS: 'T.',
}


def visualize_room(room, show_connections=True):
    """
    Visualize a single room as ASCII art.
    
    Args:
        room: Room object
        show_connections: Whether to show room connections
    """
    print(f"\n╔{'═' * 22}╗")
    print(f"║ Room {room.room_number:2d}             ║")
    print(f"╚{'═' * 22}╝")
    
    if show_connections:
        connections = []
        if room.left is not None:
            connections.append(f"←{room.left}")
        if room.right is not None:
            connections.append(f"→{room.right}")
        if room.up is not None:
            connections.append(f"↑{room.up}")
        if room.down is not None:
            connections.append(f"↓{room.down}")
        if connections:
            print(f"Connections: {', '.join(connections)}")
    
    # Draw the room
    print("┌" + "─" * 20 + "┐")
    for y, row in enumerate(room.tiles):
        line = "│"
        for tile in row:
            char = TILE_CHARS.get(tile.tile_type, '??')
            line += char
        line += "│"
        print(line)
    print("└" + "─" * 20 + "┘")


def visualize_level(level_num, rooms_to_show=None):
    """
    Visualize a complete level.
    
    Args:
        level_num: Level number to load
        rooms_to_show: List of room numbers to show, or None for all
    """
    loader = LevelLoader()
    level = loader.load_level(level_num)
    
    if not level:
        print(f"Failed to load level {level_num}")
        return
    
    print("\n" + "=" * 60)
    print(f"PRINCE OF PERSIA - LEVEL {level_num}")
    print("=" * 60)
    
    print(f"\nPlayer starts at: Screen {level.info.kid_start_screen}, "
          f"Block {level.info.kid_start_block}")
    print(f"Facing: {'Right' if level.info.kid_start_face else 'Left'}")
    
    active_guards = [g for g in level.info.guards if g.is_active]
    print(f"Active guards: {len(active_guards)}")
    
    # Show specified rooms or first few
    if rooms_to_show is None:
        rooms_to_show = [0, 1, 2]  # Show first 3 rooms by default
    
    for room_num in rooms_to_show:
        if room_num < len(level.rooms):
            visualize_room(level.rooms[room_num])


def level_stats(level_num):
    """Show statistics about a level"""
    loader = LevelLoader()
    level = loader.load_level(level_num)
    
    if not level:
        return
    
    print(f"\n{'=' * 60}")
    print(f"Level {level_num} Statistics")
    print(f"{'=' * 60}")
    
    # Count tile types across all rooms
    tile_counts = {}
    for room in level.rooms:
        for row in room.tiles:
            for tile in row:
                tile_type = tile.tile_type.name
                tile_counts[tile_type] = tile_counts.get(tile_type, 0) + 1
    
    # Sort by count
    sorted_tiles = sorted(tile_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTile type distribution:")
    for tile_type, count in sorted_tiles:
        if count > 0:
            print(f"  {tile_type:20s}: {count:3d}")
    
    # Guard info
    active_guards = [g for g in level.info.guards if g.is_active]
    print(f"\nActive guards: {len(active_guards)}")
    
    # Dangerous tiles
    dangerous_count = sum(
        count for tile_type, count in sorted_tiles
        if tile_type in ['SPIKE', 'CHOMPER']
    )
    print(f"Dangerous tiles: {dangerous_count}")


def show_all_levels_summary():
    """Show summary of all levels"""
    loader = LevelLoader()
    
    print("\n" + "=" * 80)
    print("PRINCE OF PERSIA - ALL LEVELS SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Level':<8} {'Start Room':<12} {'Guards':<10} {'Spikes':<10} {'Gates':<10}")
    print("-" * 80)
    
    for level_num in range(15):
        level = loader.load_level(level_num)
        if level:
            active_guards = sum(1 for g in level.info.guards if g.is_active)
            
            # Count specific tiles
            spike_count = 0
            gate_count = 0
            
            for room in level.rooms:
                for row in room.tiles:
                    for tile in row:
                        if tile.tile_type == TileType.SPIKE:
                            spike_count += 1
                        elif tile.tile_type in [TileType.GATE, TileType.GATE_TOP]:
                            gate_count += 1
            
            print(f"{level_num:<8} {level.info.kid_start_screen:<12} "
                  f"{active_guards:<10} {spike_count:<10} {gate_count:<10}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Visualize specific level
        level_num = int(sys.argv[1])
        print(f"\nVisualizing Level {level_num}...")
        visualize_level(level_num, rooms_to_show=[0, 1, 2, 3, 4])
        level_stats(level_num)
    else:
        # Show summary of all levels
        show_all_levels_summary()
