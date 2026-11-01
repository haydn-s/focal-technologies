PYTHON ?= python

.DEFAULT_GOAL := help

.PHONY: help install demo-a demo-b demo-c demo-family test test-a test-b test-c test-family

help:
	@printf '%s\n' 'make install  Install dependencies for all three demos' 'make demo-a   Run Focal Monitor on port 8501' 'make demo-b   Run Focal Family on port 8502' 'make demo-c   Run Focal DMV Pre-Check on port 8503' 'make demo-family  Run the Focal Family master prototype on port 8504' 'make test     Run every independent test suite' 'make test-a   Run only Demo A tests (also test-b, test-c, test-family)' 'Use PYTHON=.venv/bin/python when the environment is not activated.'

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

demo-a:
	$(PYTHON) -m streamlit run prototypes/prototype-a-riley-vision-tracking/app.py --server.port 8501

demo-b:
	$(PYTHON) -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502

demo-c:
	$(PYTHON) -m streamlit run prototypes/prototype-c-alex-dmv-precheck/app.py --server.port 8503

demo-family:
	$(PYTHON) -m streamlit run prototypes/focal-family/app.py --server.port 8504

test: test-a test-b test-c test-family

# Existing A tests resolve app.py relative to their own directory.
# An absolute interpreter path also supports `make PYTHON=.venv/bin/python test`.
test-a:
	cd prototypes/prototype-a-riley-vision-tracking && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'

test-b:
	cd prototypes/prototype-b-parent-guided-check && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'

test-c:
	cd prototypes/prototype-c-alex-dmv-precheck && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'

test-family:
	cd prototypes/focal-family && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'
