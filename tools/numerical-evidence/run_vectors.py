"""Run P2.4-D-5 evidence vectors; never modifies production files."""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
from fractions import Fraction

ROOT = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get("PCB_SOURCE_WORKTREE", "/home/ubuntu/PCB-Studio-Pro-p2-4-d-1"))
TSX = Path(os.environ.get("TSX_BIN", str(SOURCE / "node_modules/.bin/tsx")))

sys.path.insert(0, str(ROOT))
from interval_trig import point_interval
from binary64_cells import classify_decimal_interval

def capture(vector):
    proc = subprocess.run([str(TSX), str(ROOT / "reference_capture.ts"), json.dumps(vector)], capture_output=True, text=True, check=True)
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

def main():
    results=[]; unresolved=0
    for v in VECTORS:
        observed=capture(v)
        trig=point_interval(observed["radiansBits"])
        # The full coordinate interval propagation is deliberately conservative
        # until a sign-aware MPFR interval arithmetic layer is enabled.
        output_cell="UNRESOLVED"
        unresolved += 1
        results.append({"name": v["name"], "observed": observed, "radianTrigInterval": trig, "finalOutputCell": output_cell})
    out={"referenceSource": str(SOURCE), "vectorCount": len(results), "unresolvedCount": unresolved, "results": results}
    print(json.dumps(out, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
