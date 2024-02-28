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