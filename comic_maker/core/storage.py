import json
import os
from datetime import datetime

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config


def resolve_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(config.BASE_DIR, path)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_json(path: str, default):
    abs_path = resolve_path(path)
    if not os.path.exists(abs_path):
        return default
    with open(abs_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data) -> None:
    abs_path = resolve_path(path)
    parent = os.path.dirname(abs_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clear_panels_dir(panels_dir: str = config.PANELS_DIR) -> None:
    """Delete all image files in the panels directory before a new chapter run."""
    if not os.path.isdir(panels_dir):
        return
    for fname in os.listdir(panels_dir):
        fpath = os.path.join(panels_dir, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)


def init_data_files() -> None:
    ensure_dir(config.DATA_DIR)
    for path, default in [
        (config.CHARACTER_DB_PATH, {}),
        (config.SCENE_DB_PATH, {}),
        (config.PROP_DB_PATH, {}),
        (config.PANEL_MANIFEST_PATH, []),
    ]:
        if not os.path.exists(path):
            save_json(path, default)


def append_panel_manifest(record: dict, path: str = config.PANEL_MANIFEST_PATH):
    manifest = load_json(path, [])

    panel_id = record.get("panel_id")
    if panel_id is None:
        manifest.append(record)
        save_json(path, manifest)
        return

    for i, item in enumerate(manifest):
        if item.get("panel_id") == panel_id:
            manifest[i] = record
            save_json(path, manifest)
            return

    manifest.append(record)
    save_json(path, manifest)


def init_project_state(path: str = config.PROJECT_STATE_PATH):
    state = {
        "created_at": datetime.now().isoformat(),
        "chapter": "",
        "beats_total": 0,
        "panels_generated": 0,
        "panels_approved": 0,
        "last_updated": datetime.now().isoformat(),
    }
    save_json(path, state)
    return state


def update_project_state(updates: dict, path: str = config.PROJECT_STATE_PATH):
    state = load_json(path, {})
    state.update(updates)
    state["last_updated"] = datetime.now().isoformat()
    save_json(path, state)


def append_log(message: str, path: str = config.RUN_LOG_PATH):
    abs_path = resolve_path(path)
    ensure_dir(os.path.dirname(abs_path))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(abs_path, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")
