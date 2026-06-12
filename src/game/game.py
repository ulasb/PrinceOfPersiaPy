"""
Game orchestrator: level lifecycle, the per-tick simulation (kid, guards,
tiles, combat, hazards), camera/room tracking, HUD and game states.
"""

import json
import time
from pathlib import Path
from typing import List, Optional

from entities.char import Char
from entities.guard import GuardChar
from entities.player import Input, Kid
from game import constants as C
from game.sound import Sounds
from graphics.assets import Assets
from graphics.render import Renderer
from levels import level as L

SAVE_PATH = Path("saved_games") / "quicksave.json"

STATE_TITLE = "title"
STATE_PLAYING = "playing"
STATE_DEAD = "dead"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"


class Game:
    def __init__(self, assets: Assets, renderer: Renderer, sounds: Sounds):
        self.assets = assets
        self.renderer = renderer
        self.sounds = sounds
        self.state = STATE_TITLE
        self.level_num = C.FIRST_LEVEL
        self.level: Optional[L.LevelState] = None
        self.kid = Kid()
        self.guards: List[GuardChar] = []
        self.ticks_left = C.TIME_LIMIT_TICKS
        self.message = ""
        self.message_ticks = 0
        self.dead_ticks = 0
        self.has_sword = False
        self.max_hp = C.INITIAL_HP
        self.visible_room = 1

    # ------------------------------------------------------------ levels
    def start_level(self, number: int) -> None:
        self.level_num = number
        self.level = L.LevelState.load(number)
        self.assets.configure(
            guard_table=C.GUARD_TABLE.get(number, "GD"),
            palace=number in C.PALACE_LEVELS)
        self.kid = Kid()
        self.kid.max_hp = self.max_hp
        self.kid.hp = self.max_hp
        self.kid.has_sword = self.has_sword
        self.kid.spawn(self.level)
        self.guards = [GuardChar.from_level(g, number)
                       for g in self.level.guards]
        self.visible_room = self.kid.room
        self.state = STATE_PLAYING
        self.show_message(f"LEVEL {number}" if number < 14 else "THE TOWER")

    def next_level(self) -> None:
        self.has_sword = self.kid.has_sword
        self.max_hp = self.kid.max_hp
        self.sounds.play("level_done")
        if self.level_num >= C.LAST_LEVEL:
            self.state = STATE_VICTORY
            return
        self.start_level(self.level_num + 1)

    def restart_level(self) -> None:
        self.start_level(self.level_num)

    def show_message(self, text: str, ticks: int = 30) -> None:
        self.message = text
        self.message_ticks = ticks

    # ------------------------------------------------------------- save
    def quicksave(self) -> None:
        SAVE_PATH.parent.mkdir(exist_ok=True)
        SAVE_PATH.write_text(json.dumps({
            "level": self.level_num,
            "ticks_left": self.ticks_left,
            "max_hp": self.kid.max_hp,
            "has_sword": self.kid.has_sword,
        }))
        self.show_message("GAME SAVED")

    def quickload(self) -> bool:
        if not SAVE_PATH.exists():
            self.show_message("NO SAVED GAME")
            return False
        data = json.loads(SAVE_PATH.read_text())
        self.max_hp = data["max_hp"]
        self.has_sword = data["has_sword"]
        self.ticks_left = data["ticks_left"]
        self.start_level(data["level"])
        return True

    # ------------------------------------------------------------ combat
    def opponent(self) -> Optional[GuardChar]:
        best = None
        for g in self.guards:
            if not g.alive or g.npc or g.room != self.kid.room:
                continue
            if best is None or abs(g.x - self.kid.x) < abs(best.x -
                                                           self.kid.x):
                best = g
        return best

    def _resolve_strikes(self) -> None:
        """Check strike connections at full sword extension frames."""
        opp = self.opponent()
        if opp is None:
            return
        kid = self.kid
        dist = abs(kid.x - opp.x)
        if dist > 26 or kid.row != opp.row:
            return
        # kid strikes (full extension frame 154 / 167)
        if kid.frame in (154, 167) and opp.alive:
            if opp.in_seq("readyblock", "blockedstrike", "strikeblock"):
                self.sounds.play("sword_clash")
                kid.start_seq("blockedstrike")
            else:
                self._hit(opp)
        # guard strikes
        if opp.frame in (154, 167) and kid.alive:
            if kid.in_seq("readyblock", "blockedstrike", "strikeblock"):
                self.sounds.play("sword_clash")
                opp.start_seq("blockedstrike")
            else:
                self._hit(kid)

    def _hit(self, char: Char) -> None:
        if getattr(char, "hurt_cooldown", 0) > 0:
            return
        char.hp -= 1
        char.hurt_cooldown = 8
        if char.hp <= 0:
            char.alive = False
            char.start_seq("dropdead")
            if char is self.kid:
                self.sounds.play("death")
                self._kid_died()
            else:
                self.sounds.play("guard_death")
        else:
            self.sounds.play("sword_hit")
            char.start_seq("stabbed")

    # ------------------------------------------------------------ deaths
    def _kid_died(self) -> None:
        if self.state == STATE_PLAYING:
            self.state = STATE_DEAD
            self.dead_ticks = 0

    def kill_kid(self, seq: str, sound: str = "death") -> None:
        if not self.kid.alive:
            return
        self.kid.hp = 0
        self.kid.alive = False
        self.kid.start_seq(seq)
        self.sounds.play(sound)
        self._kid_died()

    # -------------------------------------------------------------- tick
    def tick(self, inp: Input) -> None:
        if self.state == STATE_TITLE:
            return
        if self.message_ticks > 0:
            self.message_ticks -= 1
            if self.message_ticks == 0:
                self.message = ""
        if self.state in (STATE_GAME_OVER, STATE_VICTORY):
            return

        self.ticks_left -= 1
        if self.ticks_left <= 0:
            self.state = STATE_GAME_OVER
            return
        minute = 60 * C.TICKS_PER_SECOND
        minutes_left = self.ticks_left // minute
        if self.ticks_left % minute == 0 and minutes_left > 0 \
                and (minutes_left % 10 == 0 or minutes_left <= 5):
            self.show_message(f"{minutes_left} MINUTES LEFT", ticks=42)
        elif self.ticks_left == 30 * C.TICKS_PER_SECOND:
            self.show_message("30 SECONDS LEFT", ticks=42)

        level = self.level
        kid = self.kid

        if self.state == STATE_DEAD:
            self.dead_ticks += 1
            if self.dead_ticks == 30:
                self.show_message("PRESS ENTER TO TRY AGAIN", ticks=240)

        # --- kid ---
        if kid.hurt_cooldown:
            kid.hurt_cooldown -= 1
        if kid.weightless:
            kid.weightless -= 1
        opp = self.opponent()
        kid.control(inp, level, opp)
        prev_row = kid.row
        prev_y = kid.y
        kid.animate()
        kid.apply_gravity()
        kid.add_fall()
        self._post_move(kid, prev_y)
        kid.normalize(level)
        if kid.row > 2 and kid.alive:
            # fell out of the world (no room below)
            self.kill_kid("hardland", "splat")
        self._kid_events()
        self._check_hazards(kid)
        self._check_plates(kid)
        if kid.room != 0:
            self.visible_room = kid.room

        # --- guards ---
        for g in self.guards:
            if g.room != kid.room and not g.alive:
                continue
            if g.hurt_cooldown:
                g.hurt_cooldown -= 1
            g.control(kid, level)
            gy = g.y
            g.animate()
            g.apply_gravity()
            g.add_fall()
            self._post_move(g, gy)
            g.normalize(level)
            if g.row > 2 and g.alive:
                g.alive = False
                g.hp = 0
            self._char_seq_events(g)
            if g.alive:
                self._check_hazards(g)
                self._check_plates(g)

        self._resolve_strikes()
        self._char_separation()

        # --- tiles ---
        level.tick()
        self._crush_check()
        for event in level.events:
            self.sounds.play(event)
        level.events.clear()

        # princess level: reaching her is victory
        if self.level_num == 14 and kid.alive:
            for g in self.guards:
                if g.npc and g.room == kid.room and abs(g.x - kid.x) < 24:
                    self.state = STATE_VICTORY

    # --------------------------------------------------------- post-move
    def _post_move(self, char: Char, prev_y: int) -> None:
        """Floor checks, landings and barrier collisions after movement."""
        from entities.char import HANG_SEQS
        level = self.level
        if char.char_id == C.CHAR_KID and char.in_seq(*HANG_SEQS):
            return
        # barrier collision: can't walk into walls/closed gates
        if char.action in (C.ACT_STAND, C.ACT_MOVE, C.ACT_BUMPED):
            self._check_barrier(char)
        # landing during fall
        if char.action in (C.ACT_MIDAIR, C.ACT_FREEFALL):
            falling_frames = 102 <= char.frame <= 106
            if char.action == C.ACT_FREEFALL or falling_frames:
                self._check_landing(char, prev_y)
        # walking off an edge: the original only checks the floor on
        # frames bearing check marks (Fcheck bits 6-7); unmarked frames
        # are airborne (jump arcs sail over gaps)
        elif char.action in (C.ACT_STAND, C.ACT_MOVE, C.ACT_TURN):
            if char.action == C.ACT_STAND and char.frame == 15:
                # re-align feet with the floor after landing sequences
                char.y = C.floor_y(char.row)
            info = char.frame_info()
            if not (info.check & 0x40):
                return  # airborne frame (no check mark)
            # jump arcs are carried by the sequence; only the landing
            # frames touch the ground again
            if char.in_seq("runjump") and 36 <= char.frame <= 43:
                return
            if char.in_seq("standjump") and 18 <= char.frame <= 25:
                return
            # testfoot leans over the edge and comes back; net zero move
            if char.in_seq("testfoot"):
                return
            # fall when both the body column and the trailing foot have no
            # floor; standing with the body over a gap is allowed only for
            # a few pixels of toe overhang past the edge
            body_col = int(char.x) // C.TILE_W
            foot_col = int(char.x - char.face * (info.foot_dx // 2)) \
                // C.TILE_W
            supported = level.is_floor(char.room, body_col, char.row)
            if not supported and foot_col != body_col \
                    and level.is_floor(char.room, foot_col, char.row):
                edge = body_col * C.TILE_W if char.face > 0 \
                    else (body_col + 1) * C.TILE_W
                supported = abs(char.x - edge) <= 5
            if char.room and not supported:
                char.yvel = 0
                char.xvel = 0
                char.start_seq("stepfall")
                char.animate()  # enter falling immediately

    def _check_barrier(self, char: Char) -> None:
        level = self.level
        col = char.col
        t = level.tile(char.room, col, char.row)
        if level.is_barrier(char.room, col, char.row):
            # push back out of the barrier toward where we came from
            if char.face > 0:
                char.x = col * C.TILE_W - 1
            else:
                char.x = (col + 1) * C.TILE_W + 1
            if char.action == C.ACT_MOVE and 1 <= char.frame <= 14:
                char.start_seq("hardbump" if char.char_id == 0 else "bump")
            elif char.frame != 15:
                char.start_seq("bump")

    def _check_landing(self, char: Char, prev_y: int) -> None:
        level = self.level
        if char.y <= prev_y:
            return
        row = C.row_from_y(prev_y)
        while row <= C.row_from_y(char.y):
            fy = C.floor_y(row)
            r_room, r_col, r_row = level.locate(char.room, char.col, row)
            if prev_y < fy <= char.y and r_room \
                    and level.is_floor(r_room, r_col, r_row):
                char.y = fy
                char.row = row
                self._land(char, r_room, r_col, r_row)
                return
            row += 1
        # fell below the screen: normalize() moves to the room below
        if C.row_from_y(char.y) > 2:
            char.row = C.row_from_y(char.y)

    def _land(self, char: Char, room: int, col: int, row: int) -> None:
        level = self.level
        vel = char.yvel
        char.xvel = 0
        char.yvel = 0
        if level.tile(room, col, row) == L.SPIKES \
                and level.spikes_deadly(room, col, row):
            char.action = C.ACT_BUMPED
            char.start_seq("impale")
            if char is self.kid:
                self.kill_kid("impale", "splat")
            else:
                char.alive = False
                char.hp = 0
            return
        char.action = C.ACT_BUMPED
        if level.tile(room, col, row) == L.LOOSE:
            level.shake_loose(room, col, row)
        if char.weightless or vel < C.OOF_VELOCITY:
            char.start_seq("softland")
            self.sounds.play("land")
        elif vel < C.DEATH_VELOCITY and char.char_id == C.CHAR_KID:
            char.hp -= 1
            self.sounds.play("oof")
            if char.hp <= 0:
                if char is self.kid:
                    self.kill_kid("hardland", "splat")
                else:
                    char.alive = False
                    char.start_seq("hardland")
            else:
                char.start_seq("medland")
        else:
            if char is self.kid:
                self.kill_kid("hardland", "splat")
            else:
                char.alive = False
                char.hp = 0
                char.start_seq("hardland")

    # ------------------------------------------------------ tile hazards
    def _check_hazards(self, char: Char) -> None:
        level = self.level
        if char.room == 0 or not char.alive:
            return
        t = level.tile(char.room, char.col, char.row)
        # spikes trigger when approached, or seen below while falling
        if char.action in (C.ACT_MIDAIR, C.ACT_FREEFALL):
            row = C.row_from_y(char.y)
            for r in (row, row + 1):
                if level.tile(char.room, char.col, r) == L.SPIKES:
                    level.trigger_spikes(char.room, char.col, r)
        else:
            for col in (char.col, char.col + char.face):
                if level.tile(char.room, col, char.row) == L.SPIKES:
                    level.trigger_spikes(char.room, col, char.row)
        # running into extended spikes is fatal
        if t == L.SPIKES and level.spikes_deadly(char.room, char.col,
                                                 char.row) \
                and char.action == C.ACT_MOVE and 1 <= char.frame <= 14:
            if char is self.kid:
                self.kill_kid("impale", "splat")
            else:
                char.alive = False
                char.start_seq("impale")
            return
        # slicers
        if t == L.SLICER and level.slicer_deadly(char.room, char.col,
                                                 char.row):
            in_blade = 2 < int(char.x) % C.TILE_W < 12
            if in_blade and char.action in (C.ACT_MOVE, C.ACT_MIDAIR,
                                            C.ACT_FREEFALL):
                self.sounds.play("slicer")
                if char is self.kid:
                    self.kill_kid("halve", "splat")
                else:
                    char.alive = False
                    char.start_seq("halve")

    def _check_plates(self, char: Char) -> None:
        level = self.level
        if char.room == 0:
            return
        if not (char.frame_info().check & 0x40):
            return  # airborne frame: feet aren't on the ground
        if char.action in (C.ACT_STAND, C.ACT_MOVE, C.ACT_BUMPED):
            t = level.tile(char.room, char.col, char.row)
            if t in (L.PRESSPLATE, L.UPRESSPLATE, L.DPRESSPLATE):
                level.press_plate(char.room, char.col, char.row,
                                  jam=not char.alive)
            elif t == L.LOOSE and char.action == C.ACT_MOVE:
                level.shake_loose(char.room, char.col, char.row)

    def _crush_check(self) -> None:
        for ff in self.level.falling:
            if ff.crashed != 1:
                continue
            for char in [self.kid] + self.guards:
                if char.alive and char.room == ff.room \
                        and char.col == ff.col \
                        and abs(char.y - ff.y) < 20:
                    if char is self.kid:
                        self.kill_kid("crush", "splat")
                    else:
                        char.alive = False
                        char.hp = 0
                        char.start_seq("crush")

    def _char_separation(self) -> None:
        """The kid can't walk through a living guard."""
        kid = self.kid
        for g in self.guards:
            if not g.alive or g.npc or g.room != kid.room \
                    or g.row != kid.row:
                continue
            dist = kid.x - g.x
            if abs(dist) < 10 and kid.action in (C.ACT_STAND, C.ACT_MOVE):
                kid.x = g.x + (10 if dist >= 0 else -10)

    # ------------------------------------------------------- seq events
    def _kid_events(self) -> None:
        kid = self.kid
        for event in kid.events:
            if event == "nextlevel":
                self.next_level()
            elif event == "effect":
                self._apply_pickup()
            elif event in ("tap0", "tap1"):
                self.sounds.play("tap")
            elif event == "jaru":
                self._jar_floors(kid.room, kid.row - 1)
            elif event == "jard":
                self._jar_floors(kid.room, kid.row)
            elif event == "die" and kid.hp > 0:
                kid.hp = 0
                self._kid_died()
        kid.events.clear()

    def _char_seq_events(self, char: Char) -> None:
        for event in char.events:
            if event in ("tap0", "tap1"):
                self.sounds.play("tap")
            elif event == "jard":
                self._jar_floors(char.room, char.row)
        char.events.clear()

    def _jar_floors(self, room: int, row: int) -> None:
        if room == 0 or self.level_num == 13:  # SHAKEM skips level 13
            return
        for col in range(10):
            if self.level.tile(room, col, row) == L.LOOSE:
                self.level.shake_loose(room, col, row)

    def _apply_pickup(self) -> None:
        kid = self.kid
        if kid.pickup == "sword":
            kid.has_sword = True
            self.has_sword = True
            self.sounds.play("pickup")
            self.level.set_tile(*kid.pickup_tile, L.FLOOR, 0)
            self.show_message("YOU GOT THE SWORD")
        elif kid.pickup == "flask":
            spec = self.level.spec(*kid.pickup_tile)
            ptype = spec >> 5
            self.sounds.play("potion")
            if ptype <= 1:
                kid.hp = min(kid.hp + 1, kid.max_hp)
            elif ptype == 2:
                kid.max_hp += 1
                kid.hp = kid.max_hp
                self.max_hp = kid.max_hp
            elif ptype in (3, 4):
                kid.weightless = 12 * C.TICKS_PER_SECOND
            elif ptype == 5:
                kid.hp -= 1
                if kid.hp <= 0:
                    self.kill_kid("dropdead")
            self.level.set_tile(*kid.pickup_tile, L.FLOOR, 0)
        kid.pickup = ""

    # -------------------------------------------------------- debug dump
    def debug_info(self) -> dict:
        """Everything needed to diagnose 'this frame looks wrong'."""
        from data import seqdata

        def seq_label(offset: int) -> str:
            best, best_addr = "?", -1
            for name, addr in seqdata.LABELS.items():
                if best_addr < addr <= offset:
                    best, best_addr = name, addr
            return f"{best}+{offset - best_addr}"

        def char_info(c) -> dict:
            return {
                "room": c.room, "x": c.x, "y": c.y, "row": c.row,
                "col": c.col, "face": c.face, "action": c.action,
                "frame": c.frame, "seq": seq_label(c.seq), "hp": c.hp,
                "alive": c.alive,
            }

        level = self.level
        room = self.visible_room
        info = {
            "state": self.state,
            "level": self.level_num,
            "ticks_left": self.ticks_left,
            "visible_room": room,
            "kid": char_info(self.kid),
            "kid_extra": {
                "has_sword": self.kid.has_sword,
                "sword_drawn": self.kid.sword_drawn,
                "weightless": self.kid.weightless,
            },
            "guards": [char_info(g) | {"npc": g.npc, "skill": g.skill,
                                       "engaged": g.engaged}
                       for g in self.guards if g.room == room],
        }
        if level and room:
            info["room_links"] = level.links.get(room)
            info["room_tiles"] = [
                [f"{level.types[room][r][c] & 0x1F}"
                 f":{level.specs[room][r][c]}" for c in range(10)]
                for r in range(3)]
            info["active"] = {
                "gates": {str(k): v for k, v in level.gates.items()},
                "gate_timers": {str(k): v
                                for k, v in level.gate_timers.items()},
                "plates": {str(k): v for k, v in level.plates.items()},
                "spikes": {str(k): v for k, v in level.spikes.items()},
                "loose": {str(k): v for k, v in level.loose.items()},
                "falling": [vars(f) for f in level.falling],
            }
        return info

    # ------------------------------------------------------------ render
    def render(self) -> None:
        r = self.renderer
        if self.state == STATE_TITLE:
            r.center_text([
                "A port of the Apple II classic by Jordan Mechner",
                "",
                "Arrows move - Shift careful step / action",
                "Up jump or climb - Down crouch or climb down",
                "In combat: Shift strike, Up parry, Down sheathe",
                "",
                "Press ENTER to begin",
            ], title="PRINCE OF PERSIA")
            return
        if self.state == STATE_VICTORY:
            r.center_text([
                "The princess is saved.",
                "Peace returns to Persia.",
                "",
                "Press ENTER for the title screen",
            ], title="VICTORY")
            return
        if self.state == STATE_GAME_OVER:
            r.center_text([
                "Time has run out.",
                "",
                "Press ENTER to try the level again",
            ], title="GAME OVER")
            return

        room = self.visible_room
        r.draw_room(self.level, room)
        r.draw_falling(self.level, room)
        for g in self.guards:
            if g.room == room:
                r.draw_char(g)
        if self.kid.room == room:
            r.draw_char(self.kid)
        r.draw_foreground(self.level, room)
        minutes = max(0, self.ticks_left // (60 * C.TICKS_PER_SECOND))
        status = self.message or \
            f"LEVEL {self.level_num}      {minutes} MIN LEFT"
        r.draw_hud(self.kid, self.opponent(), self.level_num, status)
