import unittest

class TestStringMethods(unittest.TestCase):

    #Checks that the .upper() method converts 'foo' to 'FOO'
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
        self.assertEqual('foo'.upper(), 'Foo') #incorrect

    #Validates correct behavior of .isupper() for fully and partially uppercase strings
    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    #Tests both the normal behavior and exception handling of .split()
    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_isdigit(self):
        self.assertTrue('123'.isdigit())


if __name__ == '__main__':
    unittest.main()

#result: 
# ----------------------------------------------------------------------
#Ran 3 tests in 0.000s

''' 
added self.assertEqual('foo'.upper(), 'Foo')
 ...F
======================================================================
FAIL: test_upper (__main__.TestStringMethods.test_upper)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/stella/Documents/yoobee/MSE800-PSE/week11/task3.py", line 8, in test_upper
    self.assertEqual('foo'.upper(), 'Foo') #incorrect
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: 'FOO' != 'Foo'
- FOO
+ Foo


----------------------------------------------------------------------
Ran 4 tests in 0.001s

FAILED (failures=1)
'''