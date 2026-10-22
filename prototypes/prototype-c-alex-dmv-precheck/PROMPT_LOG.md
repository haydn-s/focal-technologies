# Prompt Log: Focal DMV Pre-Check (Prototype C)
> **Course:** Duke University · MENG 570 Product Management
> **Author:** Burak Donbekci (CTO), building with Claude Code
> **Started:** October 21, 2026

Each entry records what we asked the AI, **what we were trying to learn or decide**, and what changed as a result. Prompts are quoted as typed.

---

## Prompt 1: Ground the AI in our own research first

```text
the knowledge base folder has all the submissions we made so far for this class/project.
its a business class so not that technical at all. look through the knowledge base to
understand our product first please.
```

**Trying to learn:** Can the AI build an accurate picture of Focal from our past submissions alone (Lean Canvas, customer discovery workbook, competitive analysis, business model deck, Define-phase workbook) before we ask it to build anything? We wanted the prototype grounded in our evidence, not the AI's assumptions about vision apps.

**What came back:** A summary of Focal as Test → Track → Guide → Share; our four personas and how strong the evidence is for each; the "convenient or thorough, never both" market gap; key insights (trust and acting on results matter more than accuracy, give a next step rather than a score, the first check has no baseline); and our four Hills.

**Decision:** The summary matched our view, so we used it as the brief for everything that follows.

---

## Prompt 2: Share the assignment and ask how it maps to our work

```text
this is this assignments prompt: [pasted the full Prototype assignment brief]
```

**Trying to learn:** How should three prototypes be split so the class vote actually answers a strategy question, rather than producing three versions of the same thing?

**What came back:** A recommendation to give each prototype a different persona *and* a different approach. A (Riley) tests ongoing tracking. B (Pat) tests a kid-friendly test that can't be memorized. C (Alex) tests a deadline-triggered "Will I pass my DMV eye test?" check, which is also the free channel on our Lean Canvas. Framed this way, the vote answers "which persona and approach first?"

**Decision:** A teammate is building Pat (B). Burak takes C for Alex.

---

## Prompt 3: Build Prototype C for Alex

```text
yes someone else is doing pat. so lets do persona C and lets do Alex as per your suggestion.
```

**Trying to learn:** Will a check framed around a specific, deadline-tied question ("Will I pass my state's DMV test?") resonate more than general vision monitoring?

**What the AI did, and the product decisions we reviewed:**
1. **Re-read Alex's full interview transcript.** Every feature traces back to a quote (see README §3). For example: "I had to google what the DMV standard is, and the first answers were for a different state" led to the state picker.
2. **Researched real state rules** for NC, CA, NY, TX and FL from official sources (DMV pages and administrative code) rather than inventing them. Finding: all five use 20/40 as the "pass at the counter" line, but the consequences and eye-doctor forms differ (DL 62, MV-619/MV-80L, Form 72010).
3. **Chose Streamlit** to match Prototype A, so all three prototypes deploy the same way.
4. **Designed against "I guessed and got lucky":** 6 letters at the deciding line plus a "Can't tell" button, so a pure guesser gets "on track" less than 1% of the time (verified in tests).
5. **Designed against "two different answers and I'm done":** one retake, both results shown, and no keeping the better score.
6. **Cut on purpose:** per-eye testing, real reminders, real booking or insurance lookup, a Lisa/agency view, and the other 45 states (see the Feature Scope Card in the README).

**Verified:** 27 automated tests pass (scoring, letter sizing, state data, and every click path through the app). Clicked through manually in desktop, phone and light/dark views.

---

## Prompt 4: Check C against the teammate's Prototype B

```text
also one of my teammates pushed their branch. they were the one doing persona B. maybe check it
out but idk if it should lead to any change. you tell me that.
```

**Trying to learn:** Are A, B and C still genuinely different approaches, or are B and C drifting into the same product? Does anything in B change what C should be?

**What came back:** C's concept stays. B (Focal Family) deliberately gives **no score and no pass/fail**: the parent judges. C gives a **verdict against an external rule**: the product judges. A sits in between, with the user reading a trend. Together the three span "how much should Focal judge for you?", which makes the class vote more informative. Small changes to C:
- Switched to the official Focal mark (same geometry and colors as [`assets/brand/focal-lockup.svg`](../../assets/brand/focal-lockup.svg)), so all three demos share one brand.
- Pinned `streamlit==1.66.1` to match B; moved C to port 8503.
- The "on track" result now says it does **not** mean your eyes are fine overall, in line with our Define-phase decision never to imply someone is "fine".
- Added an A/B/C comparison table to the README.

**Raised for the team, not changed:** visual consistency across the three demos, so styling doesn't sway the vote; one shared feedback question across all three; and two overlapping research folders. Haydn's later reorganization resolved the folders by consolidating them into `docs/`.

---

## Prompt 5: Integrate with the team repository

```text
lets merge Haydn's branch into burak-dev and then push our work on top of it. Then I can check
out C myself and see if we want to PR
```

**Trying to learn:** Does C fit cleanly into the shared repository structure Haydn set up (one independent Streamlit app per folder, each with its own port and Cloud deployment), so all three demos can be run and deployed side by side?

**What changed:** Merged Haydn's branch into `burak-dev` (clean merge). Replaced the empty `prototypes/prototype-c/` placeholder with this folder, and added C to the root README (prototype table, run commands, deploy table, tests), the `Makefile` (`make demo-c`, `make test-c`) and `requirements-dev.txt`. Ran all three test suites before pushing.

---

## Prompt 6: Compare deployment readiness across A, B and C

```text
ok so talking about everything on main and my PR. are all deployed to the same extent. like is
proto A already on streamlit. are B and C. like is anything fundamentally different.
```

**Trying to learn:** Are the three demos equally ready for a shareable class link, and is anything fundamentally different between them?

**What came back (no code changes):**
- **None of the three is deployed yet.**
- **All three deploy the same way:** one Streamlit Cloud app per folder.
- **Recommendation:** merge first, then deploy all three from `main`, and open the links shortly before class because idle apps go to sleep.
- **One real difference:** A's revised results now show acuity labels such as "20/20 · Normal vision", derived from fixed, uncalibrated letter sizes. These could contradict C's calibrated verdict during a live demo.

A's prompt log records those labels as a deliberate PM decision, so this was raised as a team discussion rather than changed. The updated A suite passed 51/51.

---

Repository requests from this chat (opening PR #3, and adding C to the shared [`prompts.md`](../../prompts.md)) are logged there under shared repository work (R6–R7).

## Prompt 7: Add states whose line isn't 20/40

```text
maybe the demo should include Georgia NJ and Wyoming since those are the non 20/40 states. If we
push will it end up on stream lit automatically?
```
```text
yes do that.
```

**Trying to learn:** All five original states used 20/40, so in a live demo the state picker looked cosmetic. Would adding states with a different line make "your state's *real* standard" visible?

**What we found:**

| State | Official source says | Decision |
|---|---|---|
| Georgia | 20/60 in at least one eye (GA DDS) | Added |
| New Jersey | 20/50; if you fail, visit a doctor and complete Form ST-14 (NJ MVC) | Added |
| Wyoming | 20/40 with both eyes (WYDOT form, 2014) | Not added: the same line as the others |

**What changed:**
- Georgia's 20/60 line is slotted into the letter scale only for states that use it, so the 20/40 test is unchanged (covered by a test).
- Georgia's page names no form for failing the acuity part, so the app only suggests asking about its Vision Report Form (DDS-MR-274).
- 4 new tests, for 31 in total.
- The demo script now switches the state to Georgia so the class sees the line change.

**On deployment:** Streamlit Community Cloud redeploys automatically when the branch it is deployed from changes, which is `main`. So this change reaches the live link only once its pull request is merged.

---

Requests from this chat about the presentation draft and demo script are logged under shared repository work in [`prompts.md`](../../prompts.md) (R8).

## Prompts 8+ (add as we iterate)

Log each new prompt here in the same format: the prompt, what we were trying to learn, and what changed. Likely next ones:
- Rehearsal fixes after the first dry-run demo
- Changes based on early feedback from real users (ideally 2–3 students with a DMV visit coming up)
