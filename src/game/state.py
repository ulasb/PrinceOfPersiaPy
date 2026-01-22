"""
Prince of Persia - Game State Management

Manages the overall game state and transitions between different game modes.
Corresponds to TOPCTRL.S and MASTER.S in the original source.
"""

from typing import Optional
import pygame

from game.constants import (
    GameState,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_UI_TEXT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SHOW_FPS,
)


class GameStateManager:
    """
    Manages game state transitions and delegates to appropriate controllers.
    
    This class acts as the top-level controller, similar to the TOPCTRL.S
    and MASTER.S modules in the original Apple II source.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the game state manager.
        
        Args:
            screen: The main Pygame display surface
        """
        self.screen = screen
        self.current_state = GameState.TITLE
        self.running = True
        
        # Frame counter
        self.frame_count = 0
        self.fps_counter = 0.0
        self.fps_display = 0
        
        # Initialize font for UI
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # State controllers (to be implemented)
        self.title_controller = None
        self.intro_controller = None
        self.game_controller = None
        self.cutscene_controller = None
        
        print("Prince of Persia - Python Port")
        print("Initializing game...")
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle Pygame events.
        
        Args:
            event: The Pygame event to handle
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC key exits or pauses
                if self.current_state == GameState.PLAYING:
                    self.change_state(GameState.PAUSED)
                elif self.current_state == GameState.PAUSED:
                    self.change_state(GameState.PLAYING)
                else:
                    self.running = False
                    
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # Enter/Space starts game from title
                if self.current_state == GameState.TITLE:
                    self.change_state(GameState.PLAYING)
                elif self.current_state == GameState.PAUSED:
                    self.change_state(GameState.PLAYING)
    
    def update(self, dt: float) -> None:
        """
        Update the current game state.
        
        Args:
            dt: Delta time in seconds since last frame
        """
        self.frame_count += 1
        
        # Update FPS counter
        if SHOW_FPS:
            self.fps_counter += dt
            if self.fps_counter >= 1.0:
                self.fps_display = int(1.0 / dt) if dt > 0 else 0
                self.fps_counter = 0.0
        
        # Delegate to appropriate state controller
        if self.current_state == GameState.TITLE:
            self.update_title(dt)
        elif self.current_state == GameState.INTRO:
            self.update_intro(dt)
        elif self.current_state == GameState.PLAYING:
            self.update_playing(dt)
        elif self.current_state == GameState.PAUSED:
            self.update_paused(dt)
        elif self.current_state == GameState.CUTSCENE:
            self.update_cutscene(dt)
        elif self.current_state == GameState.GAME_OVER:
            self.update_game_over(dt)
        elif self.current_state == GameState.VICTORY:
            self.update_victory(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the current game state.
        
        Args:
            screen: The surface to render to
        """
        # Clear screen
        screen.fill(COLOR_BLACK)
        
        # Delegate to appropriate state renderer
        if self.current_state == GameState.TITLE:
            self.render_title(screen)
        elif self.current_state == GameState.INTRO:
            self.render_intro(screen)
        elif self.current_state == GameState.PLAYING:
            self.render_playing(screen)
        elif self.current_state == GameState.PAUSED:
            self.render_paused(screen)
        elif self.current_state == GameState.CUTSCENE:
            self.render_cutscene(screen)
        elif self.current_state == GameState.GAME_OVER:
            self.render_game_over(screen)
        elif self.current_state == GameState.VICTORY:
            self.render_victory(screen)
        
        # Draw FPS counter
        if SHOW_FPS:
            fps_text = self.font_small.render(
                f"FPS: {self.fps_display}",
                True,
                COLOR_UI_TEXT
            )
            screen.blit(fps_text, (SCREEN_WIDTH - 100, 10))
    
    def change_state(self, new_state: GameState) -> None:
        """
        Change to a new game state.
        
        Args:
            new_state: The state to transition to
        """
        print(f"State change: {self.current_state} -> {new_state}")
        self.current_state = new_state
        
    # ==========================================================================
    # State Update Methods
    # ==========================================================================
    
    def update_title(self, dt: float) -> None:
        """Update title screen state"""
        pass
    
    def update_intro(self, dt: float) -> None:
        """Update intro/cutscene state"""
        pass
    
    def update_playing(self, dt: float) -> None:
        """Update gameplay state"""
        # TODO: Implement game logic
        pass
    
    def update_paused(self, dt: float) -> None:
        """Update paused state"""
        pass
    
    def update_cutscene(self, dt: float) -> None:
        """Update cutscene state"""
        pass
    
    def update_game_over(self, dt: float) -> None:
        """Update game over state"""
        pass
    
    def update_victory(self, dt: float) -> None:
        """Update victory state"""
        pass
    
    # ==========================================================================
    # State Render Methods
    # ==========================================================================
    
    def render_title(self, screen: pygame.Surface) -> None:
        """Render title screen"""
        title_text = self.font_large.render(
            "PRINCE OF PERSIA",
            True,
            COLOR_WHITE
        )
        subtitle_text = self.font_medium.render(
            "Python Port",
            True,
            COLOR_UI_TEXT
        )
        start_text = self.font_small.render(
            "Press ENTER to Start",
            True,
            COLOR_UI_TEXT
        )
        
        # Center the text
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        
        screen.blit(title_text, title_rect)
        screen.blit(subtitle_text, subtitle_rect)
        
        # Blink the start text
        if (self.frame_count // 30) % 2 == 0:
            screen.blit(start_text, start_rect)
    
    def render_intro(self, screen: pygame.Surface) -> None:
        """Render intro/cutscene"""
        pass
    
    def render_playing(self, screen: pygame.Surface) -> None:
        """Render gameplay"""
        # TODO: Render game world
        # For now, just show a placeholder
        text = self.font_medium.render(
            "Game World (In Development)",
            True,
            COLOR_WHITE
        )
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
    
    def render_paused(self, screen: pygame.Surface) -> None:
        """Render paused state"""
        # First render the game
        self.render_playing(screen)
        
        # Then overlay pause screen
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, COLOR_WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, pause_rect)
    
    def render_cutscene(self, screen: pygame.Surface) -> None:
        """Render cutscene"""
        pass
    
    def render_game_over(self, screen: pygame.Surface) -> None:
        """Render game over screen"""
        game_over_text = self.font_large.render("GAME OVER", True, COLOR_WHITE)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, game_over_rect)
    
    def render_victory(self, screen: pygame.Surface) -> None:
        """Render victory screen"""
        victory_text = self.font_large.render("VICTORY!", True, COLOR_WHITE)
        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(victory_text, victory_rect)
