import unittest
from binaryTreeBetter import bintree

b = bintree.BinTree()


class TestBinTree(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(b.test(3, 2))

    def test_height_type(self):
        with self.assertRaises(TypeError):
            b.test("3", 2)

    def test_height_value(self):
        with self.assertRaises(ValueError):
            b.test(0, 2)

    def test_root_type(self):
        with self.assertRaises(TypeError):
            b.test(3, "abc")

    def test_parser_flag_type(self):
        with self.assertRaises(TypeError):
            b.test(3, 2, use_parser1="yes")

    def test_large_tree(self):
        with self.assertRaises(ValueError):
            b.test(50, 1, max_nodes=1000)

    def test_gen_parser2(self):
        self.assertIsNone(b.gen_bin_tree(3, 2))

    def test_gen_parser1(self):
        self.assertIsNone(b.gen_bin_tree(3, 2, use_parser1=True))


if __name__ == '__main__':
    unittest.main()
