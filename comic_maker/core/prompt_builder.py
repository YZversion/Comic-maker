from .context_manager import get_context_for_beat
from .models import Beat, PanelJob, ShotPlan


def build_prompt(beat: Beat, shot: ShotPlan, context: dict | None = None) -> str:
    if context is None:
        context = get_context_for_beat(beat)

    char_desc = context.get("character_text", "")
    scene_desc = context.get("scene_text", "")
    prop_desc = context.get("prop_text", "")

    parts = []
    if char_desc:
        parts.append(char_desc)
    if scene_desc:
        parts.append(f"Setting: {scene_desc}")
    if prop_desc:
        parts.append(prop_desc)
    if beat.actions:
        parts.append(f"Action: {', '.join(beat.actions)}")
    if beat.emotion:
        parts.append(f"Emotion: {beat.emotion}")
    parts.append(f"Shot: {shot.shot_type}, composition {shot.composition}, mood {shot.mood}")
    parts.append("Manga panel, black and white, clean lineart, detailed")

    return ". ".join(parts)


def build_panel_jobs(beats: list[Beat], shots: list[ShotPlan]) -> list[PanelJob]:
    jobs = []
    for i, (beat, shot) in enumerate(zip(beats, shots), start=1):
        context = get_context_for_beat(beat)
        prompt = build_prompt(beat, shot, context)
        jobs.append(
            PanelJob(
                panel_id=f"p{i:03d}",
                beat_id=beat.beat_id,
                prompt=prompt,
            )
        )
    return jobs
