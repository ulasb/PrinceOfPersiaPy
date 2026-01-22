"""
Prince of Persia - Main Entry Point

This is the main entry point for the Prince of Persia Python port.

Original Apple II version by Jordan Mechner (1985-1989)
Python port for educational and preservation purposes.
"""

import sys
import pygame
from game.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GAME_TITLE,
    GAME_VERSION
)
from game.state import GameStateManager


def main() -> int:
    """Main game entry point"""
    
    # Initialize Pygame
    pygame.init()
    
    try:
        # Create display
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"{GAME_TITLE} - {GAME_VERSION}")
        
        # Create clock for frame timing
        clock = pygame.time.Clock()
        
        # Create game state manager
        game_state = GameStateManager(screen)
        
        # Main game loop
        running = True
        while running:
            # Calculate delta time
            dt = clock.tick(FPS) / 1000.0  # Convert to seconds
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    game_state.handle_event(event)
            
            # Update game state
            game_state.update(dt)
            
            # Render
            game_state.render(screen)
            
            # Update display
            pygame.display.flip()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        pygame.quit()


if __name__ == "__main__":
    sys.exit(main())
