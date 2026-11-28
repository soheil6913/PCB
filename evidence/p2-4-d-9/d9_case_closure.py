#!/usr/bin/env python3
import hashlib,json,os,subprocess,sys
from pathlib import Path
INV=json.loads(Path(sys.argv[1]).read_text())
CAP=json.loads(Path(sys.argv[2]).read_text())
MP=json.loads(Path(sys.argv[3]).read_text())
OUT=Path(sys.argv[4])
EXPECTED='941262899a46e54cbf1a94a4da6dd528b8d36780'
source=Path(os.environ.get('PCB_SOURCE_WORKTREE','/tmp/p24d7-source')).resolve()

def run(*a): return subprocess.run(a,text=True,capture_output=True,check=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bits(v):
    return {k:v[k] for k in ['rad_bits','x_bits','y_bits','ox_bits','oy_bits'] if k in v}
def input_bits(v):
    return {k:v['input'][k]['bits'] for k in ['degrees','radians'] if k in v['input']} | {f'local.{k}':v['input']['local'][k]['bits'] for k in ['x','y']} | {f'origin.{k}':v['input']['origin'][k]['bits'] for k in ['x','y']}
cap={v['id']:v for v in CAP['vectors']}; mp={v['id']:v for v in MP['vectors']}
orig={x['id']:x for x in INV['inventory']}
rows=[]
for ident in [x['id'] for x in INV['inventory']]:
    c=cap[ident]; m=mp[ident]; o=orig[ident]
    issue=o['mathematical_or_numerical_issue']
    trig_mismatch=not m.get('trig_interval_contains_js',True)
    unique=m.get('output_cell_unique',{})
    if trig_mismatch:
        oracle='Independent Node/V8 capture + 256-bit directed MPFR interval and unique-cell comparison'
        status='implementation-dependent under available assumptions; observed mismatch is reproducible but not a proof of incorrect ECMAScript behavior'
    elif ident=='overflow-translation':
        oracle='Independent JavaScript bit probe + binary64 special-value propagation'
        status='bounded runtime observation; exact-real/stepwise relation remains unresolved'
    else:
        oracle='Directed MPFR interval + exact binary64 bit comparison'
        status='bounded only; original proposition remains unresolved'
    rows.append({'id':ident,'original_unresolved_proposition':issue,'reproduction':{'capture_present':True,'fresh_capture_bits':input_bits(c)|bits(c),'mpfr_record_present':True,'trig_interval_contains_js':m.get('trig_interval_contains_js'),'model_a_contains_model_b':m.get('model_a_output_interval_contains_model_b'),'output_cell_unique':unique},'independent_oracle':oracle,'determination':status,'reproducible_test':'capture.ts + analyze.py/mpfr_eval.py + binary64_suite.py; case-specific bits are in this record','final_disposition':'NOT CLOSED — proposition not independently established; retain for next authorized evidence phase'})
observed=run('git','-C',str(source),'rev-parse','HEAD').stdout.strip(); dirty=run('git','-C',str(source),'status','--porcelain=v1','--untracked-files=all').stdout
out={'attestation':{'sourceRoot':str(source),'expectedSha':EXPECTED,'observedSha':observed,'dirtyStatus':dirty,'fileSha256':sha(source/'shared/engineering.ts'),'accepted':observed==EXPECTED and not dirty},'summary':{'inventory_count':len(rows),'closed_count':0,'remaining_count':len(rows),'trig_mismatch_count':sum(not mp[x['id']].get('trig_interval_contains_js',True) for x in INV['inventory']),'verdict':'PARTIALLY_VALIDATED'},'cases':rows,'acceptance_matrix':[{'id':x['id'],'reproduced':True,'oracle_established':False,'closed':False,'reason':'Runtime and MPFR evidence reproduced; original unresolved proposition remains unproven'} for x in INV['inventory']]}
OUT.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out['summary']))
