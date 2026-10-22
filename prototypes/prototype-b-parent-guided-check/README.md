# Focal Family Prototype B

Focal Family is a concept for **Parent Pat**, a working parent of children aged 4–10. A parent and child learn the buttons with a practice picture, explore six large matching pictures with optional breaks, and record observations. The parent chooses a follow-up step and can prepare questions, edit a message, and download a summary. Haydn owns this workspace; Demo A stays in its existing sibling directory.

## Hypothesis and evidence

**Proposed hypothesis:** Parents will complete a short picture activity and use an observation summary to choose a concrete follow-up step.

The [customer discovery workbook](../../docs/research/customer-discovery/interview-workbook.docx) describes Parent Pat and records a real parent's concern that children memorize a fixed home chart. That parent already kept historical examination records, so another tracking dashboard alone would not address the observed gap. The [discovery presentation](../../docs/research/customer-discovery/presentation.pptx) identifies trust, result framing, and next-step guidance as questions for further testing.

This concept explores engagement and preparation for follow-up. Randomizing pictures varies the interaction; it does not establish clinical validity or solve chart memorization in a validated screening. The persona choice and hypothesis are provisional and can change when new material is added to [the research library](../../docs/README.md).

**Difference from Demo A:** A explores whether a corrective-lens wearer values trends over a single result. B explores a parent-and-child workflow and whether parents can turn their own observations into a concrete next step.

## Feature scope card

| Feature | Value to test | Effort | Complexity | Proposed success signal |
| --- | --- | --- | --- | --- |
| Six randomized, fixed-size pictures with skip | Can a parent and child engage with a varied activity? | Low | Low | At least 4 of 5 parent evaluators complete the activity without facilitator help |
| Guided practice and pause/resume | Can families learn the controls and take a break without losing their place? | Low | Medium | Practice does not change activity counts; parents can resume at the next unanswered picture |
| Observations and optional notes | Can a parent express what they have noticed? | Low | Low | Evaluators create a summary without needing to interpret a clinical score |
| Parent-selected next step and checklist | Does preparation help parents decide what to do? | Low | Low | At least 3 of 5 parent evaluators choose appointment or school-contact preparation |
| Downloadable summary | Is the output useful outside the app? | Low | Low | Observe whether evaluators request the summary and can explain its purpose |
| Parent-selected questions and editable message draft | Can a parent prepare the conversation they want to have? | Medium | Medium | Evaluators add a relevant question and can edit and export a note without facilitator help |
| Neutral feedback and session JSON | What helped, what was missing, and would they return? | Low | Low | Collect positive, negative, and uncertain responses without preselected answers |
| Clarity and follow-through questions | Does the parent understand their next step, and what might stop them? | Low | Low | Capture clarity ratings and optional barriers without treating stated intent as completed action |

These are proposed small-sample decision rules, not findings. Aim for a two-minute unaided journey. Record observed completion time, help needed, chosen action, download requests, and comments. A download click indicates a request, not proof that a file was saved or an appointment made. Analyze fictional-example sessions separately from sessions in which evaluators completed the activity.

**Deliberate cuts:** accounts, child names, camera access, clinical calibration, acuity measurement, diagnoses, prescriptions, provider search, real booking, messages, persistent records, and automatic feedback collection. All symbols stay the same large size. B does not reproduce A's trend chart.

## Run and verify

Run from the repository root:

```bash
python -m pip install -r prototypes/prototype-b-parent-guided-check/requirements.txt
python -m streamlit run prototypes/prototype-b-parent-guided-check/app.py --server.port 8502
```

Open `http://localhost:8502`. For tests:

```bash
cd prototypes/prototype-b-parent-guided-check
python -m unittest discover -p 'test_*.py'
```

`app.py` renders the interface. `demo.py` handles activity state, fictional examples, and text exports. Each user session has independent state; “Start over” clears the activity, observations, checklist, and feedback.

For Streamlit Community Cloud, set the main file to `prototypes/prototype-b-parent-guided-check/app.py`. Its adjacent requirements file is independent of A's. The [deployment guide](../../docs/deployment.md) explains how to publish separate links for the three demos.

## Demo rehearsal

1. Open a fresh session. Select a child label and age group, then choose “Let's play.”
2. Complete the guided practice, start the activity, match several pictures, skip one, and use pause/resume to show that progress is kept.
3. Select an observation, add a short note, and choose appointment preparation.
4. Create the summary, tick a preparation task, add questions or edit the message draft, and download the summary or message.
5. Edit observations or choose another next step to demonstrate that the parent controls the path.
6. Save neutral feedback, including next-step clarity and any follow-through barrier, and download the session JSON. Start over to show that the previous session clears.

“Explore a fictional example” is a clearly labeled alternative walkthrough. It loads made-up activity responses and observations and should not be presented as a completed participant activity.

## Data and interpretation

The matching activity is an interaction demonstration, not a vision screening or medical result. Its score reflects shape matching, attention, familiarity, and possible assistance. The app never uses answers or observations to infer a condition, issue a pass/fail result, or recommend a course of care. Preparation tasks follow the parent's selected action.

Session data lives in Streamlit's server-side session memory. There is no database, account, analytics collector, or automatic submission. Refresh/reconnection behavior depends on Streamlit session lifetime. To retain a summary or feedback, download it. The session JSON includes activity choices, observations, chosen next step, questions, editable message, checklist, download-request flag, feedback, and current-versus-fictional provenance. Feedback retains a snapshot of the evaluated context, even if the parent later edits the note or next step. Regenerating a note resets the current summary's download-request flag. Avoid entering identifying information in free text.

This is a working initial concept. Continue the [team prompt log](../../prompts.md#prototype-b-focal-family), validate it with parents, rehearse twice, and publish an accessible shared URL.
