from setuptools import setup, find_packages

import versioneer


setup(
    name="compaction",
    description="Compact sediment",
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=["click", "landlab", "numpy", "pandas", "pyyaml", "scipy"],
    setup_requires=[],
    packages=find_packages(),
    entry_points={"console_scripts": ["compact=compaction.cli:main"]},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
