"""Parent note, next steps and reminders for Focal Family.

Nothing here interprets the vision task clinically. The parent's reason for checking and
their own observations drive the suggested next step, never the task score. Observation,
next-step and question wording comes from Prototype B (demo.py).
"""

from datetime import datetime, timezone

CHILD_LABELS = ("Child A", "Child B", "Child C")
AGE_GROUPS = ("4–6", "7–10")
REASONS = (
    "A school vision letter came home",
    "A teacher or doctor mentioned a concern",
    "I've noticed something at home",
    "Just a routine check-in",
)
OBSERVATIONS = (
    "Squinting or moving closer to see",
    "Mentions blurry print or screens",
    "Has trouble staying with the activity",
    "A teacher or school has raised a concern",
)
TIMING = ("Within the past week", "Within the past month", "Longer than a month", "Not sure")
NEXT_STEPS = (
    "Prepare for an eye appointment",
    "Ask about a school screening",
    "Keep a copy of my observations",
    "I'm not sure yet",
)
QUESTION_OPTIONS = (
    "What did the school screening cover, and what follow-up was suggested?",
    "What information should I bring to an appointment?",
    "How can I describe the changes I've noticed clearly?",
    "Who should I contact if I have more questions?",
)
RECIPIENTS = ("School nurse", "Eye doctor", "Just for my records")
REMINDERS = ("Tomorrow", "In 3 days", "In 1 week")


def concern_already_raised(reason):
    """A school letter or a teacher/doctor concern is a referral the task must never cancel."""
    return reason in REASONS[:2]


def suggested_next_step(reason):
    """Suggest from the parent's reason for checking. The task score is never an input."""
    if reason in REASONS[:3]:
        return NEXT_STEPS[0]
    return NEXT_STEPS[2]


def suggested_recipient(reason):
    return RECIPIENTS[0] if reason == REASONS[0] else RECIPIENTS[1]


def follow_up_tasks(next_step):
    if next_step == NEXT_STEPS[0]:
        return (
            "Find a provider and check which vision coverage they accept",
            "Choose an appointment time that works for our family",
            "Bring my observations and any school screening letter",
        )
    if next_step == NEXT_STEPS[1]:
        return (
            "Find the school screening letter or school nurse's contact details",
            "Write down the questions I want to ask",
            "Keep a copy of the school's response",
        )
    if next_step == NEXT_STEPS[2]:
        return (
            "Check that my observations describe what I actually noticed",
            "Download a copy of this note",
        )
    return (
        "Write down what would help me decide on a next step",
        "Save my observations to discuss with an eye-care professional",
    )


def check_line(summary):
    """One plain sentence about a practice check, always labelled as not a screening."""
    sizes = ", ".join(f"{row['Correct']}/{row['Trials']} at {row['Task size'].split()[0]} size"
                      for row in summary["levels"])
    return (f"At home we tried a practice direction task (not a vision screening): "
            f"{summary['correct']} of {summary['total']} directions matched ({sizes}).")


def questions(note):
    result = list(note.get("questions", []))
    if note.get("custom_question", "").strip():
        result.append(note["custom_question"].strip())
    return result


def build_message(note, check_summary=None):
    """Draft a parent-controlled message. The parent edits it and decides whether to send it."""
    recipient = note.get("recipient", RECIPIENTS[2])
    reason = note.get("reason", REASONS[3])
    if recipient == RECIPIENTS[0]:
        opening = ("Hello, I'm following up on the vision screening letter that came home for my child."
                   if reason == REASONS[0] else "Hello, I'd like to talk about my child's vision.")
        closing = "Could you tell me what the screening found and what follow-up you recommend?"
    elif recipient == RECIPIENTS[1]:
        opening = "Hello, I'd like to arrange an eye appointment for my child."
        closing = "Please let me know available times, what to bring, and which vision coverage you accept."
    else:
        opening = "Notes about my child's vision."
        closing = f"Next step I chose: {note.get('next_step') or 'not decided yet'}."

    lines = [opening, "", f"Age group: {note.get('age_group', 'not given')}", f"Why I'm checking: {reason}"]
    observations = note.get("observations", [])
    lines += ["", "What I've noticed:"]
    lines += [f"- {item}" for item in observations] or ["- Nothing specific yet."]
    lines.append(f"When I noticed it: {note.get('timing', TIMING[3])}")
    if note.get("notes", "").strip():
        lines.append(note["notes"].strip())
    if check_summary and note.get("include_check"):
        lines += ["", check_line(check_summary)]
    if questions(note):
        lines += ["", "Questions I'd like to ask:"]
        lines += [f"- {q}" for q in questions(note)]
    lines += ["", closing]
    if note.get("fictional"):
        lines.insert(0, "FICTIONAL EXAMPLE, for demonstration only.\n")
    return "\n".join(lines)


def build_summary(note, message, check_summary=None, history_line=None, reminder=None):
    """Take-home text file: the parent's own answers plus clearly labelled task results."""
    lines = [
        "FOCAL FAMILY | TAKE-HOME NOTE",
        "Academic product prototype. Not a vision screening, diagnosis or medical result.",
        f"Created (UTC): {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Data: {'Fictional example' if note.get('fictional') else 'This session'}",
        f"Child label: {note.get('child', 'not given')} · Age group: {note.get('age_group', 'not given')}",
        f"Why I'm checking: {note.get('reason', 'not given')}",
        "",
        "WHAT I'VE NOTICED",
        *(note.get("observations") or ["Nothing specific yet."]),
        f"When: {note.get('timing', TIMING[3])}",
        f"Notes: {note.get('notes', '').strip() or 'None added.'}",
        "",
        "PRACTICE TASK",
        check_line(check_summary) if check_summary else "No practice task completed in this session.",
    ]
    if history_line:
        lines.append(history_line)
    lines += [
        "Task results can reflect attention, guessing, learning and setup. A good result does not",
        "rule out an eye problem or cancel a school or professional referral.",
        "",
        f"MY NEXT STEP: {note.get('next_step') or 'Not chosen yet'}",
    ]
    done = note.get("tasks", {})
    lines += [f"[{'x' if done.get(task) else ' '}] {task}" for task in follow_up_tasks(note.get("next_step"))]
    if reminder:
        lines.append(f"Reminder chosen: {reminder.lower()} (prototype: no reminder is actually sent).")
    lines += ["", "MY MESSAGE", message, "", "Nothing has been booked or sent by this prototype."]
    return "\n".join(lines) + "\n"


def fictional_note():
    """A made-up, clearly labelled note for demos. Never mixed with a real session."""
    return {
        "fictional": True,
        "child": "Child A",
        "age_group": "7–10",
        "reason": REASONS[0],
        "observations": [OBSERVATIONS[0], OBSERVATIONS[3]],
        "timing": TIMING[1],
        "notes": "Moved closer to the TV after school. The letter asks for a full eye exam.",
        "next_step": NEXT_STEPS[0],
        "recipient": RECIPIENTS[0],
        "questions": [QUESTION_OPTIONS[0], QUESTION_OPTIONS[1]],
        "custom_question": "",
        "include_check": False,
    }
