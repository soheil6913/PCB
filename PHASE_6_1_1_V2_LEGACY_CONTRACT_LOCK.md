# Phase 6.1.1 — Schema-v2 Via Clearance Legacy Contract Lock

## Purpose and scope

This is a test-first compatibility checkpoint on `soheil6913/-PCB-Studio-Pro`, starting from required baseline `ff63f3e3e53ce797990ab3e4124ba3bf8637ecd1`. It freezes observed schema-v2 Via clearance behavior before any Schema-v3 work. Production DRC, schema/types, UI, storage, database, export, dependencies, and lockfiles were not changed. No Schema-v3 implementation or design-freeze approval is included.

The fixture/test commit is `8df3d5401ded0eb0ea949e683c4af94cdbdbdfc8`, on branch `verification/phase6-1-p1-v2-legacy-contract-20261121`.

## Locked v2 behavior

- When `minimumViaClearance` is configured, `validatePcb` examines every unordered pair of Vias using nested array-index loops (`i` ascending, then `j > i`), projected 2D center distance, and no layer-span-intersection gate.
- Each effective Via diameter is `via.diameter ?? via.drill * 2`; the required center distance is `(effectiveDiameterA / 2) + (effectiveDiameterB / 2) + minimumViaClearance`. An absent rule disables the pair check.
- The pair clearance violation RuleId remains `PCB_VIA_TO_VIA_CLEARANCE`; the existing numeric-uncertainty RuleId remains `PCB_GEOMETRY_INDETERMINATE`. A finding identity is `${ruleId}:${objectIds.join(",")}`. The object ID order follows the input Via order, and pair findings retain nested-loop order; reversing the array therefore reverses pair object order and identity.
- With absent `layers`, the current implementation may also emit one `PCB_VIA_LAYER_SPAN_UNAVAILABLE` Info finding per Via. That does not suppress the Via-pair clearance finding. The v2 schema accepts only the two distinct copper-layer tuple (`F.Cu`/`B.Cu`), so hypothetical disjoint future spans are represented solely as fixture annotation and are not added to a v2 project.
- `compareClearance` treats `actual >= required` as clear. A shortfall no larger than `Number.EPSILON * max(abs(actual), abs(required), Number.MIN_VALUE) * 16` is indeterminate; a larger shortfall is a violation. The exact boundary passes. The one-representable-step-inside case is within the existing uncertainty band and emits `PCB_GEOMETRY_INDETERMINATE` with Error severity. This historical floating-point classification is recorded, not changed.

## Golden coverage and independent oracle

`shared/engineering.v2-compatibility.fixtures.ts` contains deterministic expected finding snapshots (ID, RuleId, severity, and object IDs) for: missing layers; valid v2 layer metadata; a test-only hypothetical pair of disjoint future spans; both diameters absent; both explicit; mixed explicit/fallback; exact boundary; definite violation; definite pass; reversed array order; three Vias with multiple violating pairs; and the floating-point uncertainty boundary. It also contains migration goldens for schema-v1 with absent optional arrays, explicit schema-v2 input, and missing `schemaVersion` legacy input.

`shared/engineering.v2-compatibility.test.ts` checks exact snapshots and finding counts. Its separate test-side oracle enumerates each Via pair independently, computes `Math.hypot` from coordinates, applies the documented diameter fallback and clearance formula, and compares the resulting violation state with the production finding outside the explicit uncertainty-band case. Pair ordering is tested independently from the formula assertion.

Invalid-input compatibility is covered as well. Non-finite coordinates and an invalid v2 layer tuple fail `validateProjectJsonDetailed`; `validatePcb` returns `PCB_INVALID_INPUT`, while `runDesignRules` returns `PROJECT_INVALID`. The existing `diameter === drill` validation exception is preserved: detailed validation reports `vias[0].diameter` / `must be greater than drill`, `validatePcb` emits `PCB_INVALID_VIA_GEOMETRY` for that Via, and `runDesignRules` blocks on `PROJECT_INVALID`.

Migration assertions record that v1 input migrates to schema v2 and fills absent optional arrays; explicit v2 data is retained; and absent `schemaVersion` follows the legacy-v1 path, including the existing default grid value of 20.

## Verification

All commands below exited with code 0:

| Command | Result |
|---|---|
| `pnpm exec vitest run shared/engineering.v2-compatibility.test.ts` | 1 file passed; 20 tests passed. |
| `pnpm test` | 12 test files passed; 139 tests passed. |
| `pnpm check` | Passed (`tsc --noEmit`). |
| `pnpm build` | Passed (Vite client build and esbuild server bundle). |

The build emitted the existing non-fatal warning that `/api/platform/config.js` in `index.html` cannot be bundled without a `type="module"` attribute. The build still exited successfully. The full test run also printed the platform test's expected missing-`MANUS_OAUTH_API_URL` diagnostic; all tests passed.

The GitHub Actions **Engineering verification** workflow succeeded on the fixture/test commit (`8df3d5401ded0eb0ea949e683c4af94cdbdbdfc8`) for both events:

- Pull-request run: [44901614113](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/44901614113) — success; TypeScript check, automated tests, and production build passed.
- Push run: [44901591237](https://github.com/soheil6913/-PCB-Studio-Pro/actions/runs/44901591237) — success.

Both workflows included a non-failing Node.js 20 deprecation annotation for GitHub Actions. The report-only follow-up commit will cause PR checks to run again; its result is reported separately with the final PR evidence.

## Review boundary

PR #2 is opened against `main` and intentionally remains unmerged. The branch is isolated from `main`; no production behavior was changed. This checkpoint only records and tests legacy v2 behavior and does not authorize Schema-v3 work, migration changes, Design Freeze, or release.
