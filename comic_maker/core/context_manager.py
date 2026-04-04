try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .models import Beat
from .storage import load_json


def load_character_db(path: str = config.CHARACTER_DB_PATH) -> dict:
    return load_json(path, {})


def load_scene_db(path: str = config.SCENE_DB_PATH) -> dict:
    return load_json(path, {})


def load_prop_db(path: str = config.PROP_DB_PATH) -> dict:
    return load_json(path, {})


def get_character_context(beat: Beat, character_db: dict) -> dict:
    matched = {}
    for name in beat.characters:
        if name in character_db:
            matched[name] = character_db[name]
    return matched


def get_scene_context(beat: Beat, scene_db: dict) -> dict:
    if beat.location and beat.location in scene_db:
        return scene_db[beat.location]
    return {}


def get_prop_context(beat: Beat, prop_db: dict) -> dict:
    _ = (beat, prop_db)
    return {}


def format_character_text(char_ctx: dict) -> str:
    if not char_ctx:
        return ""
    parts = []
    for name, info in char_ctx.items():
        desc = info.get("appearance", "")
        parts.append(f"{name}: {desc}")
    return "; ".join(parts)


def format_scene_text(scene_ctx: dict) -> str:
    return scene_ctx.get("description", "")


def get_context_for_beat(beat: Beat) -> dict:
    character_db = load_character_db()
    scene_db = load_scene_db()
    prop_db = load_prop_db()

    char_ctx = get_character_context(beat, character_db)
    scene_ctx = get_scene_context(beat, scene_db)
    prop_ctx = get_prop_context(beat, prop_db)

    return {
        "character_context": char_ctx,
        "scene_context": scene_ctx,
        "prop_context": prop_ctx,
        "character_text": format_character_text(char_ctx),
        "scene_text": format_scene_text(scene_ctx),
        "prop_text": "",
    }
