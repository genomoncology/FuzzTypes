ACTIVATE = . ./activate.sh

format:
	$(ACTIVATE) && ruff format src tests

test:
	$(ACTIVATE) && pytest -s tests/

cov:
	$(ACTIVATE) && coverage run -m pytest -s tests && coverage combine && coverage report --show-missing && coverage html
