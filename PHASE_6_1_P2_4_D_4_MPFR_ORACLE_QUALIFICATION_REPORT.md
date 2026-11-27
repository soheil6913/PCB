# PHASE 6.1 — P2.4-D-4 MPFR Oracle Qualification and Exact Binary64 Input Validation

## Final verdict

**MPFR_ORACLE_PARTIALLY_QUALIFIED**

A genuine MPFR-backed directed-rounding path was established in an isolated temporary Python virtual environment using `gmpy2` 2.3.2, bundled with MPFR 4.2.2 and GMP 6.3.0. The qualification harness demonstrated distinct downward and upward rounding, exact import of representative binary64 values from hexadecimal bit patterns through exact rationals, directed π bounds, outward endpoint evaluation for a representative trigonometric interval, and exact-rational output-cell boundary behavior.

The result is partial rather than complete. The harness was not added to CI or the repository, the installed wheel path is not yet pinned/reproducibly provisioned for all target CI architectures, and the complete extreme/non-finite transform corpus and full overflow-cell classifier remain unfinished. No JavaScript `Math.sin`/`Math.cos` correct-rounding claim is made.

No production source, existing test, `main`, merge, pull request, checked transform, or production dependency was modified. All temporary dependencies and runners were kept outside the production worktree.

## 1. Baseline and reference verification

- Repository: `soheil6913/PCB`
- Reference implementation: `941262899a46e54cbf1a94a4da6dd528b8d36780`
- Reference parent: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Inspected source HEAD: `af976d356f84ea90fe74a90cf390a850387d3567`
- Previous evidence commit: `f20de1baa8a138a8cb0e6326db22541fcf8fb635`
- Documentation baseline: `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`
- New branch: `evidence/phase6-1-p2-4-d-4-mpfr-oracle-qualification-20261127`

The requested reference commit exists, has the expected subject, and is an ancestor of the inspected source checkout. The previous P2.4-D-3 report is present at the stated commit.

## 2. MPFR/GMP availability and qualification

### 2.1 Discovered installations

The base system contains runtime libraries:

- `libmpfr6`: `4.2.1-1build1.1`; runtime string `4.2.1`.
- `libgmp10`: `2:6.3.0+dfsg-2ubuntu6.1`.
- Development headers and `gmpy2` were not present in the base Python environment.

An isolated virtual environment was created at `/tmp/p24d4-venv`, outside both repositories. `pip install gmpy2` succeeded and installed:

- `gmpy2`: `2.3.2`.
- `gmpy2.mpfr_version()`: `MPFR 4.2.2`.
- `gmpy2.mp_version()`: `GMP 6.3.0`.

The qualification results below use this isolated binding, not the project dependency graph.

### 2.2 Precision and rounding configuration

The harness set MPFR precision to **256 bits** for qualification operations. This is sufficient to import every finite binary64 value exactly because every finite binary64 significand has at most 53 significant bits; the exponent range is separately widened in the temporary context to avoid accidental context-range failures during proof exercises.

The available gmpy2 context exposed:

- `RoundDown` — MPFR RNDD toward negative infinity.
- `RoundUp` — MPFR RNDU toward positive infinity.
- `RoundToNearest` and other modes.
- Explicit precision, exponent range, and exception flags.

### 2.3 Directed-rounding witness

At precision 53, the exact value `1 + 2^-53` was evaluated once with each directed mode:

```text
RoundDown: 1.0
RoundUp:   1.0000000000000002
```

This is a direct behavioral witness that the harness is not silently using round-to-nearest for both modes. It does not, by itself, qualify every future operation; every operation in a production harness must still be executed under the intended local context.

### 2.4 Directed π bounds

At precision 256:

```text
pi_lo = 3.141592653589793238462643383279502884197169399375105820974944592307816406286198
pi_hi = 3.141592653589793238462643383279502884197169399375105820974944592307816406286233
```

The lower bound was produced under `RoundDown` and the upper bound under `RoundUp`. The endpoints are distinct and ordered. The harness therefore has a usable directed-constant path for π.

This evidence qualifies the MPFR/gmpy2 operation used by the harness; it does not qualify JavaScript's `Math.PI` constant or native trigonometric implementation.

## 3. Exact binary64 input import

### 3.1 Canonical representation

The harness treats a 64-bit hexadecimal word as canonical input. It decodes:

```text
sign = bit 63
exponent = bits 62..52
fraction = bits 51..0
```

For a normal finite value it reconstructs the exact rational:

```text
(-1)^sign × (2^52 + fraction) / 2^52 × 2^(exponent - 1023)
```

For a subnormal finite value it reconstructs:

```text
(-1)^sign × fraction / 2^1074
```

The exact rational is passed to GMP/MPFR as an integer numerator and denominator. No decimal string is used for import. Positive and negative zero are retained as separate bit-pattern cases because zero has no non-zero rational magnitude.

### 3.2 Exact-import observations

At 256-bit MPFR precision, the harness imported the following finite values with identical RNDD and RNDU results, establishing exact import for those cases:

| Case | Binary64 bits | Exact import result |
|---|---|---|
| `+0` | `0x0000000000000000` | signed-zero case retained separately |
| `-0` | `0x8000000000000000` | signed-zero case retained separately |
| smallest positive subnormal | `0x0000000000000001` | exact; `4.940656458412465441765687928682213723650598...e-324` |
| smallest negative subnormal | `0x8000000000000001` | exact negative counterpart |
| largest subnormal | `0x000fffffffffffff` | exact; approximately `2.225073858507200889024586876...e-308` |
| smallest normal | `0x0010000000000000` | exact; approximately `2.225073858507201383090232717...e-308` |
| `+1` | `0x3ff0000000000000` | exact `1` |
| maximum finite positive | `0x7fefffffffffffff` | exact; approximately `1.797693134862315708145274237...e+308` |
| maximum finite negative | `0xffefffffffffffff` | exact negative counterpart |

The equality check was performed between the MPFR values produced under RNDD and RNDU. A decimal rendering was used only for display after exact import; it was not an input conversion path.

### 3.3 Input-import status

**Qualified for the tested finite classes at 256 bits.** The exact rational reconstruction is suitable for arbitrary finite binary64 inputs, subject to implementation review of the eventual runner. NaN and infinity are not imported as real MPFR values; they must remain explicit classification cases and must not be silently converted to a nearby finite number.

## 4. Separate mathematical and JavaScript operation models

The harness keeps the two models separate.

### Mode A — mathematical rotation

Inputs are exact real values represented by the supplied binary64 words. The expression is:

```text
theta = exact(degrees) × exact(π) / 180
x = exact(x) × cos(theta) - exact(y) × sin(theta)
y = exact(x) × sin(theta) + exact(y) × cos(theta)
```

π, trigonometric values, products, and sums are evaluated through MPFR contexts and directed endpoint operations. For the representative 45° interval, monotonicity around π/4 was used to map the θ interval to sine/cosine endpoint intervals; a general implementation must use range-aware interval logic rather than assume monotonicity globally.

### Mode B — JavaScript sequence analysis

The reference JavaScript operation is captured separately:

```text
radians = degrees * Math.PI / 180
cos = Math.cos(radians)
sin = Math.sin(radians)
```

The actual `radians` binary64 bits must be captured from JavaScript. That exact binary64 radian value is then imported into MPFR from its bits and used as the input to independently enclosed mathematical sine/cosine evaluation. The comparison is:

```text
observed JavaScript Math.sin/cos output bits
versus
MPFR interval for mathematical sin/cos of the exact observed radian value
```

This separates:

1. Exact binary64 input import.
2. JavaScript degree-to-radian rounding.
3. Native JavaScript transcendental approximation.
4. MPFR mathematical transcendental enclosure.
5. Coordinate multiplication rounding.
6. Final addition/subtraction rounding.

No assumption is made that the JavaScript native trigonometric output is correctly rounded.

### `transformLocalPoint`

The final origin addition is evaluated independently after the enclosed rotation result. It is not inferred solely from the rotation interval. This is required to detect cancellation, overflow, signed-zero behavior, and loss of a small displacement at a large origin.

## 5. Representative directed interval evidence

For exact mathematical `45°`, exact coordinates `(3,4)`, and 256-bit directed operations, the harness produced the following MPFR endpoint observations:

```text
theta_lo = 0.7853981633974483096156608458198757210492923498437764552437361480769541015715322
theta_hi = 0.7853981633974483096156608458198757210492923498437764552437361480769541015715668

sin_lo = 0.7071067811865475244008443621048490392848359376884740365883398689953662392310337
sin_hi = 0.7071067811865475244008443621048490392848359376884740365883398689953662392310683

cos_lo = 0.7071067811865475244008443621048490392848359376884740365883398689953662392310424
cos_hi = 0.7071067811865475244008443621048490392848359376884740365883398689953662392310683

x_lo = -0.7071067811865475244008443621048490392848359376884740365883398689953662392310769
x_hi = -0.7071067811865475244008443621048490392848359376884740365883398689953662392310078

y_lo = 4.949747468305832670805910534733943274993851563819318256118379082967563674617262
y_hi = 4.949747468305832670805910534733943274993851563819318256118379082967563674617538
```

These are outward endpoint calculations for the stated representative path. They are not a complete proof for arbitrary angles because general trigonometric range reduction, interval dependency, and endpoint monotonicity still require a fully implemented interval engine.

The corresponding observed JavaScript output from the reference module was:

```text
x = -0.707106781186547       bits 0xbfe6a09e667f3bc8
y =  4.949747468305833       bits 0x4013cc8a99af5453
```

The mathematical interval is consistent with the observed values, but this single comparison does not prove that the JavaScript `Math.sin` and `Math.cos` calls are correctly rounded.

## 6. Output-cell classifier qualification

### 6.1 Classifier rule

The temporary classifier represents binary64 values and interval endpoints as exact Python rationals. For a finite candidate `f`, it computes the exact midpoints between `f` and its adjacent representable values. An interval is:

- `UNIQUE` only when it lies strictly inside the candidate's rounding cell.
- `UNRESOLVED` when it touches or crosses a midpoint.

This intentionally does not infer a proof from decimal equality. A production version must add explicit handling for signed zero, the subnormal/normal boundary, and the finite/overflow boundary.

### 6.2 Exact rational validation results

For candidate `1.0`, exact rational tests produced:

| Test value/interval | Classifier result |
|---|---|
| exactly representable `1.0` | `UNIQUE` |
| just below the upper midpoint | `UNIQUE` |
| exactly at the lower midpoint | `UNRESOLVED` |
| exactly at the upper midpoint | `UNRESOLVED` |
| just above the upper midpoint | `UNRESOLVED` for candidate `1.0` |

The same exact-value test returned `UNIQUE` for the smallest normal candidate (`0x0010000000000000`). The classifier therefore demonstrates the required conservative behavior for exact values and midpoint contacts in the tested normal/subnormal-adjacent case.

A separate maximum-finite test exposed the expected implementation gap: `nextafter(MAX_FINITE, +Infinity)` is infinity and cannot be passed through ordinary finite-rational conversion. The overflow cell must be represented explicitly rather than by calling `Fraction.from_float(infinity)`. This case remains unresolved in the temporary classifier.

### 6.3 Classifier status

**Partially qualified.** The exact-rational midpoint logic is validated for ordinary finite and smallest-normal cases, and unresolved behavior is conservative. The overflow boundary, signed-zero cell, and complete subnormal lattice require additional explicit cases before the classifier can be called complete.

## 7. Revisit of prior P2.4-D-3 evidence

The previous report correctly distinguished mathematical values from JavaScript outputs, but its `mpmath` calculations used decimal test literals such as `2.3` and did not constitute an exact binary64 import proof. This phase corrects that gap for the tested import classes by using hexadecimal words and exact rational reconstruction.

The observed JavaScript outputs themselves remain unchanged. For example, the direct reference output for `(3,4), 90°` remains:

```text
x = -4                  bits 0xc010000000000000
y = 3.0000000000000004  bits 0x4008000000000001
```

The mathematical exact result is `(-4,3)`. The difference is retained as an observed compatibility fact, not “corrected” by the oracle.

For future vectors such as `(-7,2.3), -31°`, the input must be represented by the exact bit pattern captured from JavaScript (`2.3` as binary64), then reconstructed as an exact rational before MPFR evaluation. The runner must report both that bit pattern and the exact rational; it must not substitute an arbitrary decimal real named `2.3`.

## 8. Reproducibility and CI assessment

### Established

- The isolated environment can install `gmpy2` with `pip`.
- The installed binding exposes MPFR rounding modes and version information.
- The qualification harness is independent of project dependencies and does not modify the source worktree.
- Exact binary64 input reconstruction uses only the standard Python library plus gmpy2.

### Not yet established

- A pinned package hash and architecture matrix for the gmpy2 wheel.
- A clean CI image with known MPFR/GMP versions and a documented offline/reproducible installation path.
- A committed test-only runner and golden output artifact.
- A general interval trig implementation covering arbitrary angles, large arguments, and all quadrants with proven range handling.
- Complete output-cell handling for signed zero, all subnormals, midpoint ties-to-even, and overflow to infinity.

The runner is therefore suitable for an isolated engineering experiment, but not yet suitable as a project CI gate. Adding CI configuration or production dependencies was outside this phase's authorization.

## 9. Qualification matrix

| Requirement | Result | Status |
|---|---|---|
| MPFR-backed runtime available | gmpy2 2.3.2 with MPFR 4.2.2 | PASS |
| GMP version recorded | GMP 6.3.0 | PASS |
| RNDD/RNDU demonstrated | `1 + 2^-53` differs under down/up | PASS |
| Directed π enclosure | distinct ordered 256-bit bounds | PASS |
| Exact binary64 import | tested finite normal, subnormal, max, signed-zero classes | PASS for tested classes |
| No decimal import substitution | exact bit decode to rational to MPFR | PASS |
| Outward trig endpoint evidence | representative 45° interval | PARTIAL |
| Mathematical rotation mode | implemented in temporary harness for representative case | PARTIAL |
| JavaScript sequence separation | reference bits captured; exact-radian import path defined | PARTIAL |
| Final translation composition | direct MPFR composition path designed; full interval corpus incomplete | PARTIAL |
| Output-cell classifier | exact rational midpoint cases | PARTIAL |
| Overflow cell | explicit special case still required | BLOCKED |
| Complete arbitrary-angle range reduction | not established | BLOCKED |
| Clean CI reproducibility | not packaged/pinned | BLOCKED |

## 10. Remaining blockers and next evidence

1. Provide a pinned, architecture-compatible gmpy2/MPFR installation or a separately packaged MPFR runner for CI.
2. Add a test-only, repository-approved runner only after its dependency and artifact policy is accepted; this phase intentionally added no supporting file.
3. Implement general MPFR interval trigonometry with quadrant/range-reduction logic and prove that every endpoint is outward rounded.
4. Complete the JavaScript-sequence mode for every required vector, including exact captured radian bits and independent MPFR sine/cosine intervals.
5. Finish the binary64 cell classifier for signed zero, every subnormal boundary, ties-to-even, and finite-to-infinity overflow.
6. Execute the complete transform corpus and classify each result as unique-cell or `UNRESOLVED`.
7. Do not infer any native JavaScript `Math.sin`/`Math.cos` correct-rounding property until the independent intervals uniquely contain the observed output cell for the relevant vector set and the remaining engine assumptions are documented.

## 11. Restrictions observed

- No production source changes.
- No existing test changes.
- No changes to `main`.
- No branch merge or pull request.
- No checked-transform implementation.
- No coordinate, angle, or geometry bound introduced.
- Temporary virtual environment and runners kept outside the production worktree.
- Exactly one documentation report is intended for publication in this phase; no supporting artifact is added.

## Conclusion

The previous `mpmath`-only gap is materially reduced. A real MPFR-backed directed-rounding environment is available and has been behaviorally qualified for the core operations used by the evidence harness. Exact binary64 import from hexadecimal bits is demonstrated for representative zeros, subnormals, normals, and maximum finite values. A representative outward trigonometric interval and conservative rational output-cell classifier also execute.

The remaining gaps are substantial enough to prevent a full `MPFR_ORACLE_QUALIFIED` verdict: CI reproducibility is not pinned, arbitrary-angle interval range reduction is incomplete, and special output cells at overflow/signed-zero/subnormal boundaries are not fully qualified.

**MPFR_ORACLE_PARTIALLY_QUALIFIED**
