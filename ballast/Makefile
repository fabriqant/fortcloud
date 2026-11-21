.PHONY: install test check strict clean

install:
	python -m pip install -e .

test:
	python -m unittest discover -s tests -v

check:
	fortcloud-ballast check --out ./docs/generated

strict:
	fortcloud-ballast check --strict --out ./docs/generated

clean:
	rm -rf docs/generated artifacts
