#!/usr/bin/env python3
import json,sys
from pathlib import Path
src=Path(sys.argv[1]); out=Path(sys.argv[2])
d9=json.loads(src.read_text())
rows=[]
for c in d9['cases']:
 ident=c['id']
 if ident in {'ordinary-45','ordinary-90','ordinary-180','ordinary-270','ordinary-360','negative-angle','adjacent-45','adjacent-90','adjacent-180','adjacent-270','adjacent-360'}:
  cls='Runtime-specific'; input_class='Finite angle; axis or adjacent-angle boundary' if ident.startswith('ordinary-') or ident.startswith('adjacent-') else 'Finite negative angle'
  req='Establish the actual Math.sin/Math.cos result and its relation to the mathematical real result without assuming an ECMAScript correct-rounding requirement.'
  oracle='Pinned-runtime bit capture plus MPFR directed intervals, unique-cell test, and cross-runtime comparison.'
  ecma='Boundary results are normative; non-boundary result is implementation-approximated under 21.3.2.31/21.3.2.12.'
  closure='Close only with runtime-scoped certificate or an authoritative standard-level bound; universal closure is unavailable from ECMAScript alone.'
 elif ident in {'large-cancellation','large-opposite'}:
  cls='Conditionally provable'; input_class='Finite operands with cancellation or opposite scale'
  req='Bound each stepwise binary64 operation and establish whether the final Model B cell is consistent with the specified sequence.'
  oracle='Exact binary64 replay plus directed MPFR intervals with outward endpoint checks.'
  ecma='Number arithmetic is binary64; the exact-real intended expression is not automatically the stepwise expression.'
  closure='Provide operation-by-operation error bounds including cancellation and prove the final cell.'
 elif ident=='huge-angle':
  cls='Runtime-specific'; input_class='Extreme finite angle'
  req='Justify argument reduction and bound the runtime trigonometric result.'
  oracle='Runtime/build/library attestation plus independently validated argument-reduction reference and MPFR cell proof.'
  ecma='Math.sin/cos non-boundary results remain implementation-approximated.'
  closure='Close only for a fully attested runtime or with a language-level bound, neither currently available.'
 elif ident=='max-angle':
  cls='Not currently provable'; input_class='Extreme finite angle and output-cell/overflow boundary'
  req='Prove a unique binary64 result and the Model A/Model B relation at the extreme boundary.'
  oracle='Directed MPFR intervals, exact binary64 cell comparison, and independently specified runtime argument reduction.'
  ecma='IEEE binary64 Number semantics are specified, but Math trig is implementation-approximated.'
  closure='Unique cell plus runtime-specific trig/error proof and explicit overflow boundary proof.'
 else:
  cls='Conditionally provable'; input_class='Overflow translation / signed zero / non-finite boundary'
  req='Prove observable JavaScript special-value propagation and distinguish it from exact-real interval semantics.'
  oracle='Raw binary64 bit tests, signed-zero total-order checks, exact operation replay, and runtime attestation.'
  ecma='Number includes signed zero, infinities, NaN, and binary64 roundTiesToEven; Math boundary rules are normative where stated.'
  closure='Close only after all special-value bits and Model A/Model B assumptions are explicitly bounded.'
 rows.append({'case_id':ident,'original_claim':' ; '.join(c['original_unresolved_proposition']),'input_class':input_class,'required_property':req,'ecmascript_support':ecma,'oracle_strategy':oracle,'proof_obligation':'Do not conflate exact-real Model A with stepwise JavaScript Model B; prove every intermediate rounding, special-value, and runtime-dependent assumption relevant to the case.','runtime_dependency':'Engine/version/platform/math-library dependent for Math.sin/Math.cos; binary64 arithmetic semantics are language-level.','evidence_required':'D9 exact-bit capture, MPFR directed interval artifact, case-specific adversarial vectors, source/runtime attestation, and independent reproduction.','classification':cls,'closure_criterion':closure})
assert len(rows)==16 and len({r['case_id'] for r in rows})==16
out.write_text(json.dumps({'source_inventory':'D9 case-by-case-closure.json','case_count':16,'cases':rows},indent=2,sort_keys=True)+'\n')
print('matrix cases:',len(rows))
