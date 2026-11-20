# PHASE_6_0_5_MICROVIA_EVIDENCE_TOPOLOGY_CLOSURE

**Status:** Design-only architecture proposal; no implementation is authorized.  
**Scope:** Phase 6.0.5 — Microvia Evidence & Topology Contract Closure.  
**Output location:** `/home/ubuntu/readonly-inspection/PHASE_6_0_5_MICROVIA_EVIDENCE_TOPOLOGY_CLOSURE.md` (outside the application repository).  
**Design Freeze:** NOT APPROVED.  
**Phase 6.1 / 6.2:** Out of scope.

## 1. Executive summary and status

This report consolidates the requested closure design for four gaps: a shared versioned `ContactEvidence`/`ContactWitness` contract; explicit Microvia stage sequencing and exact consecutive-transition validation; a centralized deterministic diagnostic registry with ViaSpan/Microvia arbitration; and independently testable serialized Contact Ledger invariants. It also records compatibility obligations for NetAssignment, physical connectivity, ViaSpan, Stackup, geometry outcomes and schema-v2 `minimumViaClearance`.

The proposed architecture is fail-closed for physical edge admission: only a current, independently validated witness for the exact canonical pair, layer and context, with an eligible positive-area-overlap outcome, can admit a conductive contact edge under the carried-forward Phase 6.0.4 contact rule. A Microvia inter-stage edge additionally requires valid declared consecutive stages and exact ownership of both endpoint nodes. A status label such as `certified`, a NetId, a name, proximity, a stage relationship, or an unverified assertion is not proof. Unknown, invalid and unsupported remain separate states. No unproven edge is admitted; independent valid contacts and confirmed shorts are not erased by unrelated uncertainty.

This document is a design proposal and traceability report, not a claim that any schema, validator, registry, ledger or test exists in application code. Exact wire versions, digest recipes, rule registry entries and some proposed taxonomy require product-owner/architecture approval. The unresolved decisions in §11 remain open. The report does not approve Design Freeze or authorize implementation.

## 2. Provenance, source limits and isolation record

### 2.1 Sources actually reviewed

The following supplied files were read for this synthesis:

1. `/home/ubuntu/upload/PCB_Studio_Pro_—_Phase_6.0(8).md` — the verified Phase 6.0.4 final contract consistency audit. It describes its content as design proposals, lists pending product decisions, and reports a pre-existing audit of Phase 6.0.3 contracts.
2. `/home/ubuntu/upload/pasted_content.txt` — the original Phase 6.0.5 handover/specification, including the requested scope, output requirements and isolation restrictions.

The actual underlying Phase 6.0.3 source contract documents are not present in the supplied materials. In particular, the Phase 6.0.4 attachment references but does not reproduce the original Phase 6.0.3 diagnostic registry (§10.1), Net and physical-connectivity contracts, and cited v2 details. Accordingly, cross-consistency in this report is checked against the explicit carry-forward summaries in the supplied Phase 6.0.4 attachment and the verified attachment itself—not against independent examination of the missing Phase 6.0.3 originals. The summaries are identified as audit-reported carry-forward, not represented as independently verified source wording. No other reports or repository materials are substitutes for the missing originals.

### 2.2 Repository and action record

Read-only checks were performed on the authorized fresh clone immediately before design analysis and repeated after report synthesis:

| Item | Verified result |
|---|---|
| Fresh local clone | `/home/ubuntu/readonly-inspection/pcb-studio-pro` |
| Origin | `https://github.com/soheil6913/-PCB-Studio-Pro.git` |
| Local checkout before and after | Branch `main`; `HEAD` `de7497a675af7c6212bbc4751fce098c1f414e8d` |
| Remote `main` before and after | `de7497a675af7c6212bbc4751fce098c1f414e8d` |
| Worktree before and after | Clean; status and staged/unstaged diff checks showed no changes |
| Phase 6 baseline | `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` present in the clone and contained in remote `verification/phase5-5-drc-policy-certification-20261120` |
| Intended implementation branch | `implementation/phase6-net-aware-drc-20261120` absent from the observed remote branch refs; it was not created |

These checks establish only the state of this authorized fresh clone, not any pre-existing local worktree. No branch was created or switched; no commit, push, PR, merge, rebase, cherry-pick, amend or reset was performed. No repository file or application code was edited. No code tests or builds were run; the Git identity, ref, status and diff checks described above were run read-only. The report itself is written outside the repository at the path in the header.

## 3. Contract status and terminology

The Phase 6.0.4 attachment proposes, among other things, exact Microvia witness validation (§5), canonical contact identity and one-union behavior (§7), canonical Stackup order (§8), and unchanged NetAssignment / v2 behavior (§9). It also explicitly leaves process, evidence-authority, tangent-contact, severity and revision questions pending (§11–12). The original Phase 6.0.5 specification says 6.0.4 was not approved for Design Freeze or implementation and calls the four items above unresolved. Therefore:

- **Audit-reported carry-forward** means a statement expressly summarized or asserted by the supplied Phase 6.0.4 attachment; its underlying Phase 6.0.3 wording was not available for independent verification.
- **Proposed contract** means this report’s design recommendation for closing the Phase 6.0.5 gaps; it is not an approved schema or existing behavior.
- **Current validation result** is computed by revalidating evidence against current objects, revisions, geometry and supported verifier contracts. A persisted assertion alone is not authoritative.
- **Contact identity**, **evidence identity**, **Microvia transition identity**, and **diagnostic occurrence identity** are distinct keys. None is a DSU root or NetId.
- **Physical edge** is an edge admitted to the geometry-derived conductive graph. Net assignment annotates that graph after construction and never creates or suppresses physical contact.

## 4. Invariants retained from Phase 6.0.4

The following constraints are mandatory compatibility requirements in this proposal:

1. **Unknown, invalid, unsupported and known outcomes stay distinct.** A valid disjoint span is known-disjoint, not missing or an empty unknown set. Invalid structure is not reclassified as mere uncertainty. Unsupported capability is not invalid geometry or known separation. `indeterminate` is not `separated`.
2. **No unproven edge.** Missing, stale, unverifiable, unsupported, indeterminate, contradictory or boundary-only evidence (while tangent semantics remain pending) admits no physical edge. An unrelated valid within-stage contact remains valid and is not removed.
3. **NetAssignment is post-graph annotation.** NetId, names, assignment state or same-net claims cannot create, certify, merge, split or suppress physical edges. Same-Net disconnected islands remain disconnected. A verified physical short is not hidden by an unrelated unknown annotation.
4. **Contact outcome distinctions remain explicit.** The geometry outcomes are `positive-area-overlap`, `boundary-contact`, `separated`, `indeterminate`, `invalid` and `unsupported`. Only positive-area overlap is edge-eligible under the audit-reported Phase 6.0.4 §7 rule; boundary/tangent electrical meaning remains pending and is not silently resolved here.
5. **ViaSpan is independent and typed.** Valid disjoint spans are known-disjoint. Unknown, invalid, unsupported or unevidenced spans create no inferred cross-layer edge; none is represented as an empty layer set. ContactEvidence cannot repair a malformed span or establish barrel continuity.
6. **Stackup uses one validated physical order source.** Follow the audit’s `layersFrontToBack` source-of-truth proposal; derive copper order and face interpretation only after validation. Disabled copper layers remain represented but cannot host valid conductive geometry or endpoints. Do not repair inputs by sorting names or IDs.
7. **Schema-v2 `minimumViaClearance` remains independent.** Preserve the audit-reported legacy 2D projected all-pairs comparison of every applicable Via pair, outer-copper radii and `drill` fallback. Span state, graph connectivity, missing/stale evidence or topology validation must not gate, filter, suppress or replace that check.
8. **Confirmed shorts survive unrelated uncertainty.** As summarized by the attachment, a confirmed physical component containing distinct verified NetIds remains a definite short even if a separate contact or annotation is uncertain.

## 5. Canonical, versioned contact evidence contract

### 5.1 Identity model

One contact is a candidate physical relation between exactly two distinct conductive node IDs on one exact copper layer, evaluated under a defined geometry and analysis context. It is not a general relation between stages or nets.

The design separates four identities:

- **`ContactId`:** identifies the canonical unordered node pair, layer and predicate evaluation identity. It is stable for the identity tuple and does not include result, evidence multiplicity, NetId or DSU state.
- **`EvidenceId`:** identifies one immutable evidence/provenance payload or proof contribution for a contact.
- **`MicroviaTransitionId`:** identifies one directed expected stage transition in a declared path/topology revision. Direction is meaningful for transition validation even though the underlying physical contact node pair is unordered.
- **`DiagnosticOccurrenceId`:** identifies one occurrence of one versioned rule in its project/run and context; it is not interchangeable with ContactId or component snapshot ID.

### 5.2 TypeScript-like schema proposal

The following is illustrative and proposed for review. Schema names and versions, exact proof representation, canonical bytes and digest choices must be frozen before implementation.

```ts
type Digest = `sha256:${string}`;
type NodeId = string;
type LayerId = string;
type ContactId = string;
type EvidenceId = string;
type Revision = string;

type ContactOutcome =
  | { kind: "positive-area-overlap"; proof: ProofRef }
  | { kind: "boundary-contact"; proof?: ProofRef }
  | { kind: "separated"; proof: ProofRef; measure?: ExactMeasure }
  | { kind: "indeterminate"; reasonCode: string; detailsDigest?: Digest }
  | { kind: "invalid"; reasonCodes: readonly string[] }
  | { kind: "unsupported"; capability: string; capabilityVersion?: string };

type ProofRef = {
  mediaType: string;
  contentDigest: Digest;
  resolverId: string;
  resolverVersion: string;
};

type ContactContext = {
  schemaVersion: "contact-context/1";
  projectStableId: string;
  inputRevision: Revision;
  stackupRevision: Revision;
  topologyRevision?: Revision;
  graphContractVersion: string;
  predicateId: string;
  predicateVersion: string;
  kernelId: string;
  kernelVersion: string;
};

type ContactBinding = {
  schemaVersion: "contact-binding/1";
  contactId: ContactId;                 // recomputed, not caller-authoritative
  nodeIds: readonly [NodeId, NodeId];   // distinct NFC IDs, bytewise UTF-8 ascending
  layerId: LayerId;                     // exact enabled copper LayerId
  geometryHashes: readonly [Digest, Digest]; // aligned to nodeIds
  context: ContactContext;
  contextDigest: Digest;                // digest of canonical full context
};

type ProvenanceRecord = {
  kind: "computed" | "imported" | "human-assertion" | "derived";
  sourceId: string;
  sourceVersion?: string;
  sourceDigest?: Digest;
  locator?: string;
};

type ContactEvidenceRecord = {
  schemaVersion: "contact-evidence/1";
  evidenceId: EvidenceId;               // digest over canonical evidence payload
  binding: ContactBinding;
  outcome: ContactOutcome;              // observation, never a free-standing boolean
  provenance: readonly ProvenanceRecord[];
  verifier: { id: string; version: string };
};

type ContactWitness = {
  schemaVersion: "contact-witness/1";
  contactId: ContactId;
  evidenceIds: readonly EvidenceId[];    // sorted, unique, resolving references
  outcomeKind: ContactOutcome["kind"];
  validation: {
    state: "verified-current" | "stale" | "unavailable" |
           "unverifiable" | "contradictory" | "invalid" | "unsupported";
    validatedContextDigest?: Digest;
    validationContractVersion: string;
    reasonCodes: readonly string[];
  };
};

type ContactLedger = {
  schemaVersion: "contact-ledger/1";
  projectStableId: string;
  context: ContactContext;
  records: readonly ContactEvidenceRecord[];
  unionApplications: readonly {
    contactId: ContactId;
    nodeIds: readonly [NodeId, NodeId];
  }[];
};
```

`ContactWitness.validation` is derived by the current validator, not imported as a trusted truth. Only a witness with `state: "verified-current"`, exact binding, resolved proof and eligible outcome can be passed to the graph builder. Human assertions and imported evidence may be retained as provenance but cannot alone yield `verified-current`; configured trusted evidence authorities and proof-validation requirements remain open owner decisions.

### 5.3 Deterministic identity and serialization proposal

Normalize all identity-bearing strings to Unicode NFC and require stable, nonempty IDs. Canonicalize the unordered node pair by bytewise UTF-8 ordering after normalization; sort geometry hashes in lockstep with their corresponding node IDs. Distinct raw IDs that collide after normalization are an integrity defect and must be rejected, not silently merged. Do not use names, display text, coordinates, stage order, insertion order or Net assignment to resolve identity.

The carried-forward ContactId inputs in Phase 6.0.4 §7 are: canonical node pair, layer, geometry hashes, input revision, predicate ID/version, and kernel ID/version. A recommended identity object is:

```json
{
  "domain": "pcb-contact",
  "identityFormat": 1,
  "nodeIds": ["canonical-low", "canonical-high"],
  "layerId": "...",
  "geometryHashes": ["sha256:...", "sha256:..."],
  "inputRevision": "...",
  "predicateId": "...",
  "predicateVersion": "...",
  "kernelId": "...",
  "kernelVersion": "..."
}
```

Recommended procedure is RFC 8785 JSON Canonicalization Scheme (JCS) over UTF-8 bytes after NFC normalization, then SHA-256, lower-case hex, prefixed by a versioned form such as `pc1:`. This digest recipe is a proposal, not specified by the supplied source as the ContactId wire format. The identity-format version is separate from evidence serialization schema version.

`contextDigest` additionally binds project identity, Stackup revision/content, graph contract and applicable topology/assembly revision. A change to any bound context makes prior evidence stale even if ContactId inputs reproduce. Whether Stackup/topology revision should be added directly to the ContactId identity tuple or remain freshness-only context is unresolved; this proposal does not silently change the audit-reported tuple. `EvidenceId` should be a domain-separated digest of the canonical evidence record excluding its own ID and including binding, outcome/proof reference, provenance and verifier contract. Exact timestamp policy, proof payload limits, hash algorithm lifecycle and key rotation remain decisions; wall-clock time must not enter ContactId or freshness identity.

Canonical serialized ledgers use only supported schema versions; reject unknown versions unless an explicit version adapter exists. A migration adapter must produce a new canonical record and preserve original schema/provenance. Never reinterpret legacy bytes as `/1` by default. Persisted contact, evidence and union arrays are sorted by documented canonical keys and unique where required; object member order, hash-map iteration, DSU roots and input arrival order have no semantic effect.

### 5.4 Outcome, freshness and edge admission

For each candidate contact, validator must resolve both exact node IDs, project, layer, geometry snapshot, enabled copper membership, current input and Stackup revisions, graph contract, predicate/kernel versions, evidence objects and proofs. Missing sources are unavailable/unknown. Impossible or contradictory ownership is invalid. A formerly coherent witness whose bound revision or hash no longer matches is stale, not separated. Unsupported predicate/evidence capability remains unsupported.

Recompute geometry hashes and all identity digests. Resolve immutable proof references and verify content digest, verifier identity/version, exact node-pair/layer/context binding and declared outcome. A false `certified` label is not proof. Do not infer separation from failed proof, missing object or stale hash.

Graph builder admits one undirected contact edge only when the shared witness is current, exact-binding, noncontradictory, evidence-valid, and `positive-area-overlap`. Boundary contact remains a retained outcome but is not conductive while tangent policy is pending. `separated`, `indeterminate`, `invalid` and `unsupported` yield no edge. A stale/unavailable witness yields no edge and is not rewritten as any geometric outcome. A failure on one contact does not erase independently valid edges.

## 6. Strict Microvia stage topology and junction validation

### 6.1 Topology schema proposal

The stage path must be declared by an explicit authoritative ordered sequence, not inferred from arbitrary array order, names, coordinates, layer numbering or junction arrival order. The sequence source and process semantics need owner approval. The following illustrates a sequence-based model without deciding whether other topology models are permissible:

```ts
type StageId = string;
type CopperNodeId = string;
type TopologyId = string;

type MicroviaStage = {
  id: StageId;
  fromLayerId: LayerId;
  toLayerId: LayerId;
  memberNodeIds: readonly CopperNodeId[];
};

type MicroviaPath = {
  schemaVersion: "microvia-path/1";
  id: TopologyId;
  topologyRevision: Revision;
  orderedStageIds: readonly StageId[]; // authoritative directed progression
  continuityClaim: "continuous" | "non-continuous";
};

type MicroviaJunction = {
  schemaVersion: "microvia-junction/1";
  pathId: TopologyId;
  topologyRevision: Revision;
  ordinal: number;
  fromStageId: StageId;
  toStageId: StageId;
  fromNodeId: CopperNodeId;
  toNodeId: CopperNodeId;
  contactLayerId: LayerId;
  witness: {
    contactId: ContactId;
    evidenceIds: readonly EvidenceId[];
  } | { state: "missing" | "unsupported"; reasonCode?: string };
};
```

For a continuous ordered path `[s0, …, sn]`, expected transitions are exactly `[(s0,s1), (s1,s2), …, (s(n-1),sn)]`. If a serialized transitions mirror is added later, it is checked against that derivation element-by-element and is not a second source of truth. Each stage and node reference must be unique within its declared scope unless an approved model explicitly permits sharing. Each junction’s endpoint nodes must be distinct, conductive, resolved, and owned by the declared `fromStageId` and `toStageId`; their exact current layer ownership must match the declared compatible common copper layer and validated Stackup.

A directed transition identity may be `(pathId, topologyRevision, ordinal, fromStageId, toStageId)`. Reversal detection uses a canonical unordered stage-pair key plus canonical unordered node-pair/layer/ContactId. Preserve direction for coverage checks; canonical unordered keys are for duplicate detection only. Do not conflate transition identity with physical ContactId.

### 6.2 Exact deterministic validation algorithm

For each project analysis snapshot:

1. **Freeze and validate context.** Capture input/topology revisions, validated Stackup and enabled copper layers, current node geometries/hashes, graph contract and supported predicate/kernel/evidence versions. Missing/incomplete source is unknown. Duplicate IDs, impossible type/layer ownership or contradictory serialized topology is invalid. Do not repair by sorting names or IDs.
2. **Validate path declaration.** For each continuous path, require a supported topology version, unique resolvable StageIds, explicit `orderedStageIds`, and a valid declared continuity claim. Derive expected consecutive pairs strictly from sequence positions. Do not infer order from other arrays or junction graph. If transition mirrors are present, require exact equality to the derivation; reject omissions, extras, reversals, duplicates and permutations.
3. **Validate Stackup and stages.** Require each stage endpoint to resolve under a valid Stackup to enabled copper layers, distinct where the model requires; validate process-specific endpoint constraints only if approved. Disabled copper cannot host a valid node or Via endpoint. Unsupported process is classified unsupported, not invalid.
4. **Build unique ownership indexes.** Construct `stageById`, `nodeById`, and stage-membership maps. Reject duplicate StageIds, duplicate conflicting node membership, dangling references and impossible duplicate ownership under the approved model. Resolve all endpoint nodes; require conductive copper geometry and exact declared stage ownership. A stage name or shared label cannot prove ownership.
5. **Check each junction’s structure.** Require from/to stages to exist and differ; each node to exist, differ from the other node, and belong to its corresponding stage; contact layer to resolve to the exact compatible enabled copper layer; the junction stage pair to match one expected directed consecutive transition. Nonconsecutive chords do not cover any expected transition. A field contradiction is invalid and admits no affected edge.
6. **Group duplicate/reversed records deterministically.** Retain original direction. Group by path/revision, canonical unordered stage pair, canonical unordered node pair, layer and ContactId. Exact duplicate serialized entries are duplicate ledger/topology records, not extra contacts. A reversed record alone does not satisfy the expected directed transition. A correct and reversed duplicate pair contributes at most one accepted edge and receives deterministic duplicate/reversal attribution. Validate evidence on every candidate before deduplication. Contradictory same-key evidence is retained, not voted or first/last-wins. If distinct node pairs claim one transition and no approved multiplicity policy exists, mark ambiguity/unresolved and admit none.
7. **Resolve shared ContactWitness.** Resolve exactly one canonical evidence identity for the exact node pair and layer. Validate version, canonical pair, ContactId recomputation, current geometry hashes in node order, current input/Stackup/topology/graph/predicate/kernel context, immutable evidence digests, proof resolver and supported authority. Witness assertion is not trusted without verification. Wrong node pair, wrong layer or impossible ownership is invalid. Stale hash/revision is unknown-stale. Missing/unavailable proof is unknown/unverifiable. Unsupported format/process is unsupported.
8. **Classify geometry without collapsing results.** Only verified-current `positive-area-overlap` is eligible for a contact edge. `boundary-contact` is retained but non-edge pending tangent policy. `separated` is known absence for that exact pair; if it is a required transition in a path claimed continuous, the path remains incomplete. `indeterminate`, missing, stale or unverifiable is unknown. Invalid and unsupported retain their distinct classifications. No record is upgraded by duplicate count or majority vote.
9. **Enforce coverage.** Every required consecutive pair of a continuous path must have exactly one unambiguous accepted junction identity to count as confirmed. Zero qualifying records means missing/unknown transition; nonconsecutive or reversed-only records do not cover it. More than one distinct candidate is unresolved absent approved multiplicity semantics. Non-continuous paths are not forced to have full-chain evidence, and no new error is invented solely because they have no junctions.
10. **Detect cycles and other graph anomalies separately.** Detect cycles/branches deterministically in the declared stage graph. Cycles do not create physical edges, excuse missing consecutive transitions, or add multiplicity. Whether cycles are invalid, unsupported or process-permissible remains a product decision. Do not infer a path by traversing junction insertion order.
11. **Emit only after validation.** Emit one inter-stage graph edge per unique ContactId associated with an exact expected transition and verified-current witness. Preserve independently valid within-stage edges and other valid contacts. Deduplicate by ContactId and assert one union per contact identity. NetAssignment has no role in edge admission.
12. **Deterministic output.** Sort canonical records/findings by normalized UTF-8 keys while preserving semantic sequence order where meaningful. No timestamps, input order, DSU root, traversal order or majority vote affects acceptance or identity. Re-running on identical canonical inputs yields byte-identical result.

### 6.3 Classification of required error/evidence cases

| Case | Classification and topology effect |
|---|---|
| Missing expected consecutive transition/evidence | Unknown/incomplete continuity; no edge. |
| Reversed-only stage transition | Does not satisfy directed expectation; no edge; expected transition remains missing/unknown. |
| Exact duplicate/reversed duplicate | One record identity at most; duplicate reported; at most one edge/union. |
| Nonconsecutive transition/chord | Invalid reference/topology candidate; covers no expected pair; no edge. |
| Duplicate stage ID, dangling node, wrong stage ownership, impossible layer | Invalid structure; offending edge excluded; independent valid contacts retained. |
| Stale geometry/context/hash | Unknown-stale; no edge; preserve stale provenance. |
| Missing/unavailable/untrusted proof | Unknown/unverifiable; no edge. |
| Explicitly unsupported evidence format/process | Unsupported; no edge; independent checks continue. |
| Conflicting current evidence for one identity | Preserve all; contradictory; no edge; no majority vote. |
| Boundary-only witness | Boundary remains explicit; no edge pending tangent policy. |
| Cycle | Detect; no extra physical edge. Permissibility/severity undecided. |
| `separated` witness for required transition | Known non-contact for pair; claimed continuous path remains incomplete. |

## 7. Contact Ledger serialization and independent invariants

### 7.1 Serialized ledger validation

The ledger is an independently readable contract, not merely an in-memory product of graph construction. A separate reader must be able to parse it, recompute identities, resolve evidence, validate freshness and verify union applications without trusting producer state or DSU roots.

Recommended validation procedure:

1. Parse strict UTF-8 JSON. Reject malformed JSON, duplicate object member names, unsupported schema versions, malformed digest encodings, missing required fields and unrecognized versions absent an explicit adapter. Validate types without coercion.
2. Validate project/ledger context and require each record’s context to agree. Resolve exact nodes, layer, geometry snapshot, current input, Stackup, predicate/kernel and graph contract. Missing objects/snapshot are unavailable/unknown; contradictions are invalid.
3. Normalize identity strings to NFC; reject empty IDs and normalization collisions. Require node IDs distinct and serialized pair already bytewise UTF-8 ascending. Require geometry hashes aligned with that pair; reversed pair with unswapped hashes fails.
4. Recompute ContactId and context digest from canonical identity/context. Mismatch is an integrity error. Recompute current geometry hashes; mismatch is stale, never separated. Validate current enabled copper layer and both node ownership facts.
5. Validate evidence records: supported schema/kind, unique EvidenceId, exact ContactId subject, canonical payload digest, immutable proof resolution, verifier/authority contract and all reference targets. Missing/unavailable proof means no union. Same EvidenceId with different content is an integrity contradiction.
6. Validate uniqueness before normalization can hide a defect. Repeated persisted ContactId or EvidenceId is reported as duplicate even if payload bytes match. Byte-identical duplicate input may only be normalized by an explicit deterministic ingestion adapter before persistence; persisted malformed ledger is rejected, never first/last-wins.
7. Group by recomputed ContactId. Distinct validated provenance records may be retained in sorted order for one contact. Contradictory current outcomes or contexts preserve all claims and mark contact contradictory; no majority vote and no union. Stale records cannot be merged as current evidence.
8. Recompute the eligible contact set. Validate `unionApplications` has one existing unique ContactId for each and only each eligible contact, exact matching canonical pair, current witness and eligible outcome. Reject duplicate, dangling, extra-ineligible, mismatched-pair or omitted union identities. Maintain `appliedContactIds`; a repeated DSU request is idempotent but diagnosed, and never produces a second union/contact count. Two distinct eligible contacts remain distinct witnesses even if their endpoints are already in the same DSU component.
9. Preserve independent valid edges despite unrelated invalid/unknown records. Never let NetId create or suppress union.
10. Require canonical ordering: contact records by ContactId; evidence/provenance and reference arrays by documented stable keys; union applications by ContactId. Preserve meaningful ordered topology. Canonical serialization is RFC 8785/JCS UTF-8 after NFC under the proposed format. No timestamps, insertion indexes, hash-map order, traversal order, DSU root or Net assignment enter identity.
11. Round-trip the canonical serialization through an independent reader; identical canonical input must reproduce byte-identical output and findings. Do not claim test execution here.

### 7.2 Testable ledger invariants

- **Unique contact IDs:** exactly one persisted record per ContactId; duplicate records are defects, not multiplicity.
- **Canonical pair:** each pair consists of exactly two distinct normalized IDs, ascending by canonical byte order; associated hashes follow the same order.
- **Evidence integrity:** every EvidenceId recomputes; each digest resolves to immutable content; all references bind the claimed contact, pair, layer and context.
- **Freshness:** geometry hashes and revisions match the current snapshot. A stale record cannot qualify or be silently rewritten as separated/current.
- **Outcome consistency:** contradictory same-ID evidence remains visible and blocks union; no first/last/majority selection.
- **Union uniqueness:** each unique qualifying ContactId is applied at most once; union request set exactly equals independently computed eligible set.
- **Determinism:** order permutations of equivalent inputs produce byte-identical canonical ledger/findings; DSU roots and operation order do not affect output.
- **Separation of identities:** ContactId, EvidenceId, TransitionId, component snapshot ID, diagnostic occurrence ID and NetId are not interchangeable.

## 8. Central diagnostic registry and arbitration

### 8.1 Registry model and occurrence identity

Every diagnostic rule should be centrally registered with stable `ruleId`, `semanticsVersion`, canonical owner, allowed producers, subject kinds, trigger contract, attribution fields, canonical dedupe-field specification, prerequisites, any explicitly permitted causal precedence, severity/sign-off policy reference and compatibility version. Validators submit structured candidates; the registry normalizes, validates, arbitrates and finalizes them. Unregistered IDs, duplicate registration, conflicting definitions or missing owners are registry-integrity failures—not opportunities for a validator to invent a finding.

Proposed occurrence identity is a domain-separated canonical object containing rule ID, semantics version, project scope (stable project ID or explicitly run-local identity), and only the prescribed normalized occurrence fields for that rule. Recommend NFC + RFC 8785 JCS + SHA-256 (`diag1:<lowercase hex>`). Producer, display text, severity, timestamps, enumeration order, DSU root, NetId and evidence arrival order are excluded unless a rule explicitly identifies an evidence/context digest as part of its prescribed occurrence key. Store all evidence and producer references separately, sorted and addressable.

Coalesce compatible duplicates for the same rule and occurrence key, retaining sorted unique provenance/evidence. If identity-bearing payloads conflict, retain all conflicting records deterministically, flag registry/evidence conflict and do not select a winner. A user-facing conflict finding may be emitted only if registered; do not invent unapproved product IDs. Across distinct rule IDs, retain both unless the central registry explicitly states that one same-cause finding subsumes another because it restates no separate guarantee. Precedence is causal/validation ordering, not severity ranking.

### 8.2 Trigger, ownership and precedence table

The ViaSpan/Microvia finding IDs and base triggers below are carried forward as described in Phase 6.0.4 §4.1; the audit itself calls severities pending. Candidate contact-ledger/contact-evidence IDs are proposals only and must be reconciled with the missing Phase 6.0.3 registry. Proposed ownership/arbitration is not approved policy.

| Rule / status | Trigger and canonical owner | Stable attribution/key inputs | Precedence and edge effect |
|---|---|---|---|
| `PCB_VIA_SPAN_MISSING_OR_UNRESOLVED` (audit-reported) | Required span absent/unresolvable, Stackup unavailable, or endpoint unresolved. ViaSpan validator. Not triggered by two valid disjoint spans. | Project, Via ID, span digest or `MISSING`, known endpoints/layers, Stackup revision or `UNKNOWN`. | No inferred cross-layer edge. v2 clearance runs. Suppress only derivative Microvia uncertainty that merely restates this exact root defect, if registry policy approves. |
| `PCB_VIA_SPAN_INVALID` (audit-reported) | Malformed/contradictory span, bad endpoint/kind/order/duplicate-stage/Stackup reference. ViaSpan owner for span fields. | Project, Via ID, span digest, endpoint IDs, sorted codes, Stackup revision. | No span edge; do not also call same defect “missing.” A distinct assembly defect may remain separate. |
| `PCB_VIA_BARREL_EVIDENCE_MISSING` (audit-reported) | Required continuous-barrel proof reference absent. ViaSpan evidence owner. | Project, Via ID, span/kind/endpoints, evidence role and span digest. | No barrel edge; distinct from unverifiable proof. |
| `PCB_VIA_BARREL_EVIDENCE_UNVERIFIABLE` (audit-reported) | Evidence exists but unavailable, hash-mismatched, untrusted or fails to prove full-span continuity. Evidence resolver/ViaSpan owner. | Via ID, EvidenceId/content hash/source, endpoints, resolver/status and context digest. | No inferred barrel edge; distinct from absent proof. |
| `PCB_MICROVIA_STAGE_REFERENCE_INVALID` (audit-reported) | Duplicate/dangling/equal stage references; invalid endpoint; absent, duplicated or wrongly owned node; impossible layer; contradictory topology. Microvia assembly owner. | Via, assembly/path, stage/junction IDs, sorted stage/node/layer references, validation codes. | No affected inter-stage edge. Do not also emit indeterminate solely because this same structural root prevents witness evaluation. Via-level span defect belongs to ViaSpan owner. |
| `PCB_MICROVIA_JUNCTION_INDETERMINATE` (audit-reported) | Structurally valid expected transition but missing, stale, not-connected, indeterminate, uncertified or unprovable exact-pair/current-context evidence. Microvia evidence owner. | Via, directed expected transition, canonical node pair or `UNKNOWN`, layer or `UNKNOWN`, current context digest and reason. | No junction edge. Not a cascade from structural invalidity; not a rewrite of unsupported or valid-disjoint. |
| `PCB_VIA_PROCESS_UNSUPPORTED` (audit-reported) | Well-formed identifiable process outside supported/validated set. Capability/process owner. | Via, process token/digest, stages if known, capability registry version. | Unsupported; no inferred edge. Independent geometric and v2 checks continue. |
| `PCB_CONTACT_EVIDENCE_SCHEMA_INVALID` (candidate) | Unsupported/malformed evidence schema, required-field/type/encoding failure. Contact evidence validator. | Project, ledger digest, record identity, schema version, sorted validation codes. | Reject record; no edge. Rule ID/severity pending registry approval. |
| `PCB_CONTACT_EVIDENCE_IDENTITY_MISMATCH` (candidate) | Recomputed ContactId/EvidenceId/context digest differs, or normalization collision/ID-content collision. Identity validator. | Claimed ID, recomputed binding/context, project and rule version. | Integrity defect; no edge; do not dedupe away conflict. |
| `PCB_CONTACT_EVIDENCE_STALE` (candidate) | Coherent evidence has stale geometry, input/Stackup/topology revision, graph, predicate or kernel context. Freshness validator. | ContactId, current context digest, EvidenceIds. | Unknown/stale; no edge; preserve old evidence. |
| `PCB_CONTACT_EVIDENCE_UNVERIFIABLE` (candidate) | Missing/unavailable/untrusted proof or verifier cannot substantiate outcome. Evidence verifier. | ContactId, proof digest/resolver and current context. | No edge; unknown/unverifiable, not separated. |
| `PCB_CONTACT_EVIDENCE_CONFLICT` (candidate) | Current evidence for one identity disagrees on outcome, binding or proof. Shared evidence/ledger owner. | ContactId, sorted conflicting EvidenceIds and context. | Preserve all; no union; one canonical occurrence despite multiple producers. |
| `PCB_CONTACT_OUTCOME_INDETERMINATE` / `PCB_CONTACT_GEOMETRY_UNSUPPORTED` (candidate) | Robust predicate undecidable / declared capability unsupported. Geometry owner. | ContactId, predicate/kernel or capability/version and context. | Preserve distinct outcome; no edge. Registry must not collapse with invalid or separated. |
| `PCB_CONTACT_BOUNDARY_POLICY_UNRESOLVED` (candidate) | Boundary-only result while tangent electrical policy remains open. Contact policy owner. | ContactId, predicate version and context. | Retain boundary; no edge pending decision. |
| `PCB_CONTACT_LEDGER_DUPLICATE_ID` (candidate) | Repeated persisted ContactId or EvidenceId. Ledger reader. | Ledger digest, duplicate ID and schema version. | Serialized ledger invalid; no first/last-wins. |
| Phase 6.0.3 finding contracts (audit-reported only) | Existing short, indeterminate connectivity, island, assignment and geometry rules remain as summarized in attachment §9.1; original table unavailable. | Import exact IDs/triggers/keys from original §10.1 when available; do not guess. | Preserve audit-reported definite-short, no NetId island merge, and geometry distinctions. |

If one invalid Via span field is reported by both ViaSpan and Microvia validators, central registry should designate one canonical owner for that field-level occurrence and permit the other validator only to reference/coalesce it. If there are distinct failed guarantees—e.g., invalid Via-level span plus an independent well-formed but stale junction witness—retain distinct findings. Only suppress a dependent uncertainty finding when it would solely restate the exact structural/root defect; never suppress independent clearance checks, definite shorts or separate evidence failures. Exact cross-validator ownership and cascade suppression require approval.

## 9. Cross-document consistency and explicit limitations

The following consistency checks are against statements in the verified Phase 6.0.4 attachment and the original Phase 6.0.5 specification. They are not independent validation of absent Phase 6.0.3 source contracts.

| Contract area | Compatibility obligation in this report | Provenance qualification |
|---|---|---|
| NetAssignment / physical graph | Graph is geometry/evidence-derived; assignment is post-graph annotation. NetId cannot create/suppress an edge or merge same-Net disconnected islands. | Asserted in supplied audit §§7, 9.1 (including its summary of prior states); original §7 source unavailable. |
| Confirmed shorts | Distinct verified NetIds in one confirmed physical component remain a definite short despite unrelated unknown annotations. | Carried forward by supplied audit §9.1; not independently checked against original source. |
| Geometry outcomes | Preserve positive-area overlap, boundary contact, separated, indeterminate, invalid and unsupported. Boundary/tangent semantics remain pending. | Explicit audit §§7, 9.1 and 11. |
| ViaSpan | Valid disjoint is known-disjoint; unknown/invalid/unsupported/unevidenced spans create no inferred cross-layer edge. Contact evidence does not repair ViaSpan/barrel evidence. | Explicit audit §§4.1–4.2; details remain proposed in that audit. |
| Stackup | Use the validated physical sequence and enabled-layer constraints; do not infer/sort order from labels. | Explicit audit §8, itself described as a proposed contract. |
| Microvia | Only exact current-context witness for exact node pair/layer, correctly owned by referenced stages, can support the required transition. | Explicit audit §§5.1–5.2; 6.0.5 adds strict sequence source closure without presuming unresolved process policy. |
| Contact ledger | One canonical contact identity; evidence retained; contradictory same-identity outcomes do not union; union once. | Explicit audit §7 algorithm; this report adds proposed independent serialized invariants. |
| Schema-v2 clearance | Keep `minimumViaClearance` projected 2D all-pairs with outer copper radii and drill fallback, irrespective of spans/contact topology. | Explicit audit §§4.2 and 9.1, which cite absent Phase 6.0.3 §§3/12 for details. |
| Diagnostic registry | Centralize ViaSpan additions alongside earlier rules; do not replace absent earlier IDs. | Audit §9.1 explicitly calls for registry follow-up; original registry unavailable. |

An important scope ambiguity remains: the Phase 6.0.5 specification demands strict sequence and consecutive transitions, while audit §5.2 says not to infer intended sequence from array order and leaves process adjacency/cycles pending. These are compatible only if an authoritative explicit sequence contract and its semantics are approved. Until then, the validator must not invent order, missing transitions, adjacency or process invalidity from incidental serialization. A further freshness question is whether Stackup and Microvia assembly revisions must appear directly in ContactId or only in the witness context digest; this report requires freshness coverage but leaves identity-format placement unresolved.

## 10. Adversarial test matrix and expected results

These are required proposed tests/acceptance criteria. No tests were executed for this report.

| # | Adversarial input or permutation | Expected result |
|---:|---|---|
| 1 | Pair serialized `{B,A}` versus `{A,B}` with hashes permuted consistently | Same canonical identity after explicit normalization; persisted noncanonical pair is rejected by strict ledger reader. |
| 2 | Reverse pair but do not reverse geometry hashes | Binding/identity mismatch; no edge. |
| 3 | Equal node IDs; NFC-colliding raw identifiers; malformed digest | Invalid schema/identity; reject, never coerce or merge. |
| 4 | Change geometry, input revision, layer, predicate/kernel version | Contact identity changes where in the defined identity tuple; old evidence is stale under current context and never admitted. |
| 5 | Change Stackup/topology/graph context while identity tuple remains same | ContactId may remain the same under the proposed tuple, but context digest differs; old evidence is stale and cannot join current graph. |
| 6 | Forged `certified` label with no resolvable proof or wrong digest | Unverifiable/integrity failure; no edge. |
| 7 | Correct stage pair but witness names different node pair or wrong layer | Structural/witness mismatch; invalid affected junction; no edge. |
| 8 | Correct pair/layer, stale node hash or prior analysis context | Unknown-stale; no edge; stale provenance retained. |
| 9 | Missing/unavailable verifier versus explicitly unsupported evidence format | Unknown/unavailable in first case; unsupported in second; neither creates edge. |
| 10 | Expected `A→B`, evidence only `B→A` | Reversed record does not satisfy transition; missing/unknown `A→B`; no edge. |
| 11 | Same directed transition appears byte-identically twice | Duplicate reported; one canonical transition/contact at most; one union maximum. |
| 12 | Forward/reverse copies with conflicting hashes/outcomes | Deterministic conflict; retain both; no majority/arrival-order winner; no edge. |
| 13 | Ordered stages `[A,B,C]`, only `A→C` junction | `A→C` nonconsecutive; `A→B` and `B→C` remain missing/unknown; no shortcut edge. |
| 14 | Serialized transition mirror omits, adds, reverses or permutes a consecutive pair | Invalid mirror; do not repair/sort it. |
| 15 | Duplicate StageId, dangling stage/node, wrong node ownership, incompatible layer | Invalid topology/reference; no offending edge; independent valid contacts retained. |
| 16 | Cycle `A→B→C→A` | Deterministically detected; cycle does not add edge or excuse missing consecutive coverage; process permissibility left pending. |
| 17 | Multiple different node pairs claim one expected transition | Ambiguous/unresolved absent approved multiplicity policy; no first-wins and no multiplicity-based unions. |
| 18 | One ContactId with same outcome and distinct validated evidence refs | One contact; all unique references retained in canonical order; one union maximum. |
| 19 | Same ContactId has overlap vs separated outcomes | Contradictory; retain both; no union; output independent of record order. |
| 20 | Persisted duplicate ContactId/EvidenceId rows, even byte-identical | Serialized ledger duplicate defect; cannot disappear by sorting/dedup before validation. |
| 21 | Evidence reference dangling, subject ContactId wrong, payload hash altered | Integrity/reference failure; no union. |
| 22 | Duplicate, dangling, mismatched-pair, extra-ineligible or missing unionApplication | Ledger invariant fails; invalid entry cannot create a DSU edge. |
| 23 | Broad phase/evaluator submits same contact twice; DSU sees same ContactId twice | One application keyed by ContactId; second request idempotent/diagnosed; never extra contact count. |
| 24 | Two different valid ContactIds connect nodes already in same DSU component | Preserve two distinct certified contacts; DSU membership does not collapse witness identity. |
| 25 | Boundary-only contact | Boundary outcome preserved; no edge until tangent policy is approved. |
| 26 | Separated versus indeterminate versus invalid versus unsupported fixture | Each exact state remains distinguishable; only separated establishes known absence; none creates an edge. |
| 27 | Same NetId but no qualifying contact; different NetIds with qualifying contact | First stays physically disconnected; second physical edge remains; assignment cannot alter graph. |
| 28 | Definite short plus unrelated unknown/stale contact | Definite short remains; uncertainty is separately diagnosed. |
| 29 | Valid disjoint ViaSpans versus missing/unknown spans | Disjoint is known-disjoint; missing/unknown is not an empty set; no inferred edge for uncertain span. |
| 30 | v2 clearance violation with missing, invalid or stale span/contact evidence | All applicable Via pairs still enter projected all-pairs clearance; independent clearance finding remains. |
| 31 | Reorder records, evidence refs, object properties, candidate inputs, broad-phase buckets and DSU unions | Canonical ledger/findings and decisions byte-identical; meaningful path sequence remains ordered. |
| 32 | Missing stable project identity | Identity marked run-local/unknown per approved policy; no false global dedup claim. |
| 33 | Unsupported process plus independently valid within-stage contact | Unsupported transition creates no edge; independent within-stage physical edge remains. |
| 34 | Same root defect emitted by ViaSpan and Microvia validators; then add a separate stale witness defect | One centrally owned occurrence for shared root; retain separately the distinct stale evidence failure if its prerequisites are valid. |

All tests should also assert that each accepted graph edge references exactly one unique eligible ContactId and that every ineligible outcome generates zero unions. Finding identity and deterministic attribution should be tested independently of pending severity/sign-off policy.

## 11. Unresolved product-owner / architecture decisions

No choice below is made by this report:

1. Which evidence proof formats, authorities, resolvers and imported manufacturing sources are trusted; whether cryptographic validation or geometry re-evaluation is required; evidence retention/privacy/size constraints.
2. Whether nominal boundary/tangent contact conducts, and approved numerical tolerance, robust/exact predicate semantics and kernel guarantees.
3. Exact revision obligations for geometry, input, Stackup content, topology/assembly/process, graph contract, predicate/kernel and imported evidence. Whether Stackup/topology revision is identity-bearing or freshness-only.
4. Whether `projectStableId` is mandatory for global IDs and how run-local behavior works if unavailable.
5. Exact ContactEvidence/ContactWitness, ContactLedger and topology wire versions, canonical byte encoding, digest algorithms/prefixes, geometry-hash representation/precision/units/curve normalization, migration adapters and cross-version equivalence policy.
6. Explicit source of Microvia stage sequence; whether an ordered path is sufficient or a DAG/branch topology is needed; allowable adjacency, skip-via semantics, branches, multiple contacts per transition, shared stages/nodes, orphan stages and non-continuous path representation.
7. Whether genuine cycles are structurally forbidden, unsupported or process-permissible; whether transition direction is physically meaningful or only declared progression.
8. How distinct but same-context proof sources with equivalent outcomes combine, and whether imported/human provenance can contribute to current verification.
9. Registry rule IDs for new Contact rules, canonical ownership between ViaSpan and Microvia validators, precedence/cascade suppression, exact attribution/dedupe fields and conflict handling when no product-facing conflict rule exists.
10. Severity, blocking, DRC-clear sign-off, aggregation caps and user-facing wording for each diagnostic; audit §11 explicitly leaves these pending.
11. Whether identical persisted duplicates are always rejected versus normalized only at a deterministic ingestion boundary; this report recommends reject persisted duplicates.
12. Complete reconciliation of the proposed identity/diagnostic/ledger contracts against the actual Phase 6.0.3 originals, including original NetAssignment, geometry, island, short, v2 and finding-table details.

## 12. Readiness verdict

**Design review readiness:** Suitable as a focused proposal for independent and product-owner review, with the stated provenance limits.  
**Design Freeze:** **NOT APPROVED.** The explicit evidence contract, topology sequence authority, diagnostic registry ownership and serialized ledger rules remain proposals, and unresolved decisions in §11 require owner resolution. Full cross-document verification against the missing Phase 6.0.3 originals is still required.  
**Implementation readiness:** **NOT READY / NOT AUTHORIZED.** No implementation, branch change, repository edit, test or build is included or authorized by this report.  
**Phase 6.1 / 6.2:** Out of scope; do not begin under this report.

The design is compatible with the Phase 6.0.4 invariants when its recommendations are adopted without weakening exact evidence checks, outcome distinctions, physical-vs-Net separation, or independent v2 clearance. That compatibility is conditional and does not establish approval of the prior contracts or the proposed additions.
