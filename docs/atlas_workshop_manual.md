# Atlas Core Workshop Manual (Build Mindset)

## Step 1: Intake
Request payload includes:
- `project`
- `user_input`
- `mode` (`mentor|warrior|builder`)
- optional `context`
- optional `pipeline_stage`

Atlas receives input first. No autonomous execution.

## Step 2: Intent Decision
Classify request as one of:
- blueprint request
- learning request
- security request
- general planning
- image blueprint extraction (future-ready lane)

## Step 3: Locked Agent Order
Execution order is non-negotiable:

1. Ajani -> structured engineering plan
2. Minerva -> clarity and teach-back
3. Hermes -> validation, risk scan, policy enforcement

## Step 4: Combined Output
Return one structured payload containing:

### Ajani panel
- goal
- spec
- components
- constraints
- risks
- tests
- measurable requirements

### Minerva panel
- explanation
- lego-style steps
- next action

### Hermes panel
- flags
- warnings
- policy constraints
- approval status

## Step 5: Pipeline
Every real project follows:
- Blueprint
- Build
- Modify

Each stage must include:
- version number
- risks
- tests
- measurable outputs

