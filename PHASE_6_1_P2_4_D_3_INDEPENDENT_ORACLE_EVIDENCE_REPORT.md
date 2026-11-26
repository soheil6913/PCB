# PHASE 6.1 — P2.4-D-3 Independent Numerical Oracle and Binary64 Evidence

## Final verdict

**ORACLE_PARTIALLY_VALIDATED**

A reproducible evidence path is available for exact JavaScript reference capture and independent high-precision comparison. The reference TypeScript module was imported directly through the source worktree's existing `tsx` runtime, and Python `mpmath` 1.4.1 was available for independent arbitrary-precision mathematical evaluation. However, this environment has no MPFR/gmpy2 binding, and no validated directed-rounding or correctly-rounded binary64 output-cell certificate was established. Cases whose mathematical interval crosses, or may cross, a binary64 rounding boundary remain unresolved.

No production source, existing test, `main`, merge, pull request, or checked-transform implementation was modified. The temporary runners used for this audit were outside both repositories and were not delivered as repository artifacts.

## 1. Baseline and reference verification

- Repository: `soheil6913/PCB`
- Reference implementation: `941262899a46e54cbf1a94a4da6dd528b8d36780`
- Reference parent: `327fc0479031279b889ea1dd1140a23d4abe442f`
- Reference subject: `fix: unify geometry options iteration validation`
- Inspected source worktree HEAD: `af976d356f84ea90fe74a90cf390a850387d3567`
- Documentation baseline: `origin/main` at `5ef6266cd002fb835824bb9e6f588ab07f99a0ba`
- Prior report: `PHASE_6_1_P2_4_D_2_TRANSFORM_COMPATIBILITY_EVIDENCE_REPORT.md`
- Prior verdict: `EVIDENCE_INSUFFICIENT`

The reference commit exists and is an ancestor of the inspected source checkout. This report is being prepared on the new isolated branch `evidence/phase6-1-p2-4-d-3-independent-oracle-20261126`.

## 2. Available numerical toolchain

The following were observed in the sandbox:

| Tool | Observed version/status | Evidence meaning |
|---|---|---|
| Node.js | `v22.23.4` | Executes the reference TypeScript module through the existing project loader |
| `tsx` | `4.20.6`, present in the source worktree | Directly imports `shared/engineering.ts` without changing it |
| Python | `3.12.3` | Runs the independent numerical script |
| `mpmath` | `1.4.1` | Arbitrary-precision mathematical comparison; not an MPFR proof by itself |
| `mpmath.iv` | present | Candidate interval arithmetic; not accepted here as a validated directed-rounding certificate |
| `gmpy2` / MPFR binding | unavailable | No independently verified MPFR directed-rounding path was available |

### 2.1 What the available oracle does and does not guarantee

The `mpmath` comparison used 160 decimal digits for point evaluation. It evaluates mathematical expressions using its own arbitrary-precision implementation rather than JavaScript `Math.sin`/`Math.cos`, so it is independent in implementation and useful for detecting large discrepancies.

It does **not**, by itself, prove a correctly rounded binary64 result. The ordinary `mpmath` context does not expose a proof that its final decimal approximation encloses the exact real value with directed rounding. `mpmath.iv` is available and produces interval-looking enclosures, but this audit did not validate its endpoint implementation, transcendental reduction, dependency behavior, or CI reproducibility against an MPFR directed-rounding standard. It is therefore recorded as a candidate for future work, not as a mathematical certificate.

No output is labeled “correctly rounded” in this report. An exact JavaScript bit match to a rounded high-precision conversion is evidence of compatibility, not proof of the mathematical rounding cell.

## 3. Exact binary64 capture method

A temporary TypeScript runner imported:

```ts
import { route45, rotatePoint, transformLocalPoint }
  from '/home/ubuntu/PCB-Studio-Pro-p2-4-d-1/shared/engineering.ts';
```

It captured each output with `DataView.getBigUint64` after `setFloat64`, together with `Object.is(value, -0)`. This records the exact in-memory binary64 bit pattern, including signed zero, subnormal, infinity, and NaN classification. JSON display of `NaN` as `null` was not used as the evidence representation; the hexadecimal bit pattern is authoritative.

The runner executes the source sequence exactly as written:

```ts
const radians = degrees * Math.PI / 180;
const cos = Math.cos(radians);
const sin = Math.sin(radians);
```

It therefore distinguishes JavaScript evaluation from the mathematical expression `degrees × π / 180`. This distinction matters for both degree-to-radian rounding and subsequent native-library trigonometric results.

## 4. Observed exact reference outputs

These are actual observations from the reference TypeScript module, not invented expected values. Hexadecimal values are IEEE-754 binary64 encodings.

### 4.1 `rotatePoint`

| Vector | Input | Exact output observations |
|---|---|---|
| `r0` | `(3,4)`, `0°` | `x=3`, bits `0x4008000000000000`; `y=4`, bits `0x4010000000000000` |
| `r45` | `(3,4)`, `45°` | `x=-0.707106781186547`, bits `0xbfe6a09e667f3bc8`; `y=4.949747468305833`, bits `0x4013cc8a99af5453` |
| `r90` | `(3,4)`, `90°` | `x=-4`, bits `0xc010000000000000`; `y=3.0000000000000004`, bits `0x4008000000000001` |
| `r180` | `(3,4)`, `180°` | `x=-3.0000000000000004`, bits `0xc008000000000001`; `y=-3.9999999999999996`, bits `0xc00fffffffffffff` |
| `rneg` | `(-7,2.3)`, `-31°` | `x=-4.815583532621662`, bits `0xc0134328545f1093`; `y=5.576751315985237`, bits `0x40164e97e5a05383` |
| `rout` | `(3,4)`, `1097.25°` | `x=1.67889353346928`, bits `0x3ffadcbf773b7689`; `y=4.709704502755458`, bits `0x4012d6bcc6f4a271` |
| `rsub` | `(Number.MIN_VALUE,-Number.MIN_VALUE)`, `90°` | both outputs `5e-324`, bits `0x0000000000000001` |
| `rnan` | `(NaN,1)`, `0°` | both outputs are quiet NaN, bits `0x7ff8000000000000` in this runtime |

The quarter-turn and half-turn results demonstrate compatibility with the current native sequence, not exact mathematical quarter-turn identities. For example, the observed `90°` y output is `3.0000000000000004`, while the mathematical value is exactly `3`.

### 4.2 `route45` threshold observations

The source declares `EPSILON = 1e-7` and tests strict `< EPSILON` comparisons. Exact reference observations with start `(0,0)` and end `(delta,2)` were:

| Vector | `delta` | Exact delta bits | Returned point count | Observation |
|---|---:|---|---:|---|
| below | `9.999999999999997e-8` | `0x3e7ad7f29abcaf46` | 2 | axis-near fast path; returns `[start,end]` |
| at | `1e-7` | `0x3e7ad7f29abcaf48` | 3 | strict comparison is false; inserts `(1e-7,0)` |
| above | `1.0000000000000002e-7` | `0x3e7ad7f29abcaf4a` | 3 | inserts the horizontal-first intermediate point |
| smallest subnormal | `5e-324` | `0x0000000000000001` | 2 | subtraction/threshold path classifies the delta as below epsilon |

This establishes an important legacy compatibility fact: the exact threshold is not inclusive. Any replacement must preserve the observed `< 1e-7` behavior unless a deliberate compatibility change is approved.

### 4.3 `transformLocalPoint`

| Vector | Input | Exact output observations |
|---|---|---|
| cancellation | origin `(1,1)`, local `(-1,-1)`, `0°` | `(0,0)`, both bits `0x0000000000000000` |
| translation overflow | origin `(MAX,MAX)`, local `(MAX,-MAX)`, `0°` | `x=+Infinity`, bits `0x7ff0000000000000`; `y=+0`, bits `0x0000000000000000` |
| small displacement loss | origin `(MAX,0)`, local `(MIN_VALUE,0)`, `0°` | `x=MAX`, bits `0x7fefffffffffffff`; `y=+0` |

These are composition observations. They cannot be inferred only from the `rotatePoint` outputs because final translation addition can overflow, cancel, or erase a small displacement.

## 5. Independent high-precision comparison

The independent Python calculation used `mpmath.mp.dps = 160`, decimal inputs corresponding to the test vectors, and mathematical `mp.pi` rather than JavaScript `Math.PI` followed by binary64 operations. Representative mathematical values were:

| Vector | High-precision mathematical x | High-precision mathematical y | Reference binary64 result |
|---|---:|---:|---|
| `(3,4),45°` | `-0.707106781186547524400844362104849...` | `4.949747468305832670805910534733943...` | `(-0.707106781186547, 4.949747468305833)` |
| `(3,4),90°` | `-4.0` | `3.0` | `(-4, 3.0000000000000004)` |
| `(3,4),180°` | `-3.0` | `-4.0` | `(-3.0000000000000004, -3.9999999999999996)` |
| `(-7,2.3),-31°` | `-4.815583532621661420557...` | `5.576751315985237579477...` | `(-4.815583532621662, 5.576751315985237)` |
| `(3,4),1097.25°` | `1.678893533469276068402...` | `4.709704502755459370149...` | `(1.67889353346928, 4.709704502755458)` |

The differences are expected consequences of the specified JavaScript sequence and native binary64 trig, and demonstrate why mathematical reference values cannot be substituted directly for compatibility outputs.

The high-precision comparison is **independent approximate evidence**. It is not an outward-rounded enclosure and does not prove that the JavaScript output occupies the unique correct binary64 cell.

## 6. Degree-to-radian overflow transition

A temporary Node probe searched adjacent binary64 degree values using the exact expression `degrees * Math.PI / 180`. In this runtime, the largest tested finite degree whose intermediate product remained finite was approximately:

```text
5.722234971514056e+307
```

with a finite radian result approximately `9.98718408256842e+305`. The adjacent degree value:

```text
5.722234971514057e+307
```

produced an infinite intermediate radian value. Once the radian value is infinite, native `Math.sin` and `Math.cos` return NaN and the rotation outputs become NaN.

This is an observed runtime boundary, not a portable specification. A future compatibility runner must discover and record it on the target JavaScript engine rather than hard-code it as an implementation bound.

## 7. Compatibility corpus status

The following corpus was executed directly against the reference module:

| Required family | Status | Evidence |
|---|---|---|
| `0°`, `45°`, `90°`, `180°`, `270°`, `360°` | Partially executed | Exact bit captures for 0/45/90/180; copied-formula probe also covered 270/360, but direct-module corpus should be extended before certification |
| Negative and out-of-range angles | Executed for `-31°`, `1097.25°` | Exact direct-module bit captures recorded |
| Adjacent representable angles around 0/90/180 | Not complete | Vector generator is specified but adjacent-angle sweep was not executed in this phase |
| Degree-to-radian overflow transition | Executed as runtime probe | Adjacent finite degree observations recorded; portability remains unresolved |
| Positive/negative zero | Partially executed | Exact capture machinery exists; complete sign matrix not yet run |
| Smallest subnormal and normal/subnormal transition | Partially executed | Smallest-subnormal rotation captured; transition matrix remains open |
| Maximum finite coordinates | Partially executed | Translation overflow and loss cases captured; full rotation matrix remains open |
| Cancellation-sensitive combinations | Executed for exact zero translation cancellation | Broader trig cancellation sweep remains open |
| Non-finite coordinates/angles | Partially executed | NaN coordinate captured; complete infinity and NaN payload matrix remains open |
| Translation overflow/loss of small displacement | Executed | Exact direct-module observations recorded |
| `route45` below/at/above `EPSILON` | Executed | Exact point counts and bits recorded |
| `route45` cancellation and non-finite inputs | Not complete | Source behavior is known; direct observed corpus remains to be run |

Therefore the minimum requested corpus is not complete. The results support partial validation, not a complete compatibility certificate.

## 8. Binary64 output-cell assessment

A valid output-cell result would require an independently generated interval `[L,U]` for the mathematical output and proof that `[L,U]` lies inside the rounding cell associated with one binary64 value. For a normal finite candidate `f`, that means comparing the interval with the exact midpoints between `f` and its adjacent representable values, with correct handling for subnormals, signed zero, overflow, and NaN/Infinity.

That proof was not completed here because:

1. `mpmath` high-precision point mode is not a directed-rounding proof.
2. `mpmath.iv` is available but was not validated here as an MPFR-equivalent rigorous enclosure for all required transcendental and extreme-value cases.
3. No MPFR command-line tool or Python MPFR binding is installed.
4. The JavaScript engine's native `Math.sin`/`Math.cos` implementation is not itself accompanied by a source-level correctly-rounded guarantee in this audit.
5. Intervals that cross a binary64 midpoint must remain unresolved even if their decimal center is close to the observed output.

The exact bit capture is complete for the executed vectors. Output-cell certification is therefore **unavailable**, not failed by a counterexample.

## 9. Future checked-transform compatibility

A checked-transform implementation could preserve current behavior only if it explicitly separates two contracts:

- **Legacy compatibility:** for supported finite inputs, reproduce the current JavaScript evaluation sequence or publish an approved change in exact output-cell behavior.
- **Checked behavior:** for unsupported, non-finite, overflowed, or unresolved cases, return an explicit indeterminate result and ensure every consumer fails closed without silently changing pad placement, pin connectivity, route geometry, or persistence semantics.

The current public helpers return plain `Point` values and do not expose an indeterminate state. `route45` returns a point array and has strict `< EPSILON` behavior at the threshold. A checked transform cannot be substituted without an API and consumer migration design. This phase does not authorize that migration.

## 10. Remaining blockers

1. Install or otherwise provide an MPFR-backed independent oracle with documented precision and directed rounding, or formally validate an equivalent interval implementation.
2. Implement the binary64 rounding-cell classifier for normal values, subnormals, signed zero, overflow, infinity, and NaN handling.
3. Execute the complete adjacent-angle, signed-zero, subnormal-transition, maximum-coordinate, cancellation, and non-finite corpus directly against the reference module.
4. Run the complete `route45` cancellation/non-finite corpus and record exact returned point arrays and bit patterns.
5. Establish CI reproducibility for the reference runner, high-precision oracle, and output-cell classifier without modifying production or existing tests.
6. Decide how a future checked API preserves legacy `route45` threshold behavior and transforms while guaranteeing fail-closed DRC behavior.

## 11. Conclusion

The phase established three concrete facts:

- Exact binary64 capture from the reference TypeScript helpers is reproducible with the existing Node/`tsx` toolchain.
- `mpmath` provides a genuinely independent high-precision mathematical comparison and exposes material differences between mathematical values and the current JavaScript outputs.
- A rigorous output-cell certificate and complete compatibility corpus are not yet available with the installed toolchain and executed evidence.

**ORACLE_PARTIALLY_VALIDATED**
