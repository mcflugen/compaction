from .compaction import compact

__all__ = ["compact"]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
