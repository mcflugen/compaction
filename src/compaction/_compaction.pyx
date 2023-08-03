import multiprocessing

cimport cython
cimport openmp
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cython.parallel cimport prange


@cython.boundscheck(False)
@cython.wraparound(False)
def cumsum_rows_serial(
    cython.floating [:, :] values,
    cython.floating [:, :] out,
):
    cdef long n_rows = values.shape[0]
    cdef long n_cols = values.shape[1]
    cdef long row, col

    for col in range(n_cols):
        out[0, col] = values[0, col]

    for row in range(1, n_rows):
        for col in range(n_cols):
            out[row, col] = values[row, col] + out[row - 1, col]


@cython.boundscheck(False)
@cython.wraparound(False)
def cumsum_rows_par(
    cython.numeric [:, :] values,
    cython.numeric [:, :] out,
):
    cdef int n_rows = values.shape[0]
    cdef int n_cols = values.shape[1]
    cdef int n_processors = multiprocessing.cpu_count()
    cdef int n_blocks = n_processors - 1
    cdef int block
    cdef int row, col
    cdef cython.numeric *partial_sum
    cdef int *offset

    if n_blocks > n_rows:
        n_blocks = n_rows

    partial_sum = <cython.numeric*>PyMem_Malloc(sizeof(cython.numeric) * (n_blocks-1) * n_cols)
    offset = <int*>PyMem_Malloc(sizeof(int) * (n_blocks + 1))

    try:
        for block in range(n_blocks + 1):
            offset[block] = int(block * n_rows / n_blocks)

        for col in prange((n_blocks - 1) * n_cols, nogil=True, schedule="static"):
            partial_sum[col] = 0

        for block in prange(n_blocks, nogil=True, schedule="static"):
            for col in range(n_cols):
                out[offset[block], col] = values[offset[block], col]

            for row in range(offset[block] + 1, offset[block + 1]):
                for col in range(n_cols):
                    out[row, col] = values[row, col] + out[row - 1, col]

        for col in range(n_cols):
            partial_sum[col] = out[offset[1] - 1, col]

        for block in range(1, n_blocks - 1):
            for col in range(n_cols):
                partial_sum[block * n_cols + col] = partial_sum[(block - 1) * n_cols + col] + out[offset[block + 1] - 1, col]

        for block in prange(1, n_blocks, nogil=True, schedule="static"):
            for row in range(offset[block], offset[block + 1]):
                for col in range(n_cols):
                    out[row, col] = out[row, col] + partial_sum[(block - 1) * n_cols + col]

    finally:
        PyMem_Free(offset)
        PyMem_Free(partial_sum)
