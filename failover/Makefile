.PHONY: install test check report clean

install:
	python -m pip install -e .

test:
	python -m unittest discover -s tests -v

check:
	fortcloud-failover check --out ./docs/generated

strict:
	fortcloud-failover check --strict --out ./docs/generated

clean:
	rm -rf docs/generated artifacts
