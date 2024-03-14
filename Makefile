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

	echo "** Slowest FuzzTypes functions by total time:"
	$(ACTIVATE) && python -c "import pstats; pstats.Stats('profile.dat').sort_stats('tottime').print_stats(1000)" | grep -E "ncalls|/src/" | head -n 21

	echo "\n\n** Slowest FuzzTypes functions by cumulative time:"
	$(ACTIVATE) && python -c "import pstats; pstats.Stats('profile.dat').sort_stats('cumtime').print_stats(1000)" | grep -E  "ncalls|/src/" | head -n 21

	echo "\n\n** Slowest all-project functions by total time:"
	$(ACTIVATE) && python -c "import pstats; pstats.Stats('profile.dat').sort_stats('tottime').print_stats(20)" | tail -n +8

	rm profile.dat

pbcopy:
	# copy all code to clipboard for pasting into an LLM
	find . ! -path '*/.*/*' -type f \( -name "*.py" -o -name "*.md" \) -exec tail -n +1 {} + | pbcopy

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