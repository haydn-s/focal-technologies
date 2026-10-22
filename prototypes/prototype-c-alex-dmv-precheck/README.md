# Focal DMV Pre-Check: Prototype C

> **Course:** Duke University · MENG 570 Product Management
> **Target persona:** Anxious Applicant Alex, a college student getting a first driver's license
> **Built by:** Burak Donbekci (CTO), with Claude Code
> **Core hypothesis:** People with a DMV vision screening coming up will prefer, and act on, a free check that answers *"Will I pass my state's test?"* with a clear next step, over a general vision score.

---

## 1. The idea in one line

**"Will you pass the DMV eye test?"** Find out in about two minutes, before you wait in line. The check measures you against **your state's actual standard** and tells you what to do next.

This is the free **"Will I pass my DMV eye test?" checker** from our Lean Canvas *Channels* box, built so people can try it.

## 2. Hypothesis and how we'll know

| | |
|---|---|
| **We believe** | First-time license applicants like Alex want to know whether they'll pass *before* they go to the DMV. |
| **We'll build** | A free, about-2-minute check against their own state's line (20/40), with a pass, close or not-yet answer and a concrete next step. |
| **We'll know we're right if** | (proposed targets, for the team to confirm) |
| | • At least 60% of people with a DMV visit coming up say they'd likely use it before going |
| | • At least 70% say they knew whether they'd pass after the check |
| | • At least 50% of people told to "see an eye doctor first" say they'd book before their DMV visit |
| | • Most rate it *more useful* than an online test that just gives a score like "20/30" |
| | • The class vote picks C as the one they would actually use |
| **Riskiest assumption** | That a DMV visit is enough of a trigger. Alex said the **road test** worries him more than the vision screening ("more of a background worry"), so vision anxiety alone may not drive use. |

The feedback page asks these questions directly and exports the answers as JSON.

### How C differs from Prototypes A and B

The three demos sit on a spectrum of **how much the product judges for you**:

| | **A: Focal Monitor (Riley)** | **B: Focal Family (Pat)** | **C: DMV Pre-Check (Alex)** |
|---|---|---|---|
| Who decides what it means | The user reads a trend | **The parent** (no score at all) | **The product**, against a named external rule |
| Use pattern | Ongoing, repeated checks | A shared parent-and-child moment | **One check, triggered by a deadline** |
| Core value | See change over time | Turn observations into a prepared next step | **Certainty before an event** |
| Measurement | Demo score | None, on purpose (fixed-size pictures) | **Calibrated letter sizes, 20/x lines** |
| Business role | Premium personal tracking | Parent and pediatric channel | **Free acquisition channel**; later a DMV/agency partnership |
| What the vote tells us | Does tracking beat a single result? | Do parents value preparation over measurement? | **Does a concrete, deadline-tied verdict beat open-ended monitoring?** |

If the class picks C, it says people want Focal to give a clear answer. If they pick B, they want support, not judgment. If they pick A, the value is in tracking over time.

## 3. Built from Alex's interview (customer discovery, Burak)

Every feature traces back to something Alex said:

| What Alex said | What the prototype does |
|---|---|
| "It gave me something like '20/30,' and I didn't even know if that's a pass or a fail." | The result is a **plain answer against your state's line**, never a bare number. |
| "I had to google what the DMV standard is, and the first answers were for a different state." | **State picker** with the real rule and a link to the official source (NC, CA, NY, TX, FL). |
| "My laptop and my phone are different sizes, so I didn't know if the letters were the right size." | **Screen calibration**: match an on-screen box to any ID card, and letters are sized in real millimetres. |
| "The instructions said to stand a certain distance away... I just guessed." | **Distance step** (10 ft or 5 ft) with letters re-sized for the distance you pick. |
| "I guessed on that last line and passed... I don't know if I passed because my eyes were fine or because I got lucky." | **No lucky guesses:** 6 letters at the deciding line, plus a "Can't tell" button. A pure guesser gets "on track" less than 1% of the time. |
| "If I do it twice and get two different answers, I'm done with it." | **One honest retake.** Both results are shown side by side; if they disagree, the app says so and recommends an eye doctor, rather than keeping the better score. |
| "One of the sites had a big 'buy glasses' button..." | **No ads, no store, no sign-up.** Stated up front. |
| "I'd want to know upfront what it would cost." | "Free" on the first screen; the next steps say to **ask for the exam price before booking**. |
| "If it told me I'd probably fail... I'd sit on it for a while." | **"Remind me to book"** buttons (simulated) and a numbered plan, not just a verdict. |
| "I don't have an eye doctor... figure out insurance... call my mom about the insurance card." | Next steps point to **campus health or a nearby optometrist**, plus a **pre-written message to a parent** asking for the insurance card. |
| "It'd have to be legit enough that it ends the conversation at home." | A **copyable summary** (date, state, letters read, setup) for a parent or eye doctor. |

It also draws on **Lisa** (DMV supervisor, virtual interviews). Her insight was that a failed screening costs the agency roughly two transactions. So the prototype is built to catch likely fails *before* the counter, and it names the exact eye-doctor form each state uses (DL 62, MV-619/MV-80L, Form 72010). Because Lisa said *"If I can't put a face to the result, it's not evidence,"* the check never claims to be an official result.

## 4. Feature Scope Card

| Feature | Value | Effort | In? | Why |
|---|---|---|---|---|
| State-specific pass line and source | High | Low | ✅ | Alex's #1 ask |
| Screen and distance calibration | High | Medium | ✅ | Fixes "different sizes, different results" |
| Extra letters at the deciding line, plus "Can't tell" | High | Low | ✅ | Fixes "I got lucky" |
| Clear verdict plus next-step plan | High | Low | ✅ | Riley and Alex: "a next step, not a score" |
| One retake, shown honestly | Medium | Low | ✅ | Consistency builds trust |
| Reminder, parent message, summary | Medium | Low | ✅ | Booking stalls without a nudge |
| In-app feedback form with export | High (for us) | Low | ✅ | Measures the hypothesis |
| Testing each eye separately | Medium | Medium | ❌ | Doubles test time; CA and TX check each eye, so it's flagged in "Limits" |
| Real reminders (email/SMS), accounts | Low now | High | ❌ | Needs personal data; intent is all we need to measure |
| Real eye-doctor search, insurance lookup, booking | High later | High | ❌ | Partnerships first (Hill 3); a map link stands in |
| Agency view for Lisa | Medium | Medium | ❌ | Lisa is still unvalidated; would dilute the consumer test |
| All 50 states | Medium | High (verification) | ❌ | 5 states verified, plus a clearly labelled "Another state" fallback |
| Night, glare, side or color vision | Medium | High | ❌ | Not what the DMV counter checks; disclosed |

## 5. The flow

1. **Welcome:** the promise, how it works, "Why should I trust this?" and "What this is not".
2. **Setup:** state (with rule and source), glasses yes/no, card calibration, distance, and a 3-item checklist that must be ticked before starting.
3. **Check:** about 14 Tumbling-E letters across 4 lines (20/70 → 20/50 → **20/40 × 6** → 20/30). Directions are random every time and never repeat twice in a row. The 20/30 line only appears after a clear pass, to measure how much room you have.
4. **Result:** On track, Right at the line, Might not pass yet, or Checks didn't agree. Shows what you read line by line, a next-step plan, the state's form, a reminder, a parent message, a summary to copy, and the limits.
5. **Feedback:** 6 neutral questions (no defaults selected), one optional text question, and a JSON download.

### State rules used (checked October 2026)

| State | Rule summary | Source |
|---|---|---|
| North Carolina | 20/40 in either eye or both together; below that, corrective-lens restriction | [19A NCAC 03B .0201](https://www.ncdot.gov/about-us/how-we-operate/policy-process/rules/Documents/19a-ncac-03b-0201-emergency-rule.pdf) |
| California | 20/40 both eyes, and 20/40 one eye with at least 20/70 in the other; otherwise DL 62 | [CA DMV](https://www.dmv.ca.gov/portal/?p=1733) |
| New York | 20/40 in either or both eyes; MV-619 or MV-80L from an eye doctor | [NY DMV](https://dmv.ny.gov/driver-license/vision-requirements-and-restrictions) |
| Texas | 20/40 each eye and both for no restriction; lower means a corrective-lens restriction or specialist referral | [37 TAC §15.51](https://www.law.cornell.edu/regulations/texas/37-Tex-Admin-Code-SS-15-51) |
| Florida | Minimum 20/70, but at 20/50 or worse a specialist must complete Form 72010 | [FLHSMV](https://flhsmv.gov/ddl/vision.html) |

All five draw the "pass at the counter with no extra steps" line at **20/40**. What differs is what happens if you miss it. That's why the state picker matters even though the line is the same.

## 6. Run it locally

From the repository root (port 8503, so A on 8501 and B on 8502 can run at the same time):

```bash
python -m pip install -r prototypes/prototype-c-alex-dmv-precheck/requirements.txt
python -m streamlit run prototypes/prototype-c-alex-dmv-precheck/app.py --server.port 8503
```

Run the tests (27 tests: scoring, letter sizing, state data, and every click path through the app using Streamlit's AppTest):

```bash
cd prototypes/prototype-c-alex-dmv-precheck
python -m unittest discover -p 'test_*.py'
```

## 7. Deploy (shareable link for class)

1. Push the branch to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and choose **Create app**.
3. Pick this repo and branch, and set **Main file path** to `prototypes/prototype-c-alex-dmv-precheck/app.py`.
4. Optionally set a custom subdomain such as `focal-dmv-precheck`.

The app needs no secrets, database or API keys.

## 8. Two-minute demo script

1. **Welcome (15s):** read the headline and point at the three chips. Open "Why should I trust this?" for one second.
2. **Setup (30s):** pick **North Carolina** and show the rule card with its source link. Hold up an ID card to the calibration box. Tick the three boxes.
3. **Check (45s):** answer a few letters, deliberately tap **"Can't tell"** on two or three at the 20/40 line, and finish.
4. **Result (30s):** "Right at the line" or "Might not pass yet". Scroll the plan: map link, the state form, the parent message, **Remind me in 3 days**.
5. **Close (10s):** "Same question every applicant has, answered against their own state's rule, with a next step instead of a number."

Tip: keep a second browser tab already on a passing result, in case live answering takes longer than planned.

## 9. Honest limitations

- A **non-clinical student prototype**. Not validated against clinical equipment; not an eye exam; not accepted by any DMV.
- Tests **both eyes together** only (some states also test each eye). No side, color, glare or night vision.
- Calibration depends on the user matching the card; viewing distance is self-reported.
- State rules are summaries of official sources, checked October 2026. The "Another state" option uses the common 20/40 line.
- Reminders are simulated; no data leaves the browser session unless the user downloads their feedback.
