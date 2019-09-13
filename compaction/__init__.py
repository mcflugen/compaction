from ._version import get_versions
from .compaction import compact

__all__ = ["compact"]


__version__ = get_versions()["version"]
del get_versions
