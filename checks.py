from __future__ import annotations

import argparse
import subprocess
import sys


def _run_step(label: str, command: list[str]) -> int:
    print(f"[checks] {label}: {' '.join(command)}")
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        print(f"[checks] {label} failed with exit code {completed.returncode}")
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run project lint and test checks.")
    parser.add_argument(
        "--tests-only",
        action="store_true",
        help="Run the unittest suite without linting.",
    )
    parser.add_argument(
        "--lint-only",
        action="store_true",
        help="Run Ruff without the unittest suite.",
    )
    args = parser.parse_args()

    if args.tests_only and args.lint_only:
        parser.error("Choose only one of --tests-only or --lint-only.")

    steps: list[tuple[str, list[str]]] = []
    if not args.lint_only:
        steps.append(
            (
                "tests",
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
            )
        )
    if not args.tests_only:
        steps.append(
            (
                "lint",
                [sys.executable, "-m", "ruff", "check", "."],
            )
        )

    for label, command in steps:
        exit_code = _run_step(label, command)
        if exit_code != 0:
            return exit_code

    print("[checks] All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
