class MySolution():
    def __init__(self):
        pass

    def test_input(self, l, n):
        print(l, n)
        if type(l) != list:
            return 'errorType'
        if type(n) != int:
            return 'errorType'
        elif len(l) <= 1:
            return 'errorSize'
        elif not all(type(x) == int for x in l):
            return 'errorType'
        return True

    def ts(self, l, n):
        tst = MySolution.test_input(MySolution(), l, n)
        if tst == True:
            for i in range(len(l)):
                for j in range(i, len(l)):
                    if l[i] + l[j] == n and i != j:
                        return i, j
            return 'Подходящих пар чисел не найдено'
        elif tst == 'errorType':
            return 'Введенные данные некорректны'
        elif tst == 'errorSize':
            return 'Переданный массив имеет менее двух элементов'
