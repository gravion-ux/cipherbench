"""Benchmark summarization and known-answer test verification.

CipherBench analyzes benchmark JSON supplied by the operator. It does not
implement cryptography, and it never contacts a provider endpoint.
"""
from __future__ import annotations

import math
from statistics import median

__all__ = [
    "percentile",
    "summarize",
    "summarize_report",
    "verify_known_answers",
]


def _collect(records) -> tuple[dict[str, list[float]], int]:
    """Return the grouped measurements and the number of rejected rows.

    A row is rejected when it is not an object, when the algorithm name is not
    a usable string, or when the elapsed time is not a finite, non-negative
    number. Rejected rows are counted so an empty report can be told apart
    from a report whose input was entirely invalid.
    """
    grouped: dict[str, list[float]] = {}
    rejected = 0
    if not isinstance(records, list):
        return grouped, rejected
    for row in records:
        if not isinstance(row, dict):
            rejected += 1
            continue
        name = row.get("algorithm")
        elapsed = row.get("elapsed_ms")
        # bool is a subclass of int, and NaN/inf are not valid measurements: reject both.
        if not isinstance(name, str) or not name.strip():
            rejected += 1
            continue
        if isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)):
            rejected += 1
            continue
        try:
            value = float(elapsed)
        except (TypeError, ValueError, OverflowError):
            rejected += 1
            continue
        if value < 0 or not math.isfinite(value):
            rejected += 1
            continue
        grouped.setdefault(name.strip(), []).append(value)
    return grouped, rejected


def percentile(values, percent: float):
    """Return the nearest-rank percentile of a non-empty list of numbers."""
    if not values:
        return None
    ordered = sorted(values)
    if percent <= 0:
        return ordered[0]
    if percent >= 100:
        return ordered[-1]
    rank = math.ceil(percent / 100 * len(ordered))
    return ordered[min(max(rank - 1, 0), len(ordered) - 1)]


def _summary_rows(grouped: dict[str, list[float]]) -> list[dict]:
    return [
        {
            "algorithm": name,
            "samples": len(values),
            "median_ms": median(values),
            "min_ms": min(values),
            "max_ms": max(values),
            "p95_ms": percentile(values, 95),
        }
        for name, values in sorted(grouped.items())
    ]


def summarize(records: list[dict]) -> list[dict]:
    """Summarize measurement rows per algorithm."""
    grouped, _rejected = _collect(records)
    return _summary_rows(grouped)


def verify_known_answers(records) -> list[dict]:
    """Verify known-answer test (KAT) records.

    A known-answer record carries the digest the provider produced and the
    digest the fixture expects::

        {"algorithm": "AES-256-GCM",
         "kat": {"name": "vector-1",
                 "expected_digest": "<sha256 hex>",
                 "actual_digest": "<sha256 hex>"}}

    A mismatching digest is the signal that matters: it means the provider did
    not reproduce the expected output.
    """
    results: list[dict] = []
    if not isinstance(records, list):
        return results
    for row in records:
        if not isinstance(row, dict):
            continue
        kat = row.get("kat")
        if not isinstance(kat, dict):
            continue
        algorithm = row.get("algorithm")
        algorithm = algorithm.strip() if isinstance(algorithm, str) and algorithm.strip() else "unspecified"
        name = kat.get("name") or kat.get("vector") or "unspecified"
        expected = kat.get("expected_digest")
        actual = kat.get("actual_digest")
        expected_text = expected.strip().lower() if isinstance(expected, str) else ""
        actual_text = actual.strip().lower() if isinstance(actual, str) else ""
        if not expected_text or not actual_text:
            status = "incomplete"
        elif expected_text == actual_text:
            status = "pass"
        else:
            status = "fail"
        results.append(
            {
                "algorithm": algorithm,
                "vector": str(name),
                "status": status,
                "expected_digest": expected_text,
                "actual_digest": actual_text,
            }
        )
    return results


def summarize_report(records) -> dict:
    """Return the full benchmark report: summary, data quality and KAT results."""
    grouped, rejected = _collect(records)
    known_answers = verify_known_answers(records)
    return {
        "summary": _summary_rows(grouped),
        "rejected_rows": rejected,
        "known_answers": {
            "total": len(known_answers),
            "passed": sum(1 for row in known_answers if row["status"] == "pass"),
            "failed": sum(1 for row in known_answers if row["status"] == "fail"),
            "incomplete": sum(1 for row in known_answers if row["status"] == "incomplete"),
            "results": known_answers,
        },
    }
