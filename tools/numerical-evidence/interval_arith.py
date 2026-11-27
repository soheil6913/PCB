"""Evidence-only MPFR interval arithmetic with exact serialization."""
from __future__ import annotations
import base64
from dataclasses import dataclass
import gmpy2

PRECISION = 256


def _ctx(rounding):
    c = gmpy2.get_context().copy()
    c.precision = PRECISION
    c.round = rounding
    c.emin = -10**9
    c.emax = 10**9
    return c


def _op(a, b, rounding, fn):
    with gmpy2.local_context(_ctx(rounding)):
        return fn(a, b)


def _unary(a, rounding, fn):
    with gmpy2.local_context(_ctx(rounding)):
        return fn(a)


def serialize(value) -> str:
    """Lossless MPFR serialization: MPFR's exact binary payload, base64 encoded."""
    return base64.b64encode(gmpy2.to_binary(value)).decode("ascii")


def deserialize(token: str):
    return gmpy2.from_binary(base64.b64decode(token.encode("ascii")))


def rational(value):
    q = gmpy2.mpq(value)
    return (int(q.numerator), int(q.denominator))


@dataclass(frozen=True)
class Interval:
    lo: object
    hi: object
    reason: str = ""

    def __post_init__(self):
        if self.lo > self.hi:
            raise ValueError("invalid interval: lower endpoint exceeds upper endpoint")

    def serialized(self):
        return {"lo": serialize(self.lo), "hi": serialize(self.hi), "reason": self.reason}

    @staticmethod
    def parse(payload):
        lo, hi = deserialize(payload["lo"]), deserialize(payload["hi"])
        if lo > hi:
            raise ValueError("serialized interval is inverted")
        return Interval(lo, hi, payload.get("reason", ""))


def add(a: Interval, b: Interval) -> Interval:
    return Interval(_op(a.lo, b.lo, gmpy2.RoundDown, lambda x,y:x+y),
                    _op(a.hi, b.hi, gmpy2.RoundUp, lambda x,y:x+y))


def sub(a: Interval, b: Interval) -> Interval:
    return Interval(_op(a.lo, b.hi, gmpy2.RoundDown, lambda x,y:x-y),
                    _op(a.hi, b.lo, gmpy2.RoundUp, lambda x,y:x-y))


def neg(a: Interval) -> Interval:
    return Interval(_unary(a.hi, gmpy2.RoundDown, lambda x:-x),
                    _unary(a.lo, gmpy2.RoundUp, lambda x:-x))


def mul(a: Interval, b: Interval) -> Interval:
    lows = [_op(x, y, gmpy2.RoundDown, lambda u,v:u*v) for x in (a.lo, a.hi) for y in (b.lo, b.hi)]
    highs = [_op(x, y, gmpy2.RoundUp, lambda u,v:u*v) for x in (a.lo, a.hi) for y in (b.lo, b.hi)]
    return Interval(min(lows), max(highs))


def exact(value):
    with gmpy2.local_context(_ctx(gmpy2.RoundToNearest)):
        v = gmpy2.mpfr(value)
    return Interval(v, v)


def roundtrip(interval: Interval) -> bool:
    parsed = Interval.parse(interval.serialized())
    return parsed.lo == interval.lo and parsed.hi == interval.hi
