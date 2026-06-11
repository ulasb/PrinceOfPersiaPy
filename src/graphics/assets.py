"""
Asset loading: extracted PNG images from the original image tables.

Character images come from CHTAB tables (1-7); table 4 has one variant
per enemy type (GD/SKEL/SHAD/VIZ/FAT). Background pieces come from BGTAB1
(common) and BGTAB2 (level-type specific); each has a dungeon (.DUN) and
palace (.PAL) variant. All images were extracted facing LEFT; right-facing
characters are drawn mirrored.
"""

from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

ASSETS = Path(__file__).resolve().parents[2] / "assets" / "graphics"


class Assets:
    def __init__(self, guard_table: str = "GD", palace: bool = False):
        self._cache: Dict[Tuple[str, int, bool], Optional[pygame.Surface]] = {}
        self.guard_table = guard_table
        self.palace = palace

    def configure(self, guard_table: str, palace: bool) -> None:
        if (guard_table, palace) != (self.guard_table, self.palace):
            self.guard_table = guard_table
            self.palace = palace
            self._cache.clear()

    def _load(self, sub: str, table: str, index: int) -> Optional[pygame.Surface]:
        path = ASSETS / sub / f"{table}_{index:03d}.png"
        if not path.exists():
            return None
        return pygame.image.load(str(path)).convert_alpha()

    def char_image(self, table_num: int, index: int,
                   mirrored: bool = False) -> Optional[pygame.Surface]:
        """Character image by decoded table number (0-6) and image number."""
        names = {
            0: "CHTAB1", 1: "CHTAB2", 2: "CHTAB3",
            3: f"CHTAB4.{self.guard_table}",
            4: "CHTAB5", 5: "CHTAB6.A", 6: "CHTAB7",
        }
        name = names.get(table_num)
        if name is None:
            return None
        key = (name, index, mirrored)
        if key not in self._cache:
            img = self._load("chtab", name, index)
            if img is None and table_num == 5:
                img = self._load("chtab", "CHTAB6.B", index)
            if img is not None and mirrored:
                img = pygame.transform.flip(img, True, False)
            self._cache[key] = img
        return self._cache[key]

    def bg_image(self, image_id: int) -> Optional[pygame.Surface]:
        """Background piece by coded id (bit 7 = BGTAB2, low 7 bits = #)."""
        if image_id == 0:
            return None
        variant = "PAL" if self.palace else "DUN"
        table = "BGTAB2" if image_id & 0x80 else "BGTAB1"
        index = image_id & 0x7F
        key = (f"{table}.{variant}", index, False)
        if key not in self._cache:
            self._cache[key] = self._load("bgtab", f"{table}.{variant}", index)
        return self._cache[key]
