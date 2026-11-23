# PCB Studio Pro — Phase 6.1 P2.4
## Geometry API Remediation Design

**Status:** DESIGN COMPLETE — proposal only. No production code, tests, configuration, workflow, branch, or pull request was changed.

## 1. Executive decision

P2.4 converts the source-grounded findings in P2.3 into a minimal, staged remediation plan. The design prioritizes the two trust-boundary defects first (sparse arrays and nullable geometry options), then establishes a coherent contract for direct geometry APIs, addresses numerical indeterminacy without inventing a coordinate limit, and corrects the general-slope defect in `route45`.

The implementation must preserve:
- the existing schema-v2 dispatch and the distinction between full-project `runDesignRules` and PCB-only `validatePcb`;
- the approved Circle/Oval contract from P2.2;
- existing valid-input DRC geometry semantics and finding identities/order unless a separately reviewed regression demonstrates a necessary change;
- all current public function signatures in the first remediation pass wherever feasible.

**No P0 issue was identified in P2.3.** P2.4 is not a manufacturing-readiness or certification claim.

## 2. Verified baseline and evidence

| Item | Verified value |
|---|---|
| Source repository | `soheil6913/-PCB-Studio-Pro` |
| Source baseline | `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` |
| Baseline branch | `fix/phase6-1-p2-2-circle-oval-contract-20261123` |
| Main at inspection | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| Existing PR #3 | Open / Draft / not merged; preserve unchanged |
| Report repository | `soheil6913/PCB` |

Source-grounded files inspected at the exact P2.2 SHA:
- [`shared/engineering.ts`](https://github.com/soheil6913/-PCB-Studio-Pro/blob/192cac1e3b0293a9ce41d9c06f01a91ae70333fe/shared/engineering.ts)
- [P2.2 Circle/Oval contract tests](https://github.com/soheil6913/-PCB-Studio-Pro/blob/192cac1e3b0293a9ce41d9c06f01a91ae70333fe/shared/phase6-1-p2-2.circle-oval-contract.test.ts)
- [package.json](https://github.com/soheil6913/-PCB-Studio-Pro/blob/192cac1e3b0293a9ce41d9c06f01a91ae70333fe/package.json)

P2.3 source audit is recorded in report-repository commit [`6a297531e3e550c1d409af556e9d16dedf8f6037`](https://github.com/soheil6913/PCB/commit/6a297531e3e550c1d409af556e9d16dedf8f6037). That audit reports zero successful tests because `vitest` was unavailable in its checkout. P2.4 therefore treats its findings as source-confirmed, not dynamically reproduced.

## 3. Finding-to-remediation map

| P2.3 finding | Priority | Proposed treatment | Compatibility risk |
|---|---:|---|---|
| F-02 — sparse arrays bypass `forEach`/ `map` validation | P1 at JS/API trust boundaries; P2 for ordinary JSON ingress | Reject every sparse index with a stable path-specific validation error | Low if validation only becomes stricter for malformed runtime arrays |
| F-03 — `validatePcb(..., null)` can throw on GJK path | P2 | Validate options before evaluator entry; return one stable DRC input/options diagnostic | Low–medium; callers relying on throw must be identified |
| F-04 — direct geometry exports have inconsistent malformed-input behavior | P2 / API contract | Document and implement a staged contract; detailed APIs become fail-closed | Medium; exported helpers may have external consumers |
| F-05 — finite extreme coordinates can overflow intermediate arithmetic | P2 hardening | Preserve finite schema acceptance for now; propagate numerical uncertainty instead of false geometric conclusions | Medium–high in schematic topology |
| F-01 — `route45` fails general slopes | P2 | Correct the bend coordinate and test all octants and ratios | Medium; route shape changes for affected slopes |
| F-06 — unclear public-vs-trusted geometry API role | DESIGN | Keep exports for compatibility in this pass; explicitly document preconditions and result semantics | Low initially |

## 4. Detailed design

### 4.1 Sparse-array rejection — first implementation priority

**Problem:** JavaScript array iteration methods such as `forEach`, `map`, and `some` skip absent indices. A sparse array can therefore pass nested validation without validating the missing element. This applies not only to the four root collections but also to nested collections.

**Required behavior:**
1. Introduce one internal dense-array validator that checks every integer index from `0` through `length - 1` using an own-property check.
2. Emit a deterministic diagnostic for each missing index, for example:
   - path: `tracks[0]`
   - message: `must not contain sparse array holes`
3. Run this check before any iterator-based nested validation.
4. Cover all validated arrays:
   - root: `components`, `wires`, `tracks`, `vias`;
   - nested: `components[*].pins`, `components[*].footprintGeometry.pads`;
   - optional: `junctions`, `pad.layers`.
5. For `pad.layers`, preserve the existing exact-two-distinct-layer contract while also rejecting holes. Do not silently compact, fill, or normalize sparse arrays.
6. Ensure `validateProjectJsonDetailed`, `validateSchematic`, `validatePcb`, and `runDesignRules` return stable diagnostics and do not throw for sparse collections.

**Implementation constraint:** do not change the approved Circle/Oval checks or the PCB-only root-field boundary as part of this patch. Prefer a small reusable helper and targeted loops over a broad validator rewrite.

### 4.2 Runtime validation for geometry options

**Problem:** the default parameter `options = {}` handles `undefined`, not explicit `null`. `validatePcb` can pass `null` through to `padToPadDistanceDetailed`, where a GJK fallback dereferences `options.gjkMaxIterations`.

**Required behavior:**
- Validate the runtime options value at the public `validatePcb` boundary before invoking `evaluatePcbV2`.
- Accept omitted/`undefined` options as the existing default.
- Reject `null`, arrays, primitives, and malformed option objects deterministically.
- If `gjkMaxIterations` is present, require a positive safe integer. Do not silently treat explicit `null`, NaN, fractions, zero, or negative values as the default.
- Return one stable `DrcResult` error (prefer a distinct `PCB_INVALID_OPTIONS` rule ID so malformed project data and malformed evaluator configuration are not conflated).
- Keep `runDesignRules(project)` behavior unchanged; it does not expose a geometry-options argument in the current API.
- Do not introduce an arbitrary maximum iteration budget in this remediation without a separate performance policy and evidence. If a cap is later required, specify and test it as a separate contract.

The internal evaluator should receive a normalized, non-null `GeometryOptions` object only.

### 4.3 Direct geometry API contract — staged, non-breaking first pass

P2.3 established that direct exports differ in behavior: some return a number or boolean, `padToPadDistanceDetailed` can return `INDETERMINATE`, `padToPadDistance` throws `GeometryCalculationError` on indeterminate results, and malformed nested objects can throw before a result is produced.

**Do not remove exports or change their signatures wholesale in P2.4.** First pass:

1. Add explicit API documentation stating whether each export accepts only prevalidated inputs or performs runtime validation.
2. Make the detailed geometry entry points (`gjkWithinDistance` and `padToPadDistanceDetailed`) return `INDETERMINATE` for malformed runtime geometry/options instead of leaking `TypeError`.
3. Keep numeric compatibility wrappers (`padToPadDistance`, `viaToPadDistance`) numeric for valid inputs; on invalid or indeterminate calculations, throw the existing `GeometryCalculationError` with a stable reason.
4. For scalar helpers (`distance`, `measure`, `snapToGrid`, `rotatePoint`, `transformLocalPoint`, `segmentsIntersect`, `segmentDistance`, `route45`), document finite-input preconditions and add guards only where needed to prevent silent NaN/Infinity from being mistaken for a valid result. Do not silently coerce malformed points.
5. Keep private evaluator helpers private. Do not export new low-level support-mapping or simplex helpers.

Before implementation, search all repository call sites and tests for every exported geometry function. If a signature or exception behavior is consumed outside `shared/engineering.ts`, preserve it or provide a compatibility wrapper.

**Contract target:** detailed geometry results are explicit about uncertainty; legacy numeric wrappers never return a plausible finite distance for malformed input.

### 4.4 Extreme finite coordinates and numerical uncertainty

**Problem:** `Number.isFinite` admits values near `Number.MAX_VALUE`; later subtraction, projection, products, or midpoint calculations can overflow. P2.3 found that some DRC paths already convert non-finite clearance to `INDETERMINATE`, while schematic connectivity can treat a NaN comparison as simply false.

**Required design:**
- Do not add a hard coordinate ceiling in P2.4. Physical units and the maximum supported board-coordinate domain are not yet established strongly enough to justify an arbitrary schema restriction.
- Audit intermediate arithmetic in `pointToSegment`, `segmentDistance`, `distance`, GJK support/dot products, pad localization, and schematic wire/junction connectivity.
- Where arithmetic cannot be proven finite and determinate, propagate an explicit indeterminate state; never map numerical failure to a definitive “not connected” or “clear” result.
- For DRC, retain the existing fail-safe rule: indeterminate geometry must not be reported as clearance success.
- For schematic topology, add an explicit indeterminate diagnostic or equivalent fail-closed outcome when connectivity cannot be decided numerically. Do not silently omit the edge.
- Use translated/scaled calculations where they are mathematically valid, and verify them against independent oracles. Do not replace a numerical uncertainty with an arbitrary epsilon or coordinate clamp.
- Treat the choice of a future maximum coordinate range as a separate domain decision requiring explicit units, board-size assumptions, import/export compatibility review, and boundary tests.

### 4.5 `route45` general-slope correction

**Problem:** current midpoint calculation uses `min(abs(dx), abs(dy))` as the X displacement while leaving Y at the start value. For ratios such as 80:20, the second segment is neither axis-aligned nor 45 degrees.

**Proposed minimal formula:**

```ts
const diagonal = Math.min(Math.abs(dx), Math.abs(dy));
const bend = {
  x: start.x + Math.sign(dx) * (Math.abs(dx) - diagonal),
  y: start.y + Math.sign(dy) * (Math.abs(dy) - diagonal),
};
return [start, bend, end];
```

This produces one axis-aligned leg and one 45-degree leg for arbitrary nonzero `dx`/`dy`, while retaining the existing direct two-point result for horizontal, vertical, and equal-magnitude diagonal cases. For the existing 80:40 fixture, the bend remains (40, 0); for 80:20 it becomes (60, 0); for 20:80 it becomes (0, 60), relative to a start at (0,0).

This is a geometric dogleg helper only. It is not collision-aware routing and must not claim obstacle avoidance, clearance, or connectivity validation. Preserve input endpoints and avoid mutating caller-owned points.

## 5. Required regression matrix

### Sparse arrays
- A hole at index 0, middle index, and final index for each root collection.
- Holes in pins, footprint pads, junctions, and pad layer arrays.
- Dense arrays containing explicit `undefined` must be rejected through the ordinary element validator; distinguish this from a sparse hole.
- Assert stable error paths/messages, no thrown exceptions, and no silent omission.
- Include direct calls to all public validation boundaries.

### Options
- omitted, `undefined`, `null`, array, string, number, and object;
- `gjkMaxIterations`: omitted, 1, positive safe integer, 0, negative, fractional, NaN, Infinity, explicit null, and unsafe integer;
- use a rotated, non-coaxial Oval pair that is proven to enter the GJK path; analytic fast paths must not make the test vacuous.

### Direct geometry contracts
- malformed/missing points and Pads; unknown shape; zero/negative/non-finite dimensions; unequal Circle; invalid Via drill/diameter; malformed options;
- detailed API returns explicit indeterminate; numeric wrappers throw the documented geometry error;
- valid existing fixtures retain their exact expected values and result classifications.

### Numerical extremes
- finite coordinates near `Number.MAX_VALUE`;
- subtraction overflow between opposite-sign large coordinates;
- large common offset with small representable delta;
- GJK support/dot overflow;
- topology cases where an indeterminate distance must not become a definitive disconnected result;
- compare against independent exact or interval oracles and retain unresolved cases as unresolved.

### `route45`
- `dx:dy` ratios 4:1, 1:4, 2:1, 1:2, 1:1, axis-aligned, and near-axis/near-diagonal epsilon boundaries;
- all four sign quadrants;
- for every returned segment, assert it is horizontal, vertical, or has equal absolute X/Y displacement within the defined tolerance;
- assert endpoints are unchanged and inputs are not mutated.

### Preservation gates
- Keep all P2.2 Circle/Oval contract tests unchanged and passing.
- Keep existing P1 schema dispatch and legacy compatibility goldens unchanged.
- Keep the separate semantics of `validatePcb` and `runDesignRules`.
- Do not weaken existing DRC boundary, GJK exhaustion, or fail-safe tests.

## 6. Implementation sequence and acceptance gates

**P2.4-A — Boundary safety**
- Sparse-array rejection.
- Runtime options validation.
- Focused regression tests.
- Gate: malformed inputs produce stable diagnostics; no evaluator throw; existing valid-input findings unchanged.

**P2.4-B — Geometry API contract**
- Document exports and preconditions.
- Harden detailed geometry entry points and numeric wrappers.
- Call-site inventory and compatibility tests.
- Gate: no malformed input returns a plausible success value; public signatures remain compatible unless a separately documented exception is approved.

**P2.4-C — Numerical uncertainty**
- Robust distance/segment calculations and schematic topology uncertainty propagation.
- Independent oracle comparisons.
- Gate: no overflow/NaN path becomes a definitive clearance pass or false connectivity conclusion.

**P2.4-D — Routing helper**
- Correct `route45` midpoint and add slope/quadrant tests.
- Gate: every output segment obeys the documented axis/45-degree contract.

Do not combine these into one large refactor. Each subphase should be isolated, reviewed, and independently testable.

## 7. Execution and repository safeguards

- Start each implementation subphase from a fresh, clean worktree at the exact approved P2.2 baseline SHA unless the user explicitly approves a different base.
- Use a dedicated branch per remediation subphase. Do not work on `main`.
- Do not alter PR #3, protected branches, P1/P2.1/P2.2 verification branches, or prior audit branches.
- Do not merge, rebase, cherry-pick, release, tag, deploy, or force-push.
- Keep source implementation and audit/report archive separate: source code belongs in `soheil6913/-PCB-Studio-Pro`; reports belong in `soheil6913/PCB`.
- Run focused tests, full tests, `pnpm check`, and production build only when dependencies are available. Record exact commands, exit codes, test counts, and commit SHA. A missing test executable means **blocked / zero tests run**, never passed.
- If a proposed fix changes existing valid geometry semantics, stop and document the compatibility impact before proceeding.

## 8. Explicit non-goals

- No Circle/Oval contract redesign.
- No schema-version dispatch changes.
- No DRC rule-policy redesign or new manufacturing standards claims.
- No arbitrary maximum-coordinate policy.
- No broad rewrite of geometry algorithms or removal of public exports.
- No UI, database, server, workflow, or dependency changes unless a later, separately approved finding requires them.

## 9. Final design conclusion

The safest order is **sparse-array boundary validation → options validation → direct geometry contract → numerical uncertainty → route45 correction**, each as a small independently verifiable change. The first two are the strongest trust-boundary remediations and should be implemented before expanding geometry API semantics. Extreme-coordinate policy must remain evidence-driven and unit-aware. Circle/Oval and existing DRC compatibility contracts remain frozen.

**P2.4 design is complete. Implementation has not started.**
