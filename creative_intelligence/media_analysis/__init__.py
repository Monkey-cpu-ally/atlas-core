"""Reference media analysis package for ATLAS."""

from .adapters import (
    MediaInput,
    ObservationAdapter,
    StoryObservationAdapter,
    VideoObservationAdapter,
    VideoProvider,
    VisionProvider,
)
from .memory_bridge import MediaStudyMemoryBridge
from .pipeline import ReferenceMediaAnalyzer
from .providers import CallableVisionProvider, VisionRequest
from .schemas import MediaStudyReport, StoryObservation, VisualObservation
from .story_analyzer import StoryStructureAnalyzer
from .visual_analyzer import VisualCraftAnalyzer

__all__ = [
    "MediaInput",
    "ObservationAdapter",
    "StoryObservationAdapter",
    "VideoObservationAdapter",
    "VideoProvider",
    "VisionProvider",
    "CallableVisionProvider",
    "VisionRequest",
    "MediaStudyMemoryBridge",
    "ReferenceMediaAnalyzer",
    "MediaStudyReport",
    "StoryObservation",
    "VisualObservation",
    "StoryStructureAnalyzer",
    "VisualCraftAnalyzer",
]
