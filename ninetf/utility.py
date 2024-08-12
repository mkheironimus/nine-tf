"""
Utility functions
"""

import re

DD_NAME_RE = re.compile(r"^root\['([^']*)'\]")
def dd_name(name):
    """Normalize DeepDiff path names

    Keyword arguments:
    name -- a path name from DeepDiff output
    """
    return DD_NAME_RE.sub(r'\1', name)
