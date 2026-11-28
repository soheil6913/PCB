# PHASE 6.1 — P2.4-D-11 Geometry Remediation Contract Closure Report

**Repository:** `soheil6913/PCB`  
**Documentation branch:** `evidence/phase6-1-p2-4-d-11-geometry-remediation-contract-closure-20261128`  
**Scope:** independent adversarial design review and closure investigation only. No source, test, CI, main branch, historical artifact, merge, pull request, or implementation was changed.  
**Report base:** `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`  
**Decision:** `CONDITIONALLY_READY`

## Decision and boundary

The P2.4-D remediation contract is conditionally ready for a future implementation-readiness review. The five previously explicit questions can now be resolved at the design level using the later published design-closure artifact: route45 has a deterministic checked/legacy boundary; arbitrary-angle trigonometry is interval-certified rather than based on an unsupported `Math.sin`/`Math.cos` accuracy claim; transform validity is defined by binary64 output-cell containment; ellipse distance has deterministic proof-budget semantics; and public numeric helpers remain compatibility wrappers while engineering consumers use checked internal results.

This decision is not implementation approval. The contract remains blocked from source work until the proof artifacts, independent oracle evidence, resource-budget measurements, compatibility fixtures, and source-baseline decision listed below are reviewed and accepted. The permitted decision is therefore `CONDITIONALLY_READY`, not `CONTRACT_READY_FOR_IMPLEMENTATION_REVIEW` as an unconditional approval and not authorization to begin implementation.

The machine-readable matrix is preserved at [`evidence/p2-4-d-11/contract-closure-matrix.json`](evidence/p2-4-d-11/contract-closure-matrix.json).

## Artifact provenance and missing PDF

The exact requested artifact `PHASE_6.1_—_P2.pdf` was not found in the inspected filesystem, in the fetched report-repository refs, or in reachable Git history. The recoverable contract is the Markdown artifact published on the numerical-remediation contract branch:

- Contract branch: `docs/phase-6-1-p2-4-d-numerical-remediation-contract-20261124`
- Contract head: `e43ec1f116b0f266e8df886943f174c46810a19c`
- Contract blob: `0005c0a00c380c7d74ea6c81be9cd3202d476cfb`
- Contract blob size: 43,866 bytes
- Local candidate filename: `PHASE_6.1_—_P2 (1).md`
- Candidate SHA-256: `66e344233179e5205a32ca34c78bf9006461d481c33631a58073bfc39243b294`

The independent audit is preserved separately:

- Branch: `docs/phase-6-1-p2-4-d-independent-audit-20261124`
- Head: `dbe85a25bd7ffbe316988292c36369f48133de60`
- Blob: `b80eb14fefa2120e5061d7af809fa5a030369c3f`
- Candidate SHA-256: `976657007775cce4f94df72a2ea7b35d9e43293c68cfba724a44f8c9edb6a026`

The later closure artifact is not silently treated as the original contract. It is a supplementary design-closure report on branch `docs/phase-6-1-p2-4-d-design-closure-20261126`, head `54929160cfc0347d690101501886c287dc34a7ed`. It contains the resolutions reviewed here and explicitly retains implementation-proof gates. No original artifact was overwritten or revised.

## Baselines and applicability

The requested references are valid Git commit objects and the ancestry checks were independently repeated:

| Reference | SHA | Applicability disposition |
|---|---|---|
| P2.4-B | `e567acb883a0f81cb0c64d11f638b5f872511346` | Exact intended implementation baseline stated by the contract. |
| P2.4-C original | `21b7487eec431dcb993a44d0d642a33644141526` | Historical unmerged compatibility/reference baseline. |
| Accepted P2.4-C remediation | `327fc0479031279b889ea1dd1140a23d4abe442f` | Accepted unmerged compatibility target; not a prerequisite for D implementation. |
| Historical source `main` | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` | Current historical source-main reference; neither P2.4-B nor P2.4-C is an ancestor of this main. |

The accepted P2.4-C commit is descended from P2.4-B and from the P2.4-C original, and the historical source `main` is an ancestor of that accepted remediation branch. This does not mean the remediation is merged into source `main`. The contract is therefore implementable against the exact P2.4-B tree only if a future implementation explicitly checks out or derives from that tree. A future implementation review must not describe P2.4-C behavior as already present in source `main`.

The report repository and original evidence branches were preserved. D7–D10 identities are:

| Checkpoint | Branch | Published commit |
|---|---|---|
| D7 | `evidence/phase6-1-p2-4-d-7-ieee754-stepwise-20261128` | `9fc6b2cae447b0669833b510aa9979cd80abd43b` |
| D8 | `evidence/phase6-1-p2-4-d-8-independent-gap-closure-20261128` | `02fd0426eae61ac094834fbba80d0a890433a6a5` |
| D9 | `evidence/phase6-1-p2-4-d-9-adversarial-ieee754-20261128` | `c9833c4f2ab2ac941c8d45a46f7e1ba3abcf8a0c` |
| D10 | `evidence/phase6-1-p2-4-d-10-oracle-strategy-20261128` | `c226871885453685fcb06f160425e5b7cf99eaa8` |

All were verified as published remote refs during this review. The source checkouts and D7–D10 worktrees were not modified.

## Finding scope and adversarial review

This review retains exactly the three confirmed findings and does not promote potential ellipse overflow to a fourth finding. The three findings are:

1. **`P24D-ROUTE45-OVERFLOW`** — finite endpoint subtraction or waypoint construction can overflow or round back to an endpoint, creating duplicate or invalid route geometry.
2. **`P24D-ROTATION-CANCELLATION`** — direct two-product rotation can produce a large spurious residual or non-finite output for finite extreme coordinates, especially under cancellation.
3. **`P24D-SHAPE-SCALE-TOLERANCE`** — fixed absolute `1e-12` orientation/on-segment tests can turn a small, genuinely positive rectangle gap into zero distance.

The contract correctly separates forward numerical error from classification error. Compensated arithmetic can preserve low parts, but it cannot certify arbitrary-angle coefficients. Exact finite binary64 dyadic orientation can prove determinant sign or zero, but it does not prove Euclidean distance. Rectangle/oval distances must be interval-certified or explicitly indeterminate. This distinction is central to both the rotation and shape findings.

The contract also preserves the correct fail-closed engineering rule. An uncertain transformed pad, pin, wire, or net may affect only directly dependent conclusions. It must not produce a false union, fabricated zero, or clearance pass, and it must not suppress unrelated findings. This is a localized safety state, not a claim that the affected geometry has been solved.

## Q1–Q5 closure matrix

The complete machine-readable matrix contains exactly five question rows. The review status is summarized here:

| Question | Closure disposition | Required condition before implementation review can approve source work |
|---|---|---|
| **Q1** route45 behavior | **Closed conditionally.** `route45Checked` returns `NON_REPRESENTABLE`; legacy `route45` returns `[start,end]` for finite unrepresentable endpoints and `[]` for invalid input. The endpoint-only result is not labelled or interpreted as route45 by the client. | Freeze ordinary two-/three-point output, invalid input, duplicate-waypoint, transactional, and direct-fallback fixtures. |
| **Q2** trig provider and angle semantics | **Closed conditionally.** Use a documented dependency-free interval trig kernel with exact input decomposition, conservative range reduction, bounded polynomial error, and outward widening. `Math.sin`/`Math.cos` alone cannot certify `VALID`. | Independently review the generated constants, pi/reduction bounds, remainder proof, outward-rounding method, runtime support, and high-precision oracle corpus. |
| **Q3** `VALID` transform | **Closed conditionally.** The full enclosure must lie in one binary64 round-to-nearest-even output cell, with proven tie handling. “Within one ULP” is insufficient. | Review output-cell construction and test powers of two, subnormals, signed zero, ties, and finite overflow boundaries. |
| **Q4** ellipse proof budget and DRC semantics | **Closed conditionally.** Use deterministic interval branch-and-bound with `4096` cells, `32768` interval evaluations, and depth `32`; exhaustion is stable `INDETERMINATE`, not zero or a GJK policy. DRC remains error/fail-closed for uncertainty. | Approve limits after independent-oracle validation and representative performance measurements; verify deterministic counters and wrapper propagation. |
| **Q5** public compatibility boundary | **Closed conditionally.** Preserve public `rotatePoint`/`transformLocalPoint` signatures and ordinary behavior; use checked internal transforms for DRC/topology and never treat public best-effort output as proof. | Lock public fixtures, audit new consumers, test extreme divergence, and verify localized pad/pin uncertainty. |

These resolutions match the later design-closure document. They close policy choices but do not claim that the software proof packages or tests already exist.

## Finding-specific acceptance matrix

| Finding | Required acceptance result |
|---|---|
| `P24D-ROUTE45-OVERFLOW` | Ordinary route45 output remains unchanged. Opposite-sign `MAX_VALUE` and waypoint/delta overflow cannot produce duplicate or zero-length tracks. Checked failure is transactional. A direct fallback, if offered, is separately labelled and independently representable; no client infers route45 validity from the legacy array. |
| `P24D-ROTATION-CANCELLATION` | Special angles use exact identities only when proven. Arbitrary angles use certified coefficient intervals. Product, cancellation, translation, overflow, underflow, signed-zero, and output-cell errors are enclosed. Uncertain pads cannot clear; uncertain pins cannot union; unrelated findings continue. |
| `P24D-SHAPE-SCALE-TOLERANCE` | The absolute `1e-12` policy is removed without a replacement epsilon. Exact dyadic orientation is used only for classification. The `1e-7` width / approximately `2e-13` gap remains positive when proven. Nonlinear distance exhaustion or non-representability is fail-closed and never guessed zero or clearance pass. |

The JSON file contains the expanded criteria, including ordinary compatibility, invalid-input, transformed-state, interval, DRC, and localization requirements.

## D10 integration and what remains unresolved

D10 materially limits what can be claimed. ECMAScript specifies binary64 Number behavior but leaves non-boundary `Math.sin` and `Math.cos` implementation-approximated. MPFR can certify a mathematical exact-input interval with explicit precision, directed rounding, error bounds, and a unique target-cell stopping rule; it does not automatically certify the actual JavaScript runtime’s transcendental approximation or reproduce stepwise JavaScript semantics. Model A exact-real evaluation and Model B runtime evaluation must remain separate unless a runtime-specific approximation bound is supplied.

Accordingly, D10 does not close D9’s 16 unresolved cases through this geometry contract. D7–D10 evidence remains evidence-chain material and a constraint on the oracle design, not a blanket proof of production trig behavior. Any future `VALID` arbitrary-angle transform must use a proof package that accounts for this limitation or return `INDETERMINATE`.

The later closure report identifies the following material gates:

- trig polynomial, range-reduction, outward-rounding, and remainder proof artifacts;
- independent high-precision oracle evidence for coefficient and distance corpora;
- reviewed binary64 output-cell reference logic;
- measured and approved ellipse budget adequacy;
- frozen route45 and public-transform compatibility fixtures;
- explicit P2.4-C adapter and integration review, without assuming the unmerged branch is in `main`.

No compatibility tests, production tests, CI, or benchmarks were run in D11. This is intentional and required by the design-only authorization. No claim in this report means that any acceptance test has passed.

## Compatibility and regression obligations

A future implementation review must require the same oracle vectors against the exact P2.4-B baseline plus D, the accepted unmerged P2.4-C target plus D, and any separately authorized integrated branch. It must preserve public signatures, ordinary route45 output, Circle/Oval behavior, P2.4-A GJK boundary and exhaustion semantics, P2.4-B detailed/wrapper contracts, P2.4-C localized uncertainty semantics, schema-v2 and legacy dispatch, DRC finding IDs and order, and fail-closed behavior.

The contract’s prohibition on arbitrary GJK iteration caps remains intact. The ellipse branch-and-bound limits are resource safeguards whose exhaustion is an explicit geometry-indeterminate state; they must not change GJK semantics or convert exhaustion into a geometry conclusion.

## Residual risks

The largest residual risk is conflating a precise policy design with an implemented proof. A fixed budget is deterministic, but its adequacy is not established until measured against an independent corpus. A software interval trig kernel is feasible, but generated constants and remainder bounds are not self-authenticating. A public compatibility wrapper protects signatures, but it can reintroduce the original defect if new engineering code calls it instead of the checked path. Finally, the P2.4-B/P2.4-C/source-main relationship must remain explicit because the accepted P2.4-C remediation is unmerged.

Potential ellipse overflow remains a contract risk only. It is not promoted to a confirmed finding because the available audit did not establish an independent false classification beyond the confirmed small-scale strict-predicate defect.

## Final decision

**`CONDITIONALLY_READY`**

The P2.4-D contract is ready to enter a future implementation-readiness review only after the named proof, oracle, benchmark, compatibility, and baseline-applicability gates are presented. It is not ready for source implementation, test changes, CI changes, merge, pull-request activity, or any later phase. D11 stops at this report and matrix publication.

## References

[1]: https://github.com/soheil6913/PCB/tree/docs/phase-6-1-p2-4-d-numerical-remediation-contract-20261124 "Published P2.4-D numerical remediation contract branch"

[2]: https://github.com/soheil6913/PCB/tree/docs/phase-6-1-p2-4-d-independent-audit-20261124 "Published P2.4-D independent audit branch"

[3]: https://github.com/soheil6913/PCB/tree/docs/phase-6-1-p2-4-d-design-closure-20261126 "Published P2.4-D design-closure branch"

[4]: https://github.com/soheil6913/PCB/tree/evidence/phase6-1-p2-4-d-10-oracle-strategy-20261128 "Published D10 oracle strategy report"

[5]: https://github.com/soheil6913/-PCB-Studio-Pro/tree/fix/phase6-1-p2-4-c-numerical-uncertainty-remediation-20261124 "Accepted unmerged P2.4-C source remediation branch"

[6]: https://tc39.es/ecma262/2026/multipage/numbers-and-dates.html#sec-math.sin "ECMAScript 2026 Math.sin"

[7]: https://tc39.es/ecma262/2026/multipage/numbers-and-dates.html#sec-math.cos "ECMAScript 2026 Math.cos"

[8]: https://www.mpfr.org/mpfr-4.2.1/mpfr.html "GNU MPFR 4.2.1 Manual"
