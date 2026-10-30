# Focal Family executive pitch

[Open the editable pitch deck](<Focal Family Executive Pitch.pptx>).

This investor presentation contains **14 main slides and 5 hidden backup slides**. The full presentation is **14 minutes, including a 3-minute Focal Family demo**. The user confirmed the revised in-class time limit on October 30, 2026. Use Family only; the other prototypes are background research.

The deck reuses the Focal Prototype Presentation's visual style, master, dimensions, font, logo and Family screenshots. Each slide includes a suggested script, presenter, time window, sources and assumptions in its speaker notes. The screenshots show the existing prototype, including a clearly labeled fictional summary. Backup slides remain accessible through the slide navigator for Q&A.

## Run of show

| Slide | Topic | Presenter | Duration | Clock |
| --- | --- | --- | --- | --- |
| 1 | Focal Family and the ask | Haydn | 0:30 | 0:00–0:30 |
| 2 | The work after a school letter | Fan | 0:55 | 0:30–1:25 |
| 3 | Parent user and school buyer | Fan | 0:50 | 1:25–2:15 |
| 4 | Working parent experience | Qingyi | 0:45 | 2:15–3:00 |
| 5 | Family demo | Qingyi, then Burak | **3:00** | **3:00–6:00** |
| 6 | What funding will test and build | Burak | 0:55 | 6:00–6:55 |
| 7 | Alternatives and differentiation | Fan | 0:55 | 6:55–7:50 |
| 8 | Market size | Haydn | 0:55 | 7:50–8:45 |
| 9 | School and district sales channel | Haydn | 0:55 | 8:45–9:40 |
| 10 | Pricing and unit economics | Hadley | 0:55 | 9:40–10:35 |
| 11 | Three-year financial model | Hadley | 1:10 | 10:35–11:45 |
| 12 | Use of funds and milestones | Hadley | 0:55 | 11:45–12:40 |
| 13 | Team responsibilities | Qingyi 0:25, Burak 0:20 | 0:45 | 12:40–13:25 |
| 14 | Investment terms and close | Haydn | 0:35 | 13:25–14:00 |

Total allocation: Haydn 2:55, Fan 2:40, Qingyi 2:40, Burak 2:45, Hadley 3:00. Demo time includes clicking, pauses and the speaker handoff. The notes suggest roughly 130–150 spoken words per minute outside the demo. Rehearsal must confirm actual timing; the planned schedule is not a measured delivery time.

## Three-minute demo

Open [Focal Family](https://focal-demo-b.streamlit.app/) before presenting. Keep one fresh tab and a second tab on **Explore a fictional example**. The fallback must remain clearly identified as made up.

1. **0:00–0:20, Qingyi:** select an anonymous child label and age group. Introduce the example.
2. **0:20–0:40, Qingyi:** show the practice circle and start the activity.
3. **0:40–1:20, Qingyi:** complete six pictures, skipping one. Show pause/resume only if ahead of time.
4. **1:20–1:30:** reach observations and hand off to Burak.
5. **1:30–2:00, Burak:** choose an observation, add a short fictional note and select appointment preparation. Create the summary.
6. **2:00–2:35, Burak:** add a question, regenerate the draft and edit a sentence.
7. **2:35–2:50, Burak:** request the summary download and point out the checklist.
8. **2:50–3:00, Burak:** distinguish today's parent preparation from the proposed school workflow. Return to slide 6 at the three-minute mark.

After ten seconds of a technical failure, use the prepared fictional-example tab. If both tabs fail, use the existing practice screenshot on slide 5 and the summary screenshot on slide 4, then return to slide 6. The activity does not measure vision. A download is not an appointment, and an editable draft is not a sent message. A professional referral should never wait for the activity.

## Proposed commercial model

The user authorized a proposed model because pricing and funding were not established in the repo. These figures are **assumptions**, not customer results or commitments.

- Annual school license: **$2,400 per site**, free for families. A district may purchase several sites.
- Direct annual delivery cost: **$600 per site**. Gross margin: **75%**.
- Raise: **$600,000 for 15% equity**, implying $3.4M pre-money and $4.0M post-money. Classroom proposal, subject to negotiation.
- First 18 months: **$546,000** gross expenses plus **$54,000** reserve. Modeled revenue of $144,000 would leave $198,000 cash.
- Revenue: **$42K / $324K / $960K** over years 1–3. Year-three exit ARR: **$1.32M**, based on 550 paid sites.
- Operating result: **−$268.5K / −$207K / +$60K**. No tax, interest, capex or collection-delay assumptions.
- Existing prototype: parent activity, observations, chosen next step and exports. Partner reporting, persistent records, real reminders, permissions and integrations require funding and validation.

The market calculation uses the **2021–22 NCES historical count of 52,450 public elementary schools**, multiplied by the proposed price. The 10% serviceable subset is explicitly illustrative. This is not an independently measured current addressable market. The source is linked in the deck and in [model.json](model.json).

The research contains five real interviews, only one with a parent, and five AI simulations. It contains no documented paid Family customers, school partnerships, completed Family pilot or retention results. The story and financial model preserve those limits.

## Editing and rebuilding

- [notes.json](notes.json): slide titles, timing, scripts and citations.
- [model.json](model.json): editable planning inputs and assumptions.
- [calculated-model.json](calculated-model.json): generated half-year calculations and reconciled totals.
- [build.mjs](build.mjs): imports and adapts the existing prototype deck, creates editable tables and a chart, exports the PPTX, validates its package and renders the final slides.

To rebuild with the Codex bundled runtime, run:

```sh
"$FOCAL_NODE" docs/presentations/executive-pitch/build.mjs \
  "$FOCAL_NODE_MODULES" "$FOCAL_PYTHON" "$FOCAL_PRESENTATIONS_SKILL"
```

Set these task-specific variables to the runtime Node executable, module directory, Python executable and presentations skill directory returned by `load_workspace_dependencies`. The builder uses `@oai/artifact-tool`. Temporary renders, intermediate decks and validation reports stay under the ignored `build/executive-pitch/` directory. The final PPTX is a byte-for-byte copy of the validated export.

Changes to layout copy or narrative assumptions may also require updating the builder: the JSON files are not a generic slide-layout engine. Direct PowerPoint edits remain possible, but a rebuild will replace them. Preserve a separate copy if editing manually.

## Before class

Rehearse twice with all presenters, preload the demo, and verify that the proposed commercial assumptions represent the team's intended pitch. Review source claims and financial sensitivities for Q&A. The deck is not a submitted Canvas assignment, and no investor outreach or financing agreement has occurred.

The separate 3–5-page executive-summary assignment is outside this deck. Its required course outline is not present in the repo and was not replaced with an invented outline.
