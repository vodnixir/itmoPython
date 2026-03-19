import unittest
from python import twosum

s = twosum.MySolution()


class TestTS(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(s.ts([2, 7, 11, 15], 9), (0, 1))

    def test_none(self):
        self.assertEqual(s.ts([1, 2, 3], 7), 'Подходящих пар чисел не найдено')

    def test_one_elem(self):
        self.assertEqual(s.ts([5], 5), 'Переданный массив имеет менее двух элементов')

    def test_arr_not_none(self):
        self.assertEqual(s.ts([], 5), 'Переданный массив имеет менее двух элементов')

    def test_multi_same(self):
        self.assertEqual(s.ts([3, 3, 3], 6), (0, 1))

    def test_neg(self):
        self.assertEqual(s.ts([-1, -2, -3, -4, -5], -8), (2, 4))

    def test_type_n(self):
        self.assertEqual(s.ts([-1, -2, -3, -4, -5], 'a'), 'Введенные данные некорректны')

    def test_type_arr(self):
        self.assertEqual(s.ts('a', -8), 'Введенные данные некорректны')

    def test_type_arr_nums(self):
        self.assertEqual(s.ts(['a', -2, -3, -4, -5], -8), 'Введенные данные некорректны')

    def test_no_res(self):
        self.assertEqual(s.ts([3, 3, 3], 9), 'Подходящих пар чисел не найдено')

    def test_type_not_int(self):
        self.assertEqual(s.ts([2.131231,4.123123,5.123123,4,4], 8), 'Введенные данные некорректны')


if __name__ == '__main__':
    unittest.main()
