PYTHON = uv run
UV = uv
MAIN_FILES = amazing.py


all: install run

install:
	@echo "install package"
	$(UV) sync

run:
	@echo "executing maze"
	$(PYTHON) $(MAIN_FILES)

clean:
	@echo "remove invalid files"
	rm -rf __pycache__ .venv .uv

lint:
	@echo "check code quality (--strict - mode)"
	flake8 . --exclude .venv
	mypy . --strict --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

lint-strict:
	@echo "check (--strict -mode)"
	flake8 . --exclude .venv
	mypy . --strict --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs