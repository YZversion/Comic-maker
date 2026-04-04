from .models import Beat, ShotPlan


_EMOTION_CLOSE_UP = {
    "anger",
    "fear",
    "cry",
    "shock",
    "愤怒",
    "恐惧",
    "哭泣",
    "震惊",
}


def default_shot_type(beat: Beat) -> str:
    if len(beat.characters) >= 2:
        return "two_shot"
    if beat.emotion in _EMOTION_CLOSE_UP:
        return "close_up"
    if beat.location and not beat.characters:
        return "wide"
    return "medium"


def default_composition(beat: Beat) -> str:
    if beat.visual_priority == "high":
        return "rule_of_thirds"
    return "centered"


def plan_shot_for_beat(beat: Beat) -> ShotPlan:
    return ShotPlan(
        beat_id=beat.beat_id,
        shot_type=default_shot_type(beat),
        subject_focus=", ".join(beat.characters) if beat.characters else "scene",
        composition=default_composition(beat),
        mood=beat.emotion or "neutral",
    )


def plan_shots(beats: list[Beat]) -> list[ShotPlan]:
    return [plan_shot_for_beat(beat) for beat in beats]
