"""
Guards: enemy characters with simple combat AI.

Guard skill comes from the level data's `prog` byte. Guards engage the
kid when he is armed and in the same room/row, advance to sword range,
and mix strikes with blocks. They use the altset1 frame substitutions
(CHTAB4 variant per level) automatically via Char.frame_info.
"""

import random
from dataclasses import dataclass

from data import seqdata
from entities.char import Char
from game import constants as C
from levels import level as L


@dataclass
class GuardChar(Char):
    skill: int = 0
    engaged: bool = False
    cooldown: int = 0
    npc: bool = False        # princess & friends: no AI, just animate

    def __post_init__(self):
        self.char_id = C.CHAR_GUARD
        self.has_sword = True

    @classmethod
    def from_level(cls, g: L.Guard, level_num: int) -> "GuardChar":
        guard = cls()
        guard.room = g.room
        guard.row = g.block // 10
        guard.x = (g.block % 10) * C.TILE_W + 7
        guard.y = C.floor_y(guard.row)
        guard.face = g.face if g.face in (-1, 1) else -1
        guard.skill = g.prog if g.prog < 16 else 0
        guard.hp = 3 + min(guard.skill, 7)
        guard.max_hp = guard.hp
        # princess/vizier levels use their own char set & sequences
        if level_num == 14:
            guard.char_id = 5
            guard.npc = True
            guard.has_sword = False
        seq_addr = g.seq
        if seqdata.ORG <= seq_addr < seqdata.ORG + len(seqdata.SEQ_BYTES):
            guard.seq = seq_addr - seqdata.ORG
        else:
            guard.start_seq("Pstand" if guard.npc else "guardengarde")
        guard.animate()
        return guard

    # ------------------------------------------------------------ control
    def control(self, kid, level: L.LevelState) -> None:
        if not self.alive or self.npc:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
        same_arena = (kid.alive and kid.room == self.room
                      and kid.row == self.row)
        if not same_arena:
            if self.in_seq("advance", "fastadvance"):
                return
            return
        gap = (kid.x - self.x) * self.face
        want_face = 1 if kid.x > self.x else -1

        if not self.engaged:
            self.engaged = True
            self.face = want_face
            self.start_seq("guardengarde")
            return
        if not self.in_seq("ready", "guardengarde", "alertstand"):
            return  # mid-move
        if want_face != self.face:
            self.face = want_face
            return
        dist = abs(kid.x - self.x)
        if dist > 16:
            if self._floor_ahead(level):
                self.start_seq("advance")
            return
        if dist < 9:
            if self._floor_behind(level):
                self.start_seq("retreat")
            return
        if self.cooldown == 0:
            roll = random.random()
            strike_chance = 0.25 + 0.06 * self.skill
            if roll < strike_chance:
                self.start_seq("strike")
                self.cooldown = 4 + max(0, 6 - self.skill)
            elif roll < strike_chance + 0.25:
                self.start_seq("readyblock")
                self.cooldown = 2

    def _floor_ahead(self, level) -> bool:
        col = self.col + self.face
        return level.is_floor(self.room, col, self.row) \
            and not level.is_barrier(self.room, col, self.row)

    def _floor_behind(self, level) -> bool:
        col = self.col - self.face
        return level.is_floor(self.room, col, self.row) \
            and not level.is_barrier(self.room, col, self.row)
