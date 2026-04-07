import re

try:
    from comic_maker import config
except ModuleNotFoundError:
    import config

from .context_manager import build_alias_map, load_character_db, normalize_character_names
from .models import Beat
from ..providers.llm_provider import LLMProvider


def split_by_paragraph(chapter_text: str) -> list[str]:
    parts = [p.strip("\u3000 \t") for p in chapter_text.split("\n") if p.strip("\u3000 \t")]
    return parts


def split_by_rules(paragraphs: list[str]) -> list[str]:
    segments = []
    for paragraph in paragraphs:
        if len(paragraph) > 200:
            sentences = re.split(r"(?<=[。！？!?])", paragraph)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    segments.append(sentence)
        else:
            segments.append(paragraph)
    return segments


def merge_short_segments(segments: list[str], min_chars: int) -> list[str]:
    """Merge segments shorter than min_chars into the previous segment.

    Prevents trivially short beats (bare dialogue, one-word fragments) from
    becoming standalone panels.
    """
    if not segments:
        return segments
    merged = [segments[0]]
    for seg in segments[1:]:
        if len(merged[-1]) < min_chars:
            merged[-1] += "\u3000" + seg
        else:
            merged.append(seg)
    return merged


def build_beats_from_segments(segments: list[str]) -> list[Beat]:
    beats = []
    for i, seg in enumerate(segments, start=1):
        beats.append(Beat(beat_id=f"b{i:03d}", text=seg))
    return beats


def segment_chapter(chapter_text: str) -> list[Beat]:
    paragraphs = split_by_paragraph(chapter_text)
    segments = split_by_rules(paragraphs)
    segments = merge_short_segments(segments, config.MIN_BEAT_CHARS)
    beats = build_beats_from_segments(segments)
    llm = LLMProvider()
    alias_map = build_alias_map(load_character_db())
    for beat in beats:
        enriched = llm.enrich_beat(beat.text)
        beat.characters = normalize_character_names(enriched["characters"], alias_map)
        beat.location = enriched["location"]
        beat.time = enriched["time"]
        beat.actions = enriched["actions"]
        beat.emotion = enriched["emotion"]
        beat.visual_priority = enriched["visual_priority"]
    return beats
