import hashlib

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .context_manager import get_context_for_beat
from .models import Beat, PanelJob, ShotPlan


def _panel_seed(panel_id: str) -> int:
    """Deterministic seed derived from panel_id — same panel always gets same seed."""
    return int(hashlib.md5(panel_id.encode()).hexdigest()[:8], 16) % (2**31)


def build_prompt(
    beat: Beat,
    shot: ShotPlan,
    context: dict | None = None,
    prev_panel_state: dict | None = None,
) -> str:
    if context is None:
        context = get_context_for_beat(beat)

    # 1. Character Anchor — fall back to previous panel's anchor if beat has no characters
    char_anchor = context.get("character_text", "")
    if not char_anchor and prev_panel_state:
        char_anchor = prev_panel_state.get("character_anchor", "")

    # 2. Scene Anchor
    scene_anchor = context.get("scene_text", "")

    # 3. Action (actions + emotion)
    action_parts = []
    if beat.actions:
        action_parts.append(", ".join(beat.actions))
    if beat.emotion:
        action_parts.append(f"{beat.emotion} expression")
    action = "; ".join(action_parts)

    # 4. Camera
    camera = f"{shot.shot_type} shot, {shot.composition} composition, {shot.mood} mood"

    # 5. Style Lock (fixed — never changes between panels)
    style = config.STYLE_LOCK

    sections = [s for s in [char_anchor, scene_anchor, action, camera, style] if s]
    return ". ".join(sections)


def build_panel_jobs(beats: list[Beat], shots: list[ShotPlan]) -> list[PanelJob]:
    jobs = []
    prev_panel_state: dict | None = None
    for i, (beat, shot) in enumerate(zip(beats, shots), start=1):
        panel_id = f"p{i:03d}"
        context = get_context_for_beat(beat)
        prompt = build_prompt(beat, shot, context, prev_panel_state)
        seed = _panel_seed(panel_id)

        jobs.append(
            PanelJob(
                panel_id=panel_id,
                beat_id=beat.beat_id,
                prompt=prompt,
                seed=seed,
                negative_prompt=config.NEGATIVE_PROMPT,
            )
        )

        # Build prev_panel_state for the next iteration
        char_anchor = context.get("character_text", "")
        if not char_anchor and prev_panel_state:
            char_anchor = prev_panel_state.get("character_anchor", "")
        prev_panel_state = {
            "character_anchor": char_anchor,
            "shot_type": shot.shot_type,
        }

    return jobs
