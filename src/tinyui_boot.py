"""Standalone launcher for frozen and script-based app startup."""

from __future__ import annotations

import multiprocessing as mp

from app.main import main


if __name__ == "__main__":
    mp.freeze_support()
    main()
