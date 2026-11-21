# PCB Studio Pro — Phase 6.1 P1 Remediation Design Gate

## 1. Baseline and repository status

The inspected product repository is `soheil6913/-PCB-Studio-Pro`. The fresh isolated checkout is on `main` at `a98384bbfc3296947b90f5254a03a77b11fdc8a9`; the live remote `main` resolves to the same SHA. The origin URL identifies the same repository, the required commit object exists, and the worktree was clean. No branch, source change, commit, push, PR, merge, or test execution was performed for this design task.

The controlling architecture source is the exact user-provided attachment `PHASE_6_0_10_DELEGATED_OWNER_DECISIONS_AND_PRODUCT_ARCHITECTURE.md`, not another Phase 6.0 document. Section 11.2 requires preserving the legacy evaluator and fallback, identifying the existing diagnostic identity from the correct baseline, and implementing an explicit selector. Section 13 P1 requires golden v2 projected-2D all-Via-pairs `minimumViaClearance`, the radius/diameter/`drill` fallback, no policy selection from ViaSpan presence, and exact legacy identity preservation. P1 precedes P2; this design does not implement schema-v3 or migration. [1]

## 2. Current version, reader, validator, and evaluator architecture

### Version fields and readers

`shared/engineering.ts:10–13` declares the v2 Via shape and `EngineeringProject.schemaVersion?: number`; line 23 fixes `CURRENT_PROJECT_VERSION` at 2. No other production model-version or evaluator-selector field was found in the tracked client, server, or engineering source. `EngineeringVia` has only `id`, `x`, `y`, `drill`, optional `diameter`, and optional two-ended `layers`; it has no `ViaSpan`, Stackup, process-evidence, ledger, or graph property. [2]

The UI has a separate `Project` type at `client/src/pages/Home.tsx:18–21`; it does not include `schemaVersion`. Its seed also has no schema version. Local-storage hydration at lines 89–90 parses and validates the stored object, then uses it as UI state without migration. The autosave effect at line 91 serializes that state unchanged. Therefore normal in-memory/autosaved projects can be versionless. Explicit Save at line 97 writes `schemaVersion: 2`; JSON export at line 94 also adds `schemaVersion: 2`. File import at line 96 calls `migrateProjectJson` and stores the returned current-shape project. The production DRC panel calls `runDesignRules(p)` at line 82. [3]

### Validation and current missing/unsupported-version behavior

`validateProjectJsonDetailed` at `shared/engineering.ts:332–347` allows `schemaVersion` to be absent. If present, it must be an integer from 1 through `CURRENT_PROJECT_VERSION` (2). It also rejects unknown top-level fields through an allowlist at line 334 and unknown Via fields through the Via allowlist at line 343. [2]

`migrateProjectJson` at line 350 treats an absent `schemaVersion` as source version 1, rejects non-integer/out-of-range versions, then writes the current version 2 and defaults missing arrays and grid. This is existing v1-to-current migration behavior; it is distinct from runtime DRC behavior. Existing fixtures separately cover explicit v2, explicit v1, and missing-version migration. [2] [4]

`runDesignRules` at line 325 validates the complete project first. On validation failure, it returns the existing `PROJECT_INVALID` finding; otherwise it always runs `validateSchematic(project)` followed by `validatePcb(project)`. It does not branch on `schemaVersion`. Thus version 1, version 2, and missing-version objects that pass validation currently reach the same evaluator path. The code does not call migration from `runDesignRules`. [2]

`validatePcb` at lines 286–307 is an exported evaluator entry point. It validates a reduced object assembled from `components`, `tracks`, `vias`, `board`, and `designRules`; that projection omits the root `schemaVersion` and other root properties. This means a direct call can ignore an extra root `schemaVersion: 99` or other root-level model fields and still run the v2 evaluator. Nested unknown fields inside Via objects are retained and rejected by validation. In production, the UI invokes `runDesignRules`, not `validatePcb` directly; tests and other engineering code call `validatePcb` directly. The direct helper is therefore a bypass risk if treated as a generic model entry point. [2] [3] [4]

For the aggregate application path, unsupported versions and unknown new-model fields fail validation before evaluator execution. `validateProjectJsonDetailed` rejects future versions and unlisted root/nested fields; `runDesignRules` returns `PROJECT_INVALID`. On import, `migrateProjectJson` returns `null` for unsupported versions or invalid fields. Local-storage hydration falls back to the seed when validation fails. Existing tests reject `schemaVersion: 99`, but do not cover a full dispatcher or all unsupported states. [2] [3] [5]

### Existing V2 evaluator and exact diagnostic identity

The v2 Via-pair rule is implemented in `shared/engineering.ts:321`. It iterates every unordered pair in array order. It computes center distance in projected 2D with `distance({x:a.x,y:a.y},{x:b.x,y:b.y})`; it does not gate pair applicability on `layers`. Effective diameters are exactly `a.diameter ?? a.drill * 2` and `b.diameter ?? b.drill * 2`. Required separation is both radii plus `minimumViaClearance`. The current comparator preserves clear, violation, and numerical-indeterminate outcomes. [2]

The existing rule ID is `PCB_VIA_TO_VIA_CLEARANCE`. There is no separate `key` property in `DrcResult`; the existing finding `id` is the key: `result()` at line 81 returns ``${ruleId}:${objectIds.join(",")}``. Therefore pair identity is `PCB_VIA_TO_VIA_CLEARANCE:<firstViaId>,<secondViaId>`, in input pair order. The goldens explicitly preserve this ordering; reversing the Via array reverses `objectIds` and the finding ID. Do not sort or rename the IDs. [2] [4]

The existing tests freeze this behavior, including missing `layers`, reversed valid v2 layer tuple order, fallback and explicit diameters, mixed fallback, equality, violation, clear pairs, multiple pair order, and an uncertainty-edge result. However, the test named for hypothetically disjoint future spans stores those span sets only as test metadata outside the v2 project and asserts the actual Via object has no `futureViaSpan`; it does not execute a runtime project with that field present. The current test asserts the golden subset `id`, `ruleId`, `severity`, and `objectIds`, not every presentation string or optional payload field. [4] [5]

## 3. Proposed smallest explicit, versioned dispatch contract

Use the existing `schemaVersion` as the sole persisted selector. Keep `CURRENT_PROJECT_VERSION` at 2. Do not add a new persisted selector, numeric version, schema-v3 type, evidence model, or migration. An internal dispatch result may distinguish source cases, but it is not persisted and does not create a new schema or DRC identifier.

The resolver should receive only the declared version state (explicit integer, absent, or invalid), not the project’s arbitrary fields. It should run only after the existing full-project validator has accepted the input. This makes the selector incapable of inspecting ViaSpan, Stackup, process evidence, ledger, graph, or other feature presence. The resolver routes supported legacy source states to the unchanged v2 evaluator. Unsupported states do not reach any evaluator.

Recommended explicit cases:

- `schemaVersion === 2`: select the frozen legacy v2 evaluator.
- `schemaVersion === 1`: preserve the current direct-DRC behavior through the same existing evaluator, while keeping the input classification distinct from explicit v2. File import continues to use the existing v1-to-current-v2 migration; P1 does not add or alter migration.
- `schemaVersion === undefined`: preserve the current versionless runtime behavior through a separately classified compatibility case that reaches the same existing evaluator. Do not rewrite the in-memory object or pretend the source explicitly declared version 2. The current UI creates and autosaves versionless state, and `runDesignRules` presently evaluates it; changing that would be a product behavior change. Owner approval is required to freeze this mapping as the intended compatibility contract.
- Any present version not accepted by the current validator (including 0, negative, non-integer, non-number, or greater than 2): preserve the existing fail-closed aggregate path. `runDesignRules` returns the existing `PROJECT_INVALID` finding and `migrateProjectJson` returns `null`; do not invent a new diagnostic ID or infer a model from v2-like fields.

In implementation, place one resolver/dispatch boundary in `shared/engineering.ts` in the aggregate path. Keep the current validation-before-evaluation order. Keep `validateSchematic` and the V2 `validatePcb` implementation unchanged. The dispatch branch for each currently accepted source-version state should call the same V2 evaluator without changing order, formulas, tolerances, fallback, or finding identity. The only allowed unsupported result is the existing validation failure behavior. The direct `validatePcb` export must be explicitly documented and treated as V2-only; it must not become a generic multi-model selector. Whether to add a runtime guard for unsupported version fields on direct calls requires owner approval because current direct calls discard root fields and run the legacy evaluator.

This contract is explicit because all routing decisions are made from a finite interpretation of `schemaVersion`, including an explicit versionless case. It is versioned because supported persisted versions are taken from the existing field and current validator, not from presence of arbitrary model features. It does not implement a v3 route.

## 4. Case-by-case behavior table

| Input case | Current baseline behavior | Proposed P1 dispatch behavior | Approval / caveat |
|---|---|---|---|
| Explicit `schemaVersion: 2`, valid v2 shape | Validator accepts. Import returns v2 with existing defaults. Save/export writes 2. `runDesignRules` runs the current evaluator. | Explicitly resolve to frozen V2; run the unchanged evaluator. | No new version or stored selector required. |
| Explicit `schemaVersion: 1`, valid legacy shape | Validator accepts. Import migration writes current version 2. Direct `runDesignRules` does not migrate and runs the same evaluator as all accepted projects. | Keep a separately classified v1-source compatibility branch to the same frozen evaluator; do not add migration. | Owner should confirm that direct v1 input continues to use current V2 evaluator, rather than requiring normalization before DRC. |
| `schemaVersion` absent | Validator accepts if other fields are valid. Import migration treats it as v1 and writes version 2. Local-storage hydration preserves it absent; autosave serializes it absent unless explicit Save has added 2. Direct DRC runs current evaluator. | Keep a distinct `version-omitted` dispatch case to the same evaluator to preserve observed behavior; do not rewrite state during DRC. | Owner must approve this exact compatibility mapping. Missing is not claimed to be semantically identical to explicit 2. |
| Unsupported or malformed version | Full validator rejects. Aggregate DRC returns `PROJECT_INVALID`; importer returns `null`; local-storage hydration falls back to seed. | Reject before dispatch using those existing paths; no fallback to V2 based on shape and no new DRC ID. | Direct `validatePcb` currently omits root version from its reduced validation input; decide whether the legacy-only API is enough or a runtime guard is required. |
| V2 version with unknown root model field such as `stackup`, `processEvidence`, `ledger`, `graph`, or `viaSpan` | Full project validator rejects the unknown field; aggregate DRC returns `PROJECT_INVALID`; migration fails validation. Local storage does not load it as a valid project. | Reject before dispatch; field presence must never select an evaluator. | Direct `validatePcb` discards unknown root fields, so it must not be used as a generic project boundary. |
| Unknown field nested in a Via | Via allowlist rejects it. Aggregate path returns `PROJECT_INVALID`; direct `validatePcb` sees nested Via data and returns `PCB_INVALID_INPUT`. | Reject; do not interpret a new field as V2 span or a new model signal. | Preserve the existing diagnostic for each current entry point. |

## 5. Golden regression test matrix

The implementation should extend the existing fixture tests without replacing or weakening them. Compare the existing identity fields exactly: `id`, `ruleId`, `severity`, and ordered `objectIds`. Run the same valid v2 golden projects through the aggregate dispatcher, not only `validatePcb`, so the new dispatch boundary is covered. Do not alter the geometric expected values or introduce new identifiers.

| Test group | Inputs and assertions | Expected result |
|---|---|---|
| Projected 2D all-pairs | Two and three Vias; pairs separated and violating; distinct and missing legacy `layers`; reversed Via order. Independently compute `hypot(dx,dy)` for every pair. | Same all-pairs V2 outcomes and order; no layer-overlap gate. |
| Radius/diameter/`drill` fallback | Both explicit diameters; both omitted; mixed explicit/fallback; equality; definite violation; near-boundary indeterminate. | Preserve `diameter ?? drill * 2`, existing comparator, rule IDs, finding IDs, and order. |
| Explicit v2 dispatch | Each current v2 golden has `schemaVersion: 2` and runs through `runDesignRules`. | Exact same V2 Via findings as the current golden set. |
| Explicit v1 and missing version | Separate tests for `schemaVersion: 1` and no `schemaVersion`, through detailed validation, import migration, and aggregate DRC. Do not combine their fixtures. | Preserve each current path: direct DRC to existing evaluator; migration output is current schema 2. Expectations require owner approval before implementation. |
| Unsupported and malformed versions | Test version 3, larger future integer, 0, negative, fractional, string, and null through `validateProjectJsonDetailed`, `migrateProjectJson`, and `runDesignRules`. | Validator false, migration null, aggregate generic `PROJECT_INVALID`; no V2 fallback or new ID. |
| ViaSpan and layer metadata | No `ViaSpan`/span field: retain existing all-pairs golden. Add ViaSpan-like root and nested unknown-field cases under explicit v2. Separately unit-test resolver with only the schemaVersion input. | Resolver result depends only on version state; generic full-project entry rejects unknown fields before evaluation. No model switch from presence or absence. |
| Stackup, process evidence, ledger, graph | Inject each as unknown root metadata under schemaVersion 2 and test aggregate path. | Existing validation failure, not a different evaluator; no new model evidence gates on valid v2. |
| Direct `validatePcb` boundary | Test it as the frozen V2-only evaluator and document whether unsupported root version metadata must be rejected or remains out of contract. | No cross-model selection; any policy change to the direct helper is separately approved. |
| Existing finding identity | Use fixture values, including reversed array order and multiple pairs; check `id`, `ruleId`, severity, and ordered object IDs. | Preserve `PCB_VIA_TO_VIA_CLEARANCE:<pair in existing input order>`; never sort or rename. |

The current v2 goldens cover much of the geometry requirement. They do not currently test dispatch, run every clearance golden through `runDesignRules`, test future-version rejection through the aggregate path, or prove new-field handling at both the aggregate and direct-helper boundaries. The proposed additions close those design gaps without introducing Schema-v3.

## 6. Risks and rollback strategy

**Versionless state is a live path, not an edge case.** `Home.tsx`’s state type and seed omit `schemaVersion`; local storage accepts and auto-saves that state. Requiring explicit version 2 everywhere would affect existing local projects. The smallest behavior-preserving design is a distinct, explicit versionless compatibility route to the same frozen evaluator, subject to owner approval.

**Import and runtime semantics differ.** Import normalizes absent and v1 version states to current version 2. Runtime DRC does not migrate. The dispatcher must not call migration as a shortcut; that would add normalization/default behavior to the DRC path and exceed P1.

**The direct PCB helper can bypass aggregate validation.** `validatePcb` is exported and drops root metadata while building its validation input. The app’s only production DRC caller is `runDesignRules`, which validates the complete object first. A future model must use the aggregate dispatcher, not direct `validatePcb`. Whether P1 changes the direct helper’s unsupported-version behavior is an owner decision, since adding a rejection there changes existing behavior for unusual direct callers.

**V2 identity is order-dependent.** The pair `id` is assembled from the ordered `objectIds`. Sorting IDs or canonicalizing pairs would change existing findings even if the geometry result is identical.

**Unknown future fields are not extension points in the current schema.** Strict full-project validation rejects them. P1 should keep this behavior; lossless preservation, new field schemas, new-model evidence, and migrations belong to later authorized work, not this design.

For rollback, the future P1 change should be only a dispatch wrapper and focused tests. The existing V2 evaluator body, comparator, `result()` identity helper, and fallback must remain unchanged. If any golden differs, do not accept the new dispatch and do not enable any new-model path; revert the wrapper and retain the baseline reader/evaluator. No project data should be rewritten by the P1 dispatcher, so rollback must not require data migration. P2 remains blocked until independent review accepts P1 implementation evidence.

## 7. Owner approvals required before implementation

1. Confirm that an absent `schemaVersion` remains a distinct `versionless` compatibility input routed to the existing evaluator, because the UI routinely creates, hydrates, and autosaves projects without the field.
2. Confirm that direct `schemaVersion: 1` DRC input remains on the existing evaluator even though file import normalizes it to current version 2.
3. Confirm that `schemaVersion` remains the sole persisted selector for P1 and `CURRENT_PROJECT_VERSION` remains 2; no new persisted model field or version is introduced.
4. Decide whether exported `validatePcb` is an explicitly V2-only low-level API or must reject unsupported root version/model metadata when called directly. The current full-project path is safe; the helper currently drops root metadata.
5. Confirm the existing unsupported-version behavior is retained: generic `PROJECT_INVALID` from `runDesignRules`, `null` from `migrateProjectJson`, and no newly invented diagnostic ID or key.
6. Confirm the P1 golden contract freezes `id`, `ruleId`, `severity`, and ordered `objectIds` while not necessarily freezing explanation/correction prose or all optional output fields. The current Phase 6.1.1 snapshot captures those four identity fields.
7. Confirm that unknown ViaSpan/Stackup/process/ledger/graph fields remain rejected in the v2 full-project boundary, rather than being preserved or interpreted during P1.

## References

Canonical source is the exact user-provided, non-public attachment named `PHASE_6_0_10_DELEGATED_OWNER_DECISIONS_AND_PRODUCT_ARCHITECTURE.md`, especially Section 11.2, Section 12 cases 26 and 39, and Section 13 P1/P2. It is not replaced by another Phase 6.0 report. [1]

[1]: file:///home/ubuntu/upload/PHASE_6_0_10_DELEGATED_OWNER_DECISIONS_AND_PRODUCT_ARCHITECTURE%281%29.md "User-provided canonical Phase 6.0.10 architecture attachment"
[2]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.ts "Exact-baseline engineering types, validation, migration, evaluator, and finding identity"
[3]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/client/src/pages/Home.tsx "Exact-baseline project state, file operations, persistence, and DRC caller"
[4]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.v2-compatibility.test.ts "Exact-baseline V2 and migration compatibility tests"
[5]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.v2-compatibility.fixtures.ts "Exact-baseline V2 and migration golden fixtures"
[6]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/engineering.test.ts "Existing unsupported-version and migration tests"
[7]: https://github.com/soheil6913/-PCB-Studio-Pro/blob/a98384bbfc3296947b90f5254a03a77b11fdc8a9/shared/phase5_5.drc-policy-certification.test.ts "Existing V2 Via span limitations and all-pairs observations"
