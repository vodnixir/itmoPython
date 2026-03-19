import timeit
import matplotlib.pyplot as plt


def fact_recursive(n: int) -> int:
    """
    Вычисляет факториал числа n рекурсивным способом.

    Args:
        n (int): неотрицательное целое число.

    Returns:
        int: факториал числа n (n!).
    """
    if n <= 1:
        return 1
    return n * fact_recursive(n - 1)


def fact_iterative(n: int) -> int:
    """
    Вычисляет факториал числа n итеративным способом (через цикл).

    Args:
        n (int): неотрицательное целое число.

    Returns:
        int: факториал числа n (n!).
    """
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def benchmark(func, numbers, repeats: int = 5):
    """
    Измеряет среднее время выполнения функции для набора входных данных.

    Args:
        func (callable): функция для тестирования.
        numbers (list[int]): список чисел, для которых проводится измерение.
        repeats (int): количество повторов для усреднения (по умолчанию 5).

    Returns:
        list[float]: список средних времен выполнения для каждого числа.
    """
    times = []
    for n in numbers:
        stmt = lambda: func(n)
        elapsed = timeit.timeit(stmt, number=repeats) / repeats
        times.append(elapsed)
    return times


def main():
    """
    Главная функция: выполняет сравнение двух реализаций факториала
    и строит график зависимости времени выполнения от входного числа.
    """
    test_numbers = list(range(1, 200, 10))
    recursive_times = benchmark(fact_recursive, test_numbers)
    iterative_times = benchmark(fact_iterative, test_numbers)
    plt.figure(figsize=(8, 5))
    plt.plot(test_numbers, recursive_times, label="Рекурсивный метод", marker="o")
    plt.plot(test_numbers, iterative_times, label="Итеративный метод", marker="s")
    plt.xlabel("n (входное число)")
    plt.ylabel("Время выполнения, сек")
    plt.title("Сравнение времени вычисления факториала")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
