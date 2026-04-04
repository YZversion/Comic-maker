try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .storage import load_json, save_json


def group_panels_into_pages(panel_records: list[dict], panels_per_page: int | None = None) -> list[list[dict]]:
    panels_per_page = panels_per_page or config.PANELS_PER_PAGE
    pages = []
    for i in range(0, len(panel_records), panels_per_page):
        pages.append(panel_records[i:i + panels_per_page])
    return pages


def build_page_manifest(
    panel_manifest_path: str = config.PANEL_MANIFEST_PATH,
    output_path: str = config.PAGE_MANIFEST_PATH,
) -> list[list[dict]]:
    panels = load_json(panel_manifest_path, [])
    pages = group_panels_into_pages(panels)
    save_json(output_path, pages)
    print(f"拼页完成：{len(panels)} 格 -> {len(pages)} 页")
    return pages
