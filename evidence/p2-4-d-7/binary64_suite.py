#!/usr/bin/env python3
from __future__ import annotations
import json, math, operator, pathlib, struct, sys
from binary64 import *

OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('binary64-results.json')

SPECIAL = [
    0x0000000000000000, 0x8000000000000000,
    0x0000000000000001, 0x8000000000000001,
    0x000fffffffffffff, 0x800fffffffffffff,
    0x0010000000000000, 0x8010000000000000,
    0x3ff0000000000000, 0xbff0000000000000,
    0x4000000000000000, 0xc000000000000000,
    0x7fefffffffffffff, 0xffefffffffffffff,
    0x7ff0000000000000, 0xfff0000000000000,
    0x7ff8000000000001,
]


def native(op, a, b):
    af, bf = from_bits(a), from_bits(b)
    if op == 'add': return bits(af + bf)
    if op == 'sub': return bits(af - bf)
    if op == 'mul': return bits(af * bf)
    if op == 'div':
        if bf == 0.0:
            if math.isnan(af) or af == 0.0: return 0x7ff8000000000000
            sign = (a ^ b) & SIGN
            return sign | EXP_MASK
        return bits(af / bf)
    raise ValueError(op)

records = []
finite_pairs = [
    (0x3ff0000000000000, 0x3ff0000000000000),
    (0x3ff0000000000000, 0xbff0000000000000),
    (0x3ff0000000000001, 0x3ff0000000000000),
    (0x0010000000000000, 0x0000000000000001),
    (0x000fffffffffffff, 0x0000000000000001),
    (0x7fefffffffffffff, 0x7fefffffffffffff),
    (0x0000000000000001, 0x3ff0000000000000),
    (0x0010000000000000, 0x4000000000000000),
    (0x3ff0000000000000, 0x4000000000000000),
    (0x3ff0000000000000, 0x0000000000000001),
]
for op in ['add', 'sub', 'mul', 'div']:
    for i, (a, b) in enumerate(finite_pairs):
        expected = exact_binary_op(op, a, b)
        if expected is None: continue
        observed = native(op, a, b)
        records.append({
            'id': f'{op}-finite-{i}', 'operation': op,
            'a_bits': bits_hex(a), 'b_bits': bits_hex(b),
            'native_bits': bits_hex(observed), 'exact_bits': bits_hex(expected),
            'match': observed == expected,
            'a_class': classify_bits(a), 'b_class': classify_bits(b),
        })

# Explicit special propagation smoke vectors; no tolerance is used.
special_pairs = [
    ('add', 0x0000000000000000, 0x8000000000000000),
    ('sub', 0x0000000000000000, 0x0000000000000000),
    ('mul', 0x0000000000000000, 0x7ff0000000000000),
    ('div', 0x3ff0000000000000, 0x0000000000000000),
    ('div', 0xbff0000000000000, 0x0000000000000000),
    ('add', 0x7ff0000000000000, 0xfff0000000000000),
]
for i, (op, a, b) in enumerate(special_pairs):
    records.append({'id': f'{op}-special-{i}', 'operation': op,
                    'a_bits': bits_hex(a), 'b_bits': bits_hex(b),
                    'native_bits': bits_hex(native(op, a, b)),
                    'a_class': classify_bits(a), 'b_class': classify_bits(b)})

unary_records = []
for i, a in enumerate([0x0000000000000000, 0x8000000000000000, 0x0000000000000001, 0x8000000000000001, 0x3ff0000000000000, 0xbff0000000000000, 0x7ff0000000000000, 0x7ff8000000000001]):
    value = from_bits(a)
    unary_records.append({'id': f'neg-{i}', 'operation': 'unary-negation', 'input_bits': bits_hex(a), 'output_bits': bits_hex(bits(-value))})
    unary_records.append({'id': f'abs-{i}', 'operation': 'absolute-value', 'input_bits': bits_hex(a), 'output_bits': bits_hex(bits(abs(value)))})

comparison_records = []
for i, (a, b) in enumerate([(0x0000000000000000, 0x8000000000000000), (0x3ff0000000000000, 0x3ff0000000000001), (0xbff0000000000000, 0x3ff0000000000000), (0x7ff8000000000001, 0x3ff0000000000000)]):
    af, bf = from_bits(a), from_bits(b)
    comparison_records.append({'id': f'compare-{i}', 'a_bits': bits_hex(a), 'b_bits': bits_hex(b),
                               'lt': af < bf, 'eq': af == bf, 'gt': af > bf,
                               'unordered': math.isnan(af) or math.isnan(bf)})

result = {
    'contract': 'IEEE-754 binary64 round-to-nearest, ties-to-even',
    'finite_vectors': len([r for r in records if 'exact_bits' in r]),
    'finite_matches': sum(r.get('match', False) for r in records),
    'special_vectors': len([r for r in records if 'exact_bits' not in r]),
    'unary_vectors': len(unary_records),
    'comparison_vectors': len(comparison_records),
    'unary_records': unary_records,
    'comparison_records': comparison_records,
    'midpoint_tests': midpoint_tests(),
    'records': records,
}
OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({k: result[k] for k in ['finite_vectors','finite_matches','special_vectors','midpoint_tests']}, indent=2))
if result['finite_matches'] != result['finite_vectors']:
    raise SystemExit('finite exact verifier mismatch')
if any(x['observed_bits'] != x['expected_bits'] for x in result['midpoint_tests']):
    raise SystemExit('midpoint tie mismatch')
