"""Argparse delivery and composition root. stdout = report; stderr = logs."""
from __future__ import annotations

import argparse
import logging
import sys

import psycopg
import requests

from .api import HttpHealthChecker
from .commands import (
    CheckHealth,
    DiagnosePayment,
    NotFoundError,
    SummarizeFailed,
    SummarizeStuck,
)
from .config import Config, ConfigError, load
from .db import PostgresTransactionStore, ping_database
from .exit_codes import SIGINT, ExitCode
from .models import ApiProbes, Probe, Report
from .ports import SystemClock
from .report import render_failed, render_health, render_report, render_stuck, to_json

log = logging.getLogger("support_tool")


class CompositeHealthChecker:
    """Wires DB ping + HTTP probes. Constructed only here (composition root)."""

    def __init__(self, cfg: Config):
        self._cfg = cfg
        self._http = HttpHealthChecker(cfg.api_url, cfg.timeout_s)

    def ping_db(self) -> Probe:
        return ping_database(self._cfg.db_dsn, self._cfg.timeout_s)

    def ping_api(self) -> ApiProbes:
        return self._http.ping_api()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="support_tool",
        description="MiniPay L2 diagnostics (database is authoritative; works if the API is down).",
        epilog="exit codes: 0 ok | 1 not found | 2 anomalies detected | 3 dependency/config error",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--transaction", metavar="REF", help="diagnose one payment by transaction_ref")
    group.add_argument("--stuck-summary", action="store_true", help="count + oldest stuck PROCESSING rows")
    group.add_argument("--failed-summary", action="store_true", help="FAILED counts by failure_code")
    group.add_argument("--health", action="store_true", help="probe database, /health, and /ready")
    parser.add_argument("--json", action="store_true", help="machine-readable stdout")
    parser.add_argument("--config", metavar="PATH", help="INI file with a [minipay] section")
    parser.add_argument("-v", "--verbose", action="store_true", help="DEBUG logs on stderr")
    return parser


def _print(obj, *, as_json: bool, text_fn) -> None:
    if as_json:
        print(to_json(obj))
    else:
        print(text_fn(obj))


def _run(args: argparse.Namespace, cfg: Config) -> int:
    clock = SystemClock()
    store = PostgresTransactionStore(cfg.db_dsn, timeout_s=cfg.timeout_s)

    if args.transaction:
        report: Report = DiagnosePayment(store, clock, cfg.stuck_minutes).run(args.transaction)
        _print(report, as_json=args.json, text_fn=render_report)
        return int(ExitCode.ANOMALIES if report.anomalies else ExitCode.OK)

    if args.stuck_summary:
        summary = SummarizeStuck(store, clock, cfg.stuck_minutes).run()
        _print(summary, as_json=args.json, text_fn=render_stuck)
        return int(ExitCode.OK)

    if args.failed_summary:
        summary = SummarizeFailed(store).run()
        _print(summary, as_json=args.json, text_fn=render_failed)
        return int(ExitCode.OK)

    snapshot = CheckHealth(CompositeHealthChecker(cfg)).run()
    _print(snapshot, as_json=args.json, text_fn=render_health)
    return int(ExitCode.OK if snapshot.healthy else ExitCode.DEPENDENCY)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        stream=sys.stderr,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        cfg = load(args.config)
        return _run(args, cfg)
    except ConfigError as e:
        log.error("%s", e)
        print(e, file=sys.stderr)
        return int(ExitCode.DEPENDENCY)
    except NotFoundError as e:
        print(e, file=sys.stderr)
        return int(ExitCode.NOT_FOUND)
    except (psycopg.OperationalError, requests.RequestException) as e:
        log.error("dependency failure: %s", e)
        print(f"dependency failure: {type(e).__name__}", file=sys.stderr)
        if args.verbose:
            log.exception("dependency failure")
        return int(ExitCode.DEPENDENCY)
    except KeyboardInterrupt:
        return SIGINT
