#!/usr/bin/env python3
import json, gmpy2, sys
from gmpy2 import mpfr

def describe(label, x):
    return {"label":label,"str":str(x),"repr":repr(x),"equal_zero":bool(x==0),"is_zero":bool(gmpy2.is_zero(x)),"sign":int(gmpy2.sign(x)),"to_binary_hex":gmpy2.to_binary(x).hex()}
vals=[("plus_zero",mpfr("0")),("minus_zero",mpfr("-0")),("plus_one",mpfr("1")),("minus_one",mpfr("-1"))]
out={"gmpy2_version":gmpy2.version(),"precision":256,"values":[describe(k,v) for k,v in vals],"conclusion":"MPFR preserves a sign in its internal binary serialization for signed zero if exposed by the binding, but ordinary real equality and decimal text collapse both zeros; therefore JavaScript bit semantics must be checked independently."}
json.dump(out,open(sys.argv[1],'w'),indent=2,sort_keys=True); open(sys.argv[1],'a').write('\n')
print(json.dumps(out,indent=2))
