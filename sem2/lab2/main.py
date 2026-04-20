import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def create_vector() -> np.ndarray:
    """
    Создаёт одномерный массив чисел от 0 до 9.

    Returns:
        np.ndarray: Массив формы (10,).
    """
    return np.arange(10)


def create_matrix() -> np.ndarray:
    """
    Создаёт матрицу 5x5 со случайными числами от 0 до 1.

    Returns:
        np.ndarray: Матрица формы (5, 5).
    """
    return np.random.rand(5, 5)


def reshape_vector(vec: np.ndarray) -> np.ndarray:
    """
    Преобразует вектор формы (10,) в матрицу формы (2, 5).

    Args:
        vec: Входной одномерный массив.

    Returns:
        np.ndarray: Массив формы (2, 5).
    """
    return vec.reshape(2, 5)


def transpose_matrix(mat: np.ndarray) -> np.ndarray:
    """
    Транспонирует матрицу.

    Args:
        mat: Исходная матрица.

    Returns:
        np.ndarray: Транспонированная матрица.
    """
    return mat.T


def vector_add(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Выполняет поэлементное сложение двух векторов.

    Args:
        a: Первый вектор.
        b: Второй вектор.

    Returns:
        np.ndarray: Сумма векторов.
    """
    return a + b


def scalar_multiply(vec: np.ndarray, scalar: float | int) -> np.ndarray:
    """
    Умножает вектор на скаляр.

    Args:
        vec: Входной вектор.
        scalar: Число для умножения.

    Returns:
        np.ndarray: Результат умножения.
    """
    return vec * scalar


def elementwise_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Выполняет поэлементное умножение.

    Args:
        a: Первый массив.
        b: Второй массив.

    Returns:
        np.ndarray: Результат поэлементного умножения.
    """
    return a * b


def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    """
    Вычисляет скалярное произведение двух векторов.

    Args:
        a: Первый вектор.
        b: Второй вектор.

    Returns:
        float: Скалярное произведение.
    """
    return float(np.dot(a, b))


def matrix_multiply(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Выполняет умножение матриц.

    Args:
        a: Первая матрица.
        b: Вторая матрица.

    Returns:
        np.ndarray: Результат умножения матриц.
    """
    return a @ b


def matrix_determinant(a: np.ndarray) -> float:
    """
    Вычисляет определитель квадратной матрицы.

    Args:
        a: Квадратная матрица.

    Returns:
        float: Определитель матрицы.
    """
    return float(np.linalg.det(a))


def matrix_inverse(a: np.ndarray) -> np.ndarray:
    """
    Вычисляет обратную матрицу.

    Args:
        a: Квадратная невырожденная матрица.

    Returns:
        np.ndarray: Обратная матрица.
    """
    return np.linalg.inv(a)


def solve_linear_system(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Решает систему линейных уравнений Ax = b.

    Args:
        a: Матрица коэффициентов.
        b: Вектор свободных членов.

    Returns:
        np.ndarray: Вектор решения x.
    """
    return np.linalg.solve(a, b)


def load_dataset(path: str = "data/students_scores.csv") -> np.ndarray:
    """
    Загружает CSV-файл и возвращает данные как NumPy-массив.

    Args:
        path: Путь к CSV-файлу.

    Returns:
        np.ndarray: Загруженные данные.
    """
    return pd.read_csv(path).to_numpy()


def statistical_analysis(data: np.ndarray) -> dict[str, float]:
    """
    Вычисляет основные статистические показатели для массива.

    Args:
        data: Одномерный массив чисел.

    Returns:
        dict[str, float]: Словарь со статистиками.
    """
    return {
        "mean": float(np.mean(data)),
        "median": float(np.median(data)),
        "std": float(np.std(data)),
        "min": float(np.min(data)),
        "max": float(np.max(data)),
        "percentile_25": float(np.percentile(data, 25)),
        "percentile_75": float(np.percentile(data, 75)),
    }


def normalize_data(data: np.ndarray) -> np.ndarray:
    """
    Выполняет min-max нормализацию массива.

    Формула:
        (x - min) / (max - min)

    Args:
        data: Входной массив.

    Returns:
        np.ndarray: Нормализованный массив.
    """
    min_val = np.min(data)
    max_val = np.max(data)
    return (data - min_val) / (max_val - min_val)


def plot_histogram(data: np.ndarray) -> None:
    """
    Строит гистограмму и сохраняет её в папку plots.

    Args:
        data: Данные для построения гистограммы.
    """
    os.makedirs("plots", exist_ok=True)
    plt.figure()
    plt.hist(data, bins=10)
    plt.title("Histogram of Math Scores")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    plt.savefig("plots/histogram.png")
    plt.close()


def plot_heatmap(matrix: np.ndarray) -> None:
    """
    Строит тепловую карту и сохраняет её в папку plots.

    Args:
        matrix: Матрица для визуализации.
    """
    os.makedirs("plots", exist_ok=True)
    plt.figure()
    sns.heatmap(matrix, annot=True)
    plt.title("Correlation Heatmap")
    plt.savefig("plots/heatmap.png")
    plt.close()


def plot_line(x: np.ndarray, y: np.ndarray) -> None:
    """
    Строит линейный график и сохраняет его в папку plots.

    Args:
        x: Значения по оси X.
        y: Значения по оси Y.
    """
    os.makedirs("plots", exist_ok=True)
    plt.figure()
    plt.plot(x, y)
    plt.title("Student Math Scores")
    plt.xlabel("Student")
    plt.ylabel("Score")
    plt.savefig("plots/line_plot.png")
    plt.close()