# PrejudiceNeutrino YouTube Channels

## Source

- Repository: https://github.com/PrejudiceNeutrino/YouTube_Channels
- Primary list: https://github.com/PrejudiceNeutrino/YouTube_Channels/blob/main/README.md
- Source owner: PrejudiceNeutrino
- Source type: Curated educational YouTube-channel and learning-resource directory
- Added to ATLAS: 2026-07-15
- Status: Registered external knowledge source

## Purpose

This source expands the ATLAS Knowledge Bank with curated educational channels covering subjects such as anatomy, medicine, biology, chemistry, computer science, coding, electronics, engineering, history, mathematics, music, philosophy, physics, space, workshops, documentaries, and general science.

## ATLAS Handling Rules

1. Keep the upstream repository as the authoritative source instead of silently copying and claiming ownership of its list.
2. Preserve source attribution for every channel imported from this collection.
3. Review channels before recommending or ingesting their content. Inclusion in a curated list is not proof that every video is accurate, current, safe, or appropriate.
4. Check for duplicate channels already present in the ATLAS Knowledge Bank.
5. Classify accepted channels into ATLAS subject domains and allow multiple subject tags when appropriate.
6. Record review status, reviewer, last-reviewed date, difficulty level, evidence quality, and known risks.
7. Do not treat videos as ground truth. Prefer primary sources, official documentation, textbooks, peer-reviewed research, standards, and direct experimental evidence for important factual claims.
8. Respect copyright and platform terms. ATLAS should store links, metadata, summaries, citations, and authorized transcripts rather than unauthorized copies of videos.

## Suggested ATLAS Metadata

```yaml
source_id: prejudiceneutrino-youtube-channels
source_name: PrejudiceNeutrino/YouTube_Channels
source_url: https://github.com/PrejudiceNeutrino/YouTube_Channels
source_kind: curated_directory
content_types:
  - youtube_channels
  - podcasts
  - websites
  - online_learning
  - software
upstream_branch: main
review_required: true
deduplicate: true
attribution_required: true
trust_level: discovery_source
```

## Initial Subject Mapping

- Anatomy and Medicine → Biology, Neuroscience, Health Science
- Biology → Biology, Botany, Environmental Science, Oceanography
- Chemistry → Chemistry, Materials Science
- Computer Science and Coding → Software Engineering, AI, Game Design
- Electronics → Electronics, Robotics, Control Systems
- Engineering and Workshop → Engineering, Architecture, Robotics, Manufacturing
- Earth Science and Outdoors → Environmental Science, Geology, Terraforming
- History and Documentaries → History, Film Studies
- Math → Mathematics, Physics, AI foundations
- Music → Music Theory, Acoustics
- Philosophy → Philosophy, Psychology
- Physics and Space → Physics, Aerospace, Quantum Mechanics
- Science Experiments and Building Stuff → Engineering Lab, Project-Based Learning

## AI Assignment Guidance

- **Ajani:** strategy, engineering tradeoffs, business, history, systems analysis, project evaluation.
- **Minerva:** biology, botany, medicine, environmental science, psychology, philosophy, creative and cultural subjects.
- **Hermes:** software engineering, AI, electronics, robotics, physics, mathematics, architecture, manufacturing, and technical construction.
- **Council:** multidisciplinary sources, disputed claims, safety-sensitive material, and high-impact project decisions.

## Integration Status

The source is now registered in the ATLAS repository. The full upstream list has not been vendored into this file. A future ingestion pipeline should fetch the upstream README, parse categories and channel links, deduplicate entries, score them, and produce reviewed ATLAS records.