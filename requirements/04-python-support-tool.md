# 04 – Python Support Utility

Build a Python CLI intended for an L2 engineer.

Minimum interface:

```bash
python support_tool.py --transaction TXN000123
```

The tool should retrieve information from the API and/or database and produce a concise diagnostic report containing:
- transaction details;
- customer/reference/amount/status;
- relevant timestamps;
- callback/retry information;
- detected anomalies or likely failure reason; and
- recommended next action.

Also support a machine-readable output mode such as `--json`.

Engineering expectations:
- configuration via environment/config file rather than hard-coded credentials;
- error and timeout handling;
- useful exit codes;
- logging;
- modular/readable code; and
- automated unit tests for important logic.

Bonus: add a command that summarizes stuck/failed transactions or performs a health check across API/database dependencies.
