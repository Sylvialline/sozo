import copy
from dataclasses import FrozenInstanceError
from decimal import Decimal, localcontext
from fractions import Fraction
from functools import partial
import math
import operator
import pickle
import random
import unittest

from utils import Qn, count_integers


class QuadraticTests(unittest.TestCase):
    def test_fixed_constructor_arithmetic_and_reflected_operations(self):
        Q3 = partial(Qn, 3)
        root = Q3(0, 1)
        self.assertEqual(root * root, 3)
        self.assertEqual((1 + root) * (1 - root), -2)
        self.assertEqual(1 / (2 + root), 2 - root)
        self.assertEqual((1 + root) / 2, Q3(Fraction(1, 2), Fraction(1, 2)))
        self.assertEqual(Fraction(1, 2) + root, Q3(Fraction(1, 2), 1))
        self.assertEqual(Fraction(1, 2) * root, root / 2)
        self.assertEqual(Fraction(1, 2) - root, Q3(Fraction(1, 2), -1))
        self.assertEqual(Fraction(1, 2) / root, Q3(0, Fraction(1, 6)))
        self.assertEqual(sum([root, 1, -root]), 1)

    def test_decimal_strings_remain_exact_and_objects_are_immutable(self):
        value = Qn(3, "0.1", "-2/3")
        self.assertEqual(value.a, Fraction(1, 10))
        self.assertEqual(value.b, Fraction(-2, 3))
        with self.assertRaises(FrozenInstanceError):
            value.a = 0
        self.assertEqual(copy.deepcopy(value), value)
        self.assertEqual(pickle.loads(pickle.dumps(value)), value)
        Q3 = pickle.loads(pickle.dumps(partial(Qn, 3)))
        self.assertEqual(Q3("0.1", "-2/3"), value)

    def test_comparisons_hash_and_rational_values_across_fields(self):
        root = Qn(3, 0, 1)
        self.assertTrue(1 < root < 2)
        self.assertTrue(root >= root)
        self.assertTrue(root <= root)
        self.assertFalse(root > root)
        self.assertEqual(abs(-root), root)
        self.assertFalse(Qn(2))
        self.assertTrue(root)
        self.assertTrue(Qn(3, -2).is_integer())
        self.assertFalse(Qn(3, Fraction(1, 2)).is_integer())
        self.assertFalse(root.is_integer())
        half2, half3 = Qn(2, Fraction(1, 2)), Qn(3, Fraction(1, 2))
        self.assertEqual(half2, half3)
        self.assertEqual(hash(half2), hash(Fraction(1, 2)))
        self.assertEqual(len({half2, half3, Fraction(1, 2)}), 1)
        self.assertEqual(half2 + root, root + Fraction(1, 2))
        self.assertEqual(root + half2, half2 + root)
        self.assertTrue(half2 < root)
        self.assertNotEqual(root, object())

    def test_arithmetic_identities_with_fractional_coefficients(self):
        rng = random.Random(23)
        for n in (2, 3, 5, 8, 12, 97):
            for _ in range(35):
                x, y = [Qn(n, Fraction(rng.randrange(-20, 21), rng.randrange(1, 20)),
                           Fraction(rng.randrange(-20, 21), rng.randrange(1, 20)))
                        for _ in range(2)]
                with self.subTest(n=n, x=x, y=y):
                    self.assertEqual((x + y) - y, x)
                    if y:
                        self.assertEqual((x / y) * y, x)
                    self.assertEqual(x * (y + 1), x * y + x)

    def test_floor_ceil_and_sign_against_high_precision_decimal(self):
        rng = random.Random(71)
        with localcontext() as context:
            context.prec = 100
            for n in (2, 3, 5, 8, 12, 97):
                for _ in range(70):
                    a, b = [Fraction(rng.randrange(-10000, 10001), rng.randrange(1, 1000))
                            for _ in range(2)]
                    value = Qn(n, a, b)
                    expected = (Decimal(a.numerator) / a.denominator
                                + Decimal(b.numerator) / b.denominator * Decimal(n).sqrt())
                    with self.subTest(value=value):
                        self.assertEqual(math.floor(value), math.floor(expected))
                        self.assertEqual(math.ceil(value), math.ceil(expected))
                        self.assertEqual(value.sign(), (expected > 0) - (expected < 0))

    def test_huge_numbers_and_near_integer_boundaries(self):
        huge = 10**180
        self.assertEqual(math.floor(Qn(3, huge, 1)), huge + 1)
        self.assertEqual(math.ceil(Qn(3, -huge, -1)), -huge - 1)
        for b in (Fraction(1, huge), Fraction(-1, huge)):
            value = Qn(2, 7, b)
            self.assertEqual(math.floor(value), 7 if b > 0 else 6)
            self.assertEqual(math.ceil(value), 8 if b > 0 else 7)
        # Pell solutions have p² - 2q² = ±1: test extremely close cancellation.
        p, q = 1, 1
        for _ in range(250):
            value = Qn(2, p, -q)
            positive = p * p - 2 * q * q > 0
            self.assertEqual(value.sign(), 1 if positive else -1)
            self.assertEqual(math.floor(value), 0 if positive else -1)
            self.assertEqual(math.ceil(value), 1 if positive else 0)
            p, q = p + 2 * q, p + q

    def test_invalid_fields_unsupported_mixing_and_zero_division(self):
        for n in (-3, 0, 1, 4, 9):
            with self.subTest(n=n), self.assertRaises(ValueError):
                Qn(n)
        for n in (True, 3.0, "3"):
            with self.subTest(n=n), self.assertRaises(TypeError):
                Qn(n)
        for coefficients in ((0.1, 0), (0, 0.1)):
            with self.assertRaises(TypeError):
                Qn(3, *coefficients)
        for operation in (operator.add, operator.sub, operator.mul, operator.truediv,
                          operator.eq, operator.lt):
            with self.subTest(operation=operation), self.assertRaises(TypeError):
                operation(Qn(2, 0, 1), Qn(8, 0, 1))
        with self.assertRaises(TypeError):
            Qn(3, 0, 1) + 0.5
        with self.assertRaises(ZeroDivisionError):
            Qn(3, 1, 2) / 0
        with self.assertRaises(ZeroDivisionError):
            1 / Qn(2)


class IntegerIntervalTests(unittest.TestCase):
    def test_all_endpoint_modes_against_enumeration(self):
        endpoints = [Fraction(i, 2) for i in range(-6, 7)]
        for lo in endpoints:
            for hi in endpoints:
                for left_closed in (False, True):
                    for right_closed in (False, True):
                        expected = sum(
                            (x >= lo if left_closed else x > lo)
                            and (x <= hi if right_closed else x < hi)
                            for x in range(-4, 5)
                        )
                        self.assertEqual(count_integers(lo, hi, left_closed=left_closed,
                                                       right_closed=right_closed), expected)

    def test_quadratic_and_large_integer_endpoints(self):
        root = Qn(3, 0, 1)
        self.assertEqual(count_integers(-root, root), 3)
        self.assertEqual(count_integers(-root, root, left_closed=False, right_closed=False), 3)
        self.assertEqual(count_integers(Qn(3, 1), root, left_closed=False), 0)
        self.assertEqual(count_integers(root, -root), 0)
        huge = 10**180
        self.assertEqual(count_integers(huge, huge + 2), 3)
        self.assertEqual(count_integers(-1.5, 2.5), 4)


if __name__ == "__main__":
    unittest.main()
