#!/usr/bin/env python3
import json, math, struct, subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path('/tmp/p24d12-report/evidence/p2-4-d-12')
ROOT.mkdir(parents=True, exist_ok=True)

# Exact binary64 helpers. These are evidence-only and are not production source.
def bits(x):
    return struct.unpack('>Q', struct.pack('>d', x))[0]

def f_from_float(x):
    if math.isinf(x):
        return None
    n, d = x.as_integer_ratio()
    return Fraction(n, d)

def hexfloat(x):
    return x.hex()

def next_float(x, direction):
    return math.nextafter(x, math.inf if direction > 0 else -math.inf)

def cell(z):
    p = next_float(z, -1)
    n = next_float(z, 1)
    upper = None if math.isinf(n) else str((f_from_float(z) + f_from_float(n)) / 2)
    return {
        'value_bits': f'0x{bits(z):016x}',
        'value_hex': hexfloat(z),
        'predecessor_bits': f'0x{bits(p):016x}',
        'successor_bits': f'0x{bits(n):016x}',
        'lower_midpoint_exact': str((f_from_float(p) + f_from_float(z)) / 2),
        'upper_midpoint_exact': upper,
        'upper_boundary': 'positive-infinity overflow boundary' if math.isinf(n) else 'finite midpoint',
        'tie_even_significand_rule_required': True,
    }

vectors = [
    {'id':'positive-one','value':1.0,'expected':'normal finite cell'},
    {'id':'negative-one','value':-1.0,'expected':'normal finite cell'},
    {'id':'positive-zero','value':0.0,'expected':'signed-zero boundary requires zero-specific handling'},
    {'id':'negative-zero','value':-0.0,'expected':'signed-zero boundary requires zero-specific handling'},
    {'id':'min-positive-subnormal','value':math.ldexp(1.0,-1074),'expected':'positive subnormal'},
    {'id':'min-negative-subnormal','value':-math.ldexp(1.0,-1074),'expected':'negative subnormal'},
    {'id':'largest-subnormal','value':math.ldexp(1.0,-1022)-math.ldexp(1.0,-1074),'expected':'subnormal/normal transition'},
    {'id':'smallest-normal','value':math.ldexp(1.0,-1022),'expected':'subnormal/normal transition'},
    {'id':'power-of-two','value':2.0,'expected':'binade transition spacing asymmetry'},
    {'id':'largest-finite','value':float.fromhex('0x1.fffffffffffffp+1023'),'expected':'finite overflow boundary'},
]
output = {
  'schema_version': 1,
  'method': 'Exact Fraction midpoints from Python-imported binary64 values; predecessor/successor obtained with math.nextafter; ties require significand parity, not approximate epsilon.',
  'independence': 'Evidence-only Python reference; does not import or execute PCB production source.',
  'limitations': [
    'Zero has signed-zero and underflow semantics that require a dedicated rounder; the midpoint listing is not by itself a complete signed-zero proof.',
    'The vectors validate the reference specification and boundary enumeration, not a production transform implementation.',
    'A rounded coordinate cell does not prove downstream orientation, intersection, distance, or DRC correctness.'
  ],
  'vectors': [{**{k:v for k,v in row.items() if k not in ('value','expected')}, 'expected':row['expected'], 'cell':cell(row['value'])} for row in vectors]
}
(ROOT/'binary64-output-cell-vectors.json').write_text(json.dumps(output, indent=2)+'\n')

# Preserve D9's authoritative case set while applying the D12 independent adjudication rule.
d9 = json.loads(subprocess.check_output([
  'git','-C','/tmp/p24d10-report','show',
  'origin/evidence/phase6-1-p2-4-d-9-adversarial-ieee754-20261128:evidence/p2-4-d-9/case-by-case-closure.json'
]))
cases = []
for c in d9['cases']:
    r = c.get('reproduction', {})
    status = 'EXPERIMENTALLY_SUPPORTED' if c['id'] in {'ordinary-270', 'negative-angle', 'large-cancellation'} else 'OPEN'
    cases.append({
      'case_id': c['id'],
      'original_property': c['original_unresolved_proposition'],
      'reproduction_result': {
        'reproduced': True,
        'capture_present': r.get('capture_present'),
        'mpfr_record_present': r.get('mpfr_record_present'),
        'trig_interval_contains_js': r.get('trig_interval_contains_js'),
        'model_a_contains_model_b': r.get('model_a_contains_model_b'),
        'output_cell_unique': r.get('output_cell_unique'),
      },
      'independent_proof': False,
      'proof_status': status,
      'closure_counted': False,
      'reason': 'Runtime/MPFR observation is reproducible, but no runtime-specific trig certificate or complete Model-A/Model-B operation proof is present.',
      'source': 'D9 case-by-case-closure.json and D10 case-adjudication-matrix.json'
    })
oracle = {
  'schema_version': 1,
  'fields': {'case_id':'D9 identifier','original_property':'unresolved proposition','reproduction_result':'captured evidence fields','independent_proof':'boolean','proof_status':'PROVEN|EXPERIMENTALLY_SUPPORTED|ASSUMED|OPEN','closure_counted':'boolean','reason':'adjudication rule','source':'artifact provenance'},
  'case_count': len(cases), 'closed_count': sum(c['closure_counted'] for c in cases), 'remaining_count': len(cases), 'cases': cases,
  'rule': 'A case closes only when the original property is independently established; reproduction, MPFR agreement, or two-implementation agreement alone is insufficient.'
}
(ROOT/'oracle-case-inventory.json').write_text(json.dumps(oracle, indent=2)+'\n')

ellipse_classes = [
 'ordinary ellipse interactions','near-tangent','nearly coincident boundaries','very small dimensions','very large finite dimensions','high aspect ratio','near-zero clearance','interval dependency widening','slow subdivision convergence','budget exhaustion'
]
ellipse = {
 'schema_version':1,
 'fields': {'case_class':'required geometry class','production_evaluator_present':'whether D12 found the proposed evaluator in the baseline','reference_oracle':'available independent reference','budget_status':'UNVALIDATED|SUPPORTED|REJECTED','conclusion':'evidence disposition'},
 'proposed_budget': {'MAX_CERTIFIED_CELLS':4096,'MAX_INTERVAL_EVALUATIONS':32768,'MAX_SUBDIVISION_DEPTH':32},
 'production_evaluator_present': False,
 'budget_status':'UNVALIDATED',
 'cases': [{
   'case_class': cls,
   'production_evaluator_present': False,
   'reference_oracle': 'Not executed against a production evaluator; analytic reference may be designed but cannot validate absent implementation.',
   'budget_status':'UNVALIDATED',
   'conclusion':'No counters, runtime, memory, or exhaustion behavior can be measured in this design-only phase.'
 } for cls in ellipse_classes],
 'semantic_requirements': {
   'intersection':'certified overlap/contact, not tolerance guess',
   'tangency':'exact or certified contact relation',
   'threshold_equality':'must be specified by DRC policy; no evidence here establishes pass/fail for equality',
   'positive_separation':'certified positive lower bound',
   'indeterminate':'error-severity fail-closed geometry result',
   'gJK_policy':'unchanged; budget is not a GJK iteration cap'
 }
}
(ROOT/'ellipse-budget-validation.json').write_text(json.dumps(ellipse, indent=2)+'\n')

route = {
 'schema_version':1,
 'fields': {'file_line':'exact source location','function':'symbol','caller':'direct caller','current_behavior':'baseline behavior','checked_path_requirement':'D12 requirement','compatibility_risk':'risk','required_fixture':'fixture','status':'OPEN|DESIGN_ONLY'},
 'baseline': 'P2.4-B e567acb883a0f81cb0c64d11f638b5f872511346',
 'entries': [
  {'file_line':'shared/engineering.ts:33','function':'route45','caller':'external callers; no checked route caller identified in baseline','current_behavior':'raw endpoint subtraction, absolute EPSILON comparisons, array result','checked_path_requirement':'route45Checked must validate representability and duplicate-waypoint invariants before client use','compatibility_risk':'legacy [start,end] can be mistaken for valid route45','required_fixture':'opposite-sign MAX_VALUE, invalid input, ordinary two/three-point, transactional failure','status':'OPEN'},
 ]
}
(ROOT/'route45-callsite-inventory.json').write_text(json.dumps(route, indent=2)+'\n')

transform = {
 'schema_version':1,
 'fields': {'file_line':'exact source location','function':'symbol','caller':'consumer','current_behavior':'baseline behavior','checked_path_requirement':'D12 requirement','compatibility_risk':'risk','required_fixture':'fixture','status':'OPEN|DESIGN_ONLY'},
 'baseline':'P2.4-B e567acb883a0f81cb0c64d11f638b5f872511346',
 'entries': [
  {'file_line':'shared/engineering.ts:31','function':'rotatePoint','caller':'transformLocalPoint and external callers','current_behavior':'direct Math.sin/cos and two-product arithmetic','checked_path_requirement':'internal checked transform with coefficient/error enclosure','compatibility_risk':'public best-effort point cannot carry uncertainty','required_fixture':'ordinary/special/cancellation/signed-zero/overflow','status':'OPEN'},
  {'file_line':'shared/engineering.ts:32','function':'transformLocalPoint','caller':'localPads:125; validateSchematic:340','current_behavior':'adds raw rotated point to origin','checked_path_requirement':'checked transform and localized state','compatibility_risk':'untrusted finite residual can enter pads/pins','required_fixture':'large origin, cancellation, non-representable translation','status':'OPEN'},
  {'file_line':'shared/engineering.ts:125','function':'localPads','caller':'evaluatePcbV2:372','current_behavior':'maps transformed pads without checked state','checked_path_requirement':'uncertain pad blocks only dependent clearance findings','compatibility_risk':'raw transform reaches DRC','required_fixture':'uncertain pad plus unrelated pad findings','status':'OPEN'},
  {'file_line':'shared/engineering.ts:340','function':'validateSchematic pin transform','caller':'validateSchematic','current_behavior':'raw transformed point is union candidate','checked_path_requirement':'uncertain pin cannot union','compatibility_risk':'false topology union','required_fixture':'uncertain pin and unrelated required pin','status':'OPEN'},
  {'file_line':'shared/engineering.ts:381','function':'padToPadDistanceDetailed consumer','caller':'evaluatePcbV2','current_behavior':'finite numeric result drives clearance comparison','checked_path_requirement':'consume interval/state and fail closed','compatibility_risk':'uncertainty can become pass or false geometry','required_fixture':'interval overlap and transformed uncertain pad','status':'OPEN'}
 ]
}
(ROOT/'transform-callsite-inventory.json').write_text(json.dumps(transform, indent=2)+'\n')

shape = {
 'schema_version':1,
 'fields': {'file_line':'exact source location','function':'symbol','caller':'consumer','current_behavior':'baseline behavior','checked_path_requirement':'D12 requirement','compatibility_risk':'risk','required_fixture':'fixture','status':'OPEN|DESIGN_ONLY'},
 'baseline':'P2.4-B e567acb883a0f81cb0c64d11f638b5f872511346',
 'entries': [
  {'file_line':'shared/engineering.ts:256-258','function':'strictOrientation/strictOnSegment/strictSegmentsIntersect','caller':'strictSegmentDistance, pointInConvexPolygon','current_behavior':'absolute 1e-12 determinant and coordinate tolerance','checked_path_requirement':'exact dyadic sign or interval indeterminate','compatibility_risk':'small positive gaps collapse to contact','required_fixture':'1e-7 width, approximately 2e-13 gap','status':'OPEN'},
  {'file_line':'shared/engineering.ts:259-261','function':'strictSegmentDistance/rectToRectDistance','caller':'padToPadDistanceDetailed:292','current_behavior':'zero returned on tolerance-based intersection','checked_path_requirement':'certified distance interval; no guessed zero','compatibility_risk':'false DRC violation','required_fixture':'small-scale separation, tangency, overlap, translated copies','status':'OPEN'},
  {'file_line':'shared/engineering.ts:262','function':'rectToOvalDistance/ellipse helpers','caller':'padToPadDistanceDetailed:292','current_behavior':'analytic/iterative distance path; no proposed certified budget','checked_path_requirement':'deterministic interval proof or indeterminate','compatibility_risk':'budget adequacy and overflow unvalidated','required_fixture':'near tangent, high aspect, overflow, exhaustion','status':'OPEN'},
  {'file_line':'shared/engineering.ts:381','function':'DRC pad-to-pad consumer','caller':'evaluatePcbV2','current_behavior':'indeterminate/nonfinite maps to PCB_GEOMETRY_INDETERMINATE; finite values compare threshold','checked_path_requirement':'preserve fail-closed semantics for all uncertainty','compatibility_risk':'new states may be dropped by wrappers','required_fixture':'uncertain distance cannot pass; finding IDs/order stable','status':'OPEN'}
 ]
}
(ROOT/'shape-distance-callsite-inventory.json').write_text(json.dumps(shape, indent=2)+'\n')

baseline = {
 'schema_version':1,
 'fields': {'reference':'commit or branch','sha':'identity','parent_or_ancestry':'Git relationship','source_tree_status':'applicability','compatibility_disposition':'future requirement'},
 'entries': [
  {'reference':'P2.4-B baseline','sha':'e567acb883a0f81cb0c64d11f638b5f872511346','parent_or_ancestry':'parent 3ed17c246dadf80eab73f81bfc775845d582dbf1','source_tree_status':'exact D11 implementation target; raw geometry paths present','compatibility_disposition':'implementation planning must start here or explicitly reconcile forward'},
  {'reference':'P2.4-C original','sha':'21b7487eec431dcb993a44d0d642a33644141526','parent_or_ancestry':'child of P2.4-B','source_tree_status':'unmerged historical reference','compatibility_disposition':'compatibility target only'},
  {'reference':'accepted P2.4-C remediation','sha':'327fc0479031279b889ea1dd1140a23d4abe442f','parent_or_ancestry':'child of P2.4-C original; P2.4-B ancestor','source_tree_status':'unmerged; absent from current main','compatibility_disposition':'future adapter/integration target; do not describe as main behavior'},
  {'reference':'current source main','sha':'a98384bbfc3296947b90f5254a03a77b11fdc8a9','parent_or_ancestry':'not descended from P2.4-B/P2.4-C references','source_tree_status':'historical current-main tree, earlier/different source state','compatibility_disposition':'not interchangeable with D11 baseline'},
  {'reference':'D11 report','sha':'1106443b890dc9f64d46bdc47d13ea1f0f5eac59','parent_or_ancestry':'documentation branch from report main','source_tree_status':'design closure only','compatibility_disposition':'does not authorize implementation'}
 ],
 'changed_files_p2_4_c_vs_b':['shared/engineering.ts','shared/phase6-1-p2-4-c-numerical-uncertainty.test.ts']
}
(ROOT/'baseline-compatibility-matrix.json').write_text(json.dumps(baseline, indent=2)+'\n')

proof = {
 'schema_version':1,
 'fields': {'claim':'reviewed proposition','mathematical_basis':'basis','required_assumptions':'assumptions','evidence_or_derivation':'current support','independent_verification':'method','counterexample_or_failure':'failure mode','status':'PROVEN|EXPERIMENTALLY_SUPPORTED|ASSUMED|OPEN'},
 'claims': [
  {'claim':'Exact finite binary64 input decomposition into dyadics','mathematical_basis':'IEEE-754 binary64 bit interpretation','required_assumptions':'raw bits imported without decimal conversion','evidence_or_derivation':'D7-D10 manifests and D9 captures record raw hexadecimal bits','independent_verification':'re-decode bit patterns with exact integer/exponent parser','counterexample_or_failure':'decimal import or signed-zero loss','status':'EXPERIMENTALLY_SUPPORTED'},
  {'claim':'Arbitrary-angle interval trig kernel encloses the mathematical result','mathematical_basis':'range reduction plus polynomial remainder bound','required_assumptions':'published constants, exact quotient, outward widening, complete remainder proof','evidence_or_derivation':'D11 design only; no constants or derivation artifact published','independent_verification':'review constants and interval proof against independent high-precision oracle','counterexample_or_failure':'quadrant-boundary straddle, missing directed rounding, Table Maker uncertainty','status':'OPEN'},
  {'claim':'MPFR proves ECMAScript Math.sin/cos correctness','mathematical_basis':'none without runtime approximation contract','required_assumptions':'runtime-specific libm/error bound','evidence_or_derivation':'D10 explicitly rejects this inference','independent_verification':'runtime/library attestation plus bound','counterexample_or_failure':'implementation-approximated ECMAScript Math functions','status':'OPEN'},
  {'claim':'Output-cell containment proves one rounded binary64 coordinate','mathematical_basis':'roundTiesToEven predecessor/successor midpoint cells','required_assumptions':'correct nextUp/nextDown, signed-zero, subnormal, tie, overflow handling','evidence_or_derivation':'independent D12 reference vectors; no product implementation','independent_verification':'exact Fraction boundary vectors and tie tests','counterexample_or_failure':'cell proof discarded before geometry classification','status':'EXPERIMENTALLY_SUPPORTED'},
  {'claim':'Output-cell certification proves downstream geometry correctness','mathematical_basis':'not implied by scalar rounding','required_assumptions':'consumers preserve and consume enclosures','evidence_or_derivation':'baseline consumers accept Point/number values and discard uncertainty','independent_verification':'call-site audit and integration tests','counterexample_or_failure':'raw rounded point treated as exact; false union/clearance','status':'OPEN'},
  {'claim':'4096/32768/32 ellipse budget is adequate','mathematical_basis':'requires convergence/resource analysis over corpus','required_assumptions':'certified interval evaluator exists and is benchmarked','evidence_or_derivation':'proposed only; evaluator absent from baseline','independent_verification':'independent oracle, counters, runtime/memory corpus','counterexample_or_failure':'slow convergence or interval dependency exhaustion','status':'OPEN'},
  {'claim':'Q1-Q5 policies are specified by D11 closure','mathematical_basis':'contract policy decisions','required_assumptions':'later closure report is supplementary, not implementation proof','evidence_or_derivation':'D11 report and matrix','independent_verification':'provenance comparison and source call-site audit','counterexample_or_failure':'policy mistaken for implemented behavior','status':'EXPERIMENTALLY_SUPPORTED'}
 ]
}
(ROOT/'proof-review-matrix.json').write_text(json.dumps(proof, indent=2)+'\n')

manifest = {'schema_version':1,'phase':'P2.4-D-12','generated_by':'evidence-only Python reference','artifacts':sorted(p.name for p in ROOT.glob('*.json') if p.name != 'artifact-hashes.json')}
(ROOT/'evidence-method-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
