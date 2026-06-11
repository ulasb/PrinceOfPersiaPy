"""
Room and character renderer.

Follows the original drawing model (FRAMEADV.S): each block position
draws the C-section of the piece below-left, the B-section of the piece
to the left, then its own A-section (anchored at block_bot - 3) and
D-section (anchored at block_bot). Foreground (front) pieces are drawn
over the characters. All pieces use lower-left anchoring.

The canvas is 280x192 hi-res pixels plus an 8px HUD strip; a game pixel
(140-res) is two canvas pixels wide.
"""

from typing import Optional

import pygame

from game import constants as C
from graphics import bgdata as BG
from graphics.assets import Assets
from levels import level as L

BLACK = (0, 0, 0)
HUD_BG = (0, 0, 0)
HP_COLOR = (230, 30, 30)
ENEMY_HP_COLOR = (60, 100, 255)
TEXT_COLOR = (255, 255, 255)


class Renderer:
    def __init__(self, assets: Assets):
        self.assets = assets
        self.canvas = pygame.Surface((C.CANVAS_W, C.CANVAS_H))
        pygame.font.init()
        # text is rendered crisp at window resolution by the display layer
        self.hud_text = ""
        self.overlay_title = ""
        self.overlay_lines: list = []

    # ---------------------------------------------------------- low level
    def blit_ll(self, image: Optional[pygame.Surface],
                x: int, bottom: int) -> None:
        """Blit with lower-left anchor (original Y convention)."""
        if image is None:
            return
        self.canvas.blit(image, (x, bottom - image.get_height() + 1))

    def piece(self, image_id: int, col: int, bottom: int,
              byte_dx: int = 0) -> None:
        x = col * 28 + byte_dx * 7
        img = self.assets.bg_image(image_id, parity=x & 1)
        self.blit_ll(img, x, bottom)

    # --------------------------------------------------------- background
    def draw_room(self, level: L.LevelState, room: int) -> None:
        self.canvas.fill(BLACK)
        if room == 0:
            return
        for row in range(-1, 3):
            for col in range(-1, 11):
                self._draw_block(level, room, col, row)

    def _tile(self, level, room, col, row):
        return level.tile(room, col, row)

    def _spec(self, level, room, col, row):
        return level.spec(room, col, row)

    def _draw_block(self, level, room: int, col: int, row: int) -> None:
        ay = C.block_bot(row) - 3        # A/B anchor
        dy = C.block_bot(row)            # C/D anchor
        t = self._tile(level, room, col, row)

        # C-section of the piece below & to the left
        tc = self._tile(level, room, col - 1, row + 1)
        if tc == L.BLOCK:
            self.piece(BG.BLOCKC[self._spec(level, room, col - 1, row + 1)
                                 % len(BG.BLOCKC)], col, dy)
        elif tc in (L.PANELWIF, L.PANELWOF):
            self.piece(BG.PANELC[self._spec(level, room, col - 1, row + 1)
                                 % len(BG.PANELC)], col, dy)
        elif tc == L.GATE:
            self._draw_gate_c(level, room, col - 1, row + 1, col, dy)
        elif tc == L.SLICER:
            pass  # slicer C drawn with the slicer block itself
        else:
            self.piece(BG.PIECEC[tc], col, dy)

        # B-section of the piece to the left
        tb = self._tile(level, room, col - 1, row)
        sb = self._spec(level, room, col - 1, row)
        if t != L.BLOCK:  # hidden by a solid block
            if tb == L.BLOCK:
                # wall side face leans into this block (PIECEBY[block]=2)
                self.piece(BG.BLOCKB[sb % len(BG.BLOCKB)], col, ay + 2)
            elif tb in (L.PANELWIF, L.PANELWOF):
                self.piece(BG.PANELB[sb % len(BG.PANELB)], col, ay + 3)
            elif tb == L.SPIKES:
                st = level.spike_state(room, col - 1, row)
                self.piece(BG.SPIKEB[st], col, ay)
            elif tb == L.LOOSE:
                ls = level.loose_state(room, col - 1, row)
                wig = ls % len(BG.LOOSEBY) if ls else 0
                self.piece(BG.LOOSE_B, col, ay + BG.LOOSEBY[wig] - 1)
            elif tb == L.GATE:
                self._draw_gate_b(level, room, col - 1, row, col, ay)
            else:
                self.piece(BG.PIECEB[tb], col, ay + BG.PIECEBY[tb])

        # A-section of this piece
        if t == L.BLOCK:
            # solid walls: the bright brick face fills the whole tile
            # (blockfr; the original queues it as a front piece)
            self.piece(BG.BLOCKFR[self._spec(level, room, col, row)
                                  % len(BG.BLOCKFR)], col, ay)
        elif t == L.SPIKES:
            st = level.spike_state(room, col, row)
            self.piece(BG.SPIKEA[st], col, ay)
        elif t == L.LOOSE:
            ls = level.loose_state(room, col, row)
            wig = ls % len(BG.LOOSEBY) if ls else 0
            self.piece(BG.LOOSEA[wig], col, ay + BG.LOOSEBY[wig])
        elif t == L.TORCH:
            self.piece(BG.PIECEA[t], col, ay + BG.PIECEAY[t])
            # the torch bracket is the tile's B-section, drawn one block
            # to the right; the flame sits on its sconce cup
            frame = BG.TORCHFLAME[
                (pygame.time.get_ticks() // 90 + col * 3 + row * 5)
                % len(BG.TORCHFLAME)]
            self.piece(frame, col + 1, ay - 43, byte_dx=1)
        elif t in (L.EXIT, L.EXIT2):
            self._draw_exit(level, room, col, row, ay)
        elif t == L.SLICER:
            self._draw_slicer(level, room, col, row, ay, dy)
        elif t == L.FLASK:
            self.piece(BG.PIECEA[L.FLOOR], col, ay)
            bob = (pygame.time.get_ticks() // 220 + col) % 2
            self.piece(BG.SPECIALFLASK, col, ay - 14 + bob, byte_dx=2)
        else:
            self.piece(BG.PIECEA[t], col, ay + BG.PIECEAY[t])

        # D-section of this piece
        if t == L.BLOCK:
            self.piece(BG.BLOCKD[self._spec(level, room, col, row)
                                 % len(BG.BLOCKD)], col, dy)
        elif t == L.LOOSE:
            ls = level.loose_state(room, col, row)
            wig = ls % len(BG.LOOSED) if ls else 0
            self.piece(BG.LOOSED[wig], col, dy + BG.LOOSEBY[wig])
        elif t == L.SLICER:
            pass
        else:
            self.piece(BG.PIECED[t], col, dy)

    # gates: bars hang from the top of the block down to the gate bottom;
    # position 0 = fully closed (bottom at block_bot), GATE_MAX = open.
    def _gate_bottom(self, level, room, col, row) -> int:
        pos = level.gate_pos(room, col, row)
        return C.block_bot(row) - 16 - (pos * 44 // C.GATE_MAX)

    def _draw_gate_b(self, level, room, col, row, at_col, ay) -> None:
        bottom = self._gate_bottom(level, room, col, row)
        top = C.block_top(row) - 8
        img = self.assets.bg_image(BG.GATE8B[7])
        seg_h = img.get_height() if img else 8
        y = bottom
        while y > top:
            self.blit_ll(img, at_col * 28, y)
            y -= seg_h
        self.piece(BG.GATEBOT_ORA, at_col, bottom + 4)

    def _draw_gate_c(self, level, room, col, row, at_col, dy) -> None:
        # the part of the gate visible in the block above-right
        bottom = self._gate_bottom(level, room, col, row)
        top_of_above = C.block_top(row) - 10
        img = self.assets.bg_image(BG.GATE8C[0])
        if img is None:
            return
        y = min(bottom, C.block_top(row) + 2)
        seg_h = img.get_height()
        while y > top_of_above:
            self.blit_ll(img, at_col * 28, y)
            y -= seg_h

    def _draw_exit(self, level, room, col, row, ay) -> None:
        self.piece(BG.PIECEA[L.FLOOR], col, ay)
        opening = self._spec(level, room, col, row)
        t = self._tile(level, room, col, row)
        if t == L.EXIT:
            self.piece(BG.EXIT_STAIRS, col, ay)
        else:
            door = self.assets.bg_image(BG.EXIT_DOOR)
            if door is not None:
                # door slides up as it opens
                lift = min(int(opening), 40) if opening else 0
                area = pygame.Rect(0, lift,
                                   door.get_width(),
                                   door.get_height() - lift)
                x = col * 28
                yy = ay - door.get_height() + 1
                self.canvas.blit(door, (x, yy), area)
            self.piece(BG.EXIT_TOP, col, ay - 48)

    def _draw_slicer(self, level, room, col, row, ay, dy) -> None:
        self.piece(BG.PIECEA[L.FLOOR], col, ay)
        f = level.slicer_frame(room, col, row)
        if 0 < f < len(BG.SLICERTOP):
            self.piece(BG.SLICERTOP[f], col, C.block_top(row) + 20)
        if 0 <= f < len(BG.SLICERBOT):
            self.piece(BG.SLICERBOT[f], col, ay)
        self.piece(BG.PIECED[L.FLOOR], col, dy)

    # -------------------------------------------------------- foreground
    def draw_foreground(self, level: L.LevelState, room: int) -> None:
        if room == 0:
            return
        for row in range(-1, 3):
            for col in range(-1, 11):
                t = self._tile(level, room, col, row)
                ay = C.block_bot(row) - 3
                if t == L.SLICER:
                    f = level.slicer_frame(room, col, row)
                    if 0 <= f < len(BG.SLICERFRNT):
                        self.piece(BG.SLICERFRNT[f], col, ay)
                    continue
                if t == L.BLOCK:
                    continue
                fi = BG.FRONTI[t]
                if fi:
                    self.piece(fi, col, ay + BG.FRONTY[t],
                               byte_dx=BG.FRONTX[t])
                if t == L.GATE:
                    self._draw_gate_b(level, room, col, row, col + 1, ay)

    # -------------------------------------------------------- characters
    def draw_char(self, char) -> None:
        if not char.frame or char.room == 0:
            return
        info = char.frame_info()
        mirrored = char.face > 0
        fx = int(2 * char.x) + info.dx * char.face
        bottom = char.y + info.dy
        # characters use a fixed color phase: per-position phase would
        # make fringe colors flicker between animation frames
        img = self.assets.char_image(info.table, info.image, mirrored,
                                     parity=0)
        if img is None:
            return
        x = fx - (img.get_width() - 7) if mirrored else fx
        self.blit_ll(img, x, bottom)
        if info.sword and self._sword_visible(char):
            self._draw_sword(char, info, fx, bottom)

    @staticmethod
    def _sword_visible(char) -> bool:
        """The sword overlay only shows when the sword is out: the kid in
        en-garde / sheathing / pickup moves, guards while fighting."""
        if not char.has_sword:
            return False
        if getattr(char, "npc", False):
            return False
        drawn = getattr(char, "sword_drawn", None)
        if drawn is None:  # guards: sword out once engaged and alive
            return char.alive and getattr(char, "engaged", True)
        return drawn or char.in_seq(
            "pickupsword", "resheathe", "fastsheathe", "turndraw",
            "engarde", "stabbed", "dropdead")

    def _draw_sword(self, char, info, fx: int, bottom: int) -> None:
        from data.framedefs import SWORDTAB
        entry = SWORDTAB.get(info.sword)
        if entry is None:
            return
        image, sdx, sdy = entry
        mirrored = char.face > 0
        sx = fx + sdx * char.face
        img = self.assets.char_image(2, image, mirrored, parity=0)
        if img is None:
            return
        if mirrored:
            sx -= img.get_width() - 7
        self.blit_ll(img, sx, char.y + sdy)

    # --------------------------------------------------------------- HUD
    def draw_hud(self, kid, opponent, level_num: int,
                 message: str = "") -> None:
        hud = pygame.Rect(0, C.HUD_Y, C.CANVAS_W, C.CANVAS_H - C.HUD_Y)
        self.canvas.fill(HUD_BG, hud)
        for i in range(kid.max_hp):
            color = HP_COLOR if i < kid.hp else (70, 20, 20)
            x = 2 + i * 7
            pygame.draw.polygon(self.canvas, color, [
                (x, C.HUD_Y + 2), (x + 5, C.HUD_Y + 2),
                (x + 2, C.HUD_Y + 6)])
        if opponent is not None and opponent.alive:
            for i in range(opponent.hp):
                x = C.CANVAS_W - 8 - i * 7
                pygame.draw.polygon(self.canvas, ENEMY_HP_COLOR, [
                    (x, C.HUD_Y + 2), (x + 5, C.HUD_Y + 2),
                    (x + 2, C.HUD_Y + 6)])
        self.hud_text = message
        self.overlay_title = ""
        self.overlay_lines = []

    # ------------------------------------------------------ falling mobs
    def draw_falling(self, level: L.LevelState, room: int) -> None:
        for ff in level.falling:
            if ff.room != room:
                continue
            img_a = self.assets.bg_image(BG.LOOSEA[0])
            img_d = self.assets.bg_image(BG.LOOSED[0])
            self.blit_ll(img_a, ff.col * 28, int(ff.y))
            self.blit_ll(img_d, ff.col * 28, int(ff.y) + 3)

    # ------------------------------------------------------------- text
    def center_text(self, lines, color=TEXT_COLOR, title=None) -> None:
        self.canvas.fill(BLACK)
        self.overlay_title = title or ""
        self.overlay_lines = list(lines)
        self.hud_text = ""

    def draw_text_overlay(self, surface: pygame.Surface) -> None:
        """Render queued text crisp at the display surface's resolution."""
        w, h = surface.get_size()
        scale = max(1, w // C.CANVAS_W)
        if self.overlay_title or self.overlay_lines:
            big = pygame.font.Font(None, 16 * scale)
            small = pygame.font.Font(None, 7 * scale)
            y = h // 4
            if self.overlay_title:
                surf = big.render(self.overlay_title, True, (255, 220, 120))
                surface.blit(surf, (w // 2 - surf.get_width() // 2, y))
                y += big.get_height() + 6 * scale
            for line in self.overlay_lines:
                surf = small.render(line, True, TEXT_COLOR)
                surface.blit(surf, (w // 2 - surf.get_width() // 2, y))
                y += small.get_height() + 2 * scale
        if self.hud_text:
            font = pygame.font.Font(None, 7 * scale)
            surf = font.render(self.hud_text, True, TEXT_COLOR)
            y = C.HUD_Y * h // C.CANVAS_H
            surface.blit(surf, (w // 2 - surf.get_width() // 2,
                                y + (h - y - surf.get_height()) // 2))
