# Source Health Dashboard

The Source Health Dashboard helps ATLAS understand whether its knowledge sources are strong, weak, outdated, biased, or missing.

## Mission

Track the quality of the Knowledge Division's source base across all 22 Knowledge Banks.

## Health Metrics

Each Knowledge Bank should track:

```text
Total sources
A-Level sources
B-Level sources
C-Level sources
D-Level sources
F-Level sources
Outdated sources
International source diversity
Creator sources
GitHub sources
Book sources
Paper sources
Patent sources
Manufacturer sources
Government sources
Standards sources
User sources
ATLAS-generated sources
```

## Health Score

Each bank receives a Knowledge Source Health score from 0-100.

This score does not mean ATLAS knows 100% of the subject. It means the curated source library for that bank is healthy, balanced, and traceable.

## Example Health Report

```text
Knowledge Bank: Robotics
Total Sources: 145
A-Level: 34
B-Level: 58
C-Level: 39
D-Level: 12
F-Level: 2
Outdated: 18
International Coverage: USA, Japan, Germany, South Korea, Switzerland
Weak Area: Soft robotics patents
Recommendation: Add more recent soft robotics papers and manufacturer documentation
Health Score: 82
```

## Warning Flags

ATLAS should flag:

- Too many weak sources
- Too many old sources
- Not enough international diversity
- Too few primary sources
- No standards sources
- No manufacturer documentation for engineering topics
- Heavy dependence on one creator or one country
- Missing license information
- Missing last-reviewed date

## Council Review

The Council should review source health monthly and answer:

```text
Which banks are strongest?
Which banks are weakest?
Which sources should be retired?
Which sources need re-verification?
Which countries or source types are missing?
Which ATLAS projects are affected by weak source coverage?
```
