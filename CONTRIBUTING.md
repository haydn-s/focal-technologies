# Working on the Focal repository

Each demo is a separate product experiment. Keep its entry point, dependencies, tests, scope, and prompt log together under `prototypes/`. Shared research belongs in `docs/`; original brand artwork belongs in `assets/brand/`.

## Set up a local environment

From the repository root, with Python 3.11 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` to activate. For work on one demo, install its adjacent `requirements.txt` instead of the combined file. Separate virtual environments are also supported when demos need different dependencies.

## Run the demos

Start each app from the repository root, in its own terminal:

```bash
python -m streamlit run prototypes/prototype-a-riley-vision-tracking/app.py --server.port 8501
python -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502
python -m streamlit run prototypes/prototype-c-alex-dmv-precheck/app.py --server.port 8503
```

On macOS/Linux, `make demo-a`, `make demo-b`, and `make demo-c` provide the same commands. Use `make help` for the available shortcuts. With no activated environment, use commands such as `make PYTHON=.venv/bin/python test`.

Keep the existing demo directory names stable: they are also deployment entry points. Use paths relative to `__file__` for file loading so behavior is consistent when launching from the repository root. Shared brand files are at `Path(__file__).resolve().parents[2] / "assets" / "brand"`.

## Test changes

With the environment active, `make test` runs each demo's suite in a separate process. `make test-a`, `make test-b`, and `make test-c` run one suite. On any platform, the equivalent for one demo is:

```bash
cd prototypes/prototype-b-parent-guided-check
python -m unittest discover -p 'test_*.py'
```

Run the tests from that demo's directory. A and C import their own `app.py`, so combining all suites in one Python process would create module-name collisions. B also imports its local `demo.py`.

The [GitHub Actions workflow](.github/workflows/tests.yml) installs each demo's own requirements and runs its tests independently on Python 3.12. It runs on pushes and pull requests and can also be started manually. GitHub's [Python workflow guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python) documents the setup and package caching used here.

## Place new material

| Material | Location |
| --- | --- |
| Customer interviews and discovery presentations | `docs/research/customer-discovery/` |
| Competitive analysis | `docs/research/competitive-landscape/` |
| Lean Canvas and business model work | `docs/strategy/` |
| Assignment briefs and completed phase workbooks | `docs/assignments/` |
| Original logo variants | `assets/brand/` |
| A demo's own sample data and images | Inside that demo's directory |

Use descriptive filenames and add a link to the [document index](docs/README.md). Preserve edited versions and PDF exports when they serve different purposes. Consolidate copies only when their bytes are identical. Prompt logs preserve the original wording and may refer to the folders used before the reorganization.

## Add another prototype

Use the existing layout:

```text
prototypes/prototype-<letter>-<focus>/
  app.py
  requirements.txt
  README.md
  PROMPT_LOG.md
  test_*.py
```

Record its persona, hypothesis, Feature Scope Card, demo journey, and actual build prompts. Add its requirements to `requirements-dev.txt`, its run/test shortcuts to `Makefile`, and its directory to the workflow matrix and root prototype table. Choose an unused local port and publish it as a separate Streamlit app following the [deployment guide](docs/deployment.md).

Import shared functions only when a concrete need emerges. Keep app entry points independent; importing another demo's `app.py` can mix page configuration and session state.
