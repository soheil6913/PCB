# PHASE 6.1 — P2.4-D Independent Numerical Proof & Verification Report

## Final verdict

**NOT_READY_FOR_IMPLEMENTATION**

This report records independent evidence gathering only. No source repository file, source test, source branch, pull request, `main` branch, or P2.4-C merge was modified. P2.4-D was not implemented and P2.4-E was not started.

The evidence confirms several design-level properties and supplies reproducible compatibility vectors, but it does not complete the two proof obligations that the accepted design closure report identified: a certified arbitrary-angle trigonometric kernel and a certified rectangle/oval distance evaluator. Those artifacts do not exist in the approved source baselines, and no approximation coefficients or remainder table were supplied for independent proof.

## Scope and references

| Item | Exact reference |
|---|---|
| Approved P2.4-B source baseline | `e567acb883a0f81cb0c64d11f638b5f872511346` |
| P2.4-C compatibility reference | `327fc0479031279b889ea1dd1140a23d4abe442f` |
| Accepted design closure | `PHASE_6_1_P2_4_D_DESIGN_CLOSURE_REPORT.md` |
| Numerical remediation contract | `PHASE_6_1_P2_4_D_NUMERICAL_REMEDIATION_CONTRACT.md` |
| Source repository | `soheil6913/-PCB-Studio-Pro` |
| Documentation repository | `soheil6913/PCB` |

The source commits were inspected through a read-only clone. The accepted P2.4-C remediation changes exactly `shared/engineering.ts` and `shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts`; public signatures for `route45`, `rotatePoint`, `transformLocalPoint`, detailed geometry, wrappers, and validators remain textually present with the same shapes as in P2.4-B.

## Evidence methodology and reproducibility

All experiments were run outside both repositories. The primary evidence generator was:

```text
/tmp/p2d_independent_verify.py
```

It uses Python 3.12.3, `mpmath==1.4.1` at `mp.dps = 160`, Python `Fraction` for exact dyadic IEEE-754 boundaries, and a deterministic heap-based budget scheduler. The script and output were hashed before publication:

```text
87edfaa7cb31d2803f934e68c7492591fe1331a16c27876781e785da838971ab  /tmp/p2d_independent_verify.py
06d342d7a9407265245b609cebe5da67ff05bf943466a6b1d8adcb54960adb1f  /tmp/p2d_independent_verify.out
```

Reproduction command:

```bash
python3 -m pip install --user mpmath==1.4.1
python3 /tmp/p2d_independent_verify.py > /tmp/p2d_independent_verify.out
sha256sum /tmp/p2d_independent_verify.py /tmp/p2d_independent_verify.out
```

`mpmath` is independent of the JavaScript/TypeScript implementation and was used as a high-precision reference, not as evidence that any proposed production kernel is certified. The script is not committed to the documentation repository because the deliverable is restricted to the report.

## 1. Interval trigonometric kernel

### Required claim

The closure design proposed exact binary64 input decomposition, conservative Payne–Hanek-style reduction, dyadic pi bounds, a reduced-domain polynomial, outward-rounded interval Horner evaluation, and an explicit approximation remainder bound.

### Independent evidence

The independent oracle generated fixed degree inputs:

```text
0, 1, 45, 89.99999999999999, 90, 135, 180, 270, 360,
1000000, 1e20, 1e100, -1e100
```

Representative 160-digit reference values include:

| Degrees | Independent reference sin | Independent reference cos |
|---:|---:|---:|
| `1` | `0.0174524064372835128194189785163161924722527203071396426836...` | `0.9998476951563912391570115588139148516927403105831859396583...` |
| `45` | `0.7071067811865475244008443621048490392848359376884740365883...` | same as sine |
| `89.99999999999999` | `0.9999999999999999999999999999999692415009895639169844636927...` | `0.0000000000000002480262043028360461851904643266088355166964...` |
| `1e100` | `0.898794046299166992782676695785354929973973...` | `0.438371146789077417452734540658265739062755...` |
| `-1e100` | negative of the positive-angle sine | same cosine as the positive angle |

The source baselines still use `Math.PI`, `Math.sin`, and `Math.cos` directly in `rotatePoint`, `transformLocalPoint`, rectangle corners, and common-axis oval calculations. No interval coefficient table, pi enclosure, polynomial, range-reduction proof, directed-rounding implementation, or remainder bound is present at either approved source SHA.

### Status

**BLOCKED.** The oracle vectors are reproducible, but there is no candidate kernel, coefficient set, reduction constant set, or remainder proof to evaluate. A one-ULP widening around `Math.sin`/`Math.cos` would not satisfy the requested proof and was not treated as evidence.

### Limitation

The mpmath vectors demonstrate reference generation only. They do not certify an implementation, prove correct rounding, or establish that a future TypeScript interval kernel encloses every input. A future proof package must provide the exact coefficients, domains, pi bounds, reduction error, outward-rounding primitives, and a complete independent corpus comparison.

## 2. Independent high-precision oracle vectors

### Required claim

Every claimed `VALID` arbitrary-angle coefficient or transformed coordinate must be checked against an independent high-precision reference.

### Evidence

The fixed corpus above was evaluated at 160 decimal digits. Exact special-angle behavior was not forced to zero: for example, the independent reference for 90 degrees produced a magnitude below `5e-162` for cosine rather than treating an irrational/transcendental computation as an exact binary64 identity. This is the correct conservative reference posture for a proof review.

The baseline cancellation fixture is also reproducible through the source formula:

```text
rotatePoint({x: Number.MAX_VALUE, y: Number.MAX_VALUE}, 45)
=> { x: 1.99584030953472e+292, y: Infinity }
```

The high-precision mathematical expectation for the x component is zero for equal inputs at exactly 45 degrees, while the source result emits a large finite residual and a non-finite y component. This establishes an adversarial compatibility fixture, not a proposed remediation result.

### Status

**PASS — oracle generation.** The reference vectors and cancellation input are reproducible and independent of the TypeScript implementation.

**BLOCKED — implementation comparison.** No candidate interval kernel or checked transform exists in the approved source baselines, so enclosure containment and `VALID`/`INDETERMINATE` classifications cannot be tested.

## 3. IEEE-754 output-cell verification

### Required claim

A transformed coordinate may be `VALID` only when its complete outward enclosure is contained in one round-to-nearest-even binary64 output cell, with explicit handling for zero, subnormals, ties, binade boundaries, and overflow.

### Independent exact reference

The evidence generator decomposes finite binary64 values into exact signed dyadics and computes adjacent-value midpoints as exact rational numbers. It evaluated:

- positive zero and negative zero;
- the least positive subnormal, bit pattern `0x0000000000000001`;
- the largest subnormal, `0x000fffffffffffff`;
- the least normal, `0x0010000000000000`;
- `1.0` and `2.0` at binade boundaries;
- the largest finite value, `0x7fefffffffffffff`.

Representative exact cells:

| Candidate | Exact lower boundary | Exact upper boundary |
|---|---|---|
| `1.0` | `18014398509481983/18014398509481984` | `9007199254740993/9007199254740992` |
| `2.0` | `18014398509481983/9007199254740992` | `9007199254740993/4503599627370496` |
| least subnormal | `1/2 * 2^-1074` | `3/2 * 2^-1074` |
| zero cell used by the reference | `0` | `1/2 * 2^-1074` |

The exact script output contains the full rational boundaries, including the subnormal/normal transition and largest-finite boundary. The zero cell requires a separately documented signed-zero policy; the reference calculation intentionally does not infer a production policy from the binary representation alone.

### Status

**PASS — mathematical reference construction.** Exact dyadic neighbor and midpoint construction is reproducible for the listed boundary cases.

**BLOCKED — production output-cell implementation.** No `nextUp`/`nextDown`, tie-to-even resolver, interval candidate selection, or overflow policy exists in the approved source baselines. Therefore no claim can be made that a future TypeScript implementation satisfies the output-cell criterion.

### Explicit unresolved tests

The following remain mandatory before implementation review:

1. exact halfway values with even and odd lower significands;
2. negative subnormal and negative-zero cells;
3. enclosure strictly inside a cell;
4. enclosure narrower than one ULP but crossing a cell boundary;
5. enclosure crossing the largest-finite overflow boundary;
6. signed-zero output policy and downstream geometric equality behavior.

## 4. Rectangle/oval resource-budget evaluation

### Required claim

The proposed deterministic evaluator uses `4096` cells, `32768` interval evaluations, and subdivision depth `32`; exhaustion returns `INDETERMINATE` with stable counters and reason.

### Isolated prototype

A standalone deterministic heap scheduler was executed with the proposed limits. Each cell consumes eight interval-evaluation slots; subdivision uses four children; the queue tie-breaker is a monotonic sequence number. It is intentionally only a scheduler prototype, not a certified rectangle/oval distance solver: it does not claim geometric lower/upper bounds or prove contact/separation.

Observed output:

```text
ordinary case:
state=INDETERMINATE
cells=4096 evals=32768 depth=6 reason=certified-distance-budget-exhausted maxq=12286

adversarial case:
state=INDETERMINATE
cells=4096 evals=32768 depth=6 reason=certified-distance-budget-exhausted maxq=12286
```

The measured elapsed times were approximately `0.01152 s` and `0.01039 s` in this Python prototype. These timings are not performance claims for TypeScript or browser execution and must not be used as a production benchmark.

### Status

**PASS — counter and exhaustion semantics of the proposed scheduler shape.** The prototype deterministically reaches the exact cell and evaluation limits and returns the specified fail-closed state/reason.

**BLOCKED — budget adequacy and geometric proof.** The prototype does not implement certified rectangle/oval interval bounds, broad-phase paths, queue priority by geometric uncertainty, or actual shape-distance cases. It therefore cannot establish that the proposed budget is sufficient for ordinary boards, near tangencies, tiny-scale gaps, or rotated rectangle/oval pairs.

### Required next evidence

A future isolated benchmark must implement the actual interval primitives and run fixed cases for exact contact, overlap, positive separation, near tangency, tiny-scale gaps, high curvature, overflow, and repeated exhaustion. It must report counters and distributions for a representative 10,000-pair ordinary board plus adversarial cases. No benchmark result is claimed here beyond the scheduler output above.

## 5. Exact legacy compatibility fixtures

These fixtures are derived from the exact P2.4-B source formulas and were independently re-evaluated in the standalone script.

### `route45`

| Input | Baseline expected output |
|---|---|
| `start=(0,0), end=(80,20)` | `[(0,0),(20,0),(80,20)]` |
| `start=(0,0), end=(20,80)` | `[(0,0),(20,0),(20,80)]` |
| `start=(10,10), end=(10,50)` | `[(10,10),(10,50)]` |
| `start=(10,10), end=(50,10)` | `[(10,10),(50,10)]` |
| `start=(0,0), end=(40,40)` | `[(0,0),(40,40)]` |
| `start=(5,5), end=(5,5)` | `[(5,5),(5,5)]` — existing duplicate endpoint behavior must be explicitly decided before implementation |
| `start=(-1e308,0), end=(1e308,10)` | `[(-1e308,0),(-1e308,0),(1e308,10)]` — confirmed duplicate-waypoint defect |

The proposed closure decision is therefore testable: preserve ordinary outputs exactly, eliminate the extreme duplicate through the checked path, and lock the legacy finite `NON_REPRESENTABLE` wrapper behavior before source changes. The invalid-input behavior (`[]`) remains a proposed contract decision, not an existing baseline behavior, and requires an explicit compatibility fixture.

**Status: PASS for fixture extraction; BLOCKED for implementation compatibility.** No source implementation was changed to test the proposed checked wrapper.

### `rotatePoint`

| Input | P2.4-B baseline expected output |
|---|---|
| `{1,0}, 0°` | `{1,0}` |
| `{1,0}, 90°` | `{6.123233995736766e-17,1}` |
| `{1,0}, 180°` | `{-1,1.2246467991473532e-16}` |
| `{1,0}, 270°` | `{-1.8369701987210297e-16,-1}` |
| `{10,20}, 45°` | `{-7.071067811865474,21.213203435596427}` |
| `{1e200,1e200}, 45°` | `{8.498207885068274e183,1.4142135623730949e200}` |
| `{MAX_VALUE,MAX_VALUE},45°` | `{1.99584030953472e292,Infinity}` |

The ordinary fixtures define compatibility outputs that a checked transform must not silently alter unless the design explicitly distinguishes public best-effort output from internal checked output. The final fixture demonstrates why the public helper cannot be used as proof-bearing geometry.

**Status: PASS for fixture extraction; BLOCKED for checked/public divergence review.** No internal checked transform exists to compare against these vectors.

## 6. Source-grounded P2.4-C compatibility review

### Evidence

The source repository was inspected at both exact references. The accepted remediation commit `327fc0479031279b889ea1dd1140a23d4abe442f` changes exactly:

```text
shared/engineering.ts
shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts
```

A read-only export/signature comparison found the same public geometry and validation exports at P2.4-B and P2.4-C, including:

```text
rotatePoint(point, degrees)
transformLocalPoint(origin, local, rotation = 0)
route45(start, end)
segmentsIntersect(...)
padToPadDistanceDetailed(...)
padToPadDistance(...)
validateSchematic(...)
validatePcb(...)
```

The P2.4-C source retains the public `Math.sin`/`Math.cos` rotation path and the strict rectangle/oval helpers with fixed absolute `1e-12` predicates. Its accepted changes add explicit orientation uncertainty, exact finite-input dyadic fallback for near-collinear predicates, scaled threshold handling, and localized topology uncertainty. They do not provide the P2.4-D trig kernel, output-cell logic, or certified rectangle/oval budget evaluator.

The accepted P2.4-C report and source tests establish these compatibility constraints:

- no false union through indeterminate schematic relationships;
- localized rather than global topology suppression;
- overflowed public scalar distance may remain `NaN`;
- detailed geometry uncertainty remains `INDETERMINATE`;
- numeric wrappers retain `GeometryCalculationError` behavior;
- GJK budget and exhaustion semantics remain unchanged;
- no coordinate ceiling, clamping, or NaN-to-zero conversion.

### Status

**PASS — source-grounded compatibility boundary.** The exact source refs and changed-file scope are independently verifiable, and the P2.4-D design can be reviewed as an adapter around existing public signatures and P2.4-C state semantics.

**BLOCKED — integrated behavioral proof.** The user prohibited merging P2.4-C and prohibited source/test changes, so no combined runtime test can be run here. Later implementation review must compare both source targets without changing either reference and must verify localized uncertainty, wrapper errors, GJK exhaustion, and DRC fail-closed behavior together.

## Evidence status matrix

| Investigation | Reproducible evidence | Independent reference | Status |
|---|---|---|---|
| Trig oracle vectors | Fixed 13-angle, 160-digit mpmath corpus | mpmath 1.4.1, independent of JS | PASS for oracle; BLOCKED for kernel proof |
| Trig coefficients/range reduction | No candidate artifacts at either source SHA | None supplied | BLOCKED |
| IEEE-754 output cells | Exact dyadic neighbors/midpoints for zero, subnormal, normal, binade, max finite | Python `Fraction` and binary64 bit decomposition | PASS for reference; BLOCKED for production implementation |
| Rectangle/oval budget | Deterministic scheduler reaches `4096`/`32768` | Fixed counters and stable heap sequence | PASS for scheduler; BLOCKED for geometric adequacy |
| Legacy `route45` | Exact baseline formula vectors, including duplicate extreme waypoint | P2.4-B source at exact SHA | PASS for fixture extraction; BLOCKED for checked implementation |
| Public `rotatePoint` | Exact ordinary and cancellation fixtures | P2.4-B source and independent Python evaluation | PASS for fixture extraction; BLOCKED for checked implementation |
| P2.4-C compatibility | Exact refs, export comparison, changed-file scope | Git object identities and source diff | PASS for boundary review; BLOCKED for combined runtime proof |

## Remaining blockers

1. Supply the exact trig polynomial coefficients, reduced-domain bounds, pi enclosure, range-reduction constants, outward-rounding method, and approximation remainder proof.
2. Run the fixed high-precision corpus against that candidate kernel and demonstrate that every `VALID` interval contains the independent reference.
3. Supply and review the output-cell implementation, including negative zero, negative subnormals, halfway ties, binade boundaries, and largest-finite overflow.
4. Implement the actual certified rectangle/oval interval evaluator in an isolated prototype and benchmark it against fixed contact, overlap, separation, tangency, tiny-scale, rotated, and overflow cases; approve or revise the budget from measured evidence.
5. Lock the legacy `route45` invalid-input and finite-`NON_REPRESENTABLE` behavior in compatibility fixtures before source implementation.
6. Lock ordinary public `rotatePoint` outputs and define the exact public-versus-checked divergence policy.
7. Perform a later combined P2.4-B/P2.4-C compatibility run without merging or modifying either authoritative source reference.

## Final disposition

The independent oracle and reference-cell evidence are complete for the stated fixed vectors. The resource experiment verifies only deterministic scheduler exhaustion, not geometric proof or budget adequacy. The accepted source baselines contain no candidate implementation against which the decisive proof claims can be checked.

Therefore the final verdict is:

**NOT_READY_FOR_IMPLEMENTATION**

This verdict is not implementation authorization. No source or test modification, source branch, merge, pull request, or P2.4-E work is authorized by this report.
