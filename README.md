# Focal Technologies prototypes

Three independent Streamlit product experiments for Duke MENG 570. Each demo has its own entry point, dependencies, tests, hypothesis, and prompt log, and can be developed and deployed separately.

## Choose a demo

| Demo | Persona | Product question | Workspace | Local preview |
| --- | --- | --- | --- | --- |
| A · Focal Monitor | Routine-Check Riley | Is ongoing vision tracking more useful than an isolated result? | [Demo A](prototypes/prototype-a-riley-vision-tracking/README.md) | [Port 8501](http://localhost:8501) |
| B · Focal Family | Parent Pat | Will a picture activity and observation summary help parents choose a follow-up step? | [Demo B](prototypes/prototype-b-parent-guided-check/README.md) | [Port 8502](http://localhost:8502) |
| C · Focal DMV Pre-Check | Anxious Applicant Alex | Is a state-specific pre-check with next steps more useful before a DMV visit than a general score? | [Demo C](prototypes/prototype-c-alex-dmv-precheck/README.md) | [Port 8503](http://localhost:8503) |

A's internal result-format comparison is part of Demo A. Focal Family is the separate team Demo B.

## Quick start

From the repository root, with Python 3.11 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead. Start a demo using its corresponding command:

```bash
python -m streamlit run prototypes/prototype-a-riley-vision-tracking/app.py --server.port 8501
python -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502
python -m streamlit run prototypes/prototype-c-alex-dmv-precheck/app.py --server.port 8503
```

Run each command in a separate terminal to use the demos simultaneously. On macOS/Linux, `make demo-a`, `make demo-b`, and `make demo-c` are equivalent. `make test` runs all three suites independently; `make help` lists the shortcuts.

## Repository layout

```text
prototypes/                 Independent apps, tests, scope cards, and prompt logs
  prototype-a-riley-vision-tracking/
  prototype-b-parent-guided-check/
  prototype-c-alex-dmv-precheck/
assets/brand/               Shared original logos
docs/                      Research library, strategy, and course assignments
  research/
    customer-discovery/
    competitive-landscape/
  strategy/
  assignments/
  deployment.md
.github/workflows/          Automated checks for each app
CONTRIBUTING.md             Development and file-placement conventions
Makefile                    Local run and test shortcuts
requirements-dev.txt        Combined installation for local development
```

## Project guides

- [Document library](docs/README.md): research, Lean Canvas, business model, and phase workbooks. This consolidates the former `fundamentals` and `Focal Knowledge Base` directories.
- [Brand assets](assets/brand/README.md): the team's original logo files.
- [Development guide](CONTRIBUTING.md): setup, testing, and adding another demo.
- [Team prompt log](prompts.md): build prompts and outcomes for A, B, and C, with shared repository work recorded separately.
- [Deployment guide and shared links](docs/deployment.md): publish three apps from this repository, each with its own URL.
- [Prototype assignment](docs/assignments/prototype-assignment.md): the supplied brief and deliverable requirements.

Keep each demo's requirements beside its `app.py`. Keep the current prototype directory names when publishing updates so existing deployment paths remain stable.

## Before presenting

Confirm each prototype works without a guided explanation, has a distinct hypothesis and Feature Scope Card, and has at least five actual prompts in the [team prompt log](prompts.md). Rehearse each demo twice, check its published URL from a fresh session, and submit the links and presentation to Canvas. Record the class vote and the team's response for the remaining semester work.

## License

[Apache License 2.0](LICENSE).
