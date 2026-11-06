"""CipherBench: benchmark and interoperability test harness for vetted providers.

Public API
----------
``summarize``             latency summary per algorithm
``summarize_report``      summary plus data quality and known-answer results
``verify_known_answers``  known-answer test (KAT) verification
``percentile``            nearest-rank percentile helper
"""
from .benchmark import percentile, summarize, summarize_report, verify_known_answers

__all__ = [
    "__version__",
    "percentile",
    "summarize",
    "summarize_report",
    "verify_known_answers",
]

__version__ = "0.2.0"
