# Phase 6.1 P2.4-B — Geometry API Contract Hardening

**Final verdict: ACCEPTED**

## Scope and repository separation

This implementation was authorized by the Phase 6.1 P2.4-B execution authorization. Code and tests were changed only in `soheil6913/-PCB-Studio-Pro`. This report is published only in `soheil6913/PCB`.

The approved base was verified before implementation:

- Approved P2.4-A base SHA: `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- P2.4-A branch: `fix/phase6-1-p2-4-a-boundary-safety-20261123`
- P2.4-A remote HEAD at preflight: `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- `main` at preflight: `a98384bbfc3296947b90f5254a03a77b11fdc8a9`
- P2.4-A working tree: clean in the fresh temporary clone
- PR #3: open, Draft, unmerged; head `fix/phase6-1-p1-explicit-v2-dispatch-20261122`; base `main`

A single isolated branch was created from the approved SHA, and P2.4-A was not modified:

```text
fix/phase6-1-p2-4-b-geometry-api-contract-20261124
```

Final source HEAD:

```text
e567acb883a0f81cb0c64d11f638b5f872511346
```

The remote branch was verified to point to exactly that SHA. No merge, rebase, reset, force-push, PR modification, or `main` modification was performed.

## Mandatory API and call-site inventory

The authoritative public geometry surface was re-inventoried against the approved base in `shared/engineering.ts`.

### Scalar helpers

- `distance(a: Point, b: Point): number`: finite points; Euclidean distance; no thrown error contract.
- `measure(start: Point, end: Point, grid?: number): Measurement`: points plus optional numeric grid; returns distance and grid units; non-positive grid uses pixel distance.
- `snapToGrid(point: Point, grid: number): Point`: returns the original point for a non-positive grid.
- `rotatePoint(point: Point, degrees: number): Point`: numeric point rotation.
- `transformLocalPoint(origin: Point, local: Point, rotation?: number): Point`: local-to-world transform.
- `segmentsIntersect(aStart, aEnd, bStart, bEnd): boolean`: segment intersection including degenerate segments.
- `segmentDistance(aStart, aEnd, bStart, bEnd): number`: zero for intersecting segments; otherwise segment distance.
- `route45(start, end): Point[]`: two- or three-point orthogonal/45-degree route.

### Detailed geometry APIs

- `gjkWithinDistance(a: Pad, b: Pad, clearance: number, maxIterations?: number): GjkDecision`: valid pads, finite non-negative clearance, and positive integer budget; returns `WITHIN_DISTANCE`, `OUTSIDE_DISTANCE`, or `INDETERMINATE`.
- `padToPadDistanceDetailed(a: Pad, b: Pad, options?: GeometryOptions): GeometryDistanceResult`: valid pads and options containing only optional `gjkMaxIterations`; returns finite `CONVERGED` or `INDETERMINATE`.

### Numeric compatibility wrappers

- `padToPadDistance(a: Pad, b: Pad): number`: preserves its signature and valid-input numbers; throws `GeometryCalculationError` for malformed or indeterminate calculations.
- `viaToPadDistance(pad: Pad, via: EngineeringVia): number`: preserves its signature and valid-input numbers; malformed runtime pad/Via geometry throws `GeometryCalculationError`.

### Validation and evaluator boundaries

- `validateSchematic(project)`: validates runtime schematic input and returns structured `SCH_INVALID_INPUT` findings for malformed direct input.
- `validatePcb(project, options?)`: validates the project root and geometry options, returning structured `PCB_INVALID_INPUT` or `PCB_INVALID_OPTIONS` findings before evaluation.
- `runDesignRules(project)`: validates complete project data and returns the established `PROJECT_INVALID` path for malformed projects; it retains the `validatePcb`/`runDesignRules` separation.
- `validateProjectJsonDetailed(value)`: returns `{ ok, errors }` with stable paths and messages.
- `validateProjectJson(value)`: type guard backed by the detailed validator.
- `migrateProjectJson(value)`: returns a validated project or `null`.

All internal call sites were located in `shared/engineering.ts` and the test suite. The production UI import in `client/src/pages/Home.tsx` uses `measure`, `route45`, `runDesignRules`, `validateProjectJson`, and `validateProjectJsonDetailed`. All other geometry imports are test/fixture call sites under `shared/`. No call site required a public signature change.

Existing compatibility coverage reviewed included:

- `shared/engineering.test.ts`
- `shared/engineering.p2.test.ts`
- `shared/engineering.v2-compatibility.test.ts`
- `shared/phase4.gjk.test.ts`
- `shared/phase4_1.gjk-convergence.test.ts`
- `shared/phase5_1.geometry-validation.test.ts`
- `shared/phase5_2.drc-adversarial.test.ts`
- `shared/phase5_3.independent-oracles.test.ts`
- `shared/phase5_3_8.rotated-rectangle.test.ts`
- `shared/phase5_4.drc-boundary-semantics.test.ts`
- `shared/phase5_5.drc-policy-certification.test.ts`
- `shared/phase6-1-p2-2.circle-oval-contract.test.ts`
- `shared/phase6-1-p2-4-a-boundary-safety.test.ts`

## Changed files

Only these three files were committed on the P2.4-B branch:

- `shared/engineering.ts`
- `shared/phase6-1-p2-4-b-geometry-api-contract.test.ts`
- `GEOMETRY_API_CONTRACT.md`

No dependency manifest or lockfile was changed. No P2.4-A test file was changed. The shared production file retains the approved P2.4-A sparse-array and runtime-options validation; P2.4-B adds only the detailed-API runtime guards and wrapper hardening described below.

## Implementation details

### Detailed API hardening

`gjkWithinDistance` now classifies malformed pads, clearance, and direct runtime budgets as `INDETERMINATE` with stable reasons instead of leaking property-access or numeric errors. Existing positive-budget exhaustion remains unchanged and still returns:

```text
iteration limit exhausted before convergence
```

`padToPadDistanceDetailed` validates both runtime pads and the options object before accessing shape fields. Unknown shapes, malformed points, non-positive/non-finite dimensions, unequal Circle dimensions, malformed options, and unsafe integer budgets cannot produce a plausible finite result or a runtime `TypeError`.

Stable boundary reasons include:

- `invalid first pad geometry`
- `invalid second pad geometry`
- `invalid geometry options`

Caller-supplied invalid iteration values retain the established `invalid iteration budget` classification inside the detailed result. Valid Circle/Oval, rotated geometry, GJK exhaustion, and P2.4-A boundary behavior remain intact.

### Numeric wrappers

`padToPadDistance` continues to delegate to the detailed result and throws the existing `GeometryCalculationError` whenever the result is indeterminate.

`viaToPadDistance` now validates runtime pad and Via geometry before calculation and throws `GeometryCalculationError` for malformed inputs. Existing valid-input Circle/Oval numeric results remain unchanged, including the established direct Via compatibility behavior.

### Documentation and focused tests

`GEOMETRY_API_CONTRACT.md` documents the exported scalar helpers, detailed result classifications, wrapper exceptions, validation boundaries, and fail-closed DRC behavior.

The new focused test file covers:

- malformed points and pads;
- unknown shapes;
- invalid dimensions and unequal Circle dimensions;
- malformed options;
- detailed `INDETERMINATE` results;
- direct GJK malformed-input classification;
- `GeometryCalculationError` wrapper behavior;
- valid Circle/Oval numerical fixtures;
- fail-safe DRC behavior when GJK is indeterminate.

## Verification

Frozen dependency installation was required in the fresh clone and succeeded with exit code 0. The lockfile and dependency manifests were not modified.

Exact required commands and results:

```text
pnpm exec vitest run shared/phase6-1-p2-4-b-geometry-api-contract.test.ts shared/phase6-1-p2-2.circle-oval-contract.test.ts
exit 0
2 test files passed; 31 tests passed

pnpm exec vitest run shared/engineering.v2-compatibility.test.ts
exit 0
1 test file passed; 46 tests passed

pnpm check
exit 0

pnpm test
exit 0
16 test files passed; 240 tests passed

pnpm build
exit 0
```

The complete local verification log is retained at the execution workspace as `verification.log`. The full suite includes the unchanged P2.4-A boundary-safety tests, Circle/Oval tests, GJK convergence tests, DRC tests, and server tests.

Final local working tree status before publication was clean after commit. The exact source commit was `e567acb883a0f81cb0c64d11f638b5f872511346`.

## CI evidence

GitHub Actions ran on the exact final source HEAD:

- Workflow: `Engineering verification`
- Run: `45347825537`
- Job: `verify` / `138286582006`
- Tested HEAD: `e567acb883a0f81cb0c64d11f638b5f872511346`
- Result: success
- CI TypeScript check: success
- CI automated tests: success
- CI production build: success

Run URL: https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45347825537
Job URL: https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45347825537/job/138286582006

## Limitations and unresolved issues

The scalar helpers retain their existing typed-function contracts; callers receiving untrusted runtime values should use the established validation boundaries before invoking them. This phase does not add numerical-extreme remediation, coordinate ceilings, topology indeterminacy propagation, schema-v3 behavior, model/evaluator redesign, DRC policy changes, UI/database/workflow changes, or dependency changes. P2.4-C and P2.4-D were not started.

The implementation does not silently coerce malformed values. It preserves fail-closed behavior: malformed or indeterminate detailed geometry cannot become a finite clearance result, and numeric compatibility wrappers do not return plausible distances in those cases.

## Final verdict

**ACCEPTED** — P2.4-B Geometry API Contract Hardening was implemented from the approved P2.4-A SHA, verified locally and in CI on the exact final HEAD, committed to the authorized isolated branch, and pushed without modifying P2.4-A, `main`, or PR #3. Work stops here pending any further explicit authorization; P2.4-C and P2.4-D have not begun.
