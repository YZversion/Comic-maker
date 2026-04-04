from .models import Beat, ShotPlan
from .storage import append_log

try:
    from ..providers.llm_provider import LLMProvider
except ImportError:
    from providers.llm_provider import LLMProvider


_EMOTION_CLOSE_UP = {
    "anger", "fear", "cry", "shock",
    "愤怒", "恐惧", "哭泣", "震惊",
}

_VALID_SHOT_TYPES = {"close_up", "medium", "wide", "two_shot", "over_shoulder", "dutch_angle", "extreme_close_up"}
_VALID_COMPOSITIONS = {"centered", "rule_of_thirds", "diagonal"}


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


def plan_shot_for_beat(beat: Beat, llm: LLMProvider | None = None) -> ShotPlan:
    llm_result: dict = {}
    if llm is not None:
        try:
            llm_result = llm.plan_shot(beat)
        except Exception as exc:
            append_log(f"[WARN][PLANNER] llm.plan_shot fallback for {beat.beat_id}: {exc}")

    # LLM values take priority; rule-based logic fills any gaps
    shot_type = llm_result.get("shot_type") or default_shot_type(beat)
    if shot_type not in _VALID_SHOT_TYPES:
        shot_type = default_shot_type(beat)

    subject_focus = llm_result.get("subject_focus") or (
        ", ".join(beat.characters) if beat.characters else "scene"
    )

    composition = llm_result.get("composition") or default_composition(beat)
    if composition not in _VALID_COMPOSITIONS:
        composition = default_composition(beat)

    mood = llm_result.get("mood") or beat.emotion or "neutral"

    return ShotPlan(
        beat_id=beat.beat_id,
        shot_type=shot_type,
        subject_focus=subject_focus,
        composition=composition,
        mood=mood,
    )


def plan_shots(beats: list[Beat], use_llm: bool = True) -> list[ShotPlan]:
    llm = LLMProvider() if use_llm else None
    return [plan_shot_for_beat(beat, llm=llm) for beat in beats]
