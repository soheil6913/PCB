# PHASE 6.1 — P2.4-D Numerical Remediation Contract Engineering

## Final status

**DESIGN-ONLY CONTRACT — IMPLEMENTATION NOT AUTHORIZED**

This document defines an implementation-ready numerical remediation contract for exactly the three independently confirmed P2.4-D findings:

- `P24D-ROUTE45-OVERFLOW`
- `P24D-ROTATION-CANCELLATION`
- `P24D-SHAPE-SCALE-TOLERANCE`

No source code, tests, dependencies, configuration, source branch, pull request, or implementation artifact is changed by this contract. A separate explicit authorization is required before implementation begins.

## Executive summary

The P2.4-B baseline contains three related but distinct numerical classes of defect:

1. `route45` uses raw coordinate subtraction and waypoint construction. With finite opposite-sign endpoints, the delta can overflow and the computed waypoint can round back to the start, creating duplicate points and invalid tracks.
2. `rotatePoint` uses ordinary floating products and sums. For large finite coordinates, coefficient approximation and cancellation can produce a large spurious residual. `transformLocalPoint`, transformed pads, and transformed schematic pins consume the result without a checked uncertainty state.
3. Internal rectangle/oval distance helpers use a fixed absolute `1e-12` determinant and on-segment tolerance. At small valid scales this changes separated edges into contacts and returns a false zero pad distance.

The contract therefore introduces four internal layers:

1. **Numeric Kernel** — representability, scaling, exact finite IEEE-754 dyadic operations, compensated arithmetic, intervals, and error bounds.
2. **Geometry Predicates** — orientation, point-on-segment, segment intersection, boundary relationships, and certified distance intervals.
3. **Transform Engine** — coefficient intervals, compensated rotation/translation, and localized transformed-geometry states.
4. **Engineering Integration** — route construction, pads, pins, topology, and DRC propagation without fabricated zero distances or unjustified passes.

Existing public signatures remain unchanged. Checked internal results carry explicit states where needed. Ordinary board-scale outputs must remain compatible byte-for-byte or within existing documented numeric expectations. Extreme or unresolved geometry must become a localized `INDETERMINATE` or `NON_REPRESENTABLE` result, never a guessed route, guessed contact, fabricated zero distance, false union, or clearance pass.

## Exact baseline and preserved checkpoints

- Source repository: `soheil6913/-PCB-Studio-Pro`
- Independent implementation baseline: P2.4-B `e567acb883a0f81cb0c64d11f638b5f872511346`
- P2.4-A: `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- P2.4-C original baseline: `21b7487eec431dcb993a44d0d642a33644141526`
- Accepted but unmerged P2.4-C remediation: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Source `main`: `a98384bbfc3296947b90f5254a03a77b11fdc8a9`
- Documentation repository: `soheil6913/PCB`

P2.4-D must be implementable directly against the exact P2.4-B tree. P2.4-C is not assumed present. When P2.4-C is later integrated, the compatibility strategy in this document applies; P2.4-D must not require a merge of the unmerged branch as a prerequisite.

## Finding contracts

# P24D-ROUTE45-OVERFLOW

### Existing contract and defect

The P2.4-B `route45` implementation is in `shared/engineering.ts:33`. The client caller is `client/src/pages/Home.tsx:75`, which maps every returned point into a PCB track. The documented ordinary contract is a two- or three-point orthogonal/45-degree route.

For distinct points `S=(sx,sy)` and `E=(ex,ey)`, define represented deltas:

```text
dx = ex - sx
 dy = ey - sy
```

For the ordinary non-axis case, the existing route convention is:

```text
L = min(abs(dx), abs(dy))
M = (sx + sign(dx) * L, sy)
```

The output is `[S,M,E]`; `S-M` is horizontal and `M-E` has equal absolute x/y deltas. For horizontal or vertical endpoints the output is `[S,E]`.

With `S=(-MAX_VALUE,0)` and `E=(MAX_VALUE,10)`, `dx` is `Infinity`, `L=10`, and `sx + 10` rounds back to `sx`. The output contains two identical consecutive points and the second segment cannot satisfy the route invariant.

### Mathematical route invariant

A checked route result is valid only if all of the following hold:

1. Every output point is finite and exactly representable as a JavaScript `number` coordinate.
2. The first and last output points equal the requested endpoints exactly.
3. The output has no consecutive duplicate points unless the requested endpoints are equal and the entire route is intentionally one point.
4. For equal endpoints, the result is `[S]` or the existing explicitly documented degenerate representation; the client must create no track.
5. For horizontal or vertical routes, the result is `[S,E]`, and the nonzero represented delta is finite.
6. For a non-axis route, the result is `[S,M,E]`, where `M` is finite, `M.y === S.y`, `abs(M.x-S.x) === min(abs(dx),abs(dy))` in represented arithmetic, and `abs(E.x-M.x) === abs(E.y-M.y)`.
7. Each generated segment has finite represented deltas and nonzero length.
8. The checked result must not label a route as orthogonal/45-degree unless all invariants are proven.

### Representability conditions

The intermediate waypoint is representable only when:

- both endpoint coordinates are finite;
- the required coordinate deltas can be classified without an unbounded or ambiguous subtraction;
- `L` is finite and nonnegative;
- `sx + sign(dx)*L` and `sy` are finite;
- the constructed point is not equal to `S` or `E` in a way that violates the nonzero-segment invariant;
- recomputation of the two segment deltas proves the route invariant using represented values.

A finite mathematical delta is not sufficient: the represented delta and intermediate coordinate must also be usable by downstream geometry.

### Safe behavior for an unrepresentable waypoint

The internal checked route evaluator returns `NON_REPRESENTABLE` when no valid waypoint can be proven. It must not return a duplicate waypoint or silently claim a route invariant.

The selected product policy is:

- The client route tool calls the checked evaluator.
- For `VALID`, it creates the checked segments.
- For `NON_REPRESENTABLE`, it does not create the nominal route45 polyline. It may offer an explicit direct-route fallback only if the product explicitly labels it as a direct route and the direct segment is finite and accepted by the board model. It must not label that fallback as an orthogonal/45-degree route.
- If direct routing is not accepted by the product policy, the client creates no tracks and presents a stable numerical-geometry error.
- The legacy public `route45(start,end): Point[]` signature remains unchanged. Its extreme fallback must be documented as a direct endpoint-only compatibility result or a deterministic safe result, and all production callers that require the route invariant must use the checked internal evaluator.

This resolves the direct-route versus checked-result decision: **checked internal result is authoritative; direct routing is permitted only as an explicit, separately labelled fallback after finite representability is proven.**

### Equal, horizontal, and vertical endpoints

- `S === E`: return a checked `VALID` degenerate route with no segments, or `NON_REPRESENTABLE` only if the input itself is invalid. Client creates no track.
- `sx === ex` and `sy !== ey`: return `[S,E]` only when the y delta is finite and both endpoints are finite.
- `sy === ey` and `sx !== ex`: return `[S,E]` only when the x delta is finite and both endpoints are finite.
- If a raw subtraction is non-finite, do not infer horizontal/vertical from an overflowed difference. Compare represented coordinates first, then classify the delta state.

### Client integration requirements

`Home.tsx:75` must not blindly map every returned point into tracks. The checked result must be validated for finite coordinates, duplicate points, nonzero segments, and the route invariant immediately before track creation. A defensive client guard remains required even if the geometry helper claims `VALID`.

The guard must prevent:

- zero-length PCB tracks;
- `NaN` or infinite endpoints;
- duplicate consecutive route points;
- accidental direct fallback being presented as route45;
- partial track creation if any segment fails validation.

The update must be transactional: either all checked segments are accepted or no new route segments are appended.

### Compatibility requirements

For ordinary finite board coordinates, preserve the existing two-point and three-point output, including waypoint ordering and horizontal-first convention. Existing route45 tests must remain unchanged. New extreme tests must verify safe non-creation or explicitly labelled direct fallback.

# P24D-ROTATION-CANCELLATION

### Existing contract and propagation

The P2.4-B implementation is `rotatePoint` at `shared/engineering.ts:31` and `transformLocalPoint` at `:32`. `localPads` at `:125` transforms footprint pads; `validateSchematic` at `:340` transforms pins; `evaluatePcbV2` at `:372` evaluates transformed pads. Input validation at `:481` checks finite source coordinates and finite rotation but does not prove the transformed result.

The ordinary formulas are:

```text
rx = x*cos(theta) - y*sin(theta)
ry = x*sin(theta) + y*cos(theta)
X  = ox + rx
Y  = oy + ry
```

They are mathematically correct but not sufficient as a numerical contract at extreme finite inputs.

### Separate error sources

#### 1. Trigonometric coefficient error

JavaScript `Math.sin` and `Math.cos` return rounded binary64 approximations to the mathematical coefficients. Even if multiplication and addition were exact, the coefficient errors contribute:

```text
E_coeff_x <= |x|*E_cos + |y|*E_sin
E_coeff_y <= |x|*E_sin + |y|*E_cos
```

where `E_sin` and `E_cos` are certified coefficient enclosures, not an unsupported assumption that the error is exactly one epsilon. For special angles, exact coefficient identities must be used where available:

- 0, 360: `(1,0)`
- 90: `(0,1)`
- 180: `(-1,0)`
- 270: `(0,-1)`

For 45, 135, 225, and 315 degrees, `±sqrt(1/2)` is not an exact binary64 value. Use a certified enclosure for the chosen binary64 constant rather than calling it exact.

#### 2. Multiplication rounding

Each product has a rounding error. A two-product or double-double implementation can retain a high and low component for each product. The error-free transform is only valid under its stated finite-operation assumptions; overflow and underflow must be checked before applying it.

#### 3. Addition/subtraction cancellation

Subtracting nearly equal products can lose most significant bits. Compensation preserves low-order information but does not prove that the coefficient approximation is correct. The result must carry an interval or an explicit error enclosure. A small residual is not automatically zero.

#### 4. Translation error

`transformLocalPoint` adds the rotated local coordinate to the component origin. This addition can overflow or lose low-order bits when the origin dominates the local coordinate. Translation must use compensated `TwoSum`/double-double addition with a representability check and must propagate the input rotation enclosure.

#### 5. Propagation

A transformed pad with an uncertain coordinate cannot be treated as a precise pad in pad-to-pad or track-to-pad DRC. A transformed pin with an uncertain coordinate cannot be unioned with a wire or used to assert a required-pin conclusion. Uncertainty is localized to the affected component/pad or component/pin and its directly dependent findings.

### Transform result states

The internal checked transform returns:

- `VALID`: inputs finite; output interval is finite; the rounded output is representable; the enclosure proves the result to the required binary64 output cell.
- `INDETERMINATE`: inputs finite and output interval finite, but cancellation/coefficient/rounding enclosure spans multiple representable output cells or cannot establish the required classification.
- `NON_REPRESENTABLE`: the mathematical output enclosure lies outside the finite binary64 range or translation/product overflow prevents a finite output.
- `INVALID`: non-finite input coordinate, non-finite angle, malformed shape, or unsupported runtime value.

`VALID` does not claim mathematical exactness. It claims only the stated enclosure and output-cell guarantee.

### Algorithm selection

The recommended transform engine is:

1. Normalize the angle and detect exact special-angle cases.
2. For general angles, obtain `sin`/`cos` binary64 values plus certified local coefficient enclosures. Do not claim that `Math.sin`/`Math.cos` alone are correctly rounded.
3. Compute products with two-product/double-double arithmetic when finite; retain high and low parts.
4. Combine products with compensated two-sum/two-diff.
5. Add the origin with compensated addition.
6. Propagate coefficient, multiplication, addition, and translation bounds.
7. Classify the result as `VALID`, `INDETERMINATE`, `NON_REPRESENTABLE`, or `INVALID`.

Compensated arithmetic alone is rejected because it reduces product/sum rounding but does not remove trigonometric coefficient error. A coefficient interval plus compensated arithmetic is required.

### Coefficient strategy

Accurate trigonometric coefficients are selected as follows:

- exact identities for multiples of 90 degrees;
- a deterministic angle normalization that treats equivalent full turns consistently;
- for other angles, a high-quality binary64 coefficient with a certified enclosure derived from a correctly rounded or conservatively bounded provider;
- no assumption that 45-degree coefficients are exact;
- if the coefficient enclosure cannot be bounded under the implementation’s proof model, return `INDETERMINATE` rather than fabricate precision.

### Transform integration

Public signatures remain unchanged. Existing `rotatePoint` and `transformLocalPoint` preserve ordinary outputs. Internal engineering callers use checked transforms:

- `localPads`: if a pad transform is `INDETERMINATE` or `NON_REPRESENTABLE`, mark only that pad/component geometry uncertain and prevent a pad clearance pass based on it.
- schematic pins: if a pin transform is uncertain, mark only that pin uncertain; do not union it and suppress only its required-pin conclusion.
- unaffected pads, pins, wires, and nets continue to produce findings.
- no global topology suppression is permitted.

## P24D-SHAPE-SCALE-TOLERANCE

### Existing defect

The P2.4-B strict helpers are at `shared/engineering.ts:256-261`. `strictOrientation` and `strictSegmentsIntersect` use an absolute `1e-12` determinant threshold; `strictOnSegment` uses an absolute `1e-12` coordinate expansion. `strictSegmentDistance` and `rectToRectDistance` feed these helpers, and `padToPadDistanceDetailed`/DRC consume the result at `:381`.

At width `1e-7` and a real rectangle gap of approximately `2e-13`, the determinant is around `1e-20`; the strict predicate treats separated edges as collinear and returns zero distance. Exact orientation and exact distance are different contracts: proving a determinant sign does not by itself prove a Euclidean distance.

### Predicate result states

Internal geometry predicates use only states meaningful for the operation. The shared vocabulary is:

- `VALID`: a finite numerical result or relationship is certified within its stated enclosure.
- `EXACT_CONTACT`: contact is proved by exact coordinate equality, exact dyadic orientation plus certified bounds, or an equivalent exact relation.
- `OVERLAPPING`: interiors or closed boundaries overlap, and overlap is proved rather than inferred from a tolerance.
- `SEPARATED`: a positive lower bound on distance is proved.
- `INDETERMINATE`: available bounds cannot prove contact, overlap, or positive separation.
- `NON_REPRESENTABLE`: the mathematical result or required intermediate is outside the representable output domain.
- `INVALID`: malformed or non-finite input.

Not every function exposes every state. For example, an internal orientation predicate returns sign/zero/indeterminate; a distance predicate returns a certified interval state.

### Orientation contract

For finite binary64 points `A,B,C`, define the mathematical determinant:

```text
D = (Bx-Ax)*(Cy-Ay) - (By-Ay)*(Cx-Ax)
```

The implementation may first use translated/scaled floating arithmetic, but it must attach a conservative forward-error bound. If the bound excludes zero, return the proven sign. If not, convert finite input values to exact IEEE-754 dyadics and compute the determinant sign using integer mantissas and powers of two. Exact fallback can prove `D<0`, `D=0`, or `D>0` for finite inputs; it cannot prove a result for non-finite inputs.

No fixed absolute determinant epsilon is permitted. A determinant sign is not a distance result.

### Point-on-segment contract

A point is `EXACT_CONTACT` only when:

1. exact orientation is zero or an equivalent certified collinearity result is available; and
2. exact coordinate comparisons prove the point lies within the closed endpoint box.

If the orientation is uncertain or endpoint ordering cannot be certified, return `INDETERMINATE`. Do not expand the box by an arbitrary absolute tolerance.

### Segment intersection contract

For two finite segments:

- `EXACT_CONTACT` or `OVERLAPPING` when exact orientation and endpoint/interval relations prove the relationship;
- `SEPARATED` when orientation and bounding relations prove no intersection;
- `INDETERMINATE` when the predicate cannot prove either outcome.

An indeterminate relationship must never be converted to intersection, crossing, union, or zero distance.

### Rectangle boundary relationship

Represent a rectangle by four transformed boundary segments. Before predicate evaluation, certify all transformed vertices. If any transform is uncertain, the boundary relationship is `INDETERMINATE`.

Use exact/interval segment relationships and point-in-convex-polygon predicates:

- `OVERLAPPING` if an edge intersection or certified containment proves interior overlap;
- `EXACT_CONTACT` for certified tangency/contact with no interior overlap;
- `SEPARATED` only with a positive certified distance lower bound;
- `INDETERMINATE` otherwise.

The old absolute `1e-12` determinant and on-segment policy is removed from the design target; it is not replaced by another unit-dependent epsilon.

### Rectangle/oval distance

For rectangles and ovals, the contract is a certified distance interval `[d_lo,d_hi]` with `0 <= d_lo <= d_hi` when finite:

- `EXACT_CONTACT` if contact is proven exactly;
- `OVERLAPPING` if overlap is proven;
- `SEPARATED` if `d_lo > 0` and the interval is finite;
- `VALID` for a converged positive distance interval whose width is within the numerical proof criterion used by the algorithm;
- `INDETERMINATE` if bounds do not establish contact, overlap, or positive separation;
- `NON_REPRESENTABLE` if the mathematical distance or required intermediate cannot be represented;
- `INVALID` for malformed/non-finite geometry.

For a rectangle/oval pair, exact orientation is used only for boundary and containment classification. It must not be substituted for an exact distance. The positive distance may require certified interval evaluation, interval Newton, or branch-and-bound over the segment/ellipse parameter. If an interval method cannot prove a conclusion within its finite subdivision/proof rules, it returns `INDETERMINATE`; it does not return zero.

### Distance algorithm and error model

1. Translate coordinates by a computed local origin when this is proven to reduce range without losing representability.
2. Evaluate segment and ellipse expressions with scaled interval arithmetic.
3. Track rounding outward at every interval operation.
4. Use exact dyadic comparisons for finite coordinate equality, orientation signs, and endpoint ordering.
5. Use interval Newton or certified subdivision for non-linear ellipse boundary distance.
6. Stop only when a requested classification is proven: exact contact/overlap, positive separation, or a converged finite interval satisfying the accepted numerical criterion.
7. If scale, underflow, overflow, or interval width prevents proof, return `INDETERMINATE` or `NON_REPRESENTABLE`.

Exact orientation is possible for finite binary64 inputs. Exact Euclidean distance generally is not a binary64 operation and may involve irrational values; it must be represented by a certified interval or an explicitly indeterminate result.

### Pad and DRC integration

`padToPadDistanceDetailed` retains its public union result and wrapper behavior. Internally:

- `EXACT_CONTACT`/`OVERLAPPING` map to a converged zero-distance result only when proven;
- `SEPARATED`/`VALID` map to a finite certified distance result;
- `INDETERMINATE` maps to the existing detailed `INDETERMINATE` state and then to `PCB_GEOMETRY_INDETERMINATE` in DRC;
- `NON_REPRESENTABLE` maps to the same fail-closed geometry-indeterminate path;
- no indeterminate result becomes zero distance;
- no indeterminate result becomes a clearance pass;
- no uncertainty in one pad suppresses unrelated pad, track, via, or net findings.

## Shared numerical architecture

### Layer 1 — Numeric Kernel

**Responsibilities**

- finite/invalid classification;
- exact binary64-to-dyadic conversion;
- safe translated differences and scale selection;
- outward interval primitives;
- two-sum, two-diff, two-product, and double-double operations;
- representability and non-representability checks;
- ULP/output-cell reasoning;
- conservative coefficient enclosures.

**Internal result types**

```text
FiniteScalar =
  { state: "VALID", value: number, error: Interval }
| { state: "INDETERMINATE", error: Interval, reason: string }
| { state: "NON_REPRESENTABLE", reason: string }
| { state: "INVALID", reason: string }
```

A dyadic result may additionally carry an exact sign or exact zero. Intervals are outward-rounded and must preserve `lo <= hi`.

**Input/output invariants**

- `VALID` values are finite.
- `NON_REPRESENTABLE` is never converted to `Infinity` as a valid geometry value.
- `INVALID` is reserved for malformed/non-finite input, not difficult but valid geometry.
- scaling changes classification coordinates only; it does not fabricate a scalar distance.

**Forbidden shortcuts**

- absolute determinant epsilon;
- NaN-to-zero or Infinity-to-zero;
- coordinate ceiling;
- unbounded arithmetic silently treated as finite;
- claiming exactness from a single rounded floating result.

### Layer 2 — Geometry Predicates

**Responsibilities**

- orientation sign;
- point-on-segment;
- segment intersection;
- convex boundary/containment;
- certified shape distance intervals.

**Internal result types**

```text
OrientationResult = { state: "NEGATIVE" | "ZERO" | "POSITIVE" | "INDETERMINATE" | "INVALID" }
RelationshipResult = { state: "EXACT_CONTACT" | "OVERLAPPING" | "SEPARATED" | "INDETERMINATE" | "INVALID" }
DistanceResult = { state: "VALID" | "EXACT_CONTACT" | "OVERLAPPING" | "SEPARATED" | "INDETERMINATE" | "NON_REPRESENTABLE" | "INVALID", lower?: number, upper?: number, reason?: string }
```

**Guarantees**

- `EXACT_CONTACT` and `OVERLAPPING` are proof states, not tolerance guesses.
- `SEPARATED` contains a certified positive lower bound.
- `INDETERMINATE` is conservative and never feeds an unsafe pass.

### Layer 3 — Transform Engine

**Responsibilities**

- stable angle normalization;
- special-angle exact handling;
- coefficient enclosures;
- compensated rotation and translation;
- localized transformed pad/pin state.

**Internal result type**

```text
TransformResult =
  { state: "VALID", point: Point, enclosure: IntervalPoint }
| { state: "INDETERMINATE", enclosure?: IntervalPoint, reason: string }
| { state: "NON_REPRESENTABLE", reason: string }
| { state: "INVALID", reason: string }
```

**Dependencies**

Uses Numeric Kernel intervals and compensated operations. Geometry Predicates consume only `VALID` transformed coordinates; Engineering Integration consumes all states for localized findings.

### Layer 4 — Engineering Integration

**Responsibilities**

- checked route construction and client guards;
- pad/pin transformed geometry;
- topology union only after proven relationship;
- DRC fail-closed propagation;
- stable public wrappers and finding IDs/order.

**Guarantees**

- affected uncertainty is localized;
- unrelated findings remain available;
- no false union or crossing conclusion;
- no fabricated zero distance or unjustified clearance pass;
- ordinary valid-input behavior is preserved.

## Mathematical assumptions and limitations

### Forward error versus classification error

Forward error bounds describe how far a computed scalar may be from the mathematical value. Classification error asks whether the sign, contact, overlap, or separation conclusion can be proven. A small forward error does not justify a classification when the true value lies near a boundary. Every predicate must use a bound that excludes the competing classifications before returning a decisive state.

### Exact determinant versus distance

For finite binary64 coordinates, each input is an exact dyadic rational. Orientation determinants can therefore be computed exactly with integer mantissas and exponent alignment. This proves sign and zero, not exact Euclidean distance. Distance and ellipse calculations must use certified intervals or return indeterminate.

### Overflow and underflow

- Overflow in a raw difference, product, sum, or square is a state transition requiring scaling, interval handling, or `NON_REPRESENTABLE`; it is never silently accepted.
- Underflow can erase a small determinant or distance. Exact dyadic comparison or outward intervals are required before declaring zero.
- Scaling is valid for signs and ratios only when the error model proves the transformation preserves the classification. It is not permission to emit a fabricated finite distance.
- Cancellation requires retained low parts and an uncertainty bound; a rounded residual equal to zero is not proof of exact zero.

## P2.4-C compatibility and integration strategy

### Independent implementation requirement

The contract is implementable against P2.4-B `e567acb883a0f81cb0c64d11f638b5f872511346` without first merging P2.4-C. The P2.4-C branch remains unmerged and is not a prerequisite.

### Overlapping P2.4-C functions

Potential overlap exists in:

- `safeDifference`, `safeDistance`, and scaled numeric helpers;
- exact dyadic orientation and orientation classification;
- `pointToSegmentState` and segment-intersection classification;
- `segmentIntersectionState`;
- schematic uncertainty propagation and affected wire/pin/net tracking.

P2.4-D shape predicates must not duplicate incompatible versions of these helpers. The implementation plan is:

1. Define a shared Numeric Kernel API against the P2.4-B baseline.
2. Adapt P2.4-C’s accepted orientation and localized topology semantics into that kernel when P2.4-C is later integrated.
3. Keep `CONNECT_TOLERANCE` as a topology policy only; never reuse it as a shape-distance epsilon.
4. Preserve P2.4-C’s rule that overflowed distances provably outside connectivity tolerance are outside, not indeterminate.
5. Preserve P2.4-C’s rule that uncertainty is tracked by affected wires, pins, and nets rather than globally.
6. Add compatibility tests both before and after branch integration.

### Conflict risks

- P2.4-C’s exact orientation fallback can be reused for shape orientation, but it does not solve rectangle/oval distance.
- P2.4-C’s point-to-segment fallback is connectivity-oriented and must not be assumed to certify pad clearance.
- P2.4-D transform uncertainty must feed the same localized topology model without restoring global suppression.
- A shared helper must preserve public P2.4-B wrapper error/state contracts and P2.4-C public distance behavior.

### Independent compatibility strategy

Run P2.4-D tests against:

1. exact P2.4-B baseline plus the D implementation;
2. the accepted P2.4-C remediation plus the D implementation;
3. the integrated future branch, if separately authorized.

The same oracle vectors must be used in all three modes. Differences must be classified as intentional contract changes or regressions; no branch’s behavior is assumed correct merely because it passes its own tests.

## Algorithm selection and rejected alternatives

### Route construction

**Selected:** checked route evaluator with representability proof, duplicate-point invariant, and explicit direct fallback policy.

**Rejected:** raw `Math.min(abs(dx),abs(dy))` after overflow; clamping deltas; choosing a coordinate ceiling; silently returning a direct route as if it were route45.

### Rotation

**Selected:** special-angle identities, certified coefficient enclosures, compensated/double-double products and sums, interval propagation, localized checked transform.

**Rejected:** compensated summation alone; assuming `Math.sin`/`Math.cos` are exact; treating 45-degree coefficients as exact; absolute coordinate cutoffs; silently replacing non-representable output with a finite clamp.

### Shape predicates

**Selected:** exact finite dyadic orientation where possible, scale-aware error bounds, exact endpoint ordering, certified interval distance for nonlinear shape distance, and explicit indeterminate results.

**Rejected:** fixed `1e-12` determinant/on-segment tolerance; substituting exact orientation for exact distance; converting uncertain distance to zero; using `CONNECT_TOLERANCE` for pad geometry; accepting a positive clearance from an interval that overlaps zero.

## Error propagation policy

### Pads

Each transformed pad carries its own transform state. A pad with `INDETERMINATE` or `NON_REPRESENTABLE` geometry causes only relationships involving that pad to become `PCB_GEOMETRY_INDETERMINATE`. Unrelated pad pairs and track/via findings continue.

### Pins

Each transformed pin carries its own transform state. A pin with uncertain geometry is not unioned with any wire. Its required-pin conclusion is suppressed only for that pin. Other required pins continue to produce `SCH_UNCONNECTED_REQUIRED_PIN` findings.

### Wires and nets

A shape relationship that is indeterminate marks only its affected wires and nets. No indeterminate relationship is unioned. Unrelated disconnected-net and net-name findings remain active.

### DRC

Any uncertain or non-representable pad/track/via distance produces an error-severity geometry-indeterminate result. The evaluator must not report `PCB_*_CLEARANCE` as a pass or omit the finding because a numerical operation failed.

## Detailed acceptance test specification

The following are design specifications, not implemented tests.

### Route construction tests

| Input | Expected classification | Numerical invariant | Oracle/reference | Regression purpose |
|---|---|---|---|---|
| `S===E` | `VALID`, zero segments | no duplicate segment; no client track | exact coordinate equality | deterministic degenerate behavior |
| same y, finite dx | `VALID` two-point | horizontal; finite nonzero dx | exact subtraction | preserve horizontal output |
| same x, finite dy | `VALID` two-point | vertical; finite nonzero dy | exact subtraction | preserve vertical output |
| `(0,0)` to `(80,40)` | `VALID` three-point | first horizontal; second 45-degree | exact integer oracle | ordinary output compatibility |
| `(-MAX,0)` to `(MAX,10)` | `NON_REPRESENTABLE` checked result | no duplicate waypoint; no claimed route | representability check | original defect |
| near-overflow finite delta | `VALID` only if waypoint and deltas recheck | finite points and invariant | high-precision reference | boundary behavior |
| large common offset with represented small delta | preserve ordinary classification | no unnecessary `NON_REPRESENTABLE` | exact represented-delta oracle | avoid false uncertainty |
| direct fallback enabled | explicit direct state, not route45 | client labels direct route | checked result state | resolve fallback policy |
| any checked invalid output | no tracks | transactional client update | structural invariant checker | prevent malformed PCB tracks |

### Rotation tests

| Input | Expected classification | Numerical invariant | Oracle/reference | Regression purpose |
|---|---|---|---|---|
| angles 0, 90, 180, 270, 360 | `VALID` special-angle path where representable | exact sign/swap/identity relations | exact integer/dyadic oracle | special-angle contract |
| 45, 135, 225, 315 | `VALID` or `INDETERMINATE` per enclosure | coefficient error explicitly bounded | high-precision trig reference | do not claim exact `sqrt(1/2)` |
| small board-scale points | `VALID` | existing numeric output preserved | high-precision reference | ordinary compatibility |
| equal large coordinates at 45 | `INDETERMINATE` or certified bounded result | no spurious accepted residual | high precision plus interval oracle | cancellation defect |
| opposite-sign large coordinates | `VALID`, `INDETERMINATE`, or `NON_REPRESENTABLE` as proven | no overflow silently accepted | interval reference | overflow path |
| near-maximum finite coordinates | explicit state | finite output only if interval proves finite | interval/double-double reference | representability |
| cancellation-heavy arbitrary angle | explicit error enclosure | coefficient + product + sum error included | MPFR/high precision | coefficient error coverage |
| transform with large origin | localized state after translation | translation error included | double-double reference | `transformLocalPoint` |
| transformed pad | pad-local state | uncertain pad cannot pass clearance | independent pad oracle | PCB propagation |
| transformed pin | pin-local state | uncertain pin cannot union | independent topology oracle | schematic propagation |

### Shape predicate tests

| Input | Expected classification | Numerical invariant | Oracle/reference | Regression purpose |
|---|---|---|---|---|
| rectangle tangency | `EXACT_CONTACT` | distance interval contains exactly zero by proof | rational/dyadic oracle | contact semantics |
| rectangle overlap | `OVERLAPPING` | interior overlap proven | exact orientation/containment oracle | overlap semantics |
| positive separation | `SEPARATED`/`VALID` | lower bound strictly positive | high-precision distance | no false zero |
| width around `1e-7`, gap around `1e-13` | positive separation if gap is proven | no absolute epsilon dominates scale | high precision | original defect |
| large common offsets | preserve represented relation | translation does not create false contact | exact dyadic/or interval | offset stability |
| rotated rectangles | valid/indeterminate by transform proof | transformed vertices certified | high-precision polygon oracle | rotation interaction |
| rectangle/oval boundary | contact/overlap/separation/indeterminate | exact orientation not substituted for distance | interval Newton/high precision | shape contract |
| near-degenerate positive dimensions | explicit finite/indeterminate state | no division by zero or guessed contact | interval reference | degenerate geometry |
| overflowed products | `INDETERMINATE` or `NON_REPRESENTABLE` unless proof exists | no fabricated zero | interval arithmetic | overflow behavior |
| underflowed determinants | exact dyadic or indeterminate | no guessed collinearity | exact binary64 oracle | underflow behavior |
| independent translated copies | same classification where representable | classification scale/translation consistency | independent oracle | invariance |

### Engineering regression tests

- A pad pair with real positive gap greater than the configured clearance must not report a pad-clearance violation because of the old `1e-12` rule.
- A pad pair whose interval overlaps zero must report `PCB_GEOMETRY_INDETERMINATE`, not a clearance pass.
- A transformed uncertain pad must affect only its own pair findings.
- A transformed uncertain pin must not union and must suppress only its own required-pin finding.
- An unrelated required pin must still report unconnected.
- An unrelated disconnected net must still report disconnected.
- No indeterminate relationship may produce a union, crossing conclusion, or positive clearance pass.
- Finding IDs and order for existing valid fixtures must remain stable.

## Mandatory compatibility matrix

| Contract area | Acceptance criterion |
|---|---|
| Circle/Oval | Existing Circle/Oval numeric and detailed contracts remain valid; no shape-specific regression |
| P2.4-A GJK | Boundary decisions, exhaustion, and fail-safe `INDETERMINATE` behavior unchanged |
| P2.4-B detailed/wrapper APIs | Public signatures, stable reasons, wrapper exceptions, and malformed-input behavior unchanged |
| P2.4-C numerical uncertainty | Accepted orientation, overflowed outside-threshold classification, no-false-union rule, and localized topology remain intact after later integration |
| Schematic topology | No false union; affected uncertainty localized to wires, pins, and nets |
| PCB DRC | No fabricated zero; no unjustified clearance pass; indeterminate remains error/fail-closed |
| Schema-v2 and legacy | Existing validation, dispatch, finding IDs, and order preserved |
| Public signatures | No signature changes in this phase; checked state types remain internal unless separately authorized |
| Existing route45 | Ordinary two-/three-point output and waypoint convention preserved |
| Client route integration | No duplicate or zero-length tracks; direct fallback never labelled route45; transactional update |

## Risk analysis and design decisions

### 1. Direct-route fallback versus checked route result

Decision: checked internal route result is authoritative. Direct routing is permitted only as an explicit product fallback after a finite direct segment is verified and labelled direct. The client must not use an unverified public array as proof of route45 invariants.

### 2. Accurate coefficients versus compensated arithmetic

Decision: both are required. Accurate or certified coefficient enclosures address trigonometric error; compensated/double-double products and sums address arithmetic rounding and cancellation. Either one alone is insufficient.

### 3. Error-bound propagation

Decision: each operation returns or contributes an enclosure. Rotation and translation compose enclosures; shape predicates consume only certified transformed coordinates or return indeterminate. No caller may discard an uncertainty state to preserve a convenient numeric path.

### 4. Exact orientation versus approximate distance

Decision: exact finite dyadic orientation is used for sign and equality classification only. Shape distance remains interval-certified or indeterminate. Orientation zero never implies zero Euclidean distance without point-on-segment and boundary proof.

### 5. Localized uncertainty

Decision: uncertainty is keyed to affected pads, pins, wires, and nets. Global suppression is forbidden. Affected objects may produce geometry-indeterminate errors; unrelated conclusions continue.

### 6. P2.4-B/P2.4-C branch integration

Decision: implement the Numeric Kernel against P2.4-B first, then adapt accepted P2.4-C helpers through compatibility adapters. Do not merge or assume P2.4-C. Add the same oracle suite before and after later integration.

### 7. Performance costs

- Fast path: ordinary finite board-scale values use translated/scaled binary64 arithmetic.
- Exact dyadic orientation: invoked only near a classification bound or on overflowed differences.
- Double-double transforms: invoked for large/cancellation-heavy coordinates or when the fast error bound is insufficient.
- Interval ellipse distance: used only for nonlinear shape relationships; subdivision has a deterministic proof budget, but exhaustion returns indeterminate rather than a guessed result.
- No arbitrary iteration cap may change accepted GJK semantics. Any interval proof budget must be a resource safeguard whose exhaustion is explicitly `INDETERMINATE`, not a geometry conclusion, and requires separate policy approval if introduced.

## Performance and regression risks

1. Exact dyadic conversion and big-integer determinant arithmetic can be more expensive for adversarial coordinates. Cache normalized dyadic representations where safe and keep the fast sign path.
2. Double-double and interval operations increase allocation and arithmetic cost in transformed pad/pin paths. Measure ordinary-board overhead and avoid invoking slow paths unnecessarily.
3. Certified ellipse distance can be substantially slower than the existing 96-step heuristic. Use conservative broad-phase bounds and return indeterminate when proof cannot complete, while preserving fail-closed behavior.
4. New localized states can change finding presence in previously indeterminate cases. Existing finding IDs/order for valid inputs must be locked before implementation.
5. Client route guards may expose extreme-coordinate errors that were previously persisted as malformed tracks. This is intentional and must be communicated as a correctness improvement.

## Explicit unresolved questions

1. Which exact public legacy behavior should `route45` return for `NON_REPRESENTABLE` when no client-level checked API is available: direct endpoints or a stable exception/error channel? The implementation must select one without changing the public signature and document it before coding.
2. What coefficient enclosure provider is acceptable for arbitrary-angle `sin`/`cos` under the project’s dependency restrictions? A standard-library result without a certified bound is insufficient for the `VALID` state.
3. What interval width/output-cell criterion should define a `VALID` transformed coordinate for downstream engineering use? It must be derived from representability and the error proof, not an arbitrary PCB-unit tolerance.
4. What deterministic proof budget is acceptable for interval ellipse distance, and how should budget exhaustion be reported while preserving the no-fabricated-zero rule? This is not a GJK iteration cap and must not alter GJK policy.
5. Should the public numeric `rotatePoint` remain a best-effort compatibility helper while only internal callers become checked, or should a future API expose the transform state? No public API change is authorized in this phase.

## Final approval checklist

Implementation must not begin until all are answered or explicitly accepted:

- [ ] Exact route invariant and direct-fallback product policy approved.
- [ ] Checked internal route result designed without public signature change.
- [ ] Coefficient enclosure strategy selected for arbitrary angles.
- [ ] Special-angle and 45-degree behavior specified.
- [ ] Double-double/compensated arithmetic proof and overflow handling reviewed.
- [ ] Transform states and localized pad/pin propagation reviewed.
- [ ] Exact orientation versus certified distance boundary reviewed.
- [ ] Rectangle/oval interval-distance algorithm and exhaustion semantics approved.
- [ ] P2.4-B-first implementation plan confirmed.
- [ ] P2.4-C compatibility adapters and branch-conflict tests defined.
- [ ] Required oracle and regression test matrix accepted.
- [ ] Circle/Oval, GJK, API, DRC, schema, topology, and route compatibility confirmed.
- [ ] Separate explicit authorization granted for source/test implementation.

## Publication boundary

This document is the sole P2.4-D numerical remediation contract deliverable. It contains design, mathematical constraints, and test specifications only. It does not authorize implementation, P2.4-E, source changes, test changes, or pull-request activity.
