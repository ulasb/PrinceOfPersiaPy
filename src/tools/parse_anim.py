"""
Parse FRAMEDEF.S and SEQTABLE.S from the original Apple II source and
generate Python data modules (src/data/framedefs.py, src/data/seqdata.py).

FRAMEDEF.S: frame definition records.
    main set    :1..:240   db Fimage, Fsword, Fdx, Fdy, Fcheck
    ALTSET1     :150..:189 (guards, chtable4)
    ALTSET2     :1..:90    (princess & vizier, chtable6)
    SWORDTAB    :1..:64    db image, dx, dy

Frame decoding (CTRLSUBS.S decodeim):
    table  = (Fimage & 0x80) >> 5 | (Fsword & 0xC0) >> 6   (0-7)
    image  = Fimage & 0x7F
    sword  = Fsword & 0x3F  (sword frame number, 0 = none)
    Fcheck = bit7/bit6 check marks, bit5 "thin", bits 0-4 foot offset

SEQTABLE.S: animation sequence bytecode, org $3000.
    Instructions (negative bytes): goto -1, aboutface -2, up -3, down -4,
    chx -5, chy -6, act -7, setfall -8, ifwtless -9, die -10, jaru -11,
    jard -12, effect -13, tap -14, nextlevel -15.
    goto/ifwtless are followed by a 2-byte dw address. chx/chy/act/effect/
    tap take 1 byte, setfall takes 2. Any byte 1..240 is a display frame.
    The table starts with 114 dw entries: sequence id -> entry label.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "source_reference" / "01 POP Source" / "Source"
OUT = REPO / "src" / "data"

ORG = 0x3000

INSTRUCTIONS = {
    "goto": -1, "aboutface": -2, "up": -3, "down": -4, "chx": -5,
    "chy": -6, "act": -7, "setfall": -8, "ifwtless": -9, "die": -10,
    "jaru": -11, "jard": -12, "effect": -13, "tap": -14, "nextlevel": -15,
}


def evalexpr(expr: str) -> int:
    """Evaluate a Merlin-style constant expression like `$c0+$20+6`."""
    expr = expr.strip().replace("$", "0x")
    if not re.fullmatch(r"[0-9a-fxA-FX+\-* ()]+", expr):
        raise ValueError(f"unsafe expression: {expr!r}")
    return eval(expr, {"__builtins__": {}})  # noqa: S307 - validated above


def strip_comment(line: str) -> str:
    return line.split(";", 1)[0].rstrip()


def parse_framedef() -> dict:
    sections = {"main": {}, "altset1": {}, "altset2": {}, "swordtab": {}}
    section = None
    for raw in (SRC / "FRAMEDEF.S").read_text().splitlines():
        line = strip_comment(raw)
        if not line.strip() or line.startswith("*"):
            continue
        word = line.split()[0]
        if word == "Fdef":
            section = "main"
            continue
        if word in ("ALTSET1", "ALTSET2", "SWORDTAB"):
            section = word.lower()
            continue
        m = re.match(r"^:(\d+)\s+db\s+(.*)$", line)
        if m and section:
            idx = int(m.group(1))
            vals = [evalexpr(v) for v in m.group(2).split(",")]
            sections[section][idx] = vals
    return sections


def parse_seqtable() -> tuple[bytes, dict, dict]:
    lines = (SRC / "SEQTABLE.S").read_text().splitlines()
    # skip everything before the ` org org` line
    body = []
    started = False
    skipping = False
    for raw in lines:
        if not started:
            if re.match(r"^\s+org\s+org\s*$", raw):
                started = True
            continue
        line = strip_comment(raw)
        if not line.strip() or line.lstrip().startswith("*"):
            continue
        word = line.split()[0]
        # `do 0 ... fin` blocks are assembled out; lst/lstdo/usr are
        # assembler listing directives with no output
        if word == "do":
            skipping = True
            continue
        if word == "fin":
            skipping = False
            continue
        if skipping or word in ("lst", "lstdo", "usr"):
            continue
        body.append(line)

    # statements: (label, directive, args) with local-label scoping
    def parse_line(line):
        label = None
        rest = line
        if not line[0].isspace():
            parts = line.split(None, 1)
            label = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
        rest = rest.strip()
        directive, args = None, ""
        if rest:
            parts = rest.split(None, 1)
            directive = parts[0]
            args = parts[1] if len(parts) > 1 else ""
        return label, directive, args

    # two passes: 1) compute addresses, 2) emit bytes
    def items_of(args):
        return [a.strip() for a in args.split(",") if a.strip() != ""]

    def db_size(args):
        return len(items_of(args))

    statements = [parse_line(line) for line in body]

    labels = {}          # global label -> address
    locals_map = {}      # (scope, local) -> address
    seq_index_labels = []  # ordered dw targets of the :N table entries

    addr = ORG
    scope = None
    for label, directive, args in statements:
        if label:
            if label.startswith(":"):
                locals_map[(scope, label)] = addr
            else:
                labels[label] = addr
                scope = label
        if directive == "db":
            addr += db_size(args)
        elif directive == "dw":
            addr += 2 * len(items_of(args))
        elif directive == "ds":
            addr += evalexpr(args)
        elif directive is not None:
            raise ValueError(f"unknown directive {directive!r}")

    out = bytearray()
    scope = None
    table_done = False
    for label, directive, args in statements:
        if label and not label.startswith(":"):
            scope = label
            table_done = True
        if directive == "db":
            for item in items_of(args):
                if item in INSTRUCTIONS:
                    out.append(INSTRUCTIONS[item] & 0xFF)
                else:
                    out.append(evalexpr(item) & 0xFF)
        elif directive == "dw":
            for item in items_of(args):
                if item.startswith(":"):
                    target = locals_map[(scope, item)]
                else:
                    target = labels[item]
                out += target.to_bytes(2, "little")
                if not table_done:
                    seq_index_labels.append(item)
        elif directive == "ds":
            out += bytes(evalexpr(args))

    seq_index = {i + 1: name for i, name in enumerate(seq_index_labels)}
    label_offsets = {name: a - ORG for name, a in labels.items()}
    return bytes(out), label_offsets, seq_index


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "__init__.py").touch()

    fd = parse_framedef()
    with open(OUT / "framedefs.py", "w") as f:
        f.write('"""Generated from FRAMEDEF.S by tools/parse_anim.py. '
                'Do not edit."""\n\n')
        for name in ("main", "altset1", "altset2"):
            f.write(f"{name.upper()} = {{\n")
            for idx in sorted(fd[name]):
                i, s, dx, dy, ck = fd[name][idx]
                f.write(f"    {idx}: ({i}, {s}, {dx}, {dy}, {ck}),\n")
            f.write("}\n\n")
        f.write("SWORDTAB = {\n")
        for idx in sorted(fd["swordtab"]):
            f.write(f"    {idx}: {tuple(fd['swordtab'][idx])},\n")
        f.write("}\n")

    seq_bytes, labels, seq_index = parse_seqtable()
    with open(OUT / "seqdata.py", "w") as f:
        f.write('"""Generated from SEQTABLE.S by tools/parse_anim.py. '
                'Do not edit."""\n\n')
        f.write(f"ORG = {ORG}\n\n")
        f.write(f"SEQ_BYTES = bytes({list(seq_bytes)})\n\n")
        f.write(f"LABELS = {labels}\n\n")
        f.write(f"SEQ_INDEX = {seq_index}\n")

    print(f"framedefs: main {len(fd['main'])}, altset1 {len(fd['altset1'])},"
          f" altset2 {len(fd['altset2'])}, swordtab {len(fd['swordtab'])}")
    print(f"seqtable: {len(seq_bytes)} bytes, {len(labels)} labels, "
          f"{len(seq_index)} sequence ids")
    return 0


if __name__ == "__main__":
    sys.exit(main())
