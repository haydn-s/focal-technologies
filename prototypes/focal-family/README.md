# Focal Family: master prototype

> **Course:** Duke University · MENG 570 Product Management
> **Persona:** Parent Pat, a working parent of children aged 4–10 (the investor pitch's user)
> **Built by:** Burak Donbekci (CTO), with Claude Code
> **Status:** proposed replacement for the investor demo. The pitch currently demos Prototype B on `focal-family-updates`.

Focal Family helps a parent act after a school vision letter or a concern. A parent and child do a short check together at home, compare checks over time, and leave with a note ready for the school nurse or eye doctor. It is free for families. Schools would pay, under a proposal in the investor pitch.

## Why a master prototype

Prototype C won the class vote. The team's view is that C's **delivery and polish** won the vote, while the investor pitch is about the **family** story (Prototype B). The master keeps C's look and its trust patterns, and moves them onto B's family product. It also adds A's comparison over time.

| From | What the master keeps |
|---|---|
| **C · DMV Pre-Check** | The look: centered layout, navy cards, step bar. Also: card-based screen calibration and set distance, a setup checklist that locks the Start button, "Can't tell" counting as a miss, one clear headline result, a numbered next-step plan, simulated reminders, and plain "what this is not" limits |
| **B · Focal Family** | The persona and story: parent and child together, child labels instead of names, and the reason for checking (school letter, concern). Also: the parent's observations, next steps, prepared questions, an editable message and a take-home note. **B's check-and-history engine (`vision.py`) is copied unchanged**, so a history saved in B restores here |
| **A · Focal Monitor** | Results over time: 7, 30 and 90-day windows, change against the previous window, a trend chart, and a clearly labeled fictional history |

## The journey (matches the pitch's demo order)

1. **Welcome:** "Got a school vision letter? Make the next step easy." Three promises, how it works, and expanders for *Why trust this*, *What this is not* and *For schools (proposed pilot)*.
2. **Set up:** child label and age group, **why you're here**, eyes, glasses, card calibration, screen, distance, and a 4-item checklist.
3. **Practice:** one large E. The real check starts only after a correct practice answer.
4. **Check:** 12 letters in three sizes (large, medium, small), with "Can't tell", Pause/Resume and Discard.
5. **Result:** "Child A matched 10 of 12 directions" with a bar for each size. If a school or professional already raised a concern, an amber card says **keep that follow-up**: a practice check can't cancel a referral.
6. **History:** saved checks or the fictional example; time windows, change against the previous window, a chart, a dated table, and JSON export/restore.
7. **Note:** observations, the next step (suggested from the reason for checking, never from the score), a plan with ticks, reminders, the recipient (school nurse, eye doctor or my records), questions, and a draft that **updates as you answer until you edit it**. Downloads a take-home note.

## Product decisions

- **The next step comes from the parent, not the score.** This keeps the boundary from B and the pitch. A good result never says "you're fine". A school letter always leads to "keep the follow-up".
- **One clear headline, no verdict.** C's clarity, without C's pass/fail. Children have no single DMV-style line, and the pitch's top risk is that "parents mistake play for screening".
- **Cut on purpose:**
  - **B's picture-matching game:** the pitch demo uses the direction task, and practice covers "play together".
  - **C's state rules:** they don't apply to children.
  - **A's separate single-vs-trend screen:** the history page covers it.
  - **B's feedback form:** the next evidence is a pilot, not a class poll.
  - **A school or nurse view:** the pitch lists partner reporting as future work, so only a labeled "proposed pilot" expander is included.

## Clinical boundaries

This is a student prototype, not a vision screening, diagnosis or medical device. The 20/80, 20/40 and 20/20 labels describe letter size, not acuity. Attention, guessing, learning and setup change results. No age-specific pass threshold is applied. Fictional history and the fictional note are opt-in, labeled on screen and in downloads, and never enter live history or exports. B's README covers the same limits in more depth, with sources.

## Run it locally

From the repository root (port 8504, so A, B and C can run on 8501–8503):

```bash
python -m pip install -r prototypes/focal-family/requirements.txt
python -m streamlit run prototypes/focal-family/app.py --server.port 8504
```

Tests (24: next-step logic, message and take-home note, history compatibility with B, and every click path using Streamlit's AppTest):

```bash
cd prototypes/focal-family
python -m unittest discover -p 'test_*.py'
```

## Deploy

Create a new Streamlit Community Cloud app from this repository, with main file path `prototypes/focal-family/app.py`. It updates automatically when its branch changes. No secrets or database are needed.

## Three-minute investor demo

This follows the pitch's existing run of show for slide 5, the same steps and presenters, in this app:

| Clock | Presenter | What to do |
|---|---|---|
| 0:00–0:35 | Qingyi | **Start a check together**, show the setup with the reason "A school vision letter came home", tick the 4 boxes, and do the practice letter |
| 0:35–1:20 | Qingyi | Answer the 12 letters, tapping **Can't tell** once on a small letter |
| 1:20–1:30 | Qingyi | Show the result and the amber "keep the follow-up" card, then **Save and see your history** and hand over |
| 1:30–1:55 | Burak | Point to the new saved check; a comparison needs earlier checks |
| 1:55–2:25 | Burak | Switch to **Fictional example**, then compare 7, 30 and 90 days, and say it's made up |
| 2:25–2:40 | Burak | Back to **My saved checks**, then open **Keep or restore your history** |
| 2:40–3:00 | Burak | **Turn this into a parent note**, then **Fill with a fictional example**, show the draft and the plan, and return to the slides |

Keep a second tab already on a finished note in case live answering runs long. Open the app a few minutes early, since sleeping apps take time to wake.
