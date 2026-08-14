from pathlib import Path

from creative_intelligence.creative_memory import CreativeMemory
from creative_intelligence.media_analysis.providers import CallableVisionProvider
from creative_intelligence.media_analysis.study_service import CreativeReferenceStudyService
from creative_intelligence.media_analysis.video_sampler import SampledFrame, VideoFrameSampler


def test_reference_frames_become_persistent_session_lessons(tmp_path: Path):
    frames = []
    for index in range(3):
        frame = tmp_path / f"frame_{index}.jpg"
        frame.write_bytes(b"fixture")
        frames.append(SampledFrame(float(index), str(frame)))

    def model(_request):
        return {
            "silhouette": ["clear asymmetric mass"],
            "shape_language": ["angular primary forms with circular accents"],
            "color": ["restrained base palette with focal accent"],
            "lighting": ["high-contrast rim separation"],
            "composition": ["strong diagonal hierarchy"],
            "movement": ["pose communicates direction before motion"],
        }

    memory = CreativeMemory()
    service = CreativeReferenceStudyService(CallableVisionProvider(model), memory)
    result = service.study_frames(project="ATLAS-test", source_name="approved-study", frames=frames)

    assert result.source_name == "approved-study"
    assert result.learned_lessons > 0
    assert len(memory.recall(project="ATLAS-test")) == result.learned_lessons
    assert "approved-study" in result.report_markdown


def test_uniform_video_sampling_is_deterministic():
    timestamps = VideoFrameSampler.uniform_timestamps(100.0, count=5)
    assert len(timestamps) == 5
    assert timestamps == sorted(timestamps)
    assert timestamps[0] == 2.0
    assert timestamps[-1] == 98.0
