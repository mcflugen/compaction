from setuptools import setup, find_packages

import versioneer


setup(
    name="compaction",
    description="Compact sediment",
    author="Eric Hutton",
    author_email="huttone@colorado.edu",
    url="http://csdms.colorado.edu",
    install_requires=["scipy", "pandas", "pyyaml"],
    setup_requires=[],
    packages=find_packages(),
    entry_points={"console_scripts": ["compact=compaction.cli:main"]},
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
