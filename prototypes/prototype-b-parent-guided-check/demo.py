"""Session data and exports for Focal Family. No clinical scoring is performed."""

from datetime import datetime, timezone
import random

SYMBOLS = ("Circle", "Square", "Triangle", "Star")
ROUNDS = 6
OBSERVATIONS = (
    "Squinting or moving closer to see",
    "Mentions blurry print or screens",
    "Has trouble staying with the activity",
    "A teacher or school has raised a concern",
)
NEXT_STEPS = (
    "Prepare for an eye appointment",
    "Ask about a school screening",
    "Keep a copy of my observations",
    "I'm not sure yet",
)


def new_session():
    """Create an independent, balanced picture sequence on each explicit reset."""
    targets = list(SYMBOLS) + random.sample(SYMBOLS, 2)
    random.shuffle(targets)
    questions = []
    for target in targets:
        choices = list(SYMBOLS)
        random.shuffle(choices)
        questions.append({"target": target, "choices": choices})
    return {
        "step": "setup",
        "source": "current_session",
        "profile": {},
        "questions": questions,
        "answers": [],
        "observations": [],
        "timing": "Not sure",
        "notes": "",
        "next_step": None,
        "tasks": {},
        "summary_download_requested": False,
        "feedback": None,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def record_answer(session, question_index, choice):
    """Accept only the next unanswered picture, including an explicit skip."""
    if session["step"] != "game" or question_index != len(session["answers"]):
        return False
    if not 0 <= question_index < len(session["questions"]):
        return False
    question = session["questions"][question_index]
    if choice is not None and choice not in question["choices"]:
        return False
    session["answers"].append({
        "picture": question_index + 1,
        "target": question["target"],
        "choice": choice,
        "matched": choice == question["target"],
        "skipped": choice is None,
    })
    if len(session["answers"]) == len(session["questions"]):
        session["step"] = "observations"
    return True


def activity_counts(session):
    answers = session["answers"]
    return {
        "completed": len(answers),
        "matched": sum(answer["matched"] for answer in answers),
        "skipped": sum(answer["skipped"] for answer in answers),
        "total": len(session["questions"]),
    }


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
            "Download a copy of this summary",
        )
    return (
        "Write down what would help me decide on a next step",
        "Save my observations to discuss with an eye-care professional",
    )


def build_summary(session):
    """Export observations and the parent's own choice without a recommendation."""
    counts = activity_counts(session)
    profile = session["profile"]
    lines = [
        "FOCAL FAMILY | PARENT OBSERVATION SUMMARY",
        "Academic product prototype. This is not a vision screening or medical result.",
        f"Data: {'Fictional example' if session['source'] == 'fictional_example' else 'Current session'}",
        f"Session created (UTC): {session['created_at']}",
        f"Child label: {profile.get('label', 'Not supplied')}",
        f"Age group: {profile.get('age_group', 'Not supplied')}",
        f"Usual glasses during activity: {profile.get('glasses', 'Not supplied')}",
        "",
        "PICTURE MATCHING ACTIVITY",
        f"{counts['completed']} of {counts['total']} pictures completed; "
        f"{counts['matched']} matched; {counts['skipped']} skipped.",
        "Matching activity only. Attention, shape familiarity, and assistance can affect it.",
        "This activity cannot establish whether a child needs eye care.",
        "",
        "PARENT OBSERVATIONS",
        *(session["observations"] or ["No observations selected."]),
        f"When noticed: {session['timing']}",
        f"Additional notes: {session['notes'] or 'None added.'}",
        "",
        f"PARENT'S CHOSEN NEXT STEP: {session['next_step'] or 'Not selected'}",
    ]
    for task in follow_up_tasks(session["next_step"]):
        lines.append(f"[{'x' if session['tasks'].get(task) else ' '}] {task}")
    lines.extend(["", "No appointment has been booked or message sent by this prototype."])
    return "\n".join(lines) + "\n"


def fictional_example():
    session = new_session()
    session["source"] = "fictional_example"
    session["profile"] = {"label": "Example child", "age_group": "7–10", "glasses": "Yes"}
    session["step"] = "game"
    for index, question in enumerate(session["questions"]):
        record_answer(session, index, question["target"] if index < 4 else None)
    session.update({
        "step": "summary",
        "observations": [OBSERVATIONS[0], OBSERVATIONS[3]],
        "timing": "Within the past month",
        "notes": "Moved closer to a book after school. A screening letter came home.",
        "next_step": NEXT_STEPS[0],
    })
    return session
