import unittest

def add(x, y):
    return x + y
    

class TestMathOperations(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)

if __name__ == '__main__':
    print("add(2, 3) =", add(2, 3))
    unittest.main()
    
'''
Unit testing validates that individual program functions work as intended by automatically checking 
their outputs against expected results for given inputs. This method helps catch bugs early, 
simplifies debugging, and makes code easier to maintain and refactor, with Python's built-in unittest 
module providing a structured framework for writing and running these focused tests.
'''