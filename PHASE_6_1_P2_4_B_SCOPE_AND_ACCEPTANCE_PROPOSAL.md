# Phase 6.1 P2.4-B — Scope and Acceptance Proposal

**Status:** READ-ONLY AUDIT COMPLETE — PROPOSAL PENDING REVIEW/APPROVAL  
**Report repository:** [`soheil6913/PCB`](https://github.com/soheil6913/PCB)  
**Source repository:** [`soheil6913/-PCB-Studio-Pro`](https://github.com/soheil6913/-PCB-Studio-Pro)  
**Audit date:** 2026-11-23

## 1. Decision boundary

This document is a scope and acceptance proposal only. The read-only audit did not change source code, tests, configuration, dependencies, branches, pull requests, `main`, or P2.4-A. No P2.4-B implementation is authorized by this document. No source branch may be merged until this proposal has been reviewed and explicitly approved.

The report is intentionally stored in `soheil6913/PCB`, the separate report/archive repository. It must not be added to `soheil6913/-PCB-Studio-Pro`.

## 2. Audit evidence reviewed

The following report-repository artifacts were reviewed from `soheil6913/PCB/main`:

- [`PHASE_6_1_1_V2_LEGACY_CONTRACT_LOCK.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_1_V2_LEGACY_CONTRACT_LOCK.md)
- [`PHASE_6_1_2_P1_GATE_AUDIT.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_2_P1_GATE_AUDIT.md)
- [`PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md)
- [`PHASE_6_1_P2_4_A_BOUNDARY_SAFETY_IMPLEMENTATION_REPORT.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_BOUNDARY_SAFETY_IMPLEMENTATION_REPORT.md)
- [`PHASE_6_1_P2_4_A_RUNTIME_VERIFICATION_REPORT.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_RUNTIME_VERIFICATION_REPORT.md)

The source-grounded audit also inspected the exact P2.2 baseline `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` in `soheil6913/-PCB-Studio-Pro`, including `shared/engineering.ts`, the P2.2 Circle/Oval contract test, and `package.json` through GitHub's read-only API/raw-content endpoints.

## 3. Findings that constrain P2.4-B

### 3.1 P2.4-B must remain an API-contract subphase

The design document defines P2.4-B as:

1. documenting exported geometry functions and their preconditions;
2. hardening detailed geometry entry points;
3. making numeric compatibility wrappers fail closed with the existing geometry error;
4. completing call-site inventory and compatibility tests.

P2.4-B must not include sparse-array validation or runtime geometry-options validation (P2.4-A), numerical uncertainty propagation/extreme-coordinate policy (P2.4-C), or `route45` correction (P2.4-D).

### 3.2 Reviewed public surface and observed call sites

At the reviewed P2.2 baseline, the relevant exported geometry surface includes:

- scalar helpers: `distance`, `measure`, `snapToGrid`, `rotatePoint`, `transformLocalPoint`, `segmentsIntersect`, `segmentDistance`, and `route45`;
- detailed geometry: `gjkWithinDistance` and `padToPadDistanceDetailed`;
- compatibility wrappers: `padToPadDistance` and `viaToPadDistance`;
- public validation/evaluation boundaries that consume geometry: `validateSchematic`, `validatePcb`, `runDesignRules`, `validateProjectJsonDetailed`, and migration/validation helpers.

The reviewed P2.2 test directly consumes `padToPadDistance` and `viaToPadDistance`. The source also uses the detailed pad-distance path inside PCB evaluation and uses scalar helpers throughout schematic and PCB evaluation. The implementation prompt must repeat this inventory against the exact implementation base before editing, because the inventory is a required acceptance artifact rather than an assumption.

### 3.3 Compatibility contracts that must remain frozen

P2.4-B must preserve, unless a separately approved compatibility exception is documented:

- the approved Circle/Oval contract from P2.2;
- valid-input numeric results and existing result classifications;
- existing public function names and signatures;
- `validatePcb` versus `runDesignRules` separation;
- schema-v2/legacy finding identities and ordering;
- fail-safe handling where an indeterminate geometry result must not become a clearance pass;
- the existing `GeometryCalculationError` behavior for numeric wrappers on indeterminate calculations.

P2.4-B must not introduce schema-v3, migration, model-selector, DRC-policy, manufacturing-standard, UI, database, workflow, dependency, or coordinate-limit changes.

### 3.4 Existing project-state blockers and ambiguities

1. The P1 audit records that explicit versioned model/evaluator dispatch is not present at the P2.2/main baseline. P2.4-B must not silently implement or redefine that P1 contract. If the source base is changed from the approved P2.2 baseline, the change requires explicit approval and a new baseline record.
2. The P2.4-A implementation report identifies branch head `d487e4f64fb007d2acb18df89c734e457e74c717` and six commits ahead of the P2.2 baseline. The P2.4-A runtime verification report identifies branch head `8a4de067ede025ac134b9ddc66d19652984038b2` and ten commits ahead. This is an unresolved report inconsistency. P2.4-B must not be based on, modify, merge, rebase, cherry-pick, or otherwise repair P2.4-A until the authoritative A head is reconciled.
3. The source repository currently has an open draft PR #3 for explicit v2 dispatch. It must remain unchanged. P2.4-B must not depend on an unapproved PR merge.

## 4. Proposed implementation scope

If and only if this proposal is explicitly approved, P2.4-B may proceed as one isolated source branch from the explicitly approved base SHA.

### In scope

- Add or update API documentation in the source file or the separately approved source documentation location for the reviewed geometry exports.
- Define and implement a fail-closed contract for malformed runtime geometry/options at detailed entry points, returning `INDETERMINATE` with a stable reason rather than leaking a `TypeError`.
- Preserve valid-input behavior and signatures for `padToPadDistance` and `viaToPadDistance`; numeric wrappers must not return a plausible finite result for malformed or indeterminate calculations and must use the existing `GeometryCalculationError` contract.
- Add focused compatibility tests for malformed points/pads, unknown shapes, invalid dimensions, invalid Via geometry, malformed options, detailed indeterminate results, wrapper exceptions, and valid existing fixtures.
- Search and record all repository call sites and tests for every exported geometry function before implementation. Any call site requiring a signature or exception change is a stop condition for review.

### Explicitly out of scope

- Any edit to P2.4-A's branch, commits, tests, or report.
- Sparse-array validation and public `validatePcb` options validation.
- Numerical-extreme remediation, coordinate ceilings, topology indeterminacy propagation, or P2.4-C work.
- `route45` correction or routing behavior changes.
- Schema-v3, migration, explicit selector redesign, DRC policy, UI, database, server, workflows, dependencies, lockfiles, release, deployment, or manufacturing-readiness claims.
- Changes to `main`, PR #3, P1/P2.1/P2.2 verification branches, or prior audit branches.

## 5. Proposed acceptance criteria

P2.4-B is acceptable only if all criteria below are evidenced in the final implementation report.

### A. Repository and isolation gates

- The approved base SHA and dedicated branch name are recorded before implementation.
- The branch is independent and clean before work; `main`, PR #3, P2.4-A, and all prior verification branches remain unchanged.
- The report is committed only to `soheil6913/PCB`; source code and tests are committed only to `soheil6913/-PCB-Studio-Pro`.
- No merge, rebase, cherry-pick, force-push, release, tag, or deployment is performed.

### B. API contract gates

- Every reviewed exported geometry function has documented preconditions and result/error semantics.
- `gjkWithinDistance` and `padToPadDistanceDetailed` do not leak `TypeError` for the approved malformed-input matrix; they return the documented explicit indeterminate result.
- `padToPadDistance` and `viaToPadDistance` preserve their public signatures and valid-input numeric behavior.
- Numeric wrappers never return a plausible finite distance for malformed or indeterminate input; the documented `GeometryCalculationError` path is asserted.
- No malformed input is silently coerced into a valid point, shape, dimension, option, or Via.

### C. Compatibility gates

- Existing P2.2 Circle/Oval contract tests remain unchanged and pass.
- Existing schema-v2/legacy compatibility goldens remain unchanged and pass.
- Existing valid geometry fixtures retain exact expected values or classifications, with any exception separately approved and documented before implementation.
- `validatePcb` and `runDesignRules` retain their separate public semantics.
- No finding RuleId, finding identity, object-ID order, or valid-input ordering changes are introduced.

### D. Verification gates

The final report must record exact commands, exit codes, test counts, commit SHA, and working-tree status for at least:

```text
pnpm exec vitest run <new P2.4-B focused tests> <existing P2.2 contract tests>
pnpm exec vitest run shared/engineering.v2-compatibility.test.ts
pnpm check
pnpm test
pnpm build
```

A missing test runner, dependency, or executable is **blocked / zero tests run**, never a pass. A passing focused suite alone is insufficient for acceptance.

### E. Review gates

- The final diff is reviewed against the approved scope and contains no P2.4-C/D or P2.4-A changes.
- The call-site inventory is included in the final report.
- Any public signature, exception, or valid-result change is listed as a compatibility exception and requires separate approval.
- The final report states explicitly whether P2.4-B is accepted, blocked, or rejected; it must not claim P2.4-C/D completion.

## 6. Proposed execution order after approval

1. Resolve the P2.4-A report-head inconsistency without modifying P2.4-A.
2. Record the approved P2.4-B base SHA and confirm the source/reports repository separation.
3. Perform the complete call-site/export inventory on that exact base.
4. Prepare the implementation prompt from this approved scope; stop if inventory reveals an incompatible external consumer.
5. Create one independent P2.4-B branch and implement only the approved API-contract changes.
6. Run focused tests, compatibility tests, full tests, typecheck, and build.
7. Perform final diff/repository-isolation audit.
8. Publish the final P2.4-B implementation and verification report to `soheil6913/PCB`, not the code repository.

## 7. Current disposition

**PENDING REVIEW AND EXPLICIT APPROVAL.**

Until approval is recorded, no source code may change, no branch may be merged, P2.4-A must remain untouched, and no P2.4-B implementation branch may be created.

## 8. References

- P2.4 design and staged gates: [`PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md), especially sections 3–8.
- P2.4-A runtime verification: [`PHASE_6_1_P2_4_A_RUNTIME_VERIFICATION_REPORT.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_RUNTIME_VERIFICATION_REPORT.md).
- P2.4-A implementation report: [`PHASE_6_1_P2_4_A_BOUNDARY_SAFETY_IMPLEMENTATION_REPORT.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_BOUNDARY_SAFETY_IMPLEMENTATION_REPORT.md).
- P1 gate audit: [`PHASE_6_1_2_P1_GATE_AUDIT.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_2_P1_GATE_AUDIT.md).
- Legacy v2 contract lock: [`PHASE_6_1_1_V2_LEGACY_CONTRACT_LOCK.md`](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_1_V2_LEGACY_CONTRACT_LOCK.md).
- Approved P2.2 source baseline: [`shared/engineering.ts@192cac1`](https://github.com/soheil6913/-PCB-Studio-Pro/blob/192cac1e3b0293a9ce41d9c06f01a91ae70333fe/shared/engineering.ts).
- Approved P2.2 contract tests: [`phase6-1-p2-2.circle-oval-contract.test.ts@192cac1`](https://github.com/soheil6913/-PCB-Studio-Pro/blob/192cac1e3b0293a9ce41d9c06f01a91ae70333fe/shared/phase6-1-p2-2.circle-oval-contract.test.ts).
- Open draft PR that must remain unchanged: [PR #3](https://github.com/soheil6913/-PCB-Studio-Pro/pull/3).
