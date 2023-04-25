TODAY := $(shell date "+%Y-%m-%dT%H-%M-%S" -u)
VENV := venv
BIN := $(VENV)/bin
PYTHON_VER := python3.10
GIT_PACKAGE := $(VENV)/lib/$(PYTHON_VER)/site-packages/git/__init__.py
.DEFAULT_GOAL := all

$(BIN)/pip:
	$(PYTHON_VER) -m venv $(VENV)
	touch $@

$(GIT_PACKAGE): requirements.txt $(BIN)/pip
	$(BIN)/pip install -r requirements.txt
	touch $@

README.md: $(GIT_PACKAGE)
	$(BIN)/python update_readme.py

.PHONY: commit
commit: README.md
	git diff --quiet || (git add README.md && git commit -m "Update README")
	git push

.PHONY: all
all: commit
