.PHONY: help install check validate graph report test clean

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

help:
	@echo "Fortcloud Atlas — available commands:"
	@echo "  make install   Install the package in editable mode"
	@echo "  make validate  Validate the example model"
	@echo "  make graph     Generate docs/generated/dependency-graph.md"
	@echo "  make report    Generate docs/generated/resilience-report.md"
	@echo "  make check     Validate and generate both artifacts"
	@echo "  make test      Run the unit tests"
	@echo "  make clean     Remove Python caches"

install:
	$(PIP) install -e .

validate:
	$(PYTHON) -m fortcloud_atlas validate

graph:
	$(PYTHON) -m fortcloud_atlas graph

report:
	$(PYTHON) -m fortcloud_atlas report

check:
	$(PYTHON) -m fortcloud_atlas check

test:
	$(PYTHON) -m unittest discover -s tests -v

clean:
	$(PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]"
