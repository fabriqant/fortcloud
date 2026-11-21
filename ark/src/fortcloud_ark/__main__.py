"""Point d'entrée `python -m fortcloud_ark`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
