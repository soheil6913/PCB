# PCB Studio Pro — Phase 6.1 P2

## Independent engineering audit, scope definition, and implementation design

**Audit stage only. No application source code or tests were modified, no commit was created, and nothing was pushed.**

## 1. Verified repository state

The required GitHub state was independently verified before the audit:

| Item | Verified value |
|---|---|
| Repository | `soheil6913/-PCB-Studio-Pro` |
| `main` baseline | `a98384bbfc3296947b90f5254a03a77b11fdc8a9` |
| P1 branch | `fix/phase6-1-p1-explicit-v2-dispatch-20261122` |
| P1 HEAD before P2 isolation | `f2db0afbdcdea6909e7ee91a8f340862741c6db0` |
| Pull Request | [#3](https://github.com/soheil6913/-PCB-Studio-Pro/pull/3) |
| PR state | Open / Draft |
| Local P2 branch | `audit/phase6-1-p2-independent-20261123` |
| Local P2 branch base | `f2db0afbdcdea6909e7ee91a8f340862741c6db0` |

The local P2 branch was created from the verified P1 HEAD. It has not been pushed. `main` and the P1 branch were not modified.

The existing test suite was executed without source changes: **12 test files passed and 165 tests passed**.

## 2. P2 scope

Phase 6.1 P2 should address only source-grounded integrity and failure-boundary risks around project persistence and DRC input handling:

1. Reject malformed explicit values during legacy migration instead of silently normalizing them.
2. Enforce shape-specific geometry invariants that the numerical evaluator relies on.
3. Make directly callable validation helpers fail closed rather than throwing on malformed runtime input.
4. Add regression tests for serialization/migration boundaries, direct-helper safety, and preserved P1 dispatch behavior.
5. Document the absence of an application-level JSON import/export API as an acceptance gap unless such an API is intentionally out of scope.

## Explicit non-scope

P2 should not redesign the UI, change Persian RTL or English LTR behavior, alter the P1 schema dispatch contract, change the V2 geometry evaluator without a confirmed defect, add manufacturing/export claims, implement IPC/KiCad/Gerber support, or start electrical, thermal, impedance, or 3D simulation. It must not merge PR #3, modify `main`, rewrite P1 commits, create a release/tag, or push to the P1 branch.

## 3. Confirmed findings

### P2-001 — Legacy migration silently accepts explicit `null` required arrays

**Severity:** P2

**Source:** `shared/engineering.ts:418`, `migrateProjectJson`

The migration code uses nullish fallback for required collection fields:

```ts
components: source.components ?? [],
wires: source.wires ?? [],
tracks: source.tracks ?? [],
vias: source.vias ?? [],
```

This correctly supplies defaults for absent legacy optional arrays, but it also converts explicit corruption such as `components: null` or `wires: null` into an apparently valid empty project. That loses evidence of input corruption and can silently discard design data.

**Reproduction:**

```ts
migrateProjectJson({ components: null })
// returns a schema-v2 project with components: []

migrateProjectJson({ components: [], wires: null })
// returns a schema-v2 project with wires: []
```

The current implementation rejects a non-array string such as `components: "not-an-array"`, but does not reject explicit `null`. This is an inconsistency at the persistence boundary.

**Proposed remediation:**

Distinguish an absent property from an explicitly present property. Default only when the property is absent; if present, preserve it for validation so `null` is rejected. Apply the same rule to `components`, `wires`, `tracks`, and `vias`. Add migration tests for `null`, malformed objects, and arrays containing malformed entries.

**Compatibility implication:**

Valid legacy files that omit these fields continue to migrate exactly as before. Corrupted files that previously became empty collections will now fail closed, which is the intended integrity change.

### P2-002 — Circle pads accept contradictory width/height geometry

**Severity:** P2

**Source:** `shared/engineering.ts:398`, `validatePad`; geometry consumers at lines 109, 117, 262, and 263

`validatePad` validates that both `width` and `height` are positive, but does not enforce the invariant required by the `circle` shape. The geometry implementation treats a circle's radius as `width / 2` and ignores `height` in several calculations. Therefore, a persisted pad with `shape: "circle", width: 10, height: 1` is accepted by the schema validator even though its stored dimensions contradict its declared shape.

**Reproduction:**

```ts
validateProjectJsonDetailed({
  components: [{
    id: "c", ref: "C1", x: 0, y: 0,
    footprintGeometry: {
      identifier: "fp",
      pads: [{
        id: "p", number: "1", position: { x: 0, y: 0 },
        width: 10, height: 1, shape: "circle", layer: "F.Cu"
      ]
    }
  }],
  wires: [], tracks: [], vias: []
})
// currently returns { ok: true, errors: [] }
```

**Proposed remediation:**

Define and enforce the persisted circle invariant consistently. The least disruptive option is to require finite positive `width` and `height` and exact equality for `shape: "circle"`, or explicitly normalize a circle to one diameter field before validation. The selected policy must be documented and applied identically to migration and direct validation.

**Compatibility implication:**

Existing valid circle fixtures already use equal dimensions. Any external files that intentionally encode a circle with a redundant, different height would become invalid rather than being interpreted ambiguously.

### P2-003 — Direct `validateSchematic` helper throws on malformed runtime input

**Severity:** P2

**Source:** `shared/engineering.ts:269-282`, especially lines 270, 274, 275, and 277

`validateSchematic` is exported and directly iterates `project.components`, `project.wires`, and optional `project.junctions` without a runtime validation boundary. Unlike `runDesignRules`, which first invokes `validateProjectJsonDetailed`, the direct helper can throw on malformed input.

**Reproduction:**

```ts
validateSchematic({ components: null, wires: [], junctions: [] } as never)
// throws TypeError: Cannot read properties of null (reading 'forEach')

validateSchematic(null as never)
// throws TypeError: Cannot read properties of null (reading 'components')
```

This violates the project’s fail-safe validation principle for a public validation helper and creates an inconsistency between direct and aggregate paths.

**Proposed remediation:**

Add a narrow runtime boundary for the direct schematic helper. It should validate the required schematic collections and return a stable `SCH_INVALID_INPUT` error finding, or an equivalent documented diagnostic, instead of throwing. The aggregate `runDesignRules` path must retain its existing `PROJECT_INVALID` result and must not double-report the same malformed input.

**Compatibility implication:**

Valid typed calls and aggregate DRC behavior remain unchanged. Only malformed runtime calls change from an exception to a deterministic finding.

## 4. Observed gaps that are not yet confirmed defects

### Application-level JSON import/export boundary

Repository search found `migrateProjectJson` and `validateProjectJsonDetailed`, but no dedicated application-level project JSON import/export API or UI call site. This is a verified implementation gap, not a claim that a missing feature is a bug. If JSON persistence is part of the product acceptance criteria, P2 should define an explicit import/export boundary that parses JSON, validates before state replacement, preserves the original payload on failure, and reports structured errors. If persistence is intentionally deferred, it should be recorded as a product limitation rather than implemented in P2.

### Schema semantic constraints beyond field types

The current validator checks types, finiteness, positivity, known fields, and per-collection IDs. It does not establish all cross-object semantics, such as whether pad identifiers must be globally unique across footprints, whether every net label has a corresponding connectivity model, or whether design-rule combinations are physically coherent. These are candidates for later design work, not confirmed P2 defects without a declared invariant.

## 5. Required adversarial regression tests before implementation is accepted

1. Migration defaults absent legacy arrays but rejects explicit `null`, objects, and malformed entries for every required collection.
2. Migration continues to reject unsupported versions, unknown root fields, and malformed nested fields.
3. Circle pads with equal dimensions remain valid; unequal dimensions are rejected or deterministically normalized according to the chosen policy.
4. Rectangular and oval pads retain current rotation and clearance goldens.
5. `validateSchematic(null)`, null collections, non-array collections, null junctions, and malformed wire entries return stable findings and never throw.
6. `runDesignRules` continues returning `PROJECT_INVALID` for malformed full projects and does not duplicate direct-helper diagnostics.
7. Versionless, v1, and v2 P1 inputs retain identical accepted geometry/finding goldens.
8. Stable DRC finding IDs and ordering remain unchanged for valid inputs.
9. A valid legacy project round-trips through the selected serialization boundary without data loss, if an application-level boundary is approved for scope.

## 6. Risks and compatibility implications

The principal risk is over-tightening legacy compatibility. Defaults must remain available for genuinely absent legacy fields, while explicit malformed fields must fail closed. Shape validation must not silently change the interpretation of existing valid footprints. Direct-helper hardening must preserve the existing `runDesignRules` diagnostic contract. All P2 changes should therefore be introduced behind focused regression tests and compared against the P1 goldens.

No numerical geometry rewrite is justified by this investigation. The current P1 V2 evaluator and its finding identity/order should remain frozen unless a new reproducible counterexample is found.

## 7. Acceptance criteria

P2 is acceptable only when all of the following are true:

- The three confirmed findings have source-level fixes or an explicitly approved deferral.
- Explicit `null` and malformed migration fields fail closed, while absent legacy optional arrays still receive documented defaults.
- Circle geometry has one documented invariant and validator/evaluator behavior is consistent with it.
- Direct schematic validation never throws for malformed JSON-shaped runtime input.
- All new adversarial tests pass.
- The complete existing suite, TypeScript check, and production build pass.
- P1 compatibility goldens remain unchanged and pass.
- `main` and PR #3 remain untouched and unmerged.
- P2 remains isolated on `audit/phase6-1-p2-independent-20261123` until implementation is explicitly authorized.

## 8. Implementation recommendation

**Recommendation: IMPLEMENT P2 on the isolated audit branch, but only after explicit approval of this design report.** Three actionable P2 findings are confirmed and reproducible. The remediation should be minimal: harden migration presence-vs-null handling, enforce the circle dimension invariant, and add a fail-closed boundary for direct schematic validation. Do not begin broader schema redesign or application-level import/export work without a separate scope decision.

At this stage, no source code or test changes have been made, no commit has been created, and no push or PR has been performed.
