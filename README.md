# CipherBench

> A benchmark and interoperability test harness specification for vetted post-quantum cryptographic providers.

**Status:** MVP scaffold / research prototype. Not production-certified.

## Features
- Summarize benchmark records per algorithm: sample count, median, minimum, maximum, and a nearest-rank `p95_ms`.
- Reject unusable rows (blank algorithm names, non-numeric, negative or non-finite elapsed times) and report the rejected-row count, so "no measurements" stays distinguishable from "no valid input".
- Verify known-answer tests (KAT) and report each vector as `pass`, `fail`, or `incomplete`, comparing digests case-insensitively.
- Read a JSON array of records, or a JSON object that wraps them under `records`, `results`, or `benchmark`.
- Emit a machine-readable JSON report with a `schema_version` field for CI pipelines.
- Report input problems as one-line messages with stable exit codes instead of Python tracebacks.
- Explicitly avoids custom cryptographic implementations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest
```

## Command-line usage

```bash
cipherbench records.json
cipherbench records.json --output report.json
cipherbench records.json --fail-on-kat-failure
```

| Option | Meaning |
| --- | --- |
| `records` | Required positional argument: the benchmark records JSON file |
| `--output PATH` | Write the JSON report to `PATH` in addition to printing it |
| `--fail-on-kat-failure` | Exit with status `1` when at least one known-answer test fails |

| Exit code | Meaning |
| --- | --- |
| `0` | The records were analyzed and no error occurred |
| `1` | The file could not be parsed, the report could not be written, or a known-answer test failed with `--fail-on-kat-failure` |
| `2` | The file is missing or unreadable, or the command line was not valid |

The report is JSON and carries `tool`, `mode`, `schema_version`, `summary`, `rejected_rows`, `known_answers`, and a `notice`, so downstream tooling can detect format changes.

### Input format

A measurement record carries an algorithm name and an elapsed time in milliseconds:

```json
{"algorithm": "AES-256-GCM", "elapsed_ms": 1.5}
```

A known-answer record adds a `kat` object with the expected and the actual digest:

```json
{"algorithm": "AES-256-GCM", "kat": {"name": "vector-1", "expected_digest": "<sha256 hex>", "actual_digest": "<sha256 hex>"}}
```

A vector without both digests is reported as `incomplete`. A vector whose digests differ is reported as `fail`, which means the provider did not reproduce the expected output.

## Python API

```python
from cipherbench import percentile, summarize, summarize_report, verify_known_answers

rows = [{"algorithm": "AES-256-GCM", "elapsed_ms": 1.5}]

summary = summarize(rows)          # one row per algorithm
report = summarize_report(rows)    # summary + rejected_rows + known_answers
kat = verify_known_answers(rows)   # pass / fail / incomplete per vector
p95 = percentile([1, 2, 3, 4], 95) # nearest-rank percentile
```

The package exports a stable public API (`cipherbench.__all__`) and reports its version as `cipherbench.__version__` (`0.2.0`).

## Safety and scope
The MVP analyzes benchmark JSON supplied by the operator. It does not implement cryptography or claim FIPS validation. Use vetted, standards-conformant providers and official test vectors.

## Roadmap
- [x] Stable public API and versioned schemas
- [x] More unit, integration and adversarial tests (29 passing)
- [ ] Reproducible benchmarks and sample datasets
- [ ] Signed releases and dependency review
- [x] Documentation and contribution guide

## License
MIT. See [LICENSE](LICENSE). The LICENSE file now carries the complete MIT text, including the warranty and liability clauses.
