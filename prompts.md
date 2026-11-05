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

## Focal Family master prototype

**Author:** Burak

**Persona:** Parent Pat

**Session date:** November 1, 2026

The full entry, with the decisions made, is in the [master prototype's prompt log](prototypes/focal-family/PROMPT_LOG.md).

### M1 Combine the prototypes around the investor story

**Actual user prompt:**

> look through the current repo. especially the investor presentation branch. when we did our prototype presentations my prototype C won but I think it was because of the delivery of the presentation. And as you will see the investor presentation focuses on the family aspect. so lets build a master prototype that combines the previous ones. Has the style of C but also has the focus of the presentation etc. I think proto B was focused on the family aspect.

**Intent:** One product that carries C's clarity and polish, B's family story (the investor pitch's focus) and A's comparison over time, without implying the task is a screening.

**Result:** Built `prototypes/focal-family/` in C's design.
- **Engine:** B's check-and-history engine is copied unchanged, so histories stay compatible.
- **Journey:** setup with the reason for checking → practice → 12-letter check → result → history (live and fictional; 7, 30 and 90 days; export and restore) → a parent note that suggests the next step from the parent's reason, never the score.
- **Cut on purpose:** B's picture game, C's state rules and a school-facing view.

**Verification:** 24 automated tests pass. Clicked through at desktop and phone sizes. Fixed three demo-friction issues found that way: scroll position between pages, a message draft that didn't update, and a checklist that drew only its first box.

### M2 Keep the DMV check as an option

**Actual user prompt:**

> is it still like C in fashion, maybe lets have the DMV element somewhere. like an option. but given where the presentation focuses the protoype should focus there too.

**Intent:** Keep C's DMV check in the product, but secondary to the family story the pitch tells.

**Result:**
- **Placement:** an "Also from Focal" card below the family actions on the welcome page opens Prototype C's DMV pre-check, framed for a teen's permit or a parent's renewal.
- **Logic:** copied from C in `dmv.py`, with all seven states. Calibration and distance are shared with the family check, and DMV results stay out of the family history.

**Verification:** 30 automated tests pass (6 new). Checked the welcome card and a DMV result in the running app.

### M3 Take the React UI's look where it excels

**Session date:** November 5, 2026

**Actual user prompt:**

> can you just make our demo like his where his excels?

**Intent:** Give the Streamlit master the look the team liked in Qingyi's React UI (PR #10) before class, while keeping calibrated letters, history over time and an honest parent note.

**Result:**
- **Look:** React UI palette and fonts (paper, navy, Plus Jakarta Sans, Fraunces) in a theme file scoped to this app; a top bar, two-column welcome with a labeled example card, white section cards, chip choices, a room sketch, an arrow pad, result tiles and toasts.
- **Kept:** the logic and tests from M1 and M2.
- **Fixed:** pages didn't always open at the top after a page change.

**Verification:** 32 automated tests pass (2 new). Clicked through the full family flow in the running app.

### M4 Calibration that works on a projector

**Actual user prompt:**

> ow while i remember can you make the card calibration range even wider. last time it was close when presenting but on a project screen the smallest wasn't small enough.

**Intent:** Let the presenter calibrate on a projector, where a card spans only a few dozen pixels.

**Result:** Card width now 24–800 px (was 160–600) with −/+ fine-tuning in the master; the same range in B's engine (both copies kept identical) and in Prototype C's slider (was 180–560).

**Verification:** 33 master tests pass (1 new: a full check calibrated at 26 px). A, B and C suites pass.

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

### R9 Prepare the executive investor pitch

**Date and author:** October 30, 2026, Haydn Stucker.

**Actual user prompt excerpts:**

> Update the local repo so it matches GitHub. Then open a new branch called "executive-pitch".

> We need to create an executive presentation for our pitch.

> We need to allow 3 minutes for our product demo.

> Also, we are using our Family Prototype for our final presentation.

> Make it a 14-minute presentation. He updated the requirements in class.

Haydn also selected the Focal Prototype Presentation as the visual reference and authorized a proposed school or pediatric-practice licensing model with a free parent experience and an 18-month funding plan. The supplied assignment requirements are summarized in [the pitch brief](docs/assignments/executive-pitch-assignment.md).

**Intent and result:** Fast-forwarded local `main` to GitHub and created `executive-pitch`. Added a Family-focused investor PPTX with 14 main slides, five backups, a three-minute demo, timed scripts for all five speakers, an explicitly proposed $600K raise and a reproducible financial model. The initial market and revenue model focuses on schools; pediatric practices remain an expansion possibility outside the forecast. Original decks and prototype code remain intact.

**Learning and verification:** The research contains only one real parent interview and no documented Family sales or pilot outcomes. The new pitch distinguishes that evidence from simulations, targets and financial assumptions. Financial totals, PPTX structure, editable chart data, fonts and layouts were checked, and each rendered slide was reviewed. The timed script is a rehearsal plan, not a measured live performance or customer-validation result.

### R10 Upgrade Family and revise investor coverage

**Date and author:** October 30, 2026, Haydn Stucker.

**Actual prompt:**

> Revise the slides. Are we sure that we're hitting all the major sections?
>
> We probably need to update the demo as well, and add new functionality. Create a new branch called "focal-family-updates" and start upgrading the demo. We will still use Streamlit, but we need to add functionality, live testing, and vision performance over time windows to demonstrate the capabilities of the app.

**Intent and result:** Created `focal-family-updates` from the current investor-pitch branch. Added a parent-assisted experimental direction task, controlled screen/distance setup, completed-check save, history export/restore, same-setup comparisons and 7/30/90-day windows. Retained the parent activity and editable note. Revised product/demo slides, competitive gaps, milestone timing and assignment coverage.

**Learning and verification:** Automated logic and Streamlit journey tests cover task sizing, completion guards, history isolation, windows and validated file restore. A local browser walkthrough exercised setup, practice, pause/resume, all 12 responses, save and history. Software-test responses and fictional timeline examples are not customer evidence or clinical validation. Public deployment remains a separate step.

### R11 Package the Family React UI candidate

**Date and author:** November 5, 2026, Qingyi Hu. Packaging tool: Codex; supplied UI implementation: Gemini / Google AI Studio.

**Actual prompt:**

> 我还是更喜欢REACT应用。帮我PR一个你说的保留和可保留的文件。PR到一个新branch里吧。防止branch里的内容太多太乱。最后帮我写一两句话向队友说明我干了啥。

**Intent and result:** Import the supplied React UI into a clean branch and an isolated `prototypes/focal-family-ui/` directory, retaining the standalone HTML snapshot and logo while omitting temporary generation files. Add project-specific setup/provenance documentation and a dependency lockfile; keep the Streamlit demo intact.

**Learning and verification:** Production build, TypeScript checking, and all six supplied logic tests pass. React/HTML browser parity, end-to-end interactions, and clinical validity were not verified. This packaging request is repository maintenance and does not count as an additional product-development prompt. The supplied ZIP does not establish the full history of prompts used to generate the UI.

### R12 Refresh the Family UI on the existing PR

**Date and author:** November 5, 2026, Qingyi Hu. Packaging tool: Codex; supplied UI update: Gemini / Google AI Studio.

**Actual prompt:**

> 那就更新原PR吧。我们还没merge

**Intent and result:** Update `family-react-ui-preview` / PR #10 from `untitled-2026-11-5-14-32-13.zip`. Import the brand-blue theme into the React app and HTML snapshot, retaining packaging fixes, Focal page metadata, and the original logo. Exclude the nested old ZIP, template metadata, and unused reference files.

**Learning and verification:** Production build, TypeScript checking, and all six supplied logic tests pass. No clinical or browser-performance validation is claimed. This repository update request is not an additional product-development prompt.

## Entry format for teammates

For each actual prompt, add:

- **Date and author**
- **Actual prompt:** quote the request as written, including any context needed to understand it
- **Intent:** what you were trying to build or learn
- **Result:** what changed in the prototype
- **Learning or verification:** what you observed; distinguish automated checks from customer feedback

Use one entry per actual request. Keep simulated examples, proposed future prompts, and implementation steps distinct from prompts that were actually used.
