class GuessNumber:
    """Класс GuessNumber для поиска загаданного числа в заданном диапазоне или списке."""

    def __init__(self):
        """Инициализация экземпляра класса (пустая)."""
        pass

    def check_errors(self, num, arr, alg):
        """Проверяет корректность введённых данных.

        Args:
            num (int): Загаданное число.
            arr (list): Список или диапазон чисел для поиска.
            alg (str or None): Выбранный алгоритм поиска.

        Returns:
            True или str: True, если данные корректны,
            иначе строка с описанием ошибки.
        """
        if len(arr) < 2:
            return 'Неправильно задан интервал поиска'
        if type(num) != int or type(arr) != list or any(type(x) != int for x in arr):
            return 'Введенные данные некорректны'
        if min(arr) > num or max(arr) < num:
            return 'Неправильно введено число'
        if alg != 'straight' and alg is not None:
            return 'Неправильный тип алгоритма'
        return True

    def alg_straight_simple(self, num, arr, cnt):
        """Прямой поиск числа в диапазоне [arr[0], arr[1]].

        Args:
            num (int): Загаданное число.
            arr (list): Список из двух элементов [min, max].
            cnt (int): Счётчик попыток.

        Returns:
            tuple или str: (Найденное число, кол-во попыток)
            или сообщение об ошибке.
        """
        arr.sort()
        for i in range(arr[0], arr[1]):
            cnt += 1
            if num == i:
                return i, cnt
        return 'Результат не найден'

    def alg_straight_hard(self, num, arr, cnt):
        """Прямой поиск числа в неупорядоченном списке.

        Args:
            num (int): Загаданное число.
            arr (list): Список чисел.
            cnt (int): Счётчик попыток.

        Returns:
            tuple или str: (Найденное число, кол-во попыток)
            или сообщение об ошибке.
        """
        for i in arr:
            cnt += 1
            if num == i:
                return i, cnt
        return 'Результат не найден'

    def alg_bin_simple(self, num, arr, cnt):
        """Бинарный поиск числа в диапазоне [arr[0], arr[1]].

        Args:
            num (int): Загаданное число.
            arr (list): Список из двух элементов [min, max].
            cnt (int): Счётчик попыток.

        Returns:
            tuple или str: (Найденное число, кол-во попыток)
            или сообщение об ошибке.
        """
        arr.sort()
        cnt += 1
        if arr[0] > arr[1]:
            return 'Результат не найден', cnt

        mid = (arr[0] + arr[1]) // 2

        if mid == num:
            return mid, cnt
        elif mid > num:
            return self.alg_bin_simple(num, [arr[0], mid - 1], cnt)
        else:
            return self.alg_bin_simple(num, [mid + 1, arr[1]], cnt)

    def alg_bin_hard(self, num, arr, cnt):
        """Бинарный поиск для неупорядоченного списка.

        Args:
            num (int): Загаданное число.
            arr (list): Неупорядоченный список чисел.
            cnt (int): Счётчик попыток.

        Returns:
            tuple или str: (Найденное число, кол-во попыток)
            или сообщение об ошибке.
        """
        arr = sorted(arr)
        return self._bin_search(num, arr, 0, len(arr) - 1, cnt)

    def _bin_search(self, num, arr, left, right, cnt):
        """Рекурсивный бинарный поиск (вспомогательная функция).

        Args:
            num (int): Загаданное число.
            arr (list): Упорядоченный список чисел.
            left (int): Левая граница поиска.
            right (int): Правая граница поиска.
            cnt (int): Счётчик попыток.

        Returns:
            tuple или str: (Найденное число, кол-во попыток)
            или сообщение об ошибке.
        """
        cnt += 1
        if left > right:
            return 'Результат не найден'

        mid = (left + right) // 2

        if arr[mid] == num:
            return arr[mid], cnt
        elif arr[mid] > num:
            return self._bin_search(num, arr, left, mid - 1, cnt)
        else:
            return self._bin_search(num, arr, mid + 1, right, cnt)

    def guess(self, num, arr, alg=None):
        """Запускает поиск числа с указанным алгоритмом.

        Args:
            num (int): Загаданное число.
            arr (list): Список чисел или диапазон для поиска.
            alg (str or None): Выбор алгоритма: 'straight' или None (по умолчанию — бинарный поиск).

        Returns:
            tuple или str: (Найденное число, кол-во попыток)
            или сообщение об ошибке.
        """
        if alg is None:
            algSimp = self.alg_bin_simple
            algHard = self.alg_bin_hard
        elif alg == 'straight':
            algSimp = self.alg_straight_simple
            algHard = self.alg_straight_hard
        else:
            return 'Неправильный тип алгоритма'

        t = self.check_errors(num, arr, alg)
        if t != True:
            return t

        if len(arr) > 2:
            return algHard(num, arr, 0)
        else:
            return algSimp(num, arr, 0)


g = GuessNumber()

print(g.guess(4, [1, 4, 6, 8, 10], 'straight'))

print(type(g.alg_straight_simple))

print(g.guess(5, list(range(-1000, 1000, 3))))
print(g.guess(5, list(range(-1000, 1000))))
print(g.guess(3, [-5, -3, -1, 1, 3, 5, 7, 9]))
print(g.guess(4, [-5, -3, -1, 1, 3, 5, 7, 9]))

print(g.guess(4, [1, 10]))
print(g.guess(4, [1, 10], 'straight'))

print(g.guess(812, [-1000, 1000]))

# help(GuessNumber)

# print(GuessNumber.__doc__)
# print(GuessNumber.guess.__doc__)
