PYTHON ?= python

.PHONY: install demo-a demo-b demo-c test test-a test-b test-c

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

demo-a:
	$(PYTHON) -m streamlit run prototypes/prototype-a-riley-vision-tracking/app.py --server.port 8501

demo-b:
	$(PYTHON) -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502

demo-c:
	$(PYTHON) -m streamlit run prototypes/prototype-c-alex-dmv-precheck/app.py --server.port 8503

test: test-a test-b test-c

# Existing A tests resolve app.py relative to their own directory.
# An absolute interpreter path also supports `make PYTHON=.venv/bin/python test`.
test-a:
	cd prototypes/prototype-a-riley-vision-tracking && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'

test-b:
	cd prototypes/prototype-b-parent-guided-check && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'

test-c:
	cd prototypes/prototype-c-alex-dmv-precheck && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'
