"""
Prince of Persia - Sprite Management

Handles loading and caching of sprite images.
"""

from typing import Dict, Optional, Tuple
from pathlib import Path
import pygame


class SpriteManager:
    """
    Manages loading and caching of sprite images.
    
    Sprites are loaded from the extracted PNG files and cached for performance.
    """
    
    def __init__(self, assets_path: Optional[Path] = None):
        """
        Initialize the sprite manager.
        
        Args:
            assets_path: Path to assets directory. If None, uses default.
        """
        if assets_path is None:
            # Default to assets directory relative to this file
            self.assets_path = Path(__file__).parent.parent.parent / "assets"
        else:
            self.assets_path = Path(assets_path)
        
        self.graphics_path = self.assets_path / "graphics" / "dump"
        
        # Cache for loaded sprites
        self._sprite_cache: Dict[str, pygame.Surface] = {}
        
        # Check if graphics directory exists
        if not self.graphics_path.exists():
            print(f"Warning: Graphics path not found: {self.graphics_path}")
        else:
            print(f"SpriteManager initialized with path: {self.graphics_path}")
    
    def load_sprite(self, filename: str, colorkey: Optional[Tuple[int, int, int]] = None) -> Optional[pygame.Surface]:
        """
        Load a sprite from file.
        
        Args:
            filename: Name of the sprite file (e.g., "IMG.CHTAB1_img_001_2x41.png")
            colorkey: Optional color to treat as transparent (RGB tuple)
        
        Returns:
            Loaded sprite surface, or None if not found
        """
        # Check cache first
        cache_key = f"{filename}_{colorkey}"
        if cache_key in self._sprite_cache:
            return self._sprite_cache[cache_key]
        
        # Load from file
        sprite_path = self.graphics_path / filename
        
        if not sprite_path.exists():
            print(f"Warning: Sprite not found: {sprite_path}")
            return None
        
        try:
            # Load the image
            sprite = pygame.image.load(str(sprite_path))
            
            # Convert for better performance
            if colorkey is not None:
                sprite = sprite.convert()
                sprite.set_colorkey(colorkey)
            else:
                sprite = sprite.convert_alpha()
            
            # Cache it
            self._sprite_cache[cache_key] = sprite
            
            return sprite
            
        except Exception as e:
            print(f"Error loading sprite {filename}: {e}")
            return None
    
    def get_character_sprite(self, table: str, index: int) -> Optional[pygame.Surface]:
        """
        Get a character sprite by table and index.
        
        Args:
            table: Character table name (e.g., "CHTAB1", "CHTAB4.GD")
            index: Sprite index in the table
        
        Returns:
            Sprite surface or None
        """
        # Find the file matching this pattern
        # Format: IMG.{table}_img_{index:03d}_{width}x{height}.png
        pattern = f"IMG.{table}_img_{index:03d}_"
        
        # Search for matching file
        if not self.graphics_path.exists():
            return None
        
        for file in self.graphics_path.iterdir():
            if file.name.startswith(pattern):
                # Use black (0, 0, 0) as transparent color for monochrome sprites
                return self.load_sprite(file.name, colorkey=(0, 0, 0))
        
        return None
    
    def scale_sprite(self, sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """
        Scale a sprite by a factor.
        
        Args:
            sprite: Original sprite surface
            scale: Scale factor (e.g., 2.0 for 2x size)
        
        Returns:
            Scaled sprite surface
        """
        if sprite is None:
            return None
        
        new_width = int(sprite.get_width() * scale)
        new_height = int(sprite.get_height() * scale)
        
        return pygame.transform.scale(sprite, (new_width, new_height))
    
    def clear_cache(self) -> None:
        """Clear the sprite cache to free memory."""
        self._sprite_cache.clear()
    
    def get_cache_size(self) -> int:
        """Get the number of cached sprites."""
        return len(self._sprite_cache)


# Global sprite manager instance
_sprite_manager: Optional[SpriteManager] = None


def get_sprite_manager() -> SpriteManager:
    """
    Get the global sprite manager instance.
    
    Returns:
        Global SpriteManager instance
    """
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager
