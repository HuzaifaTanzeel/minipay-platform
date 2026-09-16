"""CLI process contract: --help, missing DSN, unhealthy health check."""
import pytest

from support_tool.cli import main
from support_tool.exit_codes import ExitCode
from support_tool.models import ApiProbes, Probe


def test_help_exits_zero():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0


def test_missing_dsn_returns_3(monkeypatch, tmp_path):
    monkeypatch.delenv("MINIPAY_DB_DSN", raising=False)
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)
    rc = main(["--transaction", "TXN00000001"])
    assert rc == ExitCode.DEPENDENCY


def test_not_found_returns_1(monkeypatch, tmp_path):
    monkeypatch.setenv("MINIPAY_DB_DSN", "postgresql://unused")
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)

    class EmptyStore:
        def find_all_by_ref(self, ref):
            return []

        def callbacks_for(self, txn_id):
            return []

        def stuck(self, minutes, now, limit):
            return 0, []

        def failed_summary(self):
            return []

    monkeypatch.setattr("support_tool.cli.PostgresTransactionStore", lambda *a, **k: EmptyStore())
    rc = main(["--transaction", "NOPE"])
    assert rc == ExitCode.NOT_FOUND


def test_health_unhealthy_returns_3(monkeypatch, tmp_path):
    monkeypatch.setenv("MINIPAY_DB_DSN", "postgresql://unused")
    monkeypatch.setattr("support_tool.config.Path.home", lambda: tmp_path)

    class Down:
        def ping_db(self):
            return Probe("database", False, 1.0, "OperationalError")

        def ping_api(self):
            return ApiProbes(
                health=Probe("health", True, 1.0, "HTTP 200"),
                ready=Probe("ready", True, 1.0, "HTTP 200"),
            )

    monkeypatch.setattr("support_tool.cli.CompositeHealthChecker", lambda cfg: Down())
    rc = main(["--health"])
    assert rc == ExitCode.DEPENDENCY
