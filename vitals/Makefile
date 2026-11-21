.PHONY: install test check strict clean

install:
	python -m pip install -e .

test:
	python -m unittest discover -s tests -v

check:
	fortcloud-vitals check --out ./docs/generated

strict:
	fortcloud-vitals check --strict --out ./docs/generated

clean:
	rm -rf docs/generated artifacts
