"""Demonstrate the ATLAS media adapter contracts without a live vision model."""

from creative_intelligence.creative_memory import CreativeMemory
from creative_intelligence.media_analysis import (
    MediaInput,
    MediaStudyMemoryBridge,
    ObservationAdapter,
    ReferenceMediaAnalyzer,
)


class DemoVisionProvider:
    def analyze_image(self, image_ref: str, instructions: str) -> dict:
        return {
            "subject": image_ref,
            "silhouette": ["broad readable mass with a narrow focal shape"],
            "shape_language": ["large angular forms balanced by smaller curves"],
            "color": ["muted base colors with a high-contrast focal accent"],
            "lighting": ["hard edge light separates the subject from the background"],
            "materials": ["layered hard and soft surfaces communicate function"],
            "composition": ["strong diagonal guides attention toward the subject"],
            "movement": ["pose suggests stored energy before action"],
        }


def main() -> None:
    media = MediaInput(
        source_name="Approved reference frame",
        media_ref="demo://frame-001",
        source_type="image",
        context="Study visual craft characteristics for an original armored explorer.",
    )

    observation = ObservationAdapter(DemoVisionProvider()).from_image(media)
    report = ReferenceMediaAnalyzer().analyze(
        source_name=media.source_name,
        source_type=media.source_type,
        visual=observation,
    )

    memory = CreativeMemory()
    stored = MediaStudyMemoryBridge(memory).remember_report(
        report,
        project="Demo Project",
        task="Develop an original armored explorer",
    )

    print(report.to_markdown())
    print(f"\nStored lessons: {len(stored)}")


if __name__ == "__main__":
    main()
