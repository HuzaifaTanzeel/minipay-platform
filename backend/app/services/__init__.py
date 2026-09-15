"""Business-logic layer.

Services own the transaction boundary (they borrow a connection from the
pool) and orchestrate repositories. Both the JSON API and the server-rendered
UI call these same functions, so the two surfaces share one code path.
"""
