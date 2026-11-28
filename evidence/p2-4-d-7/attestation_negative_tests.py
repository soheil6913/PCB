#!/usr/bin/env python3
from __future__ import annotations
import os, pathlib, shutil, subprocess, tempfile

ROOT = pathlib.Path('/tmp/p24d7-work')
TSX = '/tmp/p24c-numerical-uncertainty/source/node_modules/.bin/tsx'
CAPTURE = ROOT / 'capture.ts'
PINNED = pathlib.Path('/tmp/p24d7-source')
EXPECTED = '941262899a46e54cbf1a94a4da6dd528b8d36780'

def run(source: pathlib.Path, expected=EXPECTED):
    env = os.environ.copy(); env.update({
        'PCB_SOURCE_WORKTREE': str(source),
        'PCB_EXPECTED_SOURCE_SHA': expected,
        'CAPTURE_OUTPUT': str(ROOT / 'should-not-exist.json'),
    })
    return subprocess.run([TSX, str(CAPTURE)], cwd=ROOT, env=env, text=True, capture_output=True)

cases = []
# Wrong HEAD: the existing clean source checkout is intentionally at a different SHA.
r = run(pathlib.Path('/tmp/p24c-numerical-uncertainty/source'))
cases.append(('wrong-head', r.returncode != 0 and 'SOURCE_ATTESTATION_FAILED' in r.stderr + r.stdout))
# Wrong path: a directory that is not a Git checkout.
with tempfile.TemporaryDirectory(prefix='p24d7-wrong-path-') as d:
    r = run(pathlib.Path(d)); cases.append(('wrong-path', r.returncode != 0 and 'SOURCE_ATTESTATION_FAILED' in r.stderr + r.stdout))
# Dirty and modified source copies are separate temporary Git checkouts.
for label, modify in [('dirty-worktree', lambda p: (p / 'UNTRACKED_EVIDENCE_FILE').write_text('dirty\n')), ('modified-source', lambda p: (p / 'shared/engineering.ts').write_text((p / 'shared/engineering.ts').read_text() + '\n// evidence mutation\n'))]:
    with tempfile.TemporaryDirectory(prefix='p24d7-negative-') as d:
        target = pathlib.Path(d) / 'source'
        subprocess.run(['git', 'clone', '--quiet', '--local', str(PINNED), str(target)], check=True)
        modify(target)
        r = run(target)
        cases.append((label, r.returncode != 0 and 'SOURCE_ATTESTATION_FAILED' in r.stderr + r.stdout))
print({'cases': len(cases), 'passed': sum(x[1] for x in cases), 'results': [{'id': k, 'passed': v} for k,v in cases]})
if not all(v for _, v in cases): raise SystemExit('attestation negative test failed')
