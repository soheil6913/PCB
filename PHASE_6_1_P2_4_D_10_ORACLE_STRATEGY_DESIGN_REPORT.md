# PHASE 6.1 — P2.4-D-10 Independent Oracle Strategy Design

**Repository:** `soheil6913/PCB`  
**Documentation branch:** `evidence/phase6-1-p2-4-d-10-oracle-strategy-20261128`  
**Scope:** design-only; no production implementation, test, CI, source, main branch, or historical evidence changes  
**Report base HEAD before publication:** `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`

## 1. Executive verdict

**Decision: `B. PARTIALLY ESTABLISHED`**

A defensible oracle strategy exists for specified finite binary64 operations, exact input-bit interpretation, directed-rounding mathematical intervals, midpoint handling, and explicitly specified runtime observations. It does not provide a language-wide correctly-rounded oracle for `Math.sin` or `Math.cos`, because ECMAScript 2026 deliberately leaves non-boundary results implementation-approximated. It also does not establish a general Model-A-to-Model-B equivalence theorem without additional implementation-specific error bounds and operation-by-operation analysis.

Consequently, no D11 reproduction campaign is justified under the current assumptions. A future targeted phase would be meaningful only if it supplies a concrete runtime-scoped oracle, an authoritative error bound, or a specification-level proof obligation that is not available here.

## 2. Verified repository and baseline identities

The D10 pre-investigation audit checked the exact report repository, branches, HEADs, remotes, and worktree status. The report repository is `soheil6913/PCB`, with origin at `https://github.com/soheil6913/PCB.git`.

| Reference | Verified identity |
|---|---|
| D7 branch | `evidence/phase6-1-p2-4-d-7-ieee754-stepwise-20261128` |
| D7 report commit | `9fc6b2cae447b0669833b510aa9979cd80abd43b` |
| D8 branch | `evidence/phase6-1-p2-4-d-8-independent-gap-closure-20261128` |
| D8 commit | `02fd0426eae61ac094834fbba80d0a890433a6a5` |
| D9 branch | `evidence/phase6-1-p2-4-d-9-adversarial-ieee754-20261128` |
| D9 commit | `c9833c4f2ab2ac941c8d45a46f7e1ba3abcf8a0c` |
| Accepted P2.4-C source checkout | HEAD `327fc0479031279b889ea1dd1140a23d4abe442f` |
| P2.4-C source `main` ref | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| D1 attested source | HEAD `941262899a46e54cbf1a94a4da6dd528b8d36780` |
| D1 source file | `/tmp/p24d7-source/shared/engineering.ts` |
| D1 source SHA-256 | `545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9` |

All checked source and evidence worktrees were clean during the audit. No mismatch was found between the D7, D8, D9, D1, and P2.4-C identities recorded above. They are different repositories or branches for distinct purposes, but their recorded commit identities agree with the independently observed Git state. No baseline was silently reconciled or substituted.

## 3. D7–D9 evidence-chain integrity

D9’s authoritative machine-readable inventory contains exactly these 16 identifiers: `ordinary-45`, `ordinary-90`, `ordinary-180`, `ordinary-270`, `ordinary-360`, `negative-angle`, `adjacent-45`, `adjacent-90`, `adjacent-180`, `adjacent-270`, `adjacent-360`, `large-cancellation`, `large-opposite`, `huge-angle`, `max-angle`, and `overflow-translation`.

D9 independently reproduced 19/19 capture vectors, 40/40 exact finite binary64 checks, 4/4 midpoint checks, and 7/7 dedicated evidence tests. It investigated all 15 recorded trigonometric mismatches and closed 0 of 16 cases. D10 treats that inventory as authoritative and does not reconstruct or replace it. The complete D10 matrix is preserved in `evidence/p2-4-d-10/case-adjudication-matrix.json`; the D9 inventory itself is not modified.

## 4. Official ECMAScript analysis

### 4.1 Number and binary64 semantics

ECMAScript 2026 clause 6.1.6.1, “The Number Type,” states that the Number type represents IEEE 754-2019 binary64 values, with the specification’s NaN treatment. It explicitly recognizes positive and negative zero, positive and negative infinity, finite normalized and denormalized values, and the Number-value selection procedure for exact real quantities. That procedure uses nearest selection with ties-to-even, maps the two overflow endpoint sentinels to infinities, and selects negative zero when the exact real is negative and rounds to zero. [1]

This supports a rigorous oracle for specified binary64 conversions and ordinary binary64 operations, provided the operation order and special-value rules are the actual properties under proof. It does not by itself identify the internal bit pattern of every NaN: the same clause notes that ArrayBuffer-observable bits need not equal an implementation’s internal representation and that ECMAScript code treats NaN payloads as indistinguishable. [1]

### 4.2 Math.sin and Math.cos

Clause 21.3.2.31, “Math.sin ( x ),” requires `ToNumber`, returns the input for NaN and both zero values, returns NaN for either infinity, and otherwise returns an **implementation-approximated** Number representing the sine of the real Number argument. Clause 21.3.2.12, “Math.cos ( x ),” requires NaN for non-finite input, +1 for either zero, and otherwise an implementation-approximated Number representing the cosine of the real Number argument. [2] [3]

The same Math clause states that the behavior of `sin`, `cos`, and related functions is not precisely specified except for specific boundary cases. It says that the choice of approximation algorithms is left to the implementation and that fdlibm is recommended, not specified. [2]

Clause 4.4.1 defines an implementation-approximated facility as one that defers definition to an external source while recommending ideal behavior. Conforming implementations remain free to choose behavior within the specification’s constraints and are encouraged to approximate the ideal. [4]

**Answer to the required question:** ECMAScript does **not** require `Math.sin` and `Math.cos` to return the correctly rounded binary64 result for every finite input. The normative clauses require the listed boundary results and an implementation-approximated mathematical result elsewhere; they do not impose a universal correctly-rounded binary64 result.

### 4.3 Normative versus informative status

The individual Math algorithms and Number semantics are normative specification algorithms. The statement that non-boundary Math functions are not precisely specified, the implementation latitude, and the fdlibm recommendation appear in a Note in the Math section; the individual algorithms nevertheless explicitly use the normative term “implementation-approximated.” The clause 4.4.1 definition explains that term in the specification’s overview conventions. The result is clear even without treating the recommendation as a requirement: no language-wide correctly-rounded guarantee is present.

## 5. MPFR oracle architecture

MPFR is a strong candidate for the mathematical side of the oracle. Its official manual states that input variables are regarded as exact and that destination values are correctly rounded as if the exact result were computed at infinite precision and then rounded to the destination precision. It documents `MPFR_RNDN` as ties-to-even and `MPFR_RNDD`/`MPFR_RNDU` as downward/upward directed rounding. It also defines ternary results that indicate whether a rounded value is below, equal to, or above the exact result. [5]

A defensible certificate architecture is therefore:

1. Decode each JavaScript input from its hexadecimal binary64 bits into an exact rational or exact MPFR value. Do not pass a decimal that has already undergone an unrecorded conversion.
2. Set precision explicitly and record the precision in the artifact.
3. Evaluate the mathematical expression with directed lower and upper rounding. Preserve the sign of zero and classify NaN and infinities separately.
4. Increase precision until the lower and upper results, when converted to the target binary64 format, identify the same rounding cell. Use an explicit error bound and a stopping test rather than treating a high precision as self-authenticating.
5. Handle a midpoint only after proving the exact value is at the midpoint or proving the enclosure lies strictly on one side. Apply ties-to-even from the target binary64 significands.
6. If the interval crosses a rounding boundary, report “non-unique target cell,” not a guessed binary64 result.
7. Record endpoint bit patterns, exact input bits, rounding modes, precision, ternary information, flags, and the stopping decision.

The MPFR manual documents `mpfr_can_round` as a mechanism for deciding whether an approximation with a stated error bound can be correctly rounded to a target precision. It also warns that transcendental functions can be hard to round and that very large internal precision may be needed because of Table Maker’s Dilemma. [5] This is why a 256-bit result is evidence, not automatically a certificate.

MPFR is an oracle for a mathematical function applied to exact inputs. It is not an oracle for the implementation-specific approximation chosen by a JavaScript engine’s `Math.sin`/`Math.cos`, and it does not reproduce JavaScript’s intermediate binary64 rounding unless the stepwise operations are explicitly modeled.

An independent second implementation or proof method is necessary when the conclusion depends on the oracle itself. The strongest design is to use MPFR directed intervals plus an independent exact-rational binary64 cell checker, and to cross-check selected transcendental cases with a separately validated correctly-rounded library or a formal argument-reduction certificate. Agreement between two implementations is still not a proof unless their common assumptions and error bounds are documented.

## 6. Model A versus Model B

**Model A** is the exact-real mathematical evaluation of the intended expression. It uses exact binary64 inputs interpreted as real numbers, mathematical trigonometric functions, and directed interval propagation.

**Model B** is the actual JavaScript sequence: `degrees * Math.PI / 180`, then runtime `Math.cos`/`Math.sin`, then binary64 products, subtraction/addition, and translation. Each intermediate is rounded according to the actual runtime and operation order.

A rigorous relation can be established only under explicit assumptions. For ordinary finite arithmetic, one can bound each correctly rounded operation by half an ulp under the specified binary64 mode, propagate intervals, and separately account for cancellation. Overflow, underflow, subnormals, and signed zero require branch-specific IEEE-754 reasoning. For trigonometric steps, a Model-A-to-Model-B theorem additionally needs a proved error bound for the actual runtime transcendental implementation and argument reduction. ECMAScript does not supply that bound.

Thus, a Model B output can be a valid result of the JavaScript program even when it is not the correctly rounded Model A result. That is not automatically a production defect: the language permits implementation-approximated Math results. Conversely, Model A interval containment cannot be claimed when the runtime result lies outside the interval unless the interval explicitly includes the implementation’s allowed approximation error. Cancellation can amplify a small trig or intermediate error; overflow and underflow can change the relevant target cells; signed zero can be erased by real-number abstraction. The missing proof information is the runtime’s actual approximation/error envelope and the exact assumptions connecting that envelope to the mathematical interval.

## 7. Complete 16-case adjudication matrix

The following matrix contains each authoritative D9 identifier exactly once. The full machine-readable fields are in `evidence/p2-4-d-10/case-adjudication-matrix.json`.

| Case ID | Input class | ECMAScript support | Oracle strategy | Classification | Closure criterion |
|---|---|---|---|---|---|
| `ordinary-45` | Finite angle | Boundary rules only; non-boundary trig implementation-approximated | Attested runtime bits plus MPFR interval and unique-cell comparison | Runtime-specific | Runtime-scoped certificate or authoritative error bound |
| `ordinary-90` | Finite axis angle | Boundary behavior for zero/infinity; this call remains implementation-approximated | Bits, MPFR, signed-zero checks | Runtime-specific | Same, with axis sign proof |
| `ordinary-180` | Finite axis angle | Same | Bits, MPFR, signed-zero checks | Runtime-specific | Same, with axis sign proof |
| `ordinary-270` | Finite axis angle | Same | Bits, MPFR, signed-zero checks | Runtime-specific | Same, with axis sign proof |
| `ordinary-360` | Finite axis angle | Same | Bits, MPFR, signed-zero checks | Runtime-specific | Same, with axis sign proof |
| `negative-angle` | Finite negative angle | Non-boundary trig is implementation-approximated | Runtime bits, directed interval, argument-reduction comparison | Runtime-specific | Attested runtime argument-reduction/error certificate |
| `adjacent-45` | Finite boundary-adjacent angle | No universal correct-rounding rule | Adversarial vectors plus MPFR cell comparison | Runtime-specific | Boundary family certificate, not one reproduction |
| `adjacent-90` | Finite boundary-adjacent angle | Same | Adversarial vectors plus MPFR cell comparison | Runtime-specific | Same |
| `adjacent-180` | Finite boundary-adjacent angle | Same | Adversarial vectors plus MPFR cell comparison | Runtime-specific | Same |
| `adjacent-270` | Finite boundary-adjacent angle | Same | Adversarial vectors plus MPFR cell comparison | Runtime-specific | Same |
| `adjacent-360` | Finite boundary-adjacent angle | Same | Adversarial vectors plus MPFR cell comparison | Runtime-specific | Same |
| `large-cancellation` | Finite cancellation-sensitive operands | Binary64 arithmetic is specified; intended exact expression differs from stepwise expression | Exact operation replay plus directed intervals | Conditionally provable | Operation-by-operation bound proves final cell |
| `large-opposite` | Finite opposite-scale operands | Same | Exact operation replay plus directed intervals | Conditionally provable | Same, including cancellation |
| `huge-angle` | Extreme finite angle | Trig remains implementation-approximated | Runtime/library attestation plus independent argument-reduction oracle | Runtime-specific | Fully attested runtime certificate or language-level bound |
| `max-angle` | Extreme angle and non-unique output cell | Binary64 boundaries specified; trig approximation not | MPFR intervals, cell test, runtime argument reduction, overflow proof | Not currently provable | Unique cell plus all runtime and overflow obligations |
| `overflow-translation` | Overflow/non-finite translation boundary | Binary64 special values specified; Model-A relation is not automatic | Raw bits, special-value propagation, signed-zero total order | Conditionally provable | All special-value bits and model assumptions bounded |

The 15 previously recorded trig mismatches map one-to-one to the first 15 trig-related rows above: all rows except `overflow-translation`. They are not separate hidden cases. D10 preserves their D9 identities and treats each as a runtime observation that requires a runtime-specific proof to close.

## 8. Runtime-specific evidence requirements

Any claim about an actual JavaScript runtime must record the engine and exact version, V8 or equivalent build identity, operating system and architecture, math-library implementation where discoverable, compiler and floating-point settings where relevant, and a reproducible execution environment. Cross-runtime comparison is useful to identify implementation dependence, but disagreement or agreement across a small sample does not create a language-wide theorem.

A result from Node `v22.23.4` on Linux x64 is therefore a claim about that captured environment unless a broader proof is supplied. The D7–D9 artifacts correctly record this limitation and do not generalize the observations to all ECMAScript implementations.

## 9. Adversarial failure analysis

| Failure mode | Prevention and verification |
|---|---|
| MPFR input was rounded before entry | Decode exact hexadecimal binary64 bits; record exact fractions and reject decimal-only provenance. |
| Precision falsely appears to prove a unique cell | Repeat at increasing precision; require an explicit error bound and same target cell at both directed endpoints. |
| Directed bounds are not outward-rounded | Use explicit RNDD/RNDU calls, record modes and endpoint order, and independently compare endpoint fractions. |
| Midpoint misclassified | Prove strict separation or exact midpoint; inspect adjacent significands and apply ties-to-even. |
| Signed zero erased | Store raw bits and `Object.is`/total-order observations separately from real intervals. |
| Extreme-angle reduction unjustified | Require an independently validated reduction/error certificate or classify as runtime-specific. |
| Model A and B semantics conflated | Keep exact-real intervals and actual stepwise capture in separate artifacts and separate conclusions. |
| Runtime evidence generalized to the language | Record engine/build/platform and cite the implementation-approximated Math clauses. |
| Reproduction called closure | Maintain separate `reproduced` and `proof-established` fields; D9’s 16 rows demonstrate this rule. |

## 10. Explicit proof gaps

The remaining gaps are not missing repetitions of the same capture. They are missing propositions: an authoritative bound for each runtime’s trig approximation and argument reduction; a complete operation-level Model-A/Model-B relation under cancellation, overflow, underflow, and signed zero; and a certificate protocol that identifies a unique target cell whenever the exact result is near a midpoint. ECMAScript intentionally does not supply the first item for non-boundary `Math.sin`/`Math.cos`.

## 11. D11 decision

**D11 is not justified as another generic reproduction campaign.** It would repeat already reproducible observations without supplying the missing proof authority. A narrowly scoped future phase could be justified only if it starts with a concrete new input: for example, an engine-specific documented error bound, a separately validated correctly-rounded implementation with a proof-grade interface, or a formal operation-level model accepted for the target runtime. Without such an input, the technically correct outcome is to retain the 16 cases as unresolved.

## 12. Reproducibility and preservation

The D10 audit commands checked repository HEADs, branches, remotes, clean statuses, and remote refs before authoring. The report branch was created from report-repository `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`. The official sources consulted were retrieved directly from the URLs in References below. No D7, D8, or D9 artifact was edited.

The final publication commit SHA and remote equality are reported in the completion message after the new branch is pushed. The report’s matrix generator and JSON matrix are documentation/evidence artifacts only; they do not import or modify production source.

## References

[1]: https://tc39.es/ecma262/2026/multipage/ecmascript-data-types-and-values.html#sec-ecmascript-language-types-number-type "ECMAScript 2026, 6.1.6.1 The Number Type"

[2]: https://tc39.es/ecma262/2026/multipage/numbers-and-dates.html#sec-math.sin "ECMAScript 2026, 21.3.2.31 Math.sin"

[3]: https://tc39.es/ecma262/2026/multipage/numbers-and-dates.html#sec-math.cos "ECMAScript 2026, 21.3.2.12 Math.cos"

[4]: https://tc39.es/ecma262/2026/multipage/overview.html#sec-implementation-approximated "ECMAScript 2026, 4.4.1 implementation-approximated"

[5]: https://www.mpfr.org/mpfr-4.2.1/mpfr.html "GNU MPFR 4.2.1 Manual"
