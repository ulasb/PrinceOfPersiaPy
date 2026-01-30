"""
Sprite Viewer - Quick test of sprite loading and display

This script displays a grid of character sprites to verify extraction and loading.
"""

import pygame
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from graphics.sprites import SpriteManager

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Prince of Persia - Sprite Viewer")
clock = pygame.time.Clock()

# Initialize sprite manager
sprite_mgr = SpriteManager()

# Define sprites to display
sprite_sets = [
    ("CHTAB1", "Prince Sprites", range(1, 20)),
    ("CHTAB2", "Prince Sprites 2", range(1, 20)),
    ("CHTAB4.GD", "Guard", range(1, 15)),
    ("CHTAB4.SKEL", "Skeleton", range(1, 15)),
    ("CHTAB4.SHAD", "Shadow", range(1, 15)),
]

current_set = 0
scroll_offset = 0

# Font
font = pygame.font.Font(None, 24)
title_font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_LEFT:
                current_set = (current_set - 1) % len(sprite_sets)
                scroll_offset = 0
            elif event.key == pygame.K_RIGHT:
                current_set = (current_set + 1) % len(sprite_sets)
                scroll_offset = 0
            elif event.key == pygame.K_UP:
                scroll_offset = max(0, scroll_offset - 50)
            elif event.key == pygame.K_DOWN:
                scroll_offset += 50
    
    # Clear screen
    screen.fill((20, 20, 30))
    
    # Get current sprite set
    table, name, indices = sprite_sets[current_set]
    
    # Draw title
    title = title_font.render(f"{name} ({table})", True, (255, 255, 255))
    screen.blit(title, (20, 20))
    
    # Draw instructions
    instructions = [
        "← → : Switch sprite set",
        "↑ ↓ : Scroll",
        "ESC : Quit"
    ]
    y = 60
    for inst in instructions:
        surf = font.render(inst, True, (180, 180, 180))
        screen.blit(surf, (20, y))
        y += 25
    
    # Draw sprites in a grid
    x = 50
    y = 180 - scroll_offset
    col = 0
    max_cols = 8
    
    for idx in indices:
        sprite = sprite_mgr.get_character_sprite(table, idx)
        
        if sprite:
            # Scale up for visibility
            scaled = sprite_mgr.scale_sprite(sprite, 4.0)
            
            # Draw background box
            box_rect = pygame.Rect(x - 5, y - 5, 
                                   scaled.get_width() + 10, 
                                   scaled.get_height() + 10)
            pygame.draw.rect(screen, (40, 40, 50), box_rect)
            pygame.draw.rect(screen, (80, 80, 90), box_rect, 2)
            
            # Draw sprite
            screen.blit(scaled, (x, y))
            
            # Draw index label
            label = font.render(f"#{idx}", True, (200, 200, 200))
            screen.blit(label, (x, y + scaled.get_height() + 5))
            
            # Move to next position
            col += 1
            if col >= max_cols:
                col = 0
                x = 50
                y += 120
            else:
                x += 150
        else:
            # Sprite not found
            pygame.draw.rect(screen, (60, 20, 20), (x, y, 50, 50))
            label = font.render(f"#{idx}", True, (255, 100, 100))
            screen.blit(label, (x, y + 55))
            
            col += 1
            if col >= max_cols:
                col = 0
                x = 50
                y += 120
            else:
                x += 150
    
    # Draw sprite set indicator
    indicator = font.render(f"Set {current_set + 1}/{len(sprite_sets)}", True, (150, 150, 150))
    screen.blit(indicator, (screen.get_width() - 150, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("Sprite viewer closed.")
