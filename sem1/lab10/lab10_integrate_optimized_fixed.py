# -*- coding: utf-8 -*-
r"""
# Лабораторная работа 10 — оптимизация численного интегрирования

В этой тетрадке собран **итоговый** код по всем итерациям: базовая реализация, потоки, процессы, профилирование/микро-оптимизации и Cython (включая `nogil`/параллелизм).

> Примечание: блоки Cython требуют установленного `Cython` и компилятора (на macOS: Xcode Command Line Tools, на Windows: Build Tools).

## Утилиты: проверка корректности и бенчмарки

## Итерация 1 — базовая функция `integrate` (PEP 257 + аннотации)

Метод прямоугольников:
\[
\int_a^b f(x)\,dx \approx \sum_{i=0}^{n-1} f(a + i\cdot h)\cdot h,\quad h=\frac{b-a}{n}
\]

## Итерация 2 — потоки (ThreadPoolExecutor)

Идея: разбить интервал на части и посчитать их в потоках.  
Для CPU-bound задач на чистом Python ускорение обычно небольшое из-за GIL, но реализацию сделать нужно.

## Итерация 3 — процессы (ProcessPoolExecutor)

Процессы обходят ограничения GIL, поэтому для CPU-bound задач обычно дают заметное ускорение.

## Итерация 4 — профилирование и микро-оптимизации

- Профилируем базовую `integrate` (`cProfile`).
- Делаем ускоренную версию без изменения алгоритма.

## Итерация 5 — Cython (+ `nogil` и параллелизм)

Тетрадка:
1) пишет `integrate_cy.pyx`  
2) собирает расширение через `setup.py`  
3) импортирует модуль и делает его доступным для бенчмарка

Если сборка не удалась — секция пропускается.

## Сводные замеры времени

Бенчим:
- `integrate` (pure python)
- `integrate_fast`
- `integrate_threads` (4 потока)
- `integrate_processes` (4 процесса)
- (если собралось) `integrate_cy.integrate_cy`
- (если собралось) `integrate_cy.integrate_cy_nogil_parallel` (2/4/6 потоков)

⚠️ Для честного сравнения берём одинаковое `n_iter`.

## Короткие выводы (для отчёта)

- Потоки на чистом Python для CPU-bound вычислений обычно **не ускоряют** из-за GIL.
- Процессы дают ускорение, но есть накладные расходы (создание процессов, IPC).
- Микро-оптимизации могут дать заметный выигрыш без смены технологии.
- Cython с типизацией и отключением GIL + `prange` даёт **наилучшее ускорение** и масштабирование по потокам (если внутри цикла нет Python-объектов).
"""

import math
import os
import sys
import time
import platform
import statistics
import textwrap
from dataclasses import dataclass
from typing import Callable, List, Tuple
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import cProfile
import pstats
import io
import subprocess
from pathlib import Path
import importlib
import pandas as pd

def check_close(x: float, y: float, *, tol: float = 1e-3) -> None:
    """Проверяет, что x близко к y с заданной абсолютной погрешностью."""
    err = abs(x - y)
    print(f"value={x:.8f}, expected={y:.8f}, abs_err={err:.3e}")
    if err > tol:
        raise AssertionError(f"Too large error: {err} > {tol}")

@dataclass(frozen=True)
class BenchResult:
    name: str
    seconds: float
    repeats: int

def bench(fn: Callable[[], float], *, repeats: int = 5, warmup: int = 1) -> float:
    """Возвращает медианное время выполнения fn()."""
    for _ in range(warmup):
        fn()
    times: List[float] = []
    for _ in range(repeats):
        t0 = perf_counter()
        fn()
        t1 = perf_counter()
        times.append(t1 - t0)
    return statistics.median(times)

def integrate(f: Callable[[float], float], a: float, b: float, *, n_iter: int = 100_000) -> float:
    """Численно вычисляет определённый интеграл функции f на [a, b] методом прямоугольников.

    Параметры
    ---------
    f:
        Функция одной переменной.
    a:
        Нижний предел интегрирования.
    b:
        Верхний предел интегрирования.
    n_iter:
        Количество разбиений (итераций). Чем больше, тем точнее (обычно) и тем медленнее.

    Возвращает
    ----------
    float
        Приближённое значение интеграла.

    Исключения
    ----------
    ValueError
        Если n_iter <= 0.
    """
    if n_iter <= 0:
        raise ValueError("n_iter must be positive")
    if a == b:
        return 0.0

    acc = 0.0
    step = (b - a) / n_iter
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc

def _integrate_chunk(f: Callable[[float], float], a: float, b: float, n_iter: int) -> float:
    """Интеграл на подотрезке [a, b] методом прямоугольников."""
    acc = 0.0
    step = (b - a) / n_iter
    x = a
    for _ in range(n_iter):
        acc += f(x)
        x += step
    return acc * step

def integrate_threads(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    n_iter: int = 100_000,
    n_jobs: int = 4,
) -> float:
    """Интегрирование методом прямоугольников в несколько потоков."""
    if n_jobs <= 0:
        raise ValueError("n_jobs must be positive")
    if n_iter <= 0:
        raise ValueError("n_iter must be positive")

    base = n_iter // n_jobs
    rem = n_iter % n_jobs

    step_global = (b - a) / n_iter
    tasks = []
    start_i = 0
    for j in range(n_jobs):
        iters = base + (1 if j < rem else 0)
        end_i = start_i + iters
        aa = a + start_i * step_global
        bb = a + end_i * step_global
        tasks.append((aa, bb, iters))
        start_i = end_i

    def run_one(t):
        aa, bb, iters = t
        return _integrate_chunk(f, aa, bb, iters)

    with ThreadPoolExecutor(max_workers=n_jobs) as ex:
        return sum(ex.map(run_one, tasks))

def _integrate_chunk_proc(args: Tuple[Callable[[float], float], float, float, int]) -> float:
    f, a, b, n_iter = args
    return _integrate_chunk(f, a, b, n_iter)

def integrate_processes(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    n_iter: int = 100_000,
    n_proc: int = 4,
) -> float:
    """Интегрирование методом прямоугольников в несколько процессов."""
    if n_proc <= 0:
        raise ValueError("n_proc must be positive")
    if n_iter <= 0:
        raise ValueError("n_iter must be positive")

    base = n_iter // n_proc
    rem = n_iter % n_proc

    step_global = (b - a) / n_iter
    tasks: List[Tuple[Callable[[float], float], float, float, int]] = []

    start_i = 0
    for j in range(n_proc):
        iters = base + (1 if j < rem else 0)
        end_i = start_i + iters
        aa = a + start_i * step_global
        bb = a + end_i * step_global
        tasks.append((f, aa, bb, iters))
        start_i = end_i

    ctx = mp.get_context("spawn")  # переносимо
    with ProcessPoolExecutor(max_workers=n_proc, mp_context=ctx) as ex:
        return sum(ex.map(_integrate_chunk_proc, tasks))

def integrate_fast(f: Callable[[float], float], a: float, b: float, *, n_iter: int = 100_000) -> float:
    """Микро-оптимизированная версия integrate (без изменения алгоритма)."""
    if n_iter <= 0:
        raise ValueError("n_iter must be positive")
    if a == b:
        return 0.0

    step = (b - a) / n_iter
    x = a
    acc = 0.0
    ff = f
    for _ in range(n_iter):
        acc += ff(x)
        x += step
    return acc * step

def build_extension() -> None:
    cmd = [sys.executable, "setup.py", "build_ext", "--inplace"]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

def main() -> None:
    print("Python:", sys.version)

    print("Platform:", platform.platform())

    res = integrate(math.cos, 0.0, math.pi, n_iter=200_000)

    check_close(res, 0.0, tol=2e-4)

    res_t = integrate_threads(math.cos, 0.0, math.pi, n_iter=200_000, n_jobs=4)

    check_close(res_t, 0.0, tol=2e-4)

    res_p = integrate_processes(math.cos, 0.0, math.pi, n_iter=200_000, n_proc=4)

    check_close(res_p, 0.0, tol=2e-4)

    pr = cProfile.Profile()

    pr.enable()

    _ = integrate(math.cos, 0.0, math.pi, n_iter=300_000)

    pr.disable()

    s = io.StringIO()

    ps = pstats.Stats(pr, stream=s).sort_stats("tottime")

    ps.print_stats(12)

    print(s.getvalue())

    res_f = integrate_fast(math.cos, 0.0, math.pi, n_iter=200_000)

    check_close(res_f, 0.0, tol=2e-4)

    cy_code = r'''
    # cython: boundscheck=False
    # cython: wraparound=False
    # cython: nonecheck=False
    # cython: cdivision=True
    # cython: language_level=3
    
    from libc.math cimport cos
    from cython.parallel import prange
    cimport cython
    
    @cython.cfunc
    @cython.nogil
    cdef double _integrate_cos(double a, double b, long n_iter):
        cdef double step = (b - a) / n_iter
        cdef double x = a
        cdef double acc = 0.0
        cdef long i
        for i in range(n_iter):
            acc += cos(x)
            x += step
        return acc * step
    
    cpdef double integrate_cy(double a, double b, long n_iter=100000):
        # Типизированная Cython-версия для cos(x)
        if n_iter <= 0:
            raise ValueError("n_iter must be positive")
        return _integrate_cos(a, b, n_iter)
    
    cpdef double integrate_cy_nogil_parallel(double a, double b, long n_iter=100000, int n_threads=4):
        # Параллельная версия через prange + nogil для cos(x)
        if n_iter <= 0:
            raise ValueError("n_iter must be positive")
    
        cdef double step = (b - a) / n_iter
        cdef double acc = 0.0
        cdef long i
        for i in prange(n_iter, nogil=True, num_threads=n_threads, reduction="+acc", schedule="static"):
            acc += cos(a + i * step)
        return acc * step
    '''

    setup_py = textwrap.dedent(r'''
from setuptools import setup, Extension
from Cython.Build import cythonize

ext_modules = [
    Extension(
        name="integrate_cy",
        sources=["integrate_cy.pyx"],
    )
]

setup(
    name="integrate_cy",
    ext_modules=cythonize(ext_modules, language_level=3),
)
''')

    Path("integrate_cy.pyx").write_text(cy_code, encoding="utf-8")

    Path("setup.py").write_text(setup_py, encoding="utf-8")

    try:
        import Cython  # noqa: F401
        build_extension()
        integrate_cy_mod = importlib.import_module("integrate_cy")
        print("Cython module imported OK")
    except Exception as e:
        integrate_cy_mod = None
        print("Cython build/import skipped (error):", repr(e))

    N = 600_000

    A, B = 0.0, math.pi

    results: List[BenchResult] = []

    results.append(BenchResult("integrate (pure python)", bench(lambda: integrate(math.cos, A, B, n_iter=N)), 5))

    results.append(BenchResult("integrate_fast (pure python)", bench(lambda: integrate_fast(math.cos, A, B, n_iter=N)), 5))

    results.append(BenchResult("threads (4)", bench(lambda: integrate_threads(math.cos, A, B, n_iter=N, n_jobs=4)), 5))

    results.append(BenchResult("processes (4)", bench(lambda: integrate_processes(math.cos, A, B, n_iter=N, n_proc=4)), 5))

    if integrate_cy_mod is not None:
        results.append(BenchResult("cython cos (single)", bench(lambda: integrate_cy_mod.integrate_cy(A, B, N)), 5))
        for t in (2, 4, 6):
            results.append(BenchResult(f"cython prange nogil ({t} threads)", bench(lambda t=t: integrate_cy_mod.integrate_cy_nogil_parallel(A, B, N, t)), 5))

    df = pd.DataFrame([{"method": r.name, "seconds (median)": r.seconds} for r in results]).sort_values("seconds (median)")

    df.reset_index(drop=True, inplace=True)

    df


if __name__ == "__main__":
    main()