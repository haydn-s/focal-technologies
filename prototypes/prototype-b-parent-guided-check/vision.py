"""Experimental visual task and portable history. No clinical acuity inference."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
import math
import random
from uuid import uuid4

PROTOCOL = "focal-tumbling-e-v1"
LEVELS = (80, 40, 20)  # Denominators used for geometric size only.
DIRECTIONS = ("up", "right", "down", "left")
TRIALS_PER_LEVEL = 4
REFERENCE_MM = 85.6
PROFILES = ("Child A", "Child B", "Child C")
EYES = ("Both eyes", "Right eye", "Left eye")
GLASSES = ("Usual glasses / contacts", "No glasses / contacts")
SCREENS = ("Home laptop", "Home tablet", "Classroom display")
MAX_RECORDS = 2000


def utc_now():
    return datetime.now(timezone.utc)


def timestamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def parse_time(value):
    if not isinstance(value, str):
        raise ValueError("A record has an invalid timestamp.")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("A record has an invalid timestamp.") from error
    if result.tzinfo is None:
        raise ValueError("Timestamps must include a time zone.")
    return result.astimezone(timezone.utc)


def validate_setup(setup):
    if not isinstance(setup, dict):
        raise ValueError("Missing test setup.")
    for key, options in (("profile", PROFILES), ("eye", EYES), ("glasses", GLASSES), ("screen", SCREENS)):
        if setup.get(key) not in options:
            raise ValueError(f"Invalid {key} selection.")
    if type(setup.get("distance_mm")) is not int or setup["distance_mm"] not in (1500, 3000):
        raise ValueError("Choose a supported viewing distance.")
    if type(setup.get("reference_px")) is not int or not 160 <= setup["reference_px"] <= 600:
        raise ValueError("Reference width must be between 160 and 600 CSS pixels.")
    return {k: setup[k] for k in ("profile", "eye", "glasses", "screen", "distance_mm", "reference_px")}


def size_px(level, setup):
    """Five-arcminute E at 20/20 geometry, scaled by the selected denominator."""
    setup = validate_setup(setup)
    if level not in LEVELS:
        raise ValueError("Unknown task size.")
    angle_radians = math.radians(5 * level / 20 / 60)
    height_mm = 2 * setup["distance_mm"] * math.tan(angle_radians / 2)
    return height_mm * setup["reference_px"] / REFERENCE_MM


def new_check(setup, now=None, rng=None):
    setup = validate_setup(setup)
    rng = rng or random.SystemRandom()
    trials = [{"level": level, "target": rng.choice(DIRECTIONS)}
              for level in LEVELS for _ in range(TRIALS_PER_LEVEL)]
    return {"id": str(uuid4()), "protocol": PROTOCOL, "source": "live", "setup": setup,
            "started_at": timestamp(now or utc_now()), "trials": trials,
            "responses": [], "practice_complete": False, "paused": False, "completed_at": None}


def record_response(check, index, choice, now=None):
    if (check.get("completed_at") or check.get("paused") or not check.get("practice_complete")
            or type(index) is not int or index != len(check["responses"])
            or not 0 <= index < len(check["trials"]) or choice not in (*DIRECTIONS, "cant_tell")):
        return False
    at = now or utc_now()
    if at < parse_time(check["started_at"]):
        return False
    check["responses"].append({"choice": choice, "at": timestamp(at)})
    if len(check["responses"]) == len(check["trials"]):
        check["completed_at"] = timestamp(at)
    return True


def summarize(check):
    if len(check["responses"]) != len(check["trials"]) or not check.get("completed_at"):
        raise ValueError("Finish every trial before saving a result.")
    rows = []
    for level in LEVELS:
        pairs = [(t, a) for t, a in zip(check["trials"], check["responses"]) if t["level"] == level]
        correct = sum(t["target"] == a["choice"] for t, a in pairs)
        rows.append({"Task size": f"20/{level} geometry", "Correct": correct,
                     "Trials": len(pairs), "Accuracy (%)": round(100 * correct / len(pairs), 1)})
    correct = sum(r["Correct"] for r in rows)
    return {"correct": correct, "total": len(check["trials"]),
            "accuracy": 100 * correct / len(check["trials"]), "levels": rows}


def validate_record(record, now=None):
    """Reconstruct trusted fields and reject malformed, incomplete or future records."""
    if not isinstance(record, dict) or record.get("protocol") != PROTOCOL or record.get("source") != "live":
        raise ValueError("Only completed live checks from this protocol can enter your history.")
    if not isinstance(record.get("id"), str) or not 1 <= len(record["id"]) <= 80:
        raise ValueError("Invalid record ID.")
    setup = validate_setup(record.get("setup"))
    start, end = parse_time(record.get("started_at")), parse_time(record.get("completed_at"))
    if end < start or end > (now or utc_now()):
        raise ValueError("Check times must be ordered and cannot be in the future.")
    trials, responses = record.get("trials"), record.get("responses")
    if not isinstance(trials, list) or not isinstance(responses, list) or len(trials) != 12 or len(responses) != 12:
        raise ValueError("A saved check must contain all 12 trials and responses.")
    previous = start
    for i, (trial, response) in enumerate(zip(trials, responses)):
        if (not isinstance(trial, dict) or trial.get("level") != LEVELS[i // TRIALS_PER_LEVEL]
                or trial.get("target") not in DIRECTIONS or not isinstance(response, dict)
                or response.get("choice") not in (*DIRECTIONS, "cant_tell")):
            raise ValueError("Invalid task sequence or answer.")
        at = parse_time(response.get("at"))
        if not previous <= at <= end:
            raise ValueError("Response times must be ordered within the check.")
        previous = at
    if previous != end:
        raise ValueError("Completion time must match the last response.")
    return {"id": record["id"], "protocol": PROTOCOL, "source": "live", "setup": setup,
            "started_at": timestamp(start), "completed_at": timestamp(end),
            "trials": [{"level": t["level"], "target": t["target"]} for t in trials],
            "responses": [{"choice": a["choice"], "at": timestamp(parse_time(a["at"]))} for a in responses],
            "practice_complete": True, "paused": False}


def save_check(records, check):
    validated = validate_record(check)
    if any(r["id"] == validated["id"] for r in records):
        return False
    if len(records) >= MAX_RECORDS:
        raise ValueError("History is full. Export a copy before starting a new history.")
    records.append(validated)
    return True


def export_history(records):
    return json.dumps({"schema": "focal-family-history-v1", "records": records}, indent=2)


def import_history(raw, existing, now=None):
    if len(raw) > 5_000_000:
        raise ValueError("Choose a history file smaller than 5 MB.")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as error:
        raise ValueError("Choose a valid Focal history JSON file.") from error
    if not isinstance(payload, dict) or payload.get("schema") != "focal-family-history-v1":
        raise ValueError("This is not a Focal Family history export.")
    incoming = payload.get("records")
    if not isinstance(incoming, list) or len(incoming) > MAX_RECORDS:
        raise ValueError("A history file can hold at most 2,000 checks.")
    # Validate everything before merging. Never partially import a bad file.
    result = {r["id"]: deepcopy(r) for r in existing}
    for record in incoming:
        valid = validate_record(record, now)
        if valid["id"] in result and result[valid["id"]] != valid:
            raise ValueError("Two different results use the same record ID.")
        result[valid["id"]] = valid
    if len(result) > MAX_RECORDS:
        raise ValueError("Combined history would exceed 2,000 checks.")
    return sorted(result.values(), key=lambda r: r["completed_at"])


def comparison_key(record):
    s = record["setup"]
    return (record["protocol"], record["source"], *(s[k] for k in
            ("profile", "eye", "glasses", "screen", "distance_mm", "reference_px")))


def window_summary(records, days, now=None):
    """Compare equal rolling UTC windows. Input must be one comparable series."""
    if days not in (7, 30, 90, None):
        raise ValueError("Unsupported time window.")
    if len({comparison_key(r) for r in records}) > 1:
        raise ValueError("Select one child, eye and matching setup before comparing.")
    now = now or utc_now()
    valid = [r for r in records if parse_time(r["completed_at"]) <= now]
    cutoff = now - timedelta(days=days) if days else None
    current = [r for r in valid if cutoff is None or parse_time(r["completed_at"]) >= cutoff]
    previous = [r for r in valid if now-timedelta(days=days*2) <= parse_time(r["completed_at"]) < cutoff] if days else []
    avg = lambda rs: sum(summarize(r)["accuracy"] for r in rs)/len(rs) if rs else None
    a, b = avg(current), avg(previous)
    return {"records": sorted(current, key=lambda r: r["completed_at"]), "count": len(current),
            "previous_count": len(previous), "average": a, "previous_average": b,
            "delta_points": a-b if a is not None and b is not None else None}


def fictional_history(now=None):
    """Opt-in illustrative series. It is never saved or exported as live history."""
    now = now or utc_now()
    result = []
    setup = {"profile": "Child A", "eye": "Both eyes", "glasses": GLASSES[0],
             "screen": SCREENS[0], "distance_mm": 3000, "reference_px": 324}
    for index, days in enumerate((85, 60, 35, 20, 10, 3)):
        at = now - timedelta(days=days)
        check = new_check(setup, at, random.Random(index))
        check["practice_complete"] = True
        for i, trial in enumerate(check["trials"]):
            record_response(check, i, trial["target"] if i < (7+index % 4) else "cant_tell", at+timedelta(seconds=i+1))
        check["source"] = "fictional"
        result.append(check)
    return result
