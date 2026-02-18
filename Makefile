PYTHON = uv run
UV = uv
MAIN_FILES = a_maze_ing.py
CONFIG_FILE = config.txt


all: install run

install:
	@echo "install package"
	$(UV) sync

run:
	@echo "executing maze"
	$(PYTHON) $(MAIN_FILES) $(CONFIG_FILE)

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