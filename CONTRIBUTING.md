# Contributing

Thanks for your interest in improving Temporal Graph RAG.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=src
```

## Run tests

```bash
pytest -q
```

## Run benchmarks

```bash
python benchmarks/temporal_hotpot.py --samples 50 --visualize
```

## Pull requests

- Keep changes focused and small when possible.
- Add or update tests for behavioral changes.
- Update the README if you change usage or API behavior.

## Code style

- Keep functions small and readable.
- Prefer descriptive names over long comments.
