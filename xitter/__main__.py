"""Entry point for ``python -m xitter``."""

from __future__ import annotations

import sys

from xitter.cli import main

if __name__ == "__main__":
    sys.exit(main())
