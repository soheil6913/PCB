# PCB Studio Pro — Phase 6.0.6
## Final Evidence, Microvia Process & Contact Ledger Contract Closure

**Status:** Design-only contract proposal; no implementation is authorized.  
**Design Freeze:** **NOT APPROVED.**  
**Implementation readiness:** **NOT READY / NOT AUTHORIZED.**  
**Phase 6.1 / 6.2:** Out of scope; do not begin under this report.

## 1. Scope and source basis

This report closes the Phase 6.0.6 design questions for ContactEvidence certification and proof validation, Microvia manufacturing-process evidence, separate serialized Contact Ledger collections, and diagnostic ownership across ViaSpan and Microvia validators. It proposes contracts and expected adversarial outcomes. It does not claim that these contracts exist in application code, and it does not authorize implementation, testing, repository changes, or Design Freeze.

The original Phase 6.0.3 document was accessible and reviewed at its original content, including its NetAssignment and graph rules, six contact-geometry states, ViaSpan/Microvia representation, historical diagnostic table, v2 clearance behavior, and remaining product decisions. This resolves the earlier Phase 6.0.5 report’s stated limitation that the original 6.0.3 source was then unavailable. The verified Phase 6.0.4 attachment was also reviewed; its title and content match the original audit. The 6.0.5 reference is treated as a proposal to reconcile, not as approval of its suggested wire formats, diagnostic registry, or policy choices. [1] [2] [3]

The governing compatibility principles remain: Net assignment is separate from physical connectivity; same-Net identity never creates an edge; a confirmed physical component with multiple distinct verified NetIds remains a definite short; uncertain contacts cannot disappear; valid-disjoint Via spans remain distinct from unknown or invalid spans; Stackup ordering is canonical; the legacy v2 `minimumViaClearance` remains projected 2D all-pairs clearance; geometry states are not approximated or collapsed; and no pending product decision is silently resolved. [1] [2] [3] [4]

## 2. Contract status and identity boundaries

The proposals below distinguish identities that must not be substituted for one another:

- **`ContactId`** identifies one canonical unordered pair of distinct copper nodes, one enabled copper layer, the pair’s aligned geometry hashes, input revision, and the predicate/kernel identities and versions used for that contact evaluation. This carries forward the original 6.0.3/6.0.4 tuple. A broader context digest binds project, Stackup, topology, graph, and other current-analysis context for freshness. Whether every context revision also belongs in the ContactId preimage remains unresolved. [1] [2] [3]
- **`EvidenceId`** identifies one immutable evidence contribution. Several EvidenceIds may reference the same ContactId. Evidence multiplicity is not contact multiplicity and cannot produce multiple graph unions.
- **Authority, verifier, resolver, capability, and proof-format identities** name who issued or asserted a proof, which implementation/version checked it, how immutable bytes are resolved, and which semantics the proof format claims. None is a ContactId or EvidenceId.
- **`DiagnosticOccurrenceId`** identifies one registered rule occurrence under a rule semantics version and its prescribed attribution fields. It is not a contact, evidence, stage-transition, component-snapshot, or Net identity.
- **NetId** annotates the graph after physical edges are established. It cannot create, certify, merge, split, or suppress physical connectivity. [1] [2]

A serialized `certified`, `trusted`, `valid`, or equivalent Boolean is an assertion only. The current validator derives certification status after checking the proof, authority, verifier contract, exact contact binding, provenance, integrity, and current context. A digest proves neither authority nor the truth of the payload’s geometry claim. [1] [2] [3]

## 3. ContactEvidence, certification, and proof resolver

### 3.1 Geometry outcome and validation status remain separate

The geometry result continues to use six distinct outcomes from Phase 6.0.3:

```ts
type ContactGeometryOutcome =
  | { kind: "positive-area-overlap"; proofClaim: ExactOrBoundedAreaClaim }
  | { kind: "boundary-contact"; proofClaim?: ExactOrBoundedBoundaryClaim }
  | { kind: "separated"; proofClaim: ExactOrBoundedSeparationClaim }
  | { kind: "indeterminate"; reasonCodes: readonly string[]; bounds?: NumericBounds }
  | { kind: "invalid-geometry"; reasonCodes: readonly string[] }
  | { kind: "unsupported-geometry"; feature: string; capabilityVersion?: string };

type ExactOrBoundedAreaClaim =
  | { kind: "exact"; intersectionArea: ExactArea }
  | { kind: "bounded"; intersectionArea: { lower: number; upper: number; unit: string } };

type ExactOrBoundedBoundaryClaim = { kind: "exact"; signedSeparation: 0; intersectionArea: 0 };
type ExactOrBoundedSeparationClaim =
  | { kind: "exact"; signedSeparation: PositiveExactLength }
  | { kind: "bounded"; signedSeparation: { lower: number; upper: number; unit: string } };
```

A bounded positive-area proof is eligible only if the approved sound-bound semantics establish a strictly positive intersection area; a bound that includes zero remains indeterminate. Boundary contact is not silently reclassified as either overlap or separation. Its electrical meaning, short semantics, and same-Net treatment remain pending product-owner decision. No epsilon, snap, or manufacturing tolerance is applied to physical connectivity without a separately approved rule. [1] [2]

Proof-validation status is a second, derived axis. It does not replace any geometry outcome:

```ts
type ProofValidationStatus =
  | "verified-current"
  | "missing-authority"
  | "unknown-authority"
  | "unknown-verifier-version"
  | "unsupported-proof-format"
  | "unavailable"
  | "unverifiable"
  | "digest-mismatch"
  | "invalid-payload"
  | "binding-mismatch"
  | "stale-geometry"
  | "stale-revision"
  | "contradictory"
  | "unsupported-capability";
```

Examples of the distinction: stale overlap evidence retains its original asserted geometry outcome but is `stale-geometry` and cannot union; validly hashed but malformed proof bytes are `invalid-payload`, not a valid certificate; unsupported geometry is not invalid geometry; and a verified separation is not a failed or unavailable proof. The final public diagnostic IDs and severity mappings for these states remain subject to registry and product-owner approval. [1] [2] [3]

### 3.2 Proposed ContactEvidence and proof identities

The following is a logical proposal, not a frozen wire schema. Exact required fields, normalization, version strings, digest preimages, and compatibility adapters require approval.

```ts
type DigestRef = {
  algorithm: string;
  domain: string;
  value: string;
};

type AuthorityIdentity = {
  namespace: string;
  authorityId: string;
  authorityVersion: string;
};

type VerifierIdentity = {
  verifierId: string;
  verifierVersion: string;
  contractVersion: string;
};

type ResolverIdentity = {
  resolverId: string;
  resolverVersion: string;
};

type ProofRef = {
  mediaType: string;
  proofFormatId: string;
  proofFormatVersion: string;
  contentDigest: DigestRef;
  resolver: ResolverIdentity;
};

type ContactBinding = {
  projectStableId: string;
  contactId: ContactId;                 // recomputed; never caller-authoritative
  nodeIds: readonly [CopperNodeId, CopperNodeId]; // distinct; canonical byte order
  layerId: LayerId;                     // enabled copper layer
  geometryHashes: readonly [DigestRef, DigestRef]; // aligned with nodeIds
  inputRevision: string;
  stackupRevision: string;
  topologyRevision?: string;
  graphContractVersion: string;
  predicateId: string;
  predicateVersion: string;
  kernelId: string;
  kernelVersion: string;
  contextDigest: DigestRef;
};

type ProvenanceRecord = {
  kind: "current-run" | "explicit-model" | "verified-library" |
        "manufacturing-import" | "human-assertion" | "derived";
  sourceId: string;
  sourceVersion?: string;
  sourceDigest?: DigestRef;
  locator?: string;
};

type ContactEvidenceRecord = {
  schemaVersion: string;               // proposed, not yet frozen
  evidenceId: string;                  // recomputed from canonical payload
  contactId: ContactId;
  binding: ContactBinding;
  outcome: ContactGeometryOutcome;
  proof?: ProofRef;
  authority?: AuthorityIdentity;
  verifier: VerifierIdentity;
  provenance: readonly ProvenanceRecord[];
  payloadDigest: DigestRef;
};

type ResolvedProof =
  | { status: "resolved"; bytes: Uint8Array; observedDigest: DigestRef;
      mediaType: string; provenance: readonly ProvenanceRecord[] }
  | { status: "not-found" | "unavailable" | "unsupported" | "integrity-error";
      reasonCode: string };

type ProofResolver = {
  id: string;
  version: string;
  resolve(ref: ProofRef, expected: {
    contactId: ContactId;
    contextDigest: DigestRef;
    allowedFormats: readonly string[];
  }): ResolvedProof;
};

type ValidatedContactWitness = {
  contactId: ContactId;
  evidenceIds: readonly string[];        // unique canonical order
  geometryOutcome: ContactGeometryOutcome["kind"];
  status: ProofValidationStatus;         // derived by the current validator
  validatedContextDigest?: DigestRef;
  reasonCodes: readonly string[];
};
```

`ContactBinding` retains the original identity inputs—canonical pair, layer, geometry hashes, input revision, predicate/kernel identity and versions—rather than silently changing the original ContactId contract. `contextDigest` adds broader current-context freshness, including Stackup and topology context where relevant. The exact boundary between ContactId identity and freshness-only context remains open. [1] [2] [3]

Authority and verifier are separate. An authority identifies an issuer or certification authority. A verifier identifies the implementation and version that checks proof semantics. A resolver retrieves immutable bytes but does not establish that they are true or authoritative. Unknown identity/version, missing authority, absent registry entry, untrusted source, or unverifiable payload cannot grant certification by default. No trust root, default verifier, or approved process list is selected here. [2] [3]

### 3.3 Proof resolver and certification procedure

The resolver is an exact-version, immutable-content lookup. Given a ProofRef and expected subject/context, it returns bytes and observed digest or a typed retrieval/integrity failure. The validator then independently:

1. Validates schema, required fields, supported encoding, digest encoding, identifier uniqueness, canonical two-node pair, aligned geometry hashes, exact layer, and context shape. It does not coerce or repair persisted values.
2. Recomputes ContactId, EvidenceId, payload/context digests, and current geometry hashes. It checks the enabled copper LayerId and exact node ownership. A coherent old hash/revision is stale; impossible or contradictory subject binding is invalid.
3. Resolves proof bytes using the declared resolver identity/version and checks the observed content against the declared digest. A reused digest with altered bytes is an integrity collision or mismatch; preserve the conflicting records and do not overwrite them.
4. Parses the proof under an explicitly supported proof-format version. It validates payload fields, units, proof-to-subject binding, provenance, authority, verifier identity/version, and any approved authenticity checks. A digest that matches malformed or semantically invalid content does not verify the payload.
5. Independently re-evaluates the claim using an authorized current predicate/kernel, or validates a portable certificate only under an explicitly approved compatible verifier contract. The proof must establish the claimed outcome for the exact pair, layer, geometry hashes, and current context.
6. Derives `verified-current` only if all required checks pass and an explicit authority/capability policy permits the exact verifier/proof class. Persisted status flags are recomputed, not trusted.

Missing authority, unknown authority, unknown verifier version, unavailable proof, unsupported format, digest mismatch, malformed/invalid payload, stale geometry/revision, contradictory evidence, or context mismatch all produce zero graph unions. They must not be converted into `separated`, `clear`, or an empty geometry state. [1] [2] [3]

### 3.4 Exactly which proof classes can authorize a physical graph union

Only these two proposed classes are candidates, and neither is active unless product/architecture owners explicitly register its exact identity, version, and semantics:

1. **Current-run geometry proof.** The current analysis run evaluates the exact canonical node pair on the exact enabled copper layer using a supported predicate/kernel and a verifier identity/version explicitly authorized for graph construction. The result is reproducible or independently checkable and establishes positive intersection area under the approved exact/bounded semantics.
2. **Imported or portable certificate.** The certificate’s authority, verifier, proof format, capability, provenance, and version are explicitly approved. Immutable bytes and digest resolve correctly; current compatibility/revocation rules pass; and the proof semantically establishes positive-area overlap for the exact current pair/layer/hashes/context.

For either class, **only `verified-current` plus `positive-area-overlap` is edge-eligible**. At most one undirected edge is applied per unique ContactId. A supported proof of separation is known absence for that pair, not an edge. Boundary, indeterminate, invalid, unsupported, stale, unavailable, unverifiable, contradictory, or boolean-only evidence never unions. Net identity, contact multiplicity, stage membership, matching names, proximity, and shared layer IDs never authorize union. [1] [2] [3]

## 4. Microvia manufacturing-process evidence

### 4.1 Process evidence and process identity

Phase 6.0.3 already placed a `processEvidence` reference on each Microvia stage, with source kinds including `explicit-model`, `verified-library`, and `manufacturing-import`, plus a content hash. It also says process evidence is stage-specific and leaves supported technology, adjacency, stacked/staggered manufacturability, depth, and fabrication limits to policy. Phase 6.0.4 defines `PCB_VIA_PROCESS_UNSUPPORTED` but does not make a stage label or a process assertion sufficient proof. Phase 6.0.5 requires an explicit authoritative stage sequence and exact consecutive transitions. The closure below strengthens those proposals without deciding the pending manufacturing policy. [1] [2] [3]

```ts
type ProcessIdentity = {
  namespace: string;
  processType: string;
  processId: string;
  processRevision?: string;
  variant?: string;
};

type ProcessEvidenceRef = {
  evidenceId: string;
  mediaType: string;
  contentDigest: DigestRef;
  resolver: ResolverIdentity;
};

type MicroviaProcessEvidence = {
  schemaVersion: string;                // proposed, not frozen
  stageId: StageId;
  process: ProcessIdentity;
  processSpecificationVersion: string;
  capabilityRegistryId: string;
  capabilityRegistryVersion: string;
  evidence: readonly ProcessEvidenceRef[];
  provenance: readonly ProvenanceRecord[];
  verifier: VerifierIdentity;
  contextDigest: DigestRef;
};

type ProcessEvidenceState =
  | { state: "present"; record: MicroviaProcessEvidence }
  | { state: "missing"; sourceSchema?: string; reasonCode: string };

type MicroviaStage = {
  id: StageId;
  fromLayerId: LayerId;
  toLayerId: LayerId;
  memberNodeIds: readonly CopperNodeId[];
  processEvidence: ProcessEvidenceState;
};

type ProcessVerificationState =
  | "verified-supported"
  | "explicitly-unsupported"
  | "missing"
  | "unknown"
  | "unverifiable"
  | "stale"
  | "invalid"
  | "contradictory";

type ProcessVerification = {
  processIdentityDigest?: DigestRef;
  state: ProcessVerificationState;
  capabilityRegistryId?: string;
  capabilityRegistryVersion?: string;
  verifier: VerifierIdentity;
  contextDigest: DigestRef;
  reasonCodes: readonly string[];
};

type CapabilityEntry = {
  process: ProcessIdentity;
  status: "supported" | "unsupported";
  validatedRuleContractId?: string;
  validatedRuleContractVersion?: string;
  acceptedEvidenceKinds: readonly ProvenanceRecord["kind"][];
  acceptedVerifierIds: readonly string[];
  acceptedVerifierVersions: readonly string[];
};

type CapabilityRegistry = {
  schemaVersion: string;
  registryId: string;
  version: string;
  digest: DigestRef;
  issuer: AuthorityIdentity;
  coverage: readonly {
    namespace: string;
    completeness: "closed-world" | "partial";
  }[];
  entries: readonly CapabilityEntry[];
};
```

The `missing` union member is explicit so legacy or absent stage records cannot default to supported. A migration/reader may map an absent historical field to a typed `missing` state while retaining original source data; it must not fabricate a process identity or capability. A supported capability means only that a currently verified registry contract recognizes the process under its declared scope. It does not prove stage contact, electrical continuity, or universal manufacturability. [1] [2]

### 4.2 Process verification and stage-sequence validation

Process resolution is performed against an integrity-verified, version-pinned registry. A supported result requires an explicit applicable registry entry, a validated rule contract, accepted evidence provenance, and an allowed verifier/version. Registry coverage must be clear. An unknown token in a partial, unavailable, or unverifiable registry remains unknown; absence from an incomplete registry cannot be called unsupported.

For a continuous Microvia path, an explicit authoritative `orderedStageIds` sequence defines the directed progression. Expected transitions are exactly `(s[0], s[1])`, `(s[1], s[2])`, and so on. Do not infer order from an arbitrary array, names, layer numbers, stage arrival order, placement, or junction records. Each junction must bind exact owned stage nodes, a common enabled copper layer, current geometry/context, and a verified positive-area witness. A reversed-only or nonconsecutive junction does not cover the expected transition. Preserve independent within-stage contacts if any stage/process/transition validation fails. [1] [2] [3]

Process verification and contact proof are conjunctive but separate gates:

```text
Microvia inter-stage edge is admitted only if:
  assembly and Stackup are valid
  AND the directed stage pair is exactly an expected consecutive transition
  AND both stage/node ownership facts are current and exact
  AND applicable process evidence is verified-supported under the current registry
  AND the junction witness is verified-current for the exact pair/layer/context
  AND the geometry outcome is positive-area-overlap
```

No process record, supported process token, stacked/staggered arrangement, same endpoint label, or layer adjacency alone creates a conductive edge. No additional adjacency, depth, capture-land, cycle, branch, stack/stagger, or fabricator limits are invented here. [1] [2]

### 4.3 `PCB_VIA_PROCESS_UNSUPPORTED` trigger and attribution

The original Phase 6.0.4 proposed trigger is retained: the process/span must be well-formed enough to identify, and the process must be outside the explicitly supported process set or have no validated rule contract. The diagnostic must be emitted only when the applicable, integrity-verified registry makes that conclusion determinate. That includes an explicit unsupported entry, a conclusively complete closed-world set that excludes the identified process, or an applicable entry that lacks a validated rule contract. [2]

**Do not emit `PCB_VIA_PROCESS_UNSUPPORTED`** merely because a record is absent, malformed, stale, unavailable, or untrusted, or because a process token is unknown while registry coverage is partial. Those are missing/invalid/unknown/unverifiable states and produce no process-gated transition. The product-owner must decide whether a separate missing-process finding is required; no such finding ID or severity is established by the source documents. [1] [2] [3]

The proposed canonical owner is the Microvia process-capability resolver. Other validators may reference the decision but cannot emit a duplicate for the same occurrence. Preserve the Phase 6.0.4 key fields:

```text
(findingId, projectStableId, viaObjectId,
 processTokenDigest, capabilityRegistryVersion)
```

Attribution includes affected stage IDs where known, the process token, exact registry identity/version/digest, applicable rule-contract identity/version or its absence, evidence references, verifier, and current context. Stage-scoped key expansion is unresolved if different stages can carry different process identities. Do not collapse different Via objects, process tokens, registry versions, or independently failed guarantees into one unsupported finding. Severity and sign-off blocking remain pending. [2] [3]

## 5. Contact Ledger: canonical collections and output validation

### 5.1 Canonical representation

This resolves the apparent contradiction between one row per contact and multiple evidence contributions. The Phase 6.0.4 upsert and Phase 6.0.5 evidence multiplicity principle remain: one canonical contact identity/outcome record, with every distinct evidence contribution retained. The 6.0.6 serialized representation separates those identities explicitly. [2] [3] [4]

```ts
type ContactRecord = {
  schemaVersion: string;
  contactId: ContactId;
  binding: ContactBinding;
  claimedOutcomeKind: ContactGeometryOutcome["kind"];
  evidenceIds: readonly string[];        // sorted and unique; may be empty
};

type EvidenceRecord = {
  schemaVersion: string;
  evidenceId: string;
  contactId: ContactId;
  outcome: ContactGeometryOutcome;
  proof?: ProofRef;
  authority?: AuthorityIdentity;
  verifier: VerifierIdentity;
  provenance: readonly ProvenanceRecord[];
  payloadDigest: DigestRef;
};

type UnionApplication = {
  contactId: ContactId;
  nodeIds: readonly [CopperNodeId, CopperNodeId];
};

type ContactLedger = {
  schemaVersion: string;
  serializationProfile: string;
  projectStableId: string;
  context: ContactBinding["contextDigest"];
  contacts: readonly ContactRecord[];    // exactly one persisted row per ContactId
  evidence: readonly EvidenceRecord[];   // exactly one persisted row per EvidenceId
  unionApplications?: readonly UnionApplication[];
};
```

A ContactRecord may refer to multiple EvidenceRecords. Each evidence row refers to exactly one ContactId. The contact’s `evidenceIds` and the evidence array must agree in both directions. An empty evidence list can describe an outcome that has no proof material, but it can never authorize a union. The validator derives the aggregate evidence state; the contact’s claimed outcome or validation flags are not authoritative. Conflicting current evidence remains visible and blocks union without majority vote or first/last selection. [2] [3]

### 5.2 Uniqueness, referential integrity, digest, and canonical order

Validation must inspect raw serialized rows before constructing maps, sets, sorting, or normalization that could hide duplicates:

1. Parse strict UTF-8/JSON under a supported schema. Reject malformed JSON, duplicate object member names, unknown versions without an explicit adapter, missing required fields, type coercion, and malformed digests.
2. Scan raw `contacts[]` for duplicate ContactIds and `evidence[]` for duplicate EvidenceIds before any deduplication. Repeated persisted rows are a defect even if byte-identical. Do not first/last-win, merge, or normalize a malformed persisted ledger. Duplicate detection in output validation must occur even if the producer used an internal Map that already collapsed the duplicate.
3. Normalize identity-bearing strings according to the approved profile; reject empty values and distinct raw strings that collide after normalization. Require exactly two distinct node IDs in the canonical pair order and geometry hashes aligned to the corresponding node IDs. Reject persisted noncanonical pair order rather than silently repairing it.
4. Recompute ContactId from its approved identity tuple. Recompute EvidenceId/payload digest from the approved evidence preimage, excluding its own self-digest field. Recompute context and proof-content digests from resolved immutable bytes. A valid digest does not establish proof semantics or verifier authority.
5. Require each EvidenceRecord’s ContactId to resolve to exactly one ContactRecord. Require each ContactRecord EvidenceId to resolve to exactly one EvidenceRecord that points back to that same contact. Reject missing, orphan, duplicate, dangling, extra, or cross-contact references.
6. Recompute current geometry hashes, revisions, enabled copper ownership, proof resolution, verifier/authority policy, and geometry outcome. Stale remains stale; invalid, unsupported, indeterminate, separated, and boundary states remain distinct.
7. Independently recompute the eligible ContactId set. If `unionApplications[]` is serialized, it must contain exactly one unique entry for every eligible contact and no others. Reject duplicate, dangling, omitted, ineligible, or pair-mismatched unions. Applying a ContactId twice is diagnosed and idempotent; distinct ContactIds remain distinct evidence even if their endpoints already share a DSU component.
8. Only after those checks may the reader group evidence contributions by ContactId and produce a canonical validated view. Sort `contacts[]` by ContactId, `evidence[]` by EvidenceId, and evidence/provenance/reference arrays by documented stable keys. Preserve semantic stage sequence order; never replace it with lexical sort.
9. Round-trip the serialized output through an independent reader. Recompute identities, digests, references, freshness, proof semantics, and eligible unions. Require stable canonical bytes and equivalent findings for equivalent input.

RFC 8785/JCS over UTF-8 after Unicode NFC normalization, with domain-separated SHA-256 digests and versioned prefixes, is a candidate only; it is not yet the approved wire recipe. The exact schema/profile version, ContactId and EvidenceId preimages, hash lifecycle, unit encoding, and migration rules remain product/architecture decisions. This preserves Phase 6.0.5’s recommendation without silently freezing it. [3]

## 6. Diagnostic ownership, stable identity, and coexistence

### 6.1 Central registry model

A central registry/finalizer owns rule ID, semantics version, canonical defect owner, allowed producers, trigger, prerequisites, attribution fields, prescribed occurrence key, and any explicitly approved causal precedence. Validators submit structured diagnostic candidates. The registry validates rule registration and recomputes occurrence identity; an unregistered or contradictory rule definition is a registry-integrity issue, not permission for a validator to invent a finding. Severity, blocking, DRC-clear sign-off, output caps, and wording remain separate pending product policy. [1] [2] [3]

Proposed stable occurrence identity:

```text
DiagnosticOccurrenceId = H(
  domain,
  ruleId,
  ruleSemanticsVersion,
  stable project ID or explicitly run-local scope,
  only that rule's normalized occurrence-key fields
)
```

Use normalized canonical bytes and a versioned digest profile only after approval. Exclude producer, display text, severity, timestamp, insertion order, DSU root, NetId, and evidence arrival order unless a registered rule expressly makes a field identity-bearing. Retain producer/evidence references as sorted provenance. Identity-bearing payload conflicts are preserved and flagged; no first/last/majority winner. [3]

### 6.2 Ownership and deduplication table

| Defect class / finding family | Canonical owner | Secondary validators and attribution | Coexistence / suppression rule |
|---|---|---|---|
| Phase 6.0.3 NetAssignment invalid, conflicting, incomplete | NetAssignment validator | Graph/classifier may reference object/component context | Preserve the source IDs and keys; do not convert assignment states or suppress physical findings. Exact aggregation caps/severity remain pending. |
| Definite copper short, connectivity indeterminate, disconnected island, island indeterminate | Physical graph / connectivity classifier | Geometry and evidence validators provide ContactIds, witnesses, component snapshots, and possible edges | Preserve the historical component/pair/Net-scoped dedup rules. Definite multi-Net short coexists with unrelated uncertainty. Net identity does not construct the graph. |
| Invalid, unsupported, or numerically indeterminate geometry | Geometry predicate/geometry-input validator | Contact/evidence validator supplies affected object/pair and proof context | Keep geometry outcomes distinct. Do not replace custom/unsupported geometry with approximate shapes or turn failure into separation. |
| Via span missing/unresolved or invalid | ViaSpan validator | Microvia validator may reference the same ViaSpan occurrence | One ViaSpan-owned occurrence for the exact root defect. Do not call valid-disjoint missing. Preserve separate Microvia defect only when independently established. |
| Continuous barrel evidence missing or unverifiable | ViaSpan evidence owner, using the proof resolver | Microvia may cite its dependency on the span | Missing and unverifiable are distinct. No cross-layer barrel edge; independent v2 clearance continues. |
| Microvia stage/node/topology reference invalid | Microvia assembly/topology validator | ViaSpan may reference but does not re-own stage/node fields | One Microvia structural occurrence per registered key. No affected inter-stage edge; retain independent valid within-stage edges. |
| Microvia expected junction missing, stale, boundary-only, or unprovable | Microvia junction-evidence validator, after topology is structurally valid | Contact verifier and geometry predicate contribute exact evidence state | No transition edge. Do not also emit this solely as a derivative of the same invalid ViaSpan root; retain genuinely independent stale/wrong-pair evidence. |
| Process capability explicitly unsupported | Microvia process-capability resolver | ViaSpan and junction validators reference the same decision | Retain Phase 6.0.4 key. Coalesce only the same token/Via/registry-version occurrence. Missing or unknown process evidence is not this finding. |
| ContactEvidence schema, proof, identity, or ledger integrity | Contact-evidence/ledger reader | Geometry and resolver validators provide their separate facts | Candidate 6.0.5 Contact rules require registry approval. Duplicate persisted IDs, orphan refs, digest mismatch, and semantic invalidity remain typed and are not silently deduped. |
| Independent clearance finding, including schema-v2 rule | Existing clearance-rule owner | ViaSpan/Microvia may contribute context only | Always coexist with process/span/contact diagnostics; no topology or evidence diagnostic gates the legacy v2 all-pairs check. |

Historical Phase 6.0.3 IDs and dedup keys remain unchanged. Phase 6.0.4 ViaSpan/Microvia IDs and keys are retained as audit-reported proposals, not approved production registry entries. Phase 6.0.5 ContactEvidence/ledger diagnostic names remain candidates until reconciled with the historical registry and owner-approved. No missing-process diagnostic ID is invented here. [1] [2] [3]

### 6.3 Exact cross-validator arbitration

- Candidates with the same registered `ruleId`, semantics version, project scope, and exact canonical occurrence fields coalesce into one occurrence. Keep all distinct producer, evidence, and provenance references.
- A secondary validator that sees the same root defect references the canonical owner’s occurrence. It does not emit a competing duplicate.
- Across different rule IDs, retain both by default. Suppress a derivative finding only when a registered causal rule establishes that it restates the exact same root defect and adds no separate guarantee. Causal precedence is not severity precedence.
- A missing or invalid ViaSpan may suppress only a Microvia uncertainty finding that is solely a consequence of that exact unresolved span and cannot independently be evaluated. An independently stale witness, malformed stage/node ownership, unsupported process, or distinct transition failure remains a separate finding when its own trigger is met.
- Never suppress a confirmed short, independent valid contact, independent geometry/clearance rule, v2 all-pairs clearance, or distinct evidence-integrity failure because another validator reported a Via or Microvia problem.
- Same defect reported by ViaSpan and Microvia: one canonical ViaSpan occurrence with Microvia as a producer/reference. Two distinct defects—such as invalid ViaSpan plus a stale witness on a structurally valid expected transition—retain separate findings and keys.

## 7. Validation algorithms

### 7.1 Contact proof validation and graph admission

```text
function validateContactEvidence(rawContactRows, rawEvidenceRows, currentContext):
    parse strict schema; preserve raw multiplicity and row locations
    detect duplicate ContactIds and EvidenceIds before maps, sorting, or dedup
    validate canonical pair, aligned hashes, required fields, formats, and reference shapes
    recompute ContactId, EvidenceId, payload/context digests, and current geometry hashes
    resolve exact nodes, enabled layer, current revisions, predicate/kernel contract
    for each evidence:
        resolve immutable proof with exact resolver ID/version
        verify resolved bytes against digest
        validate authority, verifier/version, format, provenance, payload, subject, and context
        independently verify the claimed exact/bounded geometry proposition
        derive validation status; never trust persisted status/Boolean
    aggregate evidence per unique ContactId without majority vote
    retain conflicting/stale/unavailable/unsupported records distinctly
    eligible = contacts with current exact binding and verified positive-area proof
    assert each eligible ContactId is unique
    return contacts, evidence, typed failures, eligible

function buildPhysicalContactGraph(eligibleContacts):
    for each eligible ContactId in canonical order:
        apply at most one undirected union for its exact node pair
    retain all non-eligible contact outcomes and required uncertainty findings
    annotate the resulting physical graph with NetAssignment only afterward
```

Unrelated valid contacts and already-confirmed shorts are not rolled back because one evidence record is stale, unavailable, invalid, or unsupported. Matching NetIds do not replace proof. [1] [2] [3]

### 7.2 Microvia process and transition validation

```text
function validateMicroviaAssembly(assembly, validatedStackup, registry, currentContext):
    validate explicit authoritative orderedStageIds and unique stage IDs
    derive exact consecutive directed expected transitions from that sequence
    validate every stage endpoint/node owner and enabled copper layer
    for each stage:
        if processEvidence is missing:
            state = missing/unknown; do not default supported or emit unsupported
        else:
            resolve exact process identity and immutable evidence
            verify registry integrity, coverage, provenance, resolver and verifier versions
            classify supported / explicitly unsupported / unknown / unverifiable / stale / invalid
            emit PCB_VIA_PROCESS_UNSUPPORTED only on the exact registered trigger
    validate junction record against one expected directed consecutive transition
    require exact stage-node ownership, distinct current nodes and compatible layer
    validate exact ContactEvidence proof for the expected pair/context
    admit edge only if process is verified-supported AND witness is verified-current
      positive-area-overlap AND transition is expected and structurally valid
    preserve within-stage valid edges and all other independent graph evidence
    report missing, reversed-only, nonconsecutive, stale, unsupported, or conflicting cases
      without converting them to a conductive edge or to known separation
```

### 7.3 Serialized ledger and registry finalization

```text
function validateSerializedLedger(bytes, currentContext):
    parse strict supported serialization; reject duplicate object keys
    scan contacts[] / evidence[] arrays for duplicate IDs before any normalization/dedup
    validate canonical ordering, digest syntax, pair/hash alignment and schema versions
    recompute IDs/digests; validate bidirectional ContactId/EvidenceId references
    resolve all current nodes, geometry hashes, proof bytes, verifiers, and context
    reject orphan, duplicate, cross-contact, stale, contradictory, malformed, or ineligible records
    independently recompute eligible ContactIds and compare unionApplications exactly
    canonicalize only validated unique records; independently round-trip and revalidate
    return typed validation result; never normalize persisted duplicates away

function finalizeDiagnostics(candidates, registry):
    require registered rule and allowed producer
    normalize prescribed occurrence fields and recompute occurrence identity
    merge same-key compatible candidates, retaining sorted provenance/evidence
    preserve same-key conflicts; no first/last/majority winner
    across rule IDs, retain both except explicitly approved same-root causal suppression
    sort output by canonical keys; do not use arrival order, timestamp, NetId, or DSU root
```

These are proposed acceptance algorithms only. No tests or builds were run for this design task. [3] [4]

## 8. Adversarial case matrix

The outcomes below are required design acceptance criteria, not executed test results.

| # | Adversarial case | Expected validation and graph outcome |
|---:|---|---|
| 1 | Missing certification authority | Retain proof/provenance; derive `missing-authority` or approved schema-invalid state; no union. A certification Boolean cannot fill the gap. |
| 2 | Unknown verifier version | Do not auto-upgrade or trust; derive `unknown-verifier-version`/unsupported-verification status; no union. |
| 3 | Valid digest but invalid proof payload | Byte integrity may pass, but schema, binding, or semantics fails; `invalid-payload`/binding failure; no union. |
| 4 | Reused EvidenceId/digest with altered payload | Recomputed identity/content mismatch or collision; preserve conflicting records, no overwrite or majority choice; no union. |
| 5 | Unsupported or missing Microvia process evidence | Missing is `missing`/unknown and never assumed supported or mislabeled unsupported. A well-formed, conclusively unsupported process triggers `PCB_VIA_PROCESS_UNSUPPORTED`. Neither admits an inter-stage edge; independent valid within-stage contact remains. |
| 6 | Multiple evidence records reference one ContactId | Valid representation when ContactId binding/context agree and EvidenceIds are distinct; one contacts[] row, several evidence[] rows, one union maximum. Conflicting current outcomes block union and remain visible. |
| 7 | Duplicate ContactId in serialized output | Detect in raw contacts[] before maps/sorting/dedup, including byte-identical rows; reject/diagnose persisted ledger; no first/last-wins and no union from ambiguous output. |
| 8 | Orphan EvidenceId / missing ContactId reference | Referential integrity fails in either direction; preserve row/reference locations; affected evidence cannot union. |
| 9 | Same defect detected by ViaSpan and Microvia | One occurrence owned by the canonical ViaSpan rule owner when it is the same ViaSpan root; Microvia supplies secondary provenance/reference. Suppress only derivative uncertainty for that exact root. |
| 10 | Two distinct defects must remain separate | Invalid ViaSpan plus independently established stale proof on a structurally valid expected transition yields separate owned findings. No Via-level blanket suppression. |
| 11 | Stale geometry hash and stale input revision | Derive stale status; preserve old evidence; no union. Never rewrite as separated/current. Independent valid contacts and v2 clearance still run. |
| 12 | Boundary contact incorrectly treated as conductive union | Retain `boundary-contact`; zero union while tangent policy is pending; emit registered uncertainty where it can change topology/Net/island conclusions. |
| 13 | Same NetId but no qualifying contact; different NetIds with qualifying proof | First pair remains physically disconnected; second is physically joined. NetAssignment does not change union eligibility. |
| 14 | Definite multi-Net short plus unrelated uncertain contact | Preserve the definite short and independently report applicable uncertainty; uncertainty does not erase/downgrade the confirmed short. |
| 15 | Two valid Via spans have empty intersection versus one missing/invalid span | First is known-disjoint and does not trigger missing-span. Missing/invalid stays unknown/invalid, never empty. No inferred conduction edge. |
| 16 | Reversed-only or nonconsecutive Microvia junction | Does not cover an expected directed consecutive transition; no shortcut edge; expected transition remains unresolved. |
| 17 | Validly hashed proof resolves, but references wrong node pair or layer | Binding mismatch/invalid evidence; no union, regardless of digest validity. |
| 18 | Reordered ledger input and repeated DSU request | Canonical valid output is order-independent. Repeated union by same ContactId is at most idempotent and diagnosed; no duplicate contact count. |

## 9. Cross-document consistency matrix

| Invariant / area | Phase 6.0.3 original | Phase 6.0.4 audit | Phase 6.0.5 reference | Phase 6.0.6 closure result |
|---|---|---|---|---|
| NetAssignment separate from physical connectivity | §§4–5: preserve assignment states; graph is geometry-derived | §7 and §9 carry forward separation | §§4, 9 preserve post-graph annotation | Kept; NetId cannot create, merge, certify, or suppress physical edges. |
| Same-Net identity never creates physical connectivity | §5: no graph union by NetId | §7: physical graph remains separate | §§4–5, 9 reaffirm | Kept; disconnected same-Net islands remain disconnected unless physical edges exist. |
| Definite multi-Net components remain shorts | §§5, 10.1: any confirmed component with at least two distinct verified NetIds is a definite short | §9.1 carries forward | §§4, 9 carry forward | Kept; uncertainty on another contact does not erase a definite short. |
| Uncertain contacts cannot disappear | §§6–7, 10: boundary/indeterminate/invalid/unsupported remain explicit and uncertainty finding has trigger/dedup | §§5, 7, 9 require exact evidence and retained uncertainty | §§4–5, 8–10 preserve typed uncertainty | Kept; proof failure, missing evidence, stale status, or boundary remains visible and cannot become CLEAR by omission. |
| Valid disjoint Via spans vs unknown/invalid | §9: known-empty only from two valid enumerations; unknown/invalid distinct | §§4.1–4.2 preserve distinction | §§4, 9, 10 preserve | Kept; empty intersection is known-disjoint only; missing/invalid never map to empty. |
| Canonical Stackup ordering | §8 originally contains multiple authored order fields | §8 replaces them with single `layersFrontToBack` | §§4, 9 follow corrected model | Use 6.0.4’s single physical sequence as correction; derive copper order, do not repair by sorting. Disabled layers remain represented but cannot host electrical nodes/endpoints. |
| Legacy v2 `minimumViaClearance` | §§3, 12: projected 2D all-pairs outer-copper clearance, configured clearance and `drill` fallback as specified | §§4.2, 9 preserve independent check | §§4, 9 preserve | Kept independently of spans, proof, process, graph, or topology; not drill-to-drill; no gating or suppression. |
| Geometry approximation prohibited | §§6.2–6.3: robust/exact distinctions; no implicit epsilon/tolerance; unsupported types not approximated | §7 preserves outcomes and pending tangent | §§4–5 preserve six-state model | Kept; no approximation, snapping, tolerance expansion, or proof failure mapped to separation. |
| Microvia stage process and sequence | §9 has per-stage processEvidence; stage sequence/process constraints are pending | §§4.1, 5 specify unsupported rule and exact witness; no invented process adjacency | §6 requires authoritative order and exact consecutive transitions | Extend per-stage evidence and require explicit authoritative sequence; missing process is not supported; no extra manufacturing rules are decided. |
| Contact records vs evidence multiplicity | §6 defines ContactEvidence and immutable run evidence | §7 says one canonical contact outcome plus distinct evidence | §§5, 7 preserve multiple EvidenceIds under one ContactId, but ledger `records[]` is ambiguous | Resolve as contacts[] (one row/ContactId) plus evidence[] (one row/EvidenceId); detect serialized duplicates before dedup. |
| Diagnostic ownership / coexistence | §10.1 provides historical rules and dedup keys | §4.1 adds ViaSpan/Microvia rule proposals | §8 proposes central registry and conditional arbitration | One owner per defect class proposed; coalesce only same registered occurrence/root; distinct guarantees coexist. No new product-facing ID or severity is approved here. |
| Product decisions / readiness | §13 and §16 enumerate pending decisions; not implementation authorization | §§11–12 keep key choices pending and freeze unapproved | §§11–12 not ready, not approved | All new authorities, registries, schema/digest policy, process support, boundary, severity, and diagnostic details remain pending; no Design Freeze or implementation authorization. |

The 6.0.3 Stackup’s redundant order fields are intentionally not carried forward alongside the 6.0.4 correction. The 6.0.3 per-stage `processEvidence` concept is retained and strengthened; its source kinds and hash do not establish trust policy. The 6.0.5 strict stage ordering is compatible with 6.0.4 only when the sequence is an explicit authoritative topology field, not incidental array order. The 6.0.4 one-contact upsert and 6.0.5 multiple evidence contributions are reconciled by separate `contacts[]` and `evidence[]` collections. [1] [2] [3]

## 10. Unresolved product-owner and architecture decisions

None of these choices is settled by this report:

1. Approved issuer/authority identities, verifier identities and exact versions, proof resolvers, trust roots, revocation/key-rotation rules, and proof classes authorized for graph construction.
2. Whether current-run computation itself is an authorized proof class; the boundary between an internally re-evaluated predicate and a portable certificate; and whether manufacturing imports, verified libraries, or human assertions can contribute to `verified-current` status.
3. ContactEvidence, ProofRef, resolver, Contact Ledger, Microvia process, registry, and diagnostic wire schema versions; migration adapters; canonical serialization; ContactId/EvidenceId/proof digest preimages, algorithms, prefixes, payload limits, and hash-agility policy. NFC/JCS/SHA-256 remains only a candidate.
4. Which geometry, input, Stackup, graph, topology, process-registry, predicate, kernel, verifier, and resolver revisions are ContactId identity fields versus freshness-only context; exact revision increment and stale-evidence obligations; project-stable versus run-local identity.
5. Robust/exact predicate and kernel guarantees; numeric units and bounds; what constitutes a sound bounded proof; any physical or manufacturing tolerance; and boundary/tangent electrical semantics, including short and same-Net exception behavior.
6. Supported Microvia process tokens, versions, registry authority and completeness/closed-world semantics; whether support is per-stage, Via, assembly, fabricator, material, or combination; process evidence source policy and supported proof formats.
7. Whether absent/malformed/unknown/unverifiable process evidence needs separate diagnostic IDs, and whether process findings should be Via-scoped or stage-scoped when stages differ. Do not mislabel absent evidence as unsupported.
8. Authoritative source for stage order; allowed endpoints, adjacency, skipped layers, branches, multiple contacts per transition, shared stages/nodes, non-continuous paths, cycles, stacked/staggered rules, intermediate lands, depth, and fabricator limitations.
9. ViaSpan/barrel evidence authority, accepted formats and proof of full-span continuity; Via endpoints and disabled-layer use cases; Stackup policy for fewer than two enabled copper layers or disabled physical outer copper.
10. Central registry additions, exact diagnostic owners and occurrence keys, cross-validator precedence, conflict handling, severity, blocking, DRC-clear sign-off, aggregation caps, and user-facing wording. Candidate Phase 6.0.5 contact/ledger rules are not approved IDs.
11. Whether validation summaries and `unionApplications[]` are persisted or computed-only; contact/evidence cardinality for non-proof results; evidence retention, privacy, storage, and audit reproducibility requirements.
12. Carried-forward 6.0.3 decisions on Net authority/conflicts/unassigned states, short reporting, island/incomplete-routing policy, geometry/kernel guarantees, Padstack and zone/fill support, v2 migration identity, and severity/sign-off behavior.

## 11. Readiness verdict

**Design-review readiness:** Suitable as a consolidated proposal for independent architecture and product-owner review. The four required closure areas and cross-document invariants are specified at contract level, with historical rules and source limits identified.

**Design Freeze:** **NOT APPROVED.** This report cannot approve Design Freeze. Trust authorities, proof semantics, process registry and Microvia policy, ledger wire details, diagnostic registration/ownership, boundary/tolerance, severity, and other decisions above remain open.

**Implementation readiness:** **NOT READY / NOT AUTHORIZED.** No code, tests, configuration, UI, CI, dependency, branch, or repository changes were made. The adversarial matrix is an expected-outcome specification, not executed tests. No tests or builds are claimed to have run.

**Phase 6.1 / 6.2:** Not started and out of scope. Stop after delivery for independent audit. [1] [2] [3] [4]

## 12. Isolation evidence

The checks below apply only to the previously authorized fresh clone; they do not make claims about any pre-existing local worktree. The report is outside that clone at `/home/ubuntu/readonly-inspection/PHASE_6_0_6_FINAL_EVIDENCE_LEDGER_CLOSURE.md`.

| Check | Before analysis | After report draft (2026-11-20T21:37:48+00:00) |
|---|---|---|
| Repository / origin | `/home/ubuntu/readonly-inspection/pcb-studio-pro`; `https://github.com/soheil6913/-PCB-Studio-Pro.git` | Same repository and origin |
| Branch and local HEAD | `main`; `de7497a675af7c6212bbc4751fce098c1f414e8d` | `main`; `de7497a675af7c6212bbc4751fce098c1f414e8d` |
| Remote `main` | `de7497a675af7c6212bbc4751fce098c1f414e8d` | `de7497a675af7c6212bbc4751fce098c1f414e8d` |
| Worktree | Clean (`git status --porcelain` empty) | Clean (`git status --porcelain --untracked-files=all` empty) |
| Phase 6 baseline | `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` object available | `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` object available |
| Scope/actions | Read-only inspection only; no branch switch/create, repository edits, tests, build, commit, push, merge, rebase, cherry-pick, amend, or reset | Read-only checks only; no branch switch/create, repository write, tests/builds, commit, push, merge, rebase, cherry-pick, amend, or reset. The report is outside the clone. |

After inserting these results into the report, a final read-only check was repeated. It confirmed the same origin, `main` SHA, remote `main` SHA, available Phase 6 baseline object, and clean worktree; no repository files or refs were changed.

## References

[1]: https://raw.githubusercontent.com/soheil6913/PCB/main/PCB_Studio_Pro_%E2%80%94_Phase_6.0%20%286%29.md "PCB Studio Pro — Phase 6.0.3 Design Freeze Corrections"
[2]: https://raw.githubusercontent.com/soheil6913/PCB/main/PCB_Studio_Pro_%E2%80%94_Phase_6.0%20%287%29.md "PCB Studio Pro — Phase 6.0.4 Final Contract Consistency Audit"
[3]: file:///home/ubuntu/readonly-inspection/PHASE_6_0_5_MICROVIA_EVIDENCE_TOPOLOGY_CLOSURE.md "Phase 6.0.5 Microvia Evidence and Topology Closure reference report"
[4]: file:///home/ubuntu/upload/pasted_content.txt "PCB Studio Pro — Phase 6.0.6 task specification"
