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

def _adjacent(value: float, direction: float) -> float:
    return math.nextafter(value, direction)

def _midpoint(a: Fraction, b: Fraction) -> Fraction:
    return (a + b) / 2

def _cell_bounds(bits: str):
    value = bits_to_float(bits)
    if not math.isfinite(value):
        return None
    if value == 0.0:
        return None  # signed-zero is a sign/operation property, not a real cell
    q = float_to_fraction(value)
    predecessor = _adjacent(value, -math.inf)
    successor = _adjacent(value, math.inf)
    if math.isinf(successor):
        # RN-even overflow threshold: MAX + 2^970.
        step = Fraction(2) ** 970
        return _midpoint(float_to_fraction(predecessor), q), q + step
    if math.isinf(predecessor):
        step = Fraction(2) ** 970
        return q - step, _midpoint(q, float_to_fraction(successor))
    return _midpoint(float_to_fraction(predecessor), q), _midpoint(q, float_to_fraction(successor))

def classify_interval(candidate_bits: str, lower: Fraction, upper: Fraction) -> str:
    if lower > upper or not _finite_bits(candidate_bits):
        return INVALID
    value = bits_to_float(candidate_bits)
    if value == 0.0:
        return UNRESOLVED
    bounds = _cell_bounds(candidate_bits)
    if bounds is None:
        return UNRESOLVED
    lo, hi = bounds
    if lower <= lo or upper >= hi:
        return UNRESOLVED
    return UNIQUE

def classify_decimal_interval(candidate_bits: str, lower: str, upper: str) -> str:
    """Convenience adapter; production evidence must preserve exact fractions."""
    try:
        return classify_interval(candidate_bits, Fraction(lower), Fraction(upper))
    except (ValueError, ZeroDivisionError):
        return INVALID
