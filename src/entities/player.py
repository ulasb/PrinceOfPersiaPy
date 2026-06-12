"""
Player (the Kid): input-driven control layer on top of the sequence
interpreter. Decides which animation sequence to start based on input,
action state and the surrounding tiles; the sequences themselves then
drive movement, exactly like CTRL.S drove SEQTABLE in the original.
"""

import random
from dataclasses import dataclass, field

from entities.char import Char
from game import constants as C
from levels import level as L


@dataclass
class Input:
    left: bool = False
    right: bool = False
    up: bool = False
    down: bool = False
    shift: bool = False
    # edge-triggered (pressed this tick)
    up_pressed: bool = False
    down_pressed: bool = False
    shift_pressed: bool = False


@dataclass
class Kid(Char):
    sword_drawn: bool = False
    hang_ticks: int = 0
    pickup: str = ""        # pending pickup at effect event ("sword"/potion)
    pickup_tile: tuple = ()
    just_landed: int = 0

    def __post_init__(self):
        self.char_id = C.CHAR_KID
        self.has_sword = False

    # ------------------------------------------------------------- spawn
    def spawn(self, level: L.LevelState) -> None:
        room, block, face = level.kid_start
        self.room = room
        self.row = block // 10
        col = block % 10
        self.x = col * C.TILE_W + 7
        self.y = C.floor_y(self.row)
        self.face = face
        self.action = C.ACT_STAND
        self.alive = True
        self.sword_drawn = False
        self.weightless = 0
        self.xvel = self.yvel = 0
        self.start_seq("stand")
        self.animate()

    # ----------------------------------------------------------- helpers
    def dir_input(self, inp: Input) -> int:
        if inp.left and not inp.right:
            return -1
        if inp.right and not inp.left:
            return 1
        return 0

    def forward_held(self, inp: Input) -> bool:
        return self.dir_input(inp) == self.face

    def backward_held(self, inp: Input) -> bool:
        return self.dir_input(inp) == -self.face

    def is_standing(self) -> bool:
        return self.frame == 15

    def is_running(self) -> bool:
        return 1 <= self.frame <= 14

    def is_crouching(self) -> bool:
        return self.frame == 109

    def is_engarde(self) -> bool:
        return self.sword_drawn and self.in_seq(
            "ready", "engarde", "advance", "retreat", "strike",
            "strikeblock", "readyblock", "blocktostrike", "strikeadv",
            "blockedstrike", "strikeret", "fastadvance", "turnengarde")

    # ----------------------------------------------------------- control
    def control(self, inp: Input, level: L.LevelState, opponent) -> None:
        if not self.alive:
            return
        # hanging is recognized by the sequence, not only the action:
        # climbdown enters the hang loop with the action still at 3
        # (the original dispatches these states by frame range too)
        if self.action in (C.ACT_HANG, C.ACT_HANG_STRAIGHT) \
                or self.in_seq("hang", "hang1", "hangstraight"):
            self._control_hang(inp, level)
        elif self.action in (C.ACT_MIDAIR, C.ACT_FREEFALL):
            self._control_midair(inp, level)
        elif self.is_engarde():
            self._control_combat(inp, level, opponent)
        elif self.is_crouching():
            self._control_crouch(inp, level)
        elif self.is_standing():
            self._control_stand(inp, level, opponent)
        elif self.is_running():
            self._control_run(inp, level)
        # other frames: let the current sequence play out

    # --- standing ---
    def _control_stand(self, inp: Input, level, opponent) -> None:
        d = self.dir_input(inp)
        # auto draw sword when an armed opponent is near
        if opponent is not None and self._should_engarde(opponent):
            self.sword_drawn = True
            self.start_seq("engarde")
            return
        if inp.shift and not d and not inp.up and not inp.down:
            if self._try_pickup(level):
                return
        if inp.up:
            if self._tile_here(level) in (L.EXIT, L.EXIT2) \
                    and level.spec(self.room, self.col, self.row) >= 20:
                self.start_seq("climbstairs")
                return
            if d == 0 and self._try_climb(level):
                return
            if d != 0:
                if d != self.face:
                    self.face = d
                self.start_seq("standjump")
                return
            self.start_seq("jumpup")
            return
        if inp.down:
            if self._try_climb_down(level):
                return
            self.start_seq("stoop")
            return
        if d != 0:
            if d != self.face:
                self.start_seq("turn")
                return
            if inp.shift:
                self._careful_step(level)
            else:
                self.start_seq("startrun")

    def _should_engarde(self, opponent) -> bool:
        if not self.has_sword or not opponent.alive:
            return False
        if opponent.room != self.room or opponent.row != self.row:
            return False
        return abs(opponent.x - self.x) < 60

    def _tile_here(self, level) -> int:
        return level.tile(self.room, self.col, self.row)

    def _tile_front(self, level) -> int:
        col = self.col + (1 if self.face > 0 else -1)
        return level.tile(self.room, col, self.row)

    def _try_pickup(self, level) -> bool:
        for col in (self.col, self.col + self.face):
            t = level.tile(self.room, col, self.row)
            if t == L.SWORD:
                self.pickup = "sword"
                self.pickup_tile = level.locate(self.room, col, self.row)
                self.start_seq("pickupsword")
                return True
            if t == L.FLASK:
                self.pickup = "flask"
                self.pickup_tile = level.locate(self.room, col, self.row)
                self.start_seq("drinkpotion")
                return True
        return False

    def _ledge_above(self, level):
        """Return grab column if there is a climbable ledge above."""
        up_here = level.tile(self.room, self.col, self.row - 1)
        for col in (self.col + self.face, self.col - self.face):
            t = level.tile(self.room, col, self.row - 1)
            if t not in L.NO_FLOOR and up_here in L.NO_FLOOR:
                # ceiling above the ledge must be clear to climb onto
                return col
        if up_here not in L.NO_FLOOR:
            return None
        return None

    def _hang_x(self, ledge_col: int, face: int) -> float:
        """Hanging x: the body dangles on the OPEN side of the grip
        edge (facing the ledge), so it never embeds in the wall mass
        under the ledge."""
        if face > 0:   # ledge to the right
            return ledge_col * C.TILE_W - 3
        return (ledge_col + 1) * C.TILE_W + 2

    def _climb_snap(self) -> None:
        """Before pulling up, fudge x onto the ledge column's edge so
        climbup's net +6 ends well onto the tile surface (CTRL.S also
        fudges CharX around the climb sequences)."""
        ledge = self.col + self.face
        if self.face > 0:
            self.x = ledge * C.TILE_W + 2
        else:
            self.x = (ledge + 1) * C.TILE_W - 3

    def _try_climb(self, level) -> bool:
        col = self._ledge_above(level)
        if col is None:
            return False
        # face the ledge and snap inside its column edge
        self.face = 1 if col > self.col else -1
        self.x = self._hang_x(col, self.face)
        self.start_seq("jumphangMed")
        self.hang_ticks = 0
        return True

    def _try_climb_down(self, level) -> bool:
        # climb down over an adjacent edge, ending hanging from this floor.
        # The climbdown sequence has no aboutface: the kid must start
        # facing AWAY from the gap (chx -5 backs him over the edge).
        if not level.is_floor(self.room, self.col, self.row):
            return False
        for gap_dir in (self.face, -self.face):
            col = self.col + gap_dir
            if not level.is_floor(self.room, col, self.row) \
                    and not level.is_barrier(self.room, col, self.row):
                # back over the edge: the sequence's chx -5 then leaves
                # the body hanging just on the gap side of the edge
                ledge = self.col
                self.face = -gap_dir
                if gap_dir > 0:
                    self.x = (ledge + 1) * C.TILE_W - 2
                else:
                    self.x = ledge * C.TILE_W + 1
                self.start_seq("climbdown")
                self.hang_ticks = 0
                return True
        return False

    def _careful_step(self, level) -> None:
        # step up to the edge of the current floor or barrier; at the
        # edge itself, tap a foot over it (testfoot) without moving
        x = int(self.x)
        dist = 14
        for ahead in range(0, 3):
            col = self.col + ahead * self.face
            blocked = level.is_barrier(self.room, col, self.row)
            no_floor = not level.is_floor(self.room, col, self.row)
            if blocked or no_floor:
                if self.face > 0:
                    edge = col * C.TILE_W
                    dist = edge - 1 - x
                else:
                    edge = (col + 1) * C.TILE_W
                    dist = x - edge
                break
        if dist < 1:
            self.start_seq("testfoot")
        elif dist >= 14:
            self.start_seq("fullstep")
        else:
            self.start_seq(f"step{dist}")

    # --- running ---
    def _control_run(self, inp: Input, level) -> None:
        d = self.dir_input(inp)
        if inp.up:
            self.start_seq("runjump")
            return
        if inp.down:
            self.start_seq("rdiveroll")
            return
        if d == -self.face:
            self.start_seq("runturn")
            return
        if d == 0:
            self.start_seq("runstop")

    # --- crouching ---
    def _control_crouch(self, inp: Input, level) -> None:
        if not inp.down:
            self.start_seq("standup")

    # --- midair ---
    def _control_midair(self, inp: Input, level) -> None:
        if not inp.shift:
            return
        from entities.char import HANG_SEQS
        if self.in_seq(*HANG_SEQS):
            return  # a grab is already in progress
        # grab a ledge while falling past it
        row = C.row_from_y(self.y)
        for col in (self.col + self.face, self.col - self.face):
            t = level.tile(self.room, col, row - 1)
            if t in L.NO_FLOOR:
                continue
            ledge_y = C.floor_y(row)
            if abs(self.y - ledge_y) <= 15 and self.yvel >= 0:
                self.face = 1 if col > self.col else -1
                self.x = self._hang_x(col, self.face)
                self.row = row
                self.y = ledge_y
                self.yvel = 0
                self.xvel = 0
                self.start_seq("fallhang")
                self.hang_ticks = 0
                return

    # --- hanging ---
    def _control_hang(self, inp: Input, level) -> None:
        if not self.in_seq("hang", "hang1", "hangstraight"):
            return  # climbup/climbfail/hangdrop already in progress
        self.hang_ticks += 1
        # the body hangs on the open side; the ledge is one column
        # ahead in the facing direction
        ledge_col = self.col + self.face
        if inp.up or self.forward_held(inp):
            blocked = level.is_barrier(self.room, ledge_col, self.row - 1)
            if not blocked:
                self._climb_snap()
                self.start_seq("climbup")
            else:
                self.start_seq("climbfail")
            return
        if inp.down_pressed or (not inp.shift and self.hang_ticks > 2):
            # drop: land right below if there's floor, else free fall
            if level.is_floor(self.room, self.col, self.row):
                self.start_seq("hangdrop")
            else:
                self.start_seq("hangfall")
            return
        # the swing sequence ends in hangdrop by itself (grab-and-release
        # behavior); while shift is held, settle into the still hang so
        # the kid holds on indefinitely like the original
        if inp.shift and self.hang_ticks >= 6 \
                and self.in_seq("hang", "hang1"):
            self.start_seq("hangstraight")

    # --- combat ---
    def _control_combat(self, inp: Input, level, opponent) -> None:
        if opponent is None or not opponent.alive:
            if self.in_seq("ready"):
                self.sword_drawn = False
                self.start_seq("resheathe")
            return
        # always face the opponent
        want_face = 1 if opponent.x > self.x else -1
        if not self.in_seq("ready"):
            return  # mid-move
        if want_face != self.face:
            self.face = want_face
        if inp.down_pressed:
            self.sword_drawn = False
            self.start_seq("fastsheathe")
            return
        if inp.shift_pressed:
            self.start_seq("strike")
            return
        if inp.up:
            self.start_seq("readyblock")
            return
        d = self.dir_input(inp)
        if d == self.face:
            if abs(opponent.x - self.x) > 15:
                self.start_seq("advance")
            return
        if d == -self.face:
            self.start_seq("retreat")
            return
