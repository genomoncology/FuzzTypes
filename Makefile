ACTIVATE = . ./activate.sh

format:
	$(ACTIVATE) && ruff format src tests

test:
	$(ACTIVATE) && pytest -s tests/

cov:
	$(ACTIVATE) && coverage run -m pytest -s tests && coverage combine && coverage report --show-missing && coverage html

sync:
	uv pip compile pyproject.toml -o requirements.txt
	uv pip compile pyproject.toml --extra test --extra local --extra ext -o requirements-dev.txt
	uv pip sync requirements-dev.txt
	uv pip install -e ".[dev]"
	uv pip freeze

publish:
	# https://packaging.python.org/en/latest/tutorials/packaging-projects/
	$(ACTIVATE) && python -m build
	$(ACTIVATE) && python -m twine upload -r pypi dist/*

perf_test:
	$(ACTIVATE) && python -m cProfile -o profile.dat -m pytest -s tests/
	python -c "import pstats; pstats.Stats('profile.dat').strip_dirs().sort_stats('tottime').print_stats(25)"

#----------
# clean
#----------

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .cache
	rm -fr .mypy_cache
	rm -fr .pytest_cache
	rm -f .coverage
	rm -fr htmlcov/