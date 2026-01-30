"""
Prince of Persia - Graphics Renderer

This module handles rendering of game graphics.
Uses a combination of placeholder graphics and actual extracted sprites.
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
from graphics.sprites import SpriteManager


# Tile dimensions - calculated to fit a 10x3 room nicely on screen
# A room is 10 tiles wide × 3 tiles tall
# We want the room to fit comfortably on a 1280x720 screen with margins

# Target room display size (leaving margins for UI)
ROOM_DISPLAY_WIDTH = 1000  # pixels
ROOM_DISPLAY_HEIGHT = 500  # pixels

# Calculate tile size to fit the room
TILE_WIDTH = ROOM_DISPLAY_WIDTH // 10  # 100 pixels per tile
TILE_HEIGHT = ROOM_DISPLAY_HEIGHT // 3  # ~166 pixels per tile


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
        
        # Sprite manager for loading actual graphics
        self.sprite_manager = SpriteManager()
        
        # Sprite cache (will be populated when we extract real graphics)
        self.sprite_cache = {}
        
        # Create enhanced tile surfaces for better visuals
        self._create_tile_surfaces()
        
        print("Renderer initialized")
        print(f"  Screen size: {self.screen_width}x{self.screen_height}")
        print(f"  Tile size: {TILE_WIDTH}x{TILE_HEIGHT}")
        print(f"  Sprite cache: {self.sprite_manager.get_cache_size()} sprites loaded")
    
    def _create_tile_surfaces(self) -> None:
        """Create pre-rendered tile surfaces with enhanced graphics."""
        self.tile_surfaces = {}
        
        # Create enhanced surfaces for common tiles
        for tile_type in TileType:
            surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
            color = TILE_COLORS.get(tile_type, (255, 0, 255))
            
            # Draw base with gradient effect
            for y in range(TILE_HEIGHT):
                # Create subtle gradient
                brightness = 1.0 - (y / TILE_HEIGHT) * 0.2
                grad_color = tuple(int(c * brightness) for c in color)
                pygame.draw.line(surface, grad_color, (0, y), (TILE_WIDTH, y))
            
            # Add border for non-empty tiles
            if tile_type != TileType.EMPTY:
                border_color = tuple(max(0, c - 40) for c in color)
                pygame.draw.rect(surface, border_color, surface.get_rect(), 2)
            
            # Add special decorations
            if tile_type == TileType.SPIKE:
                # Draw spike triangles
                for i in range(0, TILE_WIDTH, 15):
                    points = [
                        (i + 5, TILE_HEIGHT),
                        (i + 10, TILE_HEIGHT - 15),
                        (i + 15, TILE_HEIGHT)
                    ]
                    pygame.draw.polygon(surface, (200, 0, 0), points)
            
            elif tile_type in [TileType.STUCK_BUTTON, TileType.DROP_BUTTON, TileType.RAISE_BUTTON]:
                # Draw button circle
                center = (TILE_WIDTH // 2, TILE_HEIGHT - 10)
                pygame.draw.circle(surface, (255, 255, 0), center, 6)
                pygame.draw.circle(surface, (200, 200, 0), center, 6, 2)
            
            elif tile_type == TileType.GATE:
                # Draw vertical bars
                for i in range(5, TILE_WIDTH, 12):
                    pygame.draw.line(surface, (80, 80, 80), (i, 0), (i, TILE_HEIGHT), 4)
            
            elif tile_type == TileType.POTION:
                # Draw potion bottle
                center = (TILE_WIDTH // 2, TILE_HEIGHT // 2)
                pygame.draw.circle(surface, (0, 200, 0), center, 10)
                pygame.draw.circle(surface, (0, 255, 0), (center[0] - 2, center[1] - 2), 4)
            
            self.tile_surfaces[tile_type] = surface
    
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
        # Use pre-rendered surface if available
        if tile_type in self.tile_surfaces:
            self.screen.blit(self.tile_surfaces[tile_type], (x, y))
        else:
            # Fallback to simple rectangle
            color = TILE_COLORS.get(tile_type, (255, 0, 255))
            rect = pygame.Rect(x, y, TILE_WIDTH, TILE_HEIGHT)
            pygame.draw.rect(self.screen, color, rect)
            
        # Draw text label for clarity (temporary for debugging purposes)
        if tile_type != TileType.EMPTY:
            label_surf = self.debug_font.render(tile_type.name, True, (255, 255, 255))
            # Outline for text
            label_rect = label_surf.get_rect(center=(x + TILE_WIDTH // 2, y + TILE_HEIGHT // 2))
            
            
            # Simple shadow for better readability
            shadow_surf = self.debug_font.render(tile_type.name, True, (0, 0, 0))
            self.screen.blit(shadow_surf, (label_rect.x + 1, label_rect.y + 1))
            self.screen.blit(label_surf, label_rect)

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
    def draw_player_marker(self, x: int, y: int, facing_right: bool = True) -> None:
        """
        Draw the player character.
        
        Args:
            x: X position in pixels (center)
            y: Y position in pixels (center)
            facing_right: Whether the player is facing right
        """
        # Try to load a standing sprite from CHTAB1 (prince sprites)
        sprite = self.sprite_manager.get_character_sprite("CHTAB1", 1)
        
        if sprite:
            # Scale the sprite to fit better
            scaled_sprite = self.sprite_manager.scale_sprite(sprite, 3.0)
            
            # Fix orientation: Flip vertically because extracted sprites are upside down
            scaled_sprite = pygame.transform.flip(scaled_sprite, False, True)
            
            # Flip if facing left
            if not facing_right:
                scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
            
            # Center the sprite at the position
            sprite_rect = scaled_sprite.get_rect()
            sprite_rect.center = (x, y)
            
            # Draw the sprite
            self.screen.blit(scaled_sprite, sprite_rect)
        else:
            # Fallback to colored circle
            pygame.draw.circle(self.screen, (255, 255, 0), (x, y), 15)
            # Add a direction indicator
            direction_x = x + (20 if facing_right else -20)
            pygame.draw.line(self.screen, (255, 0, 0), 
                            (x, y), (direction_x, y), 3)
    
    def draw_guard_marker(self, x: int, y: int, guard_type: str = "GD") -> None:
        """
        Draw a guard character.
        
        Args:
            x: X position in pixels (center)
            y: Y position in pixels (center)
            guard_type: Type of guard ("GD", "SKEL", "SHAD", "FAT", "VIZ")
        """
        # Try to load a guard sprite
        table_name = f"CHTAB4.{guard_type}"
        sprite = self.sprite_manager.get_character_sprite(table_name, 1)
        
        if sprite:
            # Scale the sprite
            scaled_sprite = self.sprite_manager.scale_sprite(sprite, 3.0)

            # Fix orientation: Flip vertically because extracted sprites are upside down
            scaled_sprite = pygame.transform.flip(scaled_sprite, False, True)
            
            # Center the sprite at the position
            sprite_rect = scaled_sprite.get_rect()
            sprite_rect.center = (x, y)
            
            # Draw the sprite
            self.screen.blit(scaled_sprite, sprite_rect)
        else:
            # Fallback to colored circle
            pygame.draw.circle(self.screen, (255, 0, 0), (x, y), 15)


# Convenience function to get tile dimensions
def get_tile_dimensions() -> Tuple[int, int]:
    """Get the current tile dimensions in pixels"""
    return TILE_WIDTH, TILE_HEIGHT
