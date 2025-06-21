import unittest
import math

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    return a ** b

def root(a, n):
    if a < 0 and n % 2 == 0:
        raise ValueError("Cannot take even root of negative number")
    return a ** (1/n)

def sine(x):
    return math.sin(x)

def cosine(x):
    return math.cos(x)

def tangent(x):
    return math.tan(x)

class TestMathOperations(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 34), 36)
        self.assertEqual(add(-2, -5), -7)

    def test_subtract(self):
        self.assertEqual(subtract(10, 4), 6)
        self.assertEqual(subtract(-2, -3), 1)

    def test_multiply(self):
        self.assertEqual(multiply(3, 4), 12)
        self.assertEqual(multiply(0, 5), 0)

    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)
        with self.assertRaises(ValueError):
            divide(5, 0)

    def test_power(self):
        self.assertEqual(power(2, 3), 8)
        self.assertEqual(power(4, 0.5), 2)

    def test_root(self):
        self.assertEqual(root(9, 2), 3)
        self.assertAlmostEqual(root(27, 3), 3)
        with self.assertRaises(ValueError):
            root(-16, 2)

    def test_sine(self):
        self.assertAlmostEqual(sine(math.pi/2), 1.0)
        self.assertAlmostEqual(sine(0), 0.0)

    def test_cosine(self):
        self.assertAlmostEqual(cosine(math.pi), -1.0)
        self.assertAlmostEqual(cosine(0), 1.0)

    def test_tangent(self):
        self.assertAlmostEqual(tangent(0), 0.0)
        self.assertAlmostEqual(tangent(math.pi/4), 1.0)

if __name__ == '__main__':
    unittest.main()
    
        
        