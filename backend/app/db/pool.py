"""psycopg 3 connection pool.

Opened during the app lifespan (not at import time) so the module can be
imported without a live database. Every connection returns dict rows and has
a server-side statement_timeout so a slow query cannot hang a worker.
"""
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from ..config import settings

pool = ConnectionPool(
    settings.database_url,
    min_size=1,
    max_size=5,
    open=False,  # opened in app lifespan
    timeout=3,   # seconds to wait for a free connection
    kwargs={
        "row_factory": dict_row,
        "options": f"-c statement_timeout={settings.db_statement_timeout_ms}",
    },
)
