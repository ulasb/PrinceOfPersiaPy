"""
Headless test harness: runs the game logic without a window and saves
canvas screenshots, optionally simulating input scripts.

Usage:
    python tests/harness.py --level 1 --ticks 5 --out /tmp/shot.png
    python tests/harness.py --level 1 --script "20:right" --out ...

Script format: comma-separated `ticks:keys` segments, keys among
l, r, u, d, s (left/right/up/down/shift), e.g. "5:, 20:r, 3:r+u".
"""

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame  # noqa: E402

from entities.player import Input  # noqa: E402
from game.game import Game  # noqa: E402
from game.sound import Sounds  # noqa: E402
from graphics.assets import Assets  # noqa: E402
from graphics.render import Renderer  # noqa: E402


def make_game(level: int) -> Game:
    pygame.init()
    pygame.display.set_mode((1, 1))
    game = Game(Assets(), Renderer(Assets()), Sounds(enabled=False))
    game.start_level(level)
    return game


def parse_script(script: str):
    steps = []
    for seg in script.split(","):
        seg = seg.strip()
        if not seg:
            continue
        ticks_s, keys = seg.split(":")
        steps.append((int(ticks_s), set(keys.split("+")) - {""}))
    return steps


def input_from(keys: set, prev: set) -> Input:
    return Input(
        left="l" in keys, right="r" in keys, up="u" in keys,
        down="d" in keys, shift="s" in keys,
        up_pressed="u" in keys and "u" not in prev,
        down_pressed="d" in keys and "d" not in prev,
        shift_pressed="s" in keys and "s" not in prev,
    )


def run(game: Game, script, verbose=False, trace=None):
    prev: set = set()
    t = 0
    for ticks, keys in script:
        for i in range(ticks):
            game.tick(input_from(keys, prev))
            prev = keys if i == 0 else keys
            t += 1
            if verbose:
                k = game.kid
                line = (f"t={t:4d} keys={'+'.join(sorted(keys)) or '-':10s}"
                        f" room={k.room:2d} x={k.x:6.1f} y={k.y:4d}"
                        f" row={k.row} face={k.face:+d} act={k.action}"
                        f" frame={k.frame:3d} hp={k.hp} alive={k.alive}"
                        f" state={game.state}")
                print(line)
                if trace is not None:
                    trace.append(line)
    return game


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", type=int, default=1)
    parser.add_argument("--ticks", type=int, default=2)
    parser.add_argument("--script", type=str, default="")
    parser.add_argument("--out", type=str, default="/tmp/pop_shot.png")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    game = make_game(args.level)
    script = parse_script(args.script) if args.script \
        else [(args.ticks, set())]
    run(game, script, verbose=not args.quiet)
    game.render()
    pygame.image.save(game.renderer.canvas, args.out)
    print(f"saved {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
