.PHONY: install test check strict clean

install:
	python -m pip install -e .

test:
	python -m unittest discover -s tests -v

check:
	fortcloud-ark check --out ./docs/generated

strict:
	fortcloud-ark check --strict --out ./docs/generated

clean:
	rm -rf docs/generated artifacts
