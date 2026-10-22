# Focal prototype prompt log

Use this shared file to record the prompts used to build Prototypes A, B, and C. Add the date, author, actual prompt text, intent, and resulting change or learning for each entry. Keep product-development prompts with the relevant prototype and shared repository work in its own section.

The Demo B entries below come from Haydn's October 21, 2026 chat and the Demo C entries from Burak's chat the same day. Teammates added the Demo A entries. Original per-prototype logs remain available as references.

## Prototype A Focal Monitor

**Persona:** Routine-Check Riley

### A1 Build the Initial Interactive Prototype

**Prompt excerpt:**

> Build a complete, locally runnable Streamlit prototype called “Focal Monitor” for our Duke product management course.

**Intent:** Create a four-step experience: Welcome, an eight-question tumbling-E check, Results, and Vision History with fictional records and user feedback.

**Result:** The first version included interactive questions, scoring, charts, feedback, and four passing unit tests. The teammate-supplied review found that the main journey was not yet reliable: Start, final-question navigation, View History, and Reset could fail; the last question could produce a ninth response; and placeholder data could appear as a live result.

**Learning:** Working components did not guarantee a working end-to-end journey. Reliability needed to come before visual polish.

### A2 Repair Navigation and Protect Result Integrity

**Prompt excerpt:**

> Make question submission idempotent, ensure each question can only be recorded once, and never present incomplete or fictional data as a completed user result.

**Intent:** Synchronize sidebar and button navigation, prevent duplicate answers, validate completed sessions, support Resume, and separate sample history from live results.

**Result:** Navigation callbacks and duplicate guards were added. Follow-up validation required exactly eight unique answers, a valid completion timestamp, valid schema types, and rejection of boolean question IDs. Partial or malformed sessions were handled safely and excluded from completed history. Duplicate history tables were removed.

**Verification:** The teammate-supplied review reported 35/35 project tests, 16/16 targeted checks, and browser journeys covering 0/8 and 8/8 results. These findings apply to the reviewed cases, not every possible corrupted state.

**Learning:** Normal-flow tests were insufficient; completion needed one shared, explicit validation rule.

### A3 Compare Result Views and Collect Neutral Feedback

**Prompt excerpt:**

> Determine whether users actually prefer historical context rather than assuming that more information is always better.

**Intent:** Compare Single Result with Trend Tracking using the same underlying result, then collect balanced feedback without a positive default.

**Result:** The prototype added randomized initial view assignment, a compact view switcher, required exposure to both views, neutral questions, JSON export, locked feedback after submission, and a post-submission research debrief.

**Verification:** The first implementation still had unequal framing, unstable assignment, one-view submission, and editable post-debrief feedback. After correction, the teammate-supplied review reported 46/46 project tests and 34/34 independent checks, including a downloaded JSON record matching the observed responses.

**Learning:** The flow supports exploratory preference research, but it does not prove that users prefer tracking or will return over time. Seeing the isolated result before comparison may still influence preference.

### A4 Improve Visual Usability and Demo Readiness

**Prompt excerpt:**

> Improve visual design, usability, accessibility, and live-demo readiness without compromising existing functionality or research validity.

**Intent:** Improve instructions, spacing, theme readability, responsive layouts, accessible names, contrast, and the classroom presenter flow.

**Result:** The work refined the interface and presenter guide, fixed dark-theme readability, corrected clipped mobile and laptop labels, strengthened primary-button contrast, and clarified documentation claims. Accessible labels stopped announcing the target direction, while the log acknowledged that DOM inspection could still reveal internal attributes.

**Verification:** The teammate-supplied reviews confirmed the Prompt 5.1 layout fixes at desktop, 1024×768, and 390×844 viewports. Prompt 5.2 developer reporting recorded 50 passing tests and 5.93:1 primary-button contrast, but no matching independent 5.2 sign-off was supplied.

**Learning:** CSS assertions are not a substitute for rendered inspection. The two-minute presenter flow is a proposed sequence, not evidence of a timed human rehearsal.

### A5 Simplify the Product and Redesign Result Presentation

**Prompt excerpts:**

> There are too many descriptive things for the user to focus on the important instruction or result.
>
> Show a normal vision-check result instead of correct/all.
>
> Keep the sidebar collapsible, remove “Experience A/B,” and make the chart prettier.

**Intent:** Apply the PM's direction to reduce cognitive load and make the prototype feel like one coherent consumer product instead of a segmented research dashboard.

**Result:**

- Rebuilt the welcome and task hierarchy around the primary action.
- Collapsed optional research, setup, evaluator, presenter, and question-level details.
- Removed prominent legal/regulatory copy from the interface at the PM's direction.
- Replaced visible correct / total output with a demo acuity mapping from 20/20 to 20/200; an 8/8 interaction displays 20/20 · Normal vision.
- Applied the same result language to the immediate result, Single Result, Trend Tracking, chart, table, tooltips, and feedback export.
- Simplified visible view labels to Single Result and Trend Tracking while retaining stable internal study state.
- Restored an expanded-by-default sidebar with explicit collapse and reopen controls.
- Redesigned the chart with a smooth blue historical trend, subtle area fill, horizontal labels, a compact legend, and a coral diamond for the current result.

**Verification:** python -m py_compile app.py passed. The final post-merge run of python -m unittest test_app.py test_regression.py passed 51/51 tests: 24 unit and 27 Streamlit regression tests. The local app returned HTTP 200 at http://localhost:8501. UI commit fe46b03 was merged with the latest remote changes in f691486, and main matched origin/main before this log edit.

**Product boundary:** The acuity-style result is derived from the eight demo responses and is not a calibrated clinical measurement. This intentionally changes the original no-Snellen interface rule; the decision is recorded here for transparency. No new independent visual review, public deployment, or hosted-link test was completed for this final iteration.

**Learning:** Clear hierarchy and consistent result language reduced distraction and made the result easier to understand. Before external or clinical use, the team would need to validate the acuity model and reconsider how to present safety context without overwhelming the primary task.

## Prototype B Focal Family

**Author:** Haydn

**Persona:** Parent Pat

**Session date:** October 21, 2026

### B1 Set up independent Streamlit demos

**Actual user prompt:**

> We have to create website demos. See the assignment information provided.
>
> My teammate has already created demo A. I will create demo B. Make sure this is split in a way where we can have multiple Streamlit demos within one repository. You can see the other context information in "fundamentals". I will add some more content to this directory in a little bit.

**Intent:** Use the assignment and existing research to prepare Demo B while keeping the teammate's Demo A independently runnable in the same repository.

**Result:** Reviewed the assignment and supplied research, kept A in its existing directory, and set up an independent B workspace with its own entry point, requirements, documentation, and tests. Added local launch and deployment guidance and initially reserved a separate C workspace.

**Learning:** Separate Streamlit entry points and adjacent dependency files let the team work on and publish each hypothesis independently. Demo A's internal result-format comparison is part of A, not the team's separate Demo B.

### B2 Build the initial parent and child concept

**Actual user clarification:**

> Build an initial Demo B concept

**Context:** This answered whether to leave a Streamlit starter while more material arrived or build an initial concept from the current research.

**Intent:** Produce a usable first concept grounded in the available research, with room to revise it when additional material arrived.

**Result:** Built Focal Family for the provisional Parent Pat persona. The flow includes six randomized, fixed-size matching pictures, skip controls, parent observations, a parent-selected next step, a preparation checklist, a downloadable summary, neutral feedback, and a clearly labeled fictional example. It does not infer clinical results from the matching activity.

**Learning:** The implementation makes a parent-and-child preparation workflow concrete and distinct from A's trend-tracking experience. Seven automated checks cover the activity and main journeys, including skipped pictures, editing, input preservation, neutral feedback, and reset. These checks verify behavior; the hypothesis still needs testing with parents.

### B3 Strengthen the parent follow-up experience

**Actual user request:**

> I thought the requirement was 5 prompts total for all the prototypes. If it needs 5 individually, then we can work more to beef up prototype B.

**Context:** Haydn clarified this during the assignment review. The assignment says at least five prompts per prototype; the request authorized further B development rather than counting repository maintenance as extra build prompts.

**Intent:** Make the parent workflow more useful beyond the matching activity.

**Result:** Added parent-selected questions, a custom question, an editable contact-note draft, and separate summary and message downloads. The draft follows the parent's selected next step and observations; it does not derive advice from matching performance. Feedback now preserves the context that was evaluated even when the parent later edits the summary.

**Verification and learning:** Added checks that questions and edits reach the export, regenerated notes invalidate prior download requests, and submitted feedback keeps the original evaluated context. This makes the take-home output concrete; it does not establish whether parents will actually contact a provider.

### B4 Add practice and breaks for children

**Actual user instruction:**

> Add practice and pause/resume

**Context:** This answered: “For Prototype B's child activity, should I add a guided practice picture and pause/resume controls so children can learn the interaction and take a break without losing progress?”

**Intent:** Help a parent and child learn the controls before the activity and pause without losing progress.

**Result:** Added a guided practice circle, a separate start action for the six-picture activity, and pause/resume controls. Practice is not counted in the activity result. Pausing hides the response controls and rejects stale answer events; resuming returns to the next unanswered picture.

**Verification and learning:** Added model and full-flow checks for practice gating, separate counts, pause preservation, and resume. Accommodating a child's pace improves the interaction model without adding a claim about clinical measurement.

### B5 Measure next-step clarity and barriers

**Actual user instruction:**

> Add clarity and follow-through questions

**Context:** This answered: “For Prototype B's evaluation, should I add neutral questions about how clear the parent's next step is and what could prevent follow-through?”

**Intent:** Measure the proposed guidance benefit directly and learn what could keep a parent from following through.

**Result:** Added a required next-step clarity question with negative, neutral, positive, and uncertain choices and no preselected answer. Added an optional open question about barriers to follow-through. Both are recorded with the original evaluated context in the feedback export.

**Verification and learning:** Checked that negative and uncertain answers are accepted, no clarity answer is selected initially, and barrier text is preserved. Clarity and stated barriers provide more specific research signals than usefulness alone; they still do not prove that an appointment was booked.

**Prompt count:** Five distinct B development requests are now recorded (B1–B5). B3–B5 were actual requests in this session and were implemented separately. The shared repository requests below are not counted toward this total.

## Prototype C Focal DMV Pre-Check

**Author:** Burak

**Persona:** Anxious Applicant Alex

**Session date:** October 21, 2026

These entries come from Burak's Claude Code chat. The [Prototype C prompt log](prototypes/prototype-c-alex-dmv-precheck/PROMPT_LOG.md) has the same entries in more detail.

### C1 Ground the AI in the team's research

**Actual user prompt:**

> ok nice. we will work on this branch. we are basically building a prototype. the knowledge base folder has all the submissions we made so far for this class/project. its a business class so not that technical at all. look through the knowledge base to understand our product first please.

**Intent:** Check that the AI could build an accurate picture of Focal from our own submissions (Lean Canvas, customer discovery, competitive analysis, business model deck, Define-phase workbook) before building anything, so the prototype would rest on our evidence rather than the AI's assumptions.

**Result:** A summary of Focal as Test → Track → Guide → Share, the four personas and how strong each one's evidence is, the "convenient or thorough, never both" market gap, and our four Hills. It also pulled out key insights: trust and acting on a result matter more than accuracy, a result should come with a next step rather than a bare score, and a first check has no baseline to compare against.

**Learning:** The summary matched the team's view and became the brief for everything after it.

### C2 Map the assignment to the three personas

**Actual user prompt:**

> this is this assignments prompt: [pasted the full prototype assignment brief, now saved at [docs/assignments/prototype-assignment.md](docs/assignments/prototype-assignment.md)]

**Intent:** Decide how to split three prototypes so the class vote answers a real strategy question, rather than comparing three versions of the same product.

**Result:** A recommendation to give each prototype a different persona and a different approach. A (Riley) tests ongoing tracking, B (Pat) tests a child-friendly check, and C (Alex) tests a deadline-triggered "Will I pass my DMV eye test?" check, which is also the free channel on our Lean Canvas.

**Learning:** Framed this way, the vote answers "which persona and approach should come first?" Burak took C because a teammate was already building B.

### C3 Build Prototype C for Alex

**Actual user prompt:**

> yes someone else is doing pat. so lets do persona C and lets do Alex as per your suggestion.

**Intent:** Test whether a check built around one specific, deadline-tied question ("Will I pass my state's DMV test?") resonates more than general vision monitoring.

**Result:** Built the Focal DMV Pre-Check. Each feature traces back to a quote from Burak's Alex interview:
- **State picker** using the real 20/40 rule for NC, CA, NY, TX and FL, researched from official DMV pages and administrative codes, each with a source link.
- **Screen calibration** against any ID card, plus a distance step, so letters show at their true size on any screen.
- **Six letters at the line that decides the result**, plus a "Can't tell" button, so pure guessing almost never earns "on track".
- **One honest retake**, with both results shown side by side.
- **A next-step plan**: find an eye exam, the state's eye-doctor form, a message to a parent, and a reminder.
- **A neutral feedback form** with JSON export.

**Deliberate cuts:** testing each eye separately, real reminders and booking, an agency view, and the other 45 states.

**Verification:** 27 automated tests covering scoring, letter sizing, state data and every click path. Manual click-through at desktop and phone sizes, in light and dark themes. These checks verify behavior only; the hypothesis still needs testing with real applicants.

**Learning:** The riskiest assumption is the trigger itself. Alex said the road test worried him more than the vision screening.

### C4 Review C against Prototype B

**Actual user prompt:**

> good job. also one of my teammates pushed their branch. they were the one doing persona B. maybe check it out but idk if it should lead to any change. you tell me that.

**Intent:** Confirm that B and C were still genuinely different approaches, and find out whether B changed what C should be.

**Result:** C's concept stayed the same, with small changes:
- Switched to the official Focal mark ([assets/brand/focal-lockup.svg](assets/brand/focal-lockup.svg)).
- Pinned Streamlit 1.66.1 to match B.
- Moved C to port 8503.
- Added wording that "on track" does not mean someone's eyes are fine overall, following the Define-phase rule.
- Added an A/B/C comparison to C's README.

**Learning:** The three demos now span "how much should Focal judge for you?" A shows a trend, B leaves the judgment to the parent, and C gives a verdict against a rule. That makes the class vote more informative.

### C5 Integrate C with the team repository

**Actual user prompt:**

> lets merge Haydn's branch into burak-dev and then push our work on top of it. Then I can check out C myself and see if we want to PR

**Intent:** Fit C into the shared structure (one independent Streamlit app per folder) so all three demos run and deploy side by side.

**Result:** Merged Haydn's B branch into `burak-dev` with no conflicts. Replaced the `prototype-c/` placeholder and added C to the root README, the `Makefile` and `requirements-dev.txt`.

**Verification:** All three test suites passed before the push (A 50, B 7, C 27).

### C6 Compare deployment readiness across A, B and C

**Actual user prompt:**

> ok so talking about everything on main and my PR. are all deployed to the same extent. like is proto A already on streamlit. are B and C. like is anything fundamentally different.

**Intent:** Find out whether the three demos were equally ready for the class link, and whether anything made them fundamentally different.

**Result:** No code changes. None of the three demos was deployed yet, and all three deploy the same way: one Streamlit Cloud app per folder. The recommendation was to merge first, then deploy all three from `main`, and to open the links shortly before class because idle apps go to sleep. The review also found that A's revised results show acuity labels such as "20/20 · Normal vision" from fixed, uncalibrated letter sizes. These could contradict C's calibrated verdict during a live demo. A's own log records the labels as a deliberate PM decision, so this was raised as a team discussion rather than changed.

**Verification:** The updated A suite passed 51/51 on the `main` snapshot.

### C7 Add states whose line isn't 20/40

**Date:** October 22, 2026

**Actual user prompts:**

> maybe the demo should include Georgia NJ and Wyoming since those are the non 20/40 states. If we push will it end up on stream lit automatically?

> yes do that.

**Intent:** All five original states used 20/40, so in a live demo the state picker looked cosmetic. Show that the check really follows each state's own rule.

**Result:** Checked each state's official source.
- **Georgia (20/60) and New Jersey (20/50):** added, with their rule text and source links. Georgia's 20/60 line is slotted into the letter scale only for states that use it.
- **Wyoming:** not added. Its WYDOT form also uses 20/40.
- **Demo script:** now switches to Georgia so the class sees the line change.
- **Deployment:** Streamlit redeploys from `main`, so the live app changes once this pull request merges.

**Verification:** 31 automated tests pass, including 4 new ones, one of which checks that the 20/40 test is unchanged. The Georgia rule card was checked in the running app.

**Prompt count:** Seven prompts for C. C1–C4, C6 and C7 shaped the product; C5 was integration work. Repository and presentation requests are listed under shared repository work (R6–R8).

## Shared repository work

These requests supported the demos and their collaboration workflow. They are recorded separately from the product experiments. R1–R5 were made by Haydn and R6–R8 by Burak, on October 21–22, 2026.

### R1 Push Demo B without a pull request

**Actual user prompt:**

> Push my branch but don't open a PR yet.

**Intent and result:** Committed and pushed the initial Demo B and repository setup on `codex/demo-b-focal-family`. No pull request was opened.

### R2 Synchronize with the team repository

**Actual user prompt:**

> Update the local repository to match GitHub.

**Intent and result:** Fetched the team's latest work and updated the local `main` checkout to the integrated version containing all three demos.

### R3 Reorganize the repository

**Actual user prompt:**

> Open a new branch called "repo-scaffolding". Let's start reorganizing the repo as appropriate.

**Intent and result:** Created `repo-scaffolding`, grouped reference documents by topic under `docs/`, moved original logos to `assets/brand/`, updated references, added development and deployment guides, and added independent automated test jobs. The three app entry-point paths were kept stable.

### R4 Include the newly added reference documents

**Actual user prompt:**

> I added more documents to the fundamentals directory, we can move those as appropriate.

**Intent and result:** Included those files in the reorganization. Checksums identified 14 distinct originals among 27 copies; every unique document and logo was preserved unchanged while exact duplicates were consolidated.

### R5 Merge the organization changes and establish the team log

**Actual user prompt:**

> Once you're done, merge the branch directly into main. Then clean up the local repository and open a branch called "prompt-logs". Create a file called "prompts.md" and update prompts we've used to create the prototype B in this session. My teammates will update the file to include prompts they used for the other demos.

**Intent and result:** Merged the scaffolding work directly into `main`, preserving the team's newer A prompt-log update. All 85 tests passed. Pushed `main`, removed the two fully merged local work branches, and created `prompt-logs` with this shared file and the two actual Demo B build prompts.

### R6 Open the pull request for B and C

**Actual user prompts:**

> so he isn't PR ing anymore. since mine will include it right?

> ok nice. can you do the PR.

**Intent and result:** Confirmed that `burak-dev` already contained Haydn's B commit, so one pull request could bring both B and C into `main`. Opened [#3](https://github.com/haydn-s/focal-technologies/pull/3), which merged cleanly.

### R7 Add Prototype C to this shared log

**Actual user prompts:**

> there is a new PR for prompts used. can you see it

> do that please yes

**Intent and result:** Reviewed this pull request, added the C entries above on `prompt-logs`, and updated two paths in C's own prompt log that had pointed to folders removed in the repository reorganization.

### R8 Draft a presentation and a demo script

**Actual user prompts (Burak, October 21–22, 2026):**

> do you remember the slide requirements?

> the whole deck please.

> ok just push my slides to that same branch where the other deck is. dont combine them now. another team member will deal with this.

> now things are deployed. i will only present my demo. give me a 2 minute script.

**Intent and result:** Drafted a separate 15-slide deck that follows the assignment's four presentation parts. It was pushed as a PDF, an HTML version and speaker notes to `docs/presentations/burak-draft/`, without being combined with Haydn's PPTX. Also wrote a two-minute live-demo script for Prototype C. The README's demo section now includes the Georgia state switch from C7.

## Entry format for teammates

For each actual prompt, add:

- **Date and author**
- **Actual prompt:** quote the request as written, including any context needed to understand it
- **Intent:** what you were trying to build or learn
- **Result:** what changed in the prototype
- **Learning or verification:** what you observed; distinguish automated checks from customer feedback

Use one entry per actual request. Keep simulated examples, proposed future prompts, and implementation steps distinct from prompts that were actually used.
