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
    justblocked: int = 0     # blocktime ticks: can't parry again yet
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
        if self.justblocked > 0:
            self.justblocked -= 1
        same_arena = (kid.alive and kid.room == self.room
                      and kid.row == self.row)
        if not same_arena:
            return
        want_face = 1 if kid.x > self.x else -1

        if not self.engaged:
            self.engaged = True
            self.face = want_face
            self.start_seq("guardengarde")
            return
        dist = abs(kid.x - self.x)
        if self.frame == 161:
            # parried the kid's blade: counter or fall back
            if random.random() < 0.3 + 0.07 * self.skill:
                self.start_seq("blocktostrike")
            else:
                self.start_seq("retreat")
            return
        # parry reactively while the kid's strike is committed
        # (FightCtrl: the enemy blocks when it sees the kid at guy4)
        if kid.sword_drawn and kid.frame == 152 \
                and dist < C.BLOCK_FAR and self.justblocked == 0 \
                and self.frame in (158, 165, 168, 170, 171) \
                and random.random() < 0.25 + 0.08 * self.skill:
            self.start_seq("readyblock")
            return
        if not self.in_seq("ready", "guardengarde", "alertstand"):
            return  # mid-move
        if want_face != self.face:
            self.face = want_face
            return
        if not kid.sword_drawn:
            # run the defenseless kid through
            if dist > C.OFFGUARD_RANGE:
                if self._floor_ahead(level):
                    self.start_seq("advance")
            elif self.cooldown == 0:
                self.start_seq("strike")
                self.cooldown = 6
            return
        if dist >= C.STRIKE_FAR - 4:
            if self._floor_ahead(level):
                self.start_seq("advance")
            return
        if dist < C.STRIKE_NEAR:
            if self._floor_behind(level):
                self.start_seq("retreat")
            return
        if self.cooldown == 0:
            if random.random() < 0.25 + 0.06 * self.skill:
                self.start_seq("strike")
                self.cooldown = 4 + max(0, 6 - self.skill)

    def _floor_ahead(self, level) -> bool:
        col = self.col + self.face
        return level.is_floor(self.room, col, self.row) \
            and not level.is_barrier(self.room, col, self.row)

    def _floor_behind(self, level) -> bool:
        col = self.col - self.face
        return level.is_floor(self.room, col, self.row) \
            and not level.is_barrier(self.room, col, self.row)
