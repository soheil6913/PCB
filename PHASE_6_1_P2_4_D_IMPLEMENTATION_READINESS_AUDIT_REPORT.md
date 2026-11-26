# PHASE 6.1 — P2.4-D Implementation Readiness Audit

## 1. Executive decision

**NOT_READY_FOR_IMPLEMENTATION**

The exact P2.4-B and P2.4-C commits are valid Git objects, but neither is an ancestor of the current source `main`. The options-validation inconsistency is therefore an issue in the unmerged P2.4-C reference, not a defect verified in the currently deployed source `main`.

A smallest targeted correction can be specified precisely and is independently actionable as a future, isolated implementation task. It must not be combined with the unresolved P2.4-D checked-transform, arbitrary-angle trigonometric-certification, or certified rectangle/oval-distance work. Overall P2.4-D is not implementation-ready because those proof obligations remain open and the proposed P2.4-C state is not merged into `main`.

This is a read-only/design-only audit. No production source, test, branch, `main`, public API, or application contract was modified. P2.4-C was not merged.

## 2. Verified repository and commit state

### Documentation repository

- Repository: `soheil6913/PCB`
- Documentation `origin/main`: `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`
- Published scope-reduction report branch: `docs/phase-6-1-p2-4-d-practical-feasibility-20261126`
- Published scope-reduction report commit: `7a2045848a3fdec8ca380b5a0986cf74f4014c47`

### Source repository

The read-only source checkout reports source `main` at:

- `a98384bbfc3296947b90f5254a03a77b11fdc8a9` — `test: lock schema-v2 Via clearance contract`

The requested references were verified as follows:

| Reference | Object and parent | Relationship to source `main` |
|---|---|---|
| P2.4-B `e567acb883a0f81cb0c64d11f638b5f872511346` | parent `3ed17c246dadf80eab73f81bfc775845d582dbf1` | Not an ancestor of `main` |
| P2.4-C parent `21b7487eec431dcb993a44d0d642a33644141526` | parent `e567acb883a0f81cb0c64d11f638b5f872511346` | Not an ancestor of `main` |
| P2.4-C remediation `327fc0479031279b889ea1dd1140a23d4abe442f` | parent `21b7487eec431dcb993a44d0d642a33644141526` | Not an ancestor of `main` |

The P2.4-C remediation diff relative to the P2.4-B baseline changes `shared/engineering.ts` and adds `shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts`. This audit uses those exact blobs for the requested inconsistency analysis and separately records current `main` behavior where it differs.

## 3. Exact source references

At P2.4-C reference `327fc0479031279b889ea1dd1140a23d4abe442f`, `shared/engineering.ts` contains:

- `validRuntimeGeometryOptions`: lines 177–185;
- `gjkWithinDistance`: lines 214–324;
- `padToPadDistanceDetailed`: lines 363–367;
- numeric wrapper `padToPadDistance`: line 368;
- numeric wrapper `viaToPadDistance`: lines 372–379;
- `validatePcb`: lines 560–575;
- canonical `validateGeometryOptions`: line 614;
- DRC pad-to-pad propagation: line 525.

At current source `main` `a98384b`, `shared/engineering.ts` has:

- `GeometryOptions` near line 20;
- `padToPadDistanceDetailed` near line 258;
- `validatePcb` near line 286;
- no `validRuntimeGeometryOptions` symbol and no canonical `validateGeometryOptions` symbol in the file.

This line/state distinction is material: the detailed two-validator inconsistency is present in the requested P2.4-C reference, while current `main` remains earlier code and must not be described as already containing the remediation.

## 4. Workstream 1 — detailed API options-validation inconsistency

### 4.1 API boundaries and caller flow

In the P2.4-C reference, the boundaries are:

1. `validatePcb(project, options)` calls canonical `validateGeometryOptions(options)` before evaluation. Any error becomes one `PCB_INVALID_OPTIONS` Error finding at lines 560–575.
2. `evaluatePcbV2` receives already-validated options and passes them to `padToPadDistanceDetailed` for pad-pair DRC at line 525.
3. Direct callers of exported `padToPadDistanceDetailed(a, b, options)` bypass `validatePcb` and are checked by `validRuntimeGeometryOptions` at lines 363–367.
4. `padToPadDistanceDetailed` passes `options.gjkMaxIterations ?? 64` to `gjkWithinDistance` on its generic fallback path.
5. Direct callers of `gjkWithinDistance(a, b, clearance, maxIterations)` do not pass an options object. They use the separate integer/lower-bound guard at lines 214–227.
6. `padToPadDistance(a, b)` delegates to `padToPadDistanceDetailed` and throws `GeometryCalculationError` for an `INDETERMINATE` result. It does not expose a separate options argument.
7. `viaToPadDistance` validates pad/via geometry but has no geometry-options argument.
8. `runDesignRules` does not expose a geometry-options argument in the P2.4-C source; its DRC path uses default options through its internal evaluator path.

The production `validatePcb` boundary is therefore canonical and strict. The inconsistent path is direct use of the detailed geometry API, especially when the input reaches the generic GJK fallback.

### 4.2 Exact value classification at the P2.4-C reference

The canonical predicate at line 614 requires a positive safe integer:

```text
typeof iterations === "number"
&& Number.isSafeInteger(iterations)
&& iterations >= 1
```

The runtime predicate at lines 177–185 instead accepts a number unless it is an integer, at least `1`, and unsafe. Its effective behavior is:

| `options.gjkMaxIterations` | `validRuntimeGeometryOptions` | `validateGeometryOptions` | Direct detailed result before correction | `validatePcb` result |
|---|---:|---:|---|---|
| omitted / no property | accepted | accepted | normal default path (`64`) | proceeds |
| `undefined` property value | accepted as a numeric check? **No**; `typeof undefined` is false | rejected | `INDETERMINATE`, `invalid geometry options` | `PCB_INVALID_OPTIONS` |
| `NaN` | incorrectly accepted by runtime predicate | rejected | generic path reaches GJK, then `invalid iteration budget` | `PCB_INVALID_OPTIONS` |
| `Infinity` | incorrectly accepted by runtime predicate | rejected | generic path reaches GJK, then `invalid iteration budget` | `PCB_INVALID_OPTIONS` |
| `0` | incorrectly accepted by runtime predicate | rejected | `initial overlap query: invalid iteration budget` on generic path | `PCB_INVALID_OPTIONS` |
| negative integer | incorrectly accepted by runtime predicate | rejected | `initial overlap query: invalid iteration budget` on generic path | `PCB_INVALID_OPTIONS` |
| fractional number, e.g. `1.5` | incorrectly accepted by runtime predicate | rejected | `initial overlap query: invalid iteration budget` on generic path | `PCB_INVALID_OPTIONS` |
| unsafe integer, e.g. `Number.MAX_SAFE_INTEGER + 1` | rejected | rejected | `invalid geometry options` | `PCB_INVALID_OPTIONS` |
| non-numeric string, e.g. `"64"` | rejected | rejected | `invalid geometry options` | `PCB_INVALID_OPTIONS` |
| `null`, array, or non-object options | rejected | rejected | `invalid geometry options` | `PCB_INVALID_OPTIONS` |
| unknown field, e.g. `{ timeout: 1 }` | rejected | rejected | `invalid geometry options` | `PCB_INVALID_OPTIONS` |
| positive safe integer, e.g. `1`, `64`, `257`, `Number.MAX_SAFE_INTEGER` | accepted | accepted | normal detailed path; possibly `INDETERMINATE` only if the valid budget exhausts | proceeds; DRC may report geometry indeterminate on genuine exhaustion |

The `undefined` row refers to an explicitly present property. An omitted property is accepted by both validators; an explicitly present `undefined` value is rejected by both because the property is present and its value is not a number.

The direct detailed API only reaches the later GJK classification when the selected shape pair does not finish in an analytic/rectangle/oval path. The validator inconsistency is nevertheless real at the API boundary: the same malformed options object is classified as `invalid geometry options` through `validatePcb` but can be classified later as `invalid iteration budget` through direct detailed evaluation. The direct detailed path does not produce a plausible finite distance in these cases.

### 4.3 GJK exhaustion is a separate valid-budget outcome

A positive safe integer is not an assertion of convergence. In the P2.4-C reference:

- `gjkWithinDistance(..., 1)` can return `INDETERMINATE` with `iteration limit exhausted before convergence`;
- `padToPadDistanceDetailed(..., { gjkMaxIterations: 1 })` preserves that reason with an `initial overlap query:` prefix;
- `validatePcb(..., { gjkMaxIterations: 1 })` emits `PCB_GEOMETRY_INDETERMINATE` with Error severity and does not emit a pad-clearance pass.

The unified options predicate must not collapse valid positive-budget exhaustion into invalid-options handling. Invalid options and exhausted valid budgets are distinct contract states.

## 5. Workstream 2 — compatibility and regression matrix

| API/path | Current P2.4-C reference behavior | Compatibility requirement | Future targeted-correction impact |
|---|---|---|---|
| `padToPadDistanceDetailed(a,b,options)` | Returns classified `GeometryDistanceResult`; malformed pad/options are `INDETERMINATE`; some malformed numeric budgets currently reach `invalid iteration budget` later | Preserve non-throwing result shape, stable `INDETERMINATE`, no finite distance for invalid input | Change only malformed numeric options from later `invalid iteration budget` to boundary `invalid geometry options` |
| `padToPadDistance(a,b)` | Delegates to detailed result; throws `GeometryCalculationError` on `INDETERMINATE` | Preserve signature, valid numeric results, and wrapper exception behavior | No signature change; malformed-pad behavior remains exception-based; it has no options parameter |
| `viaToPadDistance(pad,via)` | Validates runtime pad/via and throws `GeometryCalculationError` for malformed geometry | Preserve valid Circle/Oval/rectangle numbers and wrapper errors | No direct options impact |

| `validatePcb(project,options)` | Canonical options validator returns `PCB_INVALID_OPTIONS` before geometry evaluation | Preserve exact rule ID, Error severity, path, and correction text | No behavior change proposed; use as the compatibility oracle |
| `gjkWithinDistance(a,b,clearance,maxIterations)` | Direct scalar budget guard returns `invalid iteration budget` for non-positive or fractional values; positive budget can exhaust | Preserve direct scalar API reason and distinction between invalid budget and exhaustion | Do not route this API through the object-options validator |
| GJK convergence/exhaustion | Positive budget exhaustion returns `INDETERMINATE` with `iteration limit exhausted before convergence` | No finite distance and no DRC clear/pass on exhaustion | Must remain unchanged |
| P2.4-C localized uncertainty | Uncertain topology suppresses only affected conclusions; unresolved relationships are not unioned | Preserve localized findings and no false union/crossing conclusion | Regression suite must run against the unmerged P2.4-C reference before any integration |

Tests that must remain unchanged include:

- `shared/phase6-1-p2-4-a-boundary-safety.test.ts`, especially the public `validatePcb` option cases at lines 186–246;
- `shared/phase6-1-p2-4-b-geometry-api-contract.test.ts`, especially direct detailed options and wrapper behavior at lines 45–111;
- `shared/phase4_1.gjk-convergence.test.ts`, especially valid positive-budget exhaustion and zero-budget distinction at lines 38–94;
- `shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts`, especially localized uncertainty and finite-extreme fail-closed DRC cases at lines 28–75 and 122–140;
- existing compatibility, Circle/Oval, DRC boundary, and independent-oracle tests.

The future targeted correction may add a focused test file, but it must not rewrite the existing tests or alter their established assertions except through an explicitly approved contract update.

## 6. Workstream 3 — minimal remediation proposal

### 6.1 Smallest correction

Make one canonical positive-safe-integer predicate authoritative for geometry option objects. The preferred implementation shape is either:

```text
validRuntimeGeometryOptions(value) === (validateGeometryOptions(value).length === 0)
```

or a shared pure predicate used by both validators, with the public validator retaining its structured error path/message. The second form may avoid constructing error arrays in hot direct-API paths; the semantic rule must remain identical.

The exact validation boundary is the top of `padToPadDistanceDetailed`, after runtime pad validation and before any shape dispatch or derived geometry. An options object with a malformed `gjkMaxIterations` must return:

```text
{ state: "INDETERMINATE", iterations: 0, reason: "invalid geometry options" }
```

The `validatePcb` boundary remains unchanged and must continue returning:

```text
ruleId: "PCB_INVALID_OPTIONS"
severity: "Error"
path: "options.gjkMaxIterations"
correction: "must be a positive safe integer"
```

The direct `gjkWithinDistance` scalar API retains its own `invalid iteration budget` reason for invalid `maxIterations`, because it has no options object and this preserves the existing direct API distinction. A separate API-contract decision would be required to change that reason.

### 6.2 Compatibility implications

The correction changes only direct detailed-API classification for numeric values currently admitted by `validRuntimeGeometryOptions`: `NaN`, `Infinity`, zero, negative integers, and fractional values. They become `invalid geometry options` at the boundary instead of reaching GJK and becoming `invalid iteration budget` later. Unsafe integers, non-numeric values, unknown fields, null/array options, and non-object options already classify as invalid geometry options and should remain unchanged.

No valid positive safe integer changes classification. A valid budget that actually exhausts GJK remains `INDETERMINATE` with the existing exhaustion reason. Analytic shape paths must still validate options first, so malformed options cannot be hidden by an early analytic distance result.

### 6.3 Acceptance criteria

A future targeted implementation is acceptable only if it demonstrates all of the following without source-contract expansion:

1. Direct detailed calls classify `NaN`, `Infinity`, zero, negative, fractional, unsafe, non-numeric, null, arrays, unknown fields, and explicitly undefined values exactly as specified above.
2. Omitted options and `{}` remain accepted.
3. Positive safe integers, including `1`, `64`, `257`, and `Number.MAX_SAFE_INTEGER`, remain accepted.
4. Valid positive-budget GJK exhaustion retains `iteration limit exhausted before convergence` and no distance field.
5. `validatePcb` continues returning `PCB_INVALID_OPTIONS` before evaluation for malformed options.
6. Numeric wrappers retain `GeometryCalculationError` behavior for indeterminate geometry and unchanged valid numerical results.
7. Existing P2.4-A, P2.4-B, P2.4-C, GJK, DRC, and compatibility tests remain green without modifying their assertions.
8. A direct-versus-`validatePcb` differential test proves the intended boundary distinction: direct detailed returns `INDETERMINATE` with `invalid geometry options`, while `validatePcb` returns `PCB_INVALID_OPTIONS`.
9. No malformed option can cause a finite detailed distance or a DRC clearance pass.

### 6.4 Side effects and risks

The correction is localized, but it changes a reason string and diagnostic stage for malformed direct detailed calls. Any consumer matching the old nested reason `initial overlap query: invalid iteration budget` must be audited. The existing source search found tests asserting that old reason for zero and fractional detailed options; those tests would require a deliberate, approved expectation update in a future implementation task, not silent alteration during this audit.

The correction does not solve arbitrary-angle correctness, transformed-coordinate output-cell certification, rectangle/oval proof adequacy, or current-`main` integration. It should be implemented, reviewed, and published as a separate small patch before any P2.4-D checked-geometry work.

## 7. Workstream 4 — remaining P2.4-D classification

| Workstream | Existing status at verified refs | Defect or unresolved proof obligation | Dependencies / required evidence | Independently actionable? | Currently justified? |
|---|---|---|---|---|---|
| Geometry options validation | Confirmed split predicates at P2.4-C; absent as a split in current `main` | **Confirmed defect in unmerged P2.4-C** | Targeted source correction plus differential regression tests; no invented numerical bounds | Yes, as an isolated patch | Targeted correction is justified for separate implementation review; not integrated into P2.4-D yet |
| `route45` compatibility vectors | Existing arithmetic implementation and client caller; no checked route contract | Compatibility/representability semantics unresolved at extremes | Freeze ordinary, duplicate-endpoint, overflowed-difference, and invalid-input vectors; inspect route persistence behavior | Yes, as design/test preparation | Compatibility-vector preparation is justified; implementation is not |
| `rotatePoint` compatibility vectors | Public helper uses direct `Math.sin`/`Math.cos`; current and P2.4-C refs retain it | Public best-effort output versus future checked transform remains unresolved | Exact ordinary, special-angle, cancellation, signed-zero, overflow, and independent-oracle vectors | Yes, as evidence preparation | Vector extraction is justified; checked replacement is not |
| `transformLocalPoint` compatibility vectors | Composes `rotatePoint` and translation; used by pads and pins | Output-cell and non-finite derived-coordinate semantics unresolved | Exact transformed-coordinate vectors, output-cell boundary oracle, and consumer audit | Yes, as design/evidence preparation | Checked implementation is not justified |
| Checked transforms/output-cell certification | Not present at either P2.4-B or P2.4-C ref; not present on current `main` | **Unresolved proof obligation** | Certified intervals, binary64 cells, ties, subnormals, signed zero, binade boundaries, overflow, and API compatibility | No, not as a production patch yet | No |
| Arbitrary-angle trigonometric certification | Source still uses `Math.sin`/`Math.cos`; no certified coefficient/reduction artifact | **Unresolved proof obligation** | Exact coefficients, pi bounds, range reduction, remainder proof, outward rounding, and independent high-precision corpus | No, not until proof package exists | No |
| Certified rectangle/oval distance evaluation | Existing analytic paths, 96-step ellipse routines, and GJK/binary-search fallback; proposed certified evaluator absent | **Unresolved proof obligation** and budget adequacy is unmeasured | Certified interval lower/upper bounds, deterministic queue/budget semantics, adversarial cases, and representative benchmark corpus | No, not as a production patch yet | No |
| DRC fail-closed propagation | P2.4-C path emits `PCB_GEOMETRY_INDETERMINATE` Error for indeterminate pad distance and localizes topology uncertainty | Integrated consumer proof remains incomplete; current `main` is pre-P2.4-C | Combined verification against P2.4-B/P2.4-C behavior, route/UI/persistence audit, and no-false-pass tests | Partly, as an audit and regression task | Integration is not justified until the uncertainty state contract is frozen |
| Independent numerical oracle and benchmarking | Prior reports contain independent oracle vectors and a scheduler prototype, not a certified production evaluator benchmark | **Incomplete evidence**; no production geometry dataset establishes budget adequacy | Independent high-precision oracle, exact binary64 reference, actual evaluator benchmark, disclosed corpus, and reproducible counters | Yes, as evidence work | Evidence gathering is justified; implementation claims are not |

The current source `main` state adds a release/integration blocker: even a correct isolated P2.4-C/P2.4-D patch cannot be described as behavior of `main` without an explicit integration decision. This audit does not make that decision.

## 8. Risks and unresolved questions

1. **Reference-versus-main confusion:** reports based only on P2.4-C can accidentally describe behavior that is not present on source `main`.
2. **Diagnostic compatibility:** changing direct detailed reasons may break consumers or tests that match the old nested reason; the change must be intentional and isolated.
3. **Boundary duplication:** if the public validator and runtime validator remain separate, future drift can recreate the same inconsistency.
4. **GJK semantics:** invalid budgets and valid-budget exhaustion must remain distinct; unifying them would weaken diagnostics and regression guarantees.
5. **Analytic-path masking:** options must be validated before analytic dispatch, or malformed options could be accepted for some shape pairs and rejected for others.
6. **Fail-closed propagation:** adding future unsupported states without auditing every wrapper and DRC consumer could create false clears even if the detailed API itself is safe.
7. **Unresolved P2.4-D proofs:** no scope reduction or targeted options correction supplies the missing trig, output-cell, or certified nonlinear-distance proof artifacts.
8. **No invented domain:** current source validation proves finiteness/positivity, not a bounded production coordinate, angle, or dimension domain.

## 9. Recommended sequence

1. Keep current `main` and the unmerged P2.4-C reference explicitly separated in all implementation planning.
2. Review and, if separately authorized, implement the one-predicate options correction against the P2.4-C source reference.
3. Add only focused regression coverage for the classification matrix and differential direct/API-boundary behavior; preserve existing test intent and do not broaden the patch.
4. Re-verify wrapper behavior, valid-budget exhaustion, DRC Error propagation, and P2.4-C localized uncertainty on the exact targeted source commit.
5. Freeze route/rotation/transform compatibility vectors as a separate evidence artifact.
6. Do not begin checked-transform, arbitrary-angle trig, or certified rectangle/oval implementation until their independent proof artifacts and integration target are accepted.

## 10. Final verdict

**NOT_READY_FOR_IMPLEMENTATION**

The geometry-options inconsistency has a minimal, well-defined future correction, but it is located in an unmerged P2.4-C reference and must remain a separate targeted patch. The broader P2.4-D implementation is not ready: checked transforms, output-cell certification, arbitrary-angle trigonometric certification, certified rectangle/oval distance evaluation, integrated fail-closed propagation, and benchmark evidence remain incomplete.
