"""
Prince of Persia - Level Viewer

A standalone viewer to display levels using the renderer.
This is useful for testing and visualizing level data.
"""

import pygame
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BLACK
from levels.loader import LevelLoader
from graphics.renderer import Renderer, TILE_WIDTH, TILE_HEIGHT


class LevelViewer:
    """
    Interactive level viewer application.
    
    Controls:
        Arrow Keys: Navigate between rooms
        Number Keys (0-9): Jump to specific level
        ESC: Quit
        G: Toggle grid
        I: Toggle info
    """
    
    def __init__(self):
        """Initialize the level viewer"""
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Prince of Persia - Level Viewer")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize systems
        self.renderer = Renderer(self.screen)
        self.loader = LevelLoader()
        
        # Current state
        self.current_level_num = 1
        self.current_room_num = 0
        self.current_level = None
        self.show_grid = True
        self.show_info = True
        
        # Load initial level
        self.load_level(self.current_level_num)
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
    
    def load_level(self, level_num: int) -> None:
        """Load a level by number"""
        self.current_level = self.loader.load_level(level_num)
        if self.current_level:
            self.current_level_num = level_num
            # Start at the player's starting room
            self.current_room_num = self.current_level.info.kid_start_screen
            print(f"Loaded Level {level_num}, starting at room {self.current_room_num}")
        else:
            print(f"Failed to load level {level_num}")
    
    def handle_events(self) -> None:
        """Handle user input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # Level selection (0-9 keys)
                elif pygame.K_0 <= event.key <= pygame.K_9:
                    level_num = event.key - pygame.K_0
                    if level_num < 15:  # We have levels 0-14
                        self.load_level(level_num)
                
                # Room navigation
                elif event.key == pygame.K_LEFT:
                    room = self.get_current_room()
                    if room and room.left is not None:
                        self.current_room_num = room.left
                
                elif event.key == pygame.K_RIGHT:
                    room = self.get_current_room()
                    if room and room.right is not None:
                        self.current_room_num = room.right
                
                elif event.key == pygame.K_UP:
                    room = self.get_current_room()
                    if room and room.up is not None:
                        self.current_room_num = room.up
                
                elif event.key == pygame.K_DOWN:
                    room = self.get_current_room()
                    if room and room.down is not None:
                        self.current_room_num = room.down
                
                # Previous/Next room (wrapped)
                elif event.key == pygame.K_PAGEUP:
                    self.current_room_num = (self.current_room_num - 1) % 24
                
                elif event.key == pygame.K_PAGEDOWN:
                    self.current_room_num = (self.current_room_num + 1) % 24
                
                # Toggle options
                elif event.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
                
                # Jump to start room
                elif event.key == pygame.K_s:
                    if self.current_level:
                        self.current_room_num = self.current_level.info.kid_start_screen
    
    def get_current_room(self):
        """Get the currently displayed room"""
        if self.current_level:
            return self.current_level.get_room(self.current_room_num)
        return None
    
    def render(self) -> None:
        """Render the current view"""
        # Clear screen
        self.renderer.clear(COLOR_BLACK)
        
        if not self.current_level:
            self.renderer.draw_text("No level loaded", 
                                   SCREEN_WIDTH // 2 - 100, 
                                   SCREEN_HEIGHT // 2,
                                   (255, 255, 255))
            return
        
        room = self.get_current_room()
        if not room:
            return
        
        # Calculate centering offset
        room_width = 10 * TILE_WIDTH
        room_height = 3 * TILE_HEIGHT
        offset_x = (SCREEN_WIDTH - room_width) // 2
        offset_y = (SCREEN_HEIGHT - room_height) // 2 - 50  # Leave space for UI
        
        # Draw the room
        self.renderer.draw_room(room, offset_x, offset_y)
        
        # Draw grid if enabled
        if self.show_grid:
            self.renderer.draw_grid(10, 3, offset_x, offset_y)
        
        # Draw player marker if this is the start room
        if room.room_number == self.current_level.info.kid_start_screen:
            block = self.current_level.info.kid_start_block
            # Calculate position (block is tile index in room)
            tile_x = block % 10
            tile_y = block // 10
            player_x = offset_x + (tile_x * TILE_WIDTH) + TILE_WIDTH // 2
            player_y = offset_y + (tile_y * TILE_HEIGHT) + TILE_HEIGHT // 2
            self.renderer.draw_player_marker(player_x, player_y)
        
        # Draw guards if they're in this room
        for guard in self.current_level.info.guards:
            if guard.is_active:
                # Guard block encoding might be room*30 + local_block
                guard_room = guard.block // 30
                if guard_room == room.room_number:
                    local_block = guard.block % 30
                    tile_x = local_block % 10
                    tile_y = local_block // 10
                    guard_x = offset_x + (tile_x * TILE_WIDTH) + TILE_WIDTH // 2
                    guard_y = offset_y + (tile_y * TILE_HEIGHT) + TILE_HEIGHT // 2
                    self.renderer.draw_guard_marker(guard_x, guard_y)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self) -> None:
        """Draw user interface elements"""
        # Title bar
        title = f"Level {self.current_level_num} - Room {self.current_room_num}"
        title_surf = self.font.render(title, True, (255, 255, 255))
        self.screen.blit(title_surf, (20, 20))
        
        # Instructions
        if self.show_info:
            instructions = [
                "Arrow Keys: Navigate rooms",
                "PgUp/PgDn: Prev/Next room",
                "0-9: Switch level",
                "S: Go to start room",
                "G: Toggle grid",
                "I: Toggle this info",
                "ESC: Quit"
            ]
            
            y = SCREEN_HEIGHT - 200
            for instruction in instructions:
                surf = self.small_font.render(instruction, True, (180, 180, 180))
                self.screen.blit(surf, (20, y))
                y += 25
        
        # Room connections
        room = self.get_current_room()
        if room:
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
                conn_text = "Connections: " + " ".join(connections)
                surf = self.small_font.render(conn_text, True, (200, 200, 200))
                self.screen.blit(surf, (20, 60))
    
    def run(self) -> None:
        """Main loop"""
        while self.running:
            self.handle_events()
            self.render()
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()


def main():
    """Entry point"""
    viewer = LevelViewer()
    viewer.run()


if __name__ == "__main__":
    main()
