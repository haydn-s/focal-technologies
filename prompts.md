# Focal prototype prompt log

Use this shared file to record the prompts used to build Prototypes A, B, and C. Add the date, author, actual prompt text, intent, and resulting change or learning for each entry. Keep product-development prompts with the relevant prototype and shared repository work in its own section.

The Demo B entries below come from Haydn's October 21, 2026 chat. The A and C sections are ready for their teammates' additions. Original per-prototype logs remain available as references.

## Prototype A Focal Monitor

**Persona:** Routine-Check Riley

Teammate entries pending. Bring the actual prompts and outcomes into this section using the entry format below. The existing [Prototype A prompt log](prototypes/prototype-a-riley-vision-tracking/PROMPT_LOG.md) is available as a reference.

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

**Prompt count:** This chat contains two product-development prompts for B. The shared repository requests below document additional work but are not counted as extra B build prompts. Continue recording actual prompts as B develops toward the assignment's minimum of five per prototype.

## Prototype C Focal DMV Pre-Check

**Persona:** Anxious Applicant Alex

Teammate entries pending. Bring the actual prompts and outcomes into this section using the entry format below. The existing [Prototype C prompt log](prototypes/prototype-c-alex-dmv-precheck/PROMPT_LOG.md) is available as a reference.

## Shared repository work

These requests supported the demos and their collaboration workflow. They are recorded separately from the product experiments. All were made by Haydn on October 21, 2026.

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

## Entry format for teammates

For each actual prompt, add:

- **Date and author**
- **Actual prompt:** quote the request as written, including any context needed to understand it
- **Intent:** what you were trying to build or learn
- **Result:** what changed in the prototype
- **Learning or verification:** what you observed; distinguish automated checks from customer feedback

Use one entry per actual request. Keep simulated examples, proposed future prompts, and implementation steps distinct from prompts that were actually used.
