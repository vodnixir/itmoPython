
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
    