"""
Prince of Persia - Graphics Renderer

This module handles rendering of game graphics.
Initially uses placeholder graphics (colored rectangles) which will be replaced
with actual sprite graphics once extracted from Apple II format.
"""

from typing import Optional, Tuple
import pygame

from game.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BLACK,
    scale_x,
    scale_y,
)
from levels.data import TileType


# Tile dimensions in original Apple II coordinates
TILE_WIDTH_APPLE = 14  # pixels
TILE_HEIGHT_APPLE = 63  # pixels

# Scaled tile dimensions for modern screen
TILE_WIDTH = scale_x(TILE_WIDTH_APPLE)
TILE_HEIGHT = scale_y(TILE_HEIGHT_APPLE)


# Placeholder colors for each tile type (RGB)
# These will be replaced with actual sprite graphics later
TILE_COLORS = {
    TileType.EMPTY: (20, 20, 30),           # Dark blue-gray
    TileType.FLOOR: (139, 69, 19),          # Saddle brown
    TileType.SPIKE: (255, 0, 0),            # Red
    TileType.PILLAR: (169, 169, 169),       # Dark gray
    TileType.GATE: (105, 105, 105),         # Dim gray
    TileType.STUCK_BUTTON: (255, 215, 0),   # Gold
    TileType.DROP_BUTTON: (255, 140, 0),    # Dark orange
    TileType.TAPESTRY: (128, 0, 128),       # Purple
    TileType.TAPESTRY_TOP: (128, 0, 128),   # Purple
    TileType.POTION: (0, 255, 0),           # Lime green
    TileType.LOOSE_FLOOR: (160, 82, 45),    # Sienna (darker brown)
    TileType.GATE_TOP: (105, 105, 105),     # Dim gray
    TileType.MIRROR: (192, 192, 192),       # Silver
    TileType.DEBRIS: (101, 67, 33),         # Dark brown
    TileType.RAISE_BUTTON: (255, 215, 0),   # Gold
    TileType.EXIT_LEFT: (0, 255, 255),      # Cyan
    TileType.EXIT_RIGHT: (0, 255, 255),     # Cyan
    TileType.CHOMPER: (139, 0, 0),          # Dark red
    TileType.TORCH: (255, 165, 0),          # Orange
    TileType.WALL: (105, 105, 105),         # Dim gray
    TileType.SKELETON: (255, 255, 255),     # White
    TileType.SWORD: (192, 192, 192),        # Silver
    TileType.BALCONY_LEFT: (139, 69, 19),   # Brown
    TileType.BALCONY_RIGHT: (139, 69, 19),  # Brown
    TileType.LATTICE_PILLAR: (169, 169, 169), # Gray
    TileType.LATTICE_LEFT: (169, 169, 169), # Gray
    TileType.LATTICE_RIGHT: (169, 169, 169), # Gray
    TileType.BIG_PILLAR_BOTTOM: (169, 169, 169), # Gray
    TileType.BIG_PILLAR_TOP: (169, 169, 169), # Gray
    TileType.SMALL_PILLAR: (169, 169, 169), # Gray
    TileType.LATTICE_DOWN: (169, 169, 169), # Gray
    TileType.TORCH_WITH_DEBRIS: (255, 140, 0), # Orange
}


class Renderer:
    """
    Main rendering class for Prince of Persia.
    
    Handles drawing of tiles, sprites, and UI elements.
    Currently uses placeholder graphics which will be replaced with
    actual extracted sprites.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.
        
        Args:
            screen: The main Pygame surface to render to
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # Font for debug text
        pygame.font.init()
        self.debug_font = pygame.font.Font(None, 24)
        
        # Sprite cache (will be populated when we extract real graphics)
        self.sprite_cache = {}
        
        print("Renderer initialized")
        print(f"  Screen size: {self.screen_width}x{self.screen_height}")
        print(f"  Tile size: {TILE_WIDTH}x{TILE_HEIGHT}")
    
    def clear(self, color: Tuple[int, int, int] = COLOR_BLACK) -> None:
        """
        Clear the screen with a color.
        
        Args:
            color: RGB color tuple
        """
        self.screen.fill(color)
    
    def draw_tile(self, tile_type: TileType, x: int, y: int, 
                  modifier: int = 0) -> None:
        """
        Draw a single tile.
        
        Args:
            tile_type: Type of tile to draw
            x: X position in pixels (already scaled)
            y: Y position in pixels (already scaled)
            modifier: Tile modifier (for variations)
        """
        # Get placeholder color
        color = TILE_COLORS.get(tile_type, (255, 0, 255))  # Magenta for unknown
        
        # Draw filled rectangle
        rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
        pygame.draw.rect(self.screen, color, rect)
        
        # Draw border for visibility (except empty tiles)
        if tile_type != TileType.EMPTY:
            border_color = tuple(max(0, c - 40) for c in color)
            pygame.draw.rect(self.screen, border_color, rect, 2)
        
        # Draw special indicators for certain tile types
        if tile_type == TileType.SPIKE:
            # Draw triangles for spikes
            points = [
                (x + TILE_WIDTH // 4, y + TILE_HEIGHT),
                (x + TILE_WIDTH // 4, y + TILE_HEIGHT - 10),
                (x + TILE_WIDTH // 4 + 5, y + TILE_HEIGHT)
            ]
            pygame.draw.polygon(self.screen, (200, 0, 0), points)
        
        elif tile_type in [TileType.STUCK_BUTTON, TileType.DROP_BUTTON, 
                           TileType.RAISE_BUTTON]:
            # Draw circle for buttons
            center = (x + TILE_WIDTH // 2, y + TILE_HEIGHT - 10)
            pygame.draw.circle(self.screen, (255, 255, 0), center, 5)
        
        elif tile_type == TileType.GATE:
            # Draw vertical bars for gate
            for i in range(0, TILE_WIDTH, 10):
                pygame.draw.line(self.screen, (80, 80, 80), 
                               (x + i, y), (x + i, y + TILE_HEIGHT), 3)
        
        elif tile_type == TileType.POTION:
            # Draw circle for potion
            center = (x + TILE_WIDTH // 2, y + TILE_HEIGHT // 2)
            pygame.draw.circle(self.screen, (0, 200, 0), center, 8)
    
    def draw_room(self, room, offset_x: int = 0, offset_y: int = 0) -> None:
        """
        Draw a complete room.
        
        Args:
            room: Room object from levels.data
            offset_x: X offset in pixels
            offset_y: Y offset in pixels
        """
        # A room is 10 tiles wide × 3 tiles tall
        for y, row in enumerate(room.tiles):
            for x, tile in enumerate(row):
                screen_x = offset_x + (x * TILE_WIDTH)
                screen_y = offset_y + (y * TILE_HEIGHT)
                self.draw_tile(tile.tile_type, screen_x, screen_y, tile.modifier)
    
    def draw_text(self, text: str, x: int, y: int, 
                  color: Tuple[int, int, int] = (255, 255, 255)) -> None:
        """
        Draw text on screen.
        
        Args:
            text: Text to draw
            x: X position
            y: Y position
            color: RGB color
        """
        surface = self.debug_font.render(text, True, color)
        self.screen.blit(surface, (x, y))
    
    def draw_room_info(self, room, x: int = 10, y: int = 10) -> None:
        """
        Draw debug information about a room.
        
        Args:
            room: Room object
            x: X position for text
            y: Y position for text
        """
        self.draw_text(f"Room {room.room_number}", x, y)
        
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
            self.draw_text(f"Connections: {' '.join(connections)}", x, y + 25)
    
    def draw_grid(self, room_width: int, room_height: int, 
                  offset_x: int = 0, offset_y: int = 0,
                  color: Tuple[int, int, int] = (80, 80, 80)) -> None:
        """
        Draw a grid overlay for debugging.
        
        Args:
            room_width: Number of tiles wide
            room_height: Number of tiles tall
            offset_x: X offset in pixels
            offset_y: Y offset in pixels
            color: Grid color
        """
        # Draw vertical lines
        for x in range(room_width + 1):
            x_pos = offset_x + (x * TILE_WIDTH)
            pygame.draw.line(self.screen, color,
                           (x_pos, offset_y),
                           (x_pos, offset_y + room_height * TILE_HEIGHT))
        
        # Draw horizontal lines
        for y in range(room_height + 1):
            y_pos = offset_y + (y * TILE_HEIGHT)
            pygame.draw.line(self.screen, color,
                           (offset_x, y_pos),
                           (offset_x + room_width * TILE_WIDTH, y_pos))
    
    def draw_player_marker(self, x: int, y: int) -> None:
        """
        Draw a placeholder for the player character.
        
        Args:
            x: X position in pixels
            y: Y position in pixels
        """
        # Draw a simple colored circle for now
        pygame.draw.circle(self.screen, (255, 255, 0), (x, y), 15)
        # Add a direction indicator
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (x, y), (x + 20, y), 3)
    
    def draw_guard_marker(self, x: int, y: int) -> None:
        """
        Draw a placeholder for a guard.
        
        Args:
            x: X position in pixels
            y: Y position in pixels
        """
        # Draw a simple colored circle for now
        pygame.draw.circle(self.screen, (255, 0, 0), (x, y), 15)


# Convenience function to get tile dimensions
def get_tile_dimensions() -> Tuple[int, int]:
    """Get the current tile dimensions in pixels"""
    return TILE_WIDTH, TILE_HEIGHT
