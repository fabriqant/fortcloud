.PHONY: help install check validate graph report test clean

PYTHON ?= python
PIP ?= $(PYTHON) -m pip

help:
	@echo "Fortcloud Atlas — commandes disponibles :"
	@echo "  make install   Installe le paquet en mode éditable"
	@echo "  make validate  Valide le modèle d'exemple"
	@echo "  make graph     Génère docs/generated/dependency-graph.md"
	@echo "  make report    Génère docs/generated/resilience-report.md"
	@echo "  make check     Valide et génère les deux artefacts"
	@echo "  make test      Lance les tests unitaires"
	@echo "  make clean     Nettoie les caches Python"

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
