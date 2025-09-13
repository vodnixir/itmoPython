import unittest
from python import twosumfunc

class TestTS(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(twosumfunc.ts([2, 7, 11, 15], 9), (0, 1))

    def test_none(self):
        self.assertIsNone(twosumfunc.ts([1, 2, 3], 7))

    def test_one_elem(self):
        self.assertIsNone(twosumfunc.ts([5], 5))

    def test_multi_same(self):
        self.assertEqual(twosumfunc.ts([3, 3, 3], 6), (0, 1))

    def test_neg(self):
        self.assertEqual(twosumfunc.ts([-1, -2, -3, -4, -5], -8), (2, 4))



if __name__ == '__main__':
    unittest.main()
