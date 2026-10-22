# Focal Prototype A — Selected AI Development Prompt Log

**Course:** Duke MENG 570 Product Management

**Prototype:** Focal Monitor, a Streamlit demonstration for Riley

**Record period:** October 2026

**Product question:** Would an adult who wears glasses or contacts and suspects vision changes find historical context more useful than a single result? The prototype explores presentation preference and perceived usefulness; it does not establish clinical accuracy or sustained use.

**Evidence note:** Independent-review findings below come from the summary supplied by a teammate. The review files are not included in this repository, so those findings are attributed rather than independently re-verified here. Final Prompt 5 results are developer-run checks from this repository.

---

## 1. Build the Initial Interactive Prototype

**Prompt excerpt:**

> Build a complete, locally runnable Streamlit prototype called “Focal Monitor” for our Duke product management course.

**Purpose:** Create a four-step experience: Welcome, an eight-question tumbling-E check, Results, and Vision History with fictional records and user feedback.

**Outcome:** The first version included interactive questions, scoring, charts, feedback, and four passing unit tests. The teammate-supplied review found that the main journey was not yet reliable: Start, final-question navigation, View History, and Reset could fail; the last question could produce a ninth response; and placeholder data could appear as a live result.

**Learning:** Working components did not guarantee a working end-to-end journey. Reliability needed to come before visual polish.

---

## 2. Repair Navigation and Protect Result Integrity

**Prompt excerpt:**

> Make question submission idempotent, ensure each question can only be recorded once, and never present incomplete or fictional data as a completed user result.

**Purpose:** Synchronize sidebar and button navigation, prevent duplicate answers, validate completed sessions, support Resume, and separate sample history from live results.

**Outcome:** Navigation callbacks and duplicate guards were added. Follow-up validation required exactly eight unique answers, a valid completion timestamp, valid schema types, and rejection of boolean question IDs. Partial or malformed sessions were handled safely and excluded from completed history. Duplicate history tables were removed.

**Verification:** The teammate-supplied review reported 35/35 project tests, 16/16 targeted checks, and browser journeys covering 0/8 and 8/8 results. These findings apply to the reviewed cases, not every possible corrupted state.

**Learning:** Normal-flow tests were insufficient; completion needed one shared, explicit validation rule.

---

## 3. Compare Result Views and Collect Neutral Feedback

**Prompt excerpt:**

> Determine whether users actually prefer historical context rather than assuming that more information is always better.

**Purpose:** Compare Single Result with Trend Tracking using the same underlying result, then collect balanced feedback without a positive default.

**Outcome:** The prototype added randomized initial view assignment, a compact view switcher, required exposure to both views, neutral questions, JSON export, locked feedback after submission, and a post-submission research debrief.

**Verification:** The first implementation still had unequal framing, unstable assignment, one-view submission, and editable post-debrief feedback. After correction, the teammate-supplied review reported 46/46 project tests and 34/34 independent checks, including a downloaded JSON record matching the observed responses.

**Learning:** The flow supports exploratory preference research, but it does not prove that users prefer tracking or will return over time. Seeing the isolated result before comparison may still influence preference.

---

## 4. Improve Visual Usability and Demo Readiness

**Prompt excerpt:**

> Improve visual design, usability, accessibility, and live-demo readiness without compromising existing functionality or research validity.

**Purpose:** Improve instructions, spacing, theme readability, responsive layouts, accessible names, contrast, and the classroom presenter flow.

**Outcome:** The work refined the interface and presenter guide, fixed dark-theme readability, corrected clipped mobile and laptop labels, strengthened primary-button contrast, and clarified documentation claims. Accessible labels stopped announcing the target direction, while the log acknowledged that DOM inspection could still reveal internal attributes.

**Verification:** The teammate-supplied reviews confirmed the Prompt 5.1 layout fixes at desktop, 1024×768, and 390×844 viewports. Prompt 5.2 developer reporting recorded 50 passing tests and 5.93:1 primary-button contrast, but no matching independent 5.2 sign-off was supplied.

**Learning:** CSS assertions are not a substitute for rendered inspection. The two-minute presenter flow is a proposed sequence, not evidence of a timed human rehearsal.

---

## 5. Simplify the Product and Redesign Result Presentation

**Prompt excerpts:**

> There are too many descriptive things for the user to focus on the important instruction or result.
>
> Show a normal vision-check result instead of correct/all.
>
> Keep the sidebar collapsible, remove “Experience A/B,” and make the chart prettier.

**Purpose:** Apply the PM's direction to reduce cognitive load and make the prototype feel like one coherent consumer product instead of a segmented research dashboard.

**Outcome:**

- Rebuilt the welcome and task hierarchy around the primary action.
- Collapsed optional research, setup, evaluator, presenter, and question-level details.
- Removed prominent legal/regulatory copy from the interface at the PM's direction.
- Replaced visible `correct / total` output with a demo acuity mapping from `20/20` to `20/200`; an 8/8 interaction displays `20/20 · Normal vision`.
- Applied the same result language to the immediate result, Single Result, Trend Tracking, chart, table, tooltips, and feedback export.
- Simplified visible view labels to **Single Result** and **Trend Tracking** while retaining stable internal study state.
- Restored an expanded-by-default sidebar with explicit collapse and reopen controls.
- Redesigned the chart with a smooth blue historical trend, subtle area fill, horizontal labels, a compact legend, and a coral diamond for the current result.

**Verification:** `python -m py_compile app.py` passed. The final post-merge run of `python -m unittest test_app.py test_regression.py` passed **51/51 tests**: 24 unit and 27 Streamlit regression tests. The local app returned HTTP 200 at `http://localhost:8501`. UI commit `fe46b03` was merged with the latest remote changes in `f691486`, and `main` matched `origin/main` before this log edit.

**Product boundary:** The acuity-style result is derived from the eight demo responses and is not a calibrated clinical measurement. This intentionally changes the original no-Snellen interface rule; the decision is recorded here for transparency. No new independent visual review, public deployment, or hosted-link test was completed for this final iteration.

**Learning:** Clear hierarchy and consistent result language reduced distraction and made the result easier to understand. Before external or clinical use, the team would need to validate the acuity model and reconsider how to present safety context without overwhelming the primary task.
