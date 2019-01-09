from .compaction import compact, load_config

__all__ = ["compact", "load_config"]

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
