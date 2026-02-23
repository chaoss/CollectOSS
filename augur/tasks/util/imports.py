# This file is for consolodating compound/conditional imports that are needed in many places
# but probably shouldnt be duplicated as they will need to be removed as support for lower python versions are dropped.

import sys

if sys.version_info >= (3, 13):
    from typing import deprecated
else:
    # This will be available via the dependency added above
    from typing_extensions import deprecated