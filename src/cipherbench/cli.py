"""Command-line entry point for CipherBench.

Problems are reported as one-line messages instead of Python tracebacks so the
tool can be used directly in CI pipelines.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .benchmark import summarize_report

EXIT_OK = 0
EXIT_INVALID_INPUT = 1
EXIT_USAGE = 2

# A benchmark file may hold the records directly or wrap them in an object.
RECORD_KEYS = ("records", "results", "benchmark")


class RecordsFileError(Exception):
    """The benchmark file is missing or cannot be read."""


class RecordsFormatError(Exception):
    """The benchmark file was read but does not contain usable records."""


def _load_records(path: Path) -> list:
    """Read and parse a benchmark file.

    ``utf-8-sig`` keeps files exported on Windows readable: those often carry a
    UTF-8 byte-order mark that plain ``utf-8`` decoding rejects.
    """
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise RecordsFileError(
            f"cannot read benchmark file {path}: {exc.strerror or exc}"
        ) from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RecordsFormatError(
            f"invalid JSON in {path} at line {exc.lineno} column {exc.colno}: {exc.msg}"
        ) from exc
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in RECORD_KEYS:
            value = data.get(key)
            if isinstance(value, list):
                return value
        raise RecordsFormatError(
            f"benchmark file {path} holds an object without a record list "
            f"(expected one of: {', '.join(RECORD_KEYS)})"
        )
    raise RecordsFormatError(f"benchmark file {path} must contain a JSON array or object")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cipherbench",
        description="Summarize benchmark records and verify known-answer tests.",
    )
    parser.add_argument("records", type=Path, help="Benchmark records JSON file")
    parser.add_argument("--output", type=Path, help="Optional path for the JSON report")
    parser.add_argument(
        "--fail-on-kat-failure",
        action="store_true",
        help="Exit with status 1 when a known-answer test fails",
    )
    args = parser.parse_args(argv)

    try:
        records = _load_records(args.records)
    except RecordsFileError as exc:
        print(f"cipherbench: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except RecordsFormatError as exc:
        print(f"cipherbench: {exc}", file=sys.stderr)
        return EXIT_INVALID_INPUT

    report = summarize_report(records)
    report.update(
        {
            "tool": "CipherBench",
            "mode": "offline-benchmark-analysis",
            "schema_version": 1,
            "notice": (
                "Results depend on hardware, provider, configuration and workload. "
                "A known-answer test failure means the provider did not reproduce "
                "the expected output."
            ),
        }
    )
    text = json.dumps(report, indent=2)
    if args.output:
        try:
            args.output.write_text(text + "\n", encoding="utf-8")
        except OSError as exc:
            print(
                f"cipherbench: cannot write report to {args.output}: {exc.strerror or exc}",
                file=sys.stderr,
            )
            return EXIT_INVALID_INPUT
    print(text)

    if args.fail_on_kat_failure and report["known_answers"]["failed"]:
        return EXIT_INVALID_INPUT
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
