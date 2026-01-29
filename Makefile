.PHONY: api test bench latency diagram

VENV_PY := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

api:
	$(VENV_PY) -m uvicorn temporal_graph_rag.api.main:app --reload --port 8000

test:
	PYTHONPATH=src $(VENV_PY) -m pytest -q

bench:
	PYTHONPATH=src $(VENV_PY) benchmarks/temporal_hotpot.py --samples 50 --visualize

latency:
	PYTHONPATH=src $(VENV_PY) benchmarks/latency_profile.py --samples 80 --out assets/latency_profile.png

diagram:
	./scripts/render_architecture.sh assets/architecture.mmd assets/architecture.png
