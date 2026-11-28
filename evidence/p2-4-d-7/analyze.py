#!/usr/bin/env python3
from __future__ import annotations
import json, pathlib, subprocess, sys, shlex
from fractions import Fraction
from binary64 import bits_hex, round_fraction, from_bits, SIGN, MASK64

CAPTURE = pathlib.Path(sys.argv[1])
MPFR_BIN = pathlib.Path(sys.argv[2])
OUT = pathlib.Path(sys.argv[3])
data = json.loads(CAPTURE.read_text())

def parse_bits(s: str) -> int: return int(s, 16)
def rep_fraction(s: str) -> Fraction:
    if 'NaN' in s or '@' in s or 'Inf' in s:
        return None
    # MPFR helper format: [+|-]0.<binary-significand>e<base-2 exponent>.
    mant, exp = s.split('e')
    sign = -1 if mant.startswith('-') else 1
    digits = mant[3:] if mant[0] in '+-' else mant[2:]
    e = int(exp)
    n = int(digits, 2) if digits else 0
    # gmpy2.digits(base=2) returns m and e such that the binary
    # fraction 0.m is scaled by 2^e.
    shift = e - len(digits)
    value = Fraction(n << shift, 1) if shift >= 0 else Fraction(n, 1 << -shift)
    return sign * value

def ordered(b: int) -> int:
    return ((~b) & MASK64) if (b & SIGN) else (b ^ SIGN)
def ulp_diff(a: int, b: int) -> int: return abs(ordered(a) - ordered(b))
def unique_round(lo, hi, lo_raw, hi_raw):
    if lo is None or hi is None or round_fraction(lo) != round_fraction(hi): return None
    if lo == 0 and hi == 0 and lo_raw.startswith('-') and hi_raw.startswith('-'):
        return SIGN
    return round_fraction(lo)

def parse_line(line: str):
    fields = line.split()
    result = {'id': fields[0]}
    for token in fields[1:]:
        key, value = token.split('=', 1)
        result[key] = rep_fraction(value)
        result[key + '_raw'] = value
    return result

rows = data['vectors']
tsv = ''.join(f"{r['id']} {r['rad_bits'][2:]} {r['x_bits'][2:]} {r['y_bits'][2:]} {r['ox_bits'][2:]} {r['oy_bits'][2:]}\n" for r in rows)
proc = subprocess.run(shlex.split(str(MPFR_BIN)), input=tsv, text=True, capture_output=True, check=True)
mpfr = {r['id']: r for r in map(parse_line, proc.stdout.splitlines())}
results = []
for row in rows:
    m = mpfr[row['id']]
    steps = row['rotate']['steps']
    sin_bits = next(x['bits'] for x in steps if x['operation'] == 'Math.sin(radians)')
    cos_bits = next(x['bits'] for x in steps if x['operation'] == 'Math.cos(radians)')
    sin_b, cos_b = parse_bits(sin_bits), parse_bits(cos_bits)
    sx_bits, sy_bits = parse_bits(row['transform']['source_result']['x']['bits']), parse_bits(row['transform']['source_result']['y']['bits'])
    sin_lo, sin_hi = m['sin_lo'], m['sin_hi']; cos_lo, cos_hi = m['cos_lo'], m['cos_hi']
    x_lo, x_hi = m['x_lo'], m['x_hi']; y_lo, y_hi = m['y_lo'], m['y_hi']
    sin_val = Fraction.from_float(from_bits(sin_b)) if sin_b & 0x7ff0000000000000 != 0x7ff0000000000000 else None
    cos_val = Fraction.from_float(from_bits(cos_b)) if cos_b & 0x7ff0000000000000 != 0x7ff0000000000000 else None
    source_x = Fraction.from_float(from_bits(sx_bits)) if sx_bits & 0x7ff0000000000000 != 0x7ff0000000000000 else None
    source_y = Fraction.from_float(from_bits(sy_bits)) if sy_bits & 0x7ff0000000000000 != 0x7ff0000000000000 else None
    trig_within = (sin_val is not None and cos_val is not None and sin_lo is not None and sin_hi is not None and cos_lo is not None and cos_hi is not None and sin_lo <= sin_val <= sin_hi and cos_lo <= cos_val <= cos_hi)
    sin_round = unique_round(sin_lo, sin_hi, m['sin_lo_raw'], m['sin_hi_raw'])
    cos_round = unique_round(cos_lo, cos_hi, m['cos_lo_raw'], m['cos_hi_raw'])
    x_round = unique_round(x_lo, x_hi, m['x_lo_raw'], m['x_hi_raw'])
    y_round = unique_round(y_lo, y_hi, m['y_lo_raw'], m['y_hi_raw'])
    results.append({
        'id': row['id'],
        'source_final_bits': {'x': bits_hex(sx_bits), 'y': bits_hex(sy_bits)},
        'trig_bits': {'sin': bits_hex(sin_b), 'cos': bits_hex(cos_b)},
        'trig_interval_contains_js': trig_within,
        'trig_unique_binary64': {'sin': sin_round is not None, 'cos': cos_round is not None},
        'trig_js_uniquely_rounded': {'sin': sin_round == sin_b if sin_round is not None else None, 'cos': cos_round == cos_b if cos_round is not None else None},
        'model_a_output_interval_contains_model_b': source_x is not None and source_y is not None and x_lo is not None and x_hi is not None and y_lo is not None and y_hi is not None and x_lo <= source_x <= x_hi and y_lo <= source_y <= y_hi,
        'output_cell_unique': {'x': x_round is not None, 'y': y_round is not None},
        'output_expected_bits_if_unique': {'x': bits_hex(x_round) if x_round is not None else None, 'y': bits_hex(y_round) if y_round is not None else None},
        'output_ulp_difference_if_unique': {'x': ulp_diff(sx_bits, x_round) if x_round is not None else None, 'y': ulp_diff(sy_bits, y_round) if y_round is not None else None},
        'mpfr_intervals': {k: {'binary_mantissa_exponent': m[k + '_raw'], 'parsed_exact_fraction': str(m[k]) if m[k] is not None else None} for k in ['sin_lo','sin_hi','cos_lo','cos_hi','x_lo','x_hi','y_lo','y_hi']},
    })
summary = {
    'vector_count': len(results),
    'trig_enclosure_containment_count': sum(r['trig_interval_contains_js'] for r in results),
    'trig_sin_unique_count': sum(r['trig_unique_binary64']['sin'] for r in results),
    'trig_cos_unique_count': sum(r['trig_unique_binary64']['cos'] for r in results),
    'trig_sin_unique_correct_count': sum(r['trig_js_uniquely_rounded']['sin'] is True for r in results),
    'trig_cos_unique_correct_count': sum(r['trig_js_uniquely_rounded']['cos'] is True for r in results),
    'model_a_model_b_containment_count': sum(r['model_a_output_interval_contains_model_b'] for r in results),
    'output_x_unique_count': sum(r['output_cell_unique']['x'] for r in results),
    'output_y_unique_count': sum(r['output_cell_unique']['y'] for r in results),
    'output_x_unique_match_count': sum(r['output_ulp_difference_if_unique']['x'] == 0 for r in results),
    'output_y_unique_match_count': sum(r['output_ulp_difference_if_unique']['y'] == 0 for r in results),
}
OUT.write_text(json.dumps({'method': 'MPFR 256-bit directed rounding; exact binary64 input bits; interval propagation', 'summary': summary, 'vectors': results}, indent=2, sort_keys=True) + '\n')
print(json.dumps(summary, indent=2))
