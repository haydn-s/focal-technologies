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
QUESTION_OPTIONS = (
    "What did the school screening cover, and what follow-up was suggested?",
    "What information should I bring to an appointment?",
    "How can I describe the changes I've noticed clearly?",
    "Who should I contact if I have more questions?",
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
        "practice_answer": None,
        "practice_complete": False,
        "practice_dismissed": False,
        "paused": False,
        "observations": [],
        "timing": "Not sure",
        "notes": "",
        "next_step": None,
        "tasks": {},
        "summary_download_requested": False,
        "questions_to_ask": [],
        "custom_question": "",
        "message_draft": "",
        "summary_revision": 0,
        "feedback": None,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def record_practice_answer(session, choice):
    if session["step"] != "game" or session.get("practice_dismissed") or choice not in SYMBOLS:
        return False
    session["practice_answer"] = choice
    session["practice_complete"] = choice == "Circle"
    return True


def begin_activity(session):
    if session["step"] != "game" or not session.get("practice_complete"):
        return False
    session["practice_dismissed"] = True
    return True


def set_activity_paused(session, paused):
    if session["step"] != "game" or not session.get("practice_dismissed") or type(paused) is not bool:
        return False
    session["paused"] = paused
    return True


def record_answer(session, question_index, choice):
    """Accept only the next unanswered picture, including an explicit skip."""
    if (session["step"] != "game" or not session.get("practice_dismissed")
            or session.get("paused") or question_index != len(session["answers"])):
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


def parent_questions(session):
    questions = list(session.get("questions_to_ask", []))
    if session.get("custom_question", "").strip():
        questions.append(session["custom_question"].strip())
    return questions


def build_parent_message(session):
    """Draft a parent-controlled note; activity answers never determine its advice."""
    next_step = session["next_step"]
    if next_step == NEXT_STEPS[0]:
        opening = "Hello, I'd like to arrange an eye appointment for my child."
        closing = "Please let me know how to arrange a visit, what to bring, and which vision coverage you accept."
    elif next_step == NEXT_STEPS[1]:
        opening = "Hello, I'd like to ask about my child's school vision screening."
        closing = "Please let me know what the screening covered, any follow-up instructions, and whom I should contact."
    else:
        opening = "Notes for a future conversation about my child's vision."
        closing = f"My chosen next step: {next_step or 'Not selected yet'}."
    lines = [opening, f"Age group: {session['profile'].get('age_group', 'Not supplied')}", "", "My observations:"]
    lines.extend(f"- {item}" for item in session["observations"])
    if not session["observations"]:
        lines.append("I haven't added specific observations yet.")
    lines.append(f"When noticed: {session['timing']}")
    if session["notes"]:
        lines.append(session["notes"])
    if parent_questions(session):
        lines.extend(["", "Questions I'd like to ask:"])
        lines.extend(f"- {question}" for question in parent_questions(session))
    lines.extend(["", closing])
    if session["source"] == "fictional_example":
        lines.insert(0, "Fictional example — demonstration only.\n")
    return "\n".join(lines)


def refresh_parent_note(session):
    session["message_draft"] = build_parent_message(session)
    session["summary_revision"] = session.get("summary_revision", 0) + 1
    session["summary_download_requested"] = False


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
        f"Practice completed: {'Yes' if session.get('practice_complete') else 'No'} (not included in activity count).",
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
    lines.extend(["", "QUESTIONS FOR MY NEXT CONVERSATION"])
    lines.extend(parent_questions(session) or ["No questions added yet."])
    lines.extend(["", "MY TAKE-HOME NOTE", session.get("message_draft", build_parent_message(session))])
    lines.extend(["", "No appointment has been booked or message sent by this prototype."])
    return "\n".join(lines) + "\n"


def fictional_example():
    session = new_session()
    session["source"] = "fictional_example"
    session["profile"] = {"label": "Example child", "age_group": "7–10", "glasses": "Yes"}
    session["step"] = "game"
    session["practice_complete"] = True
    begin_activity(session)
    for index, question in enumerate(session["questions"]):
        record_answer(session, index, question["target"] if index < 4 else None)
    session.update({
        "step": "summary",
        "observations": [OBSERVATIONS[0], OBSERVATIONS[3]],
        "timing": "Within the past month",
        "notes": "Moved closer to a book after school. A screening letter came home.",
        "next_step": NEXT_STEPS[0],
    })
    refresh_parent_note(session)
    return session
