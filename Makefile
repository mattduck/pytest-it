bootstrap:
	pip install black flake8 tox

install:
	python setup.py install

clean:
	rm -rf build dist pytest_it.egg-info

test:
	tox

_lintblack:
	set -o pipefail && black . --check 2>&1 | sed "s/^/[black] /"

_lintflake8:
	set -o pipefail && flake8 pytest_it tests | sed "s/^/[flake8] /"

lint: _lintblack _lintflake8

format:
	black .

.PHONY: bootstrap install test lint _lintblack _lintflake8
