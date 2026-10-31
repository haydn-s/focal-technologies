# Focal Family

Focal Family is a Streamlit prototype for parents of children aged 4–10. It combines a parent activity and editable observation note with a new experimental direction-matching task and performance history. The upgrade lives on `focal-family-updates`, branched from `executive-pitch` so the revised investor deck and product stay aligned.

## Three workspaces

| Workspace | What works now | Output |
| --- | --- | --- |
| Parent activity | Practice, six picture matches, pause/resume, observations, a chosen next step and editable questions/message | Parent summary and message exports |
| Live vision check | Child label, eye choice, usual correction, screen label, card-width calibration, measured distance, practice, 12 randomized direction responses across three sizes, pause/resume | Per-size task accuracy, completed-check save |
| Performance history | Saved checks, child/setup filters, rolling 7/30/90-day or all-time views, comparison with the previous equal window | Chart, dated table, window CSV, portable JSON history and restore |

The `20/80`, `20/40` and `20/20` labels describe the E's angular size geometry. **They are not measured acuity or a clinical result.** The task is experimental. Attention, assistance, guessing, learning and self-reported setup can change performance. Neither a high score nor an upward trend rules out an eye problem or cancels a professional referral. The app does not diagnose, prescribe or decide whether a child needs care.

## Live task and setup

The parent selects a child label (A, B or C), eyes used (both/right/left), usual correction and screen setup label. They match an on-screen bar to an 85.6 mm-wide card without uploading any card information, and measure a 1.5 m or 3 m viewing distance. Browser zoom and display settings must stay unchanged after matching. If testing one eye, the other should be comfortably covered without pressure.

The E uses a five-unit SVG path with randomized orientations. Physical size is calculated from five arcminutes at 20/20 geometry, scaled by the selected size denominator and viewing distance, then converted to CSS pixels from the reference bar. This is a sizing model, not validated clinical calibration. Fixed size rendering avoids shrinking the symbol responsively. On small screens, the wide reference bar can scroll horizontally.

Practice must complete before the 12 recorded responses. Each of three sizes has four trials. “Can't tell” counts as an incorrect response, so every completed check has the same denominator. Pause preserves the next unanswered trial. A stale double-click cannot count twice. Incomplete or discarded checks cannot enter history.

## History and data boundaries

- Saving adds a completed live check once to this browser session's history. Starting another check or resetting the parent activity preserves saved checks.
- Refresh or reconnection can end the Streamlit session. **Download history JSON to keep it, then restore that file on a later visit.** There are no accounts, browser-local database or shared server database.
- History comparisons require the same child, eye, correction, screen label, distance, calibration width and protocol. A different setup creates a separate series. Actual device identity is self-reported, not verified.
- Windows use UTC timestamps. The current window includes its starting boundary; the preceding equal window excludes that boundary. With no prior observations, the change metric stays empty. “All time” has no preceding-window comparison.
- Restore validates the complete file before merging, rejects future/incomplete/unknown-protocol records, and deduplicates identical IDs. A conflicting ID rejects the import. Maximum file size is 5 MB and maximum combined history is 2,000 checks. Import does not authenticate who performed a check.
- **Fictional example history is opt-in and separate.** Its dates and responses are made up. It never enters live history or the live JSON export. Its CSV carries a fictional source label.
- Clear history requires an explicit confirmation checkbox. Keep an exported copy if needed. Parent free-text inputs should omit identifying information.

The parent activity's summary and feedback exports remain separate from the task-history JSON. An editable message is a draft. No message is sent and no appointment is booked.

## Evidence and clinical boundaries

The [discovery workbook](../../docs/research/customer-discovery/interview-workbook.docx) contains one real parent interview. That parent described examination scheduling friction and already kept historical records. This supports investigating a useful parent workflow, not a clinical measurement claim or proven willingness to pay. Five AI interviews generate hypotheses rather than customer validation.

The testing/history work is a new product experiment requested on October 30, 2026. Its success questions are whether parents understand the setup, complete the task without help, distinguish task performance from vision health, and use their history and note in a real conversation. Usability, same-setup repeatability, accuracy against professional assessment, completed follow-up and buyer demand require separate evidence.

Clinical context: the [AAO/AAPOS screening statement](https://www.aao.org/education/clinical-statement/vision-screening-infants-children-2022) describes age-appropriate methods and trained screening. The [2025 preschool recommendations](https://pmc.ncbi.nlm.nih.gov/articles/PMC12520030/) explain that optotype choice and chart layout affect screening performance. This isolated Tumbling-E software task is not an implementation of a validated pediatric screening protocol. No age-specific pass/fail threshold is applied.

## Run and test

From the repository root:

```sh
python -m pip install -r prototypes/prototype-b-parent-guided-check/requirements.txt
python -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502
```

Tests run from the demo directory:

```sh
cd prototypes/prototype-b-parent-guided-check
python -m unittest discover -p 'test_*.py'
```

`app.py` contains the parent activity and workspace routing. `demo.py` preserves its activity and note logic. `vision.py` handles the direction task, sizing, completed records, validated import and window calculations. `vision_ui.py` renders the new workspaces. `test_demo.py` exercises the original flow; `test_vision.py` covers sizing, state guards, window boundaries, setup isolation, import validation and complete Streamlit journeys.

The entry point and port remain the same. The published [Family app](https://focal-demo-b.streamlit.app/) may still run `main`. Deploy this branch, or merge its changes and redeploy, before expecting the public app to show the upgrade. No production deployment was performed while developing it.

## Three-minute investor demo

Prepare the local upgraded app, with the physical setup already checked. Use a second tab for a fictional parent-summary example.

1. **0:00–0:35:** show setup, enter the live task and complete practice.
2. **0:35–1:30:** complete 12 responses, show per-size results and save once.
3. **1:30–1:55:** open My saved checks and identify the newly saved result.
4. **1:55–2:25:** explicitly switch to Fictional example history. Compare 7, 30 and 90 days and identify these as made-up task responses.
5. **2:25–2:40:** return to My saved checks and show the JSON export/restore controls.
6. **2:40–3:00:** show the prepared parent note and close. Explain that clinical interpretation and partner reporting require further work.

Use the updated deck's screenshots if the live app stalls. Rehearse the actual click sequence and timing with both presenters. Browser software-test inputs and illustrative history are not participant outcomes.
