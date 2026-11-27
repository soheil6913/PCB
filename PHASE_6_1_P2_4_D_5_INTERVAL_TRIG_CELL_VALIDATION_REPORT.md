# PHASE 6.1 — P2.4-D-5 General MPFR Interval Trigonometry and Binary64 Cell Validation

## Final verdict

**INTERVAL_ORACLE_PARTIALLY_VALIDATED**

This phase delivers isolated numerical-evidence tooling, exact binary64 reference capture, MPFR point enclosures for arbitrary finite binary64 radian inputs, a conservative interval API, an exact-rational binary64 cell classifier, and a machine-readable 13-vector run. The MPFR point path and conservative cell semantics are validated. The result is not complete because the interval evaluator intentionally returns a broad `[-1,1]` enclosure for non-degenerate angular intervals until a fully proven critical-point/range-reduction tightening path is added, and final coordinate/translation propagation remains unresolved for all executed vectors.

No production source, existing test, `main`, or production workflow was modified. No checked transform was implemented, and no production numerical bound was introduced.

## 1. Baseline and reference verification

- Repository: `soheil6913/PCB`
- Reference implementation: `941262899a46e54cbf1a94a4da6dd528b8d36780`
- Previous evidence commit: `eea7411deaaeed50da6327e8106b1ce3ebaca535`
- Documentation baseline: `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`
- New branch: `evidence/phase6-1-p2-4-d-5-interval-trig-cell-validation-20261127`

The reference commit was verified in the source worktree and remains the authoritative implementation for the captured JavaScript observations.

## 2. Added test-only artifacts

Exactly the following evidence-only paths were added:

| Path | Purpose |
|---|---|
| `tools/numerical-evidence/interval_trig.py` | MPFR-backed exact-point sine/cosine enclosures and conservative interval API |
| `tools/numerical-evidence/binary64_cells.py` | Exact-rational `UNIQUE`/`UNRESOLVED`/`INVALID` output-cell classifier |
| `tools/numerical-evidence/reference_capture.ts` | Imports the reference `engineering.ts` and captures exact JavaScript input/radian/output bit patterns |
| `tools/numerical-evidence/run_vectors.py` | Runs the adversarial evidence corpus and emits machine-readable observations |
| `tools/numerical-evidence/vector_results.json` | Results from the executed 13-vector run |
| `tools/numerical-evidence/requirements.txt` | Pins `gmpy2==2.3.2` for the isolated runner |
| `tools/numerical-evidence/TOOLCHAIN.md` | Records Python, Node, tsx, gmpy2, MPFR, and GMP versions plus reproduction commands |
| `PHASE_6_1_P2_4_D_5_INTERVAL_TRIG_CELL_VALIDATION_REPORT.md` | This report |

No existing tests or production files were changed.

## 3. Qualified toolchain

The isolated environment used for the run contained:

- Python `3.12.3`
- `gmpy2 2.3.2`
- MPFR `4.2.2`
- GMP `6.3.0`
- Node.js `v22.23.4`
- project `tsx 4.20.6`

The MPFR context used 256-bit precision with explicit `RoundDown` and `RoundUp`. The prior D-4 qualification established distinct directed-rounding behavior, exact binary64 rational import for representative normal/subnormal/max values, and directed π bounds. This phase reuses that qualified isolated environment rather than adding project dependencies.

## 4. General interval trigonometry implementation

### 4.1 Exact binary64 point inputs

`interval_trig.py` decodes a hexadecimal IEEE-754 word into an exact rational using sign, exponent, and fraction bits. It imports that rational into MPFR without decimal conversion. For a finite binary64 radian input, `point_interval(bits)` evaluates:

```text
sin(x) under RoundDown
sin(x) under RoundUp
cos(x) under RoundDown
cos(x) under RoundUp
```

The returned endpoints are therefore MPFR directed results for the exact binary64 real input, subject to MPFR's documented transcendental guarantees. Positive and negative zero are retained as input bit cases; non-finite inputs are rejected as invalid real interval endpoints.

This path does not rely on ordinary JavaScript or Python argument reduction. MPFR performs its own arbitrary-precision range reduction. The evaluator makes no claim about JavaScript native `Math.sin` or `Math.cos` being correctly rounded.

### 4.2 Non-degenerate intervals

`interval_from_bits(lo_bits, hi_bits)` validates finite ordered endpoints. For a degenerate interval it returns the MPFR point enclosure. For a non-degenerate interval it currently returns the rigorous global bounds:

```text
sin([lo, hi]) ⊆ [-1, 1]
cos([lo, hi]) ⊆ [-1, 1]
```

This is conservative and valid for every real finite interval, including large arguments and all quadrants. It deliberately does not claim a narrow interval. Critical-point detection, quadrant tightening, and endpoint monotonicity are not inferred from ordinary floating-point argument reduction. The result carries a reason stating that tightening is unresolved.

This design satisfies the fail-safe requirement—never return a falsely narrow interval—but it does not yet provide the desired efficient general interval evaluator.

## 5. Exact binary64 output-cell classifier

`binary64_cells.py` uses exact Python `Fraction` values, not decimal-string comparisons. It computes adjacent representable values with `nextafter` and exact midpoint boundaries. It returns only:

- `UNIQUE` when the full interval lies strictly inside the candidate's cell.
- `UNRESOLVED` when the interval touches/crosses a midpoint or the candidate is signed zero.
- `INVALID` for malformed intervals or non-finite candidates.

Special behavior includes:

- Signed zero: `UNRESOLVED`, because the real-number cell alone cannot prove the sign bit selected by an operation.
- Normal and subnormal finite candidates: exact adjacent midpoint construction.
- Maximum finite values: explicit overflow-side threshold using the conceptual next power-of-two boundary rather than calling `nextafter(MAX, +Infinity)` and converting infinity to a rational.
- Non-finite candidate bits: `INVALID`.

A `UNIQUE` result is therefore intentionally stronger than a decimal match: it requires exact rational comparison against both cell boundaries.

## 6. Independent classifier validation

The classifier was tested outside the production test suite with exact rational constructions:

| Candidate/test | Result |
|---|---|
| exact `1.0` inside its own cell | `UNIQUE` |
| exact smallest normal (`0x0010000000000000`) | `UNIQUE` |
| exact maximum finite positive | `UNIQUE` |
| exact lower midpoint for `1.0` | `UNRESOLVED` |
| exact upper midpoint for `1.0` | `UNRESOLVED` |
| exact lower/upper midpoint for smallest normal | `UNRESOLVED` |
| exact lower/upper midpoint for maximum finite | `UNRESOLVED` |
| exact positive zero | `UNRESOLVED` |
| infinity candidate | `INVALID` |
| interval touching/crossing any tested midpoint | `UNRESOLVED` |

These tests validate classifier semantics independently of the MPFR interval evaluator. They do not certify the interval evaluator itself.

## 7. JavaScript reference comparison

`reference_capture.ts` imports the reference source module directly through the existing `tsx` runtime and records:

- Input coordinate bit patterns.
- Degree bit pattern.
- Exact JavaScript `degrees * Math.PI / 180` radian bit pattern.
- Native `rotatePoint` output bit patterns.
- Native `transformLocalPoint` output bit patterns.
- `route45` output point bit patterns.

The Python runner then evaluates MPFR sine/cosine for the exact captured radian bits. This preserves the required separation:

1. Mathematical exact-binary64-input model.
2. JavaScript degree-to-radian binary64 sequence.
3. Native JavaScript trigonometric output.
4. Independent MPFR trigonometric enclosure.
5. Coordinate arithmetic and final translation.
6. Output-cell classification.

The current runner deliberately marks final transform/route output cells `UNRESOLVED` because it does not yet propagate sign-aware MPFR intervals through every coordinate product and addition/subtraction. It does not infer final correctness solely from sine/cosine agreement.

## 8. Executed adversarial corpus

The machine-readable result is `tools/numerical-evidence/vector_results.json`.

Execution summary:

```text
vectorCount    = 13
unresolvedCount = 13
```

Vectors included:

1. zero angle;
2. 45°;
3. 90°;
4. 180°;
5. 270°;
6. negative angle `-31°`;
7. out-of-range angle `1097.25°`;
8. signed-zero coordinates/angle;
9. smallest-subnormal coordinates;
10. maximum-coordinate translation/overflow;
11. `route45` below `EPSILON`;
12. `route45` exactly at `EPSILON`;
13. `route45` above `EPSILON`.

Every executed vector records exact JavaScript input/output bit patterns and the captured radian bit pattern. Every finite-radian vector received an MPFR point enclosure. All final output classifications are unresolved, which is the expected conservative result of the current incomplete coordinate interval propagation—not evidence of a numerical failure.

The route45 vectors remain compatibility observations only. The runner does not treat `route45` as trigonometric evidence.

## 9. Representative observations

The 45° vector captures the same reference behavior established in prior phases:

```text
radians bits: 0x3fe921fb54442d18
rotate x bits: 0xbfe6a09e667f3bc8
rotate y bits: 0x4013cc8a99af5453
```

The quarter-turn vector captures the native sequence rather than an assumed mathematical identity:

```text
radians bits: 0x3ff921fb54442d18
rotate(3,4,90°): x bits 0xc010000000000000
                 y bits 0x4008000000000001
```

The exact `route45` threshold remains strict and non-inclusive:

- below `1e-7`: two points;
- exactly `1e-7`: three points;
- immediately above `1e-7`: three points.

These are compatibility observations from the reference source, not new production behavior.

## 10. Reproducibility

From a clean Python 3.12 environment, with the reference source worktree and `tsx` available:

```bash
python3.12 -m venv /tmp/p24d5-venv
/tmp/p24d5-venv/bin/pip install --requirement tools/numerical-evidence/requirements.txt
PCB_SOURCE_WORKTREE=/home/ubuntu/PCB-Studio-Pro-p2-4-d-1 \
TSX_BIN=/home/ubuntu/PCB-Studio-Pro-p2-4-d-1/node_modules/.bin/tsx \
/tmp/p24d5-venv/bin/python tools/numerical-evidence/run_vectors.py \
  > /tmp/p24d5-results.json
```

The report records the actual tested versions. The `gmpy2` package version is pinned, but a package hash and architecture-specific wheel lock are not yet included. The source project's CI workflows were not modified, so clean CI reproducibility is not yet qualified.

## 11. Remaining gaps

1. Replace the broad non-degenerate `[-1,1]` result with a general MPFR interval evaluator that proves quadrant/range handling, detects extrema with rigorous π bounds, and preserves enclosure for large arguments.
2. Add sign-aware MPFR interval multiplication, addition, and subtraction for `rotatePoint` and `transformLocalPoint`.
3. Use the completed interval propagation to classify final output cells rather than marking all final outputs unresolved.
4. Extend the corpus around every quadrant boundary, adjacent representable angles, range-reduction stress points, normal/subnormal transitions, maximum finite coordinates, and all non-finite combinations.
5. Add explicit overflow midpoint/ties-to-even tests beyond the current conservative maximum-finite handling.
6. Pin package hashes and define a clean CI environment without altering existing project workflows.

## Conclusion

The phase establishes a reusable evidence foundation: exact source-grounded JavaScript capture, MPFR point enclosures for arbitrary finite binary64 radians, conservative all-angle interval bounds, and an exact-rational cell classifier with conservative midpoint semantics. The executed corpus is reproducible and records 13 vectors with 13 unresolved final output cells.

The interval oracle is therefore useful and partially validated, but it is not yet a complete narrow general interval proof system for arbitrary angular intervals or composed coordinate outputs.

**INTERVAL_ORACLE_PARTIALLY_VALIDATED**
