"""Pytest plugin for the labs (registered through the pytest11 entry point).

Three things:

* `load_lab(__file__)` imports the lab module next to a test file: your
  `lab.py`, or a reference solution when CO_SOLUTION is set —
  `solution/lab.py` for "imperative" (or "1"), `solution/functional.py` for
  "functional". The same tests check all of them, so every reference solution
  is itself tested.
* A test that dies on NotImplementedError is reported as *skipped: not
  started* rather than failed, so an untouched stub reads as work to do and a
  red F always means a real bug.
* Tests named `test_stepN_...` are grouped, and a progress line per unit is
  printed at the end: a step is done when every one of its tests passes.
"""

from __future__ import annotations

import importlib.util
import os
import re
import signal
import sys
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

import pytest


SOLUTION_FILES = {"1": "lab.py", "imperative": "lab.py", "functional": "functional.py"}


def solution_variant() -> str | None:
    v = os.environ.get("CO_SOLUTION")
    if v and v not in SOLUTION_FILES:
        raise ValueError(f"CO_SOLUTION={v!r}: expected one of {sorted(SOLUTION_FILES)}")
    return "imperative" if v == "1" else v


def load_lab(test_file: str):
    lab_dir = Path(test_file).resolve().parent
    variant = solution_variant()
    path = lab_dir / "solution" / SOLUTION_FILES[variant] if variant else lab_dir / "lab.py"
    modname = f"_colab_{re.sub(r'\W', '_', lab_dir.parent.name)}_{variant or 'yours'}"
    if modname in sys.modules:
        return sys.modules[modname]
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


@contextmanager
def time_limit(seconds: float, hint: str = ""):
    """Fail, instead of hanging, when the body runs longer than `seconds`.

    For tests whose failure mode is an infinite loop (a simplex that cycles, a
    search that never terminates)."""
    def fire(signum, frame):
        raise AssertionError(f"took longer than {seconds} s. {hint}".strip())
    old = signal.signal(signal.SIGALRM, fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if call.when == "call" and call.excinfo is not None \
            and call.excinfo.errisinstance(NotImplementedError):
        msg = str(call.excinfo.value) or item.name
        rep.outcome = "skipped"
        rep.longrepr = (str(item.path), item.location[1] or 0, f"not started: {msg}")


_STEP = re.compile(r"test_step(\d+)")
_UNIT = re.compile(r"units/([^/]+)/")
_progress: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))


def pytest_runtest_logreport(report):
    step, unit = _STEP.search(report.nodeid), _UNIT.search(report.nodeid)
    if not (step and unit):
        return
    if report.when == "call" or (report.when == "setup" and not report.passed):
        _progress[unit.group(1)][int(step.group(1))].append(report.outcome)


def pytest_terminal_summary(terminalreporter):
    if not _progress:
        return
    tr = terminalreporter
    variant = solution_variant()
    label = f"reference solution: {variant}" if variant else "your lab"
    tr.section(f"lab progress ({label})", sep="─")
    for unit in sorted(_progress):
        cells = []
        for step in sorted(_progress[unit]):
            outs = _progress[unit][step]
            if all(o == "passed" for o in outs):
                cells.append(f"step {step} ✓")
            elif any(o == "failed" for o in outs):
                cells.append(f"step {step} ✗")
            elif any(o == "passed" for o in outs):
                cells.append(f"step {step} ½")
            else:
                cells.append(f"step {step} ·")
        tr.write_line(f"  {unit:<28} " + "   ".join(cells))
    tr.write_line("  ✓ done   ½ partly   ✗ failing   · not started")
