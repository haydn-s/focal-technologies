# Publishing the Focal demos

Publish each demo as an independent Streamlit Community Cloud app from this repository. Each app has its own URL, entry point, requirements file, and user sessions.

## Deployment entry points

Use the repository `haydn-s/focal-technologies` and a branch containing the intended version, normally `main` after the work is merged.

| Demo | Main file path | Requirements | Local port |
| --- | --- | --- | --- |
| A · Focal Monitor | `prototypes/prototype-a-riley-vision-tracking/app.py` | `prototypes/prototype-a-riley-vision-tracking/requirements.txt` | 8501 |
| B · Focal Family | `prototypes/prototype-b-parent-guided-check/app.py` | `prototypes/prototype-b-parent-guided-check/requirements.txt` | 8502 |
| C · Focal DMV Pre-Check | `prototypes/prototype-c-alex-dmv-precheck/app.py` | `prototypes/prototype-c-alex-dmv-precheck/requirements.txt` | 8503 |

1. Push the intended version to GitHub and run its tests.
2. Create one Cloud app for each row, selecting the repository, branch, and main file path.
3. Use Python 3.12 for consistency with the automated checks.
4. Open each deployed link in a fresh browser session and complete its main journey.
5. Confirm that classmates can access the links, then record them below for submission.

The adjacent `requirements.txt` keeps dependency installation separate for each app. `requirements-dev.txt` is only a convenience for installing all three locally. Streamlit's [file organization guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization) and [deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) describe this setup.

## Shared files

Community Cloud runs from the repository root. Launch locally from the root as well, and resolve shared file paths relative to the app's source file. Original logos are in `assets/brand/`; Demo B uses `assets/brand/focal-lockup.svg`.

If adding `.streamlit/config.toml`, place it at the root and coordinate changes across the team: apps on the same repository branch share that configuration. Keep each app's dependencies next to its entry point. Put deployed secrets in Streamlit's settings; local `.streamlit/secrets.toml` files are ignored by Git.

## Shared links

| Demo | Published URL |
| --- | --- |
| A | [Focal Monitor](https://focal-demo-a.streamlit.app/) |
| B | [Focal Family](https://focal-demo-b.streamlit.app/) |
| C | [Focal DMV Pre-Check](https://focal-demo-c.streamlit.app/) |

Haydn supplied these URLs on October 21, 2026. All three public landing pages loaded during presentation preparation. Complete the main journeys in fresh public sessions during the two human rehearsals before class.

Local addresses such as `http://localhost:8502` are previews on the developer's computer. The assignment requires accessible deployed links for all three demos.
