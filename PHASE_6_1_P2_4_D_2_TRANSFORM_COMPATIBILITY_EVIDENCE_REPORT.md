# PHASE 6.1 — P2.4-D-2 Transform and Rotation Compatibility Evidence

## Final verdict

**EVIDENCE_INSUFFICIENT**

The reference implementation and its production consumers are source-characterized, and substantial ordinary-rotation and DRC evidence already exists. The requested evidence package is not complete for implementation or numerical certification because the extreme/non-finite vector corpus has not been independently executed against a high-precision reference and no binary64 output-cell certificate exists for these APIs.

This is a read-only/design-only audit. No production source, existing test, `main` branch, or implementation branch was modified.

## 1. Verification scope and references

- Repository requested by the task: `soheil6913/PCB`
- Reference implementation: `941262899a46e54cbf1a94a4da6dd528b8d36780`
- Reference subject: `fix: unify geometry options iteration validation`
- Reference parent: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Previous report: `PHASE_6_1_P2_4_D_1_GEOMETRY_OPTIONS_REMEDIATION_REPORT.md`
- Documentation baseline: `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`

The reference commit was verified as present and as an ancestor of the inspected implementation worktree. The documentation branch was created from documentation `origin/main`, not from a source implementation branch.

## 2. Source-grounded inventory

### 2.1 `route45`

**Definition:** `shared/engineering.ts:59`.

**Type:**

```ts
route45(start: Point, end: Point): Point[]
Point = { x: number; y: number }
```

**Algorithm:** computes `dx = end.x - start.x` and `dy = end.y - start.y`; returns `[start, end]` when either absolute delta is below `EPSILON = 1e-7` or when the absolute delta difference is below `EPSILON`; otherwise computes `diagonal = Math.min(Math.abs(dx), Math.abs(dy))` and returns `[start, { x: start.x + Math.sign(dx) * diagonal, y: start.y }, end]`.

**Production caller:** one caller in `client/src/pages/Home.tsx:75`. In PCB route mode, the UI obtains two canvas points, calls `route45`, and persists each returned segment as a track through the project update path.

**Downstream consumers:** the resulting track endpoints are rendered as SVG `<line>` elements at `client/src/pages/Home.tsx:76`; they are persisted through local storage and JSON export at `client/src/pages/Home.tsx:91–97`; they are later consumed by engineering DRC track-edge, track-track, track-pad, and track-via checks in `shared/engineering.ts:514–527`.

**Error/non-finite behavior:** there is no validation, exception, or `INDETERMINATE` result. Non-finite inputs can produce non-finite deltas and intermediate points. `NaN` can reach `Math.min` and the diagonal point; infinities can create `Infinity - Infinity = NaN` or infinite intermediates. The caller normally supplies finite canvas-derived values, but the exported helper itself does not enforce that domain.

### 2.2 `rotatePoint`

**Definition:** `shared/engineering.ts:57`.

**Type:**

```ts
rotatePoint(point: Point, degrees: number): Point
```

**Algorithm:** computes `radians = degrees * Math.PI / 180`, then `cos = Math.cos(radians)` and `sin = Math.sin(radians)`, and returns the standard two-dimensional rotation products:

```text
x = point.x * cos - point.y * sin
y = point.x * sin + point.y * cos
```

**Production callers:** there are no direct production call sites other than the call from `transformLocalPoint` at `shared/engineering.ts:58`. The independent oracle has a separate same-form helper at `shared/phase5_3.independent-oracle.ts:173–184`, but that is test/reference code, not a production caller.

**Error/non-finite behavior:** no validation or exception is performed. Non-finite coordinates or degrees propagate through multiplication, subtraction, and addition. Finite large degrees can overflow during degree-to-radian conversion; `Math.sin`/`Math.cos` of an infinite radian value produce `NaN`, which then propagates to both outputs. Very small/subnormal products can underflow or lose signed-zero information.

### 2.3 `transformLocalPoint`

**Definition:** `shared/engineering.ts:58`.

**Type:**

```ts
transformLocalPoint(origin: Point, local: Point, rotation?: number): Point
```

The default rotation is `0`. It calls `rotatePoint(local, rotation)` and then returns `{ x: origin.x + rotated.x, y: origin.y + rotated.y }`.

**Production callers:**

1. `shared/engineering.ts:196`, `localPads(component)`: transforms every footprint-local pad position by the component origin and component rotation, then adds component rotation to the pad's local rotation.
2. `shared/engineering.ts:465`, `validateSchematic` pin normalization: transforms every component-local pin position into world coordinates before graph-node and wire-connectivity checks.

**Downstream consumers:** transformed pads feed `evaluatePcbV2` and DRC at `shared/engineering.ts:516–526`, including board-edge, track-to-pad, pad-to-pad, via-to-pad, and related geometry decisions. Transformed pins feed schematic connectivity and required-pin findings at `shared/engineering.ts:464–470` and ultimately `runDesignRules` at `shared/engineering.ts:586–607`.

**Error/non-finite behavior:** no local validation or exception. Non-finite transformed coordinates are subsequently detected by some DRC boundary checks and may produce `PCB_GEOMETRY_INDETERMINATE`; schematic topology paths also have numerical-indeterminate handling. That downstream fail-closed behavior is not equivalent to a certified transform result and does not establish a transform error contract.

## 3. Consumer compatibility findings

### Pad placement and footprint transformations

The PCB evaluator stores pad-local positions and component-level positions separately. `localPads` transforms pad positions into world coordinates and combines component and pad rotations. Any change in rotation rounding, signed-zero handling, angle reduction, or overflow behavior can change pad edge extents, track-to-pad distance, pad-to-pad distance, and via-to-pad outcomes.

### Pin placement and schematic topology

Pin positions are transformed before node insertion and wire proximity decisions. A one-cell change near a topology tolerance boundary can change whether a pin is connected, whether a wire crossing is reported, and whether required-pin findings are emitted.

### Route geometry

`route45` is separate from the rotation helpers. Its returned points are immediately converted into persisted track segments by the UI. It does not call `rotatePoint` or `transformLocalPoint`. A route implementation change can therefore affect track geometry and later DRC without changing footprint transforms.

### Board rendering

The current client renders component rotation directly through SVG transform text at `Home.tsx:69` and `Home.tsx:76`; it does not call the shared `rotatePoint` or `transformLocalPoint` functions for those visuals. `route45` output is rendered as track lines. Consequently, replacing shared transform helpers would primarily affect engineering evaluation and schematic/DRC calculations, while changing route output affects both rendering and persisted track data.

### DRC

The transformed pad path participates in fail-closed DRC. Non-finite transformed bounds can produce `PCB_GEOMETRY_INDETERMINATE`, but not all transform consumers are proven to classify every non-finite intermediate identically. A future checked transform must specify whether it returns a result, an explicit indeterminate state, or throws, and every consumer must be audited before replacement.

### Persistence and serialization

The client autosaves `project` with `JSON.stringify` to `localStorage` and exports JSON. Component `rotation`, track endpoints, and related numeric fields are serialized as ordinary JSON numbers. JavaScript JSON serialization converts non-finite numeric values to `null`; imported data is then validated/migrated before entering application state. This creates a compatibility boundary distinct from the in-memory helper behavior and must be included in any future non-finite policy.

### Current best-effort behavior

The shared helpers use native `Math.sin`/`Math.cos`, ordinary IEEE-754 arithmetic, and no checked transform abstraction. Existing callers therefore rely on current best-effort binary64 results for finite values, especially component/pad placement and DRC boundary decisions. The source does not document a tolerance or output-cell contract for these public helpers.

## 4. Existing regression and oracle coverage

Existing direct coverage includes:

- `shared/engineering.test.ts:33–35`: one ordinary `route45` case.
- `shared/engineering.test.ts:61–65`: component rotation feeding transformed pads and DRC.
- `shared/engineering.test.ts:132–136`: rotated rectangle and oval DRC behavior.
- `shared/engineering.test.ts:219–229`: rotated oval track-clearance boundaries.
- `shared/engineering.test.ts:249–260`: direct `transformLocalPoint` use plus combined component/pad rotation and via-to-pad behavior.
- `shared/engineering.test.ts:140–146`: rotation field validation for malformed persisted data.
- `shared/phase5_3_8.rotated-rectangle.test.ts`: broad metamorphic and rotated-rectangle cases using a separate oracle transform.
- `shared/phase5_3.independent-oracles.test.ts`: many rotated geometry cases using `rotatePointIndependent` and exact integer/rational geometry after quantization.
- `shared/phase5_4.drc-boundary-semantics.test.ts`: fixed-grid boundary and metamorphic checks using the independent oracle.

The independent helper `rotatePointIndependent` at `shared/phase5_3.independent-oracle.ts:173–184` is textually the same trigonometric kernel as production. It is useful as a separately located reference for metamorphic tests, but it is **not an independent high-precision oracle** for the arithmetic result. The exact integer/rational portions of the oracle become independent only after explicit quantization; they do not certify arbitrary binary64 rotation outputs.

No existing direct regression suite covers the complete requested vector families for `route45`, `rotatePoint`, or `transformLocalPoint`, including signed zero, subnormals, overflow-adjacent coordinates, degree-to-radian overflow, `NaN`, and infinities.

## 5. Reproducible compatibility-vector specification

The following is a test-vector design, not a claim that the vectors have been executed or certified. Each vector record should contain:

```text
id, function, inputs, reference_math, exact_binary64_output,
classification, downstream_observation, oracle_method, limitations
```

`exact_binary64_output` must be captured from the reference implementation without rounding or `toBeCloseTo`. `reference_math` must be computed independently at higher precision when the mathematical value is finite and meaningful. The two must not be conflated.

### 5.1 Shared point/angle families

Use each family with representative points `{x: 3, y: 4}`, asymmetric points such as `{x: -7, y: 2.3}`, and axis/sign variants. Angles must include:

- `0`, `90`, `180`, `270`, `360`, `-90`, `-180`;
- `45`, `-45`, `123.456`, and an angle outside the conventional range such as `1080 + 17.25`;
- the smallest finite perturbations around `0`, `90`, and `180` representable by adjacent binary64 values;
- large finite angles near the degree-to-radian multiplication overflow transition;
- `Number.MIN_VALUE`, `-Number.MIN_VALUE`, `Number.MAX_VALUE`, `-Number.MAX_VALUE`, `NaN`, `Infinity`, and `-Infinity` where the function accepts a numeric argument.

The specification must record whether each result is finite, contains signed zero, contains a subnormal, contains `NaN`, or contains infinity. It must not prescribe an invented decimal tolerance.

### 5.2 `route45` vectors

Required vector groups:

1. Ordinary finite diagonal route: unequal positive deltas; verify exact returned-point structure and both segment directions.
2. Zero rotation analogue / axis-aligned route: `dx = 0` and `dy = 0`; verify the original two-point route and object-value preservation.
3. Quarter-turn/half-turn coordinate patterns: use endpoint pairs whose deltas are axis swaps or sign reversals; route45 has no angle input, so these are coordinate-orientation compatibility vectors rather than rotations.
4. Negative deltas: all four sign quadrants.
5. Outside conventional coordinate range: large finite coordinates and large finite deltas.
6. Very small deltas: values below, exactly at, and just above the `1e-7` threshold; include cancellation-sensitive endpoint subtraction.
7. Signed zero: `+0` and `-0` in both endpoints and deltas; record whether the fast path returns original signed-zero fields.
8. Subnormal deltas: adjacent subnormal endpoints and differences that underflow to zero.
9. Large-coordinate near overflow: endpoint pairs around `Number.MAX_VALUE`, including same-sign subtraction and opposite-sign subtraction.
10. Non-finite inputs: each coordinate independently set to `NaN`, `Infinity`, or `-Infinity`; record returned point count and all non-finite fields.

Expected structural observations are derived directly from the source: only two or three points are returned; no exception is expected from the helper itself; and the `EPSILON` branches are threshold comparisons, not certified geometric predicates. Numerical output vectors must be generated from the reference commit, not guessed.

### 5.3 `rotatePoint` vectors

Required vector groups:

1. Ordinary finite coordinates at zero, quarter-turn, half-turn, and full-turn angles.
2. Negative angles and angles beyond `360` degrees; include equivalent mathematical angles to measure current binary64 differences rather than assuming exact periodic identity.
3. Very small angles around zero and around quarter turns.
4. Large finite angles, including the largest values for which `degrees * Math.PI / 180` remains finite and values just beyond that transition.
5. Signed-zero coordinates and angles; capture signs of both output zeros.
6. Subnormal coordinates and products; distinguish exact zero, subnormal, normal, and underflowed output cells.
7. Large coordinates near overflow with finite and overflowed products/sums.
8. Cancellation-sensitive values where `point.x * cos` and `point.y * sin` nearly cancel.
9. Non-finite point coordinates and non-finite degrees.

The high-precision oracle should use an independent implementation such as Python `mpmath` with a documented precision substantially above binary64, compute the mathematical sine/cosine and products, and separately compare the reference JavaScript result to a correctly rounded binary64 value. `Math.sin`/`Math.cos` copied into another TypeScript function is not an independent oracle.

### 5.4 `transformLocalPoint` vectors

Use the same local point/angle families as `rotatePoint`, plus origins designed to test addition behavior:

1. Zero origin and non-zero origin.
2. Exact cancellation between origin and rotated local point.
3. Origin and rotated local point with opposite signs near zero.
4. Origins near `Number.MAX_VALUE` where addition remains finite, overflows, or loses the local displacement.
5. Signed-zero origin and local values.
6. Subnormal origin/local values.
7. Omitted rotation versus explicit `0`.
8. Non-finite origin, local point, and rotation independently.

The oracle must compare the mathematical translated point, the exact reference binary64 output, and the output-cell classification. It must separately test the composed operation rather than infer it solely from `rotatePoint` because the final addition can change the output cell and signed-zero behavior.

## 6. Evidence status by function

| Function | Current behavior characterized? | Existing compatibility vectors complete? | Independent high-precision oracle available? | Output-cell requirements known? | Implementation readiness |
|---|---|---|---|---|---|
| `route45` | Partially: source branches, threshold, point shape, one UI path, and non-validating behavior are known | No; ordinary coverage exists, but extremes/non-finite/signed-zero/subnormal cases are absent | No dedicated oracle; exact binary64/reference branch replay is available, but geometric correctness near threshold needs an explicit specification | Partially known: threshold-cell and subtraction/intermediate-cell behavior must be captured | Not ready |
| `rotatePoint` | Partially: formula and native trig operations are known; consumer dependence is indirect through `transformLocalPoint` | No; ordinary/metamorphic rotated geometry exists, but requested raw-function edge vectors are absent | No: existing `rotatePointIndependent` uses the same native trig operations; no high-precision or correctly-rounded oracle is checked in | Known as a requirement, not certified: signs, subnormals, overflow, cancellation, and trig reduction cells remain open | Not ready |
| `transformLocalPoint` | Partially: composition and pad/pin consumers are known | No; composition is exercised in ordinary DRC cases, not the full translation/extreme matrix | No dedicated oracle; it inherits the missing independent rotation and addition-cell oracle | Known as a requirement, not certified: final addition and non-finite propagation need explicit cells | Not ready |

## 7. Exact binary64 versus mathematical reference

A future evidence runner must report at least three distinct values for finite cases:

1. **Reference implementation output:** the exact JavaScript `Number` bit pattern returned by the target commit.
2. **Independent mathematical value:** a high-precision value from an implementation not using the same native trig call path.
3. **Correctly rounded binary64 candidate or enclosure:** only if the oracle can prove the rounding cell; otherwise mark it unavailable.

`toBeCloseTo`, fixed decimal formatting, or a second implementation that calls `Math.sin` and `Math.cos` cannot establish output-cell certification. For signed zero, the runner must record `Object.is(value, -0)`. For subnormals, it must record the binary64 exponent/fraction class or equivalent bit pattern. For non-finite results, it must distinguish `NaN`, `+Infinity`, and `-Infinity` where observable.

## 8. Certification gaps and required next evidence

1. Produce and check in a reproducible high-precision vector generator for raw `rotatePoint` and composed `transformLocalPoint`.
2. Add exact-bit capture for all requested edge families, including signed zero and subnormal values.
3. Establish the degree-to-radian overflow transition empirically from the reference implementation; do not substitute an assumed angle bound.
4. Define route45's compatibility policy at and around `EPSILON`, including cancellation and non-finite inputs. The current helper has no explicit invalid-input contract.
5. Audit all downstream non-finite handling so a checked transform can return a consistent indeterminate state without false DRC passes or silent topology changes.
6. Validate JSON/local-storage round trips for non-finite intermediate results and confirm the intended `null`/rejection behavior; this is a persistence contract, not a transform proof.
7. Separate the existing same-kernel independent geometry fixtures from a genuinely independent trig oracle. Their exact integer/rational geometry remains useful, but it cannot certify native trigonometric outputs.
8. Only after these artifacts exist should output-cell certification or a checked-transform implementation be considered.

## 9. Restrictions observed

- No production source was modified.
- No existing test was modified.
- No checked transform was implemented.
- No numerical coordinate, angle, dimension, or geometry bound was introduced.
- No mathematical certification claim was made.
- No source branch was merged and `main` was not modified.

## 10. Conclusion

The source and consumer inventory is sufficiently clear to guide a future evidence runner: `route45` is a UI-to-persistence-to-track path; `rotatePoint` is the native-trigonometric primitive; and `transformLocalPoint` is consumed by transformed pads and pins with DRC and schematic consequences. Existing tests demonstrate ordinary behavior and useful metamorphic geometry, but they do not complete the requested compatibility vector corpus or supply an independent high-precision/output-cell oracle for the raw transform APIs.

**EVIDENCE_INSUFFICIENT**
