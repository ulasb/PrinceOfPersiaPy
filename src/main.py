"""
Prince of Persia - Python port of the Apple II original.

Original 6502 source by Jordan Mechner (1985-1989). This port runs the
original animation/sequence data on a modern engine. Educational and
preservation purposes only.

Run:  python src/main.py [--level N] [--scale N] [--mute]
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame  # noqa: E402

from entities.player import Input  # noqa: E402
from game import constants as C  # noqa: E402
from game.game import (Game, STATE_DEAD, STATE_GAME_OVER,  # noqa: E402
                       STATE_PLAYING, STATE_TITLE, STATE_VICTORY)
from game.sound import Sounds  # noqa: E402
from graphics.assets import Assets  # noqa: E402
from graphics.render import Renderer  # noqa: E402


def gather_input(pressed_edges: set) -> Input:
    keys = pygame.key.get_pressed()
    shift = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    return Input(
        left=keys[pygame.K_LEFT] or keys[pygame.K_a],
        right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
        up=keys[pygame.K_UP] or keys[pygame.K_w],
        down=keys[pygame.K_DOWN] or keys[pygame.K_s],
        shift=shift,
        up_pressed=pygame.K_UP in pressed_edges
        or pygame.K_w in pressed_edges,
        down_pressed=pygame.K_DOWN in pressed_edges
        or pygame.K_s in pressed_edges,
        shift_pressed=pygame.K_LSHIFT in pressed_edges
        or pygame.K_RSHIFT in pressed_edges,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prince of Persia")
    parser.add_argument("--level", type=int, default=None,
                        help="start at level N (1-14)")
    parser.add_argument("--scale", type=int, default=C.DISPLAY_SCALE)
    parser.add_argument("--mute", action="store_true")
    args = parser.parse_args()

    pygame.init()
    scale = max(1, args.scale)
    window = pygame.display.set_mode(
        (C.CANVAS_W * scale, C.CANVAS_H * scale))
    pygame.display.set_caption(f"{C.GAME_TITLE} - {C.GAME_VERSION}")
    clock = pygame.time.Clock()

    sounds = Sounds(enabled=not args.mute)
    assets = Assets()
    renderer = Renderer(assets)
    game = Game(assets, renderer, sounds)
    if args.level:
        game.start_level(args.level)

    frame_count = 0
    pressed_edges: set = set()
    paused = False
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                pressed_edges.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    if game.state == STATE_TITLE:
                        running = False
                    else:
                        paused = not paused
                elif event.key == pygame.K_RETURN:
                    if game.state == STATE_TITLE:
                        game.ticks_left = C.TIME_LIMIT_TICKS
                        game.start_level(args.level or C.FIRST_LEVEL)
                    elif game.state == STATE_DEAD:
                        game.restart_level()
                    elif game.state == STATE_GAME_OVER:
                        game.ticks_left = C.TIME_LIMIT_TICKS
                        game.restart_level()
                    elif game.state == STATE_VICTORY:
                        game.state = STATE_TITLE
                elif event.key == pygame.K_r \
                        and game.state == STATE_PLAYING:
                    game.restart_level()
                elif event.key == pygame.K_F5 \
                        and game.state == STATE_PLAYING:
                    game.quicksave()
                elif event.key == pygame.K_F9:
                    game.quickload()
                elif event.key == pygame.K_RIGHTBRACKET \
                        and game.state == STATE_PLAYING:
                    game.next_level()
                elif event.key == pygame.K_LEFTBRACKET \
                        and game.state == STATE_PLAYING \
                        and game.level_num > 1:
                    game.start_level(game.level_num - 1)

        frame_count += 1
        if frame_count % C.FRAMES_PER_TICK == 0 and not paused:
            game.tick(gather_input(pressed_edges))
            pressed_edges.clear()

        game.render()
        canvas = renderer.canvas
        pygame.transform.scale(
            canvas, window.get_size(), window)
        if paused:
            font = pygame.font.Font(None, 24 * scale // 2)
            text = font.render("PAUSED", True, (255, 255, 255))
            window.blit(text, (window.get_width() // 2
                               - text.get_width() // 2,
                               window.get_height() // 2))
        pygame.display.flip()
        clock.tick(C.FPS)

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
