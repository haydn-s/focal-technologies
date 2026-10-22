# Focal Monitor — Prototype A

> **Product:** Focal Monitor — Prototype A  
> **Course:** Duke University • MENG 570 (Product Management)  
> **Target Persona:** Riley  
> **Customer Segment:** Adults who wear glasses or contact lenses and are concerned about changes in their vision between professional examinations.  
> **Core Hypothesis:** Users will perceive additional historical tracking context as more useful than an isolated demonstration result. *(Adults concerned about changes in their vision will perceive ongoing vision tracking as more useful than receiving a single test result.)*

---

## Executive Summary & Core Requirements

### Core Features
- **Interactive eight-question demonstration check:** High-precision vector SVG Tumbling-E optotypes with randomized orientations, fixed scaling progression demonstration, and idempotent directional buttons.
- **Single Result versus Trend Tracking comparison:** Controlled A/B exposure evaluating the exact same visual-acuity result in an isolated snapshot card versus a longitudinal baseline trend chart.
- **Clearly labeled fictional historical data:** 7 weeks of historical baseline records labeled explicitly as `"Illustrative Demo Data"` for persona Riley, strictly separated from live user session data.
- **Neutral feedback questionnaire:** 4 neutral, non-leading questions with no positive defaults (`index=None`), mandatory dual-view exposure verification, and post-submission lock.
- **Feedback JSON export:** Anonymous structured payload export for product management research analysis.

### Prototype Scope
- **Familiar result language:** The eight-item interaction maps performance to visual-acuity-style results from `20/20` through `20/200` so the demo reads like a vision product rather than a quiz.
- **Consistent presentation:** The immediate result, single-result view, trend view, data table, tooltips, and feedback export all use the same acuity result.
- **Research focus:** The experiment assesses stated user preferences and immediate perceived usefulness of the two presentation formats.

---

## 1. Product Context & Objectives

### The Problem
Adults who wear corrective lenses (glasses or contact lenses) frequently experience temporary eye strain, fatigue, or subtle changes in visual clarity between their annual or bi-annual professional eye exams. When faced with an isolated vision fluctuation, patients often struggle to differentiate between transient digital eye strain and progressive refractive drift. A single snapshot vision test can cause false alarm or false confidence.

### The Solution: Focal Monitor
**Focal** is a proposed at-home digital vision monitoring tool designed to track visual clarity trends longitudinally. Rather than relying on an isolated test score, Focal provides a regular cadence of interactive checks to establish a personal baseline and visualize changes over weeks and months.

### Target Persona: Riley
- **Demographics:** 34-year-old product analyst, wears daily soft contacts and computer glasses.
- **Customer Segment:** Adults who wear glasses or contact lenses and are concerned about changes in their vision between professional examinations.
- **Pain Point:** Notices occasional blurring or headaches during intensive laptop work. Wondering whether their prescription has changed or if it's just screen fatigue.
- **Goal:** Wants reliable self-tracking to decide whether to book an early optometrist checkup or continue with their scheduled annual appointment.

---

## 2. Four Interactive Steps

The prototype is built with a strictly managed, sequential state machine using `st.session_state`:

```
[ Step 1: Welcome & Setup ] 
             ↓
[ Step 2: Vision Check (8 Tumbling-E Items) ] 
             ↓
[ Step 3: Immediate Vision Result ]
             ↓
[ Step 4: Vision History & Hypothesis Feedback ]
```

### Step 1: Welcome & Setup
- **Product Overview:** Explains the premise of at-home baseline tracking between eye exams.
- **Testing Environment Instructions:**
  1. **Corrective Lenses:** Keep glasses or contacts on throughout the check.
  2. **Viewing Distance:** Sit approx. arm's length (20–24 in / 50–60 cm) from the display.
  3. **Room & Screen Lighting:** Ensure comfortable lighting with minimal glare.
  4. **Task Instruction:** Identify which direction the 3 prongs of the Tumbling 'E' are pointing.
- **Action:** Prominent "Start Vision Check" button initiates the flow.

### Step 2: Interactive Vision Check
- **8 Tumbling-E Optotypes:** Standard 5×5 Snellen optotype proportions generated in high-precision, sharp vector SVG.
- **Randomized Orientations:** Random assignment across `Up`, `Right`, `Down`, and `Left`.
- **Fixed Size Progression Demonstration:** Optotypes follow a fixed sequence of 8 size levels (130px down to 40px) across questions to illustrate UI scaling demonstration, rather than dynamic response-adaptive difficulty.
- **Ergonomic Directional Controls:** Clickable buttons (`⬆️ Up`, `⬅️ Left`, `➡️ Right`, `⬇️ Down`).
- **Duplicate Submission Prevention:** Button keys update dynamically with the question index, and clicks immediately advance `current_question_index` before subsequent interactions can register.
- **Live Progress:** Shows `Question X of 8` and dynamic progress bar.

### Step 3: Vision Result
- **Completion Verification:** Shows completed-session results only when all 8 unique, schema-valid questions have been answered and an authentic completion timestamp parsing strictly against `%Y-%m-%d %H:%M` is stored. Boolean values are explicitly rejected as question IDs. Malformed, corrupted, or incomplete records are safely handled without `KeyError` or `TypeError`: valid 1–7-answer sessions provide a **Resume Test** button to continue from the next unanswered question, while corrupted data provides a clear restart option.
- **Visual-Acuity Result:** Translates the completed check into a familiar result (for example, `20/20 · Normal vision`) with the verified completion timestamp.
- **Question Breakdown:** Expandable table showing target orientation, user response, scale level, and match status.
- **Action:** Button to proceed to the Vision History view.

### Step 4: Compare Results & Neutral Feedback
- **Neutral & Balanced Comparison:**
  - Evaluators compare two distinct result presentation paradigms using the **exact same underlying visual-acuity result** (for example, `20/25`):
    - **Single Result:** Displays an isolated result card and an optional 8-question breakdown table. It does *not* include any historical baseline or trend line.
    - **Trend Tracking:** Displays the identical result in a longitudinal context alongside Riley's 7-week fictional baseline, featuring an interactive acuity trend chart and one tabular drawer.
  - **Identical Visual Card:** Both experiences render the exact same styled current-result card with acuity, status, date, and a short explanatory sentence. Neither experience is framed as superior or preferred.
  - **Randomized Assignment Preserved:** When proceeding from Step 3 via **Compare Results**, the initial view is randomized **once per evaluation**. The assigned order is stored in session state and preserved across reruns, view toggles, and page re-entry.
  - **Mandatory Dual-View Exposure:** Evaluators must visit both **Single Result** and **Trend Tracking** before comparative feedback can be submitted.
  - **Direct View Switching:** Evaluators switch between formats through one compact segmented presentation control, avoiding duplicate navigation controls while preserving exposure tracking.
- **Longitudinal Trend Chart (Altair in Trend Tracking):**
  - Displays **7 weeks of clearly labeled fictional baseline records** designated as **"Illustrative Demo Data"** for persona Riley.
  - **Data Integrity & Exclusion of Incompletes:** Incomplete sessions (0–7 answers) and corrupted records are strictly excluded from the trend chart to protect longitudinal data integrity. If a test is incomplete, a banner and "Resume Test" button are displayed; if corrupted or unstarted, only baseline illustrative data is shown without crashing.
  - **Completed Live Check Integration:** Only an actual completed 8-question check meeting strict validation criteria (exact integer IDs 1–8, valid schema types, and verified timestamp) appears on the chart and table, labeled **"Your Completed Demo Check"** with recorded date derived from its validated completion timestamp. No fabricated placeholders or partial scores are ever presented as live user data.
  - **Visual Separation:** Previous results use a smooth blue trend with subtle area shading; the live result is highlighted with a labeled coral diamond.
  - **Acuity Scale & Clean Legend:** The chart Y-axis uses familiar result bands from `20/20` through `20/200`, with an untruncated legend.
  - **Single Tabular Record Display:** An expandable drawer provides a single clean tabular summary of historical and completed live records.
  - Interactive tooltips display session details, date, visual-acuity result, classification, and context notes.
- **Neutral Hypothesis Evaluation Questionnaire & Feedback Locking:**
  - Designed without leading wording or positive defaults (`index=None`):
    1. *Preferred Format:* Which format did you find more useful for monitoring your vision? (5-point: Experience A / Experience B / Both equally / Neither / Not sure)
    2. *Primary Rationale:* What was the main reason for your preference? (Open-ended text area)
    3. *Clarity at a Glance:* Which format was easier to understand at a glance? (5-point: Experience A / Experience B / Both equally / Neither / Not sure)
    4. *Return Intent:* How likely would you be to use a vision-tracking tool like this regularly? (5-point: Very unlikely to Very likely)
  - **Strict Validation:** Questions 1, 3, and 4 are required; incomplete submissions display an alert without recording partial responses.
  - **Original Feedback Preservation & Post-Submission Lock:** Upon first valid submission, feedback is locked (`feedback_locked: True`). The editable form is completely replaced by a read-only summary card, a JSON download button, and a research debrief card. Participants cannot alter their responses after viewing the hypothesis. Revisiting the page preserves the locked state; the lock clears only upon Reset or starting a new evaluation.
  - **Anonymous Download:** Evaluators and researchers can download the submission payload as JSON (`focal_monitor_anonymous_feedback.json`) containing responses, exposure tracking, and assignment metadata.
  - **Hypothesis Masking & Debrief:** The research hypothesis is strictly masked in the header, Welcome screen, and sidebar navigation prior to feedback submission to reduce demand characteristics; upon submission, the debrief card and updated sidebar reveal the hypothesis and study purpose.
- **Working Reset Demo Button:** Restores session state to Step 1 with a new randomized question set, clearing all live session results, comparison assignment, exposure tracking, and submitted feedback, re-masking the hypothesis.

---

## 3. Hypothesis Validation & Research Methodology

### 3.1 Core Hypothesis
> *“Adults who suspect their vision is changing will find ongoing vision tracking more useful than receiving a single test result.”*

In consumer digital health, product development teams frequently take for granted that "more data and longitudinal tracking is always better." However, continuous tracking can also induce cognitive fatigue, anxiety over non-clinical fluctuations, and user churn. This prototype explicitly evaluates whether corrective-lens wearers (persona Riley) genuinely prefer longitudinal trends over a simple, fast snapshot check.

### 3.2 Mitigating Evaluation Bias & Research Guardrails
1. **Hypothesis Masking:** Neither the Welcome screen nor the initial sidebar discloses the hypothesis, avoiding priming or demand characteristics.
2. **Order Randomization Preserved per Evaluation:** When moving from Step 3 to Step 4, the initial view (Experience A vs Experience B) is randomized 50/50 and strictly preserved in session state across reruns, view toggles, and re-entry. It is only reassigned on an explicit Reset or a new evaluation. Evaluators navigating via the sidebar are tracked as `"researcher_sidebar"` rather than `"participant_randomized"`.
3. **Mandatory Dual-View Exposure:** Evaluators must visit both Experience A and Experience B before feedback submission is accepted; early submission attempts present a neutral notice without clearing inputs.
4. **Identical Underlying Demo Score & Visual Emphasis:** Both Experience A and Experience B evaluate the exact same score from the current session (or Riley's 7/8 demo check if testing directly) and display identical score cards and identical non-clinical limitation callouts.
5. **Neutral, Non-Leading Questions:** All survey options include neutral and negative choices ("Both are equally useful", "Neither is useful", "Not sure"), with no pre-selected positive defaults (`index=None`).
6. **Post-Submission Locking & Debrief:** Evaluators are informed of the hypothesis and product rationale only *after* recording their feedback. Upon submission, the form locks to preserve the authentic pre-debrief response and prevents post-hoc editing.

### 3.3 Known Presentation Biases & Research Limitations
- **Stated Preference vs. Demonstrated Long-Term Retention:** The prototype investigates *stated presentation preference* and *perceived immediate usefulness*, not demonstrated longitudinal behavioral retention, adherence, or health outcomes over months of real-world use.
- **Prior Score Exposure in Step 3:** Randomizing comparison order does not eliminate every source of presentation bias. In the linear flow, participants necessarily view an isolated single score in Step 3 before proceeding to the comparative Step 4. This prior exposure to the isolated score format is an inherent, acknowledged limitation of the evaluation flow.
- **Temporary Session Memory:** All user progress and feedback responses are stored in transient `st.session_state`. No external database or persistent cloud storage is connected. Researchers and evaluators **must download the JSON feedback export before resetting the demo or closing the browser session**, as resetting permanently wipes session memory.
- **Free-Text Anonymity Boundaries:** The prototype does not collect usernames, emails, IP addresses, or browser fingerprints. However, complete anonymity cannot be guaranteed if participants voluntarily enter identifying personal information (such as their full name or contact info) into the free-text rationale field.
- **Simulated Baseline Data Limits:** Fictional baseline records represent 7 weekly sample tests for the fictional persona Riley. They are explicitly labeled **"Illustrative Demo Data"** to ensure evaluators understand they are not real clinical measurements. If a user completes a live session, their score is rendered as an isolated comparison point without connecting trend lines, preventing false perceptions of clinical continuity. No participant data or research conclusions are fabricated.

---

## 4. What Conclusions Can and Cannot Be Drawn

### Conclusions That CAN Be Drawn:
- **Stated Presentation Preference:** Whether target users state a preference for contextual history over isolated scores when evaluating at-home visual checks immediately after exposure.
- **Perceived Cognitive Load & Utility:** User feedback on whether longitudinal charts clarify or complicate their understanding compared to single score cards at a glance.
- **Self-Reported Intent to Return:** Stated likelihood of adult corrective-lens wearers returning periodically for at-home checks.
- **Qualitative User Motivations:** Nuanced qualitative rationale on what information users feel is necessary before scheduling a professional eye exam.

### Conclusions That CANNOT Be Drawn:
- **No Demonstrated Long-Term Retention:** Stated survey intent does not prove longitudinal user retention, habitual compliance, or sustained engagement over weeks or months in real-world scenarios.
- **No Complete Elimination of Presentation Bias:** Randomizing presentation order in Step 4 does not neutralize the anchoring effect of viewing an isolated score in Step 3.
- **No Clinical Efficacy or Diagnostic Accuracy:** The prototype cannot determine whether at-home tracking improves clinical visual acuity, detects refractive error shifts, or identifies ocular disease earlier.
- **No Hardware Universality:** Uncalibrated consumer monitors, varied room lighting, and uncontrolled viewing distances prevent generalizing test performance across physical environments.

---

## 5. Technical Requirements & Architecture

- **Language:** Python 3.10+ (tested on Python 3.13)
- **Frameworks:** Streamlit (`>=1.35.0`), Pandas (`>=2.0.0`), Altair (`>=5.0.0`)
- **State Management:** Fully driven by `st.session_state` (no external databases, local storage cookies, or paid APIs).
- **Design System:** Healthcare dashboard theme inspired by modern clinical software (soothing Slate/Cyan palette, Inter typography, accessible contrast, alert containers).
- **Evaluator Sidebar Navigation:** A "Jump directly to step" dropdown allows evaluators and peer reviewers to test any screen instantly.

---

## 6. Local Execution Instructions

### Prerequisites
- Python 3.10 or later installed on your machine.

### Step-by-Step Setup

1. **Clone or navigate to the repository directory:**
   ```bash
   cd prototypes/prototype-a-riley-vision-tracking
   ```

2. **(Optional) Create and activate a virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit app (Entry Point):**
   ```bash
   streamlit run app.py
   ```

5. **Open in your browser:**
   Streamlit will automatically open the application at:
   ```
   http://localhost:8501
   ```

### Running Test Suites
Automated unit tests and regression tests are included:
```bash
python -m unittest test_app.py
python -m unittest test_regression.py
```

---

## 7. Prototype Data Principles

1. **No account required:** The prototype runs as a temporary session and asks for no name or login.
2. **Consistent result mapping:** All result surfaces use the same `20/20`–`20/200` demo mapping.
3. **Temporary session memory:** Results and survey responses reside in volatile `st.session_state`; researchers can download the feedback JSON before resetting or closing the session.
4. **Clearly separated sample history:** Riley's seven historical records remain labeled as illustrative demo data, while a completed live check is labeled as the user's current reading.

---
