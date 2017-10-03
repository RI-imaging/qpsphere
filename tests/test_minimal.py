import os
from os.path import abspath, dirname
import sys
import tempfile

import numpy as np

# Add parent directory to beginning of path variable
sys.path.insert(0, dirname(dirname(abspath(__file__))))
import qpsphere  # noqa: E402


def test_nothing():
    pass

if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()

