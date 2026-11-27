# PHASE 6.1 — P2.4-D-6 Evidence Harness Integrity and Sign-Aware Coordinate Propagation

## Final verdict

**COORDINATE_PROPAGATION_PARTIALLY_VALIDATED**

The D-5 evidence harness was repaired and exercised end to end. The runner now requires an explicitly supplied source checkout and TSX executable, imports the pinned reference implementation dynamically, captures the exact JavaScript radian and output bit patterns, propagates MPFR intervals through the source operation order using sign-aware addition/subtraction/multiplication, serializes every MPFR endpoint losslessly, and invokes the exact-rational binary64 cell classifier for each eligible finite output.

The 13-vector run produced 52 coordinate outputs:

```text
UNIQUE      27
UNRESOLVED  24
INVALID      0
NON_FINITE   1
```

The result is partial because unresolved outputs remain where the rigorous interval is too wide or a captured output is non-finite. No unresolved result was converted to `UNIQUE`, and no claim was made that JavaScript `Math.sin` or `Math.cos` is correctly rounded.

## 1. Immutable references and branch baseline

- Repository: `soheil6913/PCB`
- Reference implementation: `941262899a46e54cbf1a94a4da6dd528b8d36780`
- Previous evidence commit: `fba20442e8fc352dbbfdf545cb3827ca3428e69f`
- Previous evidence branch: `evidence/phase6-1-p2-4-d-5-interval-trig-cell-validation-20261127`
- Documentation baseline: `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`
- New branch: `evidence/phase6-1-p2-4-d-6-coordinate-propagation-20261127`

The new branch was created from the published D-5 evidence commit. The previous branch was not rewritten or modified.

## 2. Changed evidence-only paths

The branch contains the D-5 evidence artifacts carried forward and repaired/extended, plus this report:

- `PHASE_6_1_P2_4_D_6_COORDINATE_PROPAGATION_REPORT.md`
- `tools/numerical-evidence/interval_trig.py`
- `tools/numerical-evidence/interval_arith.py` — new sign-aware MPFR interval operations and exact endpoint serialization.
- `tools/numerical-evidence/binary64_cells.py`
- `tools/numerical-evidence/reference_capture.ts`
- `tools/numerical-evidence/run_vectors.py`
- `tools/numerical-evidence/test_numerical_evidence.py` — new dedicated evidence-tool tests.
- `tools/numerical-evidence/vector_results.json`
- `tools/numerical-evidence/TOOLCHAIN.md`
- `tools/numerical-evidence/requirements.txt`

No production source file, existing project test, CI workflow, or `main` branch was modified.

## 3. Harness portability repair

The previous `reference_capture.ts` contained a hardcoded import:

```text
/home/ubuntu/PCB-Studio-Pro-p2-4-d-1/shared/engineering.ts
```

That path was removed. The repaired capture helper requires:

- `PCB_SOURCE_WORKTREE`: supplied reference source checkout.
- `TSX_BIN`: explicit TSX executable.
- `PCB_REFERENCE_COMMIT`: required to equal `941262899a46e54cbf1a94a4da6dd528b8d36780`.

It resolves and validates:

```text
$PCB_SOURCE_WORKTREE/shared/engineering.ts
```

before dynamic import. It fails explicitly when the source checkout, source file, TSX executable, or required commit variable is missing or incorrect. The JSON output records the resolved absolute source path and pinned reference commit.

The same command is therefore portable across machines, provided the caller supplies the reference checkout and executable paths explicitly:

```bash
PCB_SOURCE_WORKTREE=/path/to/reference/source \
TSX_BIN=/path/to/reference/source/node_modules/.bin/tsx \
PCB_REFERENCE_COMMIT=941262899a46e54cbf1a94a4da6dd528b8d36780 \
python tools/numerical-evidence/run_vectors.py > /tmp/p24d6-results.json
```

There is no fallback to another checkout.

## 4. Exact source operation order

The pinned reference source was imported directly. The relevant definitions are:

```ts
// shared/engineering.ts:57
const radians = degrees * Math.PI / 180;
const cos = Math.cos(radians);
const sin = Math.sin(radians);
return {
  x: point.x * cos - point.y * sin,
  y: point.x * sin + point.y * cos,
};

// shared/engineering.ts:58
const rotated = rotatePoint(local, rotation);
return { x: origin.x + rotated.x, y: origin.y + rotated.y };
```

The evidence runner preserves this order:

1. Capture JavaScript `degrees * Math.PI / 180` as a binary64 bit pattern.
2. Import that exact radian bit pattern into MPFR.
3. Evaluate independent MPFR sine and cosine enclosures.
4. Multiply each exact local-coordinate interval by its corresponding trig interval.
5. Subtract `local.x*cos - local.y*sin` for rotated x.
6. Add `local.x*sin + local.y*cos` for rotated y.
7. Add `origin.x + rotated.x` and `origin.y + rotated.y` for transformed coordinates.
8. Classify each captured JavaScript output bit pattern against the independently propagated interval.

The runner does not replace this with an algebraically equivalent expression.

## 5. Exact MPFR endpoint serialization

The prior decimal `str(mpfr_value)` representation was not used as the authoritative interval representation. `interval_arith.py` serializes each MPFR endpoint with `gmpy2.to_binary`, then base64-encodes the exact MPFR binary payload. Parsing uses `gmpy2.from_binary`.

For each interval, the runner verifies:

```text
parse(serialize(endpoint)) == endpoint
```

for both lower and upper endpoints. The dedicated tests cover:

- positive and negative zero;
- positive and negative smallest-subnormal scale;
- values near ±1;
- signed and ordinary finite values.

The machine-readable vector result stores the base64 endpoint payloads, not decimal approximations. The report and JSON therefore distinguish exact endpoint identity from human-readable formatting.

## 6. Sign-aware MPFR interval arithmetic

`interval_arith.py` implements the required operations at 256-bit precision with explicit directed rounding.

### Addition

```text
[al, ah] + [bl, bh]
= [RNDD(al + bl), RNDU(ah + bh)]
```

### Subtraction

```text
[al, ah] - [bl, bh]
= [RNDD(al - bh), RNDU(ah - bl)]
```

### Negation

```text
-[al, ah] = [RNDD(-ah), RNDU(-al)]
```

### Multiplication

All four endpoint products are evaluated under both outward directions. The lower endpoint is the minimum of the four `RoundDown` products; the upper endpoint is the maximum of the four `RoundUp` products. This handles:

- positive × positive;
- positive × negative;
- negative × negative;
- intervals crossing zero;
- exact zero and signed-zero observations;
- subnormal-scale values;
- cancellation and large finite values.

The interval constructor rejects inverted endpoints. Unsupported/non-finite candidate classifications are not silently treated as ordinary finite cells.

## 7. Exact-rational binary64 classifier execution

The runner no longer contains the D-5 placeholder:

```text
output_cell = "UNRESOLVED"
```

For every finite captured rotate/transform output, it:

1. Reads the exact JavaScript output bits.
2. Converts the exact serialized MPFR endpoints to exact rational values through MPFR-to-rational conversion.
3. Calls `classify_with_reason(candidate_bits, lower, upper)`.
4. Records the actual status, candidate bits, serialized interval, and reason.

The classifier returns only `UNIQUE`, `UNRESOLVED`, or `INVALID`. Captured NaN/infinity outputs are recorded in the separate `NON_FINITE` category and are not sent through an ordinary finite candidate cell.

The dedicated regression test reads the runner source and fails if classifier invocation is removed or the old constant placeholder is reintroduced.

## 8. Classifier and arithmetic test results

The evidence-only unit suite ran **8 tests**, all passing:

- exact MPFR serialization round-trip for signed zero, subnormal-scale, near-one, and negative values;
- positive × positive interval multiplication;
- positive × negative multiplication;
- negative × negative multiplication;
- intervals crossing zero;
- addition, subtraction, negation, and cancellation;
- exact `UNIQUE` candidate inside a binary64 cell;
- exact lower and upper midpoint `UNRESOLVED` behavior;
- positive subnormal, smallest normal, positive/negative maximum finite, signed-zero, and invalid infinity candidate behavior;
- reason recording;
- runner classifier-invocation integrity.

These tests validate the evidence tools independently of the reference geometry tests. They do not prove JavaScript native trig correctness.

## 9. Executed vector results

The full retained 13-vector corpus ran successfully. `tools/numerical-evidence/vector_results.json` records the exact inputs, captured radian bits, captured JavaScript outputs, MPFR trig interval payloads, intermediate rotated/translated interval payloads, final candidate bits, classifier statuses, and reasons.

The run summary was:

| Classification | Count | Meaning |
|---|---:|---|
| `UNIQUE` | 27 | The propagated interval lies strictly inside the captured candidate's binary64 cell |
| `UNRESOLVED` | 24 | The interval touches/crosses a midpoint, is too broad, or signed-zero proof is unavailable |
| `INVALID` | 0 | No malformed finite candidate was produced |
| `NON_FINITE` | 1 | A captured JavaScript output was infinity/NaN and was kept out of finite-cell classification |

The 52 outputs are four coordinates per vector: rotated x/y and translated x/y. Route points remain compatibility observations and are not treated as transform output cells.

The `UNIQUE` results are genuine classifier results, not status labels assigned by the runner. The `UNRESOLVED` results are not failures of the reference implementation; they identify where the evidence interval does not prove a unique cell.

## 10. Representative compatibility observations

The 45° vector retained the reference behavior:

```text
radian bits: 0x3fe921fb54442d18
rotate x:    0xbfe6a09e667f3bc8
rotate y:    0x4013cc8a99af5453
```

The exact 90° reference sequence remains distinct from the mathematical identity:

```text
radian bits: 0x3ff921fb54442d18
rotate x:    0xc010000000000000
rotate y:    0x4008000000000001
```

No conclusion that the native JavaScript sine or cosine is correctly rounded is drawn from these observations. The classifier only answers whether the independent propagated interval proves that a captured output occupies one binary64 cell.

## 11. Explicit unresolved categories

Unresolved outputs in this run arise from one or more of:

- broad MPFR trigonometric interval bounds for non-degenerate angular intervals;
- interval width crossing a binary64 midpoint;
- signed-zero output requiring operation-sign evidence beyond a real-number cell;
- cancellation and large-coordinate propagation that does not fit a unique output cell;
- non-finite captured results, which are reported separately rather than classified as finite;
- absence of a complete general critical-point-tightening evaluator for arbitrary angular intervals.

No unresolved result was silently promoted to `UNIQUE`. No `INVALID` result was used as a substitute for an unproven finite claim.

## 12. Reproducibility record

Observed toolchain:

- Python `3.12.3`;
- Node.js `v22.23.4`;
- TSX `4.20.6`;
- gmpy2 `2.3.2`;
- MPFR `4.2.2`;
- GMP `6.3.0`.

The exact reproduction command is documented in `tools/numerical-evidence/TOOLCHAIN.md`. The runner records the resolved source path and reference commit in the output. The gmpy2 package version is pinned, but package hashes and a cross-architecture CI lock are not yet provided.

## 13. Remaining limitations

1. The interval trigonometry module still uses a conservative global bound for non-degenerate angle intervals; it does not yet provide narrow rigorous quadrant/extremum tightening for every arbitrary interval.
2. The runner's `UNIQUE` results prove output-cell occupancy only for the propagated interval produced by the evidence arithmetic; they do not prove native JavaScript trig correct rounding independently of that interval's assumptions.
3. The signed-zero classifier conservatively returns `UNRESOLVED` for real-number cells; proving the sign bit requires operation-level sign analysis.
4. Non-finite results require a separate compatibility contract and are reported as `NON_FINITE`, not finite-cell classifications.
5. CI reproducibility remains incomplete because package hashes and a fixed architecture image are not committed.

## Conclusion

D-6 closes the principal D-5 harness-integrity gap: the classifier is actually executed, exact MPFR endpoints survive serialization round trips, sign-aware interval arithmetic follows the reference operation sequence, source checkout paths are explicit and portable, and every eligible output receives a recorded classification and reason.

The evidence package is therefore **partially validated**. Twenty-seven coordinate outputs are proven by the executed classifier to lie within unique candidate binary64 cells; twenty-four remain unresolved; and one non-finite result is explicitly separated from finite classification. These outcomes are compatibility evidence, not a mathematical claim that JavaScript native trigonometric functions are correctly rounded.

**COORDINATE_PROPAGATION_PARTIALLY_VALIDATED**
