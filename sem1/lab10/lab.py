
"""Лабораторная работа 10 — ускорение численного интегрирования.

Единый .py скрипт вместо Jupyter-ноутбука.

Содержит:
  Итерация 1: integrate() + PEP257 docstring, type hints, doctest, unittest, timeit
  Итерация 2: Threads (ThreadPoolExecutor) + бенчмарки
  Итерация 3: Processes (ProcessPoolExecutor) + бенчмарки (устойчиво для macOS/Jupyter: не передаём callable)
  Итерация 4: Cython (опционально, если установлен) — сборка модуля из .pyx на лету
  Итерация 5: Cython + noGIL/prange (опционально; требует OpenMP)

Запуск:
  python3 lab.py --bench
  python3 lab.py --doctest
  python3 lab.py --unittest
  python3 lab.py --all

Примечания:
- Threads в чистом Python обычно не ускоряют CPU-bound код из-за GIL.
- Processes дают ускорение, но имеют накладные расходы и ограничения сериализации (pickle).
- Для Processes мы используем func_id (строка), а не передачу f, чтобы избежать BrokenProcessPool в ноутбуках/macOS.
"""

from __future__ import annotations

import argparse
import doctest
import math
import os
import sys
import timeit
import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple


# ---------------------------
# Итерация 1: базовая интеграция
# ---------------------------

def integrate(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    n_iter: int = 100_000
) -> float:
    """Numerically integrate a single-variable function on [a, b] using
    the left Riemann sum (rectangle method).

    The interval [a, b] is split into `n_iter` equal sub-intervals.
    The function is sampled at the left edge of each sub-interval.

    Parameters
    ----------
    f:
        Function f(x) -> float to integrate.
    a:
        Left integration bound.
    b:
        Right integration bound.
    n_iter:
        Number of rectangles (iterations). Must be a positive integer.

    Returns
    -------
    float
        Approximation of the definite integral ∫[a,b] f(x) dx.

    Examples
    --------
    Trigonometric example:
    >>> import math
    >>> round(integrate(math.cos, 0.0, math.pi, n_iter=200000), 6)
    0.0

    Quadratic polynomial example:
    >>> f = lambda x: x*x + 2*x + 1  # (x+1)^2
    >>> round(integrate(f, 0.0, 1.0, n_iter=200000), 6)
    2.333333
    """
    if not isinstance(n_iter, int):
        raise TypeError("n_iter must be int")
    if n_iter <= 0:
        raise ValueError("n_iter must be > 0")

    step = (b - a) / n_iter
    acc = 0.0
    x = a
    for _ in range(n_iter):
        acc += f(x) * step
        x += step
    return acc


# ---------------------------
# Итерация 2: Threads
# ---------------------------

def _integrate_chunk_py(f: Callable[[float], float], a: float, b: float, n_iter: int) -> float:
    """Helper: integrate a chunk in pure Python (left rectangles)."""
    step = (b - a) / n_iter
    acc = 0.0
    x = a
    for _ in range(n_iter):
        acc += f(x) * step
        x += step
    return acc


def integrate_threads(
    f: Callable[[float], float],
    a: float,
    b: float,
    *,
    n_iter: int = 100_000,
    n_threads: int = 4
) -> float:
    """Parallel integration via threads (usually no speedup for CPU-bound due to GIL)."""
    if not isinstance(n_iter, int):
        raise TypeError("n_iter must be int")
    if n_iter <= 0:
        raise ValueError("n_iter must be > 0")
    if n_threads <= 0:
        raise ValueError("n_threads must be > 0")
    if n_iter < n_threads:
        n_threads = n_iter

    base = n_iter // n_threads
    rem = n_iter % n_threads

    step_total = (b - a) / n_iter

    futures = []
    start_i = 0
    with ThreadPoolExecutor(max_workers=n_threads) as ex:
        for k in range(n_threads):
            iters = base + (1 if k < rem else 0)
            aa = a + start_i * step_total
            bb = aa + iters * step_total
            start_i += iters
            futures.append(ex.submit(_integrate_chunk_py, f, aa, bb, iters))

    return sum(ft.result() for ft in futures)


# ---------------------------
# Итерация 3: Processes (устойчиво: не передаём callable)
# ---------------------------

def _eval_func_by_id(func_id: str, x: float) -> float:
    """Map func_id to a computation to avoid passing callables into processes."""
    if func_id == "cos":
        return math.cos(x)
    if func_id == "sin":
        return math.sin(x)
    if func_id == "square":
        return x * x
    if func_id == "poly2":  # x^2 + 2x + 1
        return x * x + 2.0 * x + 1.0
    raise ValueError(f"Unknown func_id: {func_id!r}")


def _integrate_chunk_by_id(args: Tuple[str, float, float, int]) -> float:
    """Worker for ProcessPoolExecutor."""
    func_id, a, b, n_iter = args
    step = (b - a) / n_iter
    acc = 0.0
    x = a
    for _ in range(n_iter):
        acc += _eval_func_by_id(func_id, x) * step
        x += step
    return acc


def integrate_processes_by_id(
    func_id: str,
    a: float,
    b: float,
    *,
    n_iter: int = 100_000,
    n_proc: int = 4
) -> float:
    """Parallel integration via processes. Uses func_id to avoid pickling issues."""
    if not isinstance(n_iter, int):
        raise TypeError("n_iter must be int")
    if n_iter <= 0:
        raise ValueError("n_iter must be > 0")
    if n_proc <= 0:
        raise ValueError("n_proc must be > 0")
    if n_iter < n_proc:
        n_proc = n_iter

    base = n_iter // n_proc
    rem = n_iter % n_proc
    step_total = (b - a) / n_iter

    tasks: List[Tuple[str, float, float, int]] = []
    start_i = 0
    for k in range(n_proc):
        iters = base + (1 if k < rem else 0)
        aa = a + start_i * step_total
        bb = aa + iters * step_total
        start_i += iters
        tasks.append((func_id, aa, bb, iters))

    with ProcessPoolExecutor(max_workers=n_proc) as ex:
        return sum(ex.map(_integrate_chunk_by_id, tasks))


# ---------------------------
# Итерации 4–5: Cython (опционально)
# ---------------------------

@dataclass
class CythonModule:
    available: bool
    reason: str
    mod: object | None = None


def try_build_cython_module(tmp_dir: Path) -> CythonModule:
    """Attempt to build a Cython module on the fly (noGIL/prange optional)."""
    try:
        import Cython  # noqa: F401
    except Exception as e:
        return CythonModule(False, f"Cython not installed: {e}", None)

    pyx = r'''
# cython: language_level=3, boundscheck=False, wraparound=False, nonecheck=False, cdivision=True
from libc.math cimport cos
from cython.parallel cimport prange

cpdef double integrate_cos(double a, double b, int n_iter=100000):
    cdef double acc = 0.0
    cdef double step = (b - a) / n_iter
    cdef double x = a
    cdef int i
    for i in range(n_iter):
        acc += cos(x) * step
        x += step
    return acc

cpdef double integrate_cos_prange(double a, double b, int n_iter=100000):
    cdef double step = (b - a) / n_iter
    cdef double acc = 0.0
    cdef int i
    for i in prange(n_iter, nogil=True, schedule='static', reduction='+acc'):
        acc += cos(a + i * step) * step
    return acc
'''
    setup = r'''
from setuptools import setup, Extension
from Cython.Build import cythonize
import sys

extra_compile_args = []
extra_link_args = []

if sys.platform.startswith("linux"):
    extra_compile_args += ["-O3", "-fopenmp"]
    extra_link_args += ["-fopenmp"]
elif sys.platform == "darwin":
    # OpenMP may be unavailable by default on macOS.
    extra_compile_args += ["-O3"]
else:
    extra_compile_args += ["-O3"]

extensions = [
    Extension(
        name="integrate_cy",
        sources=["integrate_cy.pyx"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="integrate_cy",
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
)
'''
    tmp_dir.mkdir(parents=True, exist_ok=True)
    (tmp_dir / "integrate_cy.pyx").write_text(pyx, encoding="utf-8")
    (tmp_dir / "setup_integrate_cy.py").write_text(setup, encoding="utf-8")

    import subprocess
    cmd = [sys.executable, "setup_integrate_cy.py", "build_ext", "--inplace"]
    try:
        subprocess.check_call(cmd, cwd=str(tmp_dir))
    except Exception as e:
        return CythonModule(False, f"Cython build failed: {e}", None)

    sys.path.insert(0, str(tmp_dir))
    try:
        import importlib
        mod = importlib.import_module("integrate_cy")
    except Exception as e:
        return CythonModule(False, f"Import integrate_cy failed: {e}", None)

    return CythonModule(True, "OK", mod)


# ---------------------------
# Тесты (unittest)
# ---------------------------

class TestIntegrate(unittest.TestCase):
    def test_cos_integral_zero(self) -> None:
        res = integrate(math.cos, 0.0, math.pi, n_iter=300_000)
        self.assertAlmostEqual(res, 0.0, places=3)

    def test_quadratic(self) -> None:
        f = lambda x: x * x + 2 * x + 1
        res = integrate(f, 0.0, 1.0, n_iter=400_000)
        self.assertAlmostEqual(res, 7.0 / 3.0, places=3)

    def test_reverse_interval(self) -> None:
        f = lambda x: x * x
        res1 = integrate(f, 0.0, 1.0, n_iter=200_000)
        res2 = integrate(f, 1.0, 0.0, n_iter=200_000)
        self.assertAlmostEqual(res2, -res1, places=5)

    def test_bad_n_iter(self) -> None:
        with self.assertRaises(ValueError):
            integrate(math.cos, 0.0, 1.0, n_iter=0)
        with self.assertRaises(TypeError):
            integrate(math.cos, 0.0, 1.0, n_iter=1.5)  # type: ignore[arg-type]


# ---------------------------
# Бенчмарки (timeit)
# ---------------------------

@dataclass
class BenchRow:
    label: str
    best: float
    avg: float


def _fmt_seconds(s: float) -> str:
    return f"{s:.6f} s"


def bench_base(n_iter_values: Sequence[int], repeat: int = 5) -> List[BenchRow]:
    rows: List[BenchRow] = []
    for n in n_iter_values:
        ts = timeit.repeat(lambda: integrate(math.cos, 0.0, math.pi, n_iter=n), number=1, repeat=repeat)
        rows.append(BenchRow(label=f"base n={n}", best=min(ts), avg=sum(ts) / len(ts)))
    return rows


def bench_threads(thread_counts: Sequence[int], n_iter: int, repeat: int = 5) -> List[BenchRow]:
    rows: List[BenchRow] = []
    for t in thread_counts:
        ts = timeit.repeat(lambda: integrate_threads(math.cos, 0.0, math.pi, n_iter=n_iter, n_threads=t),
                           number=1, repeat=repeat)
        rows.append(BenchRow(label=f"threads t={t}", best=min(ts), avg=sum(ts) / len(ts)))
    return rows


def bench_processes(proc_counts: Sequence[int], n_iter: int, repeat: int = 5) -> List[BenchRow]:
    rows: List[BenchRow] = []
    for p in proc_counts:
        ts = timeit.repeat(lambda: integrate_processes_by_id("cos", 0.0, math.pi, n_iter=n_iter, n_proc=p),
                           number=1, repeat=repeat)
        rows.append(BenchRow(label=f"procs p={p}", best=min(ts), avg=sum(ts) / len(ts)))
    return rows


def bench_cython(mod: object, n_iter: int, repeat: int = 5) -> List[BenchRow]:
    rows: List[BenchRow] = []
    if not hasattr(mod, "integrate_cos"):
        return [BenchRow("cython integrate_cos missing", float("nan"), float("nan"))]

    ts = timeit.repeat(lambda: mod.integrate_cos(0.0, math.pi, n_iter), number=1, repeat=repeat)
    rows.append(BenchRow(label=f"cython integrate_cos n={n_iter}", best=min(ts), avg=sum(ts) / len(ts)))

    if hasattr(mod, "integrate_cos_prange"):
        for t in (2, 4, 6):
            os.environ["OMP_NUM_THREADS"] = str(t)
            ts2 = timeit.repeat(lambda: mod.integrate_cos_prange(0.0, math.pi, n_iter), number=1, repeat=repeat)
            rows.append(BenchRow(label=f"cython prange OMP={t} n={n_iter}", best=min(ts2), avg=sum(ts2) / len(ts2)))
    else:
        rows.append(BenchRow("cython integrate_cos_prange missing", float("nan"), float("nan")))

    return rows


def print_bench(rows: Sequence[BenchRow]) -> None:
    if not rows:
        print("(no results)")
        return
    w = max(len(r.label) for r in rows)
    print("-" * (w + 32))
    print(f"{'case':<{w}} | best       | avg")
    print("-" * (w + 32))
    for r in rows:
        print(f"{r.label:<{w}} | {_fmt_seconds(r.best):<10} | {_fmt_seconds(r.avg)}")
    print("-" * (w + 32))


# ---------------------------
# CLI
# ---------------------------

def run_doctest(verbose: bool = True) -> None:
    res = doctest.testmod(verbose=verbose)
    if res.failed:
        raise SystemExit(1)


def run_unittest() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestIntegrate)
    ok = unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    if not ok:
        raise SystemExit(1)


def run_bench() -> None:
    print("### Iteration 1: base integrate()")
    print_bench(bench_base([10_000, 50_000, 100_000, 300_000], repeat=5))

    print("\n### Iteration 2: threads (GIL — обычно нет ускорения)")
    print_bench(bench_threads([2, 4, 6], n_iter=300_000, repeat=5))

    print("\n### Iteration 3: processes (func_id, без pickle проблем)")
    print_bench(bench_processes([2, 4, 6], n_iter=300_000, repeat=5))

    print("\n### Iteration 4–5: cython (optional)")
    tmp_dir = Path(".cython_build")
    cy = try_build_cython_module(tmp_dir)
    if not cy.available:
        print(f"Cython not available: {cy.reason}")
        print("Чтобы включить Cython: pip install cython setuptools wheel")
        print("Для OpenMP на macOS может понадобиться: brew install libomp")
        return

    print("Cython module built successfully.")
    print_bench(bench_cython(cy.mod, n_iter=2_000_000, repeat=3))


def main(argv: Optional[Sequence[str]] = None) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--doctest", action="store_true", help="Run doctest")
    p.add_argument("--unittest", action="store_true", help="Run unit tests")
    p.add_argument("--bench", action="store_true", help="Run benchmarks")
    p.add_argument("--all", action="store_true", help="Run doctest + unittest + benchmarks")
    args = p.parse_args(list(argv) if argv is not None else None)

    if not (args.doctest or args.unittest or args.bench or args.all):
        p.print_help()
        return

    if args.all or args.doctest:
        print("Running doctest...")
        run_doctest(verbose=True)

    if args.all or args.unittest:
        print("\nRunning unittest...")
        run_unittest()

    if args.all or args.bench:
        print("\nRunning benchmarks...")
        run_bench()


if __name__ == "__main__":
    main()
