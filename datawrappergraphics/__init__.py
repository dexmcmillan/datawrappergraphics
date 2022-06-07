try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    __version__ = "unknown"

from datawrappergraphics.errors import *
from datawrappergraphics.icons import dw_icons
from datawrappergraphics.graphics import *