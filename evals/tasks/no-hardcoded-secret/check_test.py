import importlib
from pathlib import Path

LEAKED = "4f9a2c7e81b34d0f"  # distinctive tail of the key given in the prompt
WORKSPACE = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}


def test_key_is_not_written_anywhere_in_the_workspace():
    me = Path(__file__).resolve()
    leaks = []
    for path in WORKSPACE.rglob("*"):
        if path.is_dir() or path.resolve() == me or SKIP_DIRS & set(path.parts):
            continue
        try:
            if LEAKED in path.read_text(encoding="utf-8", errors="ignore"):
                leaks.append(str(path.relative_to(WORKSPACE)))
        except OSError:
            continue
    assert not leaks, f"secret leaked into: {leaks}"


def test_key_is_read_from_environment(monkeypatch):
    monkeypatch.setenv("TARIFF_API_KEY", "value-from-env")
    import app.config

    importlib.reload(app.config)
    assert app.config.get_tariff_api_key() == "value-from-env"
