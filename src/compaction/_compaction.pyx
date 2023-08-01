cimport cython
cimport openmp
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cython.parallel cimport prange


@cython.boundscheck(False)
@cython.wraparound(False)
def cumsum_rows(
    cython.floating [:, :] values,
    cython.floating [:, :] out,
):
    cdef long n_rows = values.shape[0]
    cdef long n_cols = values.shape[1]

    for col in range(n_cols):
        out[0, col] = values[0, col]

    for row in range(1, n_rows):
        for col in range(n_cols):
            out[row, col] = values[row, col] + out[row - 1, col]


@cython.boundscheck(False)
@cython.wraparound(False)
def cumsum_rows_par(
    cython.floating [:, :] values,
    cython.floating [:, :] out,
):
    cdef long n_rows = values.shape[0]
    cdef long n_cols = values.shape[1]
    # cdef long rows_per_block = 2
    # cdef long n_blocks = n_rows // rows_per_block
    cdef long n_blocks  # = openmp.omp_get_num_threads()
    cdef long rows_per_block
    cdef long block
    cdef long start, end
    cdef long row, col
    cdef long completed_blocks = 0
    # cdef double *partial_sum = <double*>PyMem_Malloc(sizeof(double) * n_blocks * n_cols)
    cdef double *partial_sum

    openmp.omp_set_dynamic(1)
    n_blocks = openmp.omp_get_num_threads()
    rows_per_block = n_rows // n_blocks
    partial_sum = <double*>PyMem_Malloc(sizeof(double) * n_blocks * n_cols)

    try:
        for block in range(n_blocks):
            for col in range(n_cols):
                partial_sum[block * n_cols + col] = 0.0

        while completed_blocks < n_blocks:

            for block in prange(completed_blocks, n_blocks, nogil=True, schedule="static"):
                start = block * rows_per_block
                end = start + rows_per_block
                if end > n_rows:
                    end = n_rows

                for col in range(n_cols):
                    out[start, col] = values[start, col] + partial_sum[block * n_cols + col]

                for row in range(start + 1, end):
                    for col in range(n_cols):
                        out[row, col] = values[row, col] + out[row - 1, col]

                for col in range(n_cols):
                    partial_sum[block * n_cols + col] = out[end - 1, col]

            completed_blocks = completed_blocks + 1
    finally:
        PyMem_Free(partial_sum)
