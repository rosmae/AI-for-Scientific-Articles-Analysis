# Import all routers to make them available when importing the package
from . import articles, search
# Import other routers when they are created
try:
    from . import keywords, scoring
except ImportError:
    pass  # These will be imported once the files are created
