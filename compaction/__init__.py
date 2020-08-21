import pkg_resources

from .compaction import compact

__version__ = pkg_resources.get_distribution("compaction").version
__all__ = ["compact"]
