# PHASE 6.1 — P2.4-D-8 Independent IEEE-754 Numerical Evidence Gap Closure

**Repository:** `soheil6913/PCB`  
**Phase:** P2.4-D-8  
**Scope:** evidence and verification only; no production behavior, tests, CI, or historical evidence were modified  
**Date:** 2026-11-28

## 1. Executive verdict

**Verdict: `PARTIALLY_VALIDATED`**

D8 independently reproduced the principal D7 observations and closed **0 of 16** unresolved cases. All 16 remain explicitly inventoried and unresolved. The fresh run reproduced 19 JavaScript vectors, 40/40 exact finite binary64 operation checks, 4/19 literal MPFR interval containments, 17/19 unique-cell sine agreements, 18/19 unique-cell cosine agreements, and 3/19 exact-real Model-A-to-stepwise-Model-B output containments.

The evidence is sufficient to validate the existence and reproducibility of the observed stepwise behavior, signed-zero distinctions, and non-finite propagation observations. It is not sufficient to claim universal correctly rounded ECMAScript trigonometric behavior, full numerical correctness, or equivalence between the exact-real and stepwise models.

## 2. Source attestation

D8 required the independent capture to use `PCB_SOURCE_WORKTREE=/tmp/p24d7-source` and rejected the capture unless all of the following held: expected HEAD `941262899a46e54cbf1a94a4da6dd528b8d36780`, clean worktree, and unchanged `shared/engineering.ts`.

| Attestation item | Result |
|---|---|
| Expected D1 source HEAD | `941262899a46e54cbf1a94a4da6dd528b8d36780` |
| Observed source HEAD | `941262899a46e54cbf1a94a4da6dd528b8d36780` |
| Source worktree | Clean |
| Attested file | `/tmp/p24d7-source/shared/engineering.ts` |
| File SHA-256 | `545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9` |
| File size | 81,255 bytes |
| Operation order | `degrees * Math.PI / 180`, then `Math.cos`/`Math.sin`, products, subtraction/addition, translation |

The original accepted P2.4-C source baseline was separately checked as clean at `327fc0479031279b889ea1dd1140a23d4abe442f`. It was not edited.

## 3. Complete 16-case unresolved inventory

Every case from D7 is retained. “Reproduced” means the D8 rerun regenerated the corresponding captured/MPFR evidence; it does **not** mean the numerical issue was proven correct.

| ID | Issue and existing evidence | Missing proof / required evidence | Severity | Disposition |
|---|---|---|---|---|
| `ordinary-45` | JS trig lies outside at least one directed MPFR interval; Model-A output enclosure excludes Model B | Directed-rounding interval plus independent JS comparison without assuming universal libm correctness | Medium | Remains unresolved for D9 |
| `ordinary-90` | Same trig and Model-A/Model-B containment gap; exact-axis sign/cancellation is relevant | MPFR interval, independent JS bit comparison, signed-zero proof | Medium | Remains unresolved for D9 |
| `ordinary-180` | Same trig and Model-A/Model-B containment gap; exact-axis sign/cancellation is relevant | MPFR interval, independent JS bit comparison, signed-zero proof | Medium | Remains unresolved for D9 |
| `ordinary-270` | Same trig and Model-A/Model-B containment gap; exact-axis sign/cancellation is relevant | MPFR interval, independent JS bit comparison, signed-zero proof | Medium | Remains unresolved for D9 |
| `ordinary-360` | Same trig and Model-A/Model-B containment gap; exact-axis sign/cancellation is relevant | MPFR interval, independent JS bit comparison, signed-zero proof | Medium | Remains unresolved for D9 |
| `negative-angle` | Trig interval mismatch and Model-A/Model-B containment gap under negative argument reduction | Directed interval and independent JS bit comparison for negative-angle reduction | Medium | Remains unresolved for D9 |
| `adjacent-45` | Trig interval mismatch and Model-A/Model-B containment gap near an adjacent boundary | Adversarial boundary testing and independent JS bit comparison | Medium | Remains unresolved for D9 |
| `adjacent-90` | Trig interval mismatch and Model-A/Model-B containment gap near an adjacent boundary | Adversarial boundary testing and independent JS bit comparison | Medium | Remains unresolved for D9 |
| `adjacent-180` | Trig interval mismatch and Model-A/Model-B containment gap near an adjacent boundary | Adversarial boundary testing and independent JS bit comparison | Medium | Remains unresolved for D9 |
| `adjacent-270` | Trig interval mismatch and Model-A/Model-B containment gap near an adjacent boundary | Adversarial boundary testing and independent JS bit comparison | Medium | Remains unresolved for D9 |
| `adjacent-360` | Trig interval mismatch and Model-A/Model-B containment gap near an adjacent boundary | Adversarial boundary testing and independent JS bit comparison | Medium | Remains unresolved for D9 |
| `large-cancellation` | Trig mismatch and transformed output enclosure failure under cancellation-sensitive arithmetic | Directed MPFR intervals plus exact binary64 replay of final operations | Medium | Remains unresolved for D9 |
| `large-opposite` | Trig mismatch and transformed output enclosure failure with opposite-scale operands | Directed MPFR intervals plus exact binary64 replay of final operations | Medium | Remains unresolved for D9 |
| `huge-angle` | Trig mismatch and Model-A/Model-B containment gap for extreme argument reduction | Independent execution across runtimes plus a separately specified argument-reduction reference; implementation-dependent until then | High | Remains unresolved for D9 |
| `max-angle` | Trig mismatch, Model-A/Model-B containment gap, and no unique output binary64 cell | MPFR interval, output-cell comparison, and explicit overflow/non-finite boundary proof | High | Remains unresolved for D9 |
| `overflow-translation` | Model-A/Model-B output containment failure at overflow translation boundary | Binary64 bit comparison, independent JS execution, and explicit IEEE-754 non-finite propagation proof | High | Remains unresolved for D9 |

The machine-readable version, including exact booleans, source final bit patterns, and ULP fields where available, is `evidence/p2-4-d-8/unresolved-case-inventory.json`.

## 4. Reproduction results

The D8 run used a fresh capture output and a fresh MPFR output rather than treating the published D7 JSON as the result. The results were:

| Check | Result |
|---|---:|
| JavaScript capture vectors | 19 |
| Exact finite binary64 operations | 40/40 |
| Midpoint ties-to-even cases | 4/4 |
| D7 evidence regression suite | 7/7 passed |
| Unique sine output cells | 18/19 |
| JS sine agreement with unique MPFR cell | 17/19 |
| Unique cosine output cells | 18/19 |
| JS cosine agreement with unique MPFR cell | 18/19 |
| Literal trig interval containment | 4/19 |
| Model-A output interval contains Model-B output | 3/19 |
| D8 unresolved cases closed | 0/16 |
| D8 unresolved cases remaining | 16/16 |

The fresh capture and MPFR output are preserved as `d8-javascript-capture.json` and `d8-mpfr-results.json`. The exact binary64 suite output is `d8-binary64-results.json`.

## 5. Signed-zero semantics

A standalone Node probe recorded observable binary64 bit patterns, including `Math.sin(-0)`, `Math.cos(-0)`, arithmetic sign rules, and `Object.is(x, -0)`. The probe recorded 11 signed-zero observations. It confirmed that real equality is insufficient: `-0 === 0` is true while the bit pattern and `Object.is` distinction remain observable. The probe also recorded signed-zero behavior through addition, subtraction, multiplication, division by negative infinity, and `Math.atan2`.

The MPFR probe using `gmpy2==2.3.2` at 256-bit precision recorded distinct internal binary serializations for `+0` and `-0`, while ordinary equality and numerical zero predicates identify both as zero. This establishes why MPFR real-interval serialization cannot by itself attest JavaScript signed-zero conventions. Signed zero therefore remains part of the unresolved semantic boundary rather than being silently normalized.

Artifacts: `javascript-ieee754-semantics.json` and `mpfr-signed-zero-semantics.json`.

## 6. Extreme values and non-finite behavior

The standalone JavaScript probe evaluated 121 combinations of signed zero, smallest subnormal, largest finite value, infinities, NaN, large finite values, and degrees including `0`, `-0`, ordinary angles, `1e20`, `Number.MAX_VALUE`, infinities, and NaN. It recorded:

- 57 vectors with a non-finite input;
- 65 vectors with at least one NaN output;
- 20 vectors with at least one infinite output;
- 7 vectors with a negative-zero output.

These are observations of the pinned Node/V8 runtime and the stated operation sequence. They are not a universal claim about every ECMAScript implementation's trigonometric library. Overflow, underflow, NaN propagation, infinity arithmetic, signed zero, and extreme-angle argument reduction require explicit specification and bit-level tests before being treated as closed.

Artifact: `javascript-ieee754-semantics.json`.

## 7. Trigonometric compatibility and mismatch investigation

D8 reproduced the D7 counts exactly. There were 15 vectors with a literal directed-interval trig mismatch. For each mismatch, the artifact records the vector ID, trig bits, whether each unique binary64 cell was available, whether the JavaScript result agreed with that cell, Model-A/Model-B output containment, output-cell uniqueness, and ULP differences where defined.

The evidence supports the narrower conclusion that the pinned JavaScript runtime produced these observed binary64 values and that the selected MPFR enclosure did not contain every observed value. It does **not** establish that JavaScript violates ECMAScript, that the MPFR interval is a complete model of the implementation's permitted error, or that all ECMAScript engines must agree. The 4/19 literal interval containments and 3/19 final-coordinate containments remain evidence gaps, not production-failure classifications.

Artifact: `unresolved-case-inventory.json` under `trigonometric_mismatch_investigation`.

## 8. Independent proof strategy

The D8 mapping is explicit for every case:

- **Exact rational arithmetic:** finite binary64 operations and midpoint/ties-to-even checks where the operands and operation are specified exactly.
- **Directed-rounding MPFR intervals:** exact-real Model A bounds and cancellation-sensitive coordinates.
- **Binary64 bit-level comparison:** all signed-zero, subnormal, overflow, underflow, NaN, infinity, and unique-cell claims.
- **Independent JavaScript execution:** actual Model B operation order, runtime capture, and cross-runtime comparison where needed.
- **Directed-rounding interval arithmetic:** any claim that a real-valued enclosure contains a stepwise result.
- **Adversarial boundary testing:** adjacent angles, exact-axis angles, extreme arguments, and non-finite transitions.

Model A remains the exact-real/MPFR interval model. Model B remains the actual stepwise JavaScript binary64 model. They are intentionally not merged or substituted for one another.

## 9. Limitations and blockers

The principal blocker is the absence of a proof that the selected ECMAScript `Math.sin`/`Math.cos` implementation is universally correctly rounded or that its implementation-specific error is bounded by the current MPFR intervals. Extreme-angle reduction and cross-engine behavior are likewise not closed. MPFR interval arithmetic models real values and directed rounding; it does not automatically reproduce every implementation detail of a JavaScript libm call or JavaScript signed-zero convention.

No production source, existing test, CI workflow, `main`, P2.4-C branch, P2.4-D-7 branch, or historical report was modified. No remediation was implemented, and no PR or merge was created.

## 10. Reproducibility instructions

From the D8 report worktree, with the pinned source checkout present:

```bash
export PCB_SOURCE_WORKTREE=/tmp/p24d7-source
export PCB_EXPECTED_SOURCE_SHA=941262899a46e54cbf1a94a4da6dd528b8d36780
D7=/tmp/p24c-numerical-uncertainty/archive/evidence/p2-4-d-7
PCB_SOURCE_WORKTREE="$PCB_SOURCE_WORKTREE" PCB_EXPECTED_SOURCE_SHA="$PCB_EXPECTED_SOURCE_SHA" \
  CAPTURE_OUTPUT=/tmp/p24d8-repro-javascript.json \
  /tmp/p24c-numerical-uncertainty/source/node_modules/.bin/tsx "$D7/capture.ts"
python3 "$D7/analyze.py" /tmp/p24d8-repro-javascript.json \
  "python3 $D7/mpfr_eval.py" /tmp/p24d8-repro-mpfr.json
python3 "$D7/binary64_suite.py" /tmp/p24d8-repro-binary64.json
python3 -m unittest discover -s "$D7" -p 'evidence_tests.py' -v
python3 evidence/p2-4-d-8/d8_independent_analysis.py \
  /tmp/p24d8-repro-javascript.json /tmp/p24d8-repro-mpfr.json \
  /tmp/p24d8-inventory.json
node evidence/p2-4-d-8/js_semantics_probe.mjs /tmp/p24d8-js-semantics.json
python3 evidence/p2-4-d-8/mpfr_signed_zero_probe.py /tmp/p24d8-mpfr-zero.json
```

The source attestation must fail for a wrong HEAD, dirty worktree, wrong source path, or changed `shared/engineering.ts`; no vector result is accepted before attestation.

## 11. Explicit D9 acceptance criteria

D9 may close a case only when all applicable criteria are met and the case-specific artifact identifies the exact proof:

1. The source HEAD, canonical source path, clean status, and source hash are independently attested before capture.
2. Model A and Model B are represented separately, with no interval result silently substituted for a JavaScript bit result.
3. Every claimed final binary64 value has its exact hexadecimal bits and an independently reproducible comparison.
4. Signed-zero behavior is compared by bits and observable JavaScript predicates, not by real-number equality alone.
5. Non-finite, underflow, overflow, NaN, infinity, and extreme-angle cases have adversarial boundary vectors and explicit propagation results.
6. Any trig compatibility claim states the exact runtime and library context and does not generalize to universal ECMAScript correctness without a separately valid proof.
7. Every prior unresolved case has a case-specific proof or remains explicitly unresolved; none may disappear through aggregation.
8. Repeated runs are byte-identical where deterministic serialization is claimed, and local/remote evidence commit SHAs are verified equal.
9. No production implementation or behavior is changed as part of the evidence closure.

## 12. Final engineering recommendation

Keep the numerical implementation unchanged. Accept D8 only as a reproducible evidence-gap inventory and semantic characterization. Do not promote the result to `FULLY_VALIDATED`, do not treat the trig mismatches as a universal ECMAScript defect, and require D9 to address the 16 named cases using the proof criteria above.
