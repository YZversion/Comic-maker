"""
烟雾测试：无需人工输入，自动跑一遍完整流水线。
"""

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from comic_maker import config
    from comic_maker.core.exporter import export_chapter_bundle
    from comic_maker.core.page_builder import build_page_manifest
    from comic_maker.core.panel_runner import run_panel_job
    from comic_maker.core.planner import plan_shots
    from comic_maker.core.prompt_builder import build_panel_jobs
    from comic_maker.core.segmenter import segment_chapter
    from comic_maker.core.storage import ensure_dir, init_data_files, init_project_state, save_json
except ModuleNotFoundError:
    import config
    from core.exporter import export_chapter_bundle
    from core.page_builder import build_page_manifest
    from core.panel_runner import run_panel_job
    from core.planner import plan_shots
    from core.prompt_builder import build_panel_jobs
    from core.segmenter import segment_chapter
    from core.storage import ensure_dir, init_data_files, init_project_state, save_json


SAMPLE_TEXT = """林晓推开教室门。她看见周然站在窗边，背对着走廊，望向操场。\n“你怎么还没走？”林晓轻声问。\n周然没有回答，只是把头转过来，眼镜反着光。\n窗外的阳光很烈，把他的轮廓镀成金色。\n林晓走近了几步，把书包放在桌上。"""


def run_smoke_test() -> None:
    print("-- 烟雾测试开始 --")

    ensure_dir(config.PANELS_DIR)
    ensure_dir(config.PAGES_DIR)
    ensure_dir(config.EXPORTS_DIR)
    init_data_files()
    save_json(config.PANEL_MANIFEST_PATH, [])
    init_project_state()

    beats = segment_chapter(SAMPLE_TEXT)
    assert len(beats) > 0, "切分结果不能为空"
    print(f"[OK] 切分：{len(beats)} 个 beat")

    shots = plan_shots(beats)
    assert len(shots) == len(beats), "镜头数量应与 beat 数量一致"
    print(f"[OK] 镜头规划：{len(shots)} 个镜头")

    jobs = build_panel_jobs(beats, shots)
    assert len(jobs) == len(beats), "job 数量应与 beat 数量一致"
    for job in jobs:
        assert job.prompt, f"{job.panel_id} prompt 不能为空"
    print(f"[OK] Prompt 生成：{len(jobs)} 个 job")

    for job in jobs:
        record = run_panel_job(job)
        assert record["image_path"], f"{job.panel_id} 没有返回 image_path"
    print(f"[OK] 出图（mock）：{len(jobs)} 格")

    pages = build_page_manifest()
    assert len(pages) > 0, "拼页结果不能为空"
    print(f"[OK] 拼页：{len(pages)} 页")

    export_dir = export_chapter_bundle("smoke_test")
    print(f"[OK] 导出：{export_dir}")

    print("-- 全部通过 --")


if __name__ == "__main__":
    run_smoke_test()
