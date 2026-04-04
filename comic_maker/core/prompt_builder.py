import hashlib

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .context_manager import get_context_for_beat
from .models import Beat, PanelJob, ShotPlan
from .storage import append_log
from ..providers.llm_provider import LLMProvider


def _panel_seed(panel_id: str) -> int:
    """Deterministic seed derived from panel_id — same panel always gets same seed."""
    return int(hashlib.md5(panel_id.encode()).hexdigest()[:8], 16) % (2**31)


def _assemble_sections(
    beat: Beat,
    shot: ShotPlan,
    context: dict,
    prev_panel_state: dict | None,
) -> dict:
    """Build the five named sections used both by the LLM call and the fallback."""
    char_anchor = context.get("character_text", "")
    if not char_anchor and prev_panel_state:
        char_anchor = prev_panel_state.get("character_anchor", "")

    scene_anchor = context.get("scene_text", "")

    action_parts = []
    if beat.actions:
        action_parts.append(", ".join(beat.actions))
    if beat.emotion:
        action_parts.append(f"{beat.emotion} expression")
    action = "; ".join(action_parts)

    camera = f"{shot.shot_type} shot, {shot.composition} composition, {shot.mood} mood"

    return {
        "character_anchor": char_anchor,
        "scene_anchor": scene_anchor,
        "action": action,
        "camera": camera,
    }


def build_prompt(
    beat: Beat,
    shot: ShotPlan,
    context: dict | None = None,
    prev_panel_state: dict | None = None,
    llm: LLMProvider | None = None,
) -> str:
    if context is None:
        context = get_context_for_beat(beat)

    sections = _assemble_sections(beat, shot, context, prev_panel_state)

    if llm is not None:
        try:
            content = llm.build_panel_prompt(sections)
        except Exception as exc:
            append_log(f"[WARN][PROMPT] llm.build_panel_prompt fallback for {beat.beat_id}: {exc}")
            content = ". ".join(v for v in sections.values() if v)
    else:
        content = ". ".join(v for v in sections.values() if v)

    # Style lock is always pinned in Python — never delegated to the LLM
    return f"{content}. {config.STYLE_LOCK}" if content else config.STYLE_LOCK


def build_panel_jobs(beats: list[Beat], shots: list[ShotPlan]) -> list[PanelJob]:
    llm = LLMProvider()
    jobs = []
    prev_panel_state: dict | None = None

    for i, (beat, shot) in enumerate(zip(beats, shots), start=1):
        panel_id = f"p{i:03d}"
        context = get_context_for_beat(beat)
        prompt = build_prompt(beat, shot, context, prev_panel_state, llm=llm)
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

        char_anchor = context.get("character_text", "")
        if not char_anchor and prev_panel_state:
            char_anchor = prev_panel_state.get("character_anchor", "")
        prev_panel_state = {
            "character_anchor": char_anchor,
            "shot_type": shot.shot_type,
        }

    return jobs
