# PHASE 6.1 — P2.4-D-12 Proof Artifacts and Implementation Readiness Report

**Repository:** `soheil6913/PCB`  
**Documentation branch:** `evidence/phase6-1-p2-4-d-12-proof-artifacts-implementation-readiness-20261128`  
**Scope:** independent evidence-only verification. No source, production test, CI workflow, report `main`, D7–D11 evidence, merge, rebase, reset, cherry-pick, force-push, PR, or implementation was performed.  
**Report base:** report `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`  
**Decision:** **`NOT_READY`**

## Final decision

The P2.4-D design is **not ready to authorize a separate implementation-planning phase**. The critical blockers are not merely unfinished test coverage. The proposed interval trigonometric kernel has no published constants, reduction derivation, remainder proof, or directed-rounding construction. The 16 D8/D9 cases remain unresolved as propositions: all 16 were independently adjudicated, zero were closed, 3 have reproducible experimental support only, and 13 remain open. The proposed ellipse budgets are unvalidated because the proposed certified evaluator is absent from the exact P2.4-B source baseline. The baseline call-site audit shows that unchecked transforms and tolerance-based shape predicates are still the actual implementation paths.

This decision does not reject the design direction. It preserves the D11 policies as design assumptions and identifies the smallest evidence package needed before a later readiness review. It does not authorize source implementation, test changes, CI changes, or any later phase.

## Preservation and provenance attestation

The following identities were verified before evidence generation:

| Item | Verified identity or state |
|---|---|
| Report `origin/main` | `5ef6266cd002fb835824bb9e6f588ab07f99a0ba` |
| D11 branch | `evidence/phase6-1-p2-4-d-11-geometry-remediation-contract-closure-20261128` |
| D11 commit | `1106443b890dc9f64d46bdc47d13ea1f0f5eac59` |
| D7 commit | `9fc6b2cae447b0669833b510aa9979cd80abd43b` |
| D8 commit | `02fd0426eae61ac094834fbba80d0a890433a6a5` |
| D9 commit | `c9833c4f2ab2ac941c8d45a46f7e1ba3abcf8a0c` |
| D10 commit | `c226871885453685fcb06f160425e5b7cf99eaa8` |
| D11 source baseline | P2.4-B `e567acb883a0f81cb0c64d11f638b5f872511346` |
| Current source `main` | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| D1 attested source | HEAD `941262899a46e54cbf1a94a4da6dd528b8d36780`; `shared/engineering.ts` SHA-256 `545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9` |

The report and source worktrees were clean when inspected. The accepted P2.4-C remediation `327fc0479031279b889ea1dd1140a23d4abe442f` is a descendant of P2.4-B, but it is not an ancestor of current source `main`. P2.4-C behavior must therefore remain a compatibility target, not a claim about current `main`.

D7–D10 report files and their referenced manifests, inventories, and matrices exist on their published branches. D11 exists as its published report and closure matrix. No prior evidence was rewritten. The exact requested PDF contract remains unavailable in this environment; D12 uses the preserved Markdown contract and records that limitation rather than treating absence as proof of global nonexistence.

## Six-gate status

| Gate | Status | Evidence-based disposition |
|---|---|---|
| A. Interval trigonometry proof | **OPEN** | D11 specifies a kernel shape but supplies no constants, range-reduction derivation, remainder proof, or conservative JavaScript widening construction. `Math.sin`/`Math.cos` remain implementation-approximated under ECMAScript. |
| B. Independent oracle and 16-case closure | **OPEN** | 16/16 cases were reviewed. 0 closed; 3 experimentally supported only; 13 open. MPFR mathematical intervals and runtime agreement do not prove a runtime-independent or language-wide property. |
| C. Binary64 output-cell reference and propagation | **CONDITIONAL** | D12 independently generated exact midpoint/predecessor/successor vectors for normal, subnormal, zero, tie, binade, and largest-finite boundaries. This validates a reference specification, not a production implementation. Baseline consumers discard uncertainty, so integration remains open. |
| D. Ellipse interval budget | **OPEN** | The 4096/32768/32 values are design parameters. No certified evaluator exists in the exact P2.4-B tree, so counters, runtime, memory, and deterministic exhaustion cannot be measured. Status is explicitly `UNVALIDATED`. |
| E. Compatibility and call-site audit | **FAIL** | Exact P2.4-B call sites still use raw route45, raw transforms, fixed `1e-12` predicates, and finite scalar distance consumers. No checked route/transform path exists in the baseline. |
| F. Baseline and contract compatibility | **CONDITIONAL** | Git identities and ancestry are verified. The future implementation target is P2.4-B, with P2.4-C as an unmerged adapter target. A future implementation-planning phase must choose and document this baseline explicitly. |

Because A, B, D, and E contain correctness-critical open failures, the final decision cannot be `READY_FOR_IMPLEMENTATION_PLANNING` or `CONDITIONALLY_READY` under the supplied rules.

## Workstream A — interval trigonometry proof review

The D11 proposal is a valid list of proof obligations, not a proof artifact. Exact binary64 input decomposition is mathematically tractable when raw bits are imported as sign, exponent, and significand and represented as a dyadic rational. D7–D10 provide reproducible raw-bit evidence. This supports the input model experimentally and mathematically, subject to preserving signed zero and non-finite classifications.

The remaining trigonometric steps are open. A dependency-free kernel needs a concrete bounded representation for π and any degree conversion, a quotient/range-reduction derivation that proves the selected quadrant, a documented polynomial and domain, a rigorous approximation remainder bound over that domain, and an outward enclosure method for every arithmetic operation. JavaScript Number operations do not supply directed rounding automatically. A `nextUp`/`nextDown` widening rule can be part of a proof, but only after its bit-level behavior and error relation are established for normals, subnormals, zero, overflow, and underflow.

The proposed `BigInt` path can provide exact integer or fixed-point components. It does not by itself represent real π, prove a real-valued remainder, or provide outward rounding for mixed Number operations. A high-precision MPFR result can certify the mathematical function on exact inputs when precision, directed modes, error bounds, and a unique-cell stopping rule are recorded. It cannot certify an arbitrary JavaScript engine's `Math.sin` or `Math.cos` result without a runtime-specific approximation contract. These are separate models and remain separate in D12.

The proof-review matrix records each claim, assumptions, evidence, independent method, failure mode, and status in [`proof-review-matrix.json`](evidence/p2-4-d-12/proof-review-matrix.json). The central trig-kernel claims are `OPEN`, not `PROVEN`.

## Workstream B — independent oracle and 16 unresolved cases

The D12 case inventory preserves all 16 authoritative identifiers from D9. The independent adjudication workflow applied one rule to every case: a case closes only when the original proposition is independently established. Reproduction, a 256-bit MPFR comparison, a unique output cell, or agreement between two implementations does not close a proposition when the missing runtime approximation and operation-order assumptions remain material.

The outcome is:

- **0/16 closed**;
- **3/16 experimentally supported only:** `ordinary-270`, `negative-angle`, and `large-cancellation`;
- **13/16 open:** all remaining identifiers;
- **16/16 remain unresolved for closure purposes**.

The machine-readable inventory is [`oracle-case-inventory.json`](evidence/p2-4-d-12/oracle-case-inventory.json). It preserves the original properties, reproduction fields, proof status, closure flag, reason, and source artifact. This result does not claim that the observed runtime behavior is false. It says that the available evidence does not prove the stronger proposition.

## Workstream C — binary64 output-cell reference and uncertainty propagation

D12 independently generated exact midpoint vectors using raw Python binary64 values, `math.nextafter`, and exact rational midpoint calculations. The vector set covers positive and negative normal values, positive and negative zero, minimum positive and negative subnormals, the largest subnormal, smallest normal, a power-of-two binade transition, and the largest finite value. The largest-finite vector explicitly records the positive-infinity overflow boundary rather than attempting to convert infinity into an exact fraction.

The reference proves only the shape of a cell specification. It does not prove a production `nextUp`/`nextDown` implementation, a tie-to-even implementation, or a transform consumer. In particular, proving that a mathematical coordinate rounds uniquely to one binary64 value does not prove that a downstream orientation, intersection, distance, or clearance predicate is correct.

The baseline call-site evidence shows why this is an integration blocker. `transformLocalPoint` returns a plain `Point` at `shared/engineering.ts:32`. `localPads` consumes it at line 125, schematic pin validation consumes it at line 340, and PCB DRC consumes derived pad positions through `padToPadDistanceDetailed` at line 381. There is no enclosure/state channel in the P2.4-B implementation. Until every proof-sensitive consumer preserves or safely consumes uncertainty, output-cell certification cannot authorize geometry conclusions.

The independent vectors are [`binary64-output-cell-vectors.json`](evidence/p2-4-d-12/binary64-output-cell-vectors.json).

## Workstream D — ellipse interval budget

The exact P2.4-B source has rectangle/oval distance paths at `shared/engineering.ts:261-262` and dispatches them from `padToPadDistanceDetailed` at line 292. It does not contain the D11 proposed adaptive interval branch-and-bound evaluator, deterministic priority queue, certified counters, or exhaustion state.

The proposed values `MAX_CERTIFIED_CELLS = 4096`, `MAX_INTERVAL_EVALUATIONS = 32768`, and `MAX_SUBDIVISION_DEPTH = 32` are therefore unvalidated design parameters. D12 did not substitute a production implementation, increase the limits to obtain more examples, or claim benchmark results. Ordinary, tangent, coincident, scale-extreme, high-aspect-ratio, near-zero, overflow, dependency-widening, slow-convergence, and exhaustion classes are listed with their required reference evidence and remain `UNVALIDATED`.

The DRC semantic requirement is clear but not proven in the absent evaluator: certified positive lower bounds may support separation; unresolved intervals must become `INDETERMINATE`; uncertainty must remain an Error-severity fail-closed result; equality at the configured clearance threshold still requires an explicit policy fixture; and no budget may change GJK behavior. The assessment is [`ellipse-budget-validation.json`](evidence/p2-4-d-12/ellipse-budget-validation.json).

## Workstream E — compatibility and call-site audit

The exact P2.4-B source audit found the following baseline paths:

- `route45` at `shared/engineering.ts:33` uses raw endpoint subtraction, absolute `EPSILON` comparisons, and returns only an array. No `route45Checked` API or client proof boundary exists.
- `rotatePoint` at line 31 uses `Math.sin`/`Math.cos` and direct two-product arithmetic. `transformLocalPoint` at line 32 adds the rotated point to the origin without a checked result.
- `localPads` at line 125 transforms footprint pads; `evaluatePcbV2` collects them at line 372.
- `validateSchematic` transforms pins at line 340 and uses the resulting point in connectivity union decisions.
- `strictOrientation`, `strictOnSegment`, and `strictSegmentsIntersect` at lines 256–258 use the fixed absolute `1e-12` policy. `strictSegmentDistance` and `rectToRectDistance` at lines 259–261 consume it.
- `padToPadDistanceDetailed` at line 292 returns finite scalar distances for rectangle/oval paths. `evaluatePcbV2` at line 381 compares finite results to DRC thresholds and maps only indeterminate/non-finite results to `PCB_GEOMETRY_INDETERMINATE`.

These are not proposed implementation defects; they are the baseline facts that the future checked design must replace or adapt. The call-site artifacts are [`route45-callsite-inventory.json`](evidence/p2-4-d-12/route45-callsite-inventory.json), [`transform-callsite-inventory.json`](evidence/p2-4-d-12/transform-callsite-inventory.json), and [`shape-distance-callsite-inventory.json`](evidence/p2-4-d-12/shape-distance-callsite-inventory.json).

The principal compatibility risks are that `[start,end]` can be mistaken for a valid route45 result, public Point-returning transforms cannot carry uncertainty, raw transformed pins can be union candidates, and a finite scalar distance can be interpreted as proof after an uncertainty-bearing computation. These risks are not closed by D11 policy text alone.

## Workstream F — baseline and contract compatibility

The P2.4-B baseline `e567acb...` is the exact tree named by the contract. P2.4-C original `21b7487e...` is a child of P2.4-B. Accepted P2.4-C remediation `327fc047...` changes `shared/engineering.ts` and adds `shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts`; it remains unmerged. Current source `main` `a98384b...` is not descended from P2.4-B, P2.4-C original, or accepted remediation. The P2.4-C remediation must not be described as present in current `main`.

The compatibility matrix is [`baseline-compatibility-matrix.json`](evidence/p2-4-d-12/baseline-compatibility-matrix.json). Future planning must choose one of two explicit routes: plan against the exact P2.4-B tree and later adapt to P2.4-C, or separately authorize a baseline integration decision before D implementation. Silent substitution is prohibited.

## Mathematical status classification

The D12 artifacts distinguish the required categories:

- **Mathematically proven or directly derivable:** the binary64 dyadic interpretation of raw finite input bits, subject to exact import; the Git ancestry and identity relationships; and the formal statement that MPFR mathematical evaluation is not automatically a JavaScript runtime oracle.
- **Experimentally supported:** the D7–D10 raw-bit captures, directed MPFR records, unique-cell observations, and the three case observations marked experimentally supported in the D12 inventory. These remain runtime- and artifact-scoped observations.
- **Design assumptions:** D11's dependency-free interval trig architecture, output-cell validity criterion, checked/legacy route boundary, checked transform boundary, and 4096/32768/32 ellipse budget.
- **Open:** the trig remainder and runtime approximation proofs, complete Model-A/Model-B relation, production output-cell implementation, uncertainty-preserving consumers, ellipse budget adequacy, and compatibility fixtures.

The full claim matrix is [`proof-review-matrix.json`](evidence/p2-4-d-12/proof-review-matrix.json).

## Evidence artifact hashes

| Artifact | SHA-256 |
|---|---|
| `proof-review-matrix.json` | `185e42ca689dc882596d958c87dfc169a42387609215431e12557cb0e7ca4b87` |
| `oracle-case-inventory.json` | `e97c193948328213ea90f7c959143a4ac64ea5c3f2a44e2618aa0c2aac17fe7a` |
| `binary64-output-cell-vectors.json` | `ecdb244757bc04d1e59abd34212edb89f3b1a6533bd1623679c5d32f49143db0` |
| `ellipse-budget-validation.json` | `a735bc41a37b67f2248a4bc04f193b58921232f006e89448e723f3dc7be2d3fd` |
| `route45-callsite-inventory.json` | `ce54eb28c10ec2c3e9419818f9f15e62080d370dd55e81223231366147b51b4e` |
| `transform-callsite-inventory.json` | `465c73d6f2430f0604217aabcff7d39a49228dd029e778b1d548c421dda01d71` |
| `shape-distance-callsite-inventory.json` | `c140fd1373d6b5e88be5fc4acaa146a8fb411e1911a768b435e4f52e781cc85c` |
| `baseline-compatibility-matrix.json` | `962f9054c25330f2200eaa6f4054b3b77e9f01798b03079da2a55a90cb545f3a` |
| `evidence-method-manifest.json` | `0d905de357ddc0ffa9d6881ccf90aa519e96f045ae52158647fb4fdd9b61dad3` |
| `generate_evidence.py` | `edffa67e4ad0868e6fd24a4003c4b342f2f6bf8beafa7ff455c0514b1e4352f3` |

Every JSON artifact documents its schema or field definitions. The generator is evidence-only and does not import production source.

## Preservation attestation

- Source code unchanged.
- Production tests unchanged.
- CI workflows unchanged.
- Report `main` unchanged by D12.
- D7–D11 evidence unchanged.
- No merge, PR, reset, rebase, cherry-pick, or force-push performed.
- No production implementation or test execution against the source tree performed.
- D12 work is isolated on the new documentation branch.
- The only executed code was the evidence-only Python generator and JSON validation; no production behavior is claimed from it.

## Exact next recommended phase

The next phase should be **P2.4-D-13 — targeted proof-package development and review**, still evidence-only unless separately authorized. It should address, in order: (1) an independently reviewable interval-trig constant/remainder package; (2) a reviewed binary64 output-cell reference with signed-zero and overflow semantics; (3) an explicit uncertainty-preserving consumer contract; and (4) a separately designed ellipse evaluator benchmark corpus. It must not begin source implementation, merge P2.4-C, or change GJK policy.

## References

[1]: https://github.com/soheil6913/PCB/tree/evidence/phase6-1-p2-4-d-11-geometry-remediation-contract-closure-20261128 "Published D11 contract-closure evidence"

[2]: https://github.com/soheil6913/PCB/tree/evidence/phase6-1-p2-4-d-10-oracle-strategy-20261128 "Published D10 oracle-strategy evidence"

[3]: https://github.com/soheil6913/PCB/tree/evidence/phase6-1-p2-4-d-9-adversarial-ieee754-20261128 "Published D9 adversarial IEEE-754 evidence"

[4]: https://github.com/soheil6913/PCB/tree/evidence/phase6-1-p2-4-d-8-independent-gap-closure-20261128 "Published D8 independent evidence-gap closure"

[5]: https://github.com/soheil6913/PCB/tree/evidence/phase6-1-p2-4-d-7-ieee754-stepwise-20261128 "Published D7 stepwise IEEE-754 evidence"

[6]: https://github.com/soheil6913/PCB/tree/docs/phase-6-1-p2-4-d-numerical-remediation-contract-20261124 "Published P2.4-D numerical remediation contract"

[7]: https://github.com/soheil6913/-PCB-Studio-Pro/tree/fix/phase6-1-p2-4-c-numerical-uncertainty-remediation-20261124 "Accepted unmerged P2.4-C source remediation"

[8]: https://tc39.es/ecma262/2026/multipage/numbers-and-dates.html#sec-math.sin "ECMAScript 2026 Math.sin"

[9]: https://tc39.es/ecma262/2026/multipage/numbers-and-dates.html#sec-math.cos "ECMAScript 2026 Math.cos"

[10]: https://www.mpfr.org/mpfr-4.2.1/mpfr.html "GNU MPFR 4.2.1 Manual"
