# PCB Studio Pro — Phase 6.0.4 Final Contract Consistency Audit

**Status:** Design-only correction and audit. No implementation is authorized.  
**Reference:** `/home/ubuntu/work/PHASE_6_0_3_DESIGN_FREEZE_CORRECTIONS.md`  
**Output:** `/home/ubuntu/work/PHASE_6_0_4_FINAL_CONTRACT_CONSISTENCY_AUDIT.md` (outside the repository)

## 1. Mission, scope, and repository facts

This pass corrects only the five contract gaps enumerated in the Phase 6.0.4 instructions and checks their compatibility with the full Phase 6.0.3 architecture. It proposes implementation requirements; it does not edit source, tests, configuration, dependencies, UI, CI, or Git state. It does not start Phase 6.1 or 6.2.

Before work, the actual repository was `https://github.com/soheil6913/-PCB-Studio-Pro.git` at `/home/ubuntu/work/repo`; branch `implementation/phase6-net-aware-drc-20261120`; `HEAD` exactly `6fad0dcdc7e5878e671b8b419b2f61084e5a8138`; worktree clean; `main` exactly `de7497a675af7c6212bbc4751fce098c1f414e8d`. The reference report says the Phase 6 model is proposed, not present in production. Those are repository facts verified before this report; all type contracts below are design proposals.

No tests, checks, or builds were run: this is design-only and no repository code changed. No repository changes, branch changes, commits, pushes, PRs, merges, rebases, cherry-picks, or amendments were made.

## 2. Concise change summary

1. Added explicit ViaSpan diagnostics with deterministic attribution/deduplication, severity/sign-off classification, and schema-v2 compatibility behavior; valid disjoint spans remain a separate valid result.
2. Strengthened Microvia junction validation so a conductive edge requires a certified, exact node-pair witness current for the complete geometry/evidence context; malformed topology is invalid, while absent/stale/unprovable contact evidence leaves connectivity unknown.
3. Defined a canonical SHA-256 physical-component snapshot identity independent of DSU roots and traversal order, and specified its input sensitivity and use.
4. Corrected contact-ledger pseudocode: record one canonical contact outcome per identity, retain all evidence, and enforce a uniqueness invariant before graph construction/classification.
5. Replaced redundant Stackup order fields with one canonical physical sequence; copper order and faces are derived, with explicit validation rules for invalid versus unknown state.

## 3. Correction matrix: Phase 6.0.3 defects to Phase 6.0.4 resolutions

| Phase 6.0.3 gap | Resolution in this report | Status |
|---|---|---|
| Unknown/invalid ViaSpan did not define a complete diagnostic contract | §4 specifies seven finding IDs, triggers, attribution, stable keys, sign-off semantics, and v2 handling | Corrected as proposed contract; exact severities remain pending policy |
| Microvia `certified` junction had no structural/evidence freshness checks | §5 defines stage/node/layer/evidence validation and invalid-vs-unknown outcomes | Corrected as proposed contract; manufacturing process policy remains pending |
| Physical component ID depended on unspecified snapshot naming | §6 specifies canonical node ordering, serialization, graph-contract inputs, and SHA-256 | Corrected as proposed contract |
| Boundary branch pseudocode appended result twice | §7 records a single canonical contact record and adds duplicate rejection invariant | Corrected |
| Stackup duplicated physical order, copper order, and copper list without reconciliation contract | §8 uses only `layersFrontToBack` as the order source and derives copper order/face IDs | Corrected as proposed contract |

## 4. ViaSpan diagnostic contracts

### 4.1 Principles and result types

A valid span with an empty intersection with another valid span means **known disjoint**. It is not a missing, unknown, invalid, unsupported, or unevidenced span. Unknown/invalid states never enumerate to an empty set. Unknown and invalid remain separately visible in the run result.

Proposed finding contracts (severity is a design classification, not a product severity enum):

| Finding ID | Exact trigger | Attribution and stable dedup key | DRC-clear sign-off | Schema-v2 interaction | Class |
|---|---|---|---|---|---|
| `PCB_VIA_SPAN_MISSING_OR_UNRESOLVED` | A Via requiring span-aware connectivity has absent span; legacy data cannot be resolved to a valid declared span; referenced stackup is unavailable; or required endpoint identity is unresolved. Do not trigger merely because two otherwise valid spans are disjoint. | Via object ID; optional raw span digest; implicated endpoint/layer IDs if known; schema/version. Key: `(findingId, projectId, viaObjectId, spanRecordDigest-or-MISSING, stackupRevision-or-UNKNOWN)`. | Yes: cross-layer connectivity is unknown. Whether severity is Error or Warning is pending. | Does not suppress or change v2 all-pairs projected `minimumViaClearance`; report both findings independently when applicable. Legacy unresolved span is expected here. | Pending product severity; fail-closed completeness requirement |
| `PCB_VIA_SPAN_INVALID` | A span record is structurally contradictory or violates declared kind/endpoints: unknown or non-copper endpoint, disabled endpoint, zero-length, invalid ordering/kind combination, duplicate stage ID, or invalid Stackup reference. | Via ID, span record, endpoint IDs, stackup revision, all validation codes. Key: `(findingId, projectId, viaObjectId, spanRecordDigest, sorted diagnostic codes, stackupRevision)`. | Yes; invalid span cannot establish connectivity. | Legacy v2 values that cannot satisfy the new model are not retroactively made invalid if legacy compatibility only requires projected clearance; classify span as unresolved and run v2 check unchanged. Truly malformed serialized data may additionally be invalid under schema validation. | Error candidate; severity/blocking remains pending |
| `PCB_VIA_BARREL_EVIDENCE_MISSING` | A purported continuous through/blind/buried span lacks a required continuous-plated-barrel evidence reference. Matching endpoints, names, or geometry do not qualify. | Via ID; span kind/endpoints; expected evidence role; record digest. Key: `(findingId, projectId, viaObjectId, spanRecordDigest, kind, sortedEndpoints)`. | Yes; no cross-layer edge may be created. | Same as above: v2 projected clearance remains independent. | Error candidate; severity pending |
| `PCB_VIA_BARREL_EVIDENCE_UNVERIFIABLE` | Evidence reference exists but is unavailable, hash-mismatched, untrusted/unverifiable under the configured evidence resolver, or does not establish continuity over the entire declared span. | Via ID; evidence ID/content hash/source; endpoints; resolver/status and validation-context digest. Key: `(findingId, projectId, viaObjectId, evidenceId, contentHash, validationContextDigest)`. | Yes; do not infer a continuous barrel. | Does not remove v2 projected clearance. | Error candidate; severity pending |
| `PCB_MICROVIA_STAGE_REFERENCE_INVALID` | Junction references nonexistent/equal stage IDs; duplicate stage ID; stage has invalid/non-copper/equal endpoints; referenced CopperNodeId is absent, duplicated, or not owned by its declared stage; endpoints contradict validated stackup or required stage endpoint-node layers. | Via ID; stage/junction IDs; referenced stage IDs, CopperNodeIds and LayerIds; precise validation codes. Key: `(findingId, projectId, viaObjectId, assemblyDigest, sortedStageIds, sortedNodeIds, sorted diagnostic codes)`. | Yes for affected microvia assembly; assembly is invalid and no inter-stage edge is admitted. | Legacy v2 remains evaluated by its unchanged projected rule; absent v2 stage representation is not a v2 failure. | Error candidate; severity pending |
| `PCB_MICROVIA_JUNCTION_INDETERMINATE` | Stage references are structurally valid but the expected inter-stage contact record is absent, not-connected, numerically indeterminate, uncertified, stale, or cannot prove the exact intended node pair on a common compatible copper layer in the current context. | Via ID; ordered canonical stage pair; exact expected node pair when known; layer; evidence/context digests and reason. Key: `(findingId, projectId, viaObjectId, canonicalUnorderedStagePair, canonicalNodePair-or-UNKNOWN, layerId-or-UNKNOWN, currentContextDigest)`. | Yes; the affected path remains unknown and no junction edge is added. | Does not suppress v2 projected clearance. | Pending severity; sign-off-blocking completeness finding |
| `PCB_VIA_PROCESS_UNSUPPORTED` | Span/process is well-formed enough to identify, but its technology/process is outside the explicitly supported process set or has no validated rule contract. Unsupported is not invalid, and neither is converted into a valid continuous barrel. | Via ID; process/type token; stage IDs if any; capability-registry version. Key: `(findingId, projectId, viaObjectId, processTokenDigest, capabilityRegistryVersion)`. | Yes for affected connectivity/DRC coverage; supported independent geometric checks continue. | Keep v2 projected clearance unchanged; emit unsupported finding separately if the new analyzer is requested. | Pending severity; unsupported capability |

For all findings, canonical keys are hashed only after stable field normalization; payload detail is retained in run evidence even if output aggregation caps repeated findings. If multiple defects apply, emit distinct IDs where they represent distinct missing guarantees; do not collapse unsupported into unknown or invalid, and do not report valid-disjoint as a diagnostic.

### 4.2 Enumeration and sign-off contract

`enumerateSpan(validSpan, validatedStackup)` returns `known(layers)` including both endpoints. An empty pairwise intersection of two `known` enumerations is `known-disjoint`. `unknown` input yields unknown comparison; invalid input yields invalid comparison. Neither may be translated to an empty layer set.

Unknown, invalid, unsupported, or unevidenced spans contribute no inferred cross-layer conduction edge. A missing/uncertain inter-stage path may still have known same-layer copper contacts within each stage; retain those edges and evidence while marking only the unproven transition unresolved. The independent v2 `minimumViaClearance` check continues to compare every Via pair using the observed 2D projected outer-copper rule, with `drill` fallback as specified in Phase 6.0.3, and never uses span intersection as a gate.

## 5. Microvia stage-junction validation contract

### 5.1 Proposed evidence shape

```ts
type JunctionEvidenceContext = {
  inputRevision: string;
  geometryHashes: readonly [string, string]; // canonical node order
  contactLayerId: LayerId;
  predicateId: string;
  predicateVersion: string;
  kernelId: string;
  kernelVersion: string;
};

type MicroviaStageJunction = {
  fromStageId: string;
  toStageId: string;
  fromNodeId: CopperNodeId;
  toNodeId: CopperNodeId;
  evidence:
    | { state: "certified"; contactId: ContactId; context: JunctionEvidenceContext; witness: ContactEvidence }
    | { state: "indeterminate"; reason: string; context?: Partial<JunctionEvidenceContext>; witness?: ContactEvidence }
    | { state: "not-connected"; reason: string };
};
```

An edge may be created only for a `certified` junction that passes every check below. “Certified” is an evidence assertion to validate, not a trusted boolean.

### 5.2 Validation sequence and classification

1. Resolve `fromStageId` and `toStageId`; both must exist and differ. Stage IDs must be unique within the assembly.
2. Each stage’s `from` and `to` LayerIds must resolve to enabled copper layers in a valid Stackup and be distinct. Apply approved process endpoint/adjacency rules; until approved, do not invent additional process constraints.
3. Resolve `fromNodeId` and `toNodeId`. Both CopperNodeIds must exist, be conductive nodes in the assembly, and be listed as members of their respective declared stages. Their layer IDs must equal the declared contact layer and the stages’ physically compatible endpoint layers.
4. The nodes must be distinct. The two stages must share the declared copper layer in a way consistent with their modeled conductive endpoint geometry. A coincident stage label, equal endpoint name, stacked/staggered arrangement, or placement relation is insufficient.
5. The witness’s canonical sorted `nodeIds` must equal exactly the sorted pair `{fromNodeId,toNodeId}`. No other node pair, contact between other stage lands, or same-name evidence may be substituted.
6. `witness.layerId` and `context.contactLayerId` must equal the resolved common layer. The witness geometry hashes must equal the current hashes of those exact nodes in that same canonical order. `inputRevision`, predicate/kernel IDs and versions must exactly match the current analysis context. `contactId` must recompute from the canonical node pair, layer, hashes, input revision, and predicate/kernel versions according to the ContactId contract; stale evidence is not accepted.
7. The witness must carry a robust/exact certified conductive-contact outcome under the approved contact semantics. A `boundary-contact` is not certified continuity while tangent policy is pending; `indeterminate`, `separated`, missing proof, a hand-asserted label, or an unverified imported claim cannot create the edge.
8. Junction records are keyed by canonical unordered stage pair plus canonical node pair. Duplicate records are detected even if reversed. A reversed duplicate is the same record, not a second edge. Conflicting evidence/status for the same key is contradictory. A cycle is detected in the stage-level junction graph; cycles do not create extra physical connectivity, and whether a cycle is permissible process modeling is pending owner policy. Repeated/reversed edges are deduplicated only after validating their evidence and reporting duplicates.
9. Validate assembly path coverage. Every required transition between stages in a claimed continuous path needs exactly one accepted certified junction. Missing transitions are unknown; contradictory or malformed transition references make assembly invalid. Do not infer intended sequence from array order alone.

**Invalid assembly**: nonexistent/equal stage references; duplicate stage IDs; invalid endpoints; unknown node references; node not belonging to its declared stage; impossible layer ownership; contradictory duplicate records; or an asserted junction whose node pair/layer/context contradicts its own referenced data. Emit `PCB_MICROVIA_STAGE_REFERENCE_INVALID` (or the appropriate ViaSpan invalid finding) and add no offending edge. Preserve any independently valid within-stage edges.

**Unknown connectivity**: otherwise valid stage and node structure but missing evidence, unsupported evidence source, stale/unavailable proof, certified state without valid proof, `indeterminate`/`not-connected` record where continuity is expected, or an unresolved numerical/boundary result. Emit `PCB_MICROVIA_JUNCTION_INDETERMINATE`; add no inter-stage edge. A `not-connected` result is known absence for that exact pair, but the intended assembly’s continuous path is incomplete; it is not a physical contact and is not silently treated as a confirmed edge.

## 6. Deterministic physical-component snapshot identity

### 6.1 Contract

Proposed `confirmedPhysicalComponentSnapshotId` is a content-derived identifier for the graph-construction snapshot and one confirmed component. It is not the editable component ID, not a DSU representative, and not a timestamp.

Canonical serialization uses UTF-8 JSON Canonicalization Scheme (RFC 8785) over this exact logical object, with all strings Unicode NFC-normalized and arrays sorted by bytewise UTF-8 order after normalization:

```json
{
  "domain": "pcb-confirmed-physical-component",
  "snapshotFormat": 1,
  "projectStableId": "...",
  "inputRevision": "...",
  "graphContractVersion": "...",
  "stackupRevision": "...",
  "contactPredicateVersion": "...",
  "geometryKernelVersion": "...",
  "copperNodeIds": ["sorted unique canonical CopperNodeId values"]
}
```

`projectStableId` is a stable project identity, never a display name. If unavailable, the snapshot is `identity-unknown` and cannot be used as a globally stable dedup key; the owning migration/project-identity policy must resolve it. Hash the canonical byte sequence with SHA-256; represent it as `pcsc1:` followed by lowercase hex. No timestamps, random IDs, mutable DSU roots, insertion indices, traversal order, or noncanonical object-property order participate.

All identity-bearing inputs that can alter the confirmed graph must change the snapshot: input revision, stackup revision/content revision, graph-contract version, predicate and kernel versions, and the sorted node membership (node IDs are themselves bound to canonical geometry/object/layer identity by the design contract). A geometry edit that changes membership or relevant node identity changes the ID. A geometry or policy/kernel update that leaves membership the same still changes the snapshot because the corresponding revision/version changes. If revisions do not faithfully change when such inputs change, the ID contract is not satisfied. Repeating the same analysis inputs and versions reproduces identical bytes and ID.

Use the ID as the primary key for one short finding per confirmed component, and as an immutable snapshot reference in finding/evidence payloads. It can participate in indeterminate-contact grouping only alongside the canonical unordered pair of component snapshot IDs and current context; stale snapshots must not aggregate with current evidence. Finding IDs are not replaced by component IDs.

### 6.2 Adversarial determinism examples

- Same four CopperNodeIds inserted as `[n4,n1,n3,n2]` versus `[n1,n2,n3,n4]`: sorting gives identical canonical bytes and snapshot ID.
- Edges supplied in reverse order, or with their endpoints reversed: edges do not appear in the component identity payload; the resulting sorted membership is the same, so ID is identical.
- DSU unions `n1-n2, n2-n3, n3-n4` versus `n3-n4, n1-n2, n2-n3`: roots may differ, but the sorted component node set and identity context are equal, so ID is identical.
- Same members, different `geometryKernelVersion` or `contactPredicateVersion`: IDs differ, preventing evidence from distinct evaluation contracts from aliasing.
- Same IDs and contract versions, but changed input or stackup revision: IDs differ. Same complete canonical inputs repeated: IDs match exactly.

## 7. Contact-record uniqueness and corrected algorithm

The Phase 6.0.3 pseudocode’s boundary-contact branch contains a duplicated `contacts.append(result)` according to the defect identified for this phase. Phase 6.0.4 removes the duplicate append and replaces loose branch-local appends with canonical upsert semantics, so each contact identity is recorded exactly once while all distinct evidence remains retained.

Canonical contact identity is computed once from `(canonical node pair, layer, geometry hashes, input revision, contact predicate ID/version, kernel ID/version)`. For every candidate pair, store the outcome in a map keyed by that identity. A second computation of the same identity must either be byte-identical (retain one record and attach additional provenance references) or be flagged as a contradictory duplicate-evidence defect; never append a second contact or union twice. Distinct candidate witnesses for the same physical pair remain in the evidence list under the single contact identity, deterministically sorted and individually addressable. Contact state is not upgraded by majority vote; contradictory states make that contact unresolved and emit a diagnostic.

```text
for candidate in canonicalCandidatePairs:
    result = robustContactPredicate(candidate)
    id = canonicalContactId(candidate, currentContext)
    if contactMap contains id:
        if canonicalOutcome(contactMap[id]) != canonicalOutcome(result):
            mark id contradictory; retain both evidence records; emit contact-evidence conflict
        else:
            appendUniqueEvidence(contactMap[id], result.evidence)
    else:
        contactMap[id] = canonicalContactRecord(id, result)

for contact in contactMap.values() sorted by contact.id:
    if contact is contradictory: do not union; preserve indeterminate diagnostic
    else if contact.state == positive-area-overlap: union exactly once
    else if contact.state in {boundary-contact, indeterminate}: retain possible edge; do not union
    else: retain separated/invalid/unsupported outcome without conductive union
assert unique(contactMap.keys)
assert each certified union edge references exactly one canonical contact identity
assert contact multiplicity is never used as a physical-contact count
```

This also preserves the Phase 6.0.3 separation of physical graph construction from Net assignment. Unknown Net identity does not suppress a certified physical contact. Geometry uncertainty, invalidity, unsupported geometry, boundary policy, and clearance remain distinct. A contact duplicate cannot create extra independent topology or inflate attribution counts.

## 8. Canonical Stackup ordering contract

### 8.1 Single source of truth

Remove redundant independently stored `copperOrder`, `orderedCopperLayerIds`, and `frontCopperLayerId`/`backCopperLayerId` from the proposed canonical record. The only order source is the array `layersFrontToBack`; array position is the physical order. Copper order is derived by filtering that array to copper layers. Front/back copper identities are derived as the first and last enabled copper entries under the validated Stackup contract; their IDs are not separately stored.

```ts
type StackupLayer = {
  id: LayerId;
  kind: "copper" | "dielectric" | "soldermask" | "silkscreen" | "paste" | "mechanical" | "other";
  name: string;
  enabled: boolean;
  face?: "front" | "back" | "internal"; // required for copper; absent for non-copper
};

type OrderedStackup = {
  id: StackupId;
  revision: number;
  layersFrontToBack: readonly StackupLayer[]; // canonical ordered source; no other order field
};

// Derived after successful validation only:
type ValidatedStackupView = {
  layersFrontToBack: readonly StackupLayer[];
  orderedCopperLayerIds: readonly LayerId[]; // filter, preserving sequence
  copperOrderByLayerId: ReadonlyMap<LayerId, number>; // zero-based derived index
  frontCopperLayerId: LayerId;
  backCopperLayerId: LayerId;
};
```

The derived copper list includes all copper layers in physical order, including disabled layers, so physical indexing remains stable; electrical participation separately requires enabled=true. Face identity (`front`, `back`, `internal`) is explicit metadata checked against physical sequence, not an alternate source of order. Disabled layers remain in the record and in physical/copper order; they cannot host conductive geometry or participate in valid spans. The first/last enabled copper layer identities are derived only after validation. If the intended product semantics require front/back to mean absolute physical outer copper including disabled layers, that definition must be chosen before implementation; until then a disabled outer copper makes face derivation invalid rather than silently skipping it.

### 8.2 Validation rules and unknown/invalid distinction

- Duplicate LayerId: invalid. Duplicate StackupId/revision identity is also invalid within the relevant project scope.
- Duplicate or gapped order indices do not exist in this representation: array position defines unique contiguous zero-based order. A serialized explicit order-index field is rejected as redundant/contradictory rather than used to override array position.
- Any copper layer is automatically in derived `orderedCopperLayerIds`; there is no separately authored copper list that could omit it. If a legacy/imported supplied list exists, compare it with the derived list and mark contradiction invalid; do not trust it as a second source.
- Non-copper layer cannot have a copper face or appear in any imported copper-only list; contradiction is invalid.
- Copper layer requires exactly one face. Front and back markers must agree with validated physical outer copper positions; internal layers cannot claim front/back. Missing face metadata is unknown if the source is incomplete; contradictory face metadata is invalid.
- Disabled copper is retained but cannot carry valid CopperNodes or be a Via endpoint. A Via/Object referencing it is invalid; it is not silently removed from the order.
- Missing Stackup or incomplete layer records is unknown. Duplicate IDs, impossible type/face combinations, inconsistent layer references, malformed order source, or contradictory imported order metadata is invalid.
- A structurally valid Stackup can have zero/one enabled copper layers only if product policy allows such a board; until decided, classify face derivation as unknown/pending validation policy, not as a fabricated front/back pair. Valid-but-disjoint span enumeration remains distinct from unknown and invalid.

No sort by display name, LayerId, or numeric order is performed to repair malformed input. The canonical sequence supplied by the validated Stackup is authoritative.

## 9. Cross-document consistency audit

| Check | Phase 6.0.4 outcome |
|---|---|
| All ViaSpan states have explicit diagnostic outcomes | Yes: §4 covers missing/unresolved, invalid, missing/unverifiable barrel evidence, invalid stage references, indeterminate junction, and unsupported process. Valid disjoint remains normal known-empty intersection. |
| Every Microvia conductive edge has valid stage and junction evidence | Yes as contract: §5 makes exact current-context witness validation a precondition; no other evidence creates an inter-stage edge. |
| Every finding ID has trigger, attribution, dedupe, sign-off behavior | Via diagnostics have all four in §4. Existing Phase 6.0.3 finding contracts remain as stated in its §7 and §10.1; exact severities are pending where specified. |
| Snapshot identity deterministic/reproducible | Yes as proposal: §6 uses canonical JSON, sorted node IDs, contextual revisions/versions and SHA-256. |
| Contact evidence cannot be counted twice | Yes as proposal: §7 uses canonical-keyed upsert and an explicit uniqueness invariant. |
| Stackup has single canonical interpretation | Yes as proposal: §8 uses physical layer array only; all copper ordering and face IDs are derived/validated. |
| NetAssignment remains unchanged | Yes: Phase 6.0.3 §4 states remain exactly `verified`, `unverified-candidate`, `intentional-unassigned`, `expected-but-unassigned`, `unknown`, `invalid`, and `conflicting`; no change is proposed. |
| Geometry outcomes remain distinct | Yes: positive-area overlap, boundary contact, separation, indeterminate, invalid, and unsupported remain separate; tangent electrical meaning remains pending. |
| `PCB_COPPER_CONNECTIVITY_INDETERMINATE` cannot disappear | Yes: Phase 6.0.3 §7 remains, and missing/uncertain Via and Microvia transitions add explicit diagnostics without removing possible connectivity evidence. |
| Definite confirmed shorts survive unrelated uncertainty | Yes: a confirmed component with at least two distinct verified NetIds remains a definite short regardless of unknown annotations or a separate potential contact. |
| Same-Net disconnected islands are not merged by NetId | Yes: Net identity remains post-graph annotation only; island findings compare distinct physical components. |
| v2 `minimumViaClearance` preserves observed projected all-pairs behavior | Yes: no span diagnostic gates or suppresses the v2 comparison. It remains 2D all pairs, outer copper radii, configured clearance, `drill` fallback, per Phase 6.0.3 §§3 and 12. |
| No unapproved product decision introduced | Intended yes; explicit unresolved choices are listed in §11. Proposed fail-closed sign-off expectations are requirements for review, not a final severity decision. |

### 9.1 Finding-contract carry-forward

The existing Phase 6.0.3 rule table (§10.1) remains the contract for short, indeterminate copper connectivity, islands, assignment diagnostics, and geometry diagnostics. Its stated dedup keys and triggers are unchanged. This audit adds no replacement for those IDs. It identifies two implementation-level follow-ups: (a) ensure stale component snapshots are not combined across differing input/kernel/predicate contexts; and (b) add ViaSpan findings from §4 to the final centralized finding registry with exact executable keys and severity mappings before implementation. This is a traceability requirement, not an assertion that any finding currently exists in code.

## 10. Updated adversarial examples for the five corrections

1. **Missing span versus valid disjoint:** Via V1 has a valid front-to-inner span, V2 a valid inner-to-back span with no shared copper layers: result is known-disjoint and no missing-span finding. V3 has no span: emit `PCB_VIA_SPAN_MISSING_OR_UNRESOLVED`; do not treat V3 as disjoint. For a schema-v2 project, still compare V1/V3 under the legacy all-pairs projected `minimumViaClearance` rule.
2. **Barrel evidence absent versus unverifiable:** V4 declares a valid through span but no barrel evidence: `PCB_VIA_BARREL_EVIDENCE_MISSING`, no cross-layer edge. V5 references evidence whose content hash does not match: `PCB_VIA_BARREL_EVIDENCE_UNVERIFIABLE`; no edge. Do not rewrite either as known-disjoint or a valid barrel.
3. **Microvia exact node mismatch:** stages S1 and S2 exist and share copper layer L3. Evidence claims `S1.landA` contacts `S2.landB`, but the witness pair is `{S1.landA,S3.landC}`: assembly is invalid for that junction, finding `PCB_MICROVIA_STAGE_REFERENCE_INVALID`, no edge. A correct pair with stale geometry hash is structurally coherent but connectivity unknown, yielding `PCB_MICROVIA_JUNCTION_INDETERMINATE` and no edge.
4. **Microvia duplicate/reverse/cycle:** records S1→S2 and S2→S1 with the same nodes are a duplicate/reversed record, not two edges; conflicting witness hashes for the same canonical junction key make the record contradictory/invalid. A valid S1→S2→S3 plus S3→S1 cycle is detected; it does not add three independent physical contacts. Process permissibility of a genuine cycle is pending policy.
5. **Snapshot invariance:** the same nodes `{nA,nB,nC}` with edges inserted as `(nA,nB),(nB,nC)` or reversed/reordered and unions performed in any order produce the same sorted membership and ID. Change stackup revision or kernel contract version and the ID changes despite identical membership. This prevents stale evidence from aliasing the current snapshot.
6. **Contact duplication:** one boundary pair is encountered by two broad-phase buckets and produces the same canonical ContactId. Retain one contact outcome, append distinct provenance evidence once, and count one possible contact identity. If the two evaluations disagree on state, retain both proofs, mark contradictory/indeterminate, and do not union; do not count them as two contacts.
7. **Stackup contradictions:** physical sequence is `CuF, Dielectric, Cu1, CuB`, but imported redundant `orderedCopperLayerIds` says `CuF, CuB`: derived list is `CuF, Cu1, CuB`; imported mismatch is invalid and is not silently adopted. A disabled `Cu1` stays at its position but cannot host nodes/span edges. Duplicate IDs or inconsistent front/back face metadata are invalid, not reordered by name.

## 11. Unresolved product-owner decisions and unsupported capabilities

The following remain **PENDING PRODUCT-OWNER DECISION** and are not decided by this audit:

- Severity labels and blocking policy for each ViaSpan diagnostic, Microvia uncertainty, invalid/unsupported geometry, and incomplete DRC coverage; this report recommends no DRC-clear sign-off where connectivity cannot be established, but does not set product severity.
- Which evidence sources and verification authorities qualify as trusted continuous-barrel or process evidence, and whether manufacturing imports can certify them.
- Supported via processes and microvia stage topology, allowable adjacency, stage order, cycles, and stacked/staggered manufacturability constraints.
- Whether nominal boundary/tangent contact is conductive; no junction based only on boundary contact is certified before decision.
- Stable project identity availability and behavior where project identity is absent; no global stable snapshot ID is claimed without it.
- Exact revisioning scheme and obligation to increment input/stackup revisions when relevant geometry or evidence changes.
- Stackup policy for boards with fewer than two enabled copper layers and treatment of a disabled physical outer copper as front/back.
- Rule severities for duplicate/reversed junction records versus cycles that are structurally valid but process-unsupported.
- Existing Phase 6.0.3 unresolved Net authority, conflict, unassigned/unknown semantics, island policy, Padstack support, zone/fill support, geometry/tolerance/kernel guarantees, evidence retention, and v2 migration identity remain unchanged and pending as listed in its §13.

Unsupported means the analyzer must preserve a diagnostic and avoid inferred edges; it is not evidence that geometry is invalid or disjoint. Copper Zones/fills and complex Padstack/custom shapes remain unsupported per Phase 6.0.3 §15 unless separately designed and certified. No implementation capability is claimed.

## 12. Design-readiness verdict

**Suitable for product-owner design review: Yes, conditionally.** This audit supplies a complete proposed contract for the five requested gaps and checks it against the unchanged Phase 6.0.3 Net, contact, graph, island, short, and v2 compatibility contracts. Review must explicitly resolve the pending choices in §11 and the carried-forward Phase 6.0.3 decisions.

**Ready for implementation: No.** Severity mappings, evidence authorities, stage/process policy, identity/revision guarantees, Stackup edge cases, and other Phase 6.0 decisions remain unapproved. No implementation is authorized by this report. Do not start Phase 6.1 or Phase 6.2 without explicit user/product-owner approval.

## 13. Before/after isolation verification

**Before work:** repository remote identified as `soheil6913/-PCB-Studio-Pro`; branch `implementation/phase6-net-aware-drc-20261120`; `HEAD` `6fad0dcdc7e5878e671b8b419b2f61084e5a8138`; clean worktree; `main` `de7497a675af7c6212bbc4751fce098c1f414e8d`.

**After work:** verified repository remote `https://github.com/soheil6913/-PCB-Studio-Pro.git`; branch `implementation/phase6-net-aware-drc-20261120`; `HEAD` still exactly `6fad0dcdc7e5878e671b8b419b2f61084e5a8138`; worktree clean; `main` still exactly `de7497a675af7c6212bbc4751fce098c1f414e8d`. The report is outside the repository. No tests were run. No repository changes were made.
