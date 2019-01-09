from setuptools import setup, find_packages


setup(name='compaction',
      version='0.1',
      description='Compact sediment',
      author='Eric Hutton',
      author_email='huttone@colorado.edu',
      url='http://csdms.colorado.edu',
      install_requires=['scipy', 'pandas', 'pyyaml'],
      setup_requires=[],
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'compact=compaction.cli:main',
          ],
      },
)
