"""
Synthesized retro sound effects.

The Apple II original produced clicks and beeps from the speaker; we
synthesize similar minimal effects at startup so the repo needs no audio
assets.
"""

from typing import Dict, Optional

import numpy as np
import pygame

RATE = 22050


def _to_sound(wave: np.ndarray, volume: float = 0.5) -> pygame.mixer.Sound:
    data = np.clip(wave * volume, -1, 1)
    stereo = np.repeat((data * 32767).astype(np.int16)[:, None], 2, axis=1)
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))


def _square(freq: float, dur: float, sweep: float = 1.0) -> np.ndarray:
    n = int(RATE * dur)
    t = np.arange(n) / RATE
    f = freq * np.power(sweep, t / max(dur, 1e-6))
    phase = np.cumsum(2 * np.pi * f / RATE)
    env = np.linspace(1, 0, n) ** 0.5
    return np.sign(np.sin(phase)) * env


def _noise(dur: float, lowpass: int = 1) -> np.ndarray:
    n = int(RATE * dur)
    w = np.random.uniform(-1, 1, n)
    for _ in range(lowpass):
        w = np.convolve(w, np.ones(8) / 8, mode="same")
    env = np.linspace(1, 0, n) ** 2
    return w * env


class Sounds:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.bank: Dict[str, pygame.mixer.Sound] = {}
        if not enabled:
            return
        try:
            pygame.mixer.init(frequency=RATE, channels=2)
        except pygame.error:
            self.enabled = False
            return
        self.bank = {
            "tap": _to_sound(_noise(0.04), 0.25),
            "land": _to_sound(_noise(0.12, 2), 0.5),
            "oof": _to_sound(_square(90, 0.25, 0.5), 0.4),
            "splat": _to_sound(_noise(0.4, 3), 0.7),
            "plate": _to_sound(_square(660, 0.05), 0.3),
            "gate_move": _to_sound(_noise(0.5, 4), 0.25),
            "gate_drop": _to_sound(_noise(0.25, 2), 0.5),
            "gate_slam": _to_sound(_noise(0.3, 1), 0.7),
            "spikes": _to_sound(_square(1200, 0.08, 0.4), 0.35),
            "loose": _to_sound(_square(300, 0.06), 0.3),
            "loose_fall": _to_sound(_noise(0.15, 2), 0.4),
            "floor_crash": _to_sound(_noise(0.35, 2), 0.7),
            "sword_clash": _to_sound(_square(2200, 0.09, 0.6), 0.4),
            "sword_hit": _to_sound(_noise(0.18, 1), 0.6),
            "death": _to_sound(_square(400, 0.6, 0.25), 0.5),
            "guard_death": _to_sound(_square(300, 0.5, 0.3), 0.5),
            "potion": _to_sound(_square(880, 0.3, 1.6), 0.35),
            "pickup": _to_sound(_square(1320, 0.2, 1.3), 0.35),
            "exit_open": _to_sound(_square(220, 0.6, 2.0), 0.4),
            "level_done": _to_sound(_square(523, 0.5, 1.5), 0.4),
            "slicer": _to_sound(_noise(0.1, 1), 0.5),
        }

    def play(self, name: str) -> None:
        if self.enabled and name in self.bank:
            self.bank[name].play()
