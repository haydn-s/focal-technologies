# Prompt Log: Focal Family master prototype
> **Course:** Duke University · MENG 570 Product Management
> **Author:** Burak Donbekci (CTO), building with Claude Code
> **Started:** November 1, 2026

Each entry records what we asked the AI, **what we were trying to learn or decide**, and what changed. Prompts are quoted as typed.

---

## Prompt 1: Combine the prototypes around the investor story

```text
look through the current repo. especially the investor presentation branch. when we did our
prototype presentations my prototype C won but I think it was because of the delivery of the
presentation. And as you will see the investor presentation focuses on the family aspect. so lets
build a master prototype that combines the previous ones. Has the style of C but also has the focus
of the presentation etc. I think proto B was focused on the family aspect.
```

**Trying to learn:** Can one product carry what each prototype did best? That means C's clarity and polish (which won the vote), B's family story (which the pitch is built on), and A's comparison over time, all without breaking the pitch's honesty about what the product is not.

**What the AI did, and the decisions we reviewed:**
1. **Read the pitch first.** The `executive-pitch` and `focal-family-updates` branches give a 14-minute deck, Family only, with a 3-minute demo. Parents use it and schools would pay (proposed $2,400 per school per year). The pitch's top risk is that "parents mistake play for screening".
2. **Reused B's engine instead of rewriting it.** `vision.py` is copied unchanged (a test keeps it identical), so a history saved in B restores in the master.
3. **Took C's design system and trust patterns:** card calibration, the locked setup checklist, "Can't tell", one clear headline, a numbered plan and reminders.
4. **Kept C's clarity but not its pass/fail.** Children have no single legal line, so the headline is "matched 10 of 12 directions". The next step comes from the parent's reason for checking, never the score. A school letter always produces "keep the follow-up".
5. **Matched the pitch's demo order:** setup → practice → 12-letter check → save → history (live, then fictional, then export) → parent note.
6. **Cut on purpose:** B's picture game, C's state rules, A's separate comparison screen, the feedback form, and a school-facing view (labeled "proposed" only, matching the pitch).
7. **Fixed demo friction found while clicking through:**
   - Pages now open at the top, because Streamlit kept the previous page's scroll position.
   - The message draft now updates as the parent answers, until they edit it by hand.
   - The setup checklist drew only the first box until it was ticked.

**Verified:** 24 automated tests (next-step logic, message, take-home note, history compatibility with B, and every click path). Clicked through at desktop and phone sizes.

---

## Prompt 2: Keep the DMV check as an option, without losing focus

```text
is it still like C in fashion, maybe lets have the DMV element somewhere. like an option. but given
where the presentation focuses the protoype should focus there too.
```

**Trying to learn:** Can C's DMV check stay in the product without pulling attention from the family story that the pitch is built on?

**What changed:**
- **Kept the look:** the design system already came from C, unchanged.
- **Added the DMV pre-check as a secondary option.** An "Also from Focal: getting a driver's license in the family?" card sits below the family actions on the welcome page. It's framed for a teen's learner's permit or a parent's renewal, so it stays a family moment.
- **Copied C's tested logic (`dmv.py`):** all seven states, the 6-letter state line, the verdicts and the honest retake. The calibration and distance settings are shared with the family check.
- **Kept DMV results separate:** they never enter the family history. Starting from the welcome page always begins fresh.
- **6 new tests (30 total):** for example, that the family hero comes before the DMV card, that Georgia tests its 20/60 line, that a New Jersey miss names Form ST-14, that a retake is never combined into a better result, and that family history is untouched.

---

## Prompt 3: Take the React UI's look where it excels

```text
can you just make our demo like his where his excels?
```

**Trying to learn:** The team liked Qingyi's React UI (PR #10) for its look. Can this app get that look in a few hours before class, without losing what the React version lacks: calibrated letter sizes, history over time, and a note that never starts with made-up content?

**What the AI did:**
1. **Ran the React UI locally and clicked through it** to see what it does well: warm paper and navy palette, serif headlines, a top bar, a two-column welcome with an example plan card, chip-style choices, a room diagram, an arrow pad, result tiles and toasts.
2. **Brought those into this app** without changing its logic. A theme file next to `app.py` applies only here and keeps the app light even on a dark-mode laptop.
3. **Kept this app's substance:** card-calibrated letter sizes, 7/30/90-day history with export and restore, the "keep the follow-up" card, and an empty note unless the parent picks the labeled fictional example.
4. **Fixed a bug found while clicking through:** pages didn't always open at the top, because the browser reused the scroll helper's frame without running it again. The helper now changes on every page.

**Verified:** 32 automated tests (2 new: the theme stays light and scoped to this app; the scroll helper changes on every page). Clicked through welcome → setup → practice → check → result → history → note at desktop size, and checked the welcome page at phone size.

---

## Prompts 4+ (add as we iterate)

Log each new prompt in the same format. Likely next ones: team review against the pitch, deployment, and rehearsing the 3-minute demo.
