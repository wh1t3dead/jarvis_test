from __future__ import annotations

import importlib
import pathlib
import sys


def test_app_main_importable() -> None:
    """
    Smoke check that top-level imports work in src-layout.

    This simulates an installed environment by ensuring `src/` is on sys.path
    and then importing the entrypoint module.
    """

    root = pathlib.Path(__file__).resolve().parents[1]
    src = root / "src"
    sys.path.insert(0, str(src))

    module = importlib.import_module("app.main")
    assert hasattr(module, "main")

