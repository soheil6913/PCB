# PHASE 6.1 — P2.4-D-9 Adversarial IEEE-754 Unresolved-Case Closure

**Repository:** `soheil6913/PCB`  
**Scope:** independent evidence only; no production or historical evidence changes  
**Date:** 2026-11-28

## 1. Executive verdict

**Verdict: `PARTIALLY_VALIDATED`**

D9 independently reproduced all required D7/D8 evidence and investigated all 16 authoritative D8 unresolved identifiers individually. **0 cases were closed; 16 remain unresolved.** Reproduction is not counted as closure: each original proposition still lacks sufficient independent proof under the available assumptions.

The evidence establishes actual pinned-runtime observations, exact binary64 bit patterns, directed MPFR comparison results, signed-zero distinctions, and non-finite propagation observations. It does not establish universal correctly rounded ECMAScript trigonometric behavior or equivalence between the exact-real and stepwise models.

## 2. Source and evidence attestations

The authoritative D8 inventory was retrieved from the D8 evidence artifact and contains exactly 16 identifiers. No identifier was reconstructed or invented.

| Item | Attested value |
|---|---|
| D8 branch | `evidence/phase6-1-p2-4-d-8-independent-gap-closure-20261128` |
| D8 commit | `02fd0426eae61ac094834fbba80d0a890433a6a5` |
| D7 report commit | `9fc6b2cae447b0669833b510aa9979cd80abd43b` |
| P2.4-C source baseline | `327fc0479031279b889ea1dd1140a23d4abe442f` |
| Pinned D1 source HEAD | `941262899a46e54cbf1a94a4da6dd528b8d36780` |
| Source path | `/tmp/p24d7-source/shared/engineering.ts` |
| Source SHA-256 | `545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9` |
| Source worktree | Clean |

D9's fresh capture independently observed the expected D1 source HEAD and clean status before producing vectors. The complete attestation is in `evidence/p2-4-d-9/case-by-case-closure.json` and `d9-javascript-capture.json`.

## 3. D9-F regression results

| Required check | Result |
|---|---:|
| Fresh JavaScript capture vectors | 19/19 |
| Exact finite binary64 operations | 40/40 |
| Midpoint ties-to-even checks | 4/4 |
| Dedicated evidence regression tests | 7/7 passed |
| Unique sine cells | 18/19 |
| JS sine agreement with unique MPFR cell | 17/19 |
| Unique cosine cells | 18/19 |
| JS cosine agreement with unique MPFR cell | 18/19 |
| Literal trig interval containment | 4/19 |
| Model-A output interval contains Model-B output | 3/19 |

All results matched the D7/D8 reproduction counts. Fresh artifacts are `d9-javascript-capture.json`, `d9-mpfr-results.json`, and `d9-binary64-results.json`.

## 4. Complete individual case closure matrix

The following table preserves every D8 identifier. The independent oracle was executed or recorded for every row. A row is closed only if its original unresolved proposition is answered, not merely because its runtime observation reproduced.

| ID | Original unresolved proposition | Independent oracle and exact evidence | Determination | Final disposition |
|---|---|---|---|---|
| `ordinary-45` | Trig result outside a directed MPFR interval; Model A excludes Model B | Node/V8 capture, exact input/output bits, MPFR interval and unique-cell comparison | Reproducible runtime mismatch; implementation-dependent under assumptions | Not closed |
| `ordinary-90` | Same trig and Model-A/Model-B gap at an axis angle | Node/V8 bits, directed MPFR, signed-zero probe | Bounded observation; no universal trig proof | Not closed |
| `ordinary-180` | Same trig and Model-A/Model-B gap at an axis angle | Node/V8 bits, directed MPFR, signed-zero probe | Bounded observation; no universal trig proof | Not closed |
| `ordinary-270` | Same trig and Model-A/Model-B gap at an axis angle | Node/V8 bits, directed MPFR, signed-zero probe | Bounded observation; no universal trig proof | Not closed |
| `ordinary-360` | Same trig and Model-A/Model-B gap at an axis angle | Node/V8 bits, directed MPFR, signed-zero probe | Bounded observation; no universal trig proof | Not closed |
| `negative-angle` | Negative-angle trig mismatch and Model-A/Model-B gap | Independent JS execution, exact bits, directed MPFR interval | Argument-reduction behavior remains runtime-specific | Not closed |
| `adjacent-45` | Boundary-adjacent trig mismatch and output gap | Adversarial capture plus MPFR and unique-cell comparison | Boundary observation reproduced; proof absent | Not closed |
| `adjacent-90` | Boundary-adjacent trig mismatch and output gap | Adversarial capture plus MPFR and unique-cell comparison | Boundary observation reproduced; proof absent | Not closed |
| `adjacent-180` | Boundary-adjacent trig mismatch and output gap | Adversarial capture plus MPFR and unique-cell comparison | Boundary observation reproduced; proof absent | Not closed |
| `adjacent-270` | Boundary-adjacent trig mismatch and output gap | Adversarial capture plus MPFR and unique-cell comparison | Boundary observation reproduced; proof absent | Not closed |
| `adjacent-360` | Boundary-adjacent trig mismatch and output gap | Adversarial capture plus MPFR and unique-cell comparison | Boundary observation reproduced; proof absent | Not closed |
| `large-cancellation` | Trig mismatch and transformed-coordinate enclosure failure under cancellation | Directed MPFR interval plus exact final-operation binary64 bits | Cancellation-sensitive relation remains unproven | Not closed |
| `large-opposite` | Trig mismatch and transformed-coordinate enclosure failure for opposite-scale operands | Directed MPFR interval plus exact final-operation binary64 bits | Cancellation-sensitive relation remains unproven | Not closed |
| `huge-angle` | Extreme argument-reduction mismatch and Model-A/Model-B gap | Independent JS bits, MPFR interval, extreme-angle probe | Runtime/library-specific; no authoritative universal bound | Not closed |
| `max-angle` | Trig mismatch, output gap, and non-unique output cell | MPFR interval, binary64-cell comparison, non-finite boundary probe | Cell and overflow proof incomplete | Not closed |
| `overflow-translation` | Model-A/Model-B gap at overflow translation boundary | Independent JS special-value propagation and exact bits | Runtime behavior observed; model correspondence unresolved | Not closed |

The full machine-readable record includes exact input bits, `rad_bits`, `x_bits`, `y_bits`, `ox_bits`, `oy_bits`, trig interval flags, output-cell flags, oracle method, and disposition: `evidence/p2-4-d-9/case-by-case-closure.json`.

## 5. D9-B: ECMAScript trigonometric compatibility

All 15 recorded mismatch cases were individually retained and compared against the fresh MPFR output. The evidence layers are deliberately separated:

1. **Specification layer:** this report makes no claim that ECMAScript universally mandates correctly rounded `Math.sin` or `Math.cos`.
2. **Runtime layer:** Node `v22.23.4`, V8 `12.4.254.21-node.57`, Linux x64 produced the captured values and bits.
3. **Reference layer:** MPFR 256-bit directed-rounding intervals were calculated from exact binary64 inputs.
4. **Correct-rounding layer:** unique MPFR binary64 cells were compared where available; 17/19 sine and 18/19 cosine comparisons agreed.
5. **Error-bound layer:** no authoritative universal bound was established that connects every runtime result to the current intervals.

Therefore the 15 mismatches are reproducible implementation/reference discrepancies under this test setup, not proof of an ECMAScript violation or a universal incorrect-rounding result.

## 6. D9-C: signed-zero bit-level results

The fresh JavaScript probe recorded 11 signed-zero observations, including:

- `Math.sin(-0)` and `Math.cos(-0)`;
- signed zero through addition, subtraction, multiplication, division by negative infinity, and `Math.atan2`;
- raw 64-bit patterns and `Object.is(x, -0)` observations.

The MPFR probe recorded distinct binary serializations for `+0` and `-0`, while ordinary equality treats both as zero. This demonstrates that real-number equality and decimal serialization cannot establish JavaScript floating-point semantic equivalence. Artifact files:

- `javascript-ieee754-semantics.json`
- `mpfr-signed-zero-semantics.json`

Signed-zero observations are closed as observations of the pinned runtime, but not as a universal production-model equivalence proposition.

## 7. D9-D: non-finite and extreme values

The fresh probe evaluated 121 combinations of signed zero, the smallest subnormal, largest finite values, infinities, NaN, large finite values, and angles including `1e20`, `Number.MAX_VALUE`, infinities, and NaN. It recorded:

- 57 vectors with a non-finite input;
- 65 vectors with at least one NaN output;
- 20 vectors with at least one infinite output;
- 7 vectors with a negative-zero output.

These results are exact observations of the stated JavaScript runtime and operation sequence. They distinguish overflow, underflow, subnormal, NaN, infinity, and signed-zero behavior at the bit level, but they do not establish a cross-engine or exact-real equivalence theorem. Artifact: `javascript-ieee754-semantics.json`.

## 8. D9-E: independent oracle methodology

The analysis preserves these distinct models:

- **Exact-real Model A:** MPFR directed-rounding intervals and parsed exact fractions.
- **Stepwise JavaScript Model B:** the source-attested sequence with binary64 rounding at each operation.
- **MPFR reference calculations:** high-precision directed bounds, not a substitute for JavaScript libm behavior.
- **Actual JavaScript outputs:** observed Node/V8 bits, not a universal specification claim.

Exact rational arithmetic and ties-to-even checks establish the finite binary64 conversion suite. MPFR intervals bound the selected real-valued calculations. Independent JavaScript probes establish observable runtime semantics. None of these assumptions are merged automatically.

## 9. Reproduction instructions

```bash
export PCB_SOURCE_WORKTREE=/tmp/p24d7-source
export PCB_EXPECTED_SOURCE_SHA=941262899a46e54cbf1a94a4da6dd528b8d36780
D7=/tmp/p24c-numerical-uncertainty/archive/evidence/p2-4-d-7
/tmp/p24c-numerical-uncertainty/source/node_modules/.bin/tsx "$D7/capture.ts"
python3 "$D7/analyze.py" <capture.json> "python3 $D7/mpfr_eval.py" <mpfr.json>
python3 "$D7/binary64_suite.py" <binary64.json>
python3 -m unittest discover -s "$D7" -p 'evidence_tests.py' -v
python3 evidence/p2-4-d-9/d9_case_closure.py \
  /tmp/p24d8-report/evidence/p2-4-d-8/unresolved-case-inventory.json \
  <capture.json> <mpfr.json> evidence/p2-4-d-9/case-by-case-closure.json
node evidence/p2-4-d-9/js_semantics_probe.mjs evidence/p2-4-d-9/javascript-ieee754-semantics.json
python3 evidence/p2-4-d-9/mpfr_signed_zero_probe.py evidence/p2-4-d-9/mpfr-signed-zero-semantics.json
```

The source attestation must pass before accepting any vector. The D9 case generator asserts 16 cases, 0 closures, 16 remaining, and 15 trig mismatches.

## 10. Remaining limitations and blockers

No independent proof established a universal correct-rounding guarantee for ECMAScript trigonometric functions. Extreme-angle argument reduction, implementation-specific libm behavior, signed-zero conversion boundaries, and exact-real versus stepwise output correspondence remain open. MPFR does not automatically model every JavaScript runtime behavior.

Because the original unresolved propositions remain unanswered, D9 cannot promote any case to closed despite complete reproduction. No production remediation is authorized or implemented.

## 11. Explicit acceptance matrix

The machine-readable acceptance matrix in `case-by-case-closure.json` contains one row for each of the 16 identifiers. Every row has `reproduced: true`, `oracle_established: false`, and `closed: false`. This is intentional: reproducibility is recorded separately from proof closure, as required by the D9 authorization.

| Metric | Result |
|---|---:|
| Authoritative inventory cases | 16 |
| Individually investigated | 16 |
| Reproduced | 16 |
| Independent oracles established sufficiently to close | 0 |
| Closed | 0 |
| Remaining | 16 |
| Trigonometric mismatch cases investigated | 15 |

## 12. Final engineering recommendation

Retain the current production behavior and evidence-only separation. Do not claim full numerical correctness, do not classify the 15 trig mismatches as universal ECMAScript defects, and do not merge or remediate geometry behavior based on this evidence phase. Another evidence phase is justified only if it has a concrete authoritative oracle or specification-level proof strategy for the remaining propositions.

D10 was not started.
