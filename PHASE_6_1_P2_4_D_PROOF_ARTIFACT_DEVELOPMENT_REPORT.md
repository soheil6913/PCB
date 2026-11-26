# PHASE 6.1 — P2.4-D Proof Artifact Development Report

## Final verdict

**NOT_READY_FOR_IMPLEMENTATION**

This report documents isolated proof-artifact prototypes and read-only compatibility review. No production source, existing source test, public API, source branch, pull request, `main` branch, or P2.4-C merge was modified. All experimental code remained outside the production and documentation repositories.

The work produced useful executable evidence, but the essential mathematical obligations are not all satisfied. In particular, the trigonometric prototype is empirically enclosing but lacks a complete whole-domain binary64 proof; the rectangle/oval prototype performs real conservative subdivision but lacks a formal machine-verified interval arithmetic basis and the required 10,000-pair benchmark; and the public/checked compatibility policy still requires fixture locking.

## Authoritative references

| Item | Reference |
|---|---|
| P2.4-B source baseline | `e567acb883a0f81cb0c64d11f638b5f872511346` |
| P2.4-C compatibility reference | `327fc0479031279b889ea1dd1140a23d4abe442f` |
| Design closure report | `54929160cfc0347d690101501886c287dc34a7ed` |
| Independent verification report | `f296b18c6f28e675a0f1fd3c514730ab1de1ba80` |
| Source repository | `soheil6913/-PCB-Studio-Pro` |
| Documentation repository | `soheil6913/PCB` |

The exact source refs were independently resolved in Workstream E. The P2.4-C remediation descends from P2.4-B through the accepted P2.4-C base; it is not necessary or authorized to merge it for this review.

## Executed artifact inventory

The following isolated artifacts were executed by independent workstreams. They were not copied into either repository:

| Artifact | Execution | Disposition |
|---|---|---|
| Trig prototype | `python3 /tmp/p24d_prototype.py` | Executed; blocked as a whole-domain proof |
| Geometry prototype | `python3 /tmp/geom_proto.py \| tee /tmp/geom_results_final.json` | Executed; complete with limitations |
| IEEE-754 reference | `python3 /tmp/ieee754_cells.py > /tmp/ieee754_cells_results.json` | Executed; 24/24 mathematical reference cases passed |
| Prior oracle generator | `python3 /tmp/p2d_independent_verify.py > /tmp/p2d_independent_verify.out` | Previously executed and published in the independent-verification report |
| Source compatibility review | read-only `git clone`, `git fetch`, `git show`, `git diff`, `git grep` | Executed; no repository modifications |

No result below is claimed unless the corresponding workstream executed the relevant prototype or read-only command.

## Workstream A — interval trigonometric kernel

### Prototype architecture

The isolated prototype exercised:

- exact binary64 decomposition, including signed zero and subnormals;
- a dyadic pi enclosure with `N=180`;
- Taylor sine through degree 15 with remainder `|r|^17 / 17!`;
- Taylor cosine through degree 14 with remainder `|r|^16 / 16!`;
- mpmath interval endpoints for the experimental outward enclosure;
- quadrant reduction and reconstruction;
- independent 120-digit mpmath truth values.

The prototype used the following pi enclosure:

```text
pi_lo = 3.141592653589793238462643383279502884197169399375105820901020035
pi_hi = 3.1415926535897932384626433832795028841971693993751058215535504818
width = approximately 6.5253045e-55
```

### Executed evidence

Fixed adversarial inputs included:

```text
1.5707963267948966
nextafter(pi/2, +infinity)
nextafter(pi/2, -infinity)
pi-nearest binary64 value
nextafter(pi, +infinity)
2^53
-2^53
1000000.0
5e-324
2.2250738585072014e-308
```

Observed examples:

- `1.5707963267948966`: reduced quadrant `1`, residual approximately `-6.1232339957367658861e-17`, truth `1.0`, enclosure contained truth.
- `nextafter(pi/2,+inf)`: enclosure contained the independent truth.
- `nextafter(pi/2,-inf)`: enclosure contained the independent truth.
- `2^53`: interval approximately `[-0.84892596481465543157,-0.84892596481465443237]`, containing the independent truth.
- `1000000.0`: interval approximately `[-0.34999350217129321372,-0.34999350217129265861]`, containing the independent truth.
- The fixed sample contained `20,001` points over `[-1,000,000,1,000,000]`; `sample_bad_count=0`; maximum interval width was approximately `2.9976e-15`.

### Status

**BLOCKED.** The prototype completed successfully and its finite sample contained the independent reference values, but this is not a certification of the target design.

The exact missing proof obligations are:

1. a proof that the chosen pi representation and quotient computation select the correct quadrant for every finite binary64 angle, including values near `2^1024` and quotient sizes of roughly `2^1024`;
2. a rigorously bounded residual after range reduction for the complete finite input domain;
3. an operation-level binary64 outward-rounding budget covering coefficient storage, multiply/add or fused multiply-add behavior, subnormals, signed zero, overflow, and underflow;
4. a proof that the stated polynomial remainder applies to the actual reduced interval produced by the binary64 implementation, not only to the mpmath prototype;
5. a defined NaN/infinity input policy.

The prototype therefore demonstrates an executable research direction, not a certified kernel.

## Workstream B — certified rectangle/oval distance

### Prototype architecture

The isolated prototype was a real interval/subdivision evaluator rather than a scheduler-only test. It represented rectangle perimeters as four parametric line edges and ovals as rotated ellipse parameterizations. It used:

- conservative AABB lower-distance bounds;
- sampled upper witnesses;
- rectangle edge-breakpoint handling;
- oval endpoint/cardinal-extrema handling plus derivative-based Lipschitz inflation;
- deterministic priority ordering by lower bound, depth, and insertion order;
- deterministic splitting of the longer parameter span, with rectangle-parameter tie preference;
- limits `MAX_CERTIFIED_CELLS=4096`, `MAX_INTERVAL_EVALUATIONS=32768`, `MAX_SUBDIVISION_DEPTH=32`.

### Executed cases and results

| Case | Classification | Cells | Interval evaluations | Other evidence |
|---|---|---:|---:|---|
| Ordinary separated rectangles | `SEPARATED` | 1 | 1 | lower bound `3` |
| Ordinary overlapping rectangles | `OVERLAP` | 4096 | 8193 | interior containment witness; max depth 23 |
| Exact tangent | `CONTACT` | 4096 | 8193 | explicit checked boundary witness; max depth 23 |
| Near tangent, gap `1e-10` | `SEPARATED` | 1 | 1 | lower bound approximately `1.000000082740371e-10` |
| Tiny separated geometry | `SEPARATED` | 1 | 1 | half-size `1e-12`, center separation `1e-6` |
| Huge separated geometry | `SEPARATED` | 1 | 1 | half-size `1e150`, lower bound approximately `1e150` |
| Rotated rectangles | `INDETERMINATE` | 177 | 353 | max depth 32; best upper approximately `9.243240536568016e-6` |
| Rectangle/oval | `SEPARATED` | 119 | 119 | max depth 8; best upper approximately `0.557656332048742` |
| Oval/oval | `OVERLAP` | 1843 | 3685 | containment witness; max depth 32 |
| Degenerate rectangle | `NON_REPRESENTABLE` | 0 | 0 | zero half-size rejected |
| Degenerate oval | `NON_REPRESENTABLE` | 0 | 0 | zero radius rejected |
| NaN input | `NON_REPRESENTABLE` | 0 after finite gate | attempted finite check only | no geometric result emitted |

No case exceeded the interval-evaluation limit. Overlap and tangent cases reached the 4096-cell ceiling and returned only where the explicit witness justified the classification; unresolved rotated geometry returned `INDETERMINATE`.

### Status and limitations

**COMPLETE_WITH_LIMITATIONS.** This is materially stronger than the earlier scheduler-only prototype, but it is not sufficient for implementation readiness.

The prototype has these limitations:

- Contact is certified only for the fixed exact-tangent construction with an explicit checked witness; generic contact remains conservatively unresolved.
- Overlap is certified only when the implemented interior containment witness succeeds; boundary-crossing overlap may remain `INDETERMINATE`.
- Oval enclosure uses floating-point arithmetic and derivative inflation, not a machine-verified outward-rounded interval package.
- The prototype does not expose a distinct `CONVERGED` state; certified separation returns `SEPARATED`, while exhaustion returns `INDETERMINATE`.
- No 10,000-pair representative benchmark was run. Consequently, there is no valid dataset/seed/runtime distribution, median, p95, p99, allocation, or indeterminate-rate claim for the required benchmark.

The proposed budget is therefore **not proven adequate**. The cases demonstrate deterministic behavior and useful early separation, but the budget must remain a design parameter pending a sound interval basis and the required benchmark.

## Workstream C — IEEE-754 output-cell verification

### Reference model

The isolated reference uses exact integer/rational arithmetic with binary64 precision `p=53`, normal exponent range `[-1022,1023]`, and exact subnormal quantum `2^-1074`. It tests exact round-to-nearest, ties-to-even results and exact enclosure-cell crossing.

### Executed evidence

The harness ran **24/24 cases with zero failures**, including:

- positive and negative subnormals;
- smallest positive and negative normals;
- largest subnormal;
- adjacent values around `1.0` and binade boundaries;
- exact ties with even and odd lower significands, including negative counterparts;
- largest finite positive and negative values;
- overflow boundary values;
- enclosures strictly inside a cell;
- enclosures crossing the `1.0`/next-value cell boundary;
- an enclosure strictly inside the least-subnormal output cell.

Representative exact results:

```text
+2^-1074 -> bits 0x0000000000000001
-2^-1074 -> bits 0x8000000000000001
+2^-1022 -> bits 0x0010000000000000
-2^-1022 -> bits 0x8010000000000000
largest +subnormal -> bits 0x000fffffffffffff
1.0 -> bits 0x3ff0000000000000
1 + 2^-52 -> bits 0x3ff0000000000001
largest finite -> bits 0x7fefffffffffffff
negative largest finite -> bits 0xffefffffffffffff
```

The even tie at `1.0` rounded to `0x3ff0000000000000`; the odd-lower-significand tie rounded to `0x3ff0000000000002`. The crossing enclosure had endpoints rounding to `0x3ff0000000000000` and `0x3ff0000000000001`, and was correctly rejected as a one-cell enclosure.

### Status

**PASS — mathematical reference.** The exact dyadic reference and 24 boundary cases executed successfully.

**BLOCKED — production integration.** The reference deliberately does not infer a signed-zero policy from rational zero, and no production TypeScript output-cell implementation exists at the authoritative source refs. Overflow policy must also be aligned with the future transform contract.

## Workstream D — compatibility fixtures

The parent read-only review and the prior independent-verification artifact established the exact P2.4-B source formulas and baseline vectors. The isolated Workstream D agent could not mount the source repository and therefore did not independently re-run source extraction; its formula-qualified Node results are not treated as baseline proof.

### Locked P2.4-B fixture vectors from source-grounded review

`route45` ordinary outputs:

```text
(0,0)->(80,20)  => [(0,0),(20,0),(80,20)]
(0,0)->(20,80)  => [(0,0),(20,0),(20,80)]
(10,10)->(10,50) => [(10,10),(10,50)]
(10,10)->(50,10) => [(10,10),(50,10)]
(0,0)->(40,40)  => [(0,0),(40,40)]
```

The finite extreme fixture `(-1e308,0)->(1e308,10)` produces a duplicate waypoint under the baseline formula:

```text
[(-1e308,0),(-1e308,0),(1e308,10)]
```

This confirms the defect targeted by the checked route design. Invalid/non-finite inputs and the finite `NON_REPRESENTABLE` legacy fallback remain proposed policy cases and are not baseline-established.

`rotatePoint` ordinary and adversarial baseline vectors include:

```text
{1,0}, 90°  => {6.123233995736766e-17,1}
{10,20},45° => {-7.071067811865474,21.213203435596427}
{MAX_VALUE,MAX_VALUE},45°
  => {1.99584030953472e292,Infinity}
```

### Status

**PASS — ordinary fixture extraction and extreme-defect reproduction from the source-grounded parent review.**

**BLOCKED — checked/public compatibility closure.** The proposed `route45Checked` and checked transform do not exist in production, so public-versus-checked divergence, invalid-input behavior, transactional client behavior, and exact fallback presentation cannot yet be executed. The fixtures must be committed as new tests only during a separately authorized implementation review; this report does not modify tests.

## Workstream E — P2.4-B/P2.4-C compatibility review

### Executed source review

The exact refs were cloned and inspected read-only. Findings:

- P2.4-B `e567acb...` changes exactly `GEOMETRY_API_CONTRACT.md`, `shared/engineering.ts`, and `shared/phase6-1-p2-4-b-geometry-api-contract.test.ts` relative to its parent.
- P2.4-C remediation `327fc047...` changes exactly `shared/engineering.ts` and `shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts` relative to its parent.
- P2.4-C descends from the P2.4-B line through the accepted P2.4-C base; no merge is authorized or needed for source-reference comparison.
- Public exports and signatures for `route45`, `rotatePoint`, `transformLocalPoint`, scalar geometry, detailed geometry, wrappers, validators, and rule entry points remain present and unchanged in shape.
- P2.4-B keeps numeric wrappers fail-closed through `GeometryCalculationError`, and detailed APIs classify indeterminate calculations explicitly.
- P2.4-C adds exact finite-input orientation fallback, scaled threshold handling, and localized affected-wire/pin/net uncertainty without global topology suppression.
- GJK exhaustion, DRC fail-closed behavior, no-coordinate-ceiling policy, and no-NaN-to-zero policy remain compatibility constraints.

### New compatibility risk requiring review

Static inspection identified a possible checked-API boundary inconsistency in the P2.4-B options path: the structural runtime-options predicate appears to allow numeric `NaN`, `Infinity`, zero, negative, and fractional values to proceed far enough that `gjkWithinDistance` reports an “invalid iteration budget” path rather than the documented “invalid geometry options” classification. The committed focused tests exercise some later-path values but do not establish complete coverage for all of `NaN`, `Infinity`, and negative values.

This is a source-grounded review finding, not a newly executed runtime regression. It must be resolved or explicitly accepted before any P2.4-D checked geometry adapter is implemented.

### Status

**PASS — static compatibility boundary review.** Exact refs, ancestry, changed-file scopes, public signatures, and P2.4-C uncertainty constraints were verified without source modification.

**BLOCKED — combined runtime proof.** The authorization prohibits merging or changing either source reference; therefore no combined-tree runtime test was performed.

## Consolidated evidence matrix

| Area | Executed evidence | Status |
|---|---|---|
| Trig decomposition/reduction prototype | Fixed adversarial vectors and 20,001-point sample | Empirical pass; whole-domain proof BLOCKED |
| Trig coefficient/remainder proof | Taylor coefficients and mpmath intervals in prototype | BLOCKED for binary64 implementation proof |
| Rectangle/oval evaluator | Real subdivision prototype and fixed geometry cases | Complete with limitations; formal soundness/10k benchmark BLOCKED |
| IEEE-754 reference | 24/24 exact dyadic cases | PASS for mathematical reference; production integration BLOCKED |
| route45/rotatePoint fixtures | Source-grounded ordinary and extreme vectors | PASS for extraction; checked API behavior BLOCKED |
| P2.4-B/P2.4-C review | Exact refs, ancestry, diff scopes, exports, call-site/static behavior | PASS static; combined runtime BLOCKED |

## Remaining blockers

1. Complete the whole-domain binary64 proof for range reduction, quotient selection, residual bounds, polynomial evaluation, and quadrant reconstruction.
2. Replace mpmath-dependent experimental interval operations with a documented binary64 outward-rounding implementation or another independently certified arithmetic basis.
3. Resolve signed-zero and overflow semantics in the production output-cell contract.
4. Provide a machine-checkable or otherwise independently reviewed proof that rectangle/oval lower and upper bounds are conservative for all supported parameter cells.
5. Add the required deterministic 10,000-pair benchmark with dataset/seed, runtime environment, classification distribution, indeterminate rate, evaluation/subdivision counts, median, p95, p99, and allocation observations.
6. Define and execute a distinct `CONVERGED` distance-interval state where required; do not conflate early separation with distance convergence.
7. Lock invalid/non-finite route45 behavior, finite `NON_REPRESENTABLE` legacy behavior, public `rotatePoint` ordinary outputs, and checked/public divergence semantics.
8. Review the possible P2.4-B geometry-options classification inconsistency for `NaN`, `Infinity`, zero, negative, and fractional iteration values.
9. Perform combined P2.4-B/P2.4-C runtime compatibility verification later without merging or modifying authoritative refs.

## Final disposition

The proof-artifact phase produced executed, reproducible evidence and narrowed the blockers. It did not establish all essential mathematical and experimental obligations required by the mission. A prototype passing sampled oracle cases is not sufficient, and the required benchmark and whole-domain proofs remain incomplete.

Therefore:

**NOT_READY_FOR_IMPLEMENTATION**

This verdict is not implementation authorization. No production source/test modification, source branch, merge, pull request, or P2.4-E work is authorized by this report.
