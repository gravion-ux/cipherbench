import json

import cipherbench
from cipherbench import benchmark
from cipherbench.benchmark import summarize


def test_median_and_invalid_rows():
    out=summarize([{"algorithm":"A","elapsed_ms":2},{"algorithm":"A","elapsed_ms":4},{"algorithm":"A","elapsed_ms":-1}])
    assert out[0]["median_ms"]==3 and out[0]["samples"]==2


def test_boolean_elapsed_is_rejected():
    assert summarize([{"algorithm":"A","elapsed_ms":True}])==[]


def test_non_finite_elapsed_is_rejected():
    out=summarize([{"algorithm":"A","elapsed_ms":float("nan")},{"algorithm":"A","elapsed_ms":float("inf")}])
    assert out==[]
    assert json.dumps(out,allow_nan=False)=="[]"


def test_non_list_root_is_ignored():
    assert summarize({"algorithm":"A","elapsed_ms":1})==[]


def test_non_dict_row_is_ignored():
    assert summarize(["not-a-record"])==[]


# --- data quality -----------------------------------------------------------


def test_blank_algorithm_name_is_rejected():
    assert summarize([{"algorithm":"   ","elapsed_ms":1}])==[]


def test_algorithm_name_is_trimmed():
    out = summarize([{"algorithm": "  A  ", "elapsed_ms": 2}])
    assert out[0]["algorithm"] == "A"


def test_rejected_rows_are_counted():
    report = benchmark.summarize_report(
        [{"algorithm": "A", "elapsed_ms": 2}, {"algorithm": "A", "elapsed_ms": -1}, "junk"]
    )
    assert report["rejected_rows"] == 2
    assert report["summary"][0]["samples"] == 1


def test_summary_reports_percentiles():
    out = summarize([{"algorithm": "A", "elapsed_ms": value} for value in range(1, 101)])
    assert out[0]["p95_ms"] == 95
    assert out[0]["min_ms"] == 1
    assert out[0]["max_ms"] == 100


def test_percentile_uses_the_nearest_rank():
    assert benchmark.percentile([1, 2, 3, 4], 50) == 2
    assert benchmark.percentile([1, 2, 3, 4], 100) == 4
    assert benchmark.percentile([1, 2, 3, 4], 0) == 1


def test_percentile_of_an_empty_list_is_none():
    assert benchmark.percentile([], 95) is None


# --- known-answer tests ------------------------------------------------------


def test_known_answer_that_matches_is_passed():
    results = benchmark.verify_known_answers(
        [{"algorithm": "AES-256-GCM",
          "kat": {"name": "vector-1", "expected_digest": "abc123", "actual_digest": "abc123"}}]
    )
    assert results[0]["status"] == "pass"
    assert results[0]["vector"] == "vector-1"


def test_known_answer_that_differs_is_failed():
    results = benchmark.verify_known_answers(
        [{"algorithm": "AES-256-GCM",
          "kat": {"name": "vector-1", "expected_digest": "abc123", "actual_digest": "def456"}}]
    )
    assert results[0]["status"] == "fail"


def test_known_answer_without_an_actual_digest_is_incomplete():
    results = benchmark.verify_known_answers(
        [{"algorithm": "AES-256-GCM", "kat": {"name": "vector-1", "expected_digest": "abc123"}}]
    )
    assert results[0]["status"] == "incomplete"


def test_known_answer_digests_are_compared_case_insensitively():
    results = benchmark.verify_known_answers(
        [{"algorithm": "A", "kat": {"expected_digest": "ABC123", "actual_digest": "abc123"}}]
    )
    assert results[0]["status"] == "pass"


def test_rows_without_a_known_answer_are_ignored():
    assert benchmark.verify_known_answers([{"algorithm": "A", "elapsed_ms": 1}]) == []


def test_report_counts_known_answer_results():
    report = benchmark.summarize_report(
        [
            {"algorithm": "A", "elapsed_ms": 1},
            {"algorithm": "A", "kat": {"expected_digest": "x", "actual_digest": "x"}},
            {"algorithm": "A", "kat": {"expected_digest": "x", "actual_digest": "y"}},
        ]
    )
    assert report["known_answers"]["total"] == 2
    assert report["known_answers"]["passed"] == 1
    assert report["known_answers"]["failed"] == 1


# --- public API --------------------------------------------------------------


def test_package_exposes_the_public_api():
    assert cipherbench.summarize is summarize
    assert cipherbench.summarize_report is benchmark.summarize_report
    assert cipherbench.verify_known_answers is benchmark.verify_known_answers
    assert cipherbench.percentile is benchmark.percentile
    assert cipherbench.__version__


def test_benchmark_module_exports_are_declared():
    assert "summarize" in benchmark.__all__
