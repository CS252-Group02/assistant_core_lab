"""Run local checks without CI. Default: all acceptance tests; --baseline: existing tests only.

Temporary files stay under .lab5-tmp so restricted Windows environments do not
need access to another process's pytest cache or the system temporary directory.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Check setup and existing Lab 4 tests only")
    args = parser.parse_args()
    temporary_root = ROOT / ".lab5-tmp"
    temporary_root.mkdir(exist_ok=True)
    # Keep the output for inspection. Each run gets a new directory.
    run_dir = Path(tempfile.mkdtemp(prefix="run-", dir=temporary_root))
    pytest = [
        "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp", str(run_dir / "pytest"),
    ]
    if args.baseline:
        pytest.extend(["tests", "--ignore=tests/lab5"])
    else:
        pytest.extend(["tests", "practice"])
    commands = [
        ["-m", "ruff", "check", "src", "tests", "practice", "scripts", "--no-cache"],
        pytest,
    ]
    failed = False
    for command in commands:
        print(f"\n> {sys.executable} {' '.join(command)}", flush=True)
        result = subprocess.run([sys.executable, *command], cwd=ROOT)
        failed |= result.returncode != 0
    print(f"\nTemporary test files: {run_dir}", flush=True)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
