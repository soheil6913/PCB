# PCB Studio Pro — Phase 6.0.7
## Final Microvia Schema & Diagnostic Registry Closure

**Status:** Design-only contract proposal for independent review. No implementation or product policy is approved by this report.  
**Design Freeze:** **NOT APPROVED.**  
**Implementation readiness:** **NOT READY / NOT AUTHORIZED.**  
**Phase 6.1 / 6.2:** Not started; out of scope.  
**Report location:** `/home/ubuntu/readonly-inspection/PHASE_6_0_7_FINAL_MICROVIA_SCHEMA_AND_DIAGNOSTIC_REGISTRY.md` (outside the application repository).  
**Author:** Manus AI

## 1. Executive summary

This report proposes a consistent Phase 6.0.7 contract for Microvia assembly structure, manufacturing-process registry trust, and a complete diagnostic registry. It carries forward the confirmed historical connectivity and clearance behavior from Phase 6.0.3, the audit proposals from Phase 6.0.4, and the topology and Contact Ledger proposals in Phases 6.0.5–6.0.6. The supplied Phase 6.0.7 file is the task specification, not an existing implementation or a previously completed closure report. Accordingly, the contracts below are proposals for audit, not verified behavior in application code. [1] [2] [3] [4] [5]

The central separation is: byte/digest integrity is not cryptographic authenticity; authenticity is not issuer authorization; authorization is not registry currentness; current registry coverage is not process support; process support is not physical-stage validity; and physical-stage validity is not electrical junction verification. An inter-stage edge requires a structurally valid expected consecutive transition, exact stage ownership, applicable verified-supported process evidence, and a current, exact-pair/layer/context positive-area witness. A failed process or contact gate adds no affected inter-stage edge, but does not erase independently valid within-stage edges or a separately confirmed short.

The proposal defines complete TypeScript-like types, field invariants, a deterministic validation/state model, a lifecycle-neutral trust contract, a 15-family diagnostic registry with explicit approval status, and the required 24-case adversarial matrix. It deliberately does not select trusted authorities, trust-root material, cryptographic algorithms, supported process types, severity enums, or DRC-clear policy. Based on the completeness of the proposed review package and the unresolved owner decisions, the verdict is **Conditionally design-review ready**. It is not implementation-ready, and Design Freeze remains **NOT APPROVED**.

## 2. Scope, source status, and isolation

### 2.1 Scope and evidence labels

The work was limited to a design review and report preparation. No repository source, test, configuration, dependency, UI, documentation, or CI file was changed. No branch was created or switched. No tests or builds were run. No code was implemented, and no Phase 6.1 or 6.2 work was started.

This report uses four contract-status labels:

- **Historical** means an identifier or behavior is explicitly present in the Phase 6.0.3 source. The source itself says final RuleIds and severity require product-owner review; “historical” does not by itself mean production-approved.
- **Audit-proposed** means Phase 6.0.4 proposed the identifier or contract. It is not an approved production registry entry.
- **Candidate** means a later report suggested an ID or shape for discussion. It is not a registered RuleId.
- **Unresolved** means the supplied documents do not establish a stable RuleId, policy, value, or approval. Candidate labels in this report are not product RuleIds.

The normative words “must,” “must not,” and “only” state this proposal’s contract for review. They do not claim that code implements the contract. No product-owner decision is inferred from a proposal or external standard. The original Phase 6.0.3, verified 6.0.4 attachment, 6.0.5 report, 6.0.6 report, and Phase 6.0.7 specification were reviewed as source inputs. [1] [2] [3] [4] [5]

### 2.2 Repository isolation evidence

All repository checks apply only to the authorized fresh clone at `/home/ubuntu/readonly-inspection/pcb-studio-pro`. They do not establish the state of any pre-existing local worktree. The required pre-inspection check was completed at `2026-11-20T21:49:00Z`; origin was `https://github.com/soheil6913/-PCB-Studio-Pro.git`, branch was `main`, local `HEAD` and remote `main` were both `de7497a675af7c6212bbc4751fce098c1f414e8d`, the worktree was clean, and the Phase 6 baseline `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` was available as a commit object. No source or configuration changes were found. A post-review, read-only verification is recorded in §13 after report creation. The report and research note are outside the clone.

## 3. Contract boundaries and carried-forward invariants

### 3.1 Physical graph and typed claims

Physical connectivity is derived from validated physical evidence. `NetAssignment` annotates the resulting graph; it does not make or remove edges. Same `NetId`, equal names, membership in one stage, a matching endpoint label, shared layer, stacked/staggered declaration, process token, proximity, or a stored `certified`/`trusted` Boolean never creates a physical edge. A confirmed component with two or more distinct verified `NetId`s remains a definite short, even if another independent contact is uncertain. Uncertain evidence stays visible and is not converted to separation or silently dropped. [1] [3] [4]

Keep these claims separate in data and diagnostics: (1) payload/digest integrity, (2) signature authenticity, (3) issuer authorization and scope, (4) registry currentness, (5) process capability, (6) physical-stage validity, (7) geometry outcome, and (8) electrical-junction verification. Only a separately verified current positive-area contact can be an edge candidate; all structural, process, layer, ownership, and context gates must also pass.

The retained geometry outcomes are `positive-area-overlap`, `boundary-contact`, `separated`, `indeterminate`, `invalid-geometry`, and `unsupported-geometry`. A boundary/tangent result is retained and is not promoted to an edge while electrical semantics remain unresolved. Unsupported geometry is not approximated. An unknown or invalid ViaSpan is not an empty set: only two valid enumerations with an empty intersection mean known-disjoint. [1] [2] [3] [4]

### 3.2 Stackup, ledger, and v2 compatibility

Use the Phase 6.0.4/6.0.6 correction: `layersFrontToBack` is the single physical Stackup ordering source; copper order and face interpretation are derived after validation. Do not preserve the Phase 6.0.3 redundant order fields as a second runtime authority. Disabled outer copper and fewer-than-two-enabled-copper-layer behavior remain unresolved. [1] [2] [4]

Carry forward the Phase 6.0.6 Contact Ledger representation: `contacts[]` has one persisted row per `ContactId`; `evidence[]` has one row per `EvidenceId`; references are bidirectional; `unionApplications[]` is optional. Scan raw persisted arrays for duplicate IDs before maps, sorting, normalization, or deduplication. Phase 6.0.5 `records[]` is adapter input only, not a concurrent canonical representation. Wire version, canonical bytes, digest preimages, and migration remain unapproved. [3] [4]

For schema-v2, the historical `minimumViaClearance` remains the all-pairs projected 2D outer-copper clearance comparison, using the configured clearance and `drill` fallback stated in the source. It is not drill-to-drill and is never gated by ViaSpan, Microvia, process evidence, Contact Ledger, or graph state. Preserve the existing rule/finding identity if located; neither the exact `PCB_*` RuleId nor its finding key is stated in the reviewed source, so this report does not invent either. [1] [2] [3] [4]

## 4. Proposed schemas

All `/1` schema labels below are placeholders for review, not frozen wire versions. Identity normalization, canonical serialization, digest algorithms/preimages, numeric units, project identity, migration adapters, and revision rules are unresolved. Branded IDs are logical type distinctions and do not prescribe an encoding.

### 4.1 Shared identities and current context

```ts
type Brand<T, Name extends string> = T & { readonly __brand: Name };
type AssemblyId = Brand<string, "AssemblyId">;
type StageId = Brand<string, "StageId">;
type MembershipId = Brand<string, "MembershipId">;
type TransitionId = Brand<string, "TransitionId">;
type JunctionId = Brand<string, "JunctionId">;
type CopperNodeId = Brand<string, "CopperNodeId">;
type LayerId = Brand<string, "LayerId">;
type ContactId = Brand<string, "ContactId">;
type EvidenceId = Brand<string, "EvidenceId">;
type RegistryId = Brand<string, "RegistryId">;
type RegistryVersionId = Brand<string, "RegistryVersionId">;
type ProcessEntryId = Brand<string, "ProcessEntryId">;
type Revision = string;
type UtcInstant = string;

type DigestRef = {
  algorithmId: string;       // policy identity only; no algorithm selected
  algorithmVersion: string;
  domain: string;
  value: string;
};

type IdentityContext = {
  projectStableId: string;
  projectRevision: Revision;
  inputRevision: Revision;
  stackupId: string;
  stackupRevision: Revision;
  topologyRevision: Revision;
  graphContractVersion: string;
  predicateId: string;
  predicateVersion: string;
  kernelId: string;
  kernelVersion: string;
  contextDigest: DigestRef;
};

type GeometryOutcome =
  | { kind: "positive-area-overlap"; proofClaim: ExactOrBoundedAreaClaim }
  | { kind: "boundary-contact"; proofClaim?: ExactOrBoundedBoundaryClaim }
  | { kind: "separated"; proofClaim: ExactOrBoundedSeparationClaim }
  | { kind: "indeterminate"; reasonCodes: readonly string[]; bounds?: NumericBounds }
  | { kind: "invalid-geometry"; reasonCodes: readonly string[] }
  | { kind: "unsupported-geometry"; featureId: string; capabilityVersion?: string };

type ExactOrBoundedAreaClaim =
  | { kind: "exact"; intersectionArea: ExactArea }
  | { kind: "bounded"; intersectionArea: { lower: number; upper: number; unit: string } };
type ExactOrBoundedBoundaryClaim = { kind: "exact"; signedSeparation: 0; intersectionArea: 0 };
type ExactOrBoundedSeparationClaim =
  | { kind: "exact"; signedSeparation: PositiveExactLength }
  | { kind: "bounded"; signedSeparation: { lower: number; upper: number; unit: string } };
```

`ExactArea`, `PositiveExactLength`, and `NumericBounds` are abstract proof-domain types. Their representation, units, interval soundness, and serialization must be approved by geometry/predicate owners. A bounded overlap is eligible only if approved sound bounds prove strictly positive area; a bound that includes zero is indeterminate. No epsilon, snap, or manufacturing tolerance is introduced by this schema. [1] [4]

### 4.2 Microvia assembly, stages, memberships, transitions, and junctions

```ts
type MicroviaArrangement = "stacked" | "staggered";
type ContinuityClaim = "continuous" | "non-continuous";
type TopologyDeclaration = "linear" | "branching" | "cyclic" | "unknown";

type MicroviaAssembly = {
  schemaVersion: "microvia-assembly/1"; // proposed placeholder
  id: AssemblyId;
  revision: Revision;
  context: IdentityContext;
  arrangement: MicroviaArrangement;
  continuityClaim: ContinuityClaim;
  topology: TopologyDeclaration;
  stages: readonly MicroviaStage[];                    // backing order is nonsemantic
  memberships: readonly StageNodeMembership[];        // sole membership source
  orderedStageIds: readonly StageId[];                // sole authoritative sequence
  transitions?: readonly StageTransition[];           // exact checked mirror only
  junctions: readonly StageJunction[];                 // candidate records, not edges
};

type MicroviaStage = {
  schemaVersion: "microvia-stage/1"; // proposed placeholder
  id: StageId;
  fromLayerId: LayerId;
  toLayerId: LayerId;
  processEvidence:
    | { state: "present"; record: MicroviaProcessEvidence }
    | { state: "missing"; reasonCode: string; sourceSchema?: string };
};

type StageNodeMembership = {
  schemaVersion: "stage-node-membership/1"; // proposed placeholder
  id: MembershipId;
  stageId: StageId;
  copperNodeId: CopperNodeId;
  role: "stage-land" | "stage-node" | "other-declared-role";
  sourceRef?: string;
};

type StageTransition = {
  schemaVersion: "stage-transition/1"; // proposed placeholder
  id: TransitionId;
  assemblyId: AssemblyId;
  assemblyRevision: Revision;
  ordinal: number;                                  // contiguous, zero-based
  fromStageId: StageId;                             // directed endpoint
  toStageId: StageId;                               // directed endpoint
  junctionIds?: readonly JunctionId[];               // references only
};

type StageJunction = {
  schemaVersion: "stage-junction/1"; // proposed placeholder
  id: JunctionId;
  assemblyId: AssemblyId;
  assemblyRevision: Revision;
  transitionId: TransitionId;
  fromStageId: StageId;
  toStageId: StageId;
  fromNodeId: CopperNodeId;
  toNodeId: CopperNodeId;
  contactLayerId: LayerId;
  evidence: TransitionEvidence;
};

type TransitionEvidence =
  | {
      state: "certified-claim"; // assertion to validate, never trusted as a Boolean
      contactId: ContactId;
      evidenceIds: readonly EvidenceId[];
      claimedOutcome: "positive-area-overlap";
      context: IdentityContext & {
        nodeIds: readonly [CopperNodeId, CopperNodeId]; // canonical pair
        contactLayerId: LayerId;
        geometryHashes: readonly [DigestRef, DigestRef]; // aligned to nodeIds
        predicateId: string;
        predicateVersion: string;
        kernelId: string;
        kernelVersion: string;
      };
    }
  | { state: "not-connected"; reasonCode: string; context?: IdentityContext }
  | { state: "indeterminate"; reasonCode: string; evidenceIds?: readonly EvidenceId[]; context?: IdentityContext }
  | { state: "missing"; reasonCode?: string }
  | { state: "stale"; reasonCode: string; evidenceIds: readonly EvidenceId[] }
  | { state: "unverifiable"; reasonCode: string; evidenceIds?: readonly EvidenceId[] }
  | { state: "unsupported"; reasonCode: string; capabilityId?: string }
  | { state: "invalid"; reasonCodes: readonly string[]; evidenceIds?: readonly EvidenceId[] }
  | { state: "contradictory"; reasonCodes: readonly string[]; evidenceIds: readonly EvidenceId[] };
```

The direction belongs to `StageTransition`; the underlying physical contact pair is unordered and canonicalized independently. The assembly’s `orderedStageIds` is the sole manufacturing/validation order source proposed here. If `transitions[]` is persisted, it is a mirror and must exactly match derived adjacent pairs in ordinal order. No stage or junction backing-array order is authoritative.

`stacked` and `staggered` are retained as manufacturing arrangement labels only. They are not geometric evidence. A nearby staggered land is not continuity; a stacked declaration is not continuity. Stage endpoints, allowable adjacency, capture lands, depth, fabricator/material limits, and whether an intermediate land implies any stage-internal conduction require product-owner decisions. [1] [2] [3] [4]

### 4.3 Process evidence attached to a stage

```ts
type ProcessIdentity = {
  namespace: string;
  processType: string;         // opaque identity; no supported taxonomy selected
  processId: string;
  processRevision?: string;
  variant?: string;
};

type ProcessEvidenceRef = {
  schemaVersion: string;
  evidenceId: EvidenceId;
  mediaType: string;
  contentDigest: DigestRef;
  resolverId: string;
  resolverVersion: string;
  processIdentityDigest: DigestRef;
  registryId: RegistryId;
  registryVersionId: RegistryVersionId;
  projectStableId: string;
  projectRevision: Revision;
  assemblyId: AssemblyId;
  topologyRevision: Revision;
  stageId: StageId;
  purpose: string;
  contextDigest: DigestRef;
  issuedAt?: UtcInstant;
  expiresAt?: UtcInstant;
  provenance: readonly ProvenanceRecord[];
};

type ProvenanceRecord = {
  kind: "explicit-model" | "verified-library" | "manufacturing-import" |
        "human-assertion" | "derived" | "current-run";
  sourceId: string;
  sourceVersion?: string;
  sourceDigest?: DigestRef;
  locator?: string;
};

type MicroviaProcessEvidence = {
  schemaVersion: "microvia-process-evidence/1"; // proposed placeholder
  stageId: StageId;
  process: ProcessIdentity;
  processSpecificationVersion: string;
  registryRef: { registryId: RegistryId; versionId: RegistryVersionId; snapshotDigest: DigestRef };
  evidence: readonly ProcessEvidenceRef[];
  provenance: readonly ProvenanceRecord[];
  verifier: { id: string; version: string; contractVersion: string };
  contextDigest: DigestRef;
};

type ProcessVerificationState =
  | "verified-supported" | "explicitly-unsupported" | "missing" | "unknown"
  | "unverifiable" | "stale" | "invalid" | "contradictory";
```

The legacy source kinds are preserved as provenance vocabulary, but a source label or hash does not verify the evidence. Missing, unknown, unverifiable, stale, invalid, contradictory, explicitly unsupported, and verified-supported remain distinct. Only an explicit unsupported entry, or a determinate absence under authenticated, authorized, current, applicable closed-world coverage, can produce an unsupported-process result. Partial or unavailable coverage yields unknown. [1] [2] [4]

### 4.4 Derived Microvia validation result

```ts
type TransitionValidationState =
  | "certified-current" | "known-not-connected" | "missing" | "unknown"
  | "invalid" | "unsupported" | "contradictory" | "ambiguous";

type MicroviaValidationResult = {
  schemaVersion: "microvia-validation-result/1"; // proposed placeholder
  assemblyId: AssemblyId;
  assemblyRevision: Revision;
  contextDigest: DigestRef;
  structuralState: "valid" | "unknown" | "invalid" | "unsupported" | "contradictory";
  processStateByStage: readonly {
    stageId: StageId;
    state: ProcessVerificationState;
    reasonCodes: readonly string[];
    registryVersionId?: RegistryVersionId;
  }[];
  transitionResults: readonly {
    transitionId: TransitionId;
    ordinal: number;
    fromStageId: StageId;
    toStageId: StageId;
    state: TransitionValidationState;
    geometryOutcome?: GeometryOutcome["kind"];
    acceptedJunctionId?: JunctionId;
    contactId?: ContactId;
    diagnosticRefs: readonly string[];
  }[];
  connectivityState: "complete" | "incomplete" | "unknown" | "invalid" |
                    "unsupported" | "contradictory";
  admittedInterStageEdges: readonly {
    transitionId: TransitionId;
    junctionId: JunctionId;
    contactId: ContactId;
    nodeIds: readonly [CopperNodeId, CopperNodeId];
    layerId: LayerId;
  }[];
  retainedWithinStageEdges: readonly {
    stageId: StageId;
    contactId: ContactId;
    nodeIds: readonly [CopperNodeId, CopperNodeId];
    layerId: LayerId;
  }[];
  unresolvedCandidates: readonly string[];
  diagnostics: readonly string[]; // registered RuleIds only; otherwise state is retained
};
```

`complete` means an accepted continuous linear chain satisfying all required structural, process, and contact conditions; a syntactically valid assembly is not by itself electrically complete. `incomplete` is used for known missing required coverage or a verified `not-connected` required pair. `unknown` means current evidence is insufficient. `invalid` means malformed/impossible references or ownership. `unsupported` means recognized but unapproved/unsupported topology or capability. `contradictory` preserves incompatible claims without selecting a winner. Per-stage/per-transition states coexist; a global summary must not erase independently validated edges.

## 5. Field constraints and referential integrity

1. IDs and version fields are nonempty stable identities, not display labels. No normalization/canonical bytes/digest profile is frozen here. Unknown schema versions are rejected unless a specific reviewed adapter exists. Strict parsing preserves raw multiplicity and rejects duplicate object keys/types without coercion.
2. Stage IDs are unique within an assembly before any index/map is built. Assembly identity is stable; revision changes when topology, membership, stages, evidence binding, or other identity-bearing content changes under a future approved revision policy.
3. `orderedStageIds` is nonempty for a continuous claim and must be an exact one-to-one permutation of the declared StageIds. Its array order is authoritative. `stages[]`, `memberships[]`, `junctions[]`, and evidence-array order have no semantic meaning. Equivalent permutations with unchanged orderedStageIds and identity-bearing content must yield the same result.
4. Expected transitions are derived only from adjacent sequence entries. For `[s0, s1, …, sn]`, the exact expected set/order is `(s0→s1), (s1→s2), …, (s(n-1)→sn)`. Every derived identity includes the assembly/topology revision, ordinal, and directed endpoints under the eventual identity profile. Direction cannot be repaired or reversed implicitly.
5. If the optional serialized transition mirror exists, it must match the derived list exactly: unique IDs, contiguous zero-based ordinals, exact directed endpoints, no duplicate, missing, extra, reversed, or permuted entries. A nonconsecutive chord does not cover any expected transition.
6. Each stage endpoint LayerId resolves in the current validated Stackup to a distinct enabled copper layer. The `layersFrontToBack` order is the only physical ordering source. A disabled, non-copper, unknown, duplicate, or contradictory layer reference is invalid; absent current Stackup is unknown. No layer is inferred from a name or numeric label.
7. Multiple land/node memberships per stage are permitted. Each `StageNodeMembership` points to exactly one valid StageId and one conductive CopperNodeId. A CopperNodeId may be owned by exactly one stage in the supported linear model. Duplicate membership, shared ownership, dangling node, or wrong stage attribution is invalid. Membership is attribution, not evidence that all members connect to each other.
8. Each junction references exactly one derived expected transition. Its directed StageIds match that transition; its distinct endpoint nodes exist and belong exactly to the respective source and target stages; the contact layer and current node layers match the exact compatible enabled copper layer. A witness for a different pair/layer cannot substitute.
9. ContactId, evidence references, geometry hashes, context digest, predicate/kernel versions, project/revision, Stackup/topology revision and proof bytes are independently recomputed or resolved. Stale coherent data is stale/unknown, not separated. Impossible or internally contradictory bindings are invalid/contradictory as applicable.
10. Exactly one accepted junction witness is required for each expected transition of a continuous linear path. Several evidence contributions may support one canonical ContactId, but they do not create several graph edges. Distinct junction/node-pair candidates for one transition are ambiguous absent explicit multiplicity policy; no first-wins, nearest, count, or majority selection.
11. Valid current positive-area proof is the only proposed geometry outcome eligible for the junction gate. `boundary-contact`, `separated`, `indeterminate`, `invalid-geometry`, `unsupported-geometry`, stale, missing, unavailable, unverifiable, or contradictory evidence admits no edge. A proved separation is a known non-contact for that exact pair and makes a required continuous path incomplete.
12. Branching and cyclic topology are representable but not supported by this proposed linear-path validator. Return `unsupported` or policy-unresolved; do not silently treat them as invalid or as supported. An extra cycle-closing or nonconsecutive record never adds an edge or waives expected transitions. Product owner must decide whether the model should support these topologies.
13. Valid within-stage edges are derived under their own physical evidence contract. Failure in another stage, process gate, transition, or junction does not remove a separately certified within-stage edge. Stage membership does not create a within-stage edge.

## 6. Registry trust, authenticity, and revocation contract

### 6.1 Trust model

The proposal models a registry as an immutable, versioned manifest with canonical payload digest, envelope/snapshot digest, signatures, issuer assertions, explicit coverage, entries, revocation checkpoint, and provenance. The verifier validates the exact payload bytes against an externally configured, versioned trust policy. A digest detects mismatch but does not establish origin. A signature establishes a cryptographic relationship to a key under a policy; it does not alone establish issuer authorization, currentness, process suitability, physical validity, or contact continuity.

TUF is a useful precedent for separating signed role metadata, key/role thresholds, monotonic versions, expiry, root rotation, and coherent versioned snapshots. NIST key-management guidance treats revocation and compromise as lifecycle states. These sources inform the proposed separation only; they do not select a TUF format, a NIST algorithm, any production cryptographic suite, authority, trust root, threshold, or freshness window for PCB Studio Pro. [7] [8]

### 6.2 TypeScript-like trust schemas

```ts
type AuthorityIdentity = {
  namespace: string;
  authorityId: string;
  identityVersion: string;
};

type SigningKeyIdentity = {
  authority: AuthorityIdentity;
  keyId: string;
  keyVersion: string;
  publicKeyFingerprint: DigestRef; // fingerprint reference only; no key material selected
};

type ScopeSelector = {
  namespace: string;
  registryId?: RegistryId;
  processIdentityDigest?: DigestRef;
  projectStableId?: string;
  stageId?: StageId;
  fabricatorIdentity?: string;
  materialContextDigest?: DigestRef;
};

type IssuerAuthorization = {
  authority: AuthorityIdentity;
  issuerId: string;
  roleId: string;
  registryIds: readonly RegistryId[];
  scopes: readonly ScopeSelector[];
  notBefore: UtcInstant;
  notAfter: UtcInstant;
  policyVersion: string;
};

type RegistryIssuer = {
  authority: AuthorityIdentity;
  issuerId: string;
  roleId: string;
  assertedScopes: readonly ScopeSelector[]; // claim, checked against trusted delegation
  authorizationRef: string;
};

type SignaturePolicyRef = {
  policyId: string;
  policyVersion: string;
  allowedAlgorithmProfiles: readonly { algorithmId: string; algorithmVersion: string }[];
  allowedKeyIdentityVersions: readonly string[];
  signedBytesProfileId: string;
  signedBytesProfileVersion: string;
  thresholdPolicyId: string;
  thresholdPolicyVersion: string;
};

type RegistrySignature = {
  signatureId: string;
  algorithmId: string;             // identity under configured policy; not selected here
  algorithmVersion: string;
  key: SigningKeyIdentity;
  signatureEncoding: string;
  signatureBytes: string;
  signedPayloadDigest: DigestRef;
  signedBytesProfileId: string;
  signedBytesProfileVersion: string;
  signaturePolicy: SignaturePolicyRef;
};

type RegistryVersion = {
  registryId: RegistryId;
  versionId: RegistryVersionId;
  sequence: number;
  schemaVersion: string;
  registryPolicyVersion: string;
  issuedAt: UtcInstant;
  expiresAt: UtcInstant;
  supersedes: readonly {
    registryId: RegistryId;
    versionId: RegistryVersionId;
    sequence: number;
    manifestDigest: DigestRef;
  }[];
  signaturePolicy: SignaturePolicyRef;
  trustEpoch: number;
};

type CoverageDeclaration = {
  namespace: string;
  completeness: "partial" | "closed-world";
  dimensions: readonly string[];
  scope: readonly ScopeSelector[];
  coverageVersion: string;
};

type CapabilityEntry = {
  entryId: ProcessEntryId;
  process: ProcessIdentity;
  processIdentityDigest: DigestRef;
  status: "supported" | "unsupported";
  scope: readonly ScopeSelector[];
  validFrom: UtcInstant;
  validUntil?: UtcInstant;
  validatedRuleContract?: { contractId: string; contractVersion: string };
  acceptedEvidenceKinds: readonly string[];
  acceptedVerifiers: readonly { verifierId: string; verifierVersion: string; contractVersion: string }[];
  supersedesEntryIds: readonly ProcessEntryId[];
};

type RegistryProvenance = {
  kind: string;
  sourceId: string;
  sourceVersion?: string;
  sourceDigest?: DigestRef;
  locator?: string;
};

type RegistryManifestPayload = {
  schemaVersion: string;
  registry: RegistryVersion;
  issuer: RegistryIssuer;
  coverage: readonly CoverageDeclaration[];
  entries: readonly CapabilityEntry[];
  revocationCheckpoint?: { sequence: number; digest: DigestRef; observedAt: UtcInstant };
  provenance: readonly RegistryProvenance[];
};

type RegistryManifest = {
  payload: RegistryManifestPayload;
  canonicalPayloadDigest: DigestRef;
  snapshotId: string;
  signatures: readonly RegistrySignature[];
  envelopeDigest: DigestRef;
};

type RevocationSubject =
  | { kind: "key"; authority: AuthorityIdentity; keyId: string; keyVersion: string }
  | { kind: "issuer-authorization"; authority: AuthorityIdentity; issuerId: string; authorizationRef: string }
  | { kind: "registry-version"; registryId: RegistryId; versionId: RegistryVersionId; manifestDigest: DigestRef }
  | { kind: "process-capability"; processIdentityDigest: DigestRef; scope: readonly ScopeSelector[] };

type RevocationRecord = {
  schemaVersion: string;
  revocationId: string;
  sequence: number;
  subject: RevocationSubject;
  action: "revoke" | "suspend" | "reinstate";
  effectiveAt: UtcInstant;
  issuedAt: UtcInstant;
  reasonCode: string;
  retroactiveTo?: UtcInstant;
  supersedesRevocationIds: readonly string[];
  issuer: RegistryIssuer;
  signedPayloadDigest: DigestRef;
  signatures: readonly RegistrySignature[];
};

type TrustAnchorSet = {
  trustRootSetId: string;
  trustEpoch: number;
  provisionedByPolicy: string;
  provisioningProvenance: readonly RegistryProvenance[];
  rootKeyIdentities: readonly SigningKeyIdentity[]; // identities/fingerprints only
  thresholdPolicyId: string;
  notBefore?: UtcInstant;
  notAfter?: UtcInstant;
};

type RootRotationLink = {
  fromTrustEpoch: number;
  toTrustEpoch: number;
  predecessorRootSetId: string;
  successorRootSetId: string;
  predecessorAuthorization: readonly RegistrySignature[];
  successorAuthorization: readonly RegistrySignature[];
  transitionSequence: number;
};

type TrustPolicy = {
  policyId: string;
  policyVersion: string;
  signaturePolicy: SignaturePolicyRef;
  initialTrustAnchors: readonly TrustAnchorSet[];
  acceptedIssuers: readonly IssuerAuthorization[];
  acceptedRootRotations: readonly RootRotationLink[];
  canonicalization: { profileId: string; profileVersion: string };
  digestPolicy: { allowedProfiles: readonly { algorithmId: string; algorithmVersion: string }[]; profileVersion: string };
  freshness: {
    requireExpiry: true;
    maxOfflineAgeSeconds?: number;
    revocationCheckpointMaxAgeSeconds?: number;
    trustedClockRequirement: string;
    rollbackStoreId: string;
    supersessionPolicyVersion: string;
  };
  revocation: {
    requiredSources: readonly string[];
    policyVersion: string;
    compromiseRetroactivityPolicyVersion: string;
  };
  offlinePolicyVersion: string;
  projectBindingPolicyVersion: string;
};

type ProcessVerificationResult = {
  schemaVersion: string;
  projectStableId: string;
  projectRevision: Revision;
  assemblyId: AssemblyId;
  topologyRevision: Revision;
  stageId: StageId;
  processIdentityDigest?: DigestRef;
  registrySnapshotId?: string;
  claims: {
    digestIntegrity: "verified" | "mismatch" | "unavailable" | "not-evaluated";
    registryAuthenticity: "verified" | "invalid-signature" | "unknown-key" | "unsupported-policy" | "unavailable" | "not-evaluated";
    issuerAuthorization: "authorized" | "unauthorized" | "unknown-authority" | "out-of-scope" | "not-evaluated";
    registryCurrentness: "current" | "expired" | "superseded" | "rollback" | "revoked" | "stale-offline" | "unknown" | "not-evaluated";
    processCapability: ProcessVerificationState | "not-evaluated";
    physicalStage: "valid" | "invalid" | "unknown" | "unsupported" | "not-evaluated";
    electricalJunction: "verified-current" | "missing" | "unverifiable" | "stale" | "invalid" | "unsupported" | "not-connected" | "not-evaluated";
  };
  processGateEligible: boolean;
  graphEdgeAdmitted: false; // only graph validator can admit after all gates
  validationContextDigest: DigestRef;
  trustPolicyVersion: string;
  checkedAt?: UtcInstant;
  revocationCheckpoint?: DigestRef;
  reasonCodes: readonly string[];
  provenance: readonly RegistryProvenance[];
};
```

The types name policy inputs and outcomes; they do not define a production authority, key, algorithm, threshold, registry, or process taxonomy. `RegistryIssuer.assertedScopes` are assertions and are never authorization. Registry and signature profiles must be externally configured and versioned. Unknown profiles are rejected, not silently upgraded.

### 6.3 Verification, rotation, revocation, and offline behavior

1. **Strict parse and immutable identity.** Parse only an explicitly supported schema/profile. Retain exact signed bytes and raw row multiplicity. Validate payload/envelope digests against resolved bytes and reject mismatch, duplicate identity, conflicting entry, or unsupported version. Canonicalization and digest algorithms remain product decisions.
2. **Authenticity.** Verify the signature threshold and signed-byte profile under an already trusted, versioned policy. A content digest alone is not authenticity. A mathematically valid signature from an unknown or disallowed key is not an accepted registry signature.
3. **Issuer authorization.** Separately verify that the signer/issuer has trusted delegation for the exact registry, role, operation, process namespace/scope, validity interval, and policy version. A valid signature does not authorize an out-of-scope issuer.
4. **Root provisioning and rotation.** Bootstrap trust anchors through a product-approved out-of-band process with provenance. A root update must be an explicit authenticated trust-policy transition linked to the previously trusted epoch and the successor policy; persist accepted epoch/high-water state. Do not accept a root from the registry it would authorize or silently replace local roots after a fetch failure. Recovery from compromise/loss remains owner policy.
5. **Currentness and rollback.** Enforce issue/expiry, monotonic sequence/high-water, authenticated supersession, trust epoch, and revocation state. Reject rollback below stored sequence. A superseded or expired manifest may be historically authentic but is not current. Conflicting or duplicate capability rows with overlapping identity/scope are contradictory, not resolved by first/last order.
6. **Revocation.** Treat signing-key, issuer-delegation, registry-snapshot, and process-capability revocation as distinct subjects. Validate revocation record signature/authority, sequence, scope, effective time, supersession, and checkpoint. Compromised-key treatment and retroactivity are policy choices. NIST lifecycle guidance supports explicit compromised/revoked states but does not choose product policy. [8]
7. **Coverage and process result.** `verified-supported` requires acceptable current registry authenticity, authorized in-scope issuer, valid current coverage, one applicable capability contract, accepted evidence provenance/verifier, and exact project/assembly/stage/process context. Explicit unsupported requires an explicit applicable unsupported row or absence under authenticated, current, complete closed-world coverage for every query dimension. Missing rows in partial coverage, unavailable registry, unresolved scope, or incomplete evidence remain unknown.
8. **Replay/context binding.** Bind evidence to immutable content digest, project stable ID/revision, assembly/topology revision, stage, process identity, registry snapshot, purpose, and context digest. Reject cross-project, cross-stage, cross-process, cross-revision, or cross-purpose replay. Nonce/challenge handling is not imposed on static records unless a later approved protocol defines it.
9. **Offline behavior.** Offline mode may report historically verified authenticity after local re-verification of immutable bytes. It may report current only if expiry, anti-rollback, supersession, trusted-time, and revocation-checkpoint freshness satisfy configured policy. Without required freshness or revocation evidence, return stale/unknown/unverifiable—not supported and not unsupported. Fail closed for process-gated inter-stage edges. Independent within-stage contact validation and schema-v2 all-pairs clearance continue.
10. **No implicit physical/electrical conclusion.** A supported process entry does not prove that a specific Via/stage is physically valid. A physically valid stage does not prove an electrical junction. Only the independent physical and junction validators can produce those states. The trust result itself always reports `graphEdgeAdmitted: false`.

## 7. Microvia validation and state-transition contract

### 7.1 Deterministic algorithm

```text
validateMicroviaAssembly(rawAssembly, validatedStackup, currentContext, trustPolicy):
  parse strict supported schema; preserve raw order, multiplicity, and row locations
  reject unknown versions without an explicit reviewed adapter
  validate assembly identity/revision/context; absent required context => unknown

  scan raw stage IDs and membership IDs for duplicates before indexing
  reject duplicate StageIds; never choose first/last record
  validate orderedStageIds as exact permutation of declared StageIds
  derive only consecutive directed transitions from orderedStageIds
  if transitions mirror exists, compare each ordinal/id/from/to exactly
  validate each stage endpoint against current canonical Stackup and enabled copper layers
  validate every StageNodeMembership and exact one-stage ownership
  record topology=branching/cyclic as unsupported/policy-unresolved in this linear model

  for each stage process record:
    if absent/missing: process=missing; do not call unsupported
    else validate evidence digest, registry signature/issuer/currentness/revocation/coverage
    bind process evidence to exact project/revision/assembly/topology/stage/process/purpose
    classify verified-supported / explicit-unsupported / unknown / unverifiable /
      stale / invalid / contradictory

  for each required consecutive transition:
    resolve only junctions referencing that exact directed transition
    reject dangling, reversed-only, duplicate, chord, wrong-node, wrong-layer records
    group evidence by canonical contact identity while preserving direction/provenance
    current contradictory evidence => contradictory; do not choose a winner
    distinct candidate node pairs without multiplicity policy => ambiguous/unsupported
    resolve immutable proof and independently verify exact pair/layer/context/hashes
    only verified-current positive-area-overlap can become edge-eligible
    boundary/separated/indeterminate/stale/missing/unverifiable/unsupported/invalid => no edge
    admit at most one edge for the unique accepted contact/transition

  preserve independent validated within-stage edges and existing definite graph findings
  do not let NetId, membership, labels, proximity, arrangement, or ordering create edges
  run legacy v2 minimumViaClearance all-pairs independently
  finalize only registered diagnostics; retain unresolved typed states and provenance
  sort nonsemantic results canonically while preserving orderedStageIds sequence
  return structural, per-stage process, per-transition, overall connectivity, edges and findings
```

A failed stage or transition does not erase another valid edge. A short already established from confirmed physical edges remains definite. Duplicate/reversed transition records are diagnosed only through an approved registry rule; they do not create extra edges or satisfy forward coverage. Cycles and branches do not create extra physical connectivity or waive a required transition.

### 7.2 State-transition table

| Input/result condition | Typed state | Diagnostic contract | Edge eligibility | Connectivity consequence |
|---|---|---|---|---|
| Valid structure, current supported process, one exact current positive-area witness | structural `valid`; process `verified-supported`; transition `certified-current` | No failure finding | One edge for the exact accepted contact | Can contribute to `complete` if every other requirement passes |
| Stage process record absent | process `missing`; overall connectivity `unknown` | Missing-process RuleId unresolved; never unsupported | No process-gated edge | Required process gate unresolved |
| Unknown process under partial/incomplete coverage | process `unknown` | No `PCB_VIA_PROCESS_UNSUPPORTED`; missing/unknown ID unresolved | No edge | Unknown, not unsupported |
| Explicit unsupported entry or conclusive closed-world exclusion | process `explicitly-unsupported` | `PCB_VIA_PROCESS_UNSUPPORTED` audit-proposed only | No process-gated edge | Unsupported path/capability |
| Registry authenticity fails | registry authenticity `invalid-signature` or policy failure; process `unverifiable` | Trust RuleId unresolved | No process-gated edge | Unknown/unverifiable; not unsupported |
| Issuer signature passes but authorization/scope fails | issuer `unauthorized`/`out-of-scope` | Trust RuleId unresolved | No process-gated edge | Unverifiable authorization |
| Expired, superseded, revoked, rollback, or stale offline registry | currentness typed expired/superseded/revoked/rollback/stale | Trust RuleId unresolved | No edge from stale registry evidence | Current support unavailable |
| Exact geometry proof establishes separated pair | transition `known-not-connected` | `PCB_MICROVIA_JUNCTION_INDETERMINATE` audit-proposed under expected path completeness trigger; wording/trigger pending | No edge | Required continuous path `incomplete` |
| Boundary-only witness while tangent policy pending | geometry `boundary-contact`; transition `unknown` | Junction RuleId audit-proposed; contact-specific ID candidate/unapproved | No edge | Unknown/policy-pending |
| Missing, stale, unavailable, unverifiable or indeterminate witness | transition `missing`/`unknown` | Junction RuleId audit-proposed when structural preconditions pass | No edge | Unknown/incomplete as reason warrants |
| Duplicate StageId, wrong ownership, invalid layer, or malformed transition mirror | structural `invalid` | `PCB_MICROVIA_STAGE_REFERENCE_INVALID` audit-proposed | No affected edge; unrelated valid edges retained | Invalid affected assembly/transition |
| Reversed-only record | expected forward transition remains `missing`/`unknown`; reverse does not cover | Junction finding for missing expected transition; separate malformed-record ID unresolved | No edge from reversed-only record | Incomplete/unknown |
| Nonconsecutive chord | structural transition reference `invalid` for coverage | Stage-reference finding audit-proposed; avoid duplicate derivative finding for same root | No chord edge | Required consecutive coverage still absent |
| Two distinct plausible node pairs, no multiplicity rule | transition `ambiguous`/`unsupported` | Junction finding audit-proposed; separate multiplicity ID unresolved | Neither candidate admitted | Unsupported/policy-pending |
| Contradictory current evidence for same identity | transition `contradictory` | Contact conflict ID is candidate; otherwise typed state retained | No edge | Contradictory |
| Branch/cycle in a model limited to linear paths | `unsupported`/policy-unresolved, not auto-invalid | RuleId unresolved; no invented cycle severity | Expected valid transitions may remain individually eligible; no extra branch/cycle edge | Cannot claim complete until topology policy resolves |

## 8. Microvia structural adversarial scenarios

These are expected outcomes, not executed tests. They supplement the mandatory cross-domain matrix in §10.

| # | Adversarial input | Expected typed outcome and graph result |
|---:|---|---|
| 1 | Stage records permuted while `orderedStageIds` stays fixed | Identical derived transition order and results; no order diagnostic. |
| 2 | `orderedStageIds` omits or repeats a StageId | Structural `invalid`; no complete claim and no edge that relies on ambiguous sequence. |
| 3 | Two stage records share the same StageId | Structural `invalid`; no first/last selection; unrelated valid contacts remain. |
| 4 | One StageNodeMembership references a missing StageId | Structural `invalid`; reject affected membership and junctions. |
| 5 | One CopperNodeId is owned by two stages | Structural `invalid` under the proposed linear model; neither ownership wins. |
| 6 | Stage owns multiple distinct lands, each with correct ownership | Structurally permitted; ownership does not connect the lands; required intra-stage contacts need their own evidence. |
| 7 | Stage endpoints name same layer | Invalid under this proposal because endpoints must be distinct; do not infer zero-depth continuity. |
| 8 | Endpoint LayerId is unknown/non-copper/disabled | Invalid if contradiction is established; no affected edge. Missing Stackup context is unknown instead. |
| 9 | Correct expected S1→S2 record, but proof node pair includes S3 node | Microvia reference invalid; proof may only create an ordinary contact edge if independently validated for its own exact pair. |
| 10 | Proof node pair is correct but contact layer is wrong/disabled | Invalid binding; no Microvia edge. |
| 11 | Stage membership is valid but transition node belongs to wrong stage | Invalid ownership; no claimed transition edge. |
| 12 | Expected S1→S2, only S2→S1 supplied | Reverse does not cover forward transition; no edge. |
| 13 | Ordered [S1,S2,S3], only S1→S3 supplied | Chord invalid as coverage; no shortcut; S1→S2 and S2→S3 remain uncovered. |
| 14 | Ordered [S1,S2,S3,S4], missing S2→S3 but outer transitions valid | Keep valid S1→S2 and S3→S4 edges; no middle edge; whole continuous path incomplete. |
| 15 | Exact duplicate StageTransition/Junction bytes persisted | Detect raw duplicate before normalization; no extra edge. Diagnostic ID depends on approved registry. |
| 16 | Correct/reversed duplicate pair with conflicting current evidence | Preserve both; classify contradiction; no majority/arrival-order choice; no edge for conflict. |
| 17 | Two different node-pair candidates for one expected transition | Ambiguous absent multiplicity policy; admit neither candidate for that transition. |
| 18 | One ContactId has several compatible evidence records | One contact witness identity and maximum one edge; retain all distinct evidence/provenance. |
| 19 | Same ContactId has both positive overlap and separated current claims | Contradictory; preserve both; no edge. |
| 20 | Geometry hash or project/topology/Stackup revision is stale | Stale/unknown, not separated; no edge; independent current transitions remain. |
| 21 | Proof is current and geometry is exactly separated | Known-not-connected; no edge; required path is incomplete. |
| 22 | Proof is boundary/tangent only | Preserve boundary; no edge while electrical semantics pending. |
| 23 | Assembly declares `stacked`, with no proof | Arrangement is non-evidentiary; no edge. |
| 24 | Assembly declares `staggered`, with close lands | Proximity and arrangement do not establish a junction; no edge. |
| 25 | One transition fails while another stage has a valid within-stage contact | Retain independently validated within-stage contact; assembly remains incomplete/unknown. |
| 26 | Extra S3→S1 closes cycle after valid S1→S2 and S2→S3 | Detect cycle; no extra cycle edge; valid expected edges remain; topology policy pending. |
| 27 | Branching declaration with multiple outgoing stage paths | Represent as unsupported in this linear validator; no inferred branch semantics. |
| 28 | Same NetId labels nodes in disconnected stages | No physical union; NetId never creates continuity. |
| 29 | Confirmed short exists elsewhere plus stale Microvia witness | Preserve the short and separately retain the stale/unknown Microvia status. |
| 30 | Reorder junction/evidence arrival or repeat union request | Same edge/findings identities; one application per ContactId; no order-dependent result. |

## 9. Proposed diagnostic registry

### 9.1 Registry and identity rules

Every production rule must have a centrally approved registration containing a stable RuleId, semantics version, canonical owner, allowed primary and secondary producers, exact trigger and preconditions, subject/attribution fields, canonical occurrence-key fields, dedup/conflict behavior, cross-rule causal relations, severity, DRC-clear effect, and product-owner approval. Validators submit candidates; the registry checks registration and recomputes occurrence identity. An unregistered candidate name is not a production diagnostic.

The proposed occurrence identity is a domain-separated canonical object over RuleId, semantics version, normalized stable project scope, and only that rule’s registered key fields. A versioned canonical digest is a candidate implementation choice, not approved. Exclude producer, text, severity, time, insertion order, DSU root, NetId, and evidence multiplicity unless the approved rule expressly includes a field. Retain producer/evidence/provenance references separately in canonical order. Identity-bearing conflicts remain conflicts, not first/last/majority-wins. [3] [4]

Status shorthand used below: **H** = historical ID/behavior from 6.0.3, carried forward; **P** = Phase 6.0.4 audit-proposed; **C** = candidate names from 6.0.5; **U** = unresolved RuleId or policy. A proposed label such as `historical-6.0.3` is registry metadata for review, not a source-declared/frozen semantics version.

### 9.2 Fifteen-family registry table

| # / family and RuleId status | Semantics version, canonical owner, allowed producers | Trigger and preconditions | Attribution and occurrence key | Deduplication, precedence, and coexistence | Severity, DRC-clear status, and approval |
|---|---|---|---|---|---|
| **1. NetAssignment invalid/conflicting/incomplete. H:** `PCB_NET_ASSIGNMENT_INVALID`, `PCB_NET_ASSIGNMENT_CONFLICT`, `PCB_NET_ASSIGNMENT_INCOMPLETE`. | Carry-forward label `legacy-6.0.3` proposed only. Owner: NetAssignment validator. Primary producer: assignment validator. Graph/classifier and import validators may reference or provide evidence, not re-own. | Invalid: malformed/missing/wrong-project assignment reference. Conflict: conflicting state or disagreeing source claims. Incomplete: expected-but-unassigned, unknown, unverified candidate, or electrically expected intentional-unassigned. Preserve the exact seven assignment states and claim provenance. | Attribute object and assignment record/raw value/reason. Invalid key per object/assignment record. Conflict key `(objectId, canonicalClaimSetHash)`. Incomplete key per object; grouped component key only after approved cap. | Coalesce same rule/key; preserve conflict claims. Invalid, conflict, incomplete may coexist with physical findings and one another when independent. Do not convert assignment state or suppress short/clearance. | Severity and DRC-clear mapping pending; incomplete aggregation cap pending. Historical contract carried forward; final production registry approval remains pending in 6.0.3. |
| **2. Definite copper short. H:** `PCB_COPPER_SHORT_CIRCUIT`. | `legacy-6.0.3` label proposed. Owner: physical graph/short classifier. Primary producer: graph classifier; geometry/evidence validators provide witness refs only. | One confirmed physical component contains at least two distinct verified NetIds, including verified claims retained inside a conflicting assignment. Preconditions: physical graph built only from validated physical edges. | Attribute component snapshot, sorted verified NetIds, unordered Net pairs, direct contact sites, object/node/layer IDs, witness paths. Key `(RuleId, confirmedPhysicalComponentSnapshotId)`. | One primary finding per confirmed component, aggregate sites/pairs. Coexists with assignment and unrelated uncertainty findings. Never suppressed or downgraded by unrelated uncertainty; NetId does not create graph edges. | Source establishes definite short semantics; severity enum and DRC-clear mapping remain pending. Historical ID/contract, product severity approval pending. |
| **3. Connectivity indeterminate. H:** `PCB_COPPER_CONNECTIVITY_INDETERMINATE`. | `legacy-6.0.3` label proposed. Owner: physical connectivity classifier. Geometry/contact/ViaSpan/Microvia validators provide candidate evidence and references, not parallel occurrences. | Boundary-policy unresolved or indeterminate possible contact between confirmed components could alter topology/Net result. Preconditions: preserve exact geometry/proof state; a certified separated result is not uncertainty. | Attribute canonical unordered component snapshot pair, endpoint object/node IDs, layer, verified Net sets, ContactIds, reason, bounds/evidence. Key: unordered component snapshot pair; aggregate all candidate contacts/evidence between the pair. | One occurrence per component pair. May coexist with island-indeterminate when separate guarantee is affected. Never merge with a definite short or discard possible contacts. | 6.0.3 recommends fail-closed DRC-clear behavior; severity/blocking enum pending. Historical ID/trigger/key; final approval pending. |
| **4. Disconnected same-Net islands. H:** `PCB_NET_DISCONNECTED_ISLAND`. | `legacy-6.0.3` label proposed. Owner: physical island classifier. Primary classifier; assignment and geometry validators may provide inputs. | A verified NetId exists in multiple distinct confirmed physical components and all possible connecting geometry is resolved. Preconditions: no uncertain bridge that could change island result; never union by NetId. | Attribute NetId and canonical relevant component snapshot set. Key `(NetId, relevant component set)`. | Coalesce same Net/component set. If possible bridge remains, do not assert definite island; use indeterminate family. Coexists with unrelated diagnostics. | Severity, incomplete-routing treatment and DRC-clear mapping pending. Historical contract carried forward, not product severity approval. |
| **5. Island/connectivity indeterminate. H:** `PCB_NET_ISLAND_CONNECTIVITY_INDETERMINATE`. | `legacy-6.0.3` label proposed. Owner: physical island classifier. ViaSpan/Microvia/contact/fill validators reference possible-edge evidence. | Possible/unknown contact, span, zone fill, or missing expected geometry could alter island classification. Preconditions: relevant Net/component set established; typed uncertainty retained. | Attribute NetId, relevant component snapshots, candidate edges/contacts, Via/stage/transition refs, layer and evidence. Key `(NetId, relevant component set)` with possible edges aggregated. | Coalesce per key. Distinct from component-pair connectivity-indeterminate; coexist when both guarantees are affected. No confirmed short suppression. | Severity and DRC-clear policy pending. Historical contract carried forward; approval pending. |
| **6. Geometry invalid/unsupported/indeterminate. H:** `PCB_GEOMETRY_INVALID`, `PCB_GEOMETRY_UNSUPPORTED`, `PCB_GEOMETRY_INDETERMINATE`. | `legacy-6.0.3` labels proposed. Owner: geometry-input/predicate validator. Clearance/contact/graph validators may reference impacted candidates. | Invalid malformed/unsafe shape; unsupported valid but unimplemented geometry; indeterminate numeric predicate cannot classify the threshold. Keep states separate and never approximate unsupported geometry. | Attribute object/subshape/layer, raw input digest, predicate/kernel/version, reason, affected pair candidates. Key invalid/unsupported per object/reason and affected subject; indeterminate uses existing rule/pair semantics, exact historical key must be recovered rather than guessed. | Coalesce identical object/cause. Distinct geometry and clearance defects coexist. Do not map failure to separated or clear. | Invalid/unsupported must not silently CLEAR under source design; severity and exact DRC-clear rule mapping pending. Historical names/behavior carried forward, not final product approval. |
| **7. ViaSpan missing/unresolved or invalid. P:** `PCB_VIA_SPAN_MISSING_OR_UNRESOLVED`, `PCB_VIA_SPAN_INVALID`. | `audit-6.0.4-proposal`. Owner: ViaSpan validator. Microvia validator references span-owned occurrence. | Missing/unresolved when required span absent, legacy span unresolved, Stackup unavailable, or endpoint identity unresolved. Invalid for contradictory/malformed kind/order/endpoints, unknown/non-copper/disabled endpoint, zero length, or invalid Stackup. Valid-disjoint is not missing. | Missing key `(RuleId, projectId, viaObjectId, spanRecordDigest-or-MISSING, stackupRevision-or-UNKNOWN)`. Invalid key `(RuleId, projectId, viaObjectId, spanRecordDigest, sortedCodes, stackupRevision)`. Attribute Via, endpoints, layers, raw span, Stackup revision. | One ViaSpan-owned root occurrence; Microvia may reference same root. Do not emit a derivative junction finding solely because this root prevented evaluation. Distinct assembly defects coexist. No inferred cross-layer edge. | 6.0.4 proposes affected-connectivity blocking; severity/error-warning and final DRC-clear policy pending. Audit-proposed only, not production-approved. |
| **8. Continuous barrel evidence missing/unverifiable. P:** `PCB_VIA_BARREL_EVIDENCE_MISSING`, `PCB_VIA_BARREL_EVIDENCE_UNVERIFIABLE`. | `audit-6.0.4-proposal`. Owner: ViaSpan evidence/proof resolver. Microvia may reference. | Missing when a required continuous plated-barrel proof reference is absent. Unverifiable when a reference exists but bytes/hash/trust/full-span continuity cannot be verified. Matching endpoint names are not proof. | Missing key `(RuleId, projectId, viaObjectId, spanDigest, kind, sortedEndpoints)`. Unverifiable key `(RuleId, projectId, viaObjectId, evidenceId, contentHash, contextDigest)`. Attribute resolver, evidence role, endpoints and context. | Missing and unverifiable remain distinct. No cross-layer barrel edge. Independent same-layer contacts and v2 clearance coexist. | 6.0.4 proposes no edge and affected coverage block; severity and final sign-off policy pending. Audit-proposed only. |
| **9. Microvia topology/stage reference invalid. P:** `PCB_MICROVIA_STAGE_REFERENCE_INVALID`. | `audit-6.0.4-proposal`. Owner: assembly/topology validator. Junction/contact/process validators may reference but not duplicate structural root. | Duplicate/dangling StageId; invalid layer/endpoints; duplicate, absent, or wrongly owned node; contradictory or malformed expected transition/mirror. Preconditions: distinguish absent context (unknown) from impossible structure (invalid). | Attribute Via/assembly/revision, StageIds, TransitionId, JunctionIds, node/layer refs and validation codes. Preserve audit key family `(RuleId, projectId, viaObjectId, assemblyDigest, sortedStageIds, sortedNodeIds, sortedCodes)`; any key expansion needs approval. | One structural occurrence per registered key. No affected inter-stage edge. Suppress only derivative uncertainty for same structural root; preserve independent valid within-stage edges, process defects, shorts and v2 findings. | 6.0.4 classifies affected assembly as sign-off blocking and error candidate; final severity/DRC-clear policy pending. Audit-proposed only. |
| **10. Expected junction missing/unverifiable. P:** `PCB_MICROVIA_JUNCTION_INDETERMINATE`. | `audit-6.0.4-proposal`. Owner: Microvia junction evidence validator after structural validity. Contact verifier/predicate contributes facts. | Structurally valid expected transition has missing, not-connected, indeterminate, boundary-only, stale, uncertified, or unverifiable exact pair/layer/current-context evidence. Do not cascade from a structural/ViaSpan root alone. | Attribute Via/assembly, directed expected pair, canonical node pair or UNKNOWN, layer or UNKNOWN, context and reason. Key `(RuleId, projectId, viaObjectId, canonicalUnorderedStagePair, canonicalNodePair-or-UNKNOWN, layerId-or-UNKNOWN, currentContextDigest)`. | One occurrence per expected transition/context. No edge for the failed witness. Distinct stale witness or different failed transition coexists; retain valid unrelated edges. | 6.0.4 calls the affected path incomplete/unknown and sign-off blocking; severity enum and final clear policy pending. Audit-proposed only. |
| **11. Explicitly unsupported manufacturing process. P:** `PCB_VIA_PROCESS_UNSUPPORTED`. | `audit-6.0.4-proposal`. Owner: process-capability resolver. ViaSpan/Microvia validators reference its result. | Well-formed identifiable process has an explicit unsupported entry or is determinately excluded by authenticated, authorized, current, applicable complete closed-world coverage; applicable entry may lack validated contract. Partial/untrusted/unavailable registry or missing evidence does not trigger it. | Key `(RuleId, projectId, viaObjectId, processTokenDigest, capabilityRegistryVersion)` as 6.0.4; stage-scope expansion unresolved. Attribute process identity, stage refs, registry digest/version, coverage and rule contract. | Coalesce only same process/Via/registry occurrence. No process-gated edge; independent physical validation and v2 continue. Missing/unknown process must not map here. | 6.0.4 proposes blocking affected connectivity; severity and final DRC-clear policy pending. Audit-proposed only. |
| **12. Missing/unknown/unverifiable process evidence. U:** no approved RuleId. Candidate labels such as `PROCESS_EVIDENCE_MISSING` are taxonomy placeholders, not RuleIds. | Semantics and registry ID unresolved. Proposed owner: process evidence resolver; parsers/resolvers contribute; other validators reference. | Missing record, unknown process under incomplete coverage, stale context, unresolved bytes/verifier, invalid schema, or contradictory process claims. Preconditions require exact coverage/currentness checks before `unsupported`. | Proposed key fields: project/Via/assembly/stage, typed state, evidence digest or MISSING, registry identity/version or UNKNOWN, context. Granularity, aggregation and exact key remain unresolved. | Keep missing, unknown, unverifiable, stale, invalid and contradictory separate from unsupported. No inter-stage edge absent verified support; independent within-stage edge and v2 clearance continue. No product-facing finding until registered. | Severity and DRC-clear mapping pending; connectivity cannot be claimed complete while required gate is unresolved, but final product blocking policy requires approval. ID unresolved; not approved. |
| **13. ContactEvidence invalid/stale/conflicting. C:** Phase 6.0.5 names `PCB_CONTACT_EVIDENCE_SCHEMA_INVALID`, `PCB_CONTACT_EVIDENCE_IDENTITY_MISMATCH`, `PCB_CONTACT_EVIDENCE_STALE`, `PCB_CONTACT_EVIDENCE_UNVERIFIABLE`, `PCB_CONTACT_EVIDENCE_CONFLICT`, `PCB_CONTACT_OUTCOME_INDETERMINATE`, `PCB_CONTACT_GEOMETRY_UNSUPPORTED`, `PCB_CONTACT_BOUNDARY_POLICY_UNRESOLVED`. | `candidate-6.0.5`; not production-approved. Owners: schema/identity, freshness, proof resolver, shared evidence conflict owner, geometry predicate, or contact-policy owner per defect. Contact and Microvia validators are allowed as producers only after owner approval. | Exact candidate triggers: unsupported/malformed schema; recomputed identity/binding mismatch; coherent stale geometry/context; unresolved/unavailable proof; same identity has conflicting current claim; predicate indeterminate; valid but unsupported geometry; boundary outcome with tangent policy unresolved. | Candidate keys follow ContactId, evidence/ledger digest, exact pair/layer/context, sorted EvidenceIds and reason/capability/version. See 6.0.5 proposed key tuples; exact canonical key spec not approved. Attribute project, ledger/contact/evidence IDs, pair/layer, context, resolver/verifier, geometry outcome. | One canonical owner per defect. Same-key compatible candidates coalesce with provenance; conflicts persist. No union except verified-current positive-area outcome. Distinct defects coexist; v2 independent. | Severity and DRC-clear behavior pending; 6.0.5 names are candidates only pending reconciliation and product-owner approval. |
| **14. Contact Ledger integrity errors. C/U:** `PCB_CONTACT_LEDGER_DUPLICATE_ID` is a 6.0.5 candidate; other IDs unresolved. | `candidate-6.0.5`, not approved. Owner: serialized ledger reader; evidence/contact validators reference. | Duplicate persisted ContactId/EvidenceId before normalization; dangling/orphan/cross-contact reference; digest/pair/hash mismatch; duplicate or ineligible union application; unsupported schema. Byte-identical persisted duplicates are still defects. | Candidate duplicate key `(ledgerDigest, duplicateId, schemaVersion)`. Other identity keys unresolved until registration. Attribute raw row positions, ID, schema, references, digest, context and codes. | Reject affected ledger/evidence; never first/last-wins. Preserve independent evidence validated elsewhere. Do not silently erase persisted duplicate rows. | Severity/DRC-clear policy pending; loss of required evidence cannot justify CLEAR, but final blocking policy remains owner decision. Candidate/unresolved; not approved. |
| **15. Legacy v2 clearance. H behavior; RuleId/key U in supplied registry.** Historical predicate: `minimumViaClearance`. | Semantics: schema-v2 projected all-pairs behavior confirmed; `PCB_*` RuleId and exact occurrence-key semantics not supplied. Owner: existing legacy clearance-rule owner; Microvia/ViaSpan/contact validators are context-only producers. | Each applicable Via pair violates projected 2D outer-copper clearance under configured value and drill-diameter fallback. Preconditions follow existing v2 behavior; no span or process gate. | Attribute both Via IDs, projected geometry/radii, configured clearance, schema/rule context. Preserve existing runtime/report finding identity if recovered; do not fabricate RuleId or pair-key. | Evaluate every applicable pair regardless of span/topology/process/evidence/ledger state. Findings coexist with all other families; no suppressions by uncertainty. | Historical behavior is carried forward; severity, DRC-clear mapping, registry ID/key and product approval are unverified/pending. |

### 9.3 Deterministic diagnostic finalization

```text
finalizeDiagnostics(candidates, registry):
  validate registry version and exactly one definition per RuleId + semanticsVersion
  reject unknown RuleIds as product diagnostics; retain raw candidate/state for review
  verify producer is permitted and owner preconditions are satisfied
  normalize only under the approved identity profile; do not repair conflicting persisted data
  compute occurrence key from registered fields and recompute occurrence identity
  merge same-RuleId/version/project/key compatible candidates; retain sorted provenance
  preserve same-key identity/payload conflicts; do not choose first, last, majority, or severity winner
  across RuleIds, coexist by default
  suppress only an explicitly registered same-root derivative that adds no separate guarantee
  never suppress a confirmed short, independent defect, or v2 all-pairs clearance
  sort final output canonically; do not use timestamps, producer order, NetId, or DSU root
```

A ViaSpan-owned span defect noticed by the Microvia validator is one canonical ViaSpan occurrence with a secondary reference. If a structurally valid expected transition has its own independently stale witness, that is a distinct guarantee failure and remains separate. Severity precedence is not causal deduplication. No unregistered trust-failure or missing-process RuleId is invented.

## 10. Required 24-case adversarial review

The table gives typed validation state, diagnostic status, edge eligibility, v2 continuation, and DRC-clear status for every case required by the Phase 6.0.7 specification. “Blocked” means the supplied evidence cannot support a CLEAR assertion; it does not assign diagnostic severity. “Pending” means a product-owner policy is required before a CLEAR decision. “v2 runs” applies to schema-v2 inputs in every row. No test was executed. [5]

| # | Input condition | Typed validation state and expected diagnostic | Any graph edge allowed? | Legacy clearance | DRC CLEAR |
|---:|---|---|---|---|---|
| 1 | Valid digest, invalid signature | Digest integrity valid; authenticity failed; issuer/currentness/capability not established. Trust-signature RuleId unresolved; do not say unsupported. | No process-gated inter-stage edge; unrelated validated within-stage edges remain. | v2 runs. | Blocked pending trusted process/path proof; severity unresolved. |
| 2 | Valid signature from unauthorized issuer | Signature may verify; issuer authorization/scope fails; no supported-process claim. Unauthorized-issuer RuleId unresolved. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked pending authorized evidence; policy unresolved. |
| 3 | Authorized issuer with revoked/compromised key | Signature bytes may verify historically; current trust is revoked/failed. Revocation RuleId unresolved; not unsupported. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked pending current trust evidence. |
| 4 | Expired registry manifest | Historically authenticated/authorized may remain; currentness expired. Expiry RuleId unresolved. | No edge based on expired snapshot; independent within-stage edges remain. | v2 runs. | Blocked pending current registry. |
| 5 | Superseded registry snapshot | Historical authenticity may remain; currentness superseded/stale. Supersession RuleId unresolved. | No edge based only on old snapshot; independent within-stage edges remain. | v2 runs. | Blocked pending current snapshot. |
| 6 | Unknown process in partial registry | Registry can be authentic/current but coverage is incomplete; capability unknown, not unsupported. No unsupported diagnostic; missing/unknown ID unresolved. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked because required gate is unknown; policy unresolved. |
| 7 | Unknown process in complete closed-world registry | If authenticated/current and scope conclusively covers every query dimension, process is explicitly unsupported. `PCB_VIA_PROCESS_UNSUPPORTED` is audit-proposed. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked for unsupported capability; severity pending. |
| 8 | Missing process evidence | Process state `missing`; never default supported or call unsupported. Missing-process RuleId unresolved. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked for incomplete required process/path evidence; final policy unresolved. |
| 9 | Process evidence bound to stale project context | Registry may independently be current; evidence context stale/mismatched. Stale-evidence RuleId unresolved; not unsupported. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked pending current project-bound evidence. |
| 10 | Two conflicting process identities for one stage | Process state contradictory; no selection by arrival order/count/signature alone. Contradiction RuleId unresolved. | No edge dependent on that stage; unrelated valid edges remain. | v2 runs. | Blocked pending conflict resolution. |
| 11 | Duplicate StageId | Structural state invalid. `PCB_MICROVIA_STAGE_REFERENCE_INVALID` audit-proposed. | No edge depending on ambiguous stage; independent unrelated edges may remain. | v2 runs. | Blocked for invalid topology. |
| 12 | Reversed transition where forward is expected | Forward expected transition remains missing/incomplete; reverse does not satisfy it. `PCB_MICROVIA_JUNCTION_INDETERMINATE` audit-proposed for the uncovered expected transition; malformed-record ID unresolved. | No edge from reversed-only record; other valid expected transitions remain eligible. | v2 runs. | Blocked for unproven transition. |
| 13 | Nonconsecutive transition bypass | Chord is invalid as coverage; it covers neither consecutive transition. `PCB_MICROVIA_STAGE_REFERENCE_INVALID` audit-proposed; avoid duplicate derivative finding for the same root. | No chord edge; independent valid contacts remain. | v2 runs. | Blocked for invalid/incomplete chain. |
| 14 | Missing middle transition | Structure valid; middle expected transition missing; adjacent valid transitions stay valid. One `PCB_MICROVIA_JUNCTION_INDETERMINATE` audit-proposed occurrence. | Neighbor edges may be admitted; no middle edge. | v2 runs. | Blocked because path is incomplete. |
| 15 | Multiple junction candidates for one transition, no multiplicity policy | Transition ambiguous/unsupported; no first-wins or count-based selection. Junction RuleId audit-proposed; multiplicity-specific ID unresolved. | Neither ambiguous candidate; unrelated valid edges remain. | v2 runs. | Pending policy; do not assert CLEAR until resolved. |
| 16 | Junction proof has stale geometry hash | Structure may be valid; witness stale/unknown, not separated. `PCB_MICROVIA_JUNCTION_INDETERMINATE` audit-proposed; stale-specific ID unresolved. | No edge from stale witness; independent valid contacts remain. | v2 runs. | Blocked pending current witness. |
| 17 | Valid positive-area contact proof, wrong stage ownership | Contact proof may independently validate for its exact pair; Microvia reference is structurally invalid. `PCB_MICROVIA_STAGE_REFERENCE_INVALID` audit-proposed. | Ordinary contact edge only if independently admitted by graph contract; never the claimed Microvia transition from this invalid reference. | v2 runs. | Blocked for claimed Microvia path. |
| 18 | Cycle closes after valid expected transitions | Expected consecutive edges may validate; cycle is detected, adds no extra edge, and does not waive transition coverage. Cycle RuleId unresolved. | Expected edges may remain eligible; no cycle-closing edge absent approved topology policy. | v2 runs. | Pending cycle/topology owner decision. |
| 19 | Same malformed ViaSpan root emitted by two validators | ViaSpan invalid. One `PCB_VIA_SPAN_INVALID` audit-proposed occurrence; Microvia secondary provenance only. | No edge relying on invalid span; unrelated edges remain. | v2 runs. | Blocked for affected span coverage; arbitration/severity pending. |
| 20 | Two distinct defects on one Via: invalid span plus independently stale witness | Span invalid and separate junction evidence stale/unknown. Preserve `PCB_VIA_SPAN_INVALID` and `PCB_MICROVIA_JUNCTION_INDETERMINATE` as separate audit-proposed occurrences. | Neither affected guarantee yields an edge; independent edges remain. | v2 runs. | Blocked for both affected guarantees. |
| 21 | Confirmed short plus unrelated indeterminate contact | Short remains definite; uncertain contact does not union. Historical `PCB_COPPER_SHORT_CIRCUIT`; also `PCB_COPPER_CONNECTIVITY_INDETERMINATE` if separate uncertainty meets trigger. | Preserve certified edges; no edge for indeterminate contact. | v2 runs. | Blocked by short and unresolved connectivity; severity mapping pending. |
| 22 | Missing process evidence plus valid v2 clearance violation | Process `missing/unknown`, not unsupported; legacy pair has a clearance violation. Missing-process RuleId unresolved; preserve existing clearance finding identity without inventing a `PCB_*` ID. | No process-gated Microvia edge; independent contacts remain. | v2 all-pairs runs and reports applicable violation. | Blocked by v2 violation and unverified path; severity mapping pending. |
| 23 | Registry unavailable while offline, no accepted freshness proof | Currentness/support unknown or stale; historical authenticity may be retained; not unsupported. Offline/trust RuleId unresolved. | No process-gated edge; independent within-stage edges remain. | v2 runs. | Blocked pending freshness/revocation policy. |
| 24 | Equivalent reordered inputs yield different diagnostic IDs | Expected typed states must be permutation-invariant; order-dependent identity is a contract failure, not a new approved RuleId. | Same eligible edge set for both equivalent permutations. | v2 pair results identical and continue. | Reordering itself does not block; overall CLEAR depends on all other unresolved checks/policy. |

## 11. Phase 6.0.3–6.0.6 consistency and contradiction matrix

### 11.1 Carry-forward invariants

| # | Required invariant | Source and status | Phase 6.0.7 proposal / remaining dependency |
|---:|---|---|---|
| 1 | NetAssignment remains separate from physical connectivity. | Confirmed in 6.0.3 §§4–5; carried forward in 6.0.4–6.0.6. **PASS as design contract.** | Graph from physical evidence first; assignment is post-graph annotation. No dependency beyond implementation/approval, which is out of scope. |
| 2 | Same NetId never creates a physical edge. | 6.0.3 §5; repeated in 6.0.4–6.0.6. **PASS.** | Retained; disconnected same-Net nodes stay disconnected absent certified physical contact. |
| 3 | Definite multi-Net short remains definite despite unrelated uncertainty. | 6.0.3 §§5, 10.1; carried forward. **PASS.** | Preserve short finding and independent uncertainty; no cross-rule suppression. Severity policy remains open. |
| 4 | Uncertain contacts cannot silently disappear. | 6.0.3 §§6–7, 10; 6.0.4–6.0.6 preserve typed results. **PASS as design rule; implementation unverified.** | Keep boundary/stale/unknown/unverifiable/unsupported/contradictory facts and registered uncertainty findings. Exact severity/clear mapping is pending. |
| 5 | Valid disjoint spans differ from unknown/invalid spans. | 6.0.3 §9.2; 6.0.4 §4.2; 6.0.5–6.0.6. **PASS.** | Empty intersection means known-disjoint only for two valid enumerations; unknown/invalid is never empty. |
| 6 | Only certified positive-area contact can authorize a physical edge. | 6.0.3 §§6, 9; 6.0.4 §5; 6.0.5–6.0.6. **PASS as proposal.** | Recompute proof and binding; valid current positive-area outcome required. Proof authority/verifier acceptance still needs approval. |
| 7 | Boundary/tangency is not silently promoted to continuity. | 6.0.3 §§6.2–6.3; 6.0.4–6.0.6. **PASS.** | Keep boundary explicit and non-edge until product-owner policy decides electrical meaning. |
| 8 | Every Microvia inter-stage edge has exact current-context witness. | 6.0.3 §9.2; 6.0.4 §5.2; 6.0.5 §6; 6.0.6 §§4,7.2. **PASS as proposed gate.** | Exact stage/node/pair/layer/context/hashes/predicate/kernel and current positive-area proof, plus process gate. Wire schema and branch/multiplicity policy remain open. |
| 9 | Every process claim has independently verified registry provenance. | 6.0.3 §9 references source/hash; 6.0.4 leaves authority/process policy open; 6.0.5–6.0.6 add registry concepts but leave authenticity/root/revocation unresolved. **New 6.0.7 closure proposed; not previously closed.** | Separate digest, signature, issuer, currentness/revocation, coverage, and capability checks. No production root/authority/algorithm selected. |
| 10 | Contact Ledger identities and references are deterministic. | 6.0.3 §§6,10; 6.0.4 §7; 6.0.5 §7; 6.0.6 §5. **PARTIAL; proposal reconciles shape.** | Carry forward `contacts[]` + `evidence[]` and pre-dedup uniqueness; schema version, canonical bytes/digest profile and migration are open. |
| 11 | Diagnostic ownership/dedup remains stable. | 6.0.3 §10.1 historical IDs/keys; 6.0.4 proposals; 6.0.5 candidates; 6.0.6 central arbitration proposal. **PARTIAL.** | Preserve status of each ID; one owner per defect; coexist by default. Approval of new IDs, exact keys, causal edges, severity and clear rules is pending. |
| 12 | Legacy v2 minimumViaClearance remains all-pairs projected 2D. | 6.0.3 §§3,12; 6.0.4 §§4.2,9; 6.0.5–6.0.6. **PASS as historical behavior.** | Always evaluate every applicable Via pair using outer-copper radii/configured clearance and drill fallback; never gate on newer Microvia/ledger states. Exact RuleId/key still unrecovered. |
| 13 | Unsupported geometry is not approximated; no pending policy is silently frozen. | 6.0.3 §§6,13,15; 6.0.4 §§7,11; 6.0.5–6.0.6. **PASS as design constraint.** | Preserve unsupported/invalid/indeterminate separately; no approximation or silent owner-policy selection. |

### 11.2 Contradictions and document-to-document resolution

| Area | Phase 6.0.3 | Phase 6.0.4 | Phase 6.0.5 | Phase 6.0.6 | 6.0.7 proposed resolution and open dependency |
|---|---|---|---|---|---|
| Stackup ordering | Redundant layer order, copper order/list, and front/back fields coexist. | Corrects to `layersFrontToBack` as sole physical sequence; derives copper order and face IDs. | Carries single-source correction. | Carries it forward and identifies disabled outer-copper and small-stackup edge policy as open. | Use one order source; legacy redundancy is migration validation only. Disabled physical outer copper and fewer than two enabled copper layers remain product decisions. |
| Microvia stage order | `stages[]` described as explicit manufacturing order. | Requires structural evidence but does not establish array order as complete sequence source. | Explicit `orderedStageIds`; expected transitions are exact consecutive directed pairs. | Carries ordered sequence/process gate. | `orderedStageIds` sole authority; stages/junction arrays nonsemantic. Branch/cycle/multiplicity, skipped-layer, adjacency, and non-continuous policy remain open; linear path is the only proposed supported mode. |
| Transition records | Junction references exist; no complete path identity/multiplicity contract. | Exact pair/layer/context witness and invalid-vs-unknown checks. | Reversed/chord records do not cover expected transition; cycle adds no edge; multiple candidates unresolved. | Carries strict sequence and exact process/contact conjunction. | Stable directed transition identity and exact derived coverage; ambiguous candidates do not get selected. Whether multiplicity/branch/cycle may later be supported is unresolved. |
| Registry trust | Per-stage processEvidence source/hash but no trust lifecycle. | Unsupported-process proposal; authority and process list remain pending. | Capability registry concepts remain proposal. | Registry ID/version/digest/issuer/coverage, but authenticity, root rotation, revocation, expiry and algorithms still open. | Add explicit signed immutable manifest, separate authorization/currentness/revocation/coverage, and typed verification. No product root, issuer, key material, crypto algorithm, threshold, or process type selected. |
| Contact Ledger cardinality | Contact/evidence proof concepts but not separate canonical persisted cardinality. | One canonical contact outcome with evidence retained. | `records[]` leaves ContactId/EvidenceId cardinality ambiguous. | Resolves to `contacts[]` once per ContactId and `evidence[]` once per EvidenceId, optional union applications. | Carry forward 6.0.6 split. `records[]` only via explicit migration adapter; duplicate persisted IDs rejected before normalization. Wire profile and migration version remain open. |
| Diagnostic status | Historical 6.0.3 RuleIds/keys. | Adds ViaSpan/Microvia IDs as proposals, severity pending. | Adds Contact/Ledger candidate names and conditional causal arbitration. | Preserves historical/proposed/candidate distinctions; missing-process RuleId absent. | 15-family table retains explicit status; no proposed/candidate ID is promoted. Product owner must approve registrations, exact semantics versions, keys, owners, producers, severity/clear policy. |
| DRC-clear mapping | Some uncertainty/short behavior described; severity decisions remain pending. | Proposes affected connectivity blocking for several new Via findings. | Recommends fail-closed uncertainty, not a finalized severity enum. | Keeps severities, DRC-clear approvals and user policy open. | “Blocked” in adversarial table describes inability to assert CLEAR on evidence, not a severity choice; product DRC policy remains pending. |
| Evidence basis for this report | Original design contract. | Verified audit attachment. | Previous proposal. | Prior closure proposal. | The supplied 6.0.7 source is a task specification; this report is the proposed closure artifact. No implementation, tests, approvals, or Design Freeze are evidenced by its existence. |

## 12. Unresolved product-owner decisions and unverified assumptions

### 12.1 Product-owner decisions

1. Approve wire schema versions, stable ID namespaces, identity normalization, canonical serialization, digest preimages/algorithms, project identity, context digest, revision increments, and migration/adapters. The `/1` labels and canonical hash approaches in prior reports are not frozen.
2. Choose the trusted registry authorities/issuers, bootstrap channel, trust roots and rotation/recovery process, issuer delegation/scope, signature threshold model, production signature/digest/canonicalization algorithms, algorithm retirement/agility, trusted clock, expiry, supersession, anti-rollback storage, revocation distribution/checkpoint freshness, compromise retroactivity, and offline freshness policy.
3. Define registry coverage dimensions and exact closed-world scope. Decide whether process support is per stage, Via, assembly, fabricator, material, or combination; select any actual supported process catalog. No process type is selected here.
4. Choose whether branch/DAG topology, shared stages/nodes, non-continuous paths, cycles, parallel transitions, multiple valid junctions, and multiple proofs per transition are supported, unsupported, or invalid. Define meaning of exactly one valid witness.
5. Define authoritative stage-sequence producer and revision rules; allowable endpoints, copper adjacency/skips, capture lands, intermediate-stage conduction, depth, fabricator/material constraints, and stacked/staggered manufacturing meaning.
6. Approve evidence provenance, accepted proof formats, immutable resolver identities/versions, verifier identities/versions, proof retention/privacy, and whether current-run computation, verified libraries, manufacturing imports, or human assertions can ever establish trusted process or contact evidence.
7. Decide physical boundary/tangent semantics, geometry kernel guarantees, bounded-proof thresholds, numeric units/precision, and any explicitly named physical/manufacturing tolerance. No fuzzy contact rule is added.
8. Approve all diagnostic RuleIds/statuses/semantics versions, owners, allowed producers, exact triggers/preconditions/attribution/occurrence keys, same-root causal suppression, coexistence, severity, DRC-clear blocking, wording, and reporting caps. Missing/unknown/unverifiable process and registry trust diagnostics have no approved RuleIds in the sources.
9. Recover the exact existing v2 `minimumViaClearance` finding identity/key and its severity/clear mapping, plus any unspecified historical geometry-indeterminate occurrence key. Do not invent them from the rule name.
10. Resolve incomplete-assignment aggregation caps, island/incomplete-routing behavior, Net authority/conflict/unassigned policy, Stackup disabled outer copper, and fewer-than-two-enabled-copper-layer behavior.
11. Decide whether Contact Ledger validated summaries and `unionApplications[]` are persisted or computed; approve evidence retention and independent-reader expectations.

### 12.2 Unverified assumptions

- A product security owner can provision and maintain trust anchors and a durable monotonic anti-rollback store. This report makes no assumption that such infrastructure already exists.
- Registry manifests, evidence objects, and revocation checkpoints can be resolved as immutable bytes. If unavailable, validation is typed unavailable/unknown and cannot grant a process-gated edge.
- Project and topology revisions will reliably change when identity-bearing geometry/process/assembly content changes. This is not established by the documents and requires owner-defined revision semantics.
- The proposed linear Microvia schema has an accepted single-stage ownership model. Shared nodes, multi-branch processes, and unusual non-continuous structures are intentionally not interpreted without policy.
- Trust standards are used as nonbinding architectural references only. They do not set PCB Studio Pro's authority, algorithm, key, or policy. [7] [8]
- No statement in this report establishes that the proposed types, rules, or algorithms exist in the application code. No tests/builds were run.

## 13. Readiness verdict and final isolation evidence

### 13.1 Design-readiness verdict

**Conditionally design-review ready.** This report provides the requested contract proposal, complete proposed schemas, deterministic algorithms and state transitions, a 15-family diagnostic registry with explicit rule status, the 24 required adversarial cases, the 13 carry-forward invariants, cross-document contradiction matrix, and explicit unresolved decisions. Independent architecture and product-owner review can proceed on this proposal. The condition is that no unresolved item be silently treated as approved; product owners must decide the enumerated authorities, trust lifecycle, process/topology semantics, wire profiles, RuleIds, severities, and DRC-clear behavior before Design Freeze or implementation.

**Design Freeze: NOT APPROVED.**  
**Implementation readiness: NOT READY / NOT AUTHORIZED.**  
**Phase 6.1 / 6.2: NOT STARTED.**

### 13.2 Before/after isolation record

| Check | Before source review (verified `2026-11-20T21:49:00Z`) | After report creation (verified `2026-11-20T22:12:08Z`) |
|---|---|---|
| Authorized fresh clone | `/home/ubuntu/readonly-inspection/pcb-studio-pro` | Same clone only; no pre-existing worktree claim |
| Origin | `https://github.com/soheil6913/-PCB-Studio-Pro.git` | Verified: `https://github.com/soheil6913/-PCB-Studio-Pro.git` |
| Branch | `main` | Verified: `main`; no create/switch/rename/delete |
| Local HEAD | `de7497a675af7c6212bbc4751fce098c1f414e8d` | Verified: `de7497a675af7c6212bbc4751fce098c1f414e8d` |
| Remote `main` SHA | `de7497a675af7c6212bbc4751fce098c1f414e8d` | Verified via `git ls-remote`: `de7497a675af7c6212bbc4751fce098c1f414e8d` |
| Phase 6 baseline | `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` available | Verified commit object available: `6fad0dcdc7e5878e671b8b419b2f61084e5a8138` |
| Worktree | Clean; pre-inspection `git status` and diff checks passed | Verified clean; porcelain status empty and staged/unstaged diff checks passed |
| Actions | Read-only inspection only | No repository edits/refs, tests/builds, commits, push, PR, merge, rebase, cherry-pick, amend, reset, or Phase 6.1/6.2 |

No repository source was edited and no tests/builds were run. Post-report verification completed successfully at `2026-11-20T22:12:08Z`; all required identity, SHA, baseline-availability, and clean-worktree checks passed.

## References

[1]: https://raw.githubusercontent.com/soheil6913/PCB/main/PCB_Studio_Pro_%E2%80%94_Phase_6.0%20%286%29.md "PCB Studio Pro — Phase 6.0.3 Design Freeze Corrections"
[2]: https://raw.githubusercontent.com/soheil6913/PCB/main/PCB_Studio_Pro_%E2%80%94_Phase_6.0%20%287%29.md "PCB Studio Pro — Phase 6.0.4 Final Contract Consistency Audit"
[3]: file:///home/ubuntu/readonly-inspection/PHASE_6_0_5_MICROVIA_EVIDENCE_TOPOLOGY_CLOSURE.md "Phase 6.0.5 Microvia Evidence and Topology Closure"
[4]: file:///home/ubuntu/readonly-inspection/PHASE_6_0_6_FINAL_EVIDENCE_LEDGER_CLOSURE.md "Phase 6.0.6 Final Evidence Ledger Closure"
[5]: file:///home/ubuntu/upload/pasted_content.txt "PCB Studio Pro Phase 6.0.7 Task Specification"
[6]: file:///home/ubuntu/readonly-inspection/phase6_0_7_trust_sources.md "Phase 6.0.7 Trust Source Findings"
[7]: https://theupdateframework.github.io/specification/latest/ "The Update Framework Specification"
[8]: https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final "NIST SP 800-57 Part 1 Revision 5 Recommendation for Key Management"
