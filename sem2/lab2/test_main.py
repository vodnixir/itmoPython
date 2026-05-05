import numpy as np
from main import (
    create_vector,
    reshape_vector,
    vector_add,
    scalar_multiply,
    elementwise_multiply,
    dot_product,
    matrix_multiply,
    normalize_data,
)


def test_create_vector() -> None:
    result = create_vector()
    expected = np.arange(10)
    assert np.array_equal(result, expected)


def test_reshape_vector() -> None:
    vec = np.arange(10)
    result = reshape_vector(vec)
    assert result.shape == (2, 5)


def test_vector_add() -> None:
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = vector_add(a, b)
    expected = np.array([5, 7, 9])
    assert np.array_equal(result, expected)


def test_scalar_multiply() -> None:
    vec = np.array([1, 2, 3])
    result = scalar_multiply(vec, 2)
    expected = np.array([2, 4, 6])
    assert np.array_equal(result, expected)


def test_elementwise_multiply() -> None:
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = elementwise_multiply(a, b)
    expected = np.array([4, 10, 18])
    assert np.array_equal(result, expected)


def test_dot_product() -> None:
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = dot_product(a, b)
    assert result == 32.0


def test_matrix_multiply() -> None:
    a = np.array([[1, 2], [3, 4]])
    b = np.array([[2, 0], [1, 2]])
    result = matrix_multiply(a, b)
    expected = np.array([[4, 4], [10, 8]])
    assert np.array_equal(result, expected)


def test_normalize_data() -> None:
    data = np.array([0, 5, 10])
    result = normalize_data(data)
    expected = np.array([0.0, 0.5, 1.0])
    assert np.allclose(result, expected)