PYTHON = python3
PIP = pip
MAIN_FILES = amazing.py

install:
	@echo "install package"
    $(PIP) install -r requirements.txt

run:
	@echo "executing maze"
    $(PYTHON) $(MAIN_FILES)

clean:
	@echo "remove invalid files"
	rm -rf __pycache__

lint:
	@echo "check code quality (--strict - mode)"
	$(PYTHON) -m flake8 . mypy . --strict --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs
