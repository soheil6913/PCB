#!/usr/bin/env python3
"""Evidence-only binary64 bit model.

Finite operations are checked by converting exact binary64 operands to Fractions,
performing exact rational arithmetic, and rounding to binary64 round-to-nearest,
ties-to-even. This module is not imported by production code.
"""
from __future__ import annotations
from fractions import Fraction
import math, struct

MASK64 = (1 << 64) - 1
SIGN = 1 << 63
EXP_MASK = 0x7ff0000000000000
FRAC_MASK = (1 << 52) - 1
BIAS = 1023


def bits(x: float) -> int:
    return struct.unpack('>Q', struct.pack('>d', x))[0]


def from_bits(b: int) -> float:
    return struct.unpack('>d', struct.pack('>Q', b & MASK64))[0]


def bits_hex(b: int) -> str:
    return f"0x{b & MASK64:016x}"


def classify_bits(b: int) -> str:
    e = (b & EXP_MASK) >> 52
    f = b & FRAC_MASK
    if e == 0x7ff:
        return 'nan' if f else ('-inf' if b & SIGN else '+inf')
    if e == 0 and f == 0:
        return '-zero' if b & SIGN else '+zero'
    if e == 0:
        return 'subnormal'
    return 'normal'


def fraction_from_bits(b: int) -> Fraction | None:
    b &= MASK64
    e = (b & EXP_MASK) >> 52
    f = b & FRAC_MASK
    sign = -1 if b & SIGN else 1
    if e == 0x7ff:
        return None
    if e == 0:
        significand, exponent = f, -1074
    else:
        significand, exponent = (1 << 52) | f, e - BIAS - 52
    if exponent >= 0:
        value = Fraction(significand << exponent, 1)
    else:
        value = Fraction(significand, 1 << -exponent)
    return sign * value


def round_even_ratio(n: int, d: int) -> int:
    assert n >= 0 and d > 0
    q, r = divmod(n, d)
    twice = r * 2
    if twice > d or (twice == d and (q & 1)):
        return q + 1
    return q


def round_fraction(value: Fraction, negative_zero: bool = False) -> int:
    if value == 0:
        return SIGN if negative_zero else 0
    signbit = SIGN if value < 0 else 0
    value = abs(value)
    n, d = value.numerator, value.denominator
    # Find floor(log2(value)) exactly.
    e = n.bit_length() - d.bit_length()
    if e >= 0:
        if Fraction(1 << e, 1) > value:
            e -= 1
    else:
        if Fraction(1, 1 << (-e)) > value:
            e -= 1
    if e > 1023:
        return signbit | EXP_MASK
    if e >= -1022:
        shift = 52 - e
        if shift >= 0:
            q = round_even_ratio(n << shift, d)
        else:
            q = round_even_ratio(n, d << (-shift))
        if q >= (1 << 53):
            q >>= 1
            e += 1
        if e > 1023:
            return signbit | EXP_MASK
        exponent = e + BIAS
        fraction = q - (1 << 52)
        return signbit | (exponent << 52) | (fraction & FRAC_MASK)
    # Subnormal grid is exactly 2^-1074.
    q = round_even_ratio(n << 1074, d)
    if q == 0:
        return signbit
    if q >= (1 << 52):
        return signbit | (1 << 52)  # smallest normal
    return signbit | q


def exact_binary_op(op: str, a_bits: int, b_bits: int) -> int | None:
    a = fraction_from_bits(a_bits)
    b = fraction_from_bits(b_bits)
    if a is None or b is None:
        return None
    if op == 'add':
        return round_fraction(a + b)
    if op == 'sub':
        return round_fraction(a - b)
    if op == 'mul':
        return round_fraction(a * b)
    if op == 'div':
        if b == 0:
            return None
        return round_fraction(a / b)
    raise ValueError(op)


def midpoint_tests() -> list[dict]:
    # Around 1.0, the halfway value is 1 + 2^-53.  1.0 has an even
    # significand; the next binary64 value has an odd significand.
    cases = [
        ('even-positive', Fraction(1) + Fraction(1, 1 << 53), 0x3ff0000000000000),
        ('odd-positive', Fraction(1) + Fraction(3, 1 << 53), 0x3ff0000000000002),
        ('even-negative', -(Fraction(1) + Fraction(1, 1 << 53)), 0xbff0000000000000),
        ('odd-negative', -(Fraction(1) + Fraction(3, 1 << 53)), 0xbff0000000000002),
    ]
    return [{'id': i, 'observed_bits': bits_hex(round_fraction(v)), 'expected_bits': bits_hex(e)} for i, v, e in cases]
