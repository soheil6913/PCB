#!/usr/bin/env python3
from __future__ import annotations
import sys
import gmpy2
from binary64 import fraction_from_bits


def exact_mpfr(bits: int):
    f = fraction_from_bits(bits)
    if f is None:
        if bits & 0x7ff0000000000000 == 0x7ff0000000000000 and bits & ((1 << 52) - 1) == 0:
            return gmpy2.mpfr('-inf' if bits >> 63 else 'inf')
        return gmpy2.mpfr('nan')
    return gmpy2.mpfr(gmpy2.mpq(f.numerator, f.denominator))


def repr_mp(x):
    if gmpy2.is_nan(x): return '@NaN@'
    if gmpy2.is_infinite(x): return '@-Inf@' if x < 0 else '@+Inf@'
    mant, exp, _ = x.digits(2, 0)
    sign = '-' if mant.startswith('-') else '+'
    if mant.startswith('-'): mant = mant[1:]
    return f'{sign}0.{mant}e{exp}'


def mul_scalar_interval(scalar, lo, hi, ctx):
    ctx.round = gmpy2.RoundDown
    a_lo, b_lo = scalar * lo, scalar * hi
    lower = min(a_lo, b_lo)
    ctx.round = gmpy2.RoundUp
    a_hi, b_hi = scalar * lo, scalar * hi
    upper = max(a_hi, b_hi)
    return lower, upper


def add_interval(a_lo, a_hi, b_lo, b_hi, ctx):
    ctx.round = gmpy2.RoundDown; lo = a_lo + b_lo
    ctx.round = gmpy2.RoundUp; hi = a_hi + b_hi
    return lo, hi


def sub_interval(a_lo, a_hi, b_lo, b_hi, ctx):
    ctx.round = gmpy2.RoundDown; lo = a_lo - b_hi
    ctx.round = gmpy2.RoundUp; hi = a_hi - b_lo
    return lo, hi

ctx = gmpy2.get_context(); ctx.precision = 256
for line in sys.stdin:
    fields = line.split()
    if not fields: continue
    ident, rb, xb, yb, obx, oby = fields
    r, x, y, ox, oy = [exact_mpfr(int(v, 16)) for v in [rb, xb, yb, obx, oby]]
    with gmpy2.local_context(ctx) as c:
        c.precision = 256
        c.round = gmpy2.RoundDown; slo = gmpy2.sin(r); clo = gmpy2.cos(r)
        c.round = gmpy2.RoundUp; shi = gmpy2.sin(r); chi = gmpy2.cos(r)
        xcos = mul_scalar_interval(x, clo, chi, c)
        ysin = mul_scalar_interval(y, slo, shi, c)
        rx = add_interval(*sub_interval(*xcos, *ysin, c), ox, ox, c)
        xsin = mul_scalar_interval(x, slo, shi, c)
        ycos = mul_scalar_interval(y, clo, chi, c)
        ry = add_interval(*add_interval(*xsin, *ycos, c), oy, oy, c)
    print(ident,
          'sin_lo='+repr_mp(slo), 'sin_hi='+repr_mp(shi),
          'cos_lo='+repr_mp(clo), 'cos_hi='+repr_mp(chi),
          'x_lo='+repr_mp(rx[0]), 'x_hi='+repr_mp(rx[1]),
          'y_lo='+repr_mp(ry[0]), 'y_hi='+repr_mp(ry[1]))
