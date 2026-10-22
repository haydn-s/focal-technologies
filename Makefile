PYTHON ?= python

.PHONY: install demo-a demo-b test test-a test-b

install:
	$(PYTHON) -m pip install -r requirements-dev.txt

demo-a:
	$(PYTHON) -m streamlit run prototypes/prototype-a-riley-vision-tracking/app.py --server.port 8501

demo-b:
	$(PYTHON) -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502

test: test-a test-b

# Existing A tests resolve app.py relative to their own directory.
# An absolute interpreter path also supports `make PYTHON=.venv/bin/python test`.
test-a:
	cd prototypes/prototype-a-riley-vision-tracking && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'

test-b:
	cd prototypes/prototype-b-parent-guided-check && "$(abspath $(shell command -v $(PYTHON)))" -m unittest discover -p 'test_*.py'
