import unittest
from guessnum import GuessNumber

s = GuessNumber()


class TestTS(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(s.guess(4, [1, 10]), (4, 4))

    def test_none(self):
        self.assertEqual(s.guess(20, [1, 10]), 'Неправильно введено число')

    def test_one_elem(self):
        self.assertEqual(s.guess(5, [5]), 'Неправильно задан интервал поиска')

    def test_arr_not_none(self):
        self.assertEqual(s.guess(2, []), 'Неправильно задан интервал поиска')

    def test_multi_arr(self):
        self.assertEqual(s.guess(3, [3, 3, 3]), (3, 1))

    def test_neg(self):
        self.assertEqual(s.guess(-4, [-10, -1]), (-4, 4))

    def test_type_n(self):
        self.assertEqual(s.guess(3, [1, 'a']), 'Введенные данные некорректны')

    def test_type_arr(self):
        self.assertEqual(s.guess('a', [2, 4]), 'Введенные данные некорректны')

    def test_type_arr_nums(self):
        self.assertEqual(s.guess(4, ['a', -5]), 'Введенные данные некорректны')

    def test_arr_reversed(self):
        self.assertEqual(s.guess(3, [-5, -3, -1, 1, 3, 5, 7, 9]), (3, 3))

    def test_no_res(self):
        self.assertEqual(s.guess(4, [-5, -3, -1, 1, 3, 5, 7, 9]), 'Результат не найден')

    def test_bad_number(self):
        self.assertEqual(s.guess(9, [3, 3]), 'Неправильно введено число')

    def test_type_not_int(self):
        self.assertEqual(s.guess(8, [2.131231, 4]), 'Введенные данные некорректны')

    def test_type_not_int_hard(self):
        self.assertEqual(s.guess(8, [2.131231, 6, 4]), 'Введенные данные некорректны')

    def test_type_of_alg_bin(self):
        self.assertEqual(s.guess(4, [1, 10], alg='straight'), (4, 4))

    def test_type_of_alg_straight(self):
        self.assertEqual(s.guess(4, [1, 10], None), (4, 4))

    def test_type_of_alg_wrong(self):
        self.assertEqual(s.guess(4, [1, 10], 123), 'Неправильный тип алгоритма')


if __name__ == '__main__':
    unittest.main()
