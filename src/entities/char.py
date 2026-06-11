"""
Character base: position, facing, and the original sequence interpreter.

Characters are animated by the SEQTABLE bytecode exactly as in the
original (COLL.S ANIMCHAR): each game tick consumes instructions until a
display-frame byte is reached. Movement deltas (chx/chy), row changes
(up/down), action changes and fall parameters all come from the data.

Coordinates: x is in 140-res game pixels, room-local (0-139, may go out
of range briefly before room normalization); y is the feet scanline;
row is the logical block row (CharBlockY).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from data import framedefs, seqdata
from game import constants as C

# instruction opcodes (SEQTABLE.S)
OP_GOTO = 0xFF
OP_ABOUTFACE = 0xFE
OP_UP = 0xFD
OP_DOWN = 0xFC
OP_CHX = 0xFB
OP_CHY = 0xFA
OP_ACT = 0xF9
OP_SETFALL = 0xF8
OP_IFWTLESS = 0xF7
OP_DIE = 0xF6
OP_JARU = 0xF5
OP_JARD = 0xF4
OP_EFFECT = 0xF3
OP_TAP = 0xF2
OP_NEXTLEVEL = 0xF1


def seq_offset(name: str) -> int:
    return seqdata.LABELS[name]


def signed(b: int) -> int:
    return b - 256 if b >= 128 else b


@dataclass
class FrameInfo:
    image: int      # image number within table
    table: int      # decoded table number 0-7
    sword: int      # sword frame 0-63 (0 = none)
    dx: int
    dy: int
    check: int      # Fcheck byte (foot offset in low 5 bits)

    @property
    def foot_dx(self) -> int:
        return self.check & 0x1F

    @property
    def is_odd(self) -> bool:
        return bool(self.check & 0x80)


def frame_def(frame: int, char_id: int) -> Tuple[int, int, int, int, int]:
    """Frame lookup with alternate-set substitution (CTRLSUBS usealtsets)."""
    if char_id == C.CHAR_KID:
        return framedefs.MAIN.get(frame, (0, 0, 0, 0, 0))
    if char_id >= 5:  # princess & vizier
        return framedefs.ALTSET2.get(frame, framedefs.MAIN.get(
            frame, (0, 0, 0, 0, 0)))
    # enemies: frames 102-106 (falling) -> 172-176; 150-189 from altset1
    f = frame
    if char_id >= 2 and 102 <= f <= 106:
        f += 70
    if 150 <= f <= 189:
        return framedefs.ALTSET1.get(f, (0, 0, 0, 0, 0))
    return framedefs.MAIN.get(f, (0, 0, 0, 0, 0))


def decode_frame(frame: int, char_id: int) -> FrameInfo:
    fimage, fsword, fdx, fdy, fcheck = frame_def(frame, char_id)
    table = ((fimage & 0x80) >> 5) | ((fsword & 0xC0) >> 6)
    return FrameInfo(
        image=fimage & 0x7F,
        table=table,
        sword=fsword & 0x3F,
        dx=fdx,   # generated data is already signed (280-res half-pixels)
        dy=fdy,
        check=fcheck,
    )


@dataclass
class Char:
    char_id: int = C.CHAR_KID
    room: int = 1
    x: float = 0.0          # 140-res pixels, room-local
    y: int = 0              # feet scanline
    row: int = 0            # CharBlockY
    face: int = -1          # -1 left, +1 right
    action: int = C.ACT_STAND
    xvel: int = 0
    yvel: int = 0
    frame: int = 15         # CharPosn
    seq: int = 0            # offset into SEQ_BYTES
    hp: int = C.INITIAL_HP
    max_hp: int = C.INITIAL_HP
    alive: bool = True
    has_sword: bool = True
    weightless: int = 0     # float-potion ticks remaining
    hurt_cooldown: int = 0
    events: List[str] = field(default_factory=list)

    # ------------------------------------------------------------ helpers
    @property
    def col(self) -> int:
        return int(self.x) // C.TILE_W

    def start_seq(self, name: str) -> None:
        self.seq = seq_offset(name)

    def in_seq(self, *names: str) -> bool:
        """True if current seq pointer lies within one of the named
        sequences (between its label and the next label)."""
        starts = sorted(seqdata.LABELS.values())
        for name in names:
            begin = seqdata.LABELS[name]
            idx = starts.index(begin)
            end = starts[idx + 1] if idx + 1 < len(starts) else 1 << 30
            if begin <= self.seq < end:
                return True
        return False

    def frame_info(self) -> FrameInfo:
        return decode_frame(self.frame, self.char_id)

    # -------------------------------------------------- seq interpreter
    def animate(self) -> None:
        """Advance one tick: run instructions until a frame byte."""
        b = seqdata.SEQ_BYTES
        guard = 0
        while True:
            guard += 1
            if guard > 100:  # malformed loop safety
                return
            op = b[self.seq]
            self.seq += 1
            if op < 0xF1:               # display frame (incl. blank 0)
                self.frame = op
                return
            if op == OP_GOTO:
                target = b[self.seq] | (b[self.seq + 1] << 8)
                self.seq = target - seqdata.ORG
            elif op == OP_ABOUTFACE:
                self.face = -self.face
            elif op == OP_UP:
                self.row -= 1
            elif op == OP_DOWN:
                self.row += 1
            elif op == OP_CHX:
                dx = signed(b[self.seq])
                self.seq += 1
                self.x += dx * self.face
            elif op == OP_CHY:
                self.y += signed(b[self.seq])
                self.seq += 1
            elif op == OP_ACT:
                self.action = b[self.seq]
                self.seq += 1
            elif op == OP_SETFALL:
                self.xvel = signed(b[self.seq])
                self.yvel = signed(b[self.seq + 1])
                self.seq += 2
            elif op == OP_IFWTLESS:
                target = b[self.seq] | (b[self.seq + 1] << 8)
                if self.weightless:
                    self.seq = target - seqdata.ORG
                else:
                    self.seq += 2
            elif op == OP_DIE:
                self.alive = False
                self.events.append("die")
            elif op == OP_JARU:
                self.events.append("jaru")
            elif op == OP_JARD:
                self.events.append("jard")
            elif op == OP_EFFECT:
                self.seq += 1
                self.events.append("effect")
            elif op == OP_TAP:
                sound = b[self.seq]
                self.seq += 1
                self.events.append(f"tap{sound}")
            elif op == OP_NEXTLEVEL:
                self.events.append("nextlevel")

    # ------------------------------------------------------------ physics
    # Only ACT_FREEFALL uses the velocity integrator; during ACT_MIDAIR
    # the fall ramp comes from the sequence's chy instructions (the
    # original applies gravity only once `setfall` hands over to freefall).
    def apply_gravity(self) -> None:
        if self.action == C.ACT_FREEFALL:
            if self.weightless:
                self.yvel = min(self.yvel + 1, 6)
            else:
                self.yvel = min(self.yvel + C.GRAVITY, C.TERMINAL_VELOCITY)

    def add_fall(self) -> Optional[int]:
        """Apply fall velocity; return previous y for floor crossing."""
        if self.action != C.ACT_FREEFALL:
            return None
        prev = self.y
        self.x += self.xvel * self.face
        self.y += self.yvel
        return prev

    def normalize(self, level) -> None:
        """Wrap room-local coordinates across room boundaries."""
        if self.room == 0:
            return
        while self.x < 0:
            nxt = level.link(self.room, "left")
            if nxt == 0:
                self.x = 0
                break
            self.room = nxt
            self.x += C.SCREEN_W
        while self.x >= C.SCREEN_W:
            nxt = level.link(self.room, "right")
            if nxt == 0:
                self.x = C.SCREEN_W - 1
                break
            self.room = nxt
            self.x -= C.SCREEN_W
        while self.row < 0:
            nxt = level.link(self.room, "up")
            if nxt == 0:
                break
            self.room = nxt
            self.row += C.ROOM_H
            self.y += C.ROW_H * C.ROOM_H
        while self.row > 2:
            nxt = level.link(self.room, "down")
            if nxt == 0:
                break
            self.room = nxt
            self.row -= C.ROOM_H
            self.y -= C.ROW_H * C.ROOM_H
