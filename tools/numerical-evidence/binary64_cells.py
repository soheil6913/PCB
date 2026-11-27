"""Exact-rational binary64 output-cell classifier for evidence only."""
from __future__ import annotations
from fractions import Fraction
import math
import struct

UNIQUE = "UNIQUE"
UNRESOLVED = "UNRESOLVED"
INVALID = "INVALID"


def bits_to_float(bits: str) -> float:
    return struct.unpack(">d", int(bits, 16).to_bytes(8, "big"))[0]


def float_to_fraction(value: float) -> Fraction:
    return Fraction(*value.as_integer_ratio())


def _finite_bits(bits: str) -> bool:
    return ((int(bits, 16) >> 52) & 0x7ff) != 0x7ff


def _midpoint(a: Fraction, b: Fraction) -> Fraction:
    return (a + b) / 2


def cell_bounds(bits: str):
    """Return exact open-cell boundaries, or None for signed zero/non-finite."""
    value = bits_to_float(bits)
    if not math.isfinite(value) or value == 0.0:
        return None
    q = float_to_fraction(value)
    predecessor = math.nextafter(value, -math.inf)
    successor = math.nextafter(value, math.inf)
    if math.isinf(successor):
        # Round-to-nearest overflow threshold: MAX_FINITE + 2^970.
        return _midpoint(float_to_fraction(predecessor), q), q + Fraction(2) ** 970
    if math.isinf(predecessor):
        return q - Fraction(2) ** 970, _midpoint(q, float_to_fraction(successor))
    return _midpoint(float_to_fraction(predecessor), q), _midpoint(q, float_to_fraction(successor))


def classify_interval(candidate_bits: str, lower: Fraction, upper: Fraction) -> str:
    if lower > upper or not _finite_bits(candidate_bits):
        return INVALID
    if bits_to_float(candidate_bits) == 0.0:
        return UNRESOLVED
    bounds = cell_bounds(candidate_bits)
    if bounds is None:
        return UNRESOLVED
    lo, hi = bounds
    if lower <= lo or upper >= hi:
        return UNRESOLVED
    return UNIQUE


def classify_with_reason(candidate_bits: str, lower: Fraction, upper: Fraction):
    if lower > upper:
        return INVALID, "interval lower endpoint exceeds upper endpoint"
    if not _finite_bits(candidate_bits):
        return INVALID, "candidate output is non-finite"
    if bits_to_float(candidate_bits) == 0.0:
        return UNRESOLVED, "signed-zero cell requires operation-sign evidence"
    bounds = cell_bounds(candidate_bits)
    if bounds is None:
        return UNRESOLVED, "candidate has no ordinary finite cell"
    lo, hi = bounds
    if lower <= lo or upper >= hi:
        return UNRESOLVED, "interval touches or crosses a binary64 midpoint/overflow boundary"
    return UNIQUE, "interval lies strictly inside candidate binary64 cell"


def classify_decimal_interval(candidate_bits: str, lower: str, upper: str) -> str:
    try:
        return classify_interval(candidate_bits, Fraction(lower), Fraction(upper))
    except (ValueError, ZeroDivisionError):
        return INVALID
