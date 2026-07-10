# ATLAS Source Reliability Standard

## Purpose

ATLAS uses Source Reliability Ranking to decide which registered sources should be prioritized during research and discovery review.

A high source score does **not** prove that every statement from that source is true. Reliability ranking evaluates provenance, institutional type, review readiness, access quality, and domain fit. Individual claims must still pass evidence review.

## Inputs

Each assessment uses metadata already stored in the Global Source Library:

- trust tier
- source type
- ingestion status
- access method
- registered website/provenance
- completed ATLAS review status
- requested domain match

## Reliability Bands

| Band | Score | Use |
|---|---:|---|
| `verified_priority` | 90–100 | Prioritize for discovery review; still verify claim-level evidence. |
| `strong` | 80–89 | Strong source; corroborate disputed or high-impact claims. |
| `usable_with_corroboration` | 65–79 | Requires at least one stronger independent source. |
| `caution` | 50–64 | Use for leads, context, or comparison—not as sole evidence. |
| `restricted` | 0–49 | Do not promote into trusted knowledge without Council exception and stronger evidence. |

## Scoring Rules

The score is deterministic and transparent. The API returns every factor used in the calculation.

Primary weight comes from the trust tier:

- Tier 1 official: 92
- Tier 2 academic: 84
- Tier 3 industry: 72
- Tier 4 community: 56
- Tier 5 personal: 42

Adjustments are then applied for:

- source type
- ingestion/review status
- access method
- provenance website
- completed ATLAS review
- requested domain match

Scores are always clamped between 0 and 100.

## Safety Rules

1. A source score is not a truth score.
2. Rejected or blocked sources cannot receive automatic priority.
3. Community, media, open-source, and personal sources require corroboration.
4. Domain mismatch lowers ranking and produces a warning.
5. Missing provenance or missing ATLAS review produces a warning.
6. High-impact engineering, medical, legal, financial, or safety claims require claim-level evidence review regardless of source score.

## API Surfaces

- `GET /api/global-sources/sources/{source_id}/reliability`
- `GET /api/global-sources/reliability-rankings`

Supported ranking filters:

- `domain`
- `minimum_score`
- `limit`

## Headquarters Standard

Source Reliability Ranking supports the Knowledge Division and Source Clearance surfaces. It should remain explainable, deterministic, testable, and conservative. ATLAS must always show why a source received its score.