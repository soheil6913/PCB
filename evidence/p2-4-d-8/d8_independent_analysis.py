#!/usr/bin/env python3
import hashlib, json, os, subprocess, sys
from pathlib import Path

EXPECTED = "941262899a46e54cbf1a94a4da6dd528b8d36780"
SOURCE = Path(os.environ.get("PCB_SOURCE_WORKTREE", "/tmp/p24d7-source")).resolve()
CAPTURE = Path(sys.argv[1]).resolve()
MPFR = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
source_file = SOURCE / "shared/engineering.ts"

def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=True)

def sha(path):
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()

def attest():
    observed = run("git", "-C", str(SOURCE), "rev-parse", "HEAD").stdout.strip()
    dirty = run("git", "-C", str(SOURCE), "status", "--porcelain=v1", "--untracked-files=all").stdout
    return {"sourceRoot":str(SOURCE),"expectedSha":EXPECTED,"observedSha":observed,"dirtyStatus":dirty,"file":{"path":str(source_file),"sha256":sha(source_file),"bytes":source_file.stat().st_size},"accepted":observed==EXPECTED and not dirty and source_file.exists()}

capture=json.loads(CAPTURE.read_text())
mpfr=json.loads(MPFR.read_text())
by_id={v["id"]:v for v in mpfr["vectors"]}
unresolved=["ordinary-45","ordinary-90","ordinary-180","ordinary-270","ordinary-360","negative-angle","adjacent-45","adjacent-90","adjacent-180","adjacent-270","adjacent-360","large-cancellation","large-opposite","huge-angle","max-angle","overflow-translation"]
proof={
 "ordinary-45":"directed-rounding MPFR interval plus independent JavaScript execution; do not infer universal libm correctness",
 "ordinary-90":"directed-rounding MPFR interval plus independent JavaScript execution; inspect exact-axis signed-zero and cancellation",
 "ordinary-180":"directed-rounding MPFR interval plus independent JavaScript execution; inspect exact-axis signed-zero and cancellation",
 "ordinary-270":"directed-rounding MPFR interval plus independent JavaScript execution; inspect exact-axis signed-zero and cancellation",
 "ordinary-360":"directed-rounding MPFR interval plus independent JavaScript execution; inspect exact-axis signed-zero and cancellation",
 "negative-angle":"directed-rounding interval and independent JavaScript bit comparison for negative-angle reduction",
 "adjacent-45":"adversarial boundary testing and independent JavaScript bit comparison around the adjacent degree values",
 "adjacent-90":"adversarial boundary testing and independent JavaScript bit comparison around the adjacent degree values",
 "adjacent-180":"adversarial boundary testing and independent JavaScript bit comparison around the adjacent degree values",
 "adjacent-270":"adversarial boundary testing and independent JavaScript bit comparison around the adjacent degree values",
 "adjacent-360":"adversarial boundary testing and independent JavaScript bit comparison around the adjacent degree values",
 "large-cancellation":"MPFR interval verification with directed rounding and exact binary64 final-operation replay",
 "large-opposite":"MPFR interval verification with directed rounding and exact binary64 final-operation replay",
 "huge-angle":"independent JavaScript execution across runtimes plus a separately specified argument-reduction reference; implementation-dependent until then",
 "max-angle":"MPFR interval verification, binary64 cell comparison, and explicit overflow/non-finite boundary proof",
 "overflow-translation":"binary64 bit-level comparison, independent JavaScript execution, and explicit IEEE-754 non-finite propagation proof",
}

inventory=[]
for ident in unresolved:
    v=by_id[ident]
    trig=v.get("trig_interval_contains_js")
    tuniq=v.get("trig_unique_binary64",{})
    model=v.get("model_a_output_interval_contains_model_b", False)
    cell=v.get("output_cell_unique",{})
    reasons=[]
    if trig is False: reasons.append("captured JavaScript trigonometric result is outside at least one directed MPFR interval")
    if model is False: reasons.append("exact-real Model A output enclosure does not contain stepwise Model B output")
    if cell and not all(cell.values()): reasons.append("Model A output interval does not prove a unique binary64 output cell")
    severity="high" if ident in {"max-angle","overflow-translation","huge-angle"} else "medium"
    inventory.append({"id":ident,"mathematical_or_numerical_issue":reasons,"existing_evidence":{"reproduced_from_fresh_capture":True,"trig_interval_contains_js":trig,"trig_unique_binary64":tuniq,"output_cell_unique":cell,"model_a_contains_model_b":model,"source_final_bits":v.get("source_final_bits"),"output_ulp_difference_if_unique":v.get("output_ulp_difference_if_unique")},"missing_evidence":["A proof connecting the implementation-dependent ECMAScript Math.sin/Math.cos result to the exact-real MPFR model without assuming universal correct rounding." if trig is False else "No trig interval mismatch for this case; remaining output-model relation still needs proof." ,"A complete signed-zero/non-finite semantic correspondence where applicable."],"reproducibility_status":"REPRODUCED in independent D8 rerun from freshly captured JSON and MPFR output","severity":severity,"required_proof":proof[ident],"final_disposition":"REMAINS_UNRESOLVED — retained for D9; no unresolved case is promoted to passed"})

mismatch=[]
for v in mpfr["vectors"]:
    if not v.get("trig_interval_contains_js", True):
        mismatch.append({"id":v["id"],"trig_bits":v.get("trig_bits"),"trig_interval_contains_js":False,"trig_unique_binary64":v.get("trig_unique_binary64"),"trig_js_uniquely_rounded":v.get("trig_js_uniquely_rounded"),"model_a_model_b_containment":v.get("model_a_output_interval_contains_model_b"),"output_cell_unique":v.get("output_cell_unique"),"output_ulp_difference_if_unique":v.get("output_ulp_difference_if_unique")})

summary={"d8_rerun":{"vector_count":len(capture["vectors"]),"source_sha":capture["attestation"]["observedSha"],"capture_byte_sha256":sha(CAPTURE),"mpfr_byte_sha256":sha(MPFR)},"d7_reproduced_counts":mpfr["summary"],"unresolved_case_count":len(inventory),"closed_count":0,"remaining_unresolved_count":len(inventory),"trig_mismatch_count":len(mismatch),"verdict":"PARTIALLY_VALIDATED"}
result={"attestation":attest(),"summary":summary,"inventory":inventory,"trigonometric_mismatch_investigation":mismatch,"model_policy":{"model_a":"exact-real/MPFR directed-rounding interval propagation","model_b":"actual JavaScript binary64 operation sequence captured from pinned source","relationship":"not interchangeable; containment failure is an evidence gap, not proof of a production defect or universal trig failure"}}
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
print(json.dumps({"output":str(OUT),"inventory":len(inventory),"mismatches":len(mismatch),"closed":0,"remaining":len(inventory)},indent=2))
