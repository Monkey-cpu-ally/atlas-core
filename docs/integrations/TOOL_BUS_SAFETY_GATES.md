# ATLAS Tool Bus Safety Gates

The safety gate sits between ATLAS agents and Tool Bus adapters.

```text
Agent request
    ↓
Safety policy review
    ↓
Allow / Require approval / Deny
    ↓
Adapter verification
    ↓
Tool execution
```

## Default Behavior

The default policy is intentionally restrictive:

- Tools are disabled until explicitly enabled.
- Capabilities can be enabled individually.
- Read-only, generate-only, and simulation-only jobs may be allowed for enabled tools.
- Local writes require approval by default.
- Remote writes require approval by default.
- Destructive actions are denied by default.
- Specific requesters can be blocked.
- Individual higher-risk jobs can receive explicit approval by job ID.

## Important Limitation

These safety gates do not make the external integrations live. The current adapters remain placeholders and fail verification until real local integrations are configured.

## Example

```python
from atlas.tool_bus import SafetyPolicy, ToolJob, ToolSafetyLevel
from atlas.tool_bus.registry import create_default_tool_bus

policy = SafetyPolicy()
policy.enable_tool("blender", ["generate_scene_script"])

bus = create_default_tool_bus()
bus.safety_policy = policy

job = ToolJob(
    tool_name="blender",
    capability="generate_scene_script",
    payload={"prompt": "Create a concept model."},
    requested_by="hermes",
    safety_level=ToolSafetyLevel.GENERATE_ONLY,
)

result = bus.execute(job)
```

The safety review can allow this request, but the placeholder Blender adapter will still fail verification until Blender is actually connected.

## Next Step

Add an event log so every safety decision, approval, denial, execution, result, and failure is recorded for ATLAS memory and the HUD.
