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


def _normalize_anchor_text(text: str) -> str:
    return " ".join(text.lower().split())


def _build_character_anchor_entry(name: str, character_info: dict | None) -> str:
    if not character_info:
        return name
    appearance = str(character_info.get("appearance", "")).strip()
    return f"{name}: {appearance}" if appearance else name


def _resolve_character_anchor(
    beat: Beat,
    context: dict,
    character_state: dict | None,
) -> tuple[str, list[str], list[str]]:
    if character_state is None:
        character_state = {"characters": {}, "last_active_characters": []}

    current_character_context = context.get("character_context", {})
    active_names = beat.characters or character_state.get("last_active_characters", [])

    anchor_entries: list[str] = []
    for name in active_names:
        info = current_character_context.get(name)
        if info is None:
            info = character_state.get("characters", {}).get(name)
        entry = _build_character_anchor_entry(name, info)
        if entry:
            anchor_entries.append(entry)

    character_anchor = "; ".join(anchor_entries)
    if not character_anchor:
        character_anchor = context.get("character_text", "")
        if character_anchor:
            anchor_entries = [character_anchor]

    return character_anchor, list(active_names), anchor_entries


def _reinforce_character_anchor(content: str, anchor_entries: list[str], beat_id: str) -> str:
    if not anchor_entries:
        return content

    normalized_content = _normalize_anchor_text(content)
    missing_entries = [
        entry for entry in anchor_entries if _normalize_anchor_text(entry) not in normalized_content
    ]
    if not missing_entries:
        return content

    reinforced_anchor = "; ".join(missing_entries)
    append_log(
        f"[WARN][PROMPT] Reinforced missing character anchor for {beat_id}: {reinforced_anchor}"
    )
    if not content:
        return reinforced_anchor
    return f"{reinforced_anchor}. {content}"


def _update_character_state(character_state: dict, active_names: list[str], context: dict) -> None:
    if not active_names:
        return

    stored_characters = character_state.setdefault("characters", {})
    current_character_context = context.get("character_context", {})

    for name in active_names:
        info = current_character_context.get(name, {})
        existing = stored_characters.get(name, {})
        appearance = str(info.get("appearance", "")).strip() or existing.get("appearance", "")
        refs = info.get("refs", existing.get("refs", []))
        stored_characters[name] = {
            "appearance": appearance,
            "refs": list(refs) if isinstance(refs, list) else [],
        }

    character_state["last_active_characters"] = list(active_names)


def _assemble_sections(
    beat: Beat,
    shot: ShotPlan,
    context: dict,
    character_state: dict | None,
) -> tuple[dict, list[str], list[str]]:
    """Build prompt sections plus the active character anchor metadata."""
    char_anchor, active_names, anchor_entries = _resolve_character_anchor(
        beat,
        context,
        character_state,
    )

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
    }, active_names, anchor_entries


def build_prompt(
    beat: Beat,
    shot: ShotPlan,
    context: dict | None = None,
    character_state: dict | None = None,
    llm: LLMProvider | None = None,
) -> str:
    if context is None:
        context = get_context_for_beat(beat)

    sections, _active_names, anchor_entries = _assemble_sections(
        beat,
        shot,
        context,
        character_state,
    )

    if llm is not None:
        try:
            content = llm.build_panel_prompt(sections)
        except Exception as exc:
            append_log(f"[WARN][PROMPT] llm.build_panel_prompt fallback for {beat.beat_id}: {exc}")
            content = ". ".join(v for v in sections.values() if v)
    else:
        content = ". ".join(v for v in sections.values() if v)

    content = _reinforce_character_anchor(content, anchor_entries, beat.beat_id)

    # Style lock is always pinned in Python — never delegated to the LLM
    return f"{content}. {config.STYLE_LOCK}" if content else config.STYLE_LOCK


def build_panel_jobs(beats: list[Beat], shots: list[ShotPlan]) -> list[PanelJob]:
    llm = LLMProvider()
    jobs = []
    character_state: dict = {"characters": {}, "last_active_characters": []}

    for i, (beat, shot) in enumerate(zip(beats, shots), start=1):
        panel_id = f"p{i:03d}"
        context = get_context_for_beat(beat)
        prompt = build_prompt(beat, shot, context, character_state, llm=llm)
        seed = _panel_seed(panel_id)
        _sections, active_names, _anchor_entries = _assemble_sections(
            beat,
            shot,
            context,
            character_state,
        )

        char_db = context.get("character_context", {})
        ref_image_paths = [
            p for name in active_names
            if (p := str(char_db.get(name, {}).get("ref_image", "") or "").strip())
        ]

        jobs.append(
            PanelJob(
                panel_id=panel_id,
                beat_id=beat.beat_id,
                prompt=prompt,
                seed=seed,
                negative_prompt=config.NEGATIVE_PROMPT,
                ref_image_paths=ref_image_paths,
            )
        )

        _update_character_state(character_state, active_names, context)

    return jobs
