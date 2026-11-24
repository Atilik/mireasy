"""Entry point of the ``mireasy`` command and of ``python -m mireasy``.

The analysis libraries are large, so they are loaded here, behind a loading
bar, and not at the top of this file.
"""
import sys

from .loading import loading_bar


def main(argv=None):
    """Show a loading bar while MIReasy loads, then open the shell."""
    with loading_bar():
        from .mireasy import main as open_shell
    return open_shell(argv)


if __name__ == "__main__":
    sys.exit(main())
