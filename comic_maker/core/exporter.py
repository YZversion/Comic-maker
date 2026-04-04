import os
import shutil

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .storage import ensure_dir


def export_chapter_bundle(chapter_id: str) -> str:
    export_dir = os.path.join(config.EXPORTS_DIR, chapter_id)
    ensure_dir(export_dir)

    files_to_copy = [
        (config.PANEL_MANIFEST_PATH, "panel_manifest.json"),
        (config.CHARACTER_DB_PATH, "character_db.json"),
        (config.SCENE_DB_PATH, "scene_db.json"),
        (config.PAGE_MANIFEST_PATH, "page_manifest.json"),
        (config.PROJECT_STATE_PATH, "project_state.json"),
    ]

    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy(src, os.path.join(export_dir, dst))

    print(f"导出完成：{export_dir}")
    return export_dir
