#!/usr/bin/env python3
"""Entrypoint: python python/support_tool.py --transaction TXN00000001"""
from __future__ import annotations

import sys
from pathlib import Path

# `python python/support_tool.py` puts this directory on sys.path[0].
sys.path.insert(0, str(Path(__file__).resolve().parent))

from support_tool.cli import main

if __name__ == "__main__":
    sys.exit(main())
