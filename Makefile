PYTHON := .venv/bin/python

.PHONY: data marts diagnostics experiments figures test lint all

data:
	$(PYTHON) -m src.ingestion.download_data
	$(PYTHON) -m src.ingestion.build_event_database

marts: data
	$(PYTHON) -m src.ingestion.build_analytics_marts
	$(PYTHON) -m src.ingestion.build_opportunity_marts
	$(PYTHON) -m src.ingestion.build_robustness_marts

diagnostics: marts
	$(PYTHON) -m src.analysis.cart_completion_model

experiments: diagnostics
	$(PYTHON) -m src.experimentation.validate_design
	$(PYTHON) -m src.experimentation.simulate_experiment --scenario healthy
	$(PYTHON) -m src.experimentation.simulate_experiment --scenario srm
	$(PYTHON) -m src.experimentation.analyze_experiment --scenario healthy
	$(PYTHON) -m src.experimentation.analyze_experiment --scenario srm

figures: experiments
	$(PYTHON) -m src.reporting.build_figures

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

all: figures test lint
