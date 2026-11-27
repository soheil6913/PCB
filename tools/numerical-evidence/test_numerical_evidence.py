import math
import unittest
from fractions import Fraction
import gmpy2

from interval_arith import Interval, add, sub, mul, neg, exact, roundtrip
from binary64_cells import classify_interval, classify_with_reason, UNIQUE, UNRESOLVED, INVALID


class IntervalArithmeticTests(unittest.TestCase):
    def test_serialization_roundtrip_signed_and_subnormal(self):
        for text in ("0", "-0.0", "5e-324", "-5e-324", "0.9999999999999999", "-1"):
            interval = exact(gmpy2.mpfr(text, 256))
            self.assertTrue(roundtrip(interval))

    def test_sign_combinations(self):
        p = Interval(exact(2).lo, exact(3).hi)
        n = Interval(exact(-4).lo, exact(-1).hi)
        cross = Interval(exact(-1).lo, exact(2).hi)
        self.assertLessEqual(mul(p, p).lo, gmpy2.mpfr(4))
        self.assertLessEqual(mul(p, n).lo, gmpy2.mpfr(-3))
        self.assertGreaterEqual(mul(n, n).hi, gmpy2.mpfr(1))
        self.assertLessEqual(mul(cross, p).lo, gmpy2.mpfr(-3))
        self.assertGreaterEqual(mul(cross, p).hi, gmpy2.mpfr(6))

    def test_add_sub_negation_and_cancellation(self):
        a = Interval(exact(1).lo, exact(1).hi)
        b = Interval(exact(-1).lo, exact(-1).hi)
        self.assertEqual(add(a, b).lo, 0)
        self.assertEqual(sub(a, a).hi, 0)
        self.assertEqual(neg(a).lo, -1)


class Binary64CellTests(unittest.TestCase):
    def bits(self, value):
        import struct
        return "0x" + struct.pack(">d", value).hex()

    def test_unique_and_midpoints(self):
        candidate = self.bits(1.0)
        q = Fraction.from_float(1.0)
        lo = (Fraction.from_float(math.nextafter(1.0, -math.inf)) + q) / 2
        hi = (q + Fraction.from_float(math.nextafter(1.0, math.inf))) / 2
        self.assertEqual(classify_interval(candidate, q, q), UNIQUE)
        self.assertEqual(classify_interval(candidate, lo, lo), UNRESOLVED)
        self.assertEqual(classify_interval(candidate, hi, hi), UNRESOLVED)

    def test_subnormal_normal_zero_and_invalid(self):
        self.assertEqual(classify_interval(self.bits(5e-324), Fraction.from_float(5e-324), Fraction.from_float(5e-324)), UNIQUE)
        self.assertEqual(classify_interval(self.bits(0.0), Fraction(0), Fraction(0)), UNRESOLVED)
        self.assertEqual(classify_interval("0x7ff0000000000000", Fraction(0), Fraction(0)), INVALID)

    def test_reason_is_recorded(self):
        status, reason = classify_with_reason(self.bits(1.0), Fraction.from_float(1.0), Fraction.from_float(1.0))
        self.assertEqual(status, UNIQUE)
        self.assertIn("strictly inside", reason)

    def test_negative_maximum_cell_is_conservative(self):
        value = -float.fromhex("0x1.fffffffffffffp+1023")
        candidate = self.bits(value)
        q = Fraction.from_float(value)
        self.assertEqual(classify_interval(candidate, q, q), UNIQUE)


class HarnessIntegrityTests(unittest.TestCase):
    def test_runner_invokes_classifier_not_placeholder(self):
        from pathlib import Path
        source = (Path(__file__).with_name("run_vectors.py")).read_text()
        self.assertIn("classify_with_reason", source)
        self.assertNotIn('output_cell="UNRESOLVED"', source)


if __name__ == "__main__":
    unittest.main()
