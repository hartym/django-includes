# This file has been auto-generated.
# All manual changes may be lost, see Projectfile.
#
# Date: 2016-06-16 09:24:38.951093

PYTHON ?= $(shell which python)
PYTHON_BASENAME ?= $(shell basename $(PYTHON))
PYTHON_REQUIREMENTS_FILE ?= requirements.txt
QUICK ?= 
VIRTUAL_ENV ?= .virtualenv-$(PYTHON_BASENAME)
PIP ?= $(VIRTUAL_ENV)/bin/pip
PYTEST_OPTIONS ?= --capture=no --cov=django_includes --cov-report html

.PHONY: clean install install-dev lint test

# Installs the local project dependencies.
install: $(VIRTUAL_ENV)
	if [ -z "$(QUICK)" ]; then \
	    $(PIP) install -Ur $(PYTHON_REQUIREMENTS_FILE) ; \
	fi

# Setup the local virtualenv.
$(VIRTUAL_ENV):
	virtualenv -p $(PYTHON) $(VIRTUAL_ENV)
	$(PIP) install -U pip\>=8.0,\<9.0 wheel\>=0.24,\<1.0
	ln -fs $(VIRTUAL_ENV)/bin/activate activate-$(PYTHON_BASENAME)

clean:
	rm -rf $(VIRTUAL_ENV)

lint: install-dev
	$(VIRTUAL_ENV)/bin/pylint --py3k django_includes -f html > pylint.html

test: install-dev
	$(VIRTUAL_ENV)/bin/py.test $(PYTEST_OPTIONS) tests

install-dev: $(VIRTUALENV_PATH) $(WHEELHOUSE)
	if [ -z "$(QUICK)" ]; then \
	    $(PIP) install -Ue "file://`pwd`#egg=django_includes[dev]"; \
	fi
