# Phase 6.1 P2.4-A — GJK Iteration Cap Removal Report

**Status:** COMPLETED — CAP REMOVED, P2.4-A BRANCH VERIFIED  
**Source repository:** [`soheil6913/-PCB-Studio-Pro`](https://github.com/soheil6913/-PCB-Studio-Pro)  
**Report repository:** [`soheil6913/PCB`](https://github.com/soheil6913/PCB)  
**Branch:** `fix/phase6-1-p2-4-a-boundary-safety-20261123`

## 1. Authorization and scope

This execution followed the project-owner authorization in `pasted_content.txt`:

- remove the unapproved `MAX_GJK_ITERATIONS = 256` policy;
- preserve all other P2.4-A boundary-safety changes;
- preserve positive-safe-integer validation and existing GJK exhaustion behavior;
- do not modify `main`, PR #3, historical reports, or start P2.4-B.

The work was performed in a fresh temporary clone of the existing P2.4-A branch. No existing workspace was changed.

## 2. Exact repository state

Pre-change read-only preflight confirmed:

| Check | Result |
|---|---|
| Required branch | `fix/phase6-1-p2-4-a-boundary-safety-20261123` — exact match |
| Before HEAD | `8a4de067ede025ac134b9ddc66d19652984038b2` — exact match |
| P2.4-A implementation reference | `d487e4f64fb007d2acb18df89c734e457e74c717` |
| P2.2 baseline | `192cac1e3b0293a9ce41d9c06f01a91ae70333fe` |
| `main` before execution | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| PR #3 before execution | Open / Draft / unmerged; unchanged |
| Pre-change worktree | Clean |

The focused commit was created and pushed to the existing P2.4-A branch only:

- **After HEAD:** `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- Commit message: `fix(pcb): remove unapproved GJK iteration cap`
- Remote branch was verified at the exact after SHA.

No reset, rebase, cherry-pick, merge, force-push, branch creation, PR modification, or `main` modification occurred.

## 3. Exact changes

The focused commit changed exactly two tracked files:

| File | Change |
|---|---:|
| `shared/engineering.ts` | 5 lines changed: remove cap constant, remove upper-bound rejection, restore positive-safe-integer options contract |
| `shared/phase6-1-p2-4-a-boundary-safety.test.ts` | 13 lines changed: remove cap-only assertions and add acceptance coverage for budgets greater than 256 |

Commit summary: **7 insertions, 11 deletions**.

### Removed

- `const MAX_GJK_ITERATIONS = 256`;
- the `maxIterations > MAX_GJK_ITERATIONS` rejection in `gjkWithinDistance`;
- the `iterations > MAX_GJK_ITERATIONS` rejection in `validateGeometryOptions`;
- the cap-specific diagnostic wording `must be an integer between 1 and 256`;
- the test whose sole purpose was rejecting `257` as above-cap;
- the duplicate `overBudget` assertion whose sole purpose was proving that `257` is rejected by the cap.

### Restored/preserved

- `gjkMaxIterations` must be a positive safe integer;
- zero, negative, fractional, NaN, Infinity, unsafe integer, and non-number values remain rejected;
- caller-supplied positive budgets are not silently replaced or capped;
- GJK exhaustion still returns `INDETERMINATE` with reason `iteration limit exhausted before convergence`;
- the rotated, non-coaxial Oval/GJK regression remains present;
- sparse-array validation and all existing options-boundary validation remain present;
- Circle/Oval behavior and existing valid-input geometry behavior were not changed.

A direct comparison confirmed that the post-change `shared/engineering.ts` is byte-identical to its P2.4-A implementation-state version at `d487e4f...`; the source therefore restores the approved pre-cap contract without changing the other P2.4-A source changes.

## 4. Required test coverage

The updated focused P2.4-A test explicitly accepts:

- `gjkMaxIterations: 257`;
- `gjkMaxIterations: Number.MAX_SAFE_INTEGER`.

The same test continues to reject:

- `null`;
- `0`;
- negative values;
- fractions;
- `NaN`;
- `Infinity`;
- `Number.MAX_SAFE_INTEGER + 1`;
- non-number strings.

Existing `phase4_1.gjk-convergence.test.ts` coverage remains unchanged and verifies positive-budget exhaustion as:

```text
INDETERMINATE
reason: iteration limit exhausted before convergence
```

The same suite verifies that `validatePcb` emits `PCB_GEOMETRY_INDETERMINATE` rather than a plausible clearance result when GJK is unresolved. The rotated Oval/GJK test remains in the P2.4-A boundary test and continues to execute with a valid budget.

## 5. Local verification

All required commands completed with exit code 0 in the isolated clone at `/tmp/p24a-cap-removal`.

| Command | Exit code | Result |
|---|---:|---|
| `pnpm install --frozen-lockfile` | 0 | Lockfile up to date; no dependency manifest or lockfile changes |
| `pnpm exec vitest run shared/phase6-1-p2-4-a-boundary-safety.test.ts shared/phase4.gjk.test.ts shared/phase4_1.gjk-convergence.test.ts shared/phase6-1-p2-2.circle-oval-contract.test.ts` | 0 | 4 files passed; 72 tests passed |
| `pnpm check` | 0 | `tsc --noEmit` passed |
| `pnpm test` | 0 | 15 files passed; 230 tests passed |
| `pnpm build` | 0 | Vite client build and esbuild server bundle passed |

The full-suite count is 230 rather than the prior 232 because the two cap-only assertions removed by this authorized change are no longer counted. The remaining P2.4-A and GJK coverage passed.

Build output retained the existing non-fatal Vite notice about `/api/platform/config.js` lacking `type="module"`; the build still exited 0.

The full local command output is recorded in `verification.log` in the temporary execution clone. No generated or ignored output was committed.

## 6. CI verification

The push triggered the repository's `Engineering verification` workflow on the exact after SHA:

- Workflow run: [`45310349263`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45310349263)
- Event: `push`
- Exact `head_sha`: `3ed17c246dadf80eab73f81bfc775845d582dbf1`
- Job: [`138164230728`](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/45310349263/job/138164230728)
- Job conclusion: `success`
- TypeScript check: success
- Automated tests: success
- Production build: success

The CI log for the exact after SHA reports:

```text
Test Files  15 passed (15)
Tests       230 passed (230)
```

The CI log also confirms execution of the P2.4-A boundary test, GJK convergence test, and Circle/Oval contract test. No CI result from another SHA is being substituted for this verification.

## 7. Preservation and repository-safety checks

- Sparse-array validation remains intact in `shared/engineering.ts` and its P2.4-A test suite.
- `options = null` and other malformed options boundary tests remain intact.
- Positive-budget GJK exhaustion and fail-closed `INDETERMINATE` behavior remain intact.
- Rotated Oval/GJK regression coverage remains intact.
- Existing Circle/Oval regression coverage remains intact.
- No dependency manifest or lockfile was changed.
- `main` was not modified.
- PR #3 was not modified or merged.
- Historical reports were not modified.
- P2.4-A remains on its existing dedicated branch.
- P2.4-B was not started and no P2.4-B branch was created.

## 8. Final disposition

**P2.4-A GJK cap removal is implemented and verified on the existing P2.4-A branch.** The unapproved fixed cap is removed, the approved positive-safe-integer contract is restored, and all required local and CI checks pass on `3ed17c246dadf80eab73f81bfc775845d582dbf1`.

P2.4-B remains unapproved. Stop here and wait for explicit approval before any P2.4-B work.
