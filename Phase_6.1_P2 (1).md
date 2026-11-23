# Phase 6.1 P2.4-A — SHA Reconciliation Report

**Investigation mode:** Read-only  
**Source repository:** [`soheil6913/-PCB-Studio-Pro`](https://github.com/soheil6913/-PCB-Studio-Pro)  
**Report repository:** [`soheil6913/PCB`](https://github.com/soheil6913/PCB)  
**P2.2 baseline:** `192cac1e3b0293a9ce41d9c06f01a91ae70333fe`  
**Investigation date:** 2026-11-23

## Final verdict

# CONFLICT — P2.4-A VERIFICATION BASELINE INVALID

The SHA discrepancy is conclusively resolved as Git history: `8a4de067ede025ac134b9ddc66d19652984038b2` is a descendant of `d487e4f64fb007d2acb18df89c734e457e74c717`. The runtime verification was performed against the exact `8a4de067...` source HEAD and its 232-test claim is independently corroborated by the GitHub Actions log.

However, `8a4de067...` is not merely the implementation-report state carried forward. It adds four later commits that introduce and test a new maximum GJK iteration budget of 256. The approved P2.4 design explicitly says not to introduce an arbitrary maximum iteration budget in this remediation without a separate performance policy and evidence. The implementation report describes P2.4-A as sparse-array and runtime-options boundary safety and states that the GJK contract was not changed. Therefore the runtime verification result is valid for the exact source it tested, but the claim that that source is a scope-compliant P2.4-A baseline conflicts with the approved P2.4-A scope/design. P2.4-B remains blocked pending an explicit disposition of this scope conflict.

## 1. Exact commit identity

GitHub's commit API returned the following full SHA values exactly as requested:

| Role | Full SHA | Commit message | Parent |
|---|---|---|---|
| P2.2 baseline | `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` | `docs: record Circle Oval contract verification` | `108c0667885f33debe33b70df9f18a902cf3dc7f` |
| Implementation-report SHA | `d487e4f64fb007d2acb18df89c734e457e74c717` | `test(pcb): verify sparse arrays across PCB validation boundary` | `45fd1afb397f4ac92fbf154998d4ea8d31d4ed73` |
| Runtime-verification SHA | `8a4de067ede025ac134b9ddc66d19652984038b2` | `test(pcb): enforce GJK budget at algorithm boundary` | `73e21ecbce26039048b91045101a047b4048c683` |

The exact commit objects are available at [`d487e4f...`](https://github.com/soheil6913/-PCB-Studio-Pro/commit/d487e4f64fb007d2acb18df89c734e457e74c717) and [`8a4de067...`](https://github.com/soheil6913/-PCB-Studio-Pro/commit/8a4de067ede025ac134b9ddc66d19652984038b2).

## 2. Parent relationship and ancestry

The runtime commit descends from the implementation commit. GitHub's compare API reports:

- `d487e4f...` to `8a4de067...`: **4 commits ahead, 0 behind**;
- merge base: exactly `d487e4f...`;
- runtime branch `fix/phase6-1-p2-4-a-boundary-safety-20261123` currently points to exactly `8a4de067...`.

The four post-implementation commits are:

1. `dd033ea0e16bec537e75c54bb95000599f7f17df` — `fix(pcb): cap GJK iteration budget` — parent `d487e4f...`;
2. `8e2e029b4685c676eb5a493fa91e90c14fcc5d0a` — `test(pcb): cover GJK boundary and iteration cap` — parent `dd033ea...`;
3. `73e21ecbce26039048b91045101a047b4048c683` — `fix(pcb): enforce GJK cap at algorithm boundary` — parent `8e2e029...`;
4. `8a4de067ede025ac134b9ddc66d19652984038b2` — `test(pcb): enforce GJK budget at algorithm boundary` — parent `73e21ec...`.

Thus the two reported SHA values are not competing branches or unrelated states. They are sequential states in one linear history.

## 3. Baseline comparisons

### 3.1 Implementation-report SHA versus P2.2 baseline

GitHub compare `192cac1...` to `d487e4f...` reports **6 commits ahead, 0 behind** and exactly two changed files:

| File | Status | Additions | Deletions |
|---|---:|---:|---:|
| `shared/engineering.ts` | modified | 16 | 5 |
| `shared/phase6-1-p2-4-a-boundary-safety.test.ts` | added | 194 | 0 |

This is the state described by the implementation report: sparse-array boundary validation, runtime geometry-options validation, and their focused tests.

### 3.2 Runtime-verification SHA versus P2.2 baseline

GitHub compare `192cac1...` to `8a4de067...` reports **10 commits ahead, 0 behind** and still exactly two changed files:

| File | Status | Additions | Deletions |
|---|---:|---:|---:|
| `shared/engineering.ts` | modified | 18 | 6 |
| `shared/phase6-1-p2-4-a-boundary-safety.test.ts` | added | 250 | 0 |

The runtime state contains all baseline-to-implementation changes, plus the four later commits. No additional tracked file is present in the compare result.

### 3.3 Runtime-verification SHA versus implementation-report SHA

GitHub compare `d487e4f...` to `8a4de067...` reports **4 commits ahead, 0 behind** and the following net changes:

| File | Additions | Deletions | Effect |
|---|---:|---:|---|
| `shared/engineering.ts` | 3 | 2 | Add `MAX_GJK_ITERATIONS = 256`; reject GJK budgets above 256; tighten `validateGeometryOptions` to 1–256 with a changed diagnostic. |
| `shared/phase6-1-p2-4-a-boundary-safety.test.ts` | 62 | 6 | Add rotated Oval/GJK coverage, 257-budget rejection, 256-budget acceptance, and update option expectations. |

## 4. Exact source-tree inspection at `8a4de067...`

The exact raw source at `8a4de067...` was inspected without checkout. It contains all intended sparse-array and runtime-options changes:

- `validateDenseArray` checks every array index using an own-property test;
- the PCB root boundary validates `components`, `wires`, `tracks`, and `vias` for sparse holes;
- nested component pins, footprint pads, optional Pad layers, Via layers, and junctions are covered;
- `validateGeometryOptions` is invoked at the `validatePcb` boundary;
- malformed options produce the stable `PCB_INVALID_OPTIONS` path;
- P2.4-A test coverage is present in `shared/phase6-1-p2-4-a-boundary-safety.test.ts`.

It also contains the additional GJK contract not present at `d487e4f...`:

- `MAX_GJK_ITERATIONS = 256`;
- `gjkWithinDistance` rejects a budget greater than 256;
- `validateGeometryOptions` rejects values outside the inclusive range 1–256;
- the correction text changes to `must be an integer between 1 and 256`;
- tests exercise valid 256 and invalid 257 budgets and a rotated, non-coaxial Oval-to-Oval GJK path.

Accordingly, the runtime source tree contains all intended P2.4-A boundary-safety changes, but also contains a separately material GJK-budget policy and regression contract.

## 5. Was the 232-test verification run against the exact runtime HEAD?

Yes, with independent GitHub evidence.

The runtime report states that the isolated checkout used branch `fix/phase6-1-p2-4-a-boundary-safety-20261123` at exact HEAD `8a4de067...`. GitHub currently reports that branch at the same full SHA.

GitHub Actions independently reports:

- Workflow: `Engineering verification`;
- event: `push`;
- run: [`45181864203`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45181864203);
- exact `head_sha`: `8a4de067ede025ac134b9ddc66d19652984038b2`;
- job: [`137717407140`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45181864203/job/137717407140);
- conclusion: `success`;
- all workflow steps, including TypeScript check, automated tests, and production build: `success`.

The job log independently contains:

```text
Test Files  15 passed (15)
Tests       232 passed (232)
```

Therefore the 232-test verification was performed against the exact `8a4de067...` source HEAD. This confirms the execution claim; it does not by itself approve the additional GJK cap as part of the original P2.4-A scope.

## 6. Impact on P2.4-A verification

The impact is a scope/contract conflict, not an ancestry or test-head ambiguity:

1. The implementation report's `d487e4f...` state contains the originally described boundary-safety changes.
2. The runtime-verified `8a4de067...` state contains those changes and four later GJK-budget commits.
3. The approved P2.4 design explicitly says: **“Do not introduce an arbitrary maximum iteration budget in this remediation without a separate performance policy and evidence. If a cap is later required, specify and test it as a separate contract.”**
4. The implementation report states that the evaluator implementation and GJK contract were not changed.
5. The runtime tree does change the accepted options contract and the GJK algorithm boundary by adding a maximum of 256.
6. The runtime report does test and verify that added contract, so its test result is not invalid as an observation of the `8a4de067...` tree. The invalid part is treating the expanded tree as an unqualified, scope-compliant P2.4-A baseline without a separate approval/disposition for the GJK cap.

No historical report was modified to conceal or normalize this difference.

## 7. Assessment of the P2.4-B scope proposal

The P2.4-B proposal correctly identified the two SHA values as an unresolved dependency and correctly prohibited starting P2.4-B until the discrepancy was reconciled. It also correctly required P2.4-A to remain untouched and kept P2.4-B implementation unapproved.

After this reconciliation, the dependency must be stated more precisely:

- the exact runtime-tested source is `8a4de067...`;
- it is a descendant of `d487e4f...`;
- it includes the additional GJK cap and tests;
- P2.4-B cannot use it as an approved dependency until the GJK cap is explicitly accepted as part of P2.4-A or separated into its own approved scope;
- no P2.4-B implementation may begin under this report.

The proposal itself was not modified, because the instruction prohibits modifying historical reports and the current task is reconciliation only.

## 8. Restrictions and current disposition

This investigation made no source, test, branch, PR, reset, rebase, cherry-pick, merge, or force-push changes. No checkout was created or altered. No P2.4-B implementation was started.

**Disposition:** stop after publishing this report and wait for explicit approval. The next decision required is whether the 256-iteration GJK cap is approved as part of P2.4-A, rejected/separated as a distinct change, or otherwise formally re-scoped. Until then, P2.4-B remains not approved.

## References

- [`d487e4f...` implementation commit](https://github.com/soheil6913/-PCB-Studio-Pro/commit/d487e4f64fb007d2acb18df89c734e457e74c717)
- [`8a4de067...` runtime-verified commit](https://github.com/soheil6913/-PCB-Studio-Pro/commit/8a4de067ede025ac134b9ddc66d19652984038b2)
- [P2.2 baseline `192cac1...`](https://github.com/soheil6913/-PCB-Studio-Pro/commit/192cac1e3b0293a9ce41d9c06f01a91ae70333fe)
- [Compare P2.2 to implementation SHA](https://github.com/soheil6913/-PCB-Studio-Pro/compare/192cac1e3b0293a9ce41d9c06f01a91ae70333fe...d487e4f64fb007d2acb18df89c734e457e74c717)
- [Compare implementation SHA to runtime SHA](https://github.com/soheil6913/-PCB-Studio-Pro/compare/d487e4f64fb007d2acb18df89c734e457e74c717...8a4de067ede025ac134b9ddc66d19652984038b2)
- [P2.4 design report](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_GEOMETRY_API_REMEDIATION_DESIGN.md)
- [P2.4-A implementation report](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_BOUNDARY_SAFETY_IMPLEMENTATION_REPORT.md)
- [P2.4-A runtime verification report](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_A_RUNTIME_VERIFICATION_REPORT.md)
- [P2.4-B scope proposal](https://github.com/soheil6913/PCB/blob/main/PHASE_6_1_P2_4_B_SCOPE_AND_ACCEPTANCE_PROPOSAL.md)
