# CipherBench

> A benchmark and interoperability test harness specification for vetted post-quantum cryptographic providers.

**Status:** MVP scaffold / research prototype. Not production-certified.

## Features
- Provider-neutral benchmark record schema.
- Known-answer test fixture format.
- Repeatable latency/throughput summarizer.
- Explicitly avoids custom cryptographic implementations.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
pytest
```

## Safety and scope
The MVP analyzes benchmark JSON supplied by the operator. It does not implement cryptography or claim FIPS validation. Use vetted, standards-conformant providers and official test vectors.

## Roadmap
- [ ] Stable public API and versioned schemas
- [ ] More unit, integration and adversarial tests
- [ ] Reproducible benchmarks and sample datasets
- [ ] Signed releases and dependency review
- [ ] Documentation and contribution guide

## License
MIT. See [LICENSE](LICENSE).
