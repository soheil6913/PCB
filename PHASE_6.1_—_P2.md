# PHASE 6.1 — P2.4-D Independent Engineering Audit and Remediation Design

## Final engineering verdict

**ACCEPTED FOR DESIGN**

The independent audit confirms three source-grounded geometry defects in the required P2.4-B baseline. They are reproducible with finite IEEE-754 inputs, are outside the accepted P2.4-C remediation, and justify a narrowly scoped P2.4-D design. No implementation is authorized or performed by this report.

The findings are:

- `P24D-ROUTE45-OVERFLOW`: `route45` can emit a duplicate waypoint and a non-45-degree segment when the coordinate delta overflows.
- `P24D-ROTATION-CANCELLATION`: `rotatePoint` can produce a huge spurious residual from catastrophic cancellation for finite large coordinates; transformed pins and pads inherit it.
- `P24D-SHAPE-SCALE-TOLERANCE`: rectangle/oval distance helpers use an absolute `1e-12` orientation and on-segment tolerance, producing false zero distance at small geometric scales.

These are correctness and availability defects, not evidence against the accepted P2.4-A, P2.4-B, or P2.4-C decisions.

## Exact baseline and repository state

- Source repository: `soheil6913/-PCB-Studio-Pro`
- Independent audit source baseline: P2.4-B commit `e567acb883a0f81cb0c64d11f638b5f872511346`
- P2.4-A reference: `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- P2.4-C original baseline: `21b7487eec431dcb993a44d0d642a33644141526`
- Accepted but unmerged P2.4-C remediation: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Existing source `main`: `a98384bbfc3296947b90f5254a03a77b11fdc8a9`
- Report repository: `soheil6913/PCB`

The inspected P2.4-B ancestry is:

```text
P2.4-A  3ed17c246dadf80eab73f81bfc775845d582dbf1
   |
P2.4-B  e567acb883a0f81cb0c64d11f638b5f872511346
   |
P2.4-C original  21b7487eec431dcb993a44d0d642a33644141526
   |
P2.4-C remediation  327fc0479031279b889ea1dd1140a23d4abe442f
```

Remote read-only verification confirmed that source `main` remains at `a98384bbfc3296947b90f5254a03a77b11fdc8a9`, the original P2.4-C branch remains at `21b7487eec431dcb993a44d0d642a33644141526`, and the accepted remediation branch remains at `327fc0479031279b889ea1dd1140a23d4abe442f`. The source working tree was clean before and after the audit. No source branch, pull request, implementation, test, dependency, configuration, merge, rebase, reset, or history operation was performed.

The accepted P2.4-C report and diff were inspected only as reference. The three finding functions below are textually unchanged between the P2.4-B baseline and accepted P2.4-C remediation, so P2.4-D does not depend on merging P2.4-C.

## Audit methodology

The audit used the exact P2.4-B tree, not the current remediation tree as a substitute baseline. The work was source-grounded and read-only:

1. Inspected `shared/engineering.ts`, all geometry callers, the public API boundaries, validation paths, schematic topology, PCB DRC paths, and the existing engineering and phase-specific tests.
2. Compared the P2.4-B source with the accepted P2.4-C source to exclude already-addressed numerical-uncertainty findings.
3. Traced call chains from exported geometry helpers into client routing and PCB/schematic evaluators.
4. Exercised minimal reproductions against the unchanged implementations. The reproductions use finite coordinates and do not alter source or tests.
5. Distinguished false classifications from conservative `INDETERMINATE` outcomes. A fail-closed outcome was not counted as a false-pass defect without a concrete correctness failure.
6. Reviewed existing tests for coverage gaps and checked the accepted Circle/Oval, GJK, API-wrapper, and DRC contracts as preserved constraints.

## Inspected files and functions

### Primary source

- `shared/engineering.ts`
  - `distance`, `rotatePoint`, `transformLocalPoint`, `route45`
  - `segmentsIntersect`, `segmentDistance`, `pointToSegment`
  - `strictOrientation`, `strictOnSegment`, `strictSegmentsIntersect`, `strictSegmentDistance`
  - `pointInConvexPolygon`, `rectToRectDistance`, `rectToOvalDistance`
  - `localPads`, `padToPadDistanceDetailed`, `segmentToPadDistance`
  - `validateSchematic`, `validatePcb`, `runDesignRules`
  - `validateProjectJsonDetailed` and finite-coordinate validation
- `shared/engineering.test.ts`
- `shared/phase4.gjk.test.ts`
- `shared/phase4_1.gjk-convergence.test.ts`
- `shared/phase5_2.drc-adversarial.test.ts`
- `shared/phase5_3.independent-oracles.test.ts`
- `shared/phase6-1-p2-2.circle-oval-contract.test.ts`
- `shared/phase6-1-p2-4-a-boundary-safety.test.ts`
- `shared/phase6-1-p2-4-b-geometry-api-contract.test.ts`

### Callers and contracts

- `client/src/pages/Home.tsx:75` calls `route45` and converts every returned segment into a PCB track.
- `shared/engineering.ts:125` (`localPads`) transforms footprint-local pads using `transformLocalPoint`.
- `shared/engineering.ts:340` transforms schematic pin coordinates before topology union and required-pin evaluation.
- `shared/engineering.ts:372` collects transformed pads for PCB DRC.
- `shared/engineering.ts:381` consumes `padToPadDistanceDetailed` for pad-clearance findings.
- `GEOMETRY_API_CONTRACT.md` states that `route45` returns a two- or three-point orthogonal/45-degree route and documents the public transformation helpers.

## Confirmed finding P24D-ROUTE45-OVERFLOW

### Source and call chain

- Source: `shared/engineering.ts:33` in the P2.4-B baseline.
- Caller: `client/src/pages/Home.tsx:75`, which maps each returned point to a PCB track.
- Related contract: `GEOMETRY_API_CONTRACT.md`, route45 is documented as returning a two- or three-point orthogonal/45-degree route.

The implementation computes `dx = end.x - start.x`, `dy = end.y - start.y`, chooses `diagonal = Math.min(Math.abs(dx), Math.abs(dy))`, and constructs the waypoint as `start.x + Math.sign(dx) * diagonal`.

### Triggering condition

A finite endpoint difference overflows to `Infinity`, while the other coordinate difference remains finite and nonzero. The waypoint addition then rounds back to the start coordinate or otherwise cannot represent a valid intermediate point.

### Concrete reproduction

```ts
route45(
  { x: -Number.MAX_VALUE, y: 0 },
  { x: Number.MAX_VALUE, y: 10 },
)
```

Observed result:

```text
[
  { x: -1.7976931348623157e+308, y: 0 },
  { x: -1.7976931348623157e+308, y: 0 },
  { x:  1.7976931348623157e+308, y: 10 }
]
```

The first segment is zero length. The second segment has an infinite represented x delta rather than a 45-degree diagonal. This is not a valid two- or three-point orthogonal/45-degree route.

### Expected versus actual behavior

- Expected: either a valid two- or three-point route satisfying the documented route invariant, or a deterministic safe fallback that does not create duplicate consecutive points.
- Actual: a duplicate waypoint is returned and the client creates a zero-length track followed by an unclassifiable extreme segment.

### Engineering impact

The route tool can persist a degenerate PCB track. Downstream DRC and editing behavior then operate on geometry that does not satisfy the route helper’s contract. The defect is especially relevant because finite coordinates are accepted by validation and the client uses every returned segment without filtering.

### Severity

**Medium-High.** The defect can create invalid or misleading PCB route geometry, although ordinary board-scale coordinates are unaffected.

### Proposed reproduction test

Add a design-approved test for the exact input above and assert:

- no duplicate consecutive points;
- every returned segment has finite, nonzero represented deltas unless the requested endpoints are equal;
- the result either satisfies the existing orthogonal/45-degree route contract or follows the approved extreme-range fallback policy.

Also test large common offsets, opposite-sign extremes, horizontal/vertical cases, equal endpoints, and a finite near-overflow delta.

### Recommended remediation strategy

Introduce an internal checked-delta classification for `route45`:

1. Compute coordinate deltas with overflow detection and scale-aware comparison.
2. Preserve the existing output exactly for ordinary representable deltas.
3. If the intended intermediate coordinate cannot be represented, choose an explicit contract-preserving fallback—preferably the direct `[start, end]` route rather than a duplicate waypoint—or return a documented safe result through a new internal route evaluator while keeping the public signature stable.
4. Reject duplicate consecutive output points before the client converts points to tracks.
5. Do not invent a coordinate ceiling or a new geometric tolerance.

The chosen fallback must be documented in the geometry contract and must not silently claim a 45-degree route when the represented coordinates cannot express one.

## Confirmed finding P24D-ROTATION-CANCELLATION

### Source and call chain

- Source: `shared/engineering.ts:31` (`rotatePoint`) and `:32` (`transformLocalPoint`) in the P2.4-B baseline.
- Pad caller: `shared/engineering.ts:125` (`localPads`) and `:372` (`evaluatePcbV2` pad collection).
- Pin caller: `shared/engineering.ts:340` (`validateSchematic` pin transformation).
- Input validation: `shared/engineering.ts:481` validates finite component coordinates and finite rotation, but does not validate the transformed result.

The implementation uses the standard two-product rotation formula directly:

```ts
x * cos - y * sin
x * sin + y * cos
```

### Triggering condition

Finite, very large coordinates with a rotation where two nearly equal large products should cancel. The inputs pass the existing finite-coordinate and finite-rotation validation.

### Concrete reproduction

```ts
rotatePoint(
  { x: Number.MAX_VALUE, y: Number.MAX_VALUE },
  45,
)
```

Observed result from the baseline-equivalent implementation:

```text
{ x: 1.99584030953472e+292, y: Infinity }
```

The x result is a large spurious residual caused by cancellation; mathematically, the x component is approximately zero for equal inputs at 45 degrees. The y component is beyond the representable finite range for these exact extreme inputs, but the x residual alone demonstrates the classification/accuracy defect.

### Expected versus actual behavior

- Expected: the transformation either returns a numerically justified result with a documented uncertainty classification, or routes the transformed geometry through a checked fail-closed path when the result cannot be trusted.
- Actual: the public transformation returns a finite but grossly inaccurate residual for one component and a non-finite component for the other, while the input was accepted as valid.

### Engineering impact

`localPads` can place a transformed pad at an artificial coordinate around `1e292`; transformed schematic pins can similarly be displaced before connectivity analysis. In the non-finite case, PCB DRC produces a geometry-indeterminate result, but the finite residual case can contaminate topology or clearance calculations without being recognized as invalid transformed geometry. This is an accuracy and availability defect in the shared transformation primitive.

### Severity

**High for extreme-coordinate engineering data; Medium for ordinary application use.** The ordinary UI coordinate range does not approach the trigger, but the public API accepts all finite numeric coordinates and the validator presents them as valid.

### Proposed reproduction test

Add tests that:

- exercise equal large coordinates at 45 degrees and assert a bounded, scale-aware cancellation error or an explicit indeterminate classification;
- verify transformed pad and pin callers do not consume an unbounded residual as valid geometry;
- cover rotations 0, 90, 180, 270, 45, and 135 degrees;
- cover finite values near the largest safe scale and ordinary board-scale values;
- preserve existing exact/near-exact transformation behavior for normal coordinates.

### Recommended remediation strategy

Do not change public signatures in the design phase. Introduce an internal checked transform used by DRC/topology callers:

1. Compute products and sums with compensated two-product/two-sum arithmetic or an equivalent double-double error estimate.
2. Use scale-aware residual bounds to distinguish a trustworthy transformed coordinate from cancellation-dominated output.
3. Preserve the ordinary public numeric helper behavior for normal finite inputs.
4. When a transformed pad or pin cannot be justified, propagate a localized geometry-indeterminate state to the affected pad/pin rather than accepting a fabricated location or globally suppressing unrelated findings.
5. Keep Circle/Oval and P2.4-B detailed/wrapper contracts unchanged.

The implementation must not add a coordinate ceiling or arbitrary epsilon policy.

## Confirmed finding P24D-SHAPE-SCALE-TOLERANCE

### Source and call chain

- Sources: `shared/engineering.ts:256-261` in the P2.4-B baseline.
- `strictOrientation` uses raw determinant arithmetic.
- `strictOnSegment` uses an absolute `1e-12` coordinate tolerance.
- `strictSegmentsIntersect` classifies any determinant with absolute magnitude at most `1e-12` as zero.
- `strictSegmentDistance` and `rectToRectDistance` use this predicate at `:259` and `:261`.
- PCB DRC consumes the resulting pad distance at `:381`.

These strict helpers are separate from the public P2.4-C-remediated connectivity predicate and are unchanged by accepted P2.4-C.

### Triggering condition

Small valid rectangles whose determinant scale is far below `1e-12`, with a real positive gap smaller than `1e-12`. The absolute tolerance dominates the geometry scale and converts parallel separated edges into collinear/on-segment edges.

### Concrete reproduction

```ts
const a = {
  id: "a", number: "1", position: { x: 0, y: 0 },
  width: 1e-7, height: 1e-7, shape: "rect", layer: "F.Cu",
};
const b = {
  id: "b", number: "1", position: { x: 0, y: 1e-7 + 2e-13 },
  width: 1e-7, height: 1e-7, shape: "rect", layer: "F.Cu",
};
const actual = padToPadDistance(a, b);
```

The rectangles are disjoint with a positive vertical gap of approximately `2e-13`. The observed result is:

```text
actual === 0
```

The relevant determinant for the short edges is on the order of `1e-20`, so `strictSegmentsIntersect` treats it as zero; `strictOnSegment` then accepts the separated endpoint under its absolute `1e-12` expansion.

### Expected versus actual behavior

- Expected: a positive pad-to-pad distance approximately equal to the real gap, with DRC comparing that distance against the configured clearance.
- Actual: zero distance is returned, causing a positive-clearance DRC to report a pad-to-pad violation even when the real gap exceeds the configured clearance.

### Engineering impact

This is a scale-dependent false violation. It can reject a geometrically clear design and can make pad-clearance results depend on coordinate units rather than only on the represented geometry. The current fail-closed policy prevents this particular scenario from becoming an unsafe clearance pass, but false violations are still an engineering correctness defect.

### Severity

**Medium.** It is conservative rather than an unsafe pass in the demonstrated direction, but it can produce incorrect DRC failures and blocks valid designs at small scales.

### Proposed reproduction test

Add a rectangle-distance test at several scales, including the exact `1e-7` width and `2e-13` gap case, and assert that:

- disjoint positive gaps remain positive;
- pad-to-pad DRC compares the positive result to the rule threshold;
- true tangency and overlap remain zero;
- ordinary board-scale Circle/Oval and rectangle contracts remain unchanged.

Repeat with translated common offsets and rotated rectangles after the chosen predicate design is defined.

### Recommended remediation strategy

Replace the strict helper’s absolute determinant and on-segment tolerances with a robust predicate whose classification is scale-aware and whose uncertainty state is explicit. The preferred design is an internal orientation/segment-distance classifier with:

- translated/scaled floating evaluation;
- a justified error bound;
- exact fallback for finite IEEE-754 inputs where required;
- `INDETERMINATE` propagation into pad-distance and DRC rather than a guessed zero;
- no new arbitrary geometric tolerance.

The implementation must preserve the existing Circle/Oval behavior, the detailed/wrapper API contract, and fail-closed DRC semantics.

## Rejected hypotheses and observations

### P2.4-C orientation and topology findings

Not reopened. The accepted P2.4-C report and source changes address determinant zeroing, overflowed connectivity-threshold classification, and global topology suppression. These were treated as reference constraints, not as P2.4-D findings. P2.4-D remains independently designable from the P2.4-B baseline.

### P2.4-A GJK iteration policy

Not reopened. The exact P2.4-A checkpoint and accepted boundary/exhaustion contract were preserved. The audit found no separate, independently reproduced defect that requires changing GJK iteration semantics.

### P2.4-B API wrapper behavior

Not reopened. Existing P2.4-B contract tests explicitly cover malformed pads, malformed options, numeric-wrapper exceptions, Circle/Oval behavior, and fail-closed DRC. The audit did not find a separate wrapper-signature or contract inconsistency.

### Raw ellipse overflow as a separate finding

Observed as a potential availability concern for extreme finite radii and coordinates: ellipse formulas can become non-finite during squaring even when inputs are finite. It was not promoted to a separate confirmed finding because the existing `GeometryDistanceResult` and DRC paths classify the resulting calculation as indeterminate/fail-closed, and a complete independent false classification was not established beyond the already confirmed scale-sensitive strict rectangle predicate. It should remain a P2.4-D design question and receive boundary tests.

### General GJK precision concerns

Not promoted. The implementation has explicit invalid/non-finite/duplicate-support/exhaustion states and existing convergence tests. Without a separate reproducible false `WITHIN_DISTANCE` or false `OUTSIDE_DISTANCE` classification, this remains an observation rather than a finding.

## Proposed P2.4-D scope

P2.4-D should be limited to:

1. A scale-aware, checked route-construction policy for overflowed or unrepresentable deltas, with duplicate-waypoint prevention.
2. A robust transform path for large-coordinate rotation and translation, including localized uncertainty propagation to transformed pads and pins.
3. A shared robust shape boundary/intersection predicate for strict rectangle/oval distance helpers, replacing the fixed absolute `1e-12` policy.
4. Adversarial tests and independent oracles for all three findings.
5. Compatibility tests proving preservation of Circle/Oval behavior, P2.4-A GJK boundary/exhaustion guarantees, P2.4-B detailed/wrapper contracts, P2.4-C numerical-uncertainty corrections, fail-closed DRC behavior, schema-v2/legacy behavior, and route45 ordinary-coordinate output.

P2.4-D should not merge or depend on the P2.4-C branch as a prerequisite. It should be implementable against the P2.4-B source baseline, with accepted P2.4-C behavior treated as a separate compatibility target if a later integration is authorized.

## Remediation architecture

### Internal result types

Use internal checked result types for route construction, transforms, orientation, segment relationship, and shape distance. Each result should distinguish:

- conclusively valid/classified;
- conclusively outside or separated;
- exact contact/overlap;
- indeterminate due to representability or error bounds.

Do not expose new states through existing public signatures unless separately approved. Existing wrappers should preserve their documented throw/indeterminate behavior.

### Numeric policy

- Translate before computing local predicates where it improves conditioning.
- Scale only for classification; do not fabricate a finite scalar distance from an overflow.
- Use a defensible error bound and exact IEEE-754 fallback where finite inputs permit it.
- Use localized uncertainty sets for DRC/topology conclusions.
- Do not use fixed absolute determinant epsilons, coordinate ceilings, arbitrary iteration caps, clamping, or NaN-to-zero conversion.

### Route policy

Preserve ordinary route45 outputs byte-for-byte where possible. For unrepresentable extreme deltas, explicitly choose and test a safe fallback that cannot produce duplicate points or claim a geometric invariant it cannot represent.

### Transform policy

Keep public helper signatures stable. Add checked internal transforms for engineering callers, with compensated arithmetic and an uncertainty/error-bound path. Preserve ordinary UI behavior and ensure transformed non-finite or untrusted geometry is fail-closed and localized.

### DRC policy

The existing fail-closed policy remains mandatory. A positive-clearance result may not be reported from an indeterminate shape calculation. A conservative violation is acceptable only when the predicate proves it; guessed zero is not acceptable.

## Test strategy

### Independent numerical oracles

- Use integer/rational or exact dyadic oracles independent of the production predicate for orientation and segment relationships.
- Use high-precision reference calculations for route deltas, rotation residuals, and small-scale rectangle gaps.
- Include finite extremes, subnormal-adjacent values where valid, common offsets, cancellation pairs, and translated/scaled equivalents.

### Required new adversarial tests

- `route45` opposite-sign overflow with no duplicate waypoint.
- Route invariants for finite large and ordinary coordinate ranges.
- Rotation cancellation at 45/135 degrees and transformed pad/pin propagation.
- Small-scale parallel rectangle gaps around and below the former `1e-12` threshold.
- True tangency, overlap, separation, and translated equivalents for rectangle and oval boundaries.
- DRC positive-clearance versus violation decisions around the exact computed gap.
- Explicit indeterminate behavior when exact classification is not justified.

### Existing regression suites

Run without changing expected valid-input behavior:

- P2.2 Circle/Oval contract tests.
- P2.4-A GJK boundary and exhaustion tests.
- P2.4-B detailed/wrapper API contract tests.
- Accepted P2.4-C numerical-uncertainty tests.
- GJK convergence and independent-oracle tests.
- DRC adversarial and boundary-semantics tests.
- Schema-v2/legacy dispatch and validation tests.
- Client route integration tests if route behavior is changed.

## Regression and compatibility matrix

| Area | Required compatibility outcome |
|---|---|
| Public signatures | No signature changes without separate approval |
| `route45` ordinary inputs | Existing two-/three-point output preserved |
| Circle/Oval | Existing distance and rotation contracts preserved |
| P2.4-A GJK | Boundary, exhaustion, and fail-safe semantics unchanged |
| P2.4-B API | Detailed result states and numeric-wrapper errors unchanged |
| P2.4-C | Accepted numerical-uncertainty behavior remains available; no global suppression returns |
| Schematic topology | No false union; uncertainty remains localized |
| PCB DRC | No false clearance pass; indeterminate remains fail-closed |
| Schema v2/legacy | Existing validation and dispatch behavior unchanged |
| Route client | No duplicate tracks or unverified route invariant |
| Normal-scale geometry | Existing valid results and finding IDs/order preserved |

## Risks and unresolved questions

1. The public `route45` signature cannot express `INDETERMINATE`; the approved design must choose between a direct-route fallback and a separate checked internal result without silently changing ordinary behavior.
2. Compensated rotation arithmetic can reduce cancellation but cannot make an unrepresentable mathematical result finite. The threshold for accepting a transformed point must be justified without introducing an arbitrary tolerance.
3. Exact dyadic orientation is tractable for finite inputs, but exact distance-to-ellipse and rotated-shape calculations require a separate error-bound design.
4. The existing `strictSegmentsIntersect` helpers are used internally for shape distances, while the public segment predicate has a separate contract. The implementation should avoid accidentally changing public schematic connectivity semantics while unifying shape predicates.
5. DRC finding order and IDs must remain stable for all existing valid and invalid fixtures.
6. Extreme-coordinate tests must distinguish a mathematically unrepresentable result from a numerically unstable but representable result.

## Explicit out-of-scope items

- Implementing P2.4-D source or tests.
- Merging P2.4-C or modifying any source branch.
- Reopening accepted P2.4-A, P2.4-B, or P2.4-C findings without new evidence.
- P2.4-E or any later phase.
- UI redesign, database changes, schema changes, dependency changes, or public API redesign.
- New coordinate ceilings, arbitrary epsilon policies, arbitrary GJK iteration caps, clamping, or fabricated finite distances.
- Changes to fail-closed DRC policy, Circle/Oval contracts, or P2.4-B wrapper semantics.

## Publication and verification boundary

Only this design report is intended for publication to `soheil6913/PCB`. No source file, test file, or implementation artifact is copied into the report repository. Before publication, verify that the source working tree and source `main` remain unchanged, the P2.4-C baseline and accepted remediation references remain intact, and the report commit contains only this file.

No P2.4-D implementation is authorized by this report. A separate explicit authorization is required before any source or test changes begin.
