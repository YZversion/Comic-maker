"""
comic_maker 主流程
章节文本 -> 切分 -> 镜头规划 -> prompt生成 -> 出图 -> 审核 -> 拼页 -> 导出
"""

import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

try:
    from comic_maker import config
    from comic_maker.core.exporter import export_chapter_bundle
    from comic_maker.core.page_builder import build_page_manifest
    from comic_maker.core.panel_runner import retry_panel_job, run_panel_job
    from comic_maker.core.planner import plan_shots
    from comic_maker.core.prompt_builder import build_panel_jobs
    from comic_maker.core.reviewer import approve_or_retry, review_prompt
    from comic_maker.core.segmenter import segment_chapter
    from comic_maker.core.storage import (
        append_log,
        ensure_dir,
        init_data_files,
        init_project_state,
        save_json,
        update_project_state,
    )
except ModuleNotFoundError:
    import config
    from core.exporter import export_chapter_bundle
    from core.page_builder import build_page_manifest
    from core.panel_runner import retry_panel_job, run_panel_job
    from core.planner import plan_shots
    from core.prompt_builder import build_panel_jobs
    from core.reviewer import approve_or_retry, review_prompt
    from core.segmenter import segment_chapter
    from core.storage import (
        append_log,
        ensure_dir,
        init_data_files,
        init_project_state,
        save_json,
        update_project_state,
    )


def print_stage(title: str) -> None:
    print(f"\n{'=' * 10} {title} {'=' * 10}")


def print_beat_summary(beats) -> None:
    print(f"\n共切分 {len(beats)} 个 beat：")
    for beat in beats:
        preview = beat.text[:40] + "..." if len(beat.text) > 40 else beat.text
        print(f"  [{beat.beat_id}] {preview}")


def get_chapter_id() -> str:
    chapter_id = input("\n请输入章节 ID（如 ch01）：").strip()
    return chapter_id or "ch01"


def get_chapter_text() -> str:
    print("\n请输入章节文本（输入完成后单独一行输入 END 结束）：")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def stage_segment(chapter_text: str):
    print_stage("阶段 1：章节切分")
    beats = segment_chapter(chapter_text)
    print_beat_summary(beats)
    append_log(f"切分完成，共 {len(beats)} 个 beat")
    return beats


def stage_plan(beats):
    print_stage("阶段 2：镜头规划")
    shots = plan_shots(beats)
    for shot in shots:
        print(f"  [{shot.beat_id}] {shot.shot_type} | {shot.subject_focus} | mood: {shot.mood}")
    append_log(f"镜头规划完成，共 {len(shots)} 个镜头")
    return shots


def stage_build_prompts(beats, shots):
    print_stage("阶段 3：生成 Prompt")
    jobs = build_panel_jobs(beats, shots)
    print(f"共生成 {len(jobs)} 个 panel job")
    return jobs


def stage_review_prompts(jobs):
    print_stage("阶段 4：审核 Prompt（可选）")
    ans = input("是否逐条审核 prompt？(y/n，默认跳过): ").strip().lower()
    if ans != "y":
        print("跳过 prompt 审核")
        return jobs

    for job in jobs:
        print(f"\n-- Panel {job.panel_id} (beat: {job.beat_id}) --")
        job.prompt = review_prompt(job.prompt)
    return jobs


def stage_generate_panels(jobs):
    print_stage("阶段 5：生成分格图片")

    save_json(config.PANEL_MANIFEST_PATH, [])

    approved = 0
    for job in jobs:
        print(f"\n正在生成 {job.panel_id}...")
        record = run_panel_job(job)
        print(f"  -> {record['image_path']}")

        ok, reason = approve_or_retry(job.panel_id)
        if ok:
            approved += 1
            job.status = "approved"
            continue

        for attempt in range(config.MAX_RETRY):
            print(f"  重试 #{attempt + 1}...")
            record = retry_panel_job(job, reason)
            print(f"  -> {record['image_path']}")
            ok, reason = approve_or_retry(job.panel_id)
            if ok:
                approved += 1
                job.status = "approved"
                break
        else:
            print(f"  [{job.panel_id}] 已达最大重试次数，标记为 rejected")
            job.status = "rejected"

    append_log(f"出图完成：{approved}/{len(jobs)} 通过")
    return approved


def stage_build_pages():
    print_stage("阶段 6：拼页")
    return build_page_manifest()


def stage_export(chapter_id: str) -> str:
    print_stage("阶段 7：导出章节包")
    export_dir = export_chapter_bundle(chapter_id)
    print(f"导出目录：{export_dir}")
    append_log(f"导出完成：{export_dir}")
    return export_dir


def main() -> None:
    ensure_dir(config.LOGS_DIR)
    ensure_dir(config.PANELS_DIR)
    ensure_dir(config.PAGES_DIR)
    ensure_dir(config.EXPORTS_DIR)
    init_data_files()

    print("=" * 40)
    print("  漫画自动生成流水线 v0.1")
    print("=" * 40)

    chapter_id = get_chapter_id()
    chapter_text = get_chapter_text()

    if not chapter_text.strip():
        print("章节内容为空，退出")
        return

    init_project_state()
    update_project_state({"chapter": chapter_id})
    append_log(f"=== 开始处理章节 {chapter_id} ===")

    beats = stage_segment(chapter_text)
    update_project_state({"beats_total": len(beats)})

    shots = stage_plan(beats)
    jobs = stage_build_prompts(beats, shots)
    jobs = stage_review_prompts(jobs)

    approved = stage_generate_panels(jobs)
    update_project_state({"panels_generated": len(jobs), "panels_approved": approved})

    stage_build_pages()
    export_dir = stage_export(chapter_id)

    print_stage("完成")
    print(f"  章节 ID  : {chapter_id}")
    print(f"  Beat 数量: {len(beats)}")
    print(f"  生成格数 : {len(jobs)}")
    print(f"  通过格数 : {approved}")
    print(f"  导出目录 : {export_dir}")
    append_log(f"=== 章节 {chapter_id} 处理完毕 ===\n")


if __name__ == "__main__":
    main()
