# Source Review Workflow

This workflow describes how ATLAS reviews a source before trusting or using it.

## 1. Intake

A source is discovered from a library, website, creator, GitHub repository, government agency, manufacturer, patent database, user upload, or ATLAS research.

Output:

```text
Source candidate
```

## 2. Passport Creation

ATLAS creates a Source Passport with metadata, source type, trust tier, and possible Knowledge Banks.

Output:

```text
Cataloged source
```

## 3. First Filter

Reject immediately if the source is:

- Malicious
- Clearly fake
- Plagiarized
- Unsafe instruction source
- License-problematic for intended use
- Pure hype with no value
- Outside ATLAS goals

Output:

```text
Reject / Continue
```

## 4. Evidence Rating

Apply the Source Rating Standard:

```text
A-Level
B-Level
C-Level
D-Level
F-Level
```

Output:

```text
Rated source
```

## 5. Specialist Review

Hermes reviews engineering, software, manufacturing, electronics, physics, and robotics sources.

Minerva reviews biology, medicine, botany, environment, art, design, history, and storytelling sources.

Ajani reviews economics, business, psychology, strategy, security, risk, and planning sources.

Output:

```text
Specialist review notes
```

## 6. Claim Extraction

ATLAS extracts important claims, facts, methods, examples, warnings, and project links.

Output:

```text
Extracted claims
```

## 7. Verification

Important claims are checked against stronger sources when needed.

Output:

```text
Verified / Partially Verified / Needs Evidence
```

## 8. Council Decision

The Council assigns final source status:

```text
Approved
Limited Use
Needs More Verification
Rejected
Archived
```

## 9. Bank Assignment

The source is assigned to one primary Knowledge Bank and any related banks.

## 10. Project Link

If relevant, it is connected to ATLAS projects.

## 11. Review Cycle

Every source receives a future review date depending on risk and field speed.

Fast-moving fields like AI, software, batteries, and medicine need more frequent review.

Stable historical or public-domain texts may require less frequent review.
