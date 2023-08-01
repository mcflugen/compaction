import os

from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        Extension(
            "compaction._compaction",
            ["src/compaction/_compaction.pyx"],
            extra_compile_args=["-fopenmp"] if "WITH_OPENMP" in os.environ else [],
            extra_link_args=["-fopenmp"] if "WITH_OPENMP" in os.environ else [],
        ),
        compiler_directives={"embedsignature": True, "language_level": 3},
    )
)
