"""Portable P2.4-D-6 evidence runner; never modifies production files."""
from __future__ import annotations
import json, os, subprocess, sys, struct
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parent
EXPECTED_REFERENCE = "941262899a46e54cbf1a94a4da6dd528b8d36780"
SOURCE_ENV = os.environ.get("PCB_SOURCE_WORKTREE")
TSX_ENV = os.environ.get("TSX_BIN")
COMMIT = os.environ.get("PCB_REFERENCE_COMMIT")
if not SOURCE_ENV:
    raise SystemExit("PCB_SOURCE_WORKTREE is required")
if not TSX_ENV:
    raise SystemExit("TSX_BIN is required")
if COMMIT != EXPECTED_REFERENCE:
    raise SystemExit(f"PCB_REFERENCE_COMMIT must equal {EXPECTED_REFERENCE}")
SOURCE = Path(SOURCE_ENV).expanduser().resolve()
SOURCE_FILE = SOURCE / "shared/engineering.ts"
TSX = Path(TSX_ENV).expanduser().resolve()
if not SOURCE_FILE.is_file():
    raise SystemExit(f"reference source file is missing: {SOURCE_FILE}")
if not TSX.is_file():
    raise SystemExit(f"TSX executable is missing: {TSX}")

sys.path.insert(0, str(ROOT))
from interval_arith import Interval, add, mul, sub, rational, roundtrip, deserialize
from interval_trig import exact_mpfr, point_intervals
from binary64_cells import classify_with_reason


def capture(vector):
    env = os.environ.copy()
    env.update({"PCB_SOURCE_WORKTREE": str(SOURCE), "PCB_REFERENCE_COMMIT": COMMIT})
    proc = subprocess.run([str(TSX), str(ROOT / "reference_capture.ts"), json.dumps(vector)], env=env, capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def vector(name, x, y, degrees, origin_x=0, origin_y=0, local_x=None, local_y=None, end_x=0, end_y=0):
    return {"name": name, "x": x, "y": y, "degrees": degrees,
            "originX": origin_x, "originY": origin_y,
            "localX": x if local_x is None else local_x,
            "localY": y if local_y is None else local_y,
            "endX": end_x, "endY": end_y}

VECTORS = [
    vector("zero", 3, 4, 0, end_x=80, end_y=40),
    vector("q1", 3, 4, 45, end_x=80, end_y=40),
    vector("q2", 3, 4, 90, end_x=-80, end_y=40),
    vector("q3", 3, 4, 180, end_x=-80, end_y=-40),
    vector("q4", 3, 4, 270, end_x=80, end_y=-40),
    vector("negative", -7, 2.3, -31, end_x=-80, end_y=40),
    vector("out-of-range", 3, 4, 1097.25, end_x=80, end_y=40),
    vector("signed-zero", -0.0, 0.0, -0.0, end_x=0, end_y=2),
    vector("subnormal", 5e-324, -5e-324, 90, end_x=2, end_y=2),
    vector("max-translation", 1.7976931348623157e308, 1.7976931348623157e308, 0, origin_x=1.7976931348623157e308, origin_y=1.7976931348623157e308, local_x=1.7976931348623157e308, local_y=-1.7976931348623157e308, end_x=2, end_y=3),
    vector("route-below-epsilon", 0, 0, 0, end_x=9.999999999999997e-8, end_y=2),
    vector("route-at-epsilon", 0, 0, 0, end_x=1e-7, end_y=2),
    vector("route-above-epsilon", 0, 0, 0, end_x=1.0000000000000002e-7, end_y=2),
]


def bits_float(bits):
    return struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]


def finite_bits(bits):
    return ((int(bits, 16) >> 52) & 0x7ff) != 0x7ff


def exact_point(bits):
    value = exact_mpfr(bits)
    return Interval(value, value)


def classify_output(bits, interval):
    if not finite_bits(bits):
        value = bits_float(bits)
        category = "NAN" if value != value else ("POSITIVE_INFINITY" if value > 0 else "NEGATIVE_INFINITY")
        return {"status": "NON_FINITE", "reason": f"captured JavaScript output is {category}", "candidateBits": bits, "interval": interval.serialized()}
    lower = Fraction(*rational(interval.lo))
    upper = Fraction(*rational(interval.hi))
    status, reason = classify_with_reason(bits, lower, upper)
    return {"status": status, "reason": reason, "candidateBits": bits, "interval": interval.serialized()}


def propagate(observed):
    trig = point_intervals(observed["radiansBits"])
    local_x = exact_point(observed["input"]["local"]["xBits"])
    local_y = exact_point(observed["input"]["local"]["yBits"])
    origin_x = exact_point(observed["input"]["origin"]["xBits"])
    origin_y = exact_point(observed["input"]["origin"]["yBits"])
    # Exact source order: x* cos - y* sin; x* sin + y* cos.
    rx = sub(mul(local_x, trig["cos"]), mul(local_y, trig["sin"]))
    ry = add(mul(local_x, trig["sin"]), mul(local_y, trig["cos"]))
    tx = add(origin_x, rx)
    ty = add(origin_y, ry)
    for interval in (trig["sin"], trig["cos"], rx, ry, tx, ty):
        if not roundtrip(interval):
            raise AssertionError("MPFR interval serialization did not round-trip exactly")
    return trig, {"rotatedX": rx.serialized(), "rotatedY": ry.serialized(), "translatedX": tx.serialized(), "translatedY": ty.serialized()}, {
        "rotateX": classify_output(observed["rotate"]["xBits"], rx),
        "rotateY": classify_output(observed["rotate"]["yBits"], ry),
        "transformX": classify_output(observed["transform"]["xBits"], tx),
        "transformY": classify_output(observed["transform"]["yBits"], ty),
    }


def main():
    results=[]; counts={"UNIQUE":0, "UNRESOLVED":0, "INVALID":0, "NON_FINITE":0}
    for v in VECTORS:
        observed = capture(v)
        trig, intermediates, classifications = propagate(observed)
        for item in classifications.values(): counts[item["status"]] += 1
        results.append({"name": v["name"], "observed": observed, "radianTrigInterval": {"sin": trig["sin"].serialized(), "cos": trig["cos"].serialized()}, "intermediateIntervals": intermediates, "classifications": classifications, "routeObservation": observed["route"]})
    out={"referenceSource": str(SOURCE_FILE), "referenceCommit": COMMIT, "vectorCount": len(results), "classificationCounts": counts, "results": results}
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
