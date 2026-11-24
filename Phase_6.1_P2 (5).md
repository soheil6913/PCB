# Phase 6.1 P2.4-C — Numerical Extremes and Topology Uncertainty

**Final verdict: ACCEPTED**

## Scope and repository separation

This report documents the explicitly authorized Phase 6.1 P2.4-C implementation. Production code and tests were changed only in `soheil6913/-PCB-Studio-Pro`. This report is published only in `soheil6913/PCB`.

P2.4-D was not started. No UI, database, workflow, dependency, schema, migration, model, evaluator-policy, route45, or DRC-policy redesign was performed.

## Exact baseline and preflight

Implementation started from the approved P2.4-B SHA:

```text
e567acb883a0f81cb0c64d11f638b5f872511346
```

The required preflight recorded the following state before source changes:

| Check | Result |
|---|---|
| Approved P2.4-B SHA | Present and checked out exactly |
| P2.4-B parent | `3ed17c246dadf80eab73f81bfc775845d582dbf1` |
| P2.4-A remote HEAD | `3ed17c246dadf80eab73f81bfc775845d582dbf1` |
| `main` | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| PR #3 | Open, Draft, unmerged; base `main`; head `fix/phase6-1-p1-explicit-v2-dispatch-20261122` |
| Initial source worktree | Clean |
| Design evidence | Read from `PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md` |
| P2.3/F-05 evidence | Read from `PCB_Studio_Pro_—_Phase_6.1_P2 (3).md`, F-05 section |
| Prior P2.4-B contract | Read from `PHASE_6_1_P2_4_B_GEOMETRY_API_CONTRACT_IMPLEMENTATION_REPORT.md` |

The implementation branch was created exactly once:

```text
fix/phase6-1-p2-4-c-numerical-uncertainty-20261124
```

No existing P2.4-A, P2.4-B, `main`, PR #3, or protected/history branch was modified. No merge, rebase, reset, cherry-pick, force-push, or history rewrite was performed.

## Source-grounded problem

P2.3 finding F-05 and the approved P2.4 design identified a finite-input boundary problem: `Number.isFinite` accepts values near `Number.MAX_VALUE`, but subtraction, projection, determinant, dot-product, midpoint, and support calculations can overflow. The prior schematic path could then treat `NaN <= CONNECT_TOLERANCE` as false. That converted numerical inability to decide into an apparently definitive non-connection, which could subsequently produce false required-pin, disconnected-net, or net-topology conclusions.

The approved design explicitly required:

- no arbitrary coordinate ceiling;
- no arbitrary numerical or GJK cap;
- scaled or local arithmetic where mathematically valid;
- explicit uncertainty propagation when a result cannot be proven finite and determinate;
- no union on indeterminate topology;
- no definitive disconnected or unconnected conclusion when geometry cannot be resolved numerically;
- preservation of public signatures and accepted P2.2, P2.4-A, and P2.4-B contracts.

## Implementation changes

The final source commit is:

```text
21b7487eec431dcb993a44d0d642a33644141526
```

It changes exactly two source-repository files:

```text
shared/engineering.ts
shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts
```

### Robust scalar distance and segment arithmetic

`distance` now uses finite-aware differences and scale-normalized Euclidean arithmetic. Direct subtraction remains the first operation, preserving representable common-offset deltas. If direct subtraction overflows, a scaled fallback is attempted. If the true derived distance cannot be represented finitely, the existing numeric signature returns `NaN`; it does not clamp, coerce, or fabricate a finite value.

`pointToSegment` now computes in translated relative coordinates, avoids reconstructing an absolute projected point, and uses normalized residual distance arithmetic. Its internal state distinguishes a finite result from numerical indeterminacy. The existing private numeric helper retains its numeric signature for existing callers; unresolved arithmetic becomes `NaN` at that boundary, while topology and DRC callers use explicit state-aware paths.

### Schematic topology uncertainty

A private three-state model (`TRUE`, `FALSE`, `INDETERMINATE`) was added for topology predicates. It is used for:

- node deduplication and endpoint proximity;
- junction-to-wire matching;
- pin-to-wire matching;
- robust wire intersection and endpoint-touch evaluation;
- junction-at-intersection evaluation.

When arithmetic is indeterminate:

- no union is performed;
- `SCH_GEOMETRY_INDETERMINATE` is emitted as an Error finding;
- required-pin validation does not emit a definitive `SCH_UNCONNECTED_REQUIRED_PIN` conclusion;
- disconnected-net and net-name-conflict conclusions are suppressed rather than inferred from unresolved roots;
- crossing-without-junction is not emitted as a definitive result for an unresolved intersection.

The direct `validateSchematic` public signature is unchanged. Existing malformed-input validation and accepted valid-input findings remain intact.

### GJK and DRC behavior

No GJK iteration cap or coordinate ceiling was added. Existing P2.4-A positive-safe-integer budgets, exhaustion semantics, and P2.4-B detailed-result/wrapper contracts remain unchanged.

Finite inputs whose derived GJK arithmetic is non-finite remain `INDETERMINATE`. Existing DRC fail-closed behavior is preserved: numerical indeterminacy cannot become a clearance pass or a fabricated finite clearance result.

## Regression and independent-oracle coverage

The new focused file covers:

- finite common-offset coordinates with a representable delta;
- opposite-sign finite coordinates whose true subtraction is not representable;
- finite pads whose derived GJK arithmetic becomes non-finite;
- uncertain wire endpoint and required-pin connectivity;
- uncertain crossing/endpoint-touch topology without an accidental union or crossing conclusion;
- finite-extreme DRC behavior without a plausible clearance pass.

The common-offset assertion uses the independently computed representable IEEE-754 delta `(base + delta) - base`, rather than asserting that an unrepresentable decimal survives at that magnitude. Existing independent-oracle suites remain unchanged and were included in focused verification. Unresolved cases remain classified as indeterminate; no oracle case was forced into a guessed boolean.

## Verification evidence

Dependencies were restored without changing manifests or the lockfile:

```text
pnpm install --frozen-lockfile
exit 0
```

An initial `pnpm check` before dependency restoration could not find installed `node` and `vite/client` type definitions. After the frozen install, the required check passed.

### Focused verification

Exact command:

```text
pnpm exec vitest run \
  shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts \
  shared/phase6-1-p2-2.circle-oval-contract.test.ts \
  shared/phase6-1-p2-4-a-boundary-safety.test.ts \
  shared/phase6-1-p2-4-b-geometry-api-contract.test.ts \
  shared/phase4.gjk.test.ts \
  shared/phase4_1.gjk-convergence.test.ts \
  shared/phase5_2.drc-adversarial.test.ts \
  shared/phase5_3.independent-oracles.test.ts
```

Result:

```text
exit 0
8 test files passed
123 tests passed
```

This matrix includes the new numerical-extreme tests, P2.2 Circle/Oval tests, P2.4-A boundary safety, P2.4-B API contracts, GJK convergence/exhaustion, DRC adversarial regressions, and independent-oracle tests.

### Required project verification

| Command | Exit code | Result |
|---|---:|---|
| `pnpm check` | 0 | TypeScript check passed |
| `pnpm test` | 0 | 17 test files passed; 246 tests passed |
| `pnpm build` | 0 | Client and server production build passed |
| `git diff --check` | 0 | No whitespace errors |

The build retained the repository's existing non-fatal Vite notice about `/api/platform/config.js` lacking `type="module"`, and the existing large-chunk warning. Neither changed the exit code.

The final source worktree was clean after commit and push. The final source branch HEAD was verified as:

```text
21b7487eec431dcb993a44d0d642a33644141526
```

## CI evidence

GitHub Actions ran on the exact final source SHA:

- Workflow: `Engineering verification`
- Run: `45350218282`
- URL: https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45350218282
- Tested `head_sha`: `21b7487eec431dcb993a44d0d642a33644141526`
- Run status: completed
- Run conclusion: success
- Job: `verify`
- Job ID: `138294505693`
- Job conclusion: success

The CI workflow therefore verified the exact published source commit rather than a parent, sibling, or earlier implementation SHA.

## Compatibility and safety disposition

Preserved contracts and behavior include:

- public signatures for scalar geometry, detailed geometry, wrappers, validation, and DRC entry points;
- accepted Circle/Oval and rotated-geometry behavior;
- P2.4-A sparse-array/options boundary safety;
- P2.4-A GJK positive-safe-integer and exhaustion semantics;
- P2.4-B `GeometryCalculationError` and detailed-result contracts;
- existing `validatePcb` fail-closed geometry behavior;
- schema-v2 dispatch, migration behavior, DRC separation, finding identities, and valid-input ordering;
- no route45 changes;
- no coordinate ceiling, clamping, NaN/Infinity-to-zero conversion, or arbitrary epsilon policy.

The implementation intentionally makes unresolved topology explicit rather than calling it disconnected. This can require user review for pathological finite inputs, which is the approved fail-closed behavior.

## Publication boundary

Only this report is to be committed to `soheil6913/PCB`. Source code and tests remain in `soheil6913/-PCB-Studio-Pro`. No source implementation or test file is being copied into the report repository.

## Final verdict

**ACCEPTED**

P2.4-C numerical-extreme hardening and schematic-topology uncertainty propagation were implemented from the approved P2.4-B SHA, verified locally and by CI on the exact final source commit, and kept isolated from P2.4-D. Work stops here.
