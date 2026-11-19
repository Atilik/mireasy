"""
Compatibility wrapper: the documented `python download_models.py` keeps working
in a source checkout. The code lives in mireasy/download_models.py and is also
installed as the `mireasy-download-models` command.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mireasy.download_models import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
