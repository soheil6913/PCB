# PCB Studio Pro — Phase 6.0.3 Design Freeze Corrections

**Purpose:** Independent consistency correction of `PHASE_6_0_2_ARCHITECTURE_CORRECTIONS.md` before any design freeze.

**Status:** Design-only. This report does not authorize implementation.

## 1. Isolation and baseline

- Repository: `/home/ubuntu/work/repo` (`soheil6913/-PCB-Studio-Pro`).
- Branch: `implementation/phase6-net-aware-drc-20261120`.
- Current `HEAD`: `6fad0dcdc7e5878e671b8b419b2f61084e5a8138`, exactly the required baseline.
- Worktree: clean.
- `main`: `de7497a675af7c6212bbc4751fce098c1f414e8d`, unchanged.
- Report path: `/home/ubuntu/work/PHASE_6_0_3_DESIGN_FREEZE_CORRECTIONS.md`, outside the repository.
- No source, test, configuration, or UI changes; no commits, pushes, PRs, merges, rebases, or cherry-picks.

## 2. Design-readiness verdict

**Verdict: not ready for implementation; conditionally ready for product-owner design review only.**

This revision repairs the internal type/algorithm gaps identified in the Phase 6.0.2 report. It makes unknown, conflicting, invalid, boundary, uncertain, and unsupported cases explicit and gives every algorithmic finding a proposed generation and attribution path. It also defines the base Layer/Stackup contract and explicit physical evidence for Via continuity. However, physical boundary contact semantics, geometric uncertainty/tolerance, finding severities, legacy migration project identity, and several Via/pad/microvia policies remain **PENDING PRODUCT-OWNER DECISION**. Do not start Phase 6.1 or 6.2 without explicit approval of the freeze checklist in §13.

## 3. Baseline findings and source references

At the verified baseline:

- `shared/engineering.ts:3–13`: there is no canonical Net/LayerId/Stackup/Padstack model. Track and schematic Wire carry optional `net?: string`; pads/vias/pins have no canonical Net reference.
- `shared/engineering.ts:269–284`: connectivity graph work is for schematic wires, junctions, and pins; it does not build a PCB copper graph.
- `shared/engineering.ts:286–322`: PCB checks are geometric pairwise rules; no PCB connectivity or Net-aware short rule exists.
- `shared/engineering.ts:321`: v2 `minimumViaClearance` compares 2D via-center distance against the two outer copper radii plus the configured clearance, using `drill` as the diameter fallback; it checks all via pairs without layer-span gating.
- `shared/engineering.ts:330–347`: validation requires Via layers, when provided, to be exactly two distinct values from `F.Cu` and `B.Cu`; v2 has no ordered stackup or span kind.
- `shared/phase5_1.geometry-validation.test.ts:359–389` and `shared/engineering.test.ts:156–175`: current valid explicit spans are the two outer layers in either order; absent span is not evidence of disjointness.
- `client/src/pages/Home.tsx:19,42–43,64`: demo schematic wire labels are strings, not registry-backed PCB Net IDs.
- `PHASE_6_0_2_ARCHITECTURE_CORRECTIONS.md`: this report corrects the conceptual proposal; none of its proposed types exist in production.

## 4. Corrected NetAssignment state model

The Phase 6.0.2 union omitted states its pseudocode already used (`expected-but-unassigned`, `invalid`, `conflicting`). The following union is internally explicit. Invalid/conflicting states are retained as such and must never be silently coerced to unknown or unassigned.

```ts
type NetId = string & { readonly __brand: "NetId" };
type LayerId = string & { readonly __brand: "LayerId" };
type CopperObjectId = string & { readonly __brand: "CopperObjectId" };
type CopperNodeId = string & { readonly __brand: "CopperNodeId" };
type ContactId = string & { readonly __brand: "ContactId" };
type PhysicalComponentId = string & { readonly __brand: "PhysicalComponentId" };
type Point = { x: number; y: number };
type Rational = { numerator: bigint; denominator: bigint }; // denominator > 0, reduced form
type AssignmentSource = "user" | "netlist-import" | "legacy-v2" | "library";

type NetClaim =
  | { state: "verified"; netId: NetId; source: AssignmentSource }
  | { state: "candidate"; candidateNetId: NetId; source: "legacy-v2" | "import" }
  | { state: "invalid"; rawReference: unknown; reason: string; source: AssignmentSource };

type NetAssignment =
  | { state: "verified"; netId: NetId; source: AssignmentSource }
  | { state: "unverified-candidate"; candidateNetId: NetId; source: "legacy-v2" | "import" }
  | { state: "intentional-unassigned"; reason: "mechanical" | "non-electrical" | "explicitly-unconnected" }
  | { state: "expected-but-unassigned"; expectedBy: "verified-pin" | "netlist" | "design-rule"; evidenceId: string }
  | { state: "unknown"; reason: "missing-source-data" | "ambiguous-name" | "unsupported-object" | "incomplete-import" }
  | { state: "invalid"; rawReference: unknown; reason: "missing-net-record" | "malformed-id" | "wrong-project" | "invalid-schema"; source: AssignmentSource }
  | { state: "conflicting"; claims: readonly [NetClaim, NetClaim, ...NetClaim[]]; reason: "multiple-net-references" | "pin-pad-disagreement" | "source-disagreement" };

type CopperShape =
  | { shape: "circle"; centerOffset: Point; diameter: number }
  | { shape: "rect"; centerOffset: Point; width: number; height: number; rotation: number }
  | { shape: "oval"; centerOffset: Point; width: number; height: number; rotation: number };

type CopperNode = {
  id: CopperNodeId;
  objectId: CopperObjectId;
  layerId: LayerId;
  geometry: CopperShape;
  assignment: NetAssignment;
};

type PhysicalComponent = {
  id: PhysicalComponentId;
  nodeIds: CopperNodeId[];
  objectIds: CopperObjectId[];
  certainty: "complete" | "has-indeterminate-boundary";
};

type PotentialContact = {
  contactId: ContactId;
  a: CopperNodeId;
  b: CopperNodeId;
  confirmedComponentIds: readonly [PhysicalComponentId, PhysicalComponentId];
  state: "boundary-contact" | "indeterminate";
  reason: string;
};

type PhysicalCopperGraph = {
  nodes: CopperNode[];
  contacts: PhysicalContact[];
  components: PhysicalComponent[];
  potentialAdjacency: PotentialContact[];
};
```

### Interpretation rules

- `verified` contributes one verified Net ID.
- `conflicting` preserves every claim. Its `verified` claims still contribute to short detection; its candidate/invalid claims do not become verified. It also produces an assignment-conflict finding.
- `unverified-candidate` is never treated as verified identity and never permits a same-Net overlap exemption.
- `intentional-unassigned` is a known absence of Net assignment. It is not equal to any Net and is not a short by itself. Whether a particular electrical copper role may be intentional-unassigned is product policy.
- `expected-but-unassigned` is explicitly incomplete and produces an assignment-incomplete finding; it is not a harmless no-Net state.
- `unknown` means the source cannot establish the value. It is not an invalid reference and is not intentional absence.
- `invalid` preserves the invalid reference and its reason. It is not normalized to unknown or unassigned.
- If several claims disagree, use `conflicting`, retaining every claim and source; do not choose one by precedence without approved resolution policy.

A helper used by every later algorithm is:

```text
verifiedNetIds(assignment):
  if assignment.state == "verified": return {assignment.netId}
  if assignment.state == "conflicting":
      return set(claim.netId for each claim in assignment.claims where claim.state == "verified")
  otherwise: return {}
```

This helper does not erase the outer `conflicting` state; diagnostics retain it even when some of its verified claims participate in a definite short. A physical object with two distinct verified claims is itself an electrical conflict; represent its copper nodes in the physical graph and report the conflict, rather than picking a single claim.

## 5. Physical graph and classification contract

### 5.1 Graph construction does not depend on Net identity

For each supported conductive shape on each resolved copper `LayerId`, create a physical node. Evaluate candidate contacts using geometry and physically declared conduction paths. Add every certified contact as an edge regardless of NetAssignment. Keep uncertain, boundary-unresolved, invalid, and unsupported candidates in the evidence ledger; only certified conductive edges union graph components.

Net assignment is an annotation on nodes, read only after physical components are constructed. A shared NetId never joins disconnected nodes; different NetIds do not remove a physical edge.

### 5.2 Component classification

For each confirmed physical component:

1. Gather the union of `verifiedNetIds` over its nodes.
2. If two or more distinct verified NetIds occur, emit one definite `PCB_COPPER_SHORT_CIRCUIT` for the component. Unknown, unverified, expected-but-unassigned, invalid, or conflicting annotations do not negate this finding.
3. If a component has an invalid/conflicting assignment, emit the distinct assignment diagnostic too; retain the invalid/conflicting representation.
4. If it has unknown, unverified, or expected-but-unassigned electrical copper, do not claim the component is fully same-Net verified and do not grant same-Net exemption to affected object pairs.
5. Group verified Net annotations across physical components only to detect disconnected islands. Never union components by NetId. If all geometry/connectivity is complete and the Net is expected to be routed, separate components yield `PCB_NET_DISCONNECTED_ISLAND`; if an indeterminate possible contact/span/fill could bridge them, yield an indeterminate island result instead.

### 5.3 Short deduplication and attribution

Recommended primary short dedup key: `(PCB_COPPER_SHORT_CIRCUIT, confirmedPhysicalComponentSnapshotId)`. Emit no more than one primary short per confirmed physical component, even if the component has several different Net IDs, cycles, or contact sites. Distinct disconnected physical components get separate findings.

The finding should include:

- the sorted unique verified Net IDs in the component;
- all unordered pairs of those Net IDs as the component’s co-connected conflict set;
- object IDs on direct cross-Net contact sites and on deterministic certified witness paths connecting Net representatives;
- direct contact IDs and per-contact geometry witnesses;
- whether unknown/invalid/conflicting assignments are also present; and
- a stable component-snapshot key for reproducibility.

Severity, payload limits, and whether users prefer one summary per component plus secondary per-Net-pair details remain **PENDING PRODUCT-OWNER DECISION**. The chosen primary dedup rule must not omit direct contact sites from evidence.

## 6. Complete PhysicalContact semantics

### 6.1 Result type

```ts
type ContactEvidence = {
  kernel: { name: string; version: string };
  predicate: string;                      // e.g. signed separation or robust intersection
  layerId: LayerId;
  nodeIds: readonly [CopperNodeId, CopperNodeId]; // canonical sorted pair
  geometryHashes: readonly [string, string];
  inputRevision: string;
  proof:
    | { kind: "exact"; signedSeparation?: Rational; intersectionArea?: Rational; witnessPoints?: Point[] }
    | { kind: "bounded"; signedSeparation: { lower: number; upper: number; unit: string }; intersectionArea?: { lower: number; upper: number; unit: string }; witnessPoints?: Point[] };
  toleranceModel: "nominal-exact" | "explicit-physical-tolerance";
};

type PhysicalContact =
  | { state: "positive-area-overlap"; contactId: ContactId; evidence: ContactEvidence }
  | { state: "boundary-contact"; contactId: ContactId; evidence: ContactEvidence; disposition: "PENDING_PRODUCT_OWNER_DECISION" }
  | { state: "separated"; contactId: ContactId; evidence: ContactEvidence }
  | { state: "indeterminate"; contactId: ContactId; evidence?: ContactEvidence; reason: string }
  | { state: "invalid-geometry"; contactId: ContactId; objectIds: CopperObjectId[]; reason: string }
  | { state: "unsupported-geometry"; contactId: ContactId; objectIds: CopperObjectId[]; feature: string };
```

`ContactId` should be deterministic for a canonical sorted node pair, layer ID, input geometry hashes/revisions, and predicate/kernel version. If geometry or the predicate version changes, it gets a different contact ID. When invalid/unsupported geometry cannot form CopperNodes, derive a diagnostic evidence key from the sorted object IDs, optional subshape/layer IDs, canonical raw-input digest, predicate/kernel version, and failure reason; do not pretend it is a certified contact. Geometry evidence and rule outcomes are retained in an immutable DRC-run record or content-addressed evidence store, so an audit can reproduce which inputs/kernel/predicate generated the finding. This does not require persisting bulky proof data in the editable project file.

### 6.2 Exact classification distinctions

For two nominal copper geometries on the same enabled copper layer:

- **Positive-area overlap:** a robust/exact predicate certifies an intersection region with area strictly greater than zero. This is a physical contact edge; it unions nodes independently of Net assignment.
- **Boundary/tangent contact:** an exact predicate proves touching with zero intersection area and zero separation. Record `boundary-contact`, but do not choose whether it conducts until product policy is approved. Before that decision, it does not union components, does not qualify for same-Net exemption, and cannot be reported CLEAR; it triggers the dedicated connectivity-indeterminate finding when it could affect connectivity/Net classification.
- **Certified separation:** a robust predicate proves strictly positive signed separation under the declared nominal geometry model. It is not a contact. Clearance thresholds are evaluated independently.
- **Numerically indeterminate:** outward bounds straddle the contact/separation decision or exact arithmetic is unavailable and no proof resolves it. Preserve the bound/reason, do not union, do not report CLEAR.
- **Invalid geometry:** malformed/non-finite/self-invalid data or impossible shape parameters. Emit a geometry-input error; no contact edge; affected pair remains non-clear.
- **Unsupported geometry:** the object uses a valid but unsupported type (e.g. custom polygon without certified predicate). Emit unsupported/indeterminate; do not approximate it as a circle or silently omit it.

### 6.3 Tolerance and robust-predicate policy

- Do not reuse schematic `CONNECT_TOLERANCE` as a PCB copper-contact tolerance.
- Do not add an epsilon, snap-to-grid, or fuzzy union rule as a substitute for a physical tolerance decision.
- Nominal geometry should use exact fixed-point/rational predicates where feasible. For floating/rotated/non-algebraic cases, use robust predicates and outward error bounds. If the bounds do not certify one state, return `indeterminate`.
- Manufacturing tolerance belongs in separately named manufacturing rules; it must not silently expand copper geometry for electrical connectivity.
- If product later wants a physical contact tolerance, it must be explicit in units, rule scope, source of tolerance, and whether it expands each object, and it must be separately approved. Until then, no undocumented nonzero contact tolerance is applied.

**Pending boundary decision:** whether a nominal exact tangent is an electrically conductive contact, whether it is a short when different verified Nets touch, and whether same-Net boundary contact receives the overlap exception. This report does not decide those product semantics.

## 7. Dedicated uncertain-copper finding

### Finding ID

`PCB_COPPER_CONNECTIVITY_INDETERMINATE`

This is distinct from `PCB_GEOMETRY_INDETERMINATE` (which may describe numerical uncertainty for a clearance calculation), `PCB_COPPER_SHORT_CIRCUIT` (definite confirmed multi-Net component), assignment findings, and disconnected-island findings.

### Generation rule

Emit when an indeterminate or policy-unresolved boundary contact could change physical component membership or Net connectivity. At minimum, emit when the candidate contact bridges two different confirmed physical components whose verified Net sets contain at least one different NetId pair. Also emit for a possible bridge that prevents a definite same-Net island conclusion or a clear unconnected/connected status.

### Attribution and deduplication

- Include both endpoint object IDs and node IDs, layer ID, sorted confirmed component snapshot IDs, each side’s verified NetId set, candidate ContactId, reason, and bounded/exact evidence if available.
- Deduplicate by rule ID and unordered pair of confirmed component snapshot IDs, aggregating all candidate ContactIds/witnesses between those components. If a component pair has several possible contacts, retain all of their evidence under one finding. If candidates could join components in different layer pairs, include each layer and evidence item.
- If the candidate is internal to one already-confirmed component, retain it in the evidence ledger; it does not undo a definite short. Emit a separate uncertain-connectivity finding only if the uncertain site changes a reportable topology/completeness question (otherwise avoid duplicating the component’s short result).
- The finding is never converted to CLEAR by matching names/IDs. A confirmed short in either component remains a definite short even if another possible contact is also uncertain.

### Severity and sign-off

Recommended fail-closed behavior is that this finding blocks a “DRC clear” sign-off because a possible cross-Net connection cannot be ruled out. Exact severity (`Error` vs `Warning` plus blocking status), user resolution path, and behavior in incomplete-routing mode are **PENDING PRODUCT-OWNER DECISION**. Regardless of severity, it must remain a finding and must not be silently dropped or counted as CLEAR.

## 8. Foundational LayerId and ordered Stackup contract

```ts
type StackupId = string & { readonly __brand: "StackupId" };

type LayerKind = "copper" | "dielectric" | "soldermask" | "silkscreen" | "paste" | "mechanical" | "other";
type CopperFace = "front" | "back" | "internal";

type StackupLayer =
  | { id: LayerId; kind: "copper"; name: string; copperOrder: number; face: CopperFace; enabled: boolean }
  | { id: LayerId; kind: Exclude<LayerKind, "copper">; name: string; physicalOrder: number; enabled: boolean };

type OrderedStackup = {
  id: StackupId;
  revision: number;
  layers: StackupLayer[];                 // physical front-to-back sequence
  orderedCopperLayerIds: LayerId[];       // explicit front-to-back copper sequence
  frontCopperLayerId: LayerId;
  backCopperLayerId: LayerId;
};

type StackupValidation =
  | { state: "valid"; stackupId: StackupId; revision: number }
  | { state: "unknown"; reasons: string[] }
  | { state: "invalid"; diagnostics: string[] };
```

### Stackup invariants

- IDs are stable and independent of names/aliases. Legacy `F.Cu` and `B.Cu` map to fixed front/back LayerIds only for a validated two-layer migration.
- Physical order is strictly front-to-back. Copper order has no duplicates/gaps in the canonical ordered list; all listed layers exist, are `kind: "copper"`, and enabled.
- Exactly one enabled front and one enabled back copper layer exist. Internal copper layers are explicit.
- Disabled layers remain in the stackup record for provenance but cannot host valid conductive geometry or participate in a span. A copper object on a disabled layer is invalid, not merely non-overlapping.
- Non-copper layers never enter copper-layer intersection.
- Invalid/missing stackup is distinct from a valid stackup with no shared copper layers.
- Comparison uses LayerIds after validation, never display-name string equality.

## 9. Corrected discriminated ViaSpan contract and explicit physical evidence

### 9.1 Types

```ts
type EvidenceRef = { evidenceId: string; source: "explicit-model" | "verified-library" | "manufacturing-import"; contentHash: string };
type ContinuousBarrelEvidence = { kind: "continuous-plated-barrel"; evidence: EvidenceRef };

type ValidContinuousViaSpan = {
  state: "valid";
  kind: "through" | "blind" | "buried";
  endpointA: LayerId;
  endpointB: LayerId;
  barrel: ContinuousBarrelEvidence;       // required evidence; never inferred from matching layer names
};

type MicroviaStageRef = {
  stageId: string;
  from: LayerId;
  to: LayerId;
  processEvidence: EvidenceRef;
  copperNodeIds: CopperNodeId[];           // independently described stage land/barrel nodes
};

type StageJunctionEvidence =
  | { state: "certified"; contactId: ContactId; witness: ContactEvidence }
  | { state: "indeterminate"; contactId: ContactId; reason: string; evidence?: ContactEvidence }
  | { state: "not-connected"; reason: string };

type ValidMicroviaAssembly = {
  state: "valid";
  kind: "microvia-assembly";
  arrangement: "stacked" | "staggered";
  stages: MicroviaStageRef[];              // explicit manufacturing order
  junctions: Array<{ fromStageId: string; toStageId: string; evidence: StageJunctionEvidence }>;
};

type ViaSpan =
  | ValidContinuousViaSpan
  | ValidMicroviaAssembly
  | { state: "unknown"; reason: "missing-span" | "legacy-unresolved" | "missing-stackup" | "unsupported-process"; rawLegacy?: unknown }
  | { state: "invalid"; reason: "unknown-layer" | "non-copper-endpoint" | "wrong-endpoint-kind" | "invalid-order" | "invalid-stage-reference" | "invalid-stackup"; diagnostics: string[] };

type SpanEnumeration =
  | { state: "known"; orderedCopperLayerIds: LayerId[]; set: ReadonlySet<LayerId> }
  | { state: "unknown"; reasons: string[] }
  | { state: "invalid"; diagnostics: string[] };

type SpanIntersection =
  | { state: "known"; commonCopperLayerIds: LayerId[] } // [] means valid disjoint
  | { state: "unknown"; reasons: string[] }
  | { state: "invalid"; diagnostics: string[] };
```

### 9.2 Endpoint and enumeration rules

1. Resolve both endpoints by LayerId in the validated stackup. They must be enabled copper layers. Never accept a display name as endpoint identity.
2. `through`: endpoints must be exactly front and back copper. `blind`: exactly one endpoint is a front/back face and the other is internal. `buried`: both endpoints are internal. The copper traversal is inclusive between endpoint copper-order indices; endpoint order in storage does not change set membership.
3. A zero-length span (`endpointA == endpointB`) is invalid for these Via kinds. An internal endpoint absent from the stackup is invalid; missing stackup yields unknown rather than empty.
4. For an ordinary valid continuous via, enumerate every enabled copper layer between endpoints, inclusive. Each generated physical barrel-conduction edge carries the explicit `ContinuousBarrelEvidence` reference and the Via/span revision.
5. A pair of valid spans is **known-disjoint** only if both enumerations are valid and their set intersection is empty. If either enumeration is unknown/invalid, the result is unknown/invalid, never `[]`.
6. A layer-set intersection establishes possible same-layer copper-rule applicability, not a geometric electrical connection. A physical contact between Via land/barrel node and another copper node still requires certified geometry on that layer.
7. Microvia stages must each reference valid, explicitly represented endpoint layers and physical copper nodes. If the approved process requires adjacency, validate each stage is between adjacent copper layers. Each stage’s process evidence is independent.
8. Inter-stage continuity is created only by a `StageJunctionEvidence` with a certified physical contact witness between identified stage nodes/lands. Shared layer IDs, matching stage endpoints, matching names, or asserted arrangement (`stacked`/`staggered`) alone never creates a conductive edge.
9. Missing evidence does not mean a continuous barrel. Mark the affected connection unknown/indeterminate; do not join the graph.

No microvia type should be claimed implemented by this architecture. Stacked/staggered manufacturability (allowable stage transitions, capture lands, depth and process) remains product/fabricator policy.

## 10. Revised end-to-end algorithm

```text
function validateAndBuild(project):
    schemaState = validate version, Net records, assignments, stackup, padstacks, ViaSpans
    preserve INVALID and CONFLICTING assignments as first-class states
    nodes = expand all supported known copper geometry into (object, layer) nodes
    retain unknown/unsupported shapes as invalidity records, not fake simplified nodes
    emit object-level invalid/unsupported findings for unlocatable geometry; mark affected
    DRC coverage incomplete so absence of a candidate pair cannot be interpreted as CLEAR
    contacts = []
    confirmedDSU = DisjointSet(nodes)
    possibleEdges = []

    for each broad-phase candidate pair on the same resolved enabled copper LayerId:
        result = robustContactPredicate(pair)
        contactId = stableHash(sortedNodeIds, layerId, geometryHashes, kernelVersion, predicateVersion)
        persist result + full evidence in DRC-run evidence ledger
        if result.state == "positive-area-overlap":
            contacts.append(result)
            confirmedDSU.union(a, b)     // physical, independent of NetAssignment
        else if result.state == "separated":
            contacts.append(result)      // no graph edge; run clearance predicate independently
        else if result.state == "boundary-contact":
            contacts.append(result)
            possibleEdges.append(result) // boundary policy pending; do not union or clear
        else if result.state == "indeterminate":
            contacts.append(result)
            possibleEdges.append(result) // do not discard or union
        else if result.state in {"invalid-geometry", "unsupported-geometry"}:
            contacts.append(result)
            emit explicit geometry/unsupported diagnostic

    for each ViaSpan:
        if valid continuous span with explicit barrel evidence:
            add layer-specific conductive barrel nodes/edges with evidence refs
        else if valid microvia assembly:
            add each stage independently; add stage-to-stage edge only from certified contact evidence
        else:
            add no inferred cross-layer edge; retain unknown/invalid diagnostic

    components = confirmedDSU.components()
    annotate potential component adjacencies using possibleEdges
    for each node assignment:
        preserve its exact state; never coerce invalid/conflicting to unknown/unassigned
    classify each component using union(verifiedNetIds(node.assignment))
    mark invalid, conflicting, unverified-candidate, unknown, and expected-but-unassigned separately
    emit one definite short per confirmed component with >=2 distinct verified NetIds
    emit assignment invalid/conflict/incomplete findings without coercing states
    group every possible edge by unordered pair of distinct confirmed component snapshot IDs
    for each group that could alter Net connectivity/short/island status:
        emit one PCB_COPPER_CONNECTIVITY_INDETERMINATE with all object IDs, ContactIds,
        LayerIds, verified Net sets on both sides, and exact/bounded geometry evidence
    detect same-Net islands across distinct confirmed components; uncertainty blocks definite island finding
    run copper clearances, legacy v2 Via clearance, and manufacturing rules as independent predicates
    deduplicate deterministically; retain all evidence and sort outputs
```

### 10.1 Finding generation paths

| Finding ID | Generation condition | Deduplication |
|---|---|---|
| `PCB_COPPER_SHORT_CIRCUIT` | A confirmed physical component contains at least two distinct verified NetIds (including verified claims preserved inside a conflicting assignment). | One primary finding per confirmed component snapshot; all distinct Net pairs/sites in payload. |
| `PCB_COPPER_CONNECTIVITY_INDETERMINATE` | Boundary-policy unresolved or indeterminate contact between confirmed components may change topology/Net result. | One per unordered component-snapshot pair, aggregating all candidate ContactIds and evidence. |
| `PCB_NET_DISCONNECTED_ISLAND` | One verified NetId appears in multiple distinct confirmed components and all possible connecting geometry is resolved. | One per NetId and relevant component set. |
| `PCB_NET_ISLAND_CONNECTIVITY_INDETERMINATE` | Possible/unknown contact, span, zone fill, or missing expected geometry could change island classification. | One per NetId and relevant component set, with possible edges aggregated. |
| `PCB_NET_ASSIGNMENT_INVALID` | Assignment has malformed/missing/wrong-project reference. | Per object/assignment record; preserve invalid source value and reason. |
| `PCB_NET_ASSIGNMENT_CONFLICT` | Assignment state is `conflicting`, claims disagree, or verified Pad/Pin/Net sources conflict. | Per object and canonical claim-set hash. |
| `PCB_NET_ASSIGNMENT_INCOMPLETE` | `expected-but-unassigned`, unknown, unverified candidate, or electrically expected intentional-unassigned state prevents verified classification. | Per object or grouped component according to product-approved reporting cap. |
| `PCB_GEOMETRY_INVALID` / `PCB_GEOMETRY_UNSUPPORTED` | Input geometry cannot be evaluated safely. | Per object/reason; include the pair candidates impacted. |
| `PCB_GEOMETRY_INDETERMINATE` | A numeric clearance predicate cannot certify above/below its rule threshold. | Existing rule/pair semantics, with evidence ledger. |

The exact final rule IDs and severities require product-owner review; these names make generation paths explicit for design review only.

## 11. Updated adversarial examples

Assume positive-area overlap and all stated Via/internal connections have certified physical evidence. `A`, `B`, `C` below denote verified NetIds.

1. **Four-object three-Net chain:** `T1(A)—T2(A)—Pad(B)—Via(C)`. One confirmed physical component; exactly one short finding with Net set `{A,B,C}`, all three unordered Net pairs, direct sites and witness paths. Same labels on T1/T2 do not suppress Pad/Via conflicts.
2. **Dense star:** one Pad(A) touches four Tracks `{A,B,C,D}` at four certified sites. One component, one primary short finding, six unordered Net pairs and four direct sites—not six duplicate findings.
3. **Unknown assignment in the path:** Track(A)—Track(unknown)—Pad(B). Build one physical component; definite short for A/B plus assignment-incomplete diagnostic for the middle object. Do not guess its Net.
4. **Conflicting assignment on one object:** a Pad has two distinct verified claims `{A,B}` and touches a Track(A). Keep Pad assignment state `conflicting`; physical graph records contact; component short is definite, plus assignment-conflict finding. Do not rewrite Pad as unknown or select A.
5. **Unverified legacy candidate on a contact:** Track(A) overlaps Track(candidate-A-from-v2). Physical edge exists, but candidate is not verified; no same-Net exemption. Emit assignment-incomplete/uncertain classification. If another verified Net B is connected in the same physical component, A/B is still a definite short.
6. **Disconnected same-Net islands:** two separated components assigned verified A. Never join by NetId. If all possible contacts are certified absent, one disconnected-island finding for A; if a possible contact exists, island result is indeterminate.
7. **Uncertain cross-Net contact:** separate confirmed components containing A and B have one numerically indeterminate possible contact. Emit `PCB_COPPER_CONNECTIVITY_INDETERMINATE` with both component IDs, both object/node IDs, LayerId, ContactId and numeric bounds. No definite short from this contact alone; no CLEAR. If a separate certified path already connects A and B, the definite short remains and the possible contact does not replace it.
8. **Exact tangent:** the robust predicate proves a zero-area boundary contact. Store as `boundary-contact`; until the product decides electrical semantics, do not union, do not call separated, and emit the indeterminate result if it could alter connectivity.
9. **Invalid or custom unsupported Pad geometry:** preserve the Padstack and invalid/unsupported status, emit geometry finding, and do not replace it with a circle. Candidate contacts it could affect cannot be marked clear.

## 12. Legacy schema-v2 contract remains unchanged

- `minimumViaClearance` retains its observed v2 behavior for migrated v2 documents: 2D center-distance versus outer-copper radii sum plus the configured value, all Via pairs, no span gating. It is a projected copper clearance rule, not drill-to-drill clearance.
- Migration may report an unknown legacy Via span, but that diagnostic does not silently remove the v2 projected comparison. New span-aware rules are separately named and versioned.
- Any change to this behavior requires explicit product-owner approval, deliberate migration/rule mapping, regression tests, and a versioned compatibility note.
- No v2 Net string is promoted to verified. A deterministic legacy candidate remains unverified until explicit resolution. No candidate grouping creates physical connectivity.

## 13. Product-owner decisions still required

1. **Net status authority:** who can verify a Net; how candidate legacy/import assignments are approved; how unverified or invalid assignments affect sign-off.
2. **Conflict policy:** severity and UI handling for multiple verified Net claims on one object and Pad/Pin disagreement; whether a Net tie is a supported explicit exception.
3. **Unknown/unassigned semantics:** when intentional-unassigned copper is allowed; distinction between expected-but-unassigned and non-electrical/mechanical copper; severities.
4. **Short reporting:** confirm one primary finding per physical component, versus per Net pair; severity, attribution limits, and object witness display.
5. **Potential contact finding:** approve `PCB_COPPER_CONNECTIVITY_INDETERMINATE`, blocking sign-off behavior, severity, and treatment during incomplete routing.
6. **Boundary/tangent contact:** electrically conductive or not; whether a tangent different-Net touch is a short; whether same-Net tangent qualifies for the overlap exception.
7. **Contact tolerance:** nominal CAD coordinates vs physical/manufacturing tolerance; any nonzero contact tolerance and its scope. Until approved, no fuzzy snap/tolerance is used for connectivity.
8. **Geometry numeric policy:** required exact/bounded kernel guarantees, acceptable interval widths, and rule behavior if proof cannot classify.
9. **Stackup:** stable built-in IDs, physical ordering, whether disabled copper layers can appear in a via span, layer classification and mandatory metadata.
10. **Via endpoints:** through/blind/buried endpoint definitions and allowed direction/storage conventions; valid disjoint use cases.
11. **Barrel evidence:** accepted source/authority for a continuous plated barrel and whether imported geometry is sufficiently verified.
12. **Microvias:** initial support or deferral; adjacency, stacked/staggered process rules, intermediate land evidence, and fabrication limits.
13. **Island policy:** severity in incomplete routing, intentional disconnected islands, variants/test points/split nets, and required connectivity-completeness state.
14. **Padstack support:** supported shapes, holes/slots, PTH/NPTH, multiple holes, vias-in-pad, pad-to-pin mapping authority, custom geometry fallback.
15. **v2 project identity:** workspace identity availability; whether standalone fallback hash identity is acceptable; copied/edited v2 semantics; candidate name collision handling.
16. **v2 clearance:** how long to retain all-pairs legacy projected Via clearance and whether/when it migrates to the new layer-aware rule.
17. **Unknown/invalid result severity:** invalid geometry, unsupported shape, missing span, stale fill, and connectivity uncertainty must not be silently CLEAR, but severity/blocking status remains pending.
18. **Evidence retention:** which witness data is embedded in DRC run records, retention duration, reproducibility requirements, and project privacy/storage limits.

All unresolved items remain **PENDING PRODUCT-OWNER DECISION**; this report does not infer product policy from current production behavior.

## 14. Consistency audit and traceability

| Audit finding / requirement | Correction in this report | Consistency outcome |
|---|---|---|
| NetAssignment omitted expected-unassigned, invalid/conflicting, and multiple claims | §4 union defines verified, unverified-candidate, intentional-unassigned, expected-but-unassigned, unknown, invalid, conflicting with claim list | All states used by algorithm/examples now exist; invalid/conflicting states are preserved. |
| Algorithm silently referenced states not in union | §4.2, §5.2, §10 explicitly classify every state and provide `verifiedNetIds` helper | No state is converted to another state by fallback. |
| Potential contact had no generated finding | §7 defines `PCB_COPPER_CONNECTIVITY_INDETERMINATE`, generation, attribution, dedupe, short relationship, sign-off | Cross-component potential contacts cannot disappear or become CLEAR. |
| Contact only had contact/separated/indeterminate | §6 defines positive-area, boundary, separation, numeric uncertainty, invalid, unsupported as distinct outcomes | Boundary semantics explicitly pending; invalid/unsupported never become simplified CLEAR. |
| Tolerance and robust predicate were unspecified | §6.3 prohibits silent epsilon/schematic tolerance reuse; requires exact/bounded predicates and explicit uncertainty | No undocumented fuzzy electrical connection. |
| Geometry evidence, identity, retention were unspecified | §6.1 defines `ContactEvidence`, stable ContactId, kernel/version/input hashes, immutable run ledger | Every result is reproducible and attributable to source geometry/predicate. |
| LayerId/Stackup definitions were referenced but absent | §8 defines LayerId, classifications, ordered copper list, enablement, invariants, validation states | Copper intersection uses validated IDs/order, not names. |
| Via endpoints and inclusive enumeration incomplete | §9 defines kind-specific endpoint classes, inclusive span enumeration, known-empty vs unknown/invalid | Valid disjoint is distinguishable from missing/invalid. |
| Microvia connections could be inferred from stage labels | §9 requires per-stage references and explicit certified stage-junction witness | No continuous path from matching names/endpoints alone. |
| Multiple verified IDs must be a definite short | §5, §10 and examples 1–4 classify any confirmed component with ≥2 distinct verified NetIds as short, even with unknown intermediates | Definite short survives unknown annotations. |
| Disconnected same-Net islands risk merging by NetId | §5.2, §10, §11 never union by Net; classify separate components and potential-bridge uncertainty | Same Net assignment is not physical connectivity. |
| Legacy v2 behavior risk | §12 preserves exact v2 all-pairs projected Via copper check; new rule is separately named | No silent behavior change absent approval. |
| Examples lacked proof/finding consistency | §11 examples map to finding-generation paths in §10.1 | All referenced finding IDs have explicit trigger and dedupe path. |
| No product decision/readiness boundary | §2, §13, §15 define pending items and design-readiness verdict | No implementation gate is implied by proposal completion. |

### Consistency checks against requested invariants

- Every NetAssignment state used by pseudocode has a definition in §4.
- Invalid and conflicting assignments remain distinct; multiple Net references are retained as claims.
- Every named finding in examples has a trigger and dedup rule in §10.1.
- Unknown geometry cannot union nodes, receive a same-Net exemption, or produce CLEAR.
- Unknown Net identity does not block physical graph construction and cannot be treated as same-Net.
- Two or more verified NetIds in one certified physical component always produce a definite short, even if unknown/unverified objects are also present.
- Different-Net components joined only by a potential/uncertain contact produce an explicit indeterminate finding; a separate confirmed short remains definite.
- Disconnected same-Net islands remain separate physical components; only approved completeness policy decides whether to report a definite island violation.
- v2 `minimumViaClearance` behavior remains unchanged for migrated v2 documents unless explicitly approved to change.
- Valid-disjoint Via spans require two fully resolved spans; unknown/invalid is never encoded as a valid empty intersection.

## 15. Remaining blockers and unsupported claims

- No physical PCB graph, canonical Net registry, or Padstack exists in the baseline.
- Boundary contact policy is unresolved; exact tangent is retained as boundary evidence and evaluated indeterminately until decision.
- Robust exact/bounded geometry requirements and any physical tolerance are unapproved.
- Microvia construction/electrical chain is only a future representation; no production support is claimed.
- Copper Zones and their fills/thermals/islands remain unsupported.
- Slot/custom polygon/multi-hole/complex Padstack cases remain unsupported unless separately modeled and tested.
- Existing v2 via spans cannot express valid disjoint spans; v2 clearances remain all-pairs projected.
- No tests were run or changed in this design-only phase; no TP/TN/FP/FN results are claimed.

## 16. Final design-freeze gate

This document corrects the identified architecture inconsistencies but is **not an implementation authorization**. Freeze requires explicit product-owner approval of the pending decisions in §13, especially Net verification, tangent contact, uncertain-connectivity severity/sign-off, Via barrel/stage evidence, v2 migration identity, and legacy clearance mapping. Until approval, stop. Do not start Phase 6.1 or Phase 6.2.
