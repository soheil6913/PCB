#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, shutil, subprocess, hashlib, platform, sys
ROOT = pathlib.Path('/tmp/p24d7-work')
cap = json.loads((ROOT/'javascript-capture.json').read_text())
mpfr = json.loads((ROOT/'mpfr-results.json').read_text())
binr = json.loads((ROOT/'binary64-results.json').read_text())
(ROOT/'source-attestation.json').write_text(json.dumps(cap['attestation'], indent=2, sort_keys=True)+'\n')
(ROOT/'source-expression-order.json').write_text(json.dumps(cap['expressions'], indent=2, sort_keys=True)+'\n')
(ROOT/'javascript-runtime-capture.json').write_text(json.dumps({'runtime': cap['runtime'], 'vectors': cap['vectors']}, indent=2, sort_keys=True)+'\n')
(ROOT/'model-a-results.json').write_text(json.dumps(mpfr, indent=2, sort_keys=True)+'\n')
(ROOT/'model-b-stepwise-results.json').write_text(json.dumps({'runtime': cap['runtime'], 'vectors': [{'id': v['id'], 'input': v['input'], 'rotate': v['rotate'], 'transform': v['transform'], 'route': v['route'], 'source_runtime': v['source_runtime']} for v in cap['vectors']]}, indent=2, sort_keys=True)+'\n')
trig = {'summary': {k:v for k,v in mpfr['summary'].items() if k.startswith('trig_')}, 'vectors': [{'id': v['id'], 'trig_bits': v['trig_bits'], 'trig_interval_contains_js': v['trig_interval_contains_js'], 'trig_unique_binary64': v['trig_unique_binary64'], 'trig_js_uniquely_rounded': v['trig_js_uniquely_rounded'], 'mpfr_intervals': v['mpfr_intervals']} for v in mpfr['vectors']]}
(ROOT/'mpfr-trigonometric-comparison.json').write_text(json.dumps(trig, indent=2, sort_keys=True)+'\n')
unresolved = []
for v in mpfr['vectors']:
    reasons=[]
    if not v['trig_interval_contains_js']: reasons.append('captured JavaScript Math.sin/cos is outside at least one directed MPFR interval')
    if not v.get('model_a_output_interval_contains_model_b', False):
        reasons.append('Model A transformed-coordinate enclosure does not contain the captured Model B output')
    if any(x is None for x in v['output_expected_bits_if_unique'].values()): reasons.append('Model A output interval does not prove a unique binary64 output cell')
    if reasons: unresolved.append({'id': v['id'], 'reasons': reasons})
(ROOT/'unresolved-cases.json').write_text(json.dumps({'count': len(unresolved), 'cases': unresolved}, indent=2, sort_keys=True)+'\n')
shas=[]
for p in sorted(ROOT.iterdir()):
    if p.is_file() and p.name != 'reproducibility-manifest.json' and p.suffix in {'.py','.ts','.c','.json'}:
        shas.append({'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size})
manifest = {
    'source_expected_sha': '941262899a46e54cbf1a94a4da6dd528b8d36780',
    'source_checkout': '/tmp/p24d7-source',
    'source_file_sha256': cap['attestation']['files'],
    'source_file_sha256_after': cap['attestation']['filesAfter'],
    'source_status_porcelain': cap['attestation']['dirtyStatus'],
    'runtime': cap['runtime'],
    'python': sys.version,
    'platform': platform.platform(),
    'gmpy2': subprocess.check_output([sys.executable,'-c','import gmpy2; print(gmpy2.version())'], text=True).strip(),
    'toolchain': {'capture': '/tmp/p24c-numerical-uncertainty/source/node_modules/.bin/tsx capture.ts', 'mpfr': 'python3 mpfr_eval.py', 'binary64': 'python3 binary64_suite.py', 'analyze': 'python3 analyze.py'},
    'artifact_hashes': shas,
}
(ROOT/'reproducibility-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
shutil.copy(ROOT/'binary64-results.json', ROOT/'binary64-operation-vectors.json')
print(json.dumps({'artifacts': sorted(p.name for p in ROOT.iterdir() if p.suffix == '.json')}, indent=2))
