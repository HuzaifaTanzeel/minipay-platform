"""Ensure `from fakes import ...` works whether pytest's rootdir is python/ or the repo."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
