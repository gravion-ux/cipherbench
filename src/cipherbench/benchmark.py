import math
from statistics import median


def summarize(records: list[dict]):
    if not isinstance(records, list):
        return []
    grouped = {}
    for row in records:
        if not isinstance(row, dict):
            continue
        name = row.get("algorithm")
        elapsed = row.get("elapsed_ms")
        # bool is a subclass of int, and NaN/inf are not valid measurements: reject both.
        if not isinstance(name, str) or isinstance(elapsed, bool) or not isinstance(elapsed, (int, float)):
            continue
        try:
            value = float(elapsed)
        except (TypeError, ValueError, OverflowError):
            continue
        if value < 0 or not math.isfinite(value):
            continue
        grouped.setdefault(name, []).append(value)
    return [{"algorithm": name, "samples": len(values), "median_ms": median(values),
             "min_ms": min(values), "max_ms": max(values)}
            for name, values in sorted(grouped.items())]
