# Remediation notes — 2026-11

This document records the audit and remediation applied to CipherBench in November 2026.
It is additive: the original README, SECURITY.md, CONTRIBUTING.md and example files
remain in the repository and were updated only where they were inaccurate or
inconsistent.

## Method

Every source file was read line by line and each suspected defect was confirmed with
an executable regression test. The new tests were first run against the previously
published revision to confirm the defect was real (red phase: 24 failing tests), and
only then were the fixes applied (green phase: 29 passing tests, up from 5).

## Defects fixed

| Severity | Defect | Fix |
| --- | --- | --- |
| Medium | The command line raised a raw Python traceback for a missing file or malformed JSON | `cli.main` reports one-line messages and uses exit codes `0` / `1` / `2` |
| Medium | A benchmark file whose root was a JSON object produced a silent, empty summary | The CLI now looks for the `records`, `results`, and `benchmark` keys, and reports a clean error when none of them holds a record list |
| Medium | The README promised a known-answer test fixture format, but the code had no known-answer support | New `verify_known_answers` and `summarize_report` report every vector as `pass`, `fail`, or `incomplete`, and compare digests case-insensitively |
| Low | A blank algorithm name was accepted and grouped under an empty key | Algorithm names are trimmed, and a blank name now rejects the row |
| Low | The summary reported no percentile, so a tail latency could not be reviewed | `percentile` uses the nearest-rank method, and every summary row carries `p95_ms` |
| Low | An entirely invalid input looked the same as an input with no measurements | `summarize_report` reports the `rejected_rows` count |
| Low | A benchmark file exported on Windows with a UTF-8 byte-order mark was rejected as invalid JSON | The CLI decodes the file with `utf-8-sig` |
| Low | A report could not be written to a file, and a CI pipeline had no way to fail on a known-answer failure | `--output` and `--fail-on-kat-failure` options, with an explicit error when the report cannot be written |
| Low | The package exposed no public API, and the report carried no format marker | `cipherbench.__all__`, `cipherbench.__version__`, and `schema_version` in the report |

## Documentation and spelling corrections

- `LICENSE` shipped a truncated MIT text: the warranty and liability paragraphs were
  missing. The complete, canonical MIT text is now in place, and the original
  copyright holder line is preserved.
- Spelling was inconsistent across the same file set. The prose now uses one
  convention throughout: American English. Dated records were left untouched.
- The roadmap listed "Stable public API and versioned schemas" and "Documentation and
  contribution guide" as unfinished while the package exposes `__all__`,
  `__version__`, and a versioned report schema, and while `CONTRIBUTING.md`,
  `SECURITY.md`, and this file exist. The checklist now reflects reality.
- The README documented no command-line usage and no Python API, although the project
  ships a console script and four public functions. Both are now documented, and the
  known-answer fixture format is now described next to the code that reads it.
- A dictionary spelling scan (`codespell`) now reports no misspelling in this
  repository.

## Continuous integration hardening

The workflow previously ran the test suite only. It now also runs a credential scan
on every push and pull request.

| Job | What it does |
| --- | --- |
| `secret-scan` | Runs `scripts/scan-secrets.py`, which fails the build when the repository contains a high-confidence credential pattern (cloud keys, tokens, private key blocks, JWTs) or a file that must never be committed (`.env`, `*.pem`, `*.key`, `*.p12`, `id_rsa`, credential files) |

The scanner is the one already used by the Gravion Toolkit split repositories, so
every toolkit project now shares one definition of what counts as a secret. A
"soft" match, such as a dummy `api_key` inside a test fixture, is reported for
review but does not fail the build.

## Verification

| Check | Before | After |
| --- | --- | --- |
| Secret scan in CI | absent | present |
| Tests | 24 failing in the red phase | 29 passing |
| Known-answer verification | absent | `verify_known_answers` with `pass` / `fail` / `incomplete` |
| Summary percentile | none | `p95_ms`, nearest rank |
| Invalid rows | dropped without a count | `rejected_rows` count in the report |
| JSON object root | silent empty summary | record list read from `records`, `results`, or `benchmark`, otherwise a clean error |
| CLI failure modes | traceback | one-line message, exit code `0` / `1` / `2` |
| Public API | none | `__all__` and `__version__` `0.2.0` |
| Report format marker | none | `schema_version: 1` |

## Residual limitations

- CipherBench does not implement cryptography. It never contacts a provider endpoint
  and it claims no FIPS validation; a provider's conformance has to be established
  elsewhere.
- A known-answer check only compares the digests already present in the input file.
  It does not recompute a digest, so it cannot tell a wrong digest from a wrong
  expectation.
- The summarizer trusts the supplied `elapsed_ms` values. It does not normalize
  units, and an outlier recorded as a valid number is reported as a valid number.
- The report describes the input file only. It says nothing about hardware, provider,
  configuration, or workload, and it is not a reproducible benchmark result.
- Rows that are not measurement records are ignored by `summarize`; only
  `summarize_report` counts them as rejected rows.
