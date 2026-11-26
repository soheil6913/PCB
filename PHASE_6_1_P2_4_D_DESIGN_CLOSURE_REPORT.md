# PHASE 6.1 — P2.4-D Design Closure & Adversarial Review

## Executive verdict

**NOT_READY_FOR_IMPLEMENTATION**

The five open questions in the published P2.4-D numerical remediation contract can be resolved as an implementation design, but the design is not yet ready to authorize source implementation. Two implementation-proof obligations remain material blockers: the software interval trigonometric kernel must be independently reviewed against its approximation/remainder proof, and the certified rectangle/oval evaluator must be validated against an independent oracle at the specified resource limits.

This verdict does **not** authorize implementation. It means that the design decisions below are sufficiently specific for a separate implementation-readiness review, but implementation must wait for approval of the stated proof artifacts and acceptance vectors.

The review is based on:

- exact P2.4-B baseline: `e567acb883a0f81cb0c64d11f638b5f872511346`;
- accepted P2.4-C remediation compatibility target: `327fc0479031279b889ea1dd1140a23d4abe442f`;
- published contract: `PHASE_6_1_P2_4_D_NUMERICAL_REMEDIATION_CONTRACT.md`;
- P2.4-B source observations in `shared/engineering.ts`, including `route45`, `rotatePoint`, `transformLocalPoint`, strict rectangle predicates, GJK, and `padToPadDistanceDetailed`.

No source or test file is modified by this review. P2.4-C is not merged or assumed present.

## Scope and adversarial method

This is a design-only review. Each decision is evaluated against:

- mathematical assumptions;
- IEEE-754 failure modes;
- JavaScript/TypeScript feasibility;
- dependency and bundle-size consequences;
- ordinary PCB performance;
- adversarial and boundary examples;
- executable acceptance criteria.

No claim below treats the ECMAScript `Math.sin` or `Math.cos` accuracy as a portable certification. Where a proof is required, the proposed implementation must provide a bounded interval or return `INDETERMINATE`.

## Resolution 1 — deterministic public `route45` behavior

### Decision

Keep the existing public signature and define two layers:

```text
route45(start, end): Point[]                 // legacy compatibility wrapper
route45Checked(start, end): RouteResult     // internal authoritative contract
```

For finite endpoints where a valid route45 waypoint cannot be represented, `route45Checked` returns:

```text
{ state: "NON_REPRESENTABLE", start, end, reason }
```

The legacy `route45` wrapper returns exactly `[start, end]` for this state. It does not return a duplicate waypoint, does not throw, and does not claim that the returned two-point polyline satisfies the route45 invariant. This is a deterministic endpoint-only compatibility fallback, not a route45 proof.

For invalid/non-finite input, `route45Checked` returns `INVALID`; the legacy wrapper returns `[]` and creates no geometry. This makes malformed input distinguishable internally while retaining a total array-returning public function. The invalid-input behavior must be locked by a new compatibility test before implementation.

The client route creator must call `route45Checked`, not infer validity from the public array. On `NON_REPRESENTABLE`, it may offer a separately labelled direct-route operation only if the direct segment itself is certified finite and representable for the downstream PCB model. Otherwise it creates no track. The fallback must never be displayed, persisted, or described as an orthogonal/45-degree route.

### Mathematical assumptions

The ordinary route convention is:

```text
S = (sx, sy), E = (ex, ey)
dx = ex - sx, dy = ey - sy
L = min(abs(dx), abs(dy))
M = (sx + sign(dx)L, sy)
```

A valid non-axis route requires finite, exact endpoint preservation, a finite waypoint, no consecutive duplicate points, a horizontal first segment, and a diagonal second segment. Raw subtraction is not assumed representable merely because both endpoints are finite.

### IEEE-754 failure modes

- `ex - sx` may overflow to `Infinity` for opposite-sign finite endpoints.
- `sx + L` may round back to `sx`, producing a duplicate waypoint.
- A finite mathematical segment length may not be representable as a binary64 scalar.
- `-0` can cause sign-sensitive construction differences unless normalized for route decisions.
- Endpoint equality must use represented coordinate equality, not an epsilon.

### TypeScript feasibility

The checked result is an internal discriminated union. The public wrapper can be implemented without changing the exported signature. The result must be validated again by the client immediately before track creation. No new runtime dependency is required.

### Performance and compatibility

Ordinary board coordinates take a constant-time fast path and produce the existing two- or three-point shape and ordering. The extra representability checks are a few finite checks and recomputed segment invariants. Extreme values take the failure path rather than entering downstream geometry.

### Adversarial examples

1. `(-Number.MAX_VALUE,0)` to `(Number.MAX_VALUE,10)` must produce checked `NON_REPRESENTABLE` and legacy `[S,E]`, never `[S,S,E]`.
2. Equal endpoints must produce a checked zero-segment route and no track.
3. A route whose waypoint rounds to the start must be rejected even when all endpoint values are finite.
4. A direct fallback with finite endpoint coordinates but an unrepresentable derived delta must not create a track.
5. Horizontal and vertical routes must not pass through the non-axis waypoint formula.

### Executable acceptance criteria

- Existing ordinary route vectors have identical point count, order, and coordinate values.
- Every `VALID` checked route passes a structural invariant checker.
- No `VALID` result contains a non-finite coordinate or consecutive duplicate.
- The opposite-`MAX_VALUE` reproduction is `NON_REPRESENTABLE` and creates no route45 track.
- Legacy `route45` returns `[start,end]` for finite unrepresentable endpoints and `[]` for invalid input.
- Client integration is transactional: failure of one checked segment appends no partial route.

## Resolution 2 — certified arbitrary-angle sine/cosine coefficients

### Decision

Do not use ECMAScript `Math.sin`/`Math.cos` as a certified provider. The selected design is a small, dependency-free software interval trigonometric kernel with:

1. exact binary64 input decomposition;
2. conservative Payne–Hanek-style range reduction using fixed dyadic bounds for pi and a BigInt-backed quotient where necessary;
3. a fixed, documented minimax polynomial for sine and cosine on a reduced interval such as `[-pi/4, pi/4]`;
4. dyadic interval Horner evaluation with outward rounding;
5. a separately documented approximation remainder bound for each polynomial and reduction step;
6. quadrant reconstruction using exact sign/swap operations;
7. `INDETERMINATE` when range reduction or the interval result crosses a required branch boundary.

The kernel returns intervals `[sin_lo,sin_hi]` and `[cos_lo,cos_hi]`; it does not return an unsupported statement such as “Math.sin is correctly rounded.”

The polynomial coefficients and remainder bound must be generated offline from a high-precision reference, then independently checked by interval arithmetic over the complete reduced domain. The generated constants and proof table are implementation artifacts requiring review; this report does not claim that the proof has already been performed.

A correctly-rounded external library or WASM provider may replace this kernel only if its license, browser/runtime support, accuracy contract, and independent oracle evidence are supplied. A normal npm math package without an explicit certified error contract is not an acceptable substitute.

### Mathematical assumptions

- The input angle is a finite binary64 value representing degrees or radians according to the existing API.
- A finite angle can be represented exactly as a dyadic rational, but its product with an irrational pi is not exact.
- A bounded pi interval and exact integer quotient can establish a safe reduced interval unless the reduction interval straddles a quadrant boundary.
- Polynomial approximation error can be bounded by a published remainder bound over the reduced interval.

### IEEE-754 failure modes

- Multiplying a huge angle by `pi/180` can lose quadrant information.
- Naive `% 360` is unreliable for large magnitudes.
- A reduced interval that crosses `0`, `pi/4`, or a quadrant boundary cannot safely be assigned one sign or coefficient branch.
- Polynomial evaluation can overflow or underflow if range reduction fails.
- Directed rounding is not a JavaScript primitive; outward rounding must use safe `nextUp`/`nextDown` helpers or conservative widening.
- A subnormal interval can collapse under ordinary arithmetic if outward widening is omitted.

### TypeScript and dependency feasibility

A BigInt-backed fixed-point reducer and interval polynomial evaluator are feasible in TypeScript, but BigInt is slower than Number and unavailable in some constrained older runtimes. The package must therefore keep BigInt on the slow path and feature-detect the required runtime. The ordinary path uses precomputed dyadic constants and Number arithmetic only after the interval proof confirms safe reduction.

The implementation adds code and bundle size but avoids a new native dependency and avoids assuming a platform-specific libm. BigInt itself is a language feature, not an npm dependency. The generated coefficient table must be small and tree-shakeable.

### Performance

Ordinary PCB rotations with moderate angles use a fast reduced-interval path, expected to be materially slower than `Math.sin`/`Math.cos` but still constant-time. The BigInt range-reduction path is reserved for large angles or ambiguous Number reduction. The transform engine may cache coefficient intervals by normalized angle only when caching cannot conflate different input enclosures.

For typical footprints, the cost is bounded by a handful of interval polynomial operations per transform. The slow path must be benchmarked against a representative board and a cancellation-heavy adversarial corpus. No wall-clock timeout may determine a geometry result.

### Adversarial examples

1. Angles near a multiple of 90 degrees must not be classified as exactly special angles unless the input representation proves the special value.
2. `Number.MAX_VALUE` degrees must not be normalized with `% 360` and accepted as a meaningful quadrant.
3. An angle whose reduction interval straddles a quadrant boundary must return `INDETERMINATE` rather than choose a side.
4. 45 degrees has a non-exact binary64 sine/cosine coefficient; it may use a narrow interval but not an exact equality claim.
5. Coefficient intervals that include zero must propagate zero uncertainty into the transformed coordinate.

### Executable acceptance criteria

- A test must demonstrate that the implementation never labels an arbitrary-angle coefficient `EXACT` merely because it came from `Math.sin`/`Math.cos`.
- The software kernel must be checked against an independent high-precision oracle over random, boundary, huge, tiny, and quadrant-adjacent angles.
- Every returned interval must contain the independent oracle value for the test corpus.
- No `VALID` transform may depend on an unproved coefficient interval.
- The polynomial domain, coefficient constants, remainder bounds, reduction bounds, and outward-rounding method must be reviewed as a complete proof package.
- If any proof package is absent, the implementation must return `INDETERMINATE`, not use a one-ULP assertion.

## Resolution 3 — numerical proof and output-cell criterion

### Decision

A transformed coordinate is `VALID` only when the complete outward enclosure of the mathematical result is contained in one binary64 round-to-nearest-even output cell for a finite candidate `z`.

Define `Cell(z)` as the exact set of real values that round to `z` under IEEE-754 binary64 round-to-nearest-even, including its asymmetric boundary behavior at zero, subnormals, powers of two, and the largest finite value. The transform result is `VALID` iff:

```text
input state is valid;
all intermediate intervals are finite;
[lo, hi] is a valid outward enclosure;
[lo, hi] is strictly inside Cell(z),
```

or an exact tie at a cell boundary is resolved by a proven even/odd significand rule. If the enclosure touches a cell boundary and the tie cannot be proven, return `INDETERMINATE`. If the enclosure crosses the finite range boundary, return `NON_REPRESENTABLE` unless the exact result is proven to round to the largest finite value under the implementation’s overflow policy.

This is stronger than “within one ULP”: one ULP width does not prove a unique rounded output, and a coordinate interval can cross a rounding boundary while having width less than one ULP.

### Mathematical assumptions

The interval includes:

- coefficient approximation/reduction error;
- product rounding error;
- compensated sum/difference rounding error;
- translation rounding error;
- any scaling/unscaling error;
- exact finite input coordinate values.

Correctness is a statement about the final rounded coordinate, not about equality with the mathematical real number.

### IEEE-754 failure modes

- Cell widths differ at binade boundaries.
- Zero and subnormal cells have special spacing.
- A result exactly halfway between two values requires tie-to-even resolution.
- A finite enclosure can include `Infinity` even when the midpoint is finite.
- Signed zero can affect downstream branch logic; normalize only where the geometry contract permits it.

### TypeScript feasibility

`nextUp`/`nextDown` can be implemented using `DataView` bit manipulation for finite Numbers, with explicit handling of ±0, subnormals, infinities, and NaN. Cell boundaries should be computed from exact binary64 bit patterns or a documented exact dyadic representation, not by `z ± Number.EPSILON`.

BigInt is appropriate for significand/exponent comparisons in the slow proof path. The fast path can compare normalized interval endpoints against precomputed cell boundaries when the candidate is a normal finite number.

### Transform result semantics

- `VALID`: unique correctly rounded finite binary64 coordinate is proved.
- `INDETERMINATE`: all inputs and bounds are finite, but more than one output cell remains possible or a tie cannot be resolved.
- `NON_REPRESENTABLE`: the exact enclosure is outside the finite output domain or an operation required for the result cannot be represented.
- `INVALID`: a source input is malformed or non-finite.

A `VALID` coordinate is still not mathematically exact; it is the proven binary64 representation under the stated enclosure.

### Acceptance criteria

- Tests at normal-binade boundaries, powers of two, subnormal/normal transition, signed zero, largest finite value, and exact halfway cases.
- An adversarial interval that is narrower than one ULP but straddles a cell boundary must be `INDETERMINATE`.
- An interval strictly inside one cell must be `VALID`.
- A translation result whose interval crosses the finite overflow boundary must not be emitted as a finite coordinate.
- The candidate output must equal an independent correctly rounded high-precision reference whenever `VALID` is returned.

## Resolution 4 — deterministic certified rectangle/oval resource budget

### Decision

Use a deterministic adaptive interval branch-and-bound evaluator for nonlinear rectangle/oval boundary distance, with these fixed per-pair limits:

```text
MAX_CERTIFIED_CELLS       = 4096
MAX_INTERVAL_EVALUATIONS  = 32768
MAX_SUBDIVISION_DEPTH     = 32
```

The evaluator maintains a priority queue ordered by the greatest possible lower-bound uncertainty, with a stable monotonic sequence number as the tie-breaker. The queue is seeded by the finite parameter domains. A cell is accepted only when its interval bounds prove one of:

- exact contact;
- overlap;
- positive separation;
- a converged finite distance interval satisfying the requested output criterion.

The evaluator stops at the first proof or at the first budget exhaustion. Exhaustion returns `INDETERMINATE` with a stable reason such as `certified-distance-budget-exhausted`, including counters for diagnostics. It never returns zero, `CONVERGED`, or a clearance pass solely because the budget ended.

Broad-phase analytic cases remain before this evaluator: circle-circle, common-axis oval, simple rectangle cases, exact boundary/contact checks, and safe positive lower bounds. The budget applies only after those paths fail to prove the result.

This is a resource-exhaustion safeguard, not an algorithmic convergence cap and not a GJK policy. Existing GJK behavior and its `gjkMaxIterations` semantics remain unchanged.

### Mathematical assumptions

- Interval lower/upper bounds contain the true distance over each parameter cell.
- Subdivision refines a compact parameter domain.
- A positive lower bound proves separation regardless of unresolved upper-bound width.
- Contact/overlap predicates are exact or certified independently of the distance approximation.

### IEEE-754 failure modes

- Squared distances can overflow even when the final distance is finite.
- Very small intervals can collapse to identical Number endpoints; the evaluator must widen outward or use dyadic bounds.
- Tangency has zero derivative and can defeat naive Newton termination.
- Ellipse parameterization has periodic endpoints; duplicate parameter cells must not create inconsistent results.
- NaN or infinite interval endpoints are immediate `NON_REPRESENTABLE`/`INVALID`, never queue values.

### TypeScript feasibility

A fixed-size binary heap or deterministic array priority queue is straightforward. Counters are integer values. No timer, random number, promise scheduling, or machine-dependent floating iteration count may affect classification. The evaluator can use a small internal object pool to control allocations.

### Performance

Most ordinary pad pairs must be decided by broad-phase checks or the existing analytic paths. The 4096-cell/32768-evaluation limits are a worst-case ceiling per pair, not the expected cost. Benchmark requirements are:

- ordinary board with at least 10,000 pad/shape pairs;
- near-tangent rectangle/oval pairs;
- adversarial high-curvature and tiny-scale pairs;
- repeated budget exhaustion cases.

The benchmark must report median, p95, p99, allocation count, and maximum evaluation counters. No performance result can weaken fail-closed semantics.

### Adversarial examples

1. Near-tangent rectangle/oval geometry that never proves separation within 4096 cells must be `INDETERMINATE`, not zero.
2. A deliberately difficult pair must exhaust at the same counters and return the same reason across runs and machines.
3. A positive gap with a certified lower bound must return `SEPARATED` early, without requiring full distance convergence.
4. An overlapping pair must return `OVERLAPPING` through a certified relation, not through a distance interval that merely touches zero.
5. A tiny-scale positive gap must not be erased by the interval evaluator or an absolute tolerance.

### Acceptance criteria

- Counter values and tie-breaking are fixed in tests.
- Repeated runs produce identical state, reason, counters, and finding output.
- Exhaustion always maps to detailed `INDETERMINATE` and DRC error/fail-closed behavior.
- Exhaustion never changes GJK state or GJK iteration count.
- Independent high-precision cases verify all early-positive, overlap, contact, and indeterminate branches.
- No `INDETERMINATE` distance is converted by a wrapper to zero or a clearance pass.

## Resolution 5 — public `rotatePoint` versus internal checked transforms

### Decision

Preserve the public `rotatePoint(point, angle)` signature and ordinary behavior as a compatibility wrapper. It remains a best-effort numeric helper and returns the existing point shape. It does not expose a state and must not be used by new DRC/topology code as a proof-bearing operation.

Introduce an internal checked transform path used by engineering integration:

```text
checkedRotatePoint(point, angle): TransformResult
checkedTransformLocalPoint(point, origin, angle): TransformResult
```

The public wrapper may delegate to the checked path only for `VALID` results if doing so preserves existing ordinary outputs; otherwise it retains the existing arithmetic path and is explicitly non-authoritative. It must never silently turn `INDETERMINATE` or `NON_REPRESENTABLE` into a precise checked result.

All transformed pads, pins, rectangle corners, and DRC geometry use the checked path. Existing public consumers that call `rotatePoint` retain the public signature and documented best-effort behavior. A future public checked API requires separate API approval and is out of scope.

### Mathematical assumptions

The public function’s historic Number result is a compatibility surface, not a numerical proof. Internal engineering decisions require a state and enclosure. This separation is necessary because a `Point` object cannot represent uncertainty without changing the public type.

### IEEE-754 failure modes

- A public point can contain a finite but badly cancelled coordinate.
- A public caller cannot distinguish an uncertain finite point from a certified point.
- A wrapper that catches a checked error and returns the historic value can reintroduce the original defect if internal callers consume it.
- Two paths can diverge by one or more ULPs on ordinary geometry.

### TypeScript feasibility and performance

The checked result is internal and can be structurally typed without changing exported types. The main code risk is accidental use of the public helper in new geometry code; a code-review rule and targeted search/lint check are required. Ordinary transforms incur the interval cost; the public compatibility path does not.

### Acceptance criteria

- Existing public `rotatePoint` signature and ordinary fixture outputs remain compatible.
- New engineering code contains no unreviewed use of public `rotatePoint` for DRC/topology proof.
- Any uncertain transformed pad/pin is localized and cannot create a union or clearance pass.
- Public best-effort output is never presented as a `VALID` checked result.
- Tests cover divergence between public and checked outputs at extreme cancellation without changing public API shape.

## Cross-cutting adversarial findings

### `Math.sin`/`Math.cos` portability

ECMAScript specifies the functions but does not provide a portable proof obligation that their error is within one ULP or correctly rounded on every engine. V8, SpiderMonkey, JavaScriptCore, Node, browsers, and embedded runtimes may use different libm implementations. Therefore, an implementation that sets `error = Number.EPSILON` around `Math.sin` is rejected.

### `Number.EPSILON` misuse

`Number.EPSILON` is a relative scale near one, not an absolute geometry tolerance and not a universal rounding bound. Expressions such as `Math.abs(v) <= Number.EPSILON * scale` are permissible only when derived from a specific forward-error proof and with overflow/underflow handling.

### `BigInt` limitations

BigInt gives exact integer arithmetic but does not represent arbitrary real pi, does not itself provide outward rounding, and cannot be mixed with Number without explicit conversion. It is suitable for dyadic input decomposition, exact orientation, quotient calculations, and fixed-point interval endpoints; it is not a complete certified-transcendental solution.

### Interval arithmetic limitations

Intervals can become wide through dependency effects, cancellation, and nonlinear evaluation. Wide intervals cause `INDETERMINATE`; they must not be narrowed by an unproved tolerance. An interval algorithm is only certified if every primitive widens outward and the initial constants contain the mathematical constants.

### Localized uncertainty limitations

Localized uncertainty prevents unrelated findings from being suppressed, but it does not make an affected result safe. The affected relationship must remain an error/indeterminate result, and topology must not union through it.

## Revised acceptance test matrix

### Route

- ordinary horizontal, vertical, diagonal, equal-endpoint, negative-direction, and signed-zero cases;
- opposite-`MAX_VALUE` endpoints;
- waypoint rounding back to start or endpoint;
- finite endpoint but unrepresentable segment delta;
- invalid NaN/Infinity inputs;
- legacy wrapper output and checked result state;
- client transactional no-track behavior;
- explicitly labelled, independently validated direct fallback.

### Trigonometric coefficients

- exact 0/90/180/270-degree identities;
- 45-degree non-exact coefficient interval;
- angles adjacent to quadrant boundaries;
- huge finite angles requiring BigInt reduction;
- range-reduction boundary straddle;
- tiny angles and subnormal outputs;
- randomized independent MPFR/high-precision oracle comparison;
- all `VALID` intervals contain the oracle result.

### Output cells and transforms

- normal numbers, powers of two, subnormal/normal transition;
- signed zero;
- largest finite output and overflow boundary;
- exact halfway/tie-to-even values;
- enclosure inside one cell;
- enclosure crossing one cell boundary;
- cancellation with large equal terms;
- translation with large origin and small local point;
- transformed pad/pin localized state propagation.

### Certified rectangle/oval distance

- exact contact;
- interior overlap;
- positive separation with early lower-bound proof;
- tiny positive separation;
- near-tangent indeterminate case;
- all three resource counters at one below and exactly at the limit;
- stable priority-queue tie ordering;
- deterministic exhaustion;
- overflow/underflow interval primitives;
- circle/oval and common-axis analytic compatibility;
- wrapper behavior for detailed `INDETERMINATE`.

### DRC and topology

- no false clearance pass on indeterminate distance;
- no fabricated zero distance;
- no false schematic union through an indeterminate intersection;
- affected finding localized to the relevant pad/pin/wire/net;
- unrelated required-pin and disconnected-net findings preserved;
- existing finding IDs/order unchanged for valid ordinary geometry;
- GJK boundary/exhaustion behavior unchanged.

## P2.4-B/P2.4-C compatibility matrix

| Area | P2.4-B target | P2.4-C compatibility target | Closure condition |
|---|---|---|---|
| Baseline | `e567acb883a0f81cb0c64d11f638b5f872511346` | independent target, not merged | same oracle suite runs against both |
| Public signatures | Point/Number/array wrappers unchanged | unchanged | TypeScript compile/API snapshot passes |
| `route45` | ordinary output preserved | no route topology conflict | checked result internal; legacy fallback deterministic |
| `rotatePoint` | ordinary best-effort behavior preserved | checked transforms feed uncertainty path | no public signature change |
| Exact orientation | replaces fixed shape epsilon only in D design | reuse/adapt C exact sign semantics | no fixed absolute determinant tolerance |
| Connectivity | existing GJK and topology semantics | preserve C localized uncertainty | no false union; no global suppression |
| Pad distance | detailed/wrapper state contract preserved | fail-closed uncertainty preserved | indeterminate never becomes zero/pass |
| Circle/Oval | analytic ordinary paths preserved | no C conflict | independent circle/oval regressions pass |
| Findings | IDs/order for valid inputs preserved | C localized findings preserved | snapshot and adversarial findings pass |
| Dependencies | no mandatory unreviewed math npm package | C helpers adapted through kernel | license/bundle review complete |
| Performance | fast ordinary path required | slow paths localized | benchmark thresholds approved |

## Remaining blockers

1. **Trig proof artifact:** provide and independently review the polynomial coefficients, range-reduction constants, directed-rounding method, and remainder proof. Until then, arbitrary-angle `VALID` transforms are not implementation-ready.
2. **Independent oracle evidence:** execute the coefficient and distance corpus against an independent high-precision reference. A test against the same implementation or generated constants is insufficient.
3. **Output-cell reference implementation:** review the `nextUp`/`nextDown` and round-to-nearest-even cell logic at subnormal, signed-zero, tie, and overflow boundaries.
4. **Distance-budget acceptance:** approve the fixed 4096/32768/32 limits after ordinary-board and adversarial performance measurement. The limits are design choices, not proven optimal values.
5. **Compatibility fixtures:** lock exact public `route45` invalid/fallback behavior and public `rotatePoint` ordinary outputs before source changes.
6. **P2.4-C adapter review:** compare helper names and state semantics when the remediation is later integrated; do not merge it as part of this review.

## Final implementation-readiness verdict

**NOT_READY_FOR_IMPLEMENTATION**

The contract is now closed at the policy/design level for all five questions:

1. legacy `route45` returns deterministic endpoint-only fallback for finite `NON_REPRESENTABLE` results, while checked callers reject unproven route geometry;
2. arbitrary-angle coefficients use a dependency-free software interval kernel rather than an unsupported `Math.sin`/`Math.cos` accuracy claim;
3. `VALID` transformed coordinates require containment in one IEEE-754 round-to-nearest-even output cell;
4. certified rectangle/oval distance uses deterministic 4096-cell, 32768-evaluation, depth-32 limits and fail-closed exhaustion;
5. public `rotatePoint` remains a compatibility helper while internal checked transforms carry proof states.

The exact implementation proof artifacts and independent oracle results remain outstanding. A `READY_FOR_IMPLEMENTATION_REVIEW` verdict may be considered only after those blockers are reviewed and accepted. This report does not authorize implementation, P2.4-C merge, pull-request activity, or P2.4-E.
