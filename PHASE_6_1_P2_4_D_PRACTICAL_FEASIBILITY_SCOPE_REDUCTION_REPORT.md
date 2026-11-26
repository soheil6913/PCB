# PHASE 6.1 — P2.4-D Practical Feasibility and Scope Reduction Review

## Decision

**SCOPE_REDUCTION_NOT_JUSTIFIED**

This is an engineering decision report only. It does not authorize P2.4-D implementation, production-source changes, test changes, a P2.4-C merge, or a change to `main`.

The smallest defensible conclusion from the actual source is not that P2.4-D can safely adopt a bounded production domain. It is that the current application contract accepts finite binary64 rotations and finite coordinates/dimensions without a documented upper bound, while production DRC paths depend on rotated transforms and generic rectangle/oval geometry. A bounded checked domain could be proposed as a **new contract**, but it cannot be inferred as an existing application guarantee and therefore cannot be used now to remove proof obligations without a deliberate compatibility change.

## Authoritative references and method

The review used the exact source references requested:

| Reference | Role |
|---|---|
| `e567acb883a0f81cb0c64d11f638b5f872511346` | P2.4-B implementation baseline |
| `327fc0479031279b889ea1dd1140a23d4abe442f` | P2.4-C remediation compatibility reference |
| `3ed17c246dadf80eab73f81bfc775845d582dbf1` | P2.4-B parent context |
| `21b7487eec431dcb993a44d0d642a33644141526` | P2.4-C remediation parent context |

Inspection was read-only and source-grounded. The P2.4-C source was not merged. Existing tests were inspected but not modified or treated as production telemetry.

## 1. Source-grounded call-site inventory

| API or calculation | Production use observed at the P2.4-C reference | Numerical consequence |
|---|---|---|
| `rotatePoint` | Exported scalar helper; used by `transformLocalPoint` and angle-dependent geometry | Public behavior is ordinary `Math.sin`/`Math.cos` arithmetic; no angle ceiling is enforced by this helper. |
| `transformLocalPoint` | `localPads` transforms footprint pads; schematic pin processing transforms pin positions | Component and pin/pad world coordinates depend on arbitrary finite rotation values. |
| `route45` | Imported by `client/src/pages/Home.tsx`; used by the client route-creation workflow | The route calculation itself uses endpoint subtraction and a midpoint formula; it does not require arbitrary-angle trigonometry. Its finite representability still needs a checked contract for extreme endpoints. |
| Rectangle/oval calculations | Pad transforms, axis-aligned half extents, support mappings, rectangle corners, rectangle/rectangle, rectangle/oval, oval/oval common-axis paths, point/ellipse and segment/ellipse paths | Generic rotated rectangles/ovals use direct sine/cosine and/or angle-dependent local coordinates. These are production DRC paths, not test-only utilities. |
| GJK | `padToPadDistanceDetailed` falls back to `gjkWithinDistance` for cases not proved by analytic dispatch; DRC consumes the detailed result | GJK exhaustion or numerical uncertainty is represented as `INDETERMINATE`; it cannot be replaced by a bounded-domain assumption without preserving this fail-closed behavior. |
| Segment predicates | Track/track, connectivity, and related DRC calculations use `segmentsIntersect`, `segmentDistance`, and point/segment paths | These paths are mostly arithmetic and P2.4-C adds orientation uncertainty handling, but they still receive the unrestricted finite coordinate inputs accepted by validation. |
| DRC evaluator | `validatePcb` checks track/track, pad/edge, track/pad, pad/pad, via/pad, track/via, and via/via relationships | Non-finite or indeterminate geometry is intended to produce `PCB_GEOMETRY_INDETERMINATE` Error findings and must not become a clear/pass result. |

Specific source anchors in `shared/engineering.ts` at the P2.4-C reference include: `DEFAULT_BOARD` and constants near lines 24–26; `rotatePoint`, `transformLocalPoint`, and `route45` near lines 57–59; runtime pad/options guards near lines 162–185; `localPads` and angle-dependent extents near lines 196–205; `supportPad` and `gjkWithinDistance` near lines 212–324; rectangle/oval helpers and detailed dispatch near lines 326–371; track/pad and DRC paths near lines 382 and 513–527; and schema validation near lines 612–631.

`client/src/pages/Home.tsx` imports `route45` and calls `runDesignRules`; the route workflow is therefore an actual application caller, while the geometry and DRC callers are in the shared production module.

## 2. Observed input domains and evidence

### 2.1 What production validation actually guarantees

The source validates:

- points and coordinates as finite numbers;
- component and pad rotations as finite numbers;
- board origin as finite and board width/height as positive finite values;
- pad, track, via, drill, diameter, and rule dimensions as finite, with positive/non-negative conditions where applicable;
- circle width and height consistency;
- geometry options through a public validator requiring a positive safe-integer `gjkMaxIterations`.

It does **not** impose a documented upper bound on:

- component or pad rotation magnitude;
- board origin, board width, or board height;
- component, pin, pad, track, via, or junction coordinate magnitude;
- positive pad, track, via, or board dimensions, other than finiteness/positivity.

The default board is `{ x: 150, y: 112, width: 660, height: 328, edgeClearance: 10 }`, but custom board values are accepted under the finite/positive checks. The default is not an application-wide scale limit.

### 2.2 Production workflow evidence

The client route workflow supplies ordinary drawing coordinates, but the source review found no validator, persistence contract, UI constraint, or schema rule that converts those observed ordinary values into a guaranteed global numerical domain. Component and pad rotations are loaded from project data and validated only for finiteness. A future domain restriction would therefore change accepted project inputs, not merely optimize an already-existing invariant.

No production corpus, persisted-project sample, telemetry export, or benchmark dataset was present in the reviewed source that could establish a high-percentile angle, coordinate, dimension, or clearance range. Accordingly, no measured production distribution is claimed here.

### 2.3 Test and adversarial ranges (not production limits)

The existing source tests demonstrate that compatibility and numerical behavior are expected beyond the default board scale:

| Fixture evidence | Observed values | Interpretation |
|---|---:|---|
| `phase4.gjk.test.ts` | coordinates around `1_000_000_000`; dimensions up to `200_000`; gaps around `1e-8`; rotated cases including `45°` | Existing regression expectations cover large translations, scale disparity, tiny gaps, and rotations. |
| `phase4_1.gjk-convergence.test.ts` | coordinates around `1_000_000_000`; dimensions up to `200_000`; rotations including `45°`, `180°`, `-90°`; budgets `0` and `1` | Convergence and compatibility tests intentionally exercise nontrivial scales and rotations. |
| `phase5_1.geometry-validation.test.ts` | `1e9` translated coordinates; widths as small as `1e-6`; tiny clearances; malformed/non-finite inputs | Scale-sensitive and fail-closed behavior is tested, but fixture values are not evidence of user production frequency. |
| `phase5_2.drc-adversarial.test.ts` and P2.4-C tests | dimensions around `2e201`, `Number.MAX_VALUE`, `Number.MAX_VALUE`-scale coordinates, overflowed differences | The implementation is expected to avoid false passes at extreme finite inputs. |
| independent/oracle suites | angles such as `15`, `23`, `30`, `31`, `37`, `45`, `60`, `90`, `123.456`, negative angles, and seeded angles | Arbitrary-looking finite angles are part of the proof/compatibility corpus; they do not prove user telemetry. |
| P2.4-A boundary-safety tests | `0`, `1`, `1.5`, `256`, `257`, `Number.MAX_SAFE_INTEGER`, `NaN`, `Infinity`, and unsafe values for iteration options | Boundary validation is deliberately tested separately from geometry-domain limits. |

The correct conclusion is therefore: the source proves broad **accepted-input** behavior, not a bounded **production-frequency** distribution.

## 3. Are arbitrary finite angles genuinely required?

For `route45`, no. The implementation uses endpoint arithmetic and can be checked independently for finite differences, waypoint representability, duplicate points, and endpoint preservation.

For production transforms and DRC geometry, yes in the contract sense currently exposed by the source: the application accepts every finite component/pad rotation, and the production paths use the resulting angle. The source contains no evidence that rotations are restricted to multiples of 90 degrees, a small degree interval, or a finite approved list. Existing tests cover non-orthogonal values such as `15°`, `23°`, `30°`, `31°`, `37°`, `45°`, `60°`, and `123.456°`, plus negative and combined component/pad rotations.

Some calculations can avoid arbitrary-angle trigonometry:

- `route45` is arithmetic-only.
- Circle/circle distance is rotation-independent.
- Some common-axis oval cases can use analytic axis distances after a safe axis/common-angle test.
- Some axis-aligned rectangle and oval cases are analytic.
- Segment intersection and many point/segment calculations do not intrinsically need trigonometric functions.

Those reductions do not cover component/pin transforms, rotated pad transforms, generic rotated rectangle/oval support mappings, rotated rectangle corners, rotated support functions, or arbitrary-angle local-coordinate calculations. They reduce the number of trig calls but do not justify removing arbitrary-angle proof obligations from the supported contract.

## 4. Can a bounded checked domain be adopted safely now?

Not on the present evidence. A proposed domain such as:

```text
finite coordinates and dimensions within explicitly chosen bounds;
finite rotations within an explicitly chosen magnitude bound;
finite derived values and certified trig/output enclosures;
```

would be a new behavioral contract. It is not an inferred current application guarantee. Choosing bounds from the default board, common fixtures, or developer intuition would violate the requirement not to invent application limits.

A future checked-domain contract could be implementation-reviewable only if all of the following are specified and tested:

1. the exact accepted domain and units;
2. migration and user-facing behavior for existing out-of-domain projects;
3. a checked transform and geometry API distinct from best-effort compatibility wrappers where necessary;
4. `INVALID`, `INDETERMINATE`, and `NON_REPRESENTABLE` classifications with stable propagation rules;
5. a proof that every unsupported path reaches a DRC Error, never a clear/pass;
6. representative persisted-project evidence or an explicit product decision accepting the compatibility restriction;
7. independent trig, output-cell, and nonlinear-distance proof artifacts.

Absent those artifacts, scope reduction is not mathematically defensible as a current-production simplification.

## 5. Unsupported-input behavior and fail-closed safety

Returning `INDETERMINATE` can preserve DRC safety, but only when uncertainty is localized and every relevant consumer treats it as non-acceptance. The reviewed P2.4-C path provides the required direction:

- detailed pad distance returns `INDETERMINATE` rather than a plausible finite distance;
- numeric wrappers throw `GeometryCalculationError` rather than returning a fabricated number;
- DRC emits `PCB_GEOMETRY_INDETERMINATE` with Error severity and instructs the caller not to accept the board;
- P2.4-C localizes topology uncertainty rather than suppressing unrelated findings globally;
- unresolved relationships are not unioned.

This is sufficient to support a **conditional** future checked-domain design, not sufficient to declare that all current callers already handle every newly introduced unsupported-domain state. Before implementation, every geometry consumer, route persistence path, UI path, and compatibility wrapper must be audited for accidental fallback, dropped errors, or false clear behavior.

## 6. Geometry scale limits and distance-budget reassessment

### Scale limits

No source-grounded geometry scale ceiling is available. The default board dimensions are a default, not a limit; custom boards accept arbitrary finite positive dimensions. Tests intentionally cover both very small gaps/dimensions and extreme finite values. A scale restriction would need to be a new product/schema/API decision, not a proof shortcut inferred from current workflows.

### Distance budget

The proposed deterministic subdivision budget (`4096` cells, `32768` interval evaluations, depth `32`) is a design parameter, not a measured application requirement. The source contains no production geometry dataset or telemetry from which to estimate the distribution of near-tangent, high-curvature, tiny-gap, or generic rotated rectangle/oval pairs. Existing tests show representative adversarial categories and many exact analytic cases, but they do not establish budget sufficiency for production.

Therefore:

- broad-phase and analytic dispatch should remain first;
- budget exhaustion must return `INDETERMINATE`, never `CONVERGED`, zero distance, or a clear result;
- adequacy must be benchmarked with an actual certified evaluator on a disclosed corpus, including ordinary persisted projects if available, near tangencies, tiny scales, large translations, rotation combinations, and overflow boundaries;
- any stated expected cost is an estimate until measured.

The existing 64-step binary search inside `padToPadDistanceDetailed` and the separate `gjkMaxIterations` option must not be conflated with a new rectangle/oval subdivision budget. The budget scope should be explicit per pair and per evaluator.

## 7. P2.4-B geometry-options validation inconsistency

The exact P2.4-C source has two different predicates:

- `validateGeometryOptions` rejects non-numbers, non-safe-integers, values below `1`, `NaN`, `Infinity`, zero, negative values, and fractional values with the documented invalid-options finding.
- `validRuntimeGeometryOptions` accepts a numeric `NaN`, `Infinity`, zero, negative, or fractional `gjkMaxIterations` because it only rejects values matching `(integer && >= 1 && !safeInteger)` as invalid.

Consequently, direct detailed-API calls can pass malformed numeric options through the first runtime guard and later reach `gjkWithinDistance`, where they are classified as `invalid iteration budget`. The public `validatePcb` path is stricter and reports invalid options earlier. This is a real P2.4-B/P2.4-C contract inconsistency, principally at direct detailed-API runtime validation.

Recommendation: resolve and lock one classification before P2.4-D checked-geometry integration. The likely intended rule is one positive safe integer everywhere, with malformed options returning the documented `invalid geometry options` classification at the detailed API boundary. No source or test change is made by this report.

## 8. Proof obligations eliminated versus unavoidable

### Obligations that a future explicitly narrowed contract could reduce

Only conditionally, and only after the new contract is approved and enforced, scope reduction could reduce:

- huge-angle range-reduction cases outside the documented angle interval;
- huge-coordinate cancellation cases outside the documented coordinate box;
- overflow/underflow combinations excluded by a documented scale envelope;
- some output-cell and transformed-coordinate cases made unreachable by the checked domain;
- some nonlinear distance cases excluded by a certified shape/scale envelope.

These are potential reductions, not currently available exemptions.

### Obligations that remain unavoidable now

- legacy `route45` compatibility and checked representability semantics;
- arbitrary finite angle behavior for currently accepted component/pad rotations;
- certified sine/cosine enclosures or an explicitly fail-closed alternative;
- transformed-coordinate output-cell criteria, including subnormals, signed zero, ties, binade boundaries, and overflow;
- generic rotated rectangle/oval distance correctness and deterministic exhaustion semantics;
- GJK exhaustion and P2.4-C numerical uncertainty compatibility;
- DRC propagation proving no false pass from invalid, non-finite, unsupported, or indeterminate geometry;
- public wrapper compatibility (`rotatePoint`, `transformLocalPoint`, `padToPadDistance`, `viaToPadDistance`);
- options validation consistency;
- independent oracle and benchmark evidence.

## 9. Risks of restricting the domain

Restricting angles or coordinates can reject existing saved projects, imported footprints, rotated component-plus-pad combinations, and direct API callers. It can also create silent divergence if public wrappers continue to return values while internal checked paths reject the same input. A domain check placed only in DRC may leave route creation, transformation, persistence, or schematic connectivity with inconsistent semantics. A domain check placed only in schema validation changes migration and compatibility behavior and requires product ownership, documentation, and tests.

The most serious safety risk is an unsupported-input fallback that is treated as clear, omitted, coerced to zero, or converted into an ordinary finite distance. Any future restriction must fail closed at every consumer and must preserve the existing P2.4-C localized-uncertainty behavior.

## 10. Recommended implementation-review sequence

1. Resolve the direct detailed-API options-validation inconsistency and document the single accepted budget predicate.
2. Freeze compatibility vectors for ordinary and extreme `route45`, `rotatePoint`, and `transformLocalPoint` behavior before adding checked internals.
3. Specify, with product/API approval, whether a new bounded domain is actually acceptable; do not derive it from the default board or tests.
4. If a bounded domain is approved, add a validator and explicit state propagation first; prove unsupported inputs cannot reach a DRC clear path.
5. Implement and independently review the trig enclosure/range-reduction artifact, including exact constants, remainder bounds, outward rounding, and output-cell logic.
6. Implement the certified rectangle/oval evaluator only after its interval bounds and deterministic budget are specified; retain analytic fast paths and fail-closed exhaustion.
7. Verify compatibility against both P2.4-B and the unmerged P2.4-C reference, including localized topology uncertainty, wrapper exceptions, GJK exhaustion, and DRC findings.
8. Measure the evaluator on a disclosed representative corpus. Until such data exists, label performance and budget adequacy as estimates, not facts.

## 11. Estimated engineering complexity (estimate, not measured duration)

| Workstream | Complexity estimate | Basis |
|---|---|---|
| Source/domain contract and migration policy | Medium–High | New accepted-input semantics, compatibility review, user-facing failure behavior, and schema/API documentation. |
| Checked transforms and output-cell machinery | High | Binary64 cell boundaries, ties, subnormals, overflow, interval propagation, and public-wrapper compatibility. |
| Certified arbitrary-angle trig kernel | High–Very High | Range reduction, pi bounds, approximation coefficients/remainder proof, outward rounding, independent oracle corpus, and runtime feasibility. |
| Rectangle/oval certified evaluator | High | Interval geometry, deterministic priority queue, proof-preserving subdivision, exhaustion semantics, and adversarial validation. |
| DRC/state propagation audit | Medium–High | Every geometry consumer must preserve fail-closed behavior without false passes or global suppression. |
| Independent verification and benchmark corpus | Medium–High | Requires oracle generation, boundary vectors, persisted-project or representative corpus acquisition, and reproducible measurements. |

These are engineering-complexity labels, not measured durations or delivery promises.

## Final verdict

**SCOPE_REDUCTION_NOT_JUSTIFIED**

The evidence justifies reducing work by retaining arithmetic/analytic fast paths and by considering a future explicitly approved checked-domain contract. It does not justify claiming that current production call sites already operate inside a bounded angle or geometry-scale domain. Until such a contract is deliberately introduced with explicit fail-closed behavior and independent proof artifacts, P2.4-D scope reduction is not approved for implementation review.
