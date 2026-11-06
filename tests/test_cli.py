import json

from cipherbench import cli


def _write_records(tmp_path, payload, name="records.json", encoding="utf-8"):
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding=encoding)
    return path


def test_cli_reports_a_missing_file_without_a_traceback(tmp_path, capsys):
    code = cli.main([str(tmp_path / "absent.json")])
    captured = capsys.readouterr()
    assert code == cli.EXIT_USAGE
    assert "cipherbench:" in captured.err
    assert "Traceback" not in captured.err


def test_cli_reports_invalid_json_without_a_traceback(tmp_path, capsys):
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    code = cli.main([str(path)])
    captured = capsys.readouterr()
    assert code == cli.EXIT_INVALID_INPUT
    assert "invalid JSON" in captured.err
    assert "Traceback" not in captured.err


def test_cli_reads_a_benchmark_file_that_starts_with_a_byte_order_mark(tmp_path, capsys):
    path = tmp_path / "bom.json"
    path.write_text(json.dumps([{"algorithm": "A", "elapsed_ms": 1}]), encoding="utf-8-sig")
    code = cli.main([str(path)])
    captured = capsys.readouterr()
    assert code == cli.EXIT_OK
    assert json.loads(captured.out)["summary"][0]["samples"] == 1


def test_cli_accepts_an_object_that_wraps_the_records(tmp_path, capsys):
    path = _write_records(tmp_path, {"records": [{"algorithm": "A", "elapsed_ms": 1}]})
    code = cli.main([str(path)])
    captured = capsys.readouterr()
    assert code == cli.EXIT_OK
    assert json.loads(captured.out)["summary"][0]["samples"] == 1


def test_cli_rejects_an_object_without_a_record_list(tmp_path, capsys):
    path = _write_records(tmp_path, {"unexpected": True})
    code = cli.main([str(path)])
    captured = capsys.readouterr()
    assert code == cli.EXIT_INVALID_INPUT
    assert "cipherbench:" in captured.err
    assert "Traceback" not in captured.err


def test_cli_prints_a_json_report(tmp_path, capsys):
    path = _write_records(tmp_path, [{"algorithm": "A", "elapsed_ms": 1}])
    cli.main([str(path)])
    report = json.loads(capsys.readouterr().out)
    assert report["tool"] == "CipherBench"
    assert report["mode"] == "offline-benchmark-analysis"
    assert report["schema_version"] == 1
    assert report["rejected_rows"] == 0
    assert report["known_answers"]["total"] == 0
    assert "notice" in report


def test_cli_writes_the_report_to_the_output_path(tmp_path, capsys):
    path = _write_records(tmp_path, [{"algorithm": "A", "elapsed_ms": 1}])
    output = tmp_path / "report.json"
    code = cli.main([str(path), "--output", str(output)])
    capsys.readouterr()
    assert code == cli.EXIT_OK
    assert json.loads(output.read_text(encoding="utf-8"))["tool"] == "CipherBench"


def test_cli_reports_an_unwritable_output_path_without_a_traceback(tmp_path, capsys):
    path = _write_records(tmp_path, [{"algorithm": "A", "elapsed_ms": 1}])
    output = tmp_path / "missing-directory" / "report.json"
    code = cli.main([str(path), "--output", str(output)])
    captured = capsys.readouterr()
    assert code == cli.EXIT_INVALID_INPUT
    assert "cipherbench:" in captured.err
    assert "Traceback" not in captured.err


def test_cli_fail_on_kat_failure_returns_a_failing_status(tmp_path, capsys):
    path = _write_records(
        tmp_path,
        [{"algorithm": "A", "kat": {"expected_digest": "x", "actual_digest": "y"}}],
    )
    code = cli.main([str(path), "--fail-on-kat-failure"])
    capsys.readouterr()
    assert code == cli.EXIT_INVALID_INPUT


def test_cli_fail_on_kat_failure_succeeds_when_every_known_answer_passes(tmp_path, capsys):
    path = _write_records(
        tmp_path,
        [{"algorithm": "A", "kat": {"expected_digest": "x", "actual_digest": "x"}}],
    )
    code = cli.main([str(path), "--fail-on-kat-failure"])
    capsys.readouterr()
    assert code == cli.EXIT_OK
