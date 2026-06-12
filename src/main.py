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


class Recorder:
    """F10 movie recording: one frame per game tick (12/s) saved as
    native-resolution PNGs plus a JSONL stream of the full game state,
    so a recording can be replayed and analyzed frame by frame."""

    def __init__(self):
        self.dir: Path | None = None
        self.count = 0
        self._jsonl = None

    @property
    def active(self) -> bool:
        return self.dir is not None

    def start(self, game) -> None:
        import time as _time
        stamp = _time.strftime("%Y%m%d_%H%M%S")
        self.dir = Path("recordings") / f"rec_{stamp}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.count = 0
        self._jsonl = open(self.dir / "state.jsonl", "w")
        game.show_message("RECORDING STARTED", ticks=18)

    def capture(self, game) -> None:
        import json
        # the canvas may carry a garbage alpha channel in headed mode
        frame = game.renderer.canvas.convert(24)
        pygame.image.save(
            frame, str(self.dir / f"frame_{self.count:05d}.png"))
        info = game.debug_info()
        info["rec_frame"] = self.count
        info["message"] = game.message
        self._jsonl.write(json.dumps(info, default=str) + "\n")
        self.count += 1

    def stop(self, game) -> None:
        import json
        (self.dir / "meta.json").write_text(json.dumps({
            "frames": self.count,
            "ticks_per_second": C.TICKS_PER_SECOND,
            "level": game.level_num,
        }, indent=2))
        self._jsonl.close()
        game.show_message(f"SAVED {self.dir.name} ({self.count} FRAMES)",
                          ticks=30)
        self.dir = None
        self._jsonl = None

    def draw_indicator(self, window, frame_count: int) -> None:
        if not self.active or (frame_count // 30) % 2:
            return  # blink
        scale = max(1, window.get_width() // C.CANVAS_W)
        x = window.get_width() - 14 * scale
        pygame.draw.circle(window, (230, 40, 40), (x, 6 * scale), 3 * scale)
        font = pygame.font.Font(None, 7 * scale)
        text = font.render("REC", True, (230, 40, 40))
        window.blit(text, (x + 5 * scale,
                           6 * scale - text.get_height() // 2))


def save_debug_dump(game, window) -> Path:
    """F12: save the visible frame plus a JSON of the full game state
    (kid/guard positions, sequence names, room tiles, trap states) so a
    'this looks wrong' moment can be reported precisely.

    The frame is re-composed from the game's software canvas: reading
    back the accelerated display surface returns garbage on some
    platforms (e.g. Metal-backed windows on macOS)."""
    import json
    import time as _time

    out = Path("screenshots")
    out.mkdir(exist_ok=True)
    stamp = _time.strftime("%Y%m%d_%H%M%S")
    png = out / f"debug_{stamp}.png"
    frame = pygame.transform.scale(
        game.renderer.canvas, window.get_size())
    game.renderer.draw_text_overlay(frame)
    # convert to 24-bit: in headed mode the canvas inherits an alpha
    # channel from the display format, and blitted pixels carry zero
    # alpha, which turns the saved PNG into a transparent mess
    pygame.image.save(frame.convert(24), str(png))
    (out / f"debug_{stamp}.json").write_text(
        json.dumps(game.debug_info(), indent=2, default=str))
    return png


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
    parser.add_argument("--autodump", type=int, default=0,
                        help="debug: save an F12-style dump after N frames")
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
    dump_requested = False
    recorder = Recorder()
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
                elif event.key == pygame.K_F12:
                    dump_requested = True
                elif event.key == pygame.K_F10:
                    if recorder.active:
                        recorder.stop(game)
                    else:
                        recorder.start(game)
                elif event.key == pygame.K_RIGHTBRACKET \
                        and game.state == STATE_PLAYING:
                    game.next_level()
                elif event.key == pygame.K_LEFTBRACKET \
                        and game.state == STATE_PLAYING \
                        and game.level_num > 1:
                    game.start_level(game.level_num - 1)

        frame_count += 1
        if args.autodump and frame_count == args.autodump:
            dump_requested = True
        if frame_count % C.FRAMES_PER_TICK == 0 and not paused:
            game.tick(gather_input(pressed_edges))
            pressed_edges.clear()

        game.render()
        if recorder.active and frame_count % C.FRAMES_PER_TICK == 0:
            recorder.capture(game)
        canvas = renderer.canvas
        pygame.transform.scale(
            canvas, window.get_size(), window)
        renderer.draw_text_overlay(window)
        recorder.draw_indicator(window, frame_count)
        if dump_requested:
            dump_requested = False
            path = save_debug_dump(game, window)
            game.show_message("SAVED " + path.name, ticks=30)
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
