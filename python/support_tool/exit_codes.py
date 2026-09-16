"""Process exit codes. Documented in --help and python/README.md."""
from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    NOT_FOUND = 1
    ANOMALIES = 2
    DEPENDENCY = 3


# Unix convention for SIGINT; not part of the tool's documented 0–3 set.
SIGINT = 130
