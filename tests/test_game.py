"""
Integration tests for the Prince of Persia port.

Run with:  pytest tests/test_game.py
All tests run headless (SDL dummy drivers) via the shared harness.
"""

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from harness import input_from, make_game  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from game import constants as C  # noqa: E402
from levels.level import LevelState  # noqa: E402


def run(game, n, keys=frozenset(), prev=None):
    prev = set(prev or ())
    for _ in range(n):
        game.tick(input_from(set(keys), prev))
        prev = set(keys)


def settle(game, n=16):
    run(game, n)


def teleport(kid, room, row, x, face):
    kid.room, kid.row, kid.face = room, row, face
    kid.x = float(x)
    kid.y = C.floor_y(row)
    kid.action = C.ACT_STAND
    kid.start_seq("stand")


# --------------------------------------------------------------- loading
@pytest.mark.parametrize("n", range(15))
def test_levels_load_and_run(n):
    game = make_game(n)
    random.seed(n)
    prev = set()
    for _ in range(100):
        keys = set(random.choice(
            ["", "l", "r", "u", "d", "s", "r+s", "l+u", "r+u"]
        ).split("+")) - {""}
        game.tick(input_from(keys, prev))
        prev = keys
    game.render()
    assert game.kid.room >= 0
    if not game.kid.alive:
        assert game.state in ("dead", "playing")


def test_level_data_sane():
    lv = LevelState.load(1)
    room, block, face = lv.kid_start
    assert 1 <= room <= 24 and 0 <= block < 30 and face in (-1, 1)
    assert len(lv.linkloc) == 256 and len(lv.linkmap) == 256
    assert len(lv.guards) == 2  # level 1 has two guards


# ------------------------------------------------------------- movement
def test_opening_drop_and_landing():
    game = make_game(1)
    settle(game)
    kid = game.kid
    assert kid.alive
    assert kid.row == 1
    assert kid.y == C.floor_y(1)
    assert kid.frame  # animating


def test_run_and_turn():
    game = make_game(1)
    settle(game)
    kid = game.kid
    x0 = kid.x
    run(game, 12, {"r"})
    assert kid.face == 1
    assert kid.x > x0


def test_runjump_clears_two_tile_gap():
    game = make_game(2)
    settle(game, 12)
    kid = game.kid
    # level 2 room 21 row 1: floor at col 1, gap at cols 2-3
    teleport(kid, 21, 1, 17, 1)
    run(game, 4)
    run(game, 4, {"r"})         # past the run-start frames (1-3), where
    run(game, 16, {"r", "u"})   # up would mean a standing jump instead
    assert kid.alive
    assert kid.col >= 4  # landed beyond the gap
    assert kid.row == 1


def test_climb_up_and_press_plate_opens_exit():
    game = make_game(1)
    settle(game)
    kid = game.kid
    teleport(kid, 9, 1, 21, -1)
    run(game, 3)
    run(game, 45, {"u"})        # grab ledge and climb onto the plate
    assert kid.row == 0
    run(game, 6)
    run(game, 10, {"l"})        # step fully onto the plate at col 0
    run(game, 30)
    assert game.level.spec(9, 3, 1) >= 20  # exit door open


def test_exit_advances_level():
    game = make_game(1)
    settle(game)
    kid = game.kid
    game.level.set_tile(9, 3, 1, 16, 48)   # door already open
    game.level.set_tile(9, 4, 1, 17, 48)
    teleport(kid, 9, 1, 3 * 14 + 7, 1)
    run(game, 3)
    run(game, 40, {"u"})
    assert game.level_num == 2


# --------------------------------------------------------------- hazards
def test_fall_two_stories_costs_one_hp():
    game = make_game(1)
    settle(game)
    kid = game.kid
    hp = kid.hp
    run(game, 80, {"r"})  # runs off the hole into the room below
    assert kid.alive
    assert kid.hp == hp - 1


def test_spike_pit_impales():
    game = make_game(1)
    settle(game)
    kid = game.kid
    teleport(kid, 6, 0, 1 * 14 + 7, 1)
    run(game, 2)
    run(game, 40, {"r"})
    assert not kid.alive
    assert kid.frame == 177  # impaled
    assert game.state == "dead"


def test_slicer_kills():
    game = make_game(3)
    settle(game, 12)
    kid = game.kid
    teleport(kid, 16, 2, 7, 1)
    run(game, 2)
    run(game, 30, {"r"})
    assert not kid.alive
    assert game.state == "dead"


def test_loose_floor_detaches_when_stepped_on():
    game = make_game(1)
    settle(game)
    kid = game.kid
    lv = game.level
    # loose floor at room 1, row 2, col 6; run over it from the right
    teleport(kid, 1, 2, 8 * 14 + 7, -1)
    run(game, 8, {"l"})
    run(game, 14)
    assert lv.tile(1, 6, 2) == 0  # detached and fell


# ---------------------------------------------------------------- combat
def make_duel():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.has_sword = True
    kid.hp = kid.max_hp = 10
    teleport(kid, 3, 1, 75, 1)
    opp = game.guards[0]
    opp.x, opp.row, opp.room = 89.0, 1, 3  # within sword reach
    return game, kid, opp


def test_kid_strike_hits_guard():
    game, kid, opp = make_duel()
    opp.control = lambda *a, **k: None  # passive target
    run(game, 6)
    assert kid.sword_drawn
    hp0 = opp.hp
    run(game, 1, {"s"})
    run(game, 10)
    assert opp.hp == hp0 - 1


def test_guard_kills_unarmed_kid():
    random.seed(5)
    game = make_game(1)
    settle(game)
    kid = game.kid
    teleport(kid, 3, 1, 60, 1)
    run(game, 120)
    assert not kid.alive
    assert game.state == "dead"


# ---------------------------------------------------------------- items
def test_sword_pickup():
    game = make_game(1)
    settle(game)
    kid = game.kid
    teleport(kid, 15, 2, 3 * 14 + 7, -1)
    run(game, 2)
    run(game, 2, {"s"})
    run(game, 24)
    assert kid.has_sword
    assert game.level.tile(15, 2, 2) == 1  # sword tile became floor


def test_potion_heals():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.hp = 1
    teleport(kid, 5, 2, 4 * 14 + 7, -1)
    run(game, 3)
    run(game, 2, {"s"})
    run(game, 45)
    assert kid.hp == 2
    assert game.level.tile(5, 3, 2) == 1


# ------------------------------------------------------------ animation
def test_seq_data_integrity():
    from data import seqdata
    for name in ("stand", "startrun", "runjump", "climbup", "hang",
                 "stepfall", "freefall", "strike", "dropdead",
                 "climbstairs", "drinkpotion", "pickupsword"):
        assert name in seqdata.LABELS
    assert seqdata.SEQ_INDEX[2] == "stand"


def test_frame_decode():
    from entities.char import decode_frame
    stand = decode_frame(15, C.CHAR_KID)
    assert stand.table == 0 and stand.image == 15
    guard_ready = decode_frame(158, C.CHAR_GUARD)
    assert guard_ready.table == 3  # CHTAB4 variant


def test_careful_steps_stop_at_edge():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.face = 1
    for _ in range(30):  # keep careful-stepping into the col-4 gap
        run(game, 12, {"r", "s"})
        run(game, 3)
        assert kid.row == 1 and kid.action not in (3, 4), \
            f"fell at x={kid.x}"
    assert kid.col == 3  # parked at the edge (x=55, gap starts at 56)


def test_shift_edge_grab_is_stable():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.face = 1
    run(game, 10, {"r"})
    xs = []
    for _ in range(30):  # walk off the edge holding shift
        run(game, 1, {"r", "s"}, prev={"r", "s"})
        xs.append(kid.x)
    # caught the ledge: swing hang or settled still hang
    assert kid.action in (C.ACT_HANG, C.ACT_HANG_STRAIGHT)
    assert max(xs[-12:]) - min(xs[-12:]) == 0  # no teleporting


# ------------------------------------------------- level-1 gate passage
# From a player recording: the kid opens the gate at room 7 col 9 (via
# the plate in room 8), jump-hangs at room 8's left wall and climbs up
# through the open gate.  He must end standing in the doorway, not be
# ejected across the room seam into the void of room 8 col 0.

def open_gate_and_climb(game):
    kid = game.kid
    game.level.set_tile(7, 9, 0, 4, C.GATE_MAX)   # gate fully open
    teleport(kid, 8, 1, 5, -1)
    run(game, 2)
    run(game, 40, {"u"})                   # jumphang, then climb up
    return kid


def test_climb_through_open_gate_survives():
    game = make_game(1)
    settle(game)
    kid = open_gate_and_climb(game)
    run(game, 20)                          # finish the held-up jumpup
    assert kid.alive
    assert (kid.room, kid.row) == (7, 0)   # standing above, in room 7
    assert kid.action == C.ACT_STAND
    # and he can walk out of the doorway (col 8 is solid; cols 5-6
    # beyond are loose floors, so stop short of them)
    run(game, 8, {"l"})
    run(game, 12)
    assert kid.alive and kid.room == 7 and kid.row == 0
    assert kid.col < 9


def test_closing_gate_knocks_aside_not_into_void():
    game = make_game(1)
    settle(game)
    kid = game.kid
    teleport(kid, 7, 0, 132, -1)           # standing in the gate doorway
    game.level.gates[(7, 9, 0)] = [40, 3]  # gate almost shut
    run(game, 8)
    assert kid.alive
    assert kid.room == 7 and kid.row == 0  # nudged out, never ejected
    assert kid.col <= 8                    # across the seam into the void


def test_gate_closes_at_original_creak_speed():
    lv = LevelState.load(1)
    lv.press_plate(8, 7, 1)
    for _ in range(C.GATE_MAX // C.GATE_RISE + 2):
        lv.tick()
    assert lv.gate_pos(7, 9, 0) == C.GATE_MAX
    # fully open it holds for 50 ticks, then creaks shut at 1/tick:
    # still passable 60 ticks later (the recording's route needs ~80)
    for _ in range(110):
        lv.tick()
    assert lv.gate_pos(7, 9, 0) >= C.GATE_PASSABLE


# ------------------------------------------------------ run control feel
def test_release_mid_stride_stops_on_plant_frame():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.face = 1
    run(game, 2, {"r"})                    # run-start frames 1-2
    assert 1 <= kid.frame <= 3
    run(game, 1)                           # let go immediately:
    assert 1 <= kid.frame <= 14            # still running, no skid yet
    run(game, 16)
    assert kid.frame == 15                 # stopped on a plant frame


def test_up_during_run_start_is_standing_jump():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.face = 1
    run(game, 2, {"r"})
    assert 1 <= kid.frame <= 3
    run(game, 2, {"r", "u"})
    assert kid.in_seq("standjump")
    assert not kid.in_seq("runjump")


def test_hang_holds_while_shift_held_drops_on_release():
    game = make_game(1)
    settle(game)
    kid = game.kid
    kid.face = 1
    run(game, 10, {"r"})
    run(game, 80, {"r", "s"})   # grab the edge, keep holding
    assert kid.action == C.ACT_HANG_STRAIGHT  # still hanging after 6s
    assert kid.col == 4         # body dangles in the open shaft
    run(game, 12)               # release
    assert kid.row == 2 and kid.alive  # dropped onto the rubble below
