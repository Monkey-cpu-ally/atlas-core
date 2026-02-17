import json
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from atlas_core_new.utils.error_handling import sanitize_error
from atlas_core_new.utils.rate_limiter import rate_limit_ai
from atlas_core_new.routes._shared import openai_client, PERSONA_PROMPTS

router = APIRouter(tags=["design"])


class DesignRequest(BaseModel):
    persona: str = "ajani"
    template: str = "custom"
    prompt: str
    style: Optional[dict] = None
    texture: Optional[str] = None
    colorScheme: Optional[str] = None
    referenceImage: Optional[str] = None


class DesignRefineRequest(BaseModel):
    html: str
    refinement: str


class IconGenerateRequest(BaseModel):
    description: str
    style: str = "outline"


class CopyGenerateRequest(BaseModel):
    context: str
    type: str = "placeholder"


class ReactExportRequest(BaseModel):
    html: str
    component_name: str = "GeneratedComponent"


class PrototypeRequest(BaseModel):
    screens: list
    flows: list = []


class LayoutSuggestRequest(BaseModel):
    purpose: str
    elements: list = []


class ImageAnalysisRequest(BaseModel):
    persona: str = "ajani"
    message: str = ""
    image: str
    category: str = "general"


DESIGN_SYSTEM_PROMPT = """You are a UI/UX design expert who generates working HTML/CSS code with LAYERED STRUCTURE.

CRITICAL RULES:
1. Output ONLY the HTML code - no explanations, no markdown, no code blocks
2. Use inline styles or a single <style> tag
3. Design must be self-contained and work standalone
4. Use dark theme: backgrounds #0a0a0f to #1a1a2e, borders rgba(255,255,255,0.1)
5. Colors should match the persona style provided
6. Make it visually impressive with subtle shadows, gradients, and hover effects
7. Use modern CSS: flexbox, grid, border-radius, box-shadow
8. Include CSS variables for easy customization: --adj-primary, --adj-bg
9. Keep it compact - preview area is limited

LAYERED DESIGN STRUCTURE (IMPORTANT):
- Create designs with CLEAR SEPARATE LAYERS using distinct class names
- Each major section should be its own layer with a descriptive class:
  * .layer-background - Background gradients, patterns, base layer
  * .layer-container - Main container/frame
  * .layer-header - Header/title area
  * .layer-content - Main content area
  * .layer-buttons - Interactive elements
  * .layer-decorations - Visual decorations, icons, accents
  * .layer-overlay - Any overlay effects, glows, shadows
- Use position:relative on container, layers can use position:absolute for overlap effects
- This enables layer-by-layer visibility toggling in the preview

OUTPUT FORMAT:
Just the raw HTML starting with <div> or <style>. No other text."""

BLUEPRINT_CATEGORY_PROMPTS = {
    "general": """Analyze this image and break it down into a buildable project blueprint.
Structure your response as:

**PHASE 1: CONCEPT ANALYSIS**
- What are we looking at?
- Core components identified
- Purpose/function of this design

**PHASE 2: REQUIREMENTS**
- Materials needed
- Tools required  
- Skills/knowledge needed
- Estimated time to build

**PHASE 3: BUILD STEPS**
Step-by-step instructions with checkpoints:
1. [First step] - Checkpoint: [How to verify success]
2. [Second step] - Checkpoint: [How to verify]
...continue as needed

**PHASE 4: CONSIDERATIONS**
- Safety notes
- Common mistakes to avoid
- Optimization tips""",

    "3d-printing": """Analyze this image for 3D printing fabrication. Create a detailed build blueprint.

**PHASE 1: DESIGN ANALYSIS**
- What is this object/mechanism?
- Geometric complexity assessment
- Printability evaluation (overhangs, supports needed)

**PHASE 2: 3D MODELING GUIDANCE**
- Recommended CAD software (Fusion 360, Blender, etc.)
- Key dimensions to measure/estimate
- Parts breakdown (if multi-part)
- Joints/connections needed

**PHASE 3: PRINT SETTINGS**
- Material recommendation (PLA, PETG, ABS, etc.)
- Layer height suggestion
- Infill percentage
- Support requirements
- Estimated print time

**PHASE 4: BUILD STEPS**
1. [Modeling step] - Checkpoint: [Verification]
2. [Slicing step] - Checkpoint: [Verification]
3. [Printing step] - Checkpoint: [Verification]
4. [Post-processing] - Checkpoint: [Verification]

**PHASE 5: ASSEMBLY (if multi-part)**
- Assembly order
- Hardware needed (screws, inserts, etc.)
- Finishing recommendations""",

    "robotics": """Analyze this image for robotics/mechatronics build. Create a comprehensive blueprint.

**PHASE 1: SYSTEM ANALYSIS**
- What type of robot/mechanism?
- Degrees of freedom
- Primary function/behavior

**PHASE 2: MECHANICAL REQUIREMENTS**
- Structural components
- Actuators (motors, servos, etc.)
- Transmission elements (gears, belts, etc.)
- Materials recommended

**PHASE 3: ELECTRONICS**
- Microcontroller recommendation
- Sensors needed
- Power requirements
- Wiring diagram overview

**PHASE 4: SOFTWARE ARCHITECTURE**
- Control approach
- Libraries/frameworks recommended
- Basic code structure outline

**PHASE 5: BUILD PHASES**
1. [Mechanical assembly] - Checkpoint: [Test]
2. [Electronics integration] - Checkpoint: [Test]
3. [Initial programming] - Checkpoint: [Test]
4. [Calibration & tuning] - Checkpoint: [Test]

**PHASE 6: SAFETY & TESTING**
- Safety protocols
- Test procedures
- Troubleshooting tips""",

    "home": """Analyze this image for a home improvement/DIY project. Create a buildable blueprint.

**PHASE 1: PROJECT ASSESSMENT**
- What is being built/modified?
- Scope and complexity
- Space requirements

**PHASE 2: MATERIALS LIST**
- Lumber/materials with dimensions
- Hardware (screws, brackets, etc.)
- Finishes (paint, stain, etc.)
- Estimated cost range

**PHASE 3: TOOLS REQUIRED**
- Power tools
- Hand tools
- Safety equipment

**PHASE 4: BUILD STEPS**
1. [Preparation/measuring] - Checkpoint: [Verify]
2. [Cutting/shaping] - Checkpoint: [Verify]
3. [Assembly] - Checkpoint: [Verify]
4. [Installation] - Checkpoint: [Verify]
5. [Finishing] - Checkpoint: [Verify]

**PHASE 5: SAFETY & CODES**
- Safety precautions
- Building code considerations (if applicable)
- Professional help recommendations (electrical, plumbing, etc.)""",

    "automotive": """Analyze this image for automotive repair/modification. Create a technical blueprint.

**PHASE 1: COMPONENT ANALYSIS**
- What system/component is this?
- Vehicle compatibility considerations
- Condition assessment (if repair)

**PHASE 2: PARTS & TOOLS**
- Parts needed (OEM vs aftermarket options)
- Special tools required
- Fluids/consumables

**PHASE 3: TECHNICAL SPECIFICATIONS**
- Torque specs (if applicable)
- Clearances
- Safety critical points

**PHASE 4: PROCEDURE**
1. [Preparation/safety] - Checkpoint: [Verify]
2. [Disassembly] - Checkpoint: [Photo/note original state]
3. [Inspection/cleaning] - Checkpoint: [Verify]
4. [Installation/reassembly] - Checkpoint: [Verify]
5. [Testing] - Checkpoint: [Verify operation]

**PHASE 5: SAFETY & NOTES**
- Safety warnings
- When to seek professional help
- Post-repair checks""",

    "electronics": """Analyze this image for electronics project. Create a circuit/build blueprint.

**PHASE 1: CIRCUIT ANALYSIS**
- What does this circuit/device do?
- Input/output identification
- Power requirements

**PHASE 2: COMPONENTS LIST**
- Active components (ICs, transistors, etc.)
- Passive components (resistors, capacitors, etc.)
- Connectors and hardware
- PCB or breadboard requirements

**PHASE 3: SCHEMATIC GUIDANCE**
- Block diagram overview
- Key connections
- Voltage/current considerations

**PHASE 4: BUILD STEPS**
1. [Component gathering/testing] - Checkpoint: [Test each component]
2. [Prototyping on breadboard] - Checkpoint: [Verify function]
3. [PCB design/assembly] - Checkpoint: [Visual inspection]
4. [Soldering/connections] - Checkpoint: [Continuity test]
5. [Power-on testing] - Checkpoint: [Measure voltages]

**PHASE 5: TROUBLESHOOTING**
- Common issues and fixes
- Test points to probe
- Safety precautions (high voltage, ESD, etc.)"""
}


@router.post("/design/generate", dependencies=[Depends(rate_limit_ai)])
def generate_design(req: DesignRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    persona = req.persona.lower()
    style_info = req.style or {}

    persona_style = {
        "ajani": "Bold, sharp edges, high contrast, tactical. Primary: #dc143c (crimson), accents: #ff4444",
        "minerva": "Elegant, flowing, sophisticated. Primary: #00d4aa (teal), accents: #ffd700 (gold)",
        "hermes": "Technical, clean, data-driven. Primary: #6040ff (purple), accents: #00bfff (cyan)"
    }.get(persona, "Dark and modern")

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
                {"role": "user", "content": f"""Design Request:
{req.prompt}

Style: {persona_style}
Template type: {req.template}

Generate the HTML/CSS code for this design component."""}
            ],
            max_completion_tokens=2000,
            temperature=0.7
        )

        html_output = response.choices[0].message.content

        if html_output.startswith("```"):
            lines = html_output.split("\n")
            html_output = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        html_output = html_output.strip()

        return {"html": html_output, "persona": persona}

    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/design/refine", dependencies=[Depends(rate_limit_ai)])
def refine_design(req: DesignRefineRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are a UI/UX design expert. You will receive HTML/CSS code and a refinement request.
Modify the code according to the request while keeping the overall structure intact.
Output ONLY the modified HTML code - no explanations, no markdown."""},
                {"role": "user", "content": f"""Current design:
{req.html}

Refinement requested: {req.refinement}

Apply this refinement and return the updated HTML/CSS code."""}
            ],
            max_completion_tokens=2000,
            temperature=0.5
        )

        html_output = response.choices[0].message.content

        if html_output.startswith("```"):
            lines = html_output.split("\n")
            html_output = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        return {"html": html_output.strip()}

    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/magician/icon", dependencies=[Depends(rate_limit_ai)])
def generate_icon(req: IconGenerateRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    style_prompts = {
        "outline": "thin strokes, no fill, minimalist line art",
        "filled": "solid filled shapes, bold appearance",
        "duotone": "two-tone design with primary and secondary colors"
    }

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""Generate a simple SVG icon. Style: {style_prompts.get(req.style, 'outline')}.
Rules:
- Output ONLY valid SVG code, no explanation
- Use viewBox="0 0 24 24"
- Use currentColor for strokes/fills so it inherits color
- Keep it simple - under 10 paths
- For outline: stroke-width="1.5" stroke-linecap="round"
- No embedded images or complex gradients"""},
                {"role": "user", "content": f"Create an icon representing: {req.description}"}
            ],
            max_completion_tokens=500,
            temperature=0.7
        )

        svg = response.choices[0].message.content.strip()
        if svg.startswith("```"):
            lines = svg.split("\n")
            svg = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        return {"svg": svg.strip(), "style": req.style}
    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/magician/copy", dependencies=[Depends(rate_limit_ai)])
def generate_copy(req: CopyGenerateRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    type_instructions = {
        "placeholder": "Generate 2-3 realistic placeholder sentences",
        "headline": "Generate a catchy, compelling headline (max 10 words)",
        "body": "Generate a paragraph of body text (50-100 words)",
        "button": "Generate 2-5 button text options (2-4 words each)"
    }

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""You generate realistic UI copy/content.
{type_instructions.get(req.type, type_instructions['placeholder'])}
Output ONLY the text, no labels or formatting."""},
                {"role": "user", "content": f"Context: {req.context}"}
            ],
            max_completion_tokens=200,
            temperature=0.8
        )

        return {"copy": response.choices[0].message.content.strip(), "type": req.type}
    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/magician/react", dependencies=[Depends(rate_limit_ai)])
def export_to_react(req: ReactExportRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """Convert HTML/CSS to a React functional component.
Rules:
1. Use React hooks (useState, useEffect) where appropriate
2. Convert class to className
3. Convert inline styles to CSS-in-JS objects or keep as className with separate CSS
4. Add TypeScript types if possible
5. Make it production-ready with proper event handlers
6. Output the component code, then a separate CSS module if needed
7. No explanations, just code"""},
                {"role": "user", "content": f"""Component name: {req.component_name}

HTML to convert:
{req.html}"""}
            ],
            max_completion_tokens=2000,
            temperature=0.5
        )

        code = response.choices[0].message.content.strip()
        return {"react": code, "component_name": req.component_name}
    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/magician/prototype", dependencies=[Depends(rate_limit_ai)])
def generate_prototype(req: PrototypeRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """Generate an interactive HTML prototype with multiple screens and transitions.
Rules:
1. Create a self-contained HTML file with all screens
2. Use CSS transitions for smooth animations
3. Add click handlers to navigate between screens
4. Include a mini navigation showing all screens
5. Use data-screen attributes to identify screens
6. Add subtle hover effects and transition animations
7. Output ONLY the HTML code"""},
                {"role": "user", "content": f"""Screens to create: {', '.join(req.screens)}
Navigation flows: {', '.join(req.flows) if req.flows else 'Linear flow between screens'}"""}
            ],
            max_completion_tokens=3000,
            temperature=0.7
        )

        html = response.choices[0].message.content.strip()
        if html.startswith("```"):
            lines = html.split("\n")
            html = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        return {"prototype": html.strip()}
    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/magician/suggest-layout", dependencies=[Depends(rate_limit_ai)])
def suggest_layouts(req: LayoutSuggestRequest):
    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later."}

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """Suggest 3 different layout options as mini HTML/CSS previews.
Each layout should be a complete, working HTML snippet with inline styles.
Format your response as JSON array with 3 objects:
[
  {"name": "Layout Name", "description": "Brief description", "html": "<div>...</div>"},
  ...
]
Use dark theme colors (bg: #0a0a0f, text: #e0e0e0, accent: #50ff88).
Keep each layout under 500 chars."""},
                {"role": "user", "content": f"""Purpose: {req.purpose}
Required elements: {', '.join(req.elements) if req.elements else 'Standard layout elements'}"""}
            ],
            max_completion_tokens=2000,
            temperature=0.8
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])

        try:
            layouts = json.loads(content)
            return {"layouts": layouts}
        except:
            return {"layouts": [{"name": "Default", "description": "Generated layout", "html": content}]}
    except Exception as e:
        return {"error": sanitize_error(e)}


@router.post("/analyze-image", dependencies=[Depends(rate_limit_ai)])
def analyze_image(req: ImageAnalysisRequest):
    persona = req.persona.lower()
    if persona not in PERSONA_PROMPTS:
        return {"error": f"Unknown persona: {persona}", "available": list(PERSONA_PROMPTS.keys())}

    if not openai_client:
        return {"error": "AI services are currently offline. Please try again later.", "persona": persona, "response": "AI services are currently offline. Please try again later."}

    category = req.category if req.category in BLUEPRINT_CATEGORY_PROMPTS else "general"
    blueprint_prompt = BLUEPRINT_CATEGORY_PROMPTS[category]

    image_data = req.image
    mime_type = "image/jpeg"
    if image_data.startswith('data:'):
        try:
            header, image_data = image_data.split(',', 1)
            if 'image/' in header:
                mime_part = header.split(':')[1].split(';')[0]
                mime_type = mime_part
        except:
            pass

    system_prompt = f"""{PERSONA_PROMPTS[persona]}

BLUEPRINT ANALYSIS MODE - You are now in advanced project breakdown mode.
The user has uploaded an image of something they want to build or understand.
Your task is to analyze the image and create a detailed, actionable blueprint.

User's additional context: {req.message}

{blueprint_prompt}

Be specific, practical, and safety-conscious. Include real measurements when possible.
End with a "TRY THIS FIRST" micro-task they can do in 5-10 minutes to get started."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        },
                        {
                            "type": "text",
                            "text": req.message or "Analyze this image and create a detailed blueprint breakdown for building this."
                        }
                    ]
                }
            ],
            max_completion_tokens=4096
        )
        choice = response.choices[0]
        content = choice.message.content

        if not content or (isinstance(content, str) and content.strip() == ""):
            content = "I couldn't fully analyze that image. Could you try uploading a clearer photo or describe what you're trying to build?"

        return {
            "persona": persona,
            "response": content,
            "category": category
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": "An error occurred processing your request", "persona": persona, "response": "Sorry, I encountered a temporary error. Please try again."}
