from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Beat:
    beat_id: str
    text: str
    characters: List[str] = field(default_factory=list)
    location: str = ""
    time: str = ""
    actions: List[str] = field(default_factory=list)
    emotion: str = ""
    visual_priority: str = "medium"

    def to_dict(self):
        return self.__dict__


@dataclass
class ShotPlan:
    beat_id: str
    shot_type: str
    subject_focus: str
    composition: str
    mood: str

    def to_dict(self):
        return self.__dict__


@dataclass
class PanelJob:
    panel_id: str
    beat_id: str
    prompt: str
    status: str = "pending"
    image_path: str = ""
    retry_count: int = 0

    def to_dict(self):
        return self.__dict__


@dataclass
class CharacterProfile:
    name: str
    static: Dict = field(default_factory=dict)
    dynamic: Dict = field(default_factory=dict)
    refs: List[str] = field(default_factory=list)

    def to_dict(self):
        return self.__dict__
