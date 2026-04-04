import os

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .models import PanelJob
from .storage import append_log, append_panel_manifest

try:
    from ..providers.image_provider import ImageProvider
except ImportError:
    from providers.image_provider import ImageProvider


def make_panel_output_path(panel_id: str) -> str:
    return os.path.join(config.PANELS_DIR, panel_id)


def run_panel_job(job: PanelJob) -> dict:
    provider = ImageProvider(provider=config.IMAGE_PROVIDER)
    output_path = make_panel_output_path(job.panel_id)
    image_path = provider.generate(
        job.prompt,
        output_path,
        seed=job.seed,
        negative_prompt=job.negative_prompt,
    )

    record = {
        "panel_id": job.panel_id,
        "beat_id": job.beat_id,
        "status": "generated",
        "image_path": image_path,
        "prompt": job.prompt,
        "retry_count": job.retry_count,
    }
    append_panel_manifest(record)
    append_log(f"Generated {job.panel_id} -> {image_path}")
    return record


def retry_panel_job(job: PanelJob, reason: str) -> dict:
    job.retry_count += 1
    job.prompt += f" [Retry fix: {reason}]"
    append_log(f"Retry {job.panel_id} (#{job.retry_count}): {reason}")
    return run_panel_job(job)
