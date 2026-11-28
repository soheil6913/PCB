# P2.4-D-7 — IEEE-754 Stepwise Compatibility and Reference Attestation

## Verdict

**IEEE754_STEPWISE_COMPATIBILITY_PARTIALLY_VALIDATED**

The evidence harness successfully attested the required P2.4-D-1 source checkout, reproduced the actual TypeScript operation order, captured JavaScript binary64 intermediates with exact 64-bit patterns, independently checked finite binary64 operations with exact rational rounding, and compared 19 adversarial transform vectors against a 256-bit MPFR directed-rounding model.

The result is intentionally **partial**, not universal validation. The evidence identifies real distinctions between exact-real Model A and stepwise JavaScript Model B, including output-cell differences under cancellation. It also leaves explicit unresolved cases for non-finite inputs and JavaScript signed-zero semantics in the MPFR real-number model. No claim is made that ECMAScript `Math.sin` or `Math.cos` are universally correctly rounded.

This evidence does not authorize production implementation or P2.4-D-8.

## Scope, immutable references, and authorization boundary

Repository: `soheil6913/PCB`

Required evidence branch:

```text
evidence/phase6-1-p2-4-d-7-ieee754-stepwise-20261128
```

Immutable references used:

| Reference | SHA |
|---|---|
| P2.4-D-1 source | `941262899a46e54cbf1a94a4da6dd528b8d36780` |
| P2.4-D-6 evidence | `ae24078e4f34dc13a8e1f1e82ce35c95b95ea6a2` |
| P2.4-D design closure | `54929160cfc0347d690101501886c287dc34a7ed` |
| P2.4-C remediation compatibility target | `327fc0479031279b889ea1dd1140a23d4abe442f` |

The existing source checkout at `/tmp/p24c-numerical-uncertainty/source` was not changed and remained on `327fc0479031279b889ea1dd1140a23d4abe442f`. The capture used a separate clean checkout at `/tmp/p24d7-source` so the required D-1 SHA could be attested without changing the existing source worktree.

Evidence artifact commits:

- Initial harness/artifact commit: `e68cd3664af35d145bb0748c60201aa431ba4988`
- Signed-zero comparison correction and manifest update: `0690d038859ffaa614776a1a9d36282a9727747e`

The final report is committed separately after these evidence commits. The evidence commits contain only evidence harness modules, tests, machine-readable artifacts, and reproduction metadata. No production source, existing project test, CI workflow, `main`, previous evidence branch, merge, or pull request was modified.

## 1. Exact source attestation

### Required attestation behavior

The capture harness requires `PCB_SOURCE_WORKTREE`. It does not accept `PCB_REFERENCE_COMMIT` or another environment variable as proof of identity. The harness executes Git against the supplied path and fails before vectors if any of the following is true:

- the variable is absent;
- the path is not an accessible Git worktree;
- `git -C "$PCB_SOURCE_WORKTREE" rev-parse HEAD` differs from the fixed expected D-1 SHA;
- `git -C "$PCB_SOURCE_WORKTREE" status --porcelain=v1 --untracked-files=all` is non-empty;
- the source file is not tracked by the attested checkout;
- the canonical source file path escapes the checkout or is a symlink;
- the source SHA-256 differs between pre-capture and post-capture checks.

### Actual command and output

The capture was run as:

```sh
PCB_SOURCE_WORKTREE=/tmp/p24d7-source \
PCB_EXPECTED_SOURCE_SHA=941262899a46e54cbf1a94a4da6dd528b8d36780 \
CAPTURE_OUTPUT=/tmp/p24d7-work/javascript-capture.json \
/tmp/p24c-numerical-uncertainty/source/node_modules/.bin/tsx capture.ts
```

The harness output was:

```json
{
  "vectors": 19,
  "source": "941262899a46e54cbf1a94a4da6dd528b8d36780",
  "fileSha256": "545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9",
  "output": "/tmp/p24d7-work/javascript-capture.json"
}
```

The attestation record contains the following values:

```text
canonical source worktree: /tmp/p24d7-source
expected HEAD:             941262899a46e54cbf1a94a4da6dd528b8d36780
observed HEAD:             941262899a46e54cbf1a94a4da6dd528b8d36780
git status --porcelain:    empty
source file:               shared/engineering.ts
source file bytes:         81255
source file SHA-256:       545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9
post-capture SHA-256:      545038007080da77f36e8e3bf3bab6945b6ad8bd949536fca9069cdcbf3164e9
```

The complete machine-readable record is [`source-attestation.json`](evidence/p2-4-d-7/source-attestation.json).

### Deliberate failure tests

The negative suite deliberately supplied:

1. the existing clean checkout at the wrong HEAD (`327fc047…`);
2. a non-Git temporary directory;
3. a clean clone with an untracked file;
4. a clean clone with `shared/engineering.ts` modified.

Actual output:

```text
{'cases': 4, 'passed': 4, 'results': [
  {'id': 'wrong-head', 'passed': True},
  {'id': 'wrong-path', 'passed': True},
  {'id': 'dirty-worktree', 'passed': True},
  {'id': 'modified-source', 'passed': True}
]}
```

No vector capture is performed after an attestation failure.

## 2. Actual pinned source expressions and operation order

The capture read the pinned `shared/engineering.ts` before modeling. The exact relevant source lines are:

- `rotatePoint`: line 57;
- `transformLocalPoint`: line 58;
- `route45`: line 59.

### `rotatePoint` line 57

The actual source is:

```ts
export function rotatePoint(point: Point, degrees: number) {
  const radians = degrees * Math.PI / 180;
  const cos = Math.cos(radians);
  const sin = Math.sin(radians);
  return {
    x: point.x * cos - point.y * sin,
    y: point.x * sin + point.y * cos,
  };
}
```

The degree-to-radian expression is exactly `degrees * Math.PI / 180`. Because multiplication and division are left-associative, the captured order is:

1. `degrees * Math.PI`;
2. `(degrees * Math.PI) / 180`;
3. `Math.cos(radians)`;
4. `Math.sin(radians)`;
5. `point.x * cos`;
6. `point.y * sin`;
7. x subtraction;
8. `point.x * sin`;
9. `point.y * cos`;
10. y addition.

The harness did not replace this with `degrees * (Math.PI / 180)`.

### `transformLocalPoint` line 58

The actual source first calls `rotatePoint(local, rotation)`, then performs:

1. `origin.x + rotated.x`;
2. `origin.y + rotated.y`.

The argument order is `transformLocalPoint(origin, local, rotation)`, not the reverse.

### `route45` line 59

The actual source evaluates endpoint differences, absolute values, the absolute-difference equality check, the diagonal minimum, and the waypoint expression in the exact source sequence. The evidence capture includes those intermediate values and exact bits for every vector.

The complete expression record is [`source-expression-order.json`](evidence/p2-4-d-7/source-expression-order.json).

## 3. Evidence harness architecture

The evidence-only harness consists of:

- `capture.ts`: source attestation, source expression record, actual TypeScript import, exact JavaScript step capture, route capture, and pre/post source hashes;
- `binary64.py`: exact finite binary64-to-rational conversion and round-to-nearest/ties-to-even verifier;
- `binary64_suite.py`: finite operations, special values, unary operations, comparisons, subnormal/normal boundaries, overflow, and midpoint vectors;
- `mpfr_eval.py`: isolated `gmpy2`/MPFR 256-bit directed-rounding evaluator;
- `analyze.py`: Model A/Model B separation, interval containment, unique output-cell classification, and ULP comparison;
- `attestation_negative_tests.py`: deliberate wrong-head, dirty, wrong-path, and modified-file failures;
- `evidence_tests.py`: deterministic evidence regression suite;
- `make_artifacts.py`: machine-readable artifact assembly and hash manifest.

The harness is not imported by production application code. The only source file imported by the capture is the attested `shared/engineering.ts` from `/tmp/p24d7-source`. The TypeScript runtime used `tsx` from the already installed source toolchain; no source package manifest, lockfile, or production dependency was edited.

The evidence-only runtime dependency is recorded as `gmpy2==2.3.2`. It is used only by the MPFR comparison helper and is not added to the project.

## 4. Binary64 operation contract and independent verification

### Contract

The independent verifier models finite binary64 operands as exact dyadic rationals. For addition, subtraction, multiplication, and division it performs exact rational arithmetic, then rounds to binary64 round-to-nearest, ties-to-even. It records the resulting 64-bit pattern, including sign, exponent, and fraction fields.

Special values are represented by exact bit patterns. The suite separately records:

- +0 and -0;
- smallest positive and negative subnormal;
- largest subnormal;
- smallest normal;
- largest finite values;
- positive and negative infinity;
- NaN propagation cases;
- unary negation;
- absolute value;
- ordered, equal, and unordered comparisons.

### Actual suite output

Command:

```sh
python3 binary64_suite.py binary64-results.json
```

Output:

```json
{
  "finite_vectors": 40,
  "finite_matches": 40,
  "special_vectors": 6,
  "unary_vectors": 16,
  "comparison_vectors": 4,
  "midpoint_tests": [
    {"id": "even-positive", "observed_bits": "0x3ff0000000000000", "expected_bits": "0x3ff0000000000000"},
    {"id": "odd-positive", "observed_bits": "0x3ff0000000000002", "expected_bits": "0x3ff0000000000002"},
    {"id": "even-negative", "observed_bits": "0xbff0000000000000", "expected_bits": "0xbff0000000000000"},
    {"id": "odd-negative", "observed_bits": "0xbff0000000000002", "expected_bits": "0xbff0000000000002"}
  ]
}
```

There were no finite exact-rational mismatches. The full vector record is [`binary64-operation-vectors.json`](evidence/p2-4-d-7/binary64-operation-vectors.json).

This validates the independent verifier against native Python binary64 behavior for the selected vectors. It does not by itself prove every hardware or JavaScript engine operation; the JavaScript capture and exact bit records provide the separate runtime evidence.

## 5. Model A and Model B methodology

### Model A — exact-real mathematical expression

Model A begins with the exact binary64 values represented by the JavaScript input bits. It treats the captured radian input as an exact binary64 value, evaluates MPFR sine and cosine at 256-bit precision with directed lower and upper rounding, and propagates outward intervals through:

```text
x*cos - y*sin + origin.x
x*sin + y*cos + origin.y
```

The actual y expression is exactly:

```text
point.x * sin + point.y * cos + origin.y
```

Products and sums are evaluated with outward MPFR rounding. The result is retained as a high-precision binary mantissa/exponent interval, then classified against binary64 output cells. No stepwise JavaScript result is substituted into Model A.

### Model B — actual JavaScript stepwise expression

Model B imports the pinned TypeScript functions and records every source-order intermediate after JavaScript binary64 rounding:

- exact input bit patterns;
- degree-to-radian product and division;
- actual `Math.sin` and `Math.cos` values and bits;
- every multiplication;
- x subtraction;
- y addition;
- origin translation additions;
- final source results and bits;
- actual `route45` output.

The manual capture sequence is checked against the imported source functions for every vector. A mismatch raises `SOURCE_SEQUENCE_MISMATCH` and aborts artifact creation.

The complete Model B record is [`model-b-stepwise-results.json`](evidence/p2-4-d-7/model-b-stepwise-results.json). Model A is [`model-a-results.json`](evidence/p2-4-d-7/model-a-results.json). They are deliberately separate files and are not merged into a single numerical result.

## 6. Trigonometric validation

### Method

For each captured binary64 radian input, MPFR computes directed lower and upper bounds for sine and cosine. The artifact records the exact MPFR binary mantissa/exponent strings, parsed exact fractions, actual JavaScript bits, whether the actual binary64 point lies literally inside the real-value interval, and whether the interval proves a unique binary64 output cell.

A literal real-interval containment test is intentionally distinguished from a correct-rounding test. A correctly rounded binary64 value can lie just outside a narrow interval enclosing the exact real result because the rounded representable value is not itself the exact real value. Therefore, the decisive test for binary64 compatibility is unique output-cell classification, not literal inclusion of the rounded JavaScript value in the real interval.

### Counts

There were 19 vectors.

| Measurement | Count |
|---|---:|
| JavaScript trig pairs with literal real-interval containment | 4 / 19 |
| Sine intervals proving a unique binary64 cell | 18 / 19 |
| Cosine intervals proving a unique binary64 cell | 18 / 19 |
| JavaScript sine matching the unique MPFR-rounded cell | 17 / 19 |
| JavaScript cosine matching the unique MPFR-rounded cell | 18 / 19 |
| Both transform-coordinate intervals containing Model B final x and y | 3 / 19 |

The “literal containment” count is not a claim that 15 vectors have incorrect `Math.sin`/`Math.cos`; it reflects the distinction between a real interval and a rounded binary64 point. The unique-cell counts are the relevant correct-rounding evidence for finite cases.

The one signed-zero sine mismatch remains unresolved in the independent real model: MPFR represents the mathematical sine of zero without preserving JavaScript’s signed-zero convention in the serialized interval, while JavaScript captured `Math.sin(-0)` as `0x8000000000000000`. The harness preserves the JavaScript sign and reports this as unresolved rather than falsely declaring a mismatch or universal agreement.

The full comparison is [`mpfr-trigonometric-comparison.json`](evidence/p2-4-d-7/mpfr-trigonometric-comparison.json).

### No universal ECMAScript claim

This corpus does not establish that JavaScript `Math.sin` or `Math.cos` are universally correctly rounded. It establishes only the observed results for the captured Node/V8 runtime and the listed inputs. The software contract remains runtime-specific unless a separate certified coefficient provider is introduced.

## 7. Adversarial vector corpus and exact counts

The corpus contains 19 stable IDs:

```text
ordinary-0
ordinary-45
ordinary-90
ordinary-180
ordinary-270
ordinary-360
negative-angle
adjacent-45
adjacent-90
adjacent-180
adjacent-270
adjacent-360
large-cancellation
large-opposite
subnormal
signed-zero
huge-angle
max-angle
overflow-translation
```

Coverage includes:

- ordinary coordinates and angles;
- values adjacent to 0°, 45°, 90°, 180°, 270°, and 360°;
- positive and negative angles;
- very large finite angles and `Number.MAX_VALUE` angle;
- tiny and subnormal inputs;
- large-coordinate cancellation;
- signed-zero inputs;
- positive and negative smallest subnormal values;
- largest subnormal and smallest normal through the binary64 suite;
- positive and negative maximum finite coordinates;
- finite inputs whose intermediate products or translations overflow;
- underflow-sensitive products;
- translation that changes output-cell classification;
- vectors where Model A and Model B differ.

Neighboring values are generated from exact binary64 constants and `Number.EPSILON`/`Number.MIN_VALUE` semantics, not decimal tolerance comparisons. Every captured numeric value includes a hexadecimal 64-bit pattern in the JSON artifacts.

## 8. Mismatches and unresolved results

### Observed exact-real versus stepwise differences

The following vectors did not have Model A transformed-coordinate intervals containing the captured Model B final output in at least one coordinate:

```text
ordinary-45
ordinary-90
ordinary-180
ordinary-270
ordinary-360
negative-angle
adjacent-45
adjacent-90
adjacent-180
adjacent-270
adjacent-360
large-cancellation
large-opposite
huge-angle
max-angle
overflow-translation
```

These are not automatically production defects. They demonstrate that exact-real evaluation and stepwise JavaScript evaluation are different numerical models. The differences are particularly important for cancellation and for non-finite intermediate results.

Where a unique Model A output cell was available, nonzero ULP differences were recorded for:

```text
negative-angle:       x = 1 ULP
adjacent-45:          x = 6485328709579050 ULP, y = 1 ULP
large-cancellation:   x = 6485328709579051 ULP
large-opposite:       x = 6048990701490383 ULP, y = 1 ULP
huge-angle:           x = 1 ULP
```

The large ULP values occur because the exact-real result and the stepwise result are far apart in representable ordering under severe cancellation/overflow-sensitive inputs. They do not justify applying an absolute tolerance.

### Explicit unresolved cases

[`unresolved-cases.json`](evidence/p2-4-d-7/unresolved-cases.json) records 16 unresolved cases with machine-readable reasons. The principal reasons are:

- actual JavaScript trig value is not literally inside the narrow exact-real MPFR interval, even where the unique rounded cell agrees;
- Model A final interval does not contain Model B’s stepwise output;
- non-finite huge-angle or translation behavior cannot be classified as an ordinary finite output;
- signed-zero real-model convention is not preserved by the MPFR interval serialization.

No unresolved case is converted to a claim of universal correct rounding.

## 9. Binary64 rounding validation suite

Dedicated coverage includes:

- positive and negative midpoint ties-to-even;
- even and odd significand tie cases;
- +0 and -0;
- smallest subnormal;
- largest subnormal;
- smallest normal;
- subnormal/normal boundary;
- largest finite;
- finite operation overflow;
- exact cancellation;
- multiplication and division underflow-sensitive inputs;
- NaN and infinity propagation;
- adjacent representable values around critical boundaries;
- unary negation and absolute value;
- ordered and unordered comparisons.

The exact-rational verifier matched all 40 finite vectors. Four midpoint cases matched exactly. The special, unary, and comparison vectors are recorded without tolerance.

## 10. Dedicated test commands and actual results

### Source-attestation negative suite

```sh
python3 attestation_negative_tests.py
```

Actual result:

```text
{'cases': 4, 'passed': 4, 'results': [
  {'id': 'wrong-head', 'passed': True},
  {'id': 'wrong-path', 'passed': True},
  {'id': 'dirty-worktree', 'passed': True},
  {'id': 'modified-source', 'passed': True}
]}
```

### Binary64 verifier

```sh
python3 binary64_suite.py binary64-results.json
```

Actual result: 40 finite vectors, 40 exact matches, 6 special vectors, 16 unary vectors, 4 comparison vectors, and 4/4 midpoint matches.

### Evidence regression suite

```sh
python3 -m unittest evidence_tests.py
```

Actual output:

```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.002s

OK
```

### Reproducibility

The capture was run twice with the same attested source and the two JSON outputs were byte-identical. The primary capture SHA-256 was:

```text
c0d70084d62d0372affd33471b8d15a945a4ad165262a5717e6b5ee8e3a2e09d  javascript-capture.json
```

The refreshed machine-readable artifacts have their own hashes in `reproducibility-manifest.json` and are committed under `evidence/p2-4-d-7/`.

## 11. Machine-readable artifacts

The branch contains:

- [`source-attestation.json`](evidence/p2-4-d-7/source-attestation.json)
- [`source-expression-order.json`](evidence/p2-4-d-7/source-expression-order.json)
- [`binary64-operation-vectors.json`](evidence/p2-4-d-7/binary64-operation-vectors.json)
- [`javascript-runtime-capture.json`](evidence/p2-4-d-7/javascript-runtime-capture.json)
- [`model-a-results.json`](evidence/p2-4-d-7/model-a-results.json)
- [`model-b-stepwise-results.json`](evidence/p2-4-d-7/model-b-stepwise-results.json)
- [`mpfr-trigonometric-comparison.json`](evidence/p2-4-d-7/mpfr-trigonometric-comparison.json)
- [`unresolved-cases.json`](evidence/p2-4-d-7/unresolved-cases.json)
- [`reproducibility-manifest.json`](evidence/p2-4-d-7/reproducibility-manifest.json)

Evidence modules and tests are colocated in the same directory. The report and artifacts use exact hexadecimal binary64 patterns for JavaScript floating values; MPFR values use exact binary mantissa/exponent representations plus parsed exact fractions.

## 12. Reproducibility instructions

From the evidence directory, install only the evidence dependency:

```sh
python3 -m pip install --user -r requirements-evidence.txt
```

Use the pinned source checkout and execute:

```sh
export PCB_SOURCE_WORKTREE=/absolute/path/to/clean/checkout
export PCB_EXPECTED_SOURCE_SHA=941262899a46e54cbf1a94a4da6dd528b8d36780
export CAPTURE_OUTPUT=javascript-capture.json
/path/to/tsx capture.ts
python3 binary64_suite.py binary64-results.json
python3 analyze.py javascript-capture.json 'python3 mpfr_eval.py' mpfr-results.json
python3 make_artifacts.py
python3 -m unittest evidence_tests.py
```

The harness must be run with a clean worktree at the exact source SHA. A dirty worktree, wrong HEAD, wrong path, or modified source file is an attestation failure and must stop before vectors.

The recorded environment was Node `v22.23.4`, Python `3.12.3`, gmpy2 `2.3.2`, and the source toolchain’s `tsx` runtime. The complete platform and artifact hash manifest is [`reproducibility-manifest.json`](evidence/p2-4-d-7/reproducibility-manifest.json).

## 13. Compatibility and integrity confirmation

- P2.4-B source behavior was inspected at the exact D-1 source reference supplied for this phase.
- The P2.4-C remediation target `327fc047…` was preserved as a separate compatibility reference and not merged.
- Public signatures and production geometry behavior were not changed.
- Existing project tests were not changed.
- CI workflows were not changed.
- `main` was not changed.
- Previous evidence branches were not changed.
- No pull request was created.
- No checked-transform implementation, route45 remediation, P2.4-C adapter, or production numerical kernel was started.
- The existing source worktree at `/tmp/p24c-numerical-uncertainty/source` remained clean at `327fc0479031279b889ea1dd1140a23d4abe442f`.
- The attested evidence source checkout remained clean at `941262899a46e54cbf1a94a4da6dd528b8d36780`.

## 14. Limitations and final interpretation

This evidence validates the capture and comparison methodology for the tested corpus and runtime. It does not prove:

- universal ECMAScript trigonometric correctness across engines;
- that every JavaScript operation on every supported platform uses the same implementation path;
- a production checked-transform contract;
- a production route45 fallback policy;
- a universal exact-real distance or geometry result;
- that any unresolved case is safe to classify as `VALID`.

The observed Model A/Model B differences are evidence for preserving distinct exact-real and stepwise models in future design. They are not permission to retrofit tolerances or to change production behavior in this phase.

**Final verdict: `IEEE754_STEPWISE_COMPATIBILITY_PARTIALLY_VALIDATED`**

P2.4-D-8 must not begin automatically.
