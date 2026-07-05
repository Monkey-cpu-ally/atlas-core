# Manufacturer Documentation Sources

Manufacturer documentation is one of the most important real-world source types for Hermes.

It shows how parts actually work, how they are installed, what limits they have, and what safety rules apply.

## Mission

Use manufacturer documentation to ground ATLAS engineering ideas in real components and real constraints.

## Source Types

```text
Datasheets
User manuals
Service manuals
Application notes
CAD files
PCB reference designs
Mechanical drawings
Battery specifications
Motor specifications
Sensor manuals
Processor documentation
Safety bulletins
Installation guides
Maintenance guides
```

## What Manufacturer Docs Are Good For

- Real dimensions
- Voltage and current limits
- Torque ratings
- Heat limits
- Wiring diagrams
- Communication protocols
- Material specifications
- Maintenance schedules
- Failure warnings
- Safety instructions

## What They Are Not Good For

- Independent performance proof
- Long-term reliability guarantees beyond stated conditions
- Neutral comparison against competitors
- Medical, legal, or safety conclusions beyond the product documentation

## Source Passport Additions

```text
Manufacturer
Product name
Model number
Revision number
Publication date
Part category
Operating limits
Safety notes
Known failure modes
Related standards
Related ATLAS projects
Replacement parts
Lifecycle status
```

## Trust Tier

Manufacturer documentation is usually Tier A for product-specific specifications and Tier B/C for marketing claims.

## ATLAS Rule

Product specifications should be separated from product marketing.

Example:

```text
Specification: Maximum input voltage is 24V.
Marketing claim: Industry-leading performance.
```

The first may be stored as technical data. The second needs comparison and verification.

## Engineering Use

Hermes should use manufacturer documentation when designing:

- Robots
- Motors
- PCBs
- Sensors
- Battery systems
- Power electronics
- Industrial machines
- Scanners
- Control systems

## Safety Rule

If a document contains safety warnings, ATLAS must preserve them in summaries and project links.
