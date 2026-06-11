"""
Level runtime: tiles, room links, and dynamic tile machinery.

Loads the JSON exported from the original binary blueprints
(tools/export_levels.py) and keeps the mutable per-tile state the
original kept in BLUESPEC: gate positions, pressplate timers, spike and
slicer animation states, loose-floor wiggling, and the button->gate link
table (LINKLOC/LINKMAP).
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from game import constants as C

LEVELS_DIR = Path(__file__).resolve().parents[2] / "assets" / "levels"

# tile ids (BGDATA.S)
SPACE = 0
FLOOR = 1
SPIKES = 2
POSTS = 3
GATE = 4
DPRESSPLATE = 5
PRESSPLATE = 6
PANELWIF = 7
PILLARBOTTOM = 8
PILLARTOP = 9
FLASK = 10
LOOSE = 11
PANELWOF = 12
MIRROR = 13
RUBBLE = 14
UPRESSPLATE = 15
EXIT = 16
EXIT2 = 17
SLICER = 18
TORCH = 19
BLOCK = 20
BONES = 21
SWORD = 22
WINDOW = 23
WINDOW2 = 24
ARCHBOT = 25
ARCHTOP1 = 26

# CMPSPACE: ids you can NOT stand on
NO_FLOOR = {SPACE, PILLARTOP, PANELWOF, BLOCK, 26, 27, 28, 29}
# CMPBARR: ids that block horizontal movement
BARRIERS = {PANELWIF, PANELWOF, GATE, MIRROR, BLOCK}


@dataclass
class Guard:
    room: int
    block: int
    face: int
    x: int
    seq: int
    prog: int


@dataclass
class FallingFloor:
    room: int
    col: int
    y: float          # bottom of the floor piece, in screen pixels
    vel: float = 0.0
    crashed: int = 0  # ticks since crash (for debris removal)


@dataclass
class LevelState:
    number: int
    types: Dict[int, List[List[int]]] = field(default_factory=dict)
    specs: Dict[int, List[List[int]]] = field(default_factory=dict)
    links: Dict[int, Dict[str, int]] = field(default_factory=dict)
    linkloc: List[int] = field(default_factory=list)
    linkmap: List[int] = field(default_factory=list)
    kid_start: Tuple[int, int, int] = (1, 0, -1)   # room, block, face
    guards: List[Guard] = field(default_factory=list)

    # dynamic machinery
    gates: Dict[Tuple[int, int, int], list] = field(default_factory=dict)
    gate_timers: Dict[Tuple[int, int, int], int] = field(default_factory=dict)
    plates: Dict[Tuple[int, int, int], int] = field(default_factory=dict)
    spikes: Dict[Tuple[int, int, int], int] = field(default_factory=dict)
    loose: Dict[Tuple[int, int, int], int] = field(default_factory=dict)
    falling: List[FallingFloor] = field(default_factory=list)
    slicer_phase: int = 0
    events: List[str] = field(default_factory=list)  # sound triggers

    # ------------------------------------------------------------- loading
    @classmethod
    def load(cls, number: int) -> "LevelState":
        data = json.loads(
            (LEVELS_DIR / f"level_{number:02d}.json").read_text())
        st = cls(number=number)
        for room_s, room in data["rooms"].items():
            room_n = int(room_s)
            st.types[room_n] = [row[:] for row in room["tiles"]]
            st.specs[room_n] = [row[:] for row in room["specs"]]
            st.links[room_n] = room["links"]
        st.linkloc = data["linkloc"]
        st.linkmap = data["linkmap"]
        kid = data["info"]["kid"]
        st.kid_start = (kid["room"], kid["block"], kid["face"])
        st.guards = [Guard(**g) for g in data["info"]["guards"]]
        return st

    # ------------------------------------------------------------ queries
    def link(self, room: int, direction: str) -> int:
        if room == 0:
            return 0
        return self.links[room][direction]

    def locate(self, room: int, col: int, row: int
               ) -> Tuple[int, int, int]:
        """Resolve out-of-range col/row to the neighboring room."""
        while col < 0 and room:
            room = self.links[room]["left"]
            col += C.ROOM_W
        while col >= C.ROOM_W and room:
            room = self.links[room]["right"]
            col -= C.ROOM_W
        while row < 0 and room:
            room = self.links[room]["up"]
            row += C.ROOM_H
        while row >= C.ROOM_H and room:
            room = self.links[room]["down"]
            row -= C.ROOM_H
        return room, col, row

    def tile(self, room: int, col: int, row: int) -> int:
        room, col, row = self.locate(room, col, row)
        if room == 0 or not (0 <= col < 10 and 0 <= row < 3):
            return BLOCK if room == 0 else SPACE
        return self.types[room][row][col] & 0x1F

    def spec(self, room: int, col: int, row: int) -> int:
        room, col, row = self.locate(room, col, row)
        if room == 0 or not (0 <= col < 10 and 0 <= row < 3):
            return 0
        return self.specs[room][row][col]

    def set_tile(self, room: int, col: int, row: int,
                 tile: int, spec: int = 0) -> None:
        room, col, row = self.locate(room, col, row)
        if room == 0:
            return
        self.types[room][row][col] = tile
        self.specs[room][row][col] = spec

    def is_floor(self, room: int, col: int, row: int) -> bool:
        return self.tile(room, col, row) not in NO_FLOOR

    def is_barrier(self, room: int, col: int, row: int) -> bool:
        """Blocks horizontal movement (closed gates included)."""
        t = self.tile(room, col, row)
        if t == GATE:
            return self.gate_pos(room, col, row) < C.GATE_PASSABLE
        if t in (EXIT, EXIT2):
            return False
        return t in BARRIERS

    # -------------------------------------------------------------- gates
    # self.gates[key] = [position, mode]; mode: 1 rising, 2 dropping fast,
    # 3 closing slowly. self.gate_timers[key] = open-state countdown.
    def gate_pos(self, room: int, col: int, row: int) -> int:
        """Gate opening 0 (closed) .. GATE_MAX (open)."""
        key = self.locate(room, col, row)
        if key in self.gates:
            return min(self.gates[key][0], C.GATE_MAX)
        s = self.spec(*key)
        return C.GATE_MAX if s >= C.GATE_MAX else s

    # ----------------------------------------------------------- triggers
    def press_plate(self, room: int, col: int, row: int,
                    jam: bool = False) -> None:
        """A character stepped on (or a body landed on) a pressplate."""
        key = self.locate(room, col, row)
        room, col, row = key
        t = self.tile(room, col, row)
        if t not in (PRESSPLATE, UPRESSPLATE, DPRESSPLATE):
            return
        plate_type = self.spec_plate_type(key, t)
        if key not in self.plates:
            self.events.append("plate")
        self.plates[key] = C.PP_TIMER
        link_index = self.spec(room, col, row)
        self._trigger(link_index, plate_type, jam)

    def spec_plate_type(self, key, tile: int) -> int:
        # dpressplate keeps behaving like its original type; the original
        # distinguishes via pptype from BLUETYPE which we preserve in types
        return tile if tile != DPRESSPLATE else PRESSPLATE

    def _trigger(self, link_index: int, plate_type: int, jam: bool) -> None:
        i = link_index
        for _ in range(32):
            if i >= 256 or self.linkloc[i] == 0xFF:
                return
            loc = self.linkloc[i] & 0x1F
            screen = (((self.linkmap[i] & 0xE0) >> 3)
                      | ((self.linkloc[i] & 0x60) >> 5))
            last = self.linkloc[i] & 0x80
            col, row = loc % 10, loc // 10
            t = self.tile(screen, col, row)
            if t == GATE:
                self._trigger_gate(screen, col, row, plate_type, jam)
            elif t in (EXIT, EXIT2):
                if self.spec(screen, col, row) == 0:
                    self.set_tile(screen, col, row, t, 1)
                    # the door of an exit pair lives on the EXIT2 tile;
                    # open both halves so either responds
                    other = self.locate(screen, col + 1, row)
                    if self.tile(*other) in (EXIT, EXIT2):
                        self.set_tile(*other, self.tile(*other), 1)
                    self.events.append("exit_open")
            if last:
                return
            i += 1

    def _trigger_gate(self, room: int, col: int, row: int,
                      plate_type: int, jam: bool) -> None:
        key = self.locate(room, col, row)
        if self.spec(*key) == C.GATE_JAMMED:
            return
        if jam:
            self.set_tile(*key, GATE, C.GATE_JAMMED)
            self.gates.pop(key, None)
            self.gate_timers.pop(key, None)
            return
        if plate_type == UPRESSPLATE:
            pos = self.gate_pos(*key)
            if pos >= C.GATE_MAX:
                self.gate_timers[key] = C.GATE_TIMER - C.GATE_MAX
                return
            self.events.append("gate_move")
            self.gates[key] = [pos, 1]
        else:
            pos = self.gate_pos(*key)
            if pos > 0:
                self.events.append("gate_drop")
                self.gates[key] = [pos, 2]
                self.gate_timers.pop(key, None)

    # --------------------------------------------------------------- tick
    def tick(self) -> None:
        self.slicer_phase = (self.slicer_phase + 1) % C.SLICE_TIMER
        self._tick_gates()
        self._tick_plates()
        self._tick_spikes()
        self._tick_loose()
        self._tick_exits()

    def _tick_exits(self) -> None:
        # exit doors slide open gradually once triggered (spec 1 -> 48)
        for room, rows in self.types.items():
            for row in range(3):
                for col in range(10):
                    if rows[row][col] & 0x1F in (EXIT, EXIT2):
                        s = self.specs[room][row][col]
                        if 0 < s < 48:
                            self.specs[room][row][col] = min(48, s + 4)

    def _tick_gates(self) -> None:
        for key, timer in list(self.gate_timers.items()):
            timer -= 1
            if timer <= 0:
                del self.gate_timers[key]
                self.gates[key] = [C.GATE_MAX, 3]
                self.events.append("gate_move")
            else:
                self.gate_timers[key] = timer
        for key, (pos, mode) in list(self.gates.items()):
            if mode == 1:                       # rising
                pos += C.GATE_RISE
                if pos >= C.GATE_MAX:
                    self.set_tile(*key, GATE, C.GATE_MAX)
                    self.gate_timers[key] = C.GATE_TIMER - C.GATE_MAX
                    del self.gates[key]
                    continue
            elif mode == 2:                     # dropping fast
                pos -= C.GATE_DROP
            else:                               # closing slowly
                pos -= C.GATE_CLOSE
            if pos <= 0:
                self.set_tile(*key, GATE, 0)
                self.events.append("gate_slam")
                del self.gates[key]
            else:
                self.gates[key] = [pos, mode]
                self.set_tile(*key, GATE, pos)

    def _tick_plates(self) -> None:
        for key in list(self.plates):
            room, col, row = key
            t = self.tile(room, col, row)
            if t == PRESSPLATE:
                self.types[room][row][col] = DPRESSPLATE
            self.plates[key] -= 1
            if self.plates[key] <= 0:
                del self.plates[key]
                if self.tile(room, col, row) == DPRESSPLATE:
                    self.types[room][row][col] = PRESSPLATE

    # spikes: state 0 = retracted, 1-4 extending, 5 = extended,
    # 6-8 retracting, back to 0
    def trigger_spikes(self, room: int, col: int, row: int) -> None:
        key = self.locate(room, col, row)
        if self.tile(*key) != SPIKES:
            return
        if key not in self.spikes:
            self.events.append("spikes")
            self.spikes[key] = -C.SPIKE_TIMER  # negative = holding extended

    def spike_state(self, room: int, col: int, row: int) -> int:
        key = self.locate(room, col, row)
        v = self.spikes.get(key)
        if v is None:
            return 0
        return 5 if v < 0 else v

    def spikes_deadly(self, room: int, col: int, row: int) -> bool:
        return 1 <= self.spike_state(room, col, row) <= 5

    def _tick_spikes(self) -> None:
        for key in list(self.spikes):
            v = self.spikes[key]
            if v < 0:
                v += 1
                self.spikes[key] = v if v < 0 else 6
            else:
                v += 1
                if v >= C.SPIKE_RET:
                    del self.spikes[key]
                else:
                    self.spikes[key] = v

    # slicer: shared cycle; blades chop once per SLICE_TIMER ticks
    def slicer_frame(self, room: int, col: int, row: int) -> int:
        from graphics.bgdata import SLICERSEQ
        offset = self.spec(room, col, row) & 0x1F
        idx = (self.slicer_phase + offset) % C.SLICE_TIMER
        if idx < len(SLICERSEQ):
            return SLICERSEQ[idx]
        return SLICERSEQ[-1]

    def slicer_deadly(self, room: int, col: int, row: int) -> bool:
        from graphics.bgdata import SLICERSEQ
        offset = self.spec(room, col, row) & 0x1F
        idx = (self.slicer_phase + offset) % C.SLICE_TIMER
        return idx in (1, 2, 3)  # blades closing/closed

    # loose floors
    def shake_loose(self, room: int, col: int, row: int) -> None:
        key = self.locate(room, col, row)
        if self.tile(*key) != LOOSE:
            return
        if key not in self.loose:
            self.loose[key] = 0
            self.events.append("loose")

    def loose_state(self, room: int, col: int, row: int) -> int:
        return self.loose.get(self.locate(room, col, row), 0)

    def _tick_loose(self) -> None:
        for key in list(self.loose):
            self.loose[key] += 1
            if self.loose[key] >= C.LOOSE_DETACH:
                del self.loose[key]
                room, col, row = key
                self.set_tile(room, col, row, SPACE, 0)
                self.falling.append(FallingFloor(
                    room=room, col=col,
                    y=float(C.block_bot(row) - 3)))
                self.events.append("loose_fall")
        # falling floor pieces
        for ff in list(self.falling):
            if ff.crashed:
                ff.crashed += 1
                if ff.crashed > 2:
                    self.falling.remove(ff)
                continue
            ff.vel = min(ff.vel + C.FF_ACCEL, C.FF_TERMVEL)
            ff.y += ff.vel
            row = C.row_from_y(int(ff.y) - C.VERT_DIST)
            if row > 2:
                room_below = self.links[ff.room]["down"]
                if room_below == 0:
                    self.falling.remove(ff)
                    continue
                ff.room = room_below
                ff.y -= C.ROW_H * 3
                row -= 3
            if row >= 0 and self.is_floor(ff.room, ff.col, row) \
                    and ff.y >= C.block_bot(row) - 3:
                t = self.tile(ff.room, ff.col, row)
                if t == LOOSE:
                    # falling floor knocks the next one loose
                    self.shake_loose(ff.room, ff.col, row)
                elif t in (PRESSPLATE, UPRESSPLATE, DPRESSPLATE):
                    # rubble jams the plate's gates permanently open
                    self.press_plate(ff.room, ff.col, row, jam=True)
                self.set_tile(ff.room, ff.col, row, RUBBLE, 0)
                ff.y = float(C.block_bot(row) - 3)
                ff.crashed = 1
                self.events.append("floor_crash")
