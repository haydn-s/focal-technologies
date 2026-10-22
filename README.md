# Focal Technologies prototypes

Interactive product experiments for Duke MENG 570. Each prototype is an independent Streamlit app in this repository, with its own entry point, dependencies, documentation, and prompt log. Teammates can develop and publish their demos separately.

## Prototype directory

| Demo | Persona | Approach and hypothesis | Workspace | Status |
| --- | --- | --- | --- | --- |
| A · Focal Monitor | Routine-Check Riley | Adults concerned about vision changes will find ongoing tracking more useful than an isolated demonstration result. | [Prototype A](prototypes/prototype-a-riley-vision-tracking/) | Existing demo |
| B · Focal Family | Parent Pat | Parents will complete a short picture activity and use an observation summary to choose a concrete follow-up step. | [Prototype B](prototypes/prototype-b-parent-guided-check/) | Initial working concept · Haydn |
| C | To be selected | A third distinct hypothesis is still needed. | [Prototype C](prototypes/prototype-c/) | Reserved |

Prototype A's internal “Experience A / Experience B” comparison belongs entirely to Prototype A. **Focal Family is the team's separate Prototype B.**

## Repository structure

```text
fundamentals/                             Shared research and original brand assets
prototypes/
  prototype-a-riley-vision-tracking/        Existing teammate demo
    app.py
    requirements.txt
    README.md
    PROMPT_LOG.md
    test_*.py
  prototype-b-parent-guided-check/         Haydn's demo
    app.py                                Streamlit interface
    demo.py                               Activity state and exports
    requirements.txt
    README.md
    PROMPT_LOG.md
    test_demo.py
  prototype-c/                            Reserved for the third demo
Makefile                                  Optional development shortcuts
requirements-dev.txt                      Installs all current apps for local work
```

Keep each demo's assets and sample data inside its own folder. Add new shared research to `fundamentals/` as it becomes available. Demo B reads the existing Focal logo from that directory and resolves its path relative to its source file.

## Local setup

From the repository root, using Python 3.11 or newer:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead.

Start each demo in a separate terminal from the repository root:

```bash
# Demo A → http://localhost:8501
python -m streamlit run prototypes/prototype-a-riley-vision-tracking/app.py --server.port 8501
```

```bash
# Demo B → http://localhost:8502
python -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502
```

On macOS/Linux, `make demo-a` and `make demo-b` are equivalent after activating the environment. Both apps can run simultaneously on these separate ports.

For a smaller installation, install only `prototypes/<your-demo>/requirements.txt`. If dependency versions eventually conflict, create a separate virtual environment inside each prototype directory.

## Publish separate shared links

Streamlit Community Cloud supports multiple apps from one repository. Create one deployment per demo, using the same repository and the branch containing your work:

| Deployment | Main file path | Dependency file |
| --- | --- | --- |
| Demo A | `prototypes/prototype-a-riley-vision-tracking/app.py` | `prototypes/prototype-a-riley-vision-tracking/requirements.txt` |
| Demo B | `prototypes/prototype-b-parent-guided-check/app.py` | `prototypes/prototype-b-parent-guided-check/requirements.txt` |

Each deployment receives its own URL. Record the actual links below after publishing; local demos alone do not meet the assignment's shared-link requirement.

| Demo | Published link |
| --- | --- |
| A | Not recorded |
| B | Not deployed |
| C | Not built |

Streamlit uses the requirements file beside each entry point for separate dependencies. The root `requirements-dev.txt` is a local convenience file. Community Cloud runs from the repository root, so the local launch commands above start there as well. If adding `.streamlit/config.toml`, place it at the root and coordinate changes because that configuration is shared by apps on the same branch. Keep secrets out of source control.

See Streamlit's official [file organization guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) and [deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Tests

With the virtual environment active, use `make test` on macOS/Linux to run both suites. On any platform, run each suite independently inside its own prototype directory:

```bash
cd prototypes/prototype-a-riley-vision-tracking
python -m unittest discover -p 'test_*.py'
```

```bash
# Starting from the repository root:
cd prototypes/prototype-b-parent-guided-check
python -m unittest discover -p 'test_*.py'
```

The existing A tests use a local `app` import and relative entry-point paths. Separate test processes also avoid collisions between multiple `app.py` files.

## Assignment checklist

- Three functional, clickable prototypes that people can use without a guided explanation.
- Three distinct, explicit hypotheses grounded in the personas and research. Changing colors alone does not count.
- A Feature Scope Card per prototype covering value, effort, complexity, success signal, and deliberate cuts.
- At least five actual prompts per prototype, recorded with intent and learning in its `PROMPT_LOG.md`. B currently has two recorded user prompts; continue the log as the concept develops.
- A working, accessible shared link for each prototype, checked from a fresh browser session.
- Presentation: problem and evolution (up to two minutes), versions and hypotheses (about two minutes each), live demos (about two minutes each), and prioritization and strategy justification.
- Rehearse each demo twice. Submit the links and presentation material to Canvas before presentation day.
- Record the class vote and the team's evidence-based response for the remaining semester work.

## Adding Demo C

Choose its persona and hypothesis, then add `app.py`, `requirements.txt`, `README.md`, and `PROMPT_LOG.md` inside `prototypes/prototype-c/`. Add its requirements to `requirements-dev.txt` for the combined local setup, launch it on port 8503, and give it a separate Cloud deployment. Avoid importing either other demo's `app.py`; extract reusable functions only when there is a concrete shared need.

## License

[Apache License 2.0](LICENSE).
