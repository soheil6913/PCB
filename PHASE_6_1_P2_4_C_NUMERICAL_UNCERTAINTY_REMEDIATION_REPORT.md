# Phase 6.1 P2.4-C Numerical Uncertainty Remediation Report

## Verdict

**ACCEPTED**

This targeted remediation addresses the three authorized P2.4-C findings: unsupported determinant zeroing, loss of provable outside-threshold conclusions after distance overflow, and global suppression of unrelated schematic topology findings.

## Scope and exact baseline

- Source repository: `soheil6913/-PCB-Studio-Pro`
- Report repository: `soheil6913/PCB`
- Approved P2.4-C baseline branch: `fix/phase6-1-p2-4-c-numerical-uncertainty-20261124`
- Approved P2.4-C baseline SHA: `21b7487eec431dcb993a44d0d642a33644141526`
- Approved parent: `e567acb883a0f81cb0c64d11f638b5f872511346`
- Remediation branch: `fix/phase6-1-p2-4-c-numerical-uncertainty-remediation-20261124`
- Remediation commit: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Existing P2.4-A SHA preserved: `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- Existing P2.4-B SHA preserved: `e567acb883a0f81cb0c64d11f638b5f872511346`
- `main` baseline preserved: `a98384bbfc3296947b90f5254a03a77b11fdc8a9`
- Existing PR #3 was not modified. A separate verification PR #4 was opened for the remediation branch and was not merged.

No reset, rebase, amend, force-push, merge, or history rewrite was performed. Exactly one new source commit was created after the authorized remediation branch was created from the exact P2.4-C SHA.

## Implemented remediation

### Robust orientation and intersection predicates

`shared/engineering.ts` no longer classifies a determinant as zero using `Number.EPSILON * 8`. The implementation now has an explicit `OrientationState` with positive, negative, zero, and indeterminate outcomes. It uses translated and scaled floating arithmetic with the documented conservative first-order bound:

```text
(3 + 16 * Number.EPSILON) * Number.EPSILON * (abs(left) + abs(right))
```

When the floating result is within that bound, or when coordinate subtraction overflows, the predicate falls back to exact IEEE-754 dyadic decomposition and `BigInt` determinant arithmetic. Non-finite inputs remain indeterminate rather than being guessed collinear. The public segment predicate therefore distinguishes signed near-collinear cases, exact collinearity, overlap, and non-overlap without an arbitrary determinant tolerance.

Topology intersection handling remains conservative when an overflowed segment relationship could be an actual intersection: it never unions an unresolved relationship and never asserts a crossing conclusion from an unresolved result.

### Connectivity threshold and overflow

`distanceThresholdState` preserves the existing `CONNECT_TOLERANCE` semantics. A coordinate subtraction overflow is classified as provably outside the threshold, not automatically indeterminate; no coordinate ceiling, clamping, fabricated finite distance, or NaN-to-zero conversion was introduced. Public `distance` continues to return `NaN` when its finite scalar result cannot be represented.

Point-to-segment connectivity uses a scaled fallback for overflowed differences. It returns a conclusive outside result when the scaled separation is safely beyond `CONNECT_TOLERANCE`; relationships too close to resolve remain indeterminate.

### Localized topology uncertainty

The global `topologyIndeterminate` suppression flag was removed. Uncertainty is tracked by affected wire, pin, and net sets. Required-pin findings are suppressed only for affected pins. Disconnected-net and net-name conclusions are suppressed only for affected nets. Separate required-pin and disconnected-net findings remain available when another wire pair or net is uncertain. Indeterminate relationships are never unioned.

## Changed source files

The remediation source commit contains exactly these two files:

- `shared/engineering.ts`
- `shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts`

The test additions include an independent integer-oracle comparison, signed near-collinear cases, exact collinear overlap and non-overlap, endpoint connectivity on both sides of the existing tolerance, opposite-sign overflowed node distances, large-offset behavior, localized required-pin and disconnected-net assertions, and no-false-union/no-false-crossing checks.

## Verification evidence

All commands were run from the exact remediation commit before publication.

| Verification | Result |
|---|---|
| Focused P2.4-C file | 12/12 tests passed |
| Required focused regression set | 8 files, 129/129 tests passed |
| Full `pnpm test` | 17 files, 252/252 tests passed |
| `pnpm check` | Passed (`tsc --noEmit`) |
| `pnpm build` | Passed |
| `git diff --check` | Passed |
| Forbidden-pattern audit | Passed; no `Number.EPSILON * 8`, `MAX_GJK_ITERATIONS`, or `topologyIndeterminate` in changed source/test files |

The production build emitted two non-blocking warnings already associated with the project build: `/api/platform/config.js` lacks a `type="module"` attribute for bundling, and one minified chunk exceeds 500 kB. Neither warning caused a build failure.

The full verification commands included the P2.2 Circle/Oval contract, P2.4-A boundary safety, P2.4-B geometry API contract, GJK tests and convergence/exhaustion tests, DRC adversarial tests, independent-oracle tests, the new P2.4-C adversarial tests, TypeScript checking, and production build.

## GitHub Actions verification

GitHub Actions ran on the exact final remediation SHA:

- Repository: `soheil6913/-PCB-Studio-Pro`
- Workflow: `Engineering verification`
- Run: `45352245914`
- URL: https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45352245914
- Head SHA: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Status: completed
- Conclusion: success
- Job: `verify` (`138301317527`), successful
- Verified steps: checkout, pnpm setup, Node setup, dependency installation, TypeScript check, automated tests, and production build

The runner emitted a non-blocking notice that Node.js 20 is deprecated for the referenced actions and is being forced to Node.js 24. The workflow itself completed successfully.

## Limitations and non-scope

This remediation does not change public API signatures, Circle/Oval behavior, P2.4-A GJK boundary/exhaustion behavior, P2.4-B detailed/wrapper contracts, DRC policy, schema behavior, route45, UI, database, dependencies, or connectivity tolerance policy. It does not introduce P2.4-D work. The exact dyadic fallback is intended for finite IEEE-754 inputs; non-finite runtime geometry remains indeterminate or invalid according to the existing validation contracts. Scaled point-to-segment fallback deliberately remains indeterminate when the scaled separation is not provably outside the existing threshold.

## Publication boundary

Only this remediation report is published to `soheil6913/PCB`. No source code or test file is copied into the report repository. The source branch remains unmerged, and work stops after report publication; P2.4-D is not started.
