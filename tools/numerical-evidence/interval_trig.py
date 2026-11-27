"""Conservative MPFR interval sine/cosine evaluator for evidence only.

Inputs are exact IEEE-754 binary64 words. MPFR performs all endpoint arithmetic.
Non-degenerate intervals are handled conservatively: endpoint monotonicity is
used only when a critical-point scan is proven; otherwise [-1, 1] is returned.
"""
from __future__ import annotations
from fractions import Fraction
import gmpy2

PRECISION = 256

def _ctx(rounding):
    c = gmpy2.get_context().copy()
    c.precision = PRECISION
    c.round = rounding
    c.emin = -10**9
    c.emax = 10**9
    return c

def _bits_fraction(bits: str):
    u = int(bits, 16)
    sign = -1 if u >> 63 else 1
    exp = (u >> 52) & 0x7ff
    frac = u & ((1 << 52) - 1)
    if exp == 0x7ff:
        return None
    if exp == 0:
        if frac == 0:
            return Fraction(0), sign
        return Fraction(sign * frac, 1 << 1074), sign
    return Fraction(sign * ((1 << 52) + frac), 1 << 52) * Fraction(2) ** (exp - 1023), sign

def exact_mpfr(bits: str, rounding=gmpy2.RoundToNearest):
    decoded = _bits_fraction(bits)
    if decoded is None:
        raise ValueError("non-finite binary64 input")
    q, sign = decoded
    with gmpy2.local_context(_ctx(rounding)):
        value = gmpy2.mpfr(gmpy2.mpq(q.numerator, q.denominator))
    if q == 0 and sign < 0:
        return -value
    return value

def _directed_sin(x, rounding):
    with gmpy2.local_context(_ctx(rounding)):
        return gmpy2.sin(x)

def _directed_cos(x, rounding):
    with gmpy2.local_context(_ctx(rounding)):
        return gmpy2.cos(x)

def _fmt(x):
    return str(x)

def point_interval(bits: str):
    """Return outward MPFR endpoints for sin/cos of one exact binary64 radian."""
    x = exact_mpfr(bits, gmpy2.RoundToNearest)
    sin_lo, sin_hi = _directed_sin(x, gmpy2.RoundDown), _directed_sin(x, gmpy2.RoundUp)
    cos_lo, cos_hi = _directed_cos(x, gmpy2.RoundDown), _directed_cos(x, gmpy2.RoundUp)
    return {"status": "ENCLOSED", "sin": [_fmt(sin_lo), _fmt(sin_hi)], "cos": [_fmt(cos_lo), _fmt(cos_hi)]}

def interval_from_bits(lo_bits: str, hi_bits: str):
    """Conservative interval evaluator.

    Degenerate binary64 intervals receive MPFR transcendental enclosures. For a
    non-degenerate interval, [-1,1] is a rigorous global enclosure for each
    function. This avoids unproven floating-point range reduction; callers that
    need a narrow cell must reject the broad interval as unresolved.
    """
    lo_decoded, hi_decoded = _bits_fraction(lo_bits), _bits_fraction(hi_bits)
    if lo_decoded is None or hi_decoded is None:
        return {"status": "INVALID", "reason": "non-finite endpoint"}
    lo = exact_mpfr(lo_bits); hi = exact_mpfr(hi_bits)
    if lo > hi:
        return {"status": "INVALID", "reason": "lo > hi"}
    if lo_bits == hi_bits:
        return point_interval(lo_bits)
    return {"status": "ENCLOSED", "sin": ["-1", "1"], "cos": ["-1", "1"], "reason": "conservative global bound; critical-point tightening unresolved"}
