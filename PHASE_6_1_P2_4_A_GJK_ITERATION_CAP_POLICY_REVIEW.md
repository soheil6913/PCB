# Phase 6.1 — P2.4-A GJK Iteration Cap Policy Review

**Mode:** Strictly read-only technical investigation  
**Source repository:** [`soheil6913/-PCB-Studio-Pro`](https://github.com/soheil6913/-PCB-Studio-Pro)  
**Report repository:** [`soheil6913/PCB`](https://github.com/soheil6913/PCB)  
**P2.2 baseline:** `192cac1e3b0293a9ce41d9c06f01a91ae70333fe`  
**P2.4-A implementation SHA:** `d487e4f64fb007d2acb18df89c734e457e74c717`  
**Runtime-verified SHA:** `8a4de067ede025ac134b9ddc66d19652984038b2`  
**Investigation date:** 2026-11-23

## Verdict

# REMOVE CAP — RESTORE APPROVED SCOPE

The fixed `MAX_GJK_ITERATIONS = 256` policy has no evidence-backed technical rationale in the reviewed source history, reports, tests, or repository tree. It is not required to preserve fail-closed behavior: the pre-cap implementation already validates positive integer budgets, stops after the caller-provided budget, and returns an explicit `INDETERMINATE` result when convergence is not reached.

The recommended disposition is to remove the 256 admission cap and its cap-specific contract/tests from the P2.4-A state, restore the approved positive-safe-integer options contract, and treat any future resource-exhaustion policy as a separately designed and approved change. This report makes no source or test changes; implementation of this recommendation remains unapproved until explicit approval.

## 1. Reviewed design restriction

The approved design [`PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md) states in section 4.2:

- `gjkMaxIterations` must be a positive safe integer;
- an explicit invalid value must not silently become the default;
- **an arbitrary maximum iteration budget must not be introduced without a separate performance policy and evidence**;
- if a cap is later required, it must be specified and tested as a separate contract.

The same design defines P2.4-A as sparse-array rejection, runtime options validation, and focused regression tests. It places geometry API contracts in P2.4-B and numerical uncertainty in P2.4-C. The design's regression matrix requires testing positive-budget exhaustion and preserving existing GJK exhaustion/fail-safe behavior, but does not select 256 as a sufficient convergence bound.

## 2. Complete four-commit cap history

The runtime SHA is a linear descendant of the implementation SHA. The four commits after `d487e4f...` are:

| SHA | Parent | Message | Net file change |
|---|---|---|---|
| `dd033ea0e16bec537e75c54bb95000599f7f17df` | `d487e4f...` | `fix(pcb): cap GJK iteration budget` | `shared/engineering.ts`, 2 additions / 1 deletion |
| `8e2e029b4685c676eb5a493fa91e90c14fcc5d0a` | `dd033ea...` | `test(pcb): cover GJK boundary and iteration cap` | boundary test, 58 additions / 6 deletions |
| `73e21ecbce26039048b91045101a047b4048c683` | `8e2e029...` | `fix(pcb): enforce GJK cap at algorithm boundary` | `shared/engineering.ts`, 1 addition / 1 deletion |
| `8a4de067ede025ac134b9ddc66d19652984038b2` | `73e21ec...` | `test(pcb): enforce GJK budget at algorithm boundary` | boundary test, 4 additions / 0 deletions |

The full runtime-vs-implementation comparison is four commits ahead, zero behind. No commit message, patch description, source comment, or report reviewed explains why the number **256** was selected. The first cap commit only names the action; it does not supply a benchmark, complexity argument, incident, timeout measurement, or resource budget.

## 3. What the cap actually changes

At the implementation SHA, the public `gjkWithinDistance` contract was:

```text
maxIterations must be an integer >= 1
```

At the runtime SHA, it is:

```text
maxIterations must be an integer in [1, 256]
```

The runtime source adds `MAX_GJK_ITERATIONS = 256` and rejects a larger value before geometry execution with `INDETERMINATE` and reason `invalid iteration budget`. `validateGeometryOptions` also changes its diagnostic from `must be a positive safe integer` to `must be an integer between 1 and 256`.

This is an externally observable valid-input contract change. A caller that supplied a positive safe integer such as 257 or `Number.MAX_SAFE_INTEGER` was accepted by the implementation-state contract and is rejected by the runtime state. The P2.4-A implementation report's original scope explicitly described positive-safe-integer validation and stated that the GJK contract was not changed.

## 4. GJK convergence behavior in the reviewed source

The runtime implementation at `8a4de067...` performs the following relevant steps in `shared/engineering.ts`:

1. Validates the iteration budget before geometry.
2. Computes a scale from pad dimensions, clearance, and center distance.
3. Uses scale-relative tolerances based on `Number.EPSILON`.
4. Builds Minkowski-support points and performs the simplex loop.
5. Returns `WITHIN_DISTANCE` only for explicit geometric/simplex conditions.
6. Returns `OUTSIDE_DISTANCE` when a support point excludes the origin.
7. Returns `INDETERMINATE` for non-finite arithmetic, numerical degeneracy, duplicate inconclusive support points, or exhausted iterations.
8. Returns `INDETERMINATE` with reason `iteration limit exhausted before convergence` after the supplied budget is consumed.

The pre-cap implementation at `d487e4f...` already had the same caller-controlled loop budget and explicit exhaustion result; its input validation rejected budgets below 1 or non-integers but did not impose 256.

The detailed pad-distance path can invoke GJK repeatedly: it performs an initial overlap query and, for the general rotated Oval-to-Oval path, up to 64 binary-search decisions. Therefore a 256 limit is a **per-GJK-call** limit, not a total-operation limit for `padToPadDistanceDetailed`. In the worst structural case, one detailed distance can request roughly 64 binary-search calls at up to 256 inner iterations each, in addition to the initial query. The cap does not provide a separately specified wall-clock, total-iteration, or cancellation budget for the whole public operation.

## 5. Convergence limit versus resource-exhaustion safeguard

These are different policies:

### Algorithmic convergence limit

A convergence limit is part of the numerical algorithm's classification contract. It may say that after a supplied budget the result is not proven and must be `INDETERMINATE`. The existing implementation already does this. The limit can remain caller-controlled, with a safe integer validation boundary and explicit fail-closed exhaustion.

### Resource-exhaustion safeguard

A resource safeguard is intended to bound CPU, memory, or latency. Such a policy needs a workload model, a measured budget, an accounting scope, and an externally understandable failure mode. A fixed 256 per inner GJK call is not shown to be such a policy. It does not account for the 64-call binary-search wrapper, does not include elapsed time or total operation count, and has no documented relationship to an acceptable latency or memory ceiling.

The reviewed four commits therefore conflate an input-policy cap with a resource policy without supplying the separate performance evidence required by the approved design.

## 6. Is 256 scale-independent and geometry-independent?

The integer itself is scale-independent, but that does not make it a geometry-independent convergence guarantee.

The reviewed algorithm's iteration behavior depends on support-point progression, simplex degeneracy, relative orientation, near-contact/tangency, overlap, and numerical resolution. The implementation has scale-relative tolerances, so the number of iterations needed is not established by the physical coordinate scale alone. Different shape configurations can produce different progress patterns even at the same scale; conversely, large or small coordinates do not imply a fixed iteration count.

The repository contains no proof that every supported rotated Oval or other convex-pad configuration converges in at most 256 iterations. It also contains no empirical sweep establishing a maximum observed iteration count with margin across the supported geometry domain. Consequently, 256 cannot be treated as a geometry-independent convergence theorem.

## 7. Consequences of `INDETERMINATE`

The fail-closed consequence is desirable for DRC safety: an unproven clearance result is not reported as a clear result. The runtime code maps an indeterminate detailed pad distance to `PCB_GEOMETRY_INDETERMINATE` with Error severity, and numeric `padToPadDistance` throws `GeometryCalculationError` rather than returning a plausible finite distance.

That safety property does not make the cap harmless. If a legitimate calculation would converge with a budget above 256, the cap converts a potentially resolvable valid geometry query into `INDETERMINATE`. In full DRC this can block acceptance; in direct numeric-wrapper use it throws; in detailed API use it removes a finite distance. This is a false-uncertainty/availability failure rather than a false-clearance failure.

The cap also changes explicit options that were valid under the approved positive-safe-integer contract. The tests prove only that 257 is rejected, not that no legitimate geometry requires a larger budget.

## 8. Existing evidence and missing evidence

### Evidence actually present

The runtime source and tests provide these observations:

- default GJK budget remains 64;
- a budget of 1 can exhaust on one overlapping, offset Oval pair;
- a budget of 0 is classified as invalid;
- a rotated, non-coaxial Oval fixture converges with budget 256;
- budget 257 is rejected by the new cap;
- the full CI suite at the runtime SHA passed 15 test files and 232 tests;
- the existing GJK suites include 5 Phase 4 tests and 6 Phase 4.1 convergence tests;
- the focused P2.4-A test file contains 42 tests at the runtime SHA.

### Missing evidence

No reviewed artifact provides:

- a rationale for choosing 256 rather than 128, 512, another bound, or no cap;
- a worst-case convergence analysis for all supported pad shapes/orientations;
- a randomized or exhaustive geometry sweep recording maximum iterations;
- adversarial near-tangent, near-degenerate, high-aspect-ratio, and scale-range iteration distributions;
- a benchmark linking 256 to a latency, CPU, memory, or denial-of-service requirement;
- a total-operation or wall-clock budget for the full binary-search distance calculation;
- an independent oracle study showing that all cases rejected above 256 are safely unresolved rather than merely under-budgeted;
- a test demonstrating that a legitimate supported calculation cannot require 257 or more iterations.

The repository tree contains no benchmark/performance/stress artifact associated with these commits. The 232-test CI run proves regression-suite execution and pass status; it does not establish technical sufficiency of the cap.

No benchmark or new test was executed during this read-only investigation.

## 9. Can removing the cap restore the approved scope?

Yes, at the policy level.

The implementation-state behavior already supplies the required safety mechanism:

- reject non-integer or less-than-one budgets;
- preserve the caller's positive safe integer budget;
- stop after that supplied budget;
- return explicit `INDETERMINATE` on exhaustion or numerical uncertainty;
- keep DRC fail-closed and numeric wrappers from returning plausible distances for unresolved calculations.

Removing the fixed 256 restriction and restoring the positive-safe-integer validation text would restore the approved P2.4-A options contract without removing fail-closed behavior. The cap-specific tests would need to be removed or replaced by tests for the approved contract in a separately authorized implementation change. This conclusion is based on source comparison; no such change was made here.

If a resource limit is genuinely required, it should be a separate policy proposal with at least: measured workload targets, a total-operation or elapsed-time budget, cancellation/timeout semantics, a supported-geometry benchmark matrix, worst-case and percentile results, and explicit treatment of `INDETERMINATE` at every caller boundary.

## 10. CI chronology reconciliation

The runtime report states in its limitations section that no CI workflow was requested or performed. GitHub Actions independently shows:

- Workflow: `Engineering verification`;
- run: [`45181864203`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45181864203);
- event: `push`;
- exact head SHA: `8a4de067ede025ac134b9ddc66d19652984038b2`;
- created: `2026-11-23T13:13:56Z`;
- completed: `2026-11-23T13:14:28Z`;
- job: [`137717407140`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45181864203/job/137717407140);
- conclusion: `success`.

The job log reports:

```text
Test Files  15 passed (15)
Tests       232 passed (232)
```

The runtime report was committed to `soheil6913/PCB` at `2026-11-23T13:30:04Z`, after the CI run had completed. The available evidence therefore contradicts the report's published statement that no CI workflow was run or claimed. The most conservative explanation is that the report text was stale or reflected an earlier observation before the workflow evidence was checked; the exact authoring time before publication cannot be recovered from the report repository. No historical report was modified.

This chronology does not change the policy conclusion: CI passed, but CI pass status is not a rationale or benchmark for selecting 256.

## 11. Recommendation and gating

1. Remove the fixed 256 cap from the P2.4-A state and restore the approved positive-safe-integer options contract.
2. Preserve the existing explicit `INDETERMINATE` behavior for caller-budget exhaustion and numerical uncertainty.
3. Do not replace the cap with another fixed number in P2.4-A.
4. If a resource-exhaustion policy is needed, propose it separately with performance evidence and an explicit total-work/latency contract.
5. Keep P2.4-B unapproved and do not create or modify a P2.4-B branch until this policy decision is explicitly approved.

## 12. Restrictions observed

This investigation performed no source or test edits, created no branch, changed no commit or PR, performed no reset/rebase/cherry-pick/merge/force-push, modified no historical report, and started no P2.4-B implementation. The only intended write is this new report in `soheil6913/PCB`.

## References

- [Approved P2.4 design](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md)
- [P2.4-A implementation report](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_BOUNDARY_SAFETY_IMPLEMENTATION_REPORT.md)
- [P2.4-A runtime verification report](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_RUNTIME_VERIFICATION_REPORT.md)
- [Implementation SHA `d487e4f...`](https://github.com/soheil6913/-PCB-Studio-Pro/commit/d487e4f64fb007d2acb18df89c734e457e74c717)
- [Runtime SHA `8a4de067...`](https://github.com/soheil6913/-PCB-Studio-Pro/commit/8a4de067ede025ac134b9ddc66d19652984038b2)
- [Four-commit comparison](https://github.com/soheil6913/-PCB-Studio-Pro/compare/d487e4f64fb007d2acb18df89c734e457e74c717...8a4de067ede025ac134b9ddc66d19652984038b2)
- [CI workflow run `45181864203`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45181864203)
- [CI job `137717407140`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45181864203/job/137717407140)
