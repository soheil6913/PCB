"""MPFR-backed evidence-only sine/cosine interval evaluation."""
from __future__ import annotations
from fractions import Fraction
import gmpy2
from interval_arith import Interval, exact, _ctx, serialize


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


def _trig(value, fn):
    with gmpy2.local_context(_ctx(gmpy2.RoundDown)):
        lo = fn(value)
    with gmpy2.local_context(_ctx(gmpy2.RoundUp)):
        hi = fn(value)
    return Interval(lo, hi)


def point_intervals(bits: str):
    """Outward MPFR enclosures for sin/cos of one exact binary64 radian."""
    x = exact_mpfr(bits)
    return {"status": "ENCLOSED", "sin": _trig(x, gmpy2.sin), "cos": _trig(x, gmpy2.cos), "radian": exact(x)}


def serialized_point_intervals(bits: str):
    value = point_intervals(bits)
    return {"status": value["status"], "sin": value["sin"].serialized(), "cos": value["cos"].serialized(), "radian": value["radian"].serialized()}


def interval_from_bits(lo_bits: str, hi_bits: str):
    """Conservative all-angle API; broad intervals remain explicitly unresolved."""
    lo_decoded, hi_decoded = _bits_fraction(lo_bits), _bits_fraction(hi_bits)
    if lo_decoded is None or hi_decoded is None:
        return {"status": "INVALID", "reason": "non-finite endpoint"}
    lo, hi = exact_mpfr(lo_bits), exact_mpfr(hi_bits)
    if lo > hi:
        return {"status": "INVALID", "reason": "lo > hi"}
    if lo_bits == hi_bits:
        return serialized_point_intervals(lo_bits)
    with gmpy2.local_context(_ctx(gmpy2.RoundToNearest)):
        one, minus_one = gmpy2.mpfr(1), gmpy2.mpfr(-1)
    broad = Interval(minus_one, one, "global trigonometric bound; critical-point tightening unresolved")
    return {"status": "ENCLOSED", "sin": broad.serialized(), "cos": broad.serialized(), "reason": broad.reason}
