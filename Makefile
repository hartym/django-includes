PACKAGE ?= django_includes
PYTHON ?= $(shell which python || echo python)
PYTHON_BASENAME ?= $(shell basename $(PYTHON))
PYTHON_DIRNAME ?= $(shell dirname $(PYTHON))
PYTHON_REQUIREMENTS_FILE ?= requirements.txt
PYTHON_REQUIREMENTS_INLINE ?= 
PYTHON_REQUIREMENTS_DEV_FILE ?= requirements-dev.txt
PYTHON_REQUIREMENTS_DEV_INLINE ?= 
QUICK ?= 
PIP ?= $(PYTHON) -m pip
PIP_INSTALL_OPTIONS ?= 
VERSION ?= $(shell git describe 2>/dev/null || git rev-parse --short HEAD)
BLACK ?= $(shell which black || echo black)
BLACK_OPTIONS ?= --line-length 120
ISORT ?= $(PYTHON) -m isort
ISORT_OPTIONS ?= --recursive --apply
PYTEST ?= $(PYTHON_DIRNAME)/pytest
PYTEST_OPTIONS ?= --capture=no --cov=$(PACKAGE) --cov-report html

POETRY ?= $(shell which poetry || echo poetry)

.PHONY: clean format help install install-dev medikit quick test update update-requirements

install:  ## Installs the project.
	$(POETRY) install

install-dev:  ## Installs the project (with dev dependencies).
	$(POETRY) install --with dev

clean:  ## Cleans up the working copy.
	rm -rf build dist *.egg-info
	find . -name __pycache__ -type d | xargs rm -rf

format: install-dev  ## Reformats the codebase (with black, isort).
	$(BLACK) $(BLACK_OPTIONS) .
	$(ISORT) $(ISORT_OPTIONS) .

test: install-dev  ## Runs the test suite.
	$(PYTEST) $(PYTEST_OPTIONS) tests

medikit:   # Checks installed medikit version and updates it if it is outdated.
	@$(PYTHON) -c 'import medikit, pip, sys; from packaging.version import Version; sys.exit(0 if (Version(medikit.__version__) >= Version("$(MEDIKIT_VERSION)")) and (Version(pip.__version__) < Version("10")) else 1)' || $(PYTHON) -m pip install -U "pip ~=19.0,<19.2" "medikit>=$(MEDIKIT_VERSION)"

update: medikit  ## Update project artifacts using medikit.
	$(MEDIKIT) update $(MEDIKIT_UPDATE_OPTIONS)

update-requirements:   ## Update project artifacts using medikit, including requirements files.
	MEDIKIT_UPDATE_OPTIONS="--override-requirements" $(MAKE) update

help:   ## Shows available commands.
	@echo "Available commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?##[\s]?.*$$' --no-filename $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?##"}; {printf "    make \033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo
