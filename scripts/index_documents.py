"""Compatibility shim — prefer 'python -m scripts.indexer'."""

import sys
from pathlib import Path

# Ensure project root is on sys.path when run as a bare script
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.indexer.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
