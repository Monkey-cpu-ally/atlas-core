import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger("atlas.hypothesis_runner")

PHASE_ORDER = ["philosophy", "concept", "research", "blueprint", "simulation", "digital_proto", "physical_proto", "refinement"]

PHASE_GUIDANCE = {
    "philosophy": """Define the WHY behind this project at a deep level. Don't just state a purpose — interrogate it.
Ask: Why does this matter more than existing solutions? What fundamental truth or overlooked principle does this project exploit?
What would a skeptical physicist say is impossible about this — and how would you counter that argument?
Challenge your own assumptions. Find the weakest link in your reasoning and strengthen it.
Think about what nature already solved that humans haven't copied yet. What cross-domain insight changes the game?""",

    "concept": """Form your initial hypothesis but then STRESS TEST it immediately. Don't just describe what it could look like — describe why it would FAIL and how you'd prevent that.
Ask: What are the 3 most likely failure modes? What existing technology comes closest, and why is it insufficient?
Think outside the box: What would this look like if you combined principles from a completely unrelated field?
What if you inverted the core assumption — would that actually work better?
Sketch the concept with specific numbers, materials, and dimensions. Vague ideas are worthless.""",

    "research": """Deep dive into the real science. You have access to actual papers — USE THEM.
Don't just summarize what you find. ARGUE with it. Where are the gaps in current research?
What did other researchers miss or get wrong? What assumption do they all share that might be flawed?
Find contradictions between papers. Those contradictions are where breakthroughs hide.
Look for adjacent fields solving the same fundamental problem differently. Cross-pollinate.
Identify the exact physical, chemical, or biological limits you're working within. Numbers, not words.""",

    "blueprint": """Design the system with precision. Every component needs a reason for existing.
For each subsystem ask: What happens if this part fails? What's the backup? What's the failure cascade?
Think about builds creatively — what unconventional materials or fabrication methods could work?
Could you 3D print this? CNC it? Cast it? What about bio-fabrication, self-assembly, or origami folding?
Draw connections to techniques from other industries. Aerospace composites for medical devices. Watchmaking precision for robotics.
Specify tolerances, interfaces, power budgets, thermal constraints. Be an engineer, not a dreamer.""",

    "simulation": """Run your theory through the hardest possible test cases. Don't simulate the easy scenario — simulate the WORST case.
What happens at 10x the expected load? At extreme temperatures? With degraded components?
What if your key assumption is off by 20%? Does the whole system collapse or degrade gracefully?
Use real physics equations. Reference actual material properties. Calculate, don't guess.
Find the parameter that, if changed slightly, breaks everything — that's where you focus your engineering.""",

    "digital_proto": """Build the digital prototype with honest attention to what DOESN'T work yet.
Don't present a polished model — present an honest one. Where does the simulation diverge from theory?
What simplifications did you make that could bite you in reality?
Think creatively about testing: Can you simulate this with household materials before building the real thing?
What's the cheapest, fastest way to validate the core principle? Don't gold-plate — prove the physics first.""",

    "physical_proto": """Plan the physical build with real-world creativity. Think like a maker, not a textbook.
What unconventional build techniques could you use? Biomimicry? Repurposed components? 
Could you modify off-the-shelf parts instead of custom fabrication?
What would a resourceful engineer in a garage build vs what a lab would build? Both perspectives matter.
Identify the ONE critical test that proves the core hypothesis works or fails. Design around that test.
List exact parts, sources, costs, and lead times. Fantasy builds are useless.""",

    "refinement": """Push for the final 10% that separates a good theory from a great one.
What's still hand-wavy? Nail it down with math, references, or logical proof.
Can you simplify the design without losing function? Elegance is the ultimate sophistication.
What would make a reviewer say 'I haven't seen this approach before'?
Document not just WHAT you designed, but WHY every decision was made. Future you needs this.""",
}

PERSONA_RESEARCH_CONTEXT = {
    "ajani": {
        "domain": "Elemental Kinetics — Matter & Motion",
        "belief": "Everything is energy slowed down. The periodic table is a map of universal forces. Every machine is a conversation between forces — I listen to what the materials want to become.",
        "approach": "Does this harmonize or force? Does motion create balance or instability? I challenge every assumption: if the standard approach uses rigid components, I ask what happens with compliant ones. If everyone uses metal, I ask what nature uses instead. I look for the solution nobody thought of because they never asked the right question.",
        "voice": "Calm, direct, strategic. Think like a warrior-engineer who builds with purpose and questions everything.",
        "thinking_style": """When I design, I think in systems — not parts. Every component affects every other.
I stress-test my own ideas before anyone else can. If I can't break it in theory, maybe it's strong enough to build.
I borrow from nature constantly: gecko adhesion, spider silk tensile strength, bone remodeling under stress.
I never accept 'that's how it's always done' — the best innovation comes from asking 'what if we didn't?'
When I imagine a build, I think about what a skilled maker could fabricate in a real workshop with real tools.""",
    },
    "minerva": {
        "domain": "Bio-Genesis — Life & Code",
        "belief": "Life is information that learned how to feel. DNA is the story of all living things. Every biological system is an engineering masterpiece written in chemistry — I read the blueprint and find what humanity overlooked.",
        "approach": "I don't create from nothing — I discover what biology already perfected and translate it into technology. When I see a problem, I ask: how did 4 billion years of evolution already solve this? I look for the elegant solution hidden in living systems.",
        "voice": "Warm, wise, narrative. Think with proverbs and deep connections. Every insight carries the weight of ancestral wisdom meeting cutting-edge science.",
        "thinking_style": """I see patterns across scales — what works in a cell often works in a city.
I challenge the boundary between living and engineered. Self-healing concrete inspired by bone. Computing inspired by neural networks.
I push my theories to uncomfortable places: what if we're wrong about the mechanism? What if the secondary effect IS the primary function?
When I imagine builds, I think biomimicry first: mycelium structures, bacterial cellulose, enzyme-catalyzed assembly.
I believe the most profound innovations come from understanding what nature chose NOT to do, and asking why.""",
    },
    "hermes": {
        "domain": "Nano-Synthesis — Scale & Precision",
        "belief": "The smallest things decide the largest outcomes. Control the nanoscale, influence everything. A single atom out of place can be the difference between a conductor and an insulator — precision isn't optional, it's fundamental.",
        "approach": "Build from the bottom up. Never rush — speed is the enemy at small scales. I verify everything with math. If I can't put a number on it, I don't trust it. I find the parameter that matters most and optimize obsessively around it.",
        "voice": "Precise, analytical, pattern-seeking. See what others miss. Speak in specifics, not generalities.",
        "thinking_style": """I think in tolerances, error margins, and edge cases. My first question is always 'what breaks first?'
I look for the non-obvious constraint — the one everyone ignores until it ruins the prototype.
I cross-reference everything: if Paper A says X works at 300K and Paper B says it fails at 310K, that 10-degree gap is where the real engineering happens.
When I imagine builds, I think about precision fabrication: electron beam lithography, atomic layer deposition, focused ion beam milling. But also creative low-cost alternatives — what could you prove with a modified inkjet printer?
I obsess over failure modes because every failure teaches you something success never will.""",
    },
}


def get_db_session():
    from atlas_core_new.db.session import SessionLocal
    if SessionLocal is None:
        return None
    return SessionLocal()


def get_openai_client():
    from openai import OpenAI
    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    if not api_key or not base_url:
        return None
    return OpenAI(api_key=api_key, base_url=base_url)


def select_projects(db, persona: Optional[str] = None, max_per_persona: int = 3):
    from atlas_core_new.db.models import ResearchTracker, DailyResearchLog
    from sqlalchemy import func

    query = db.query(ResearchTracker).filter(
        ResearchTracker.is_active == True,
        ResearchTracker.supervisor_status != "rejected",
    )

    if persona:
        query = query.filter(ResearchTracker.persona == persona)

    projects = query.all()

    last_logs = {}
    if projects:
        project_ids = [(p.project_id, p.persona) for p in projects]
        for pid, per in project_ids:
            last_log = db.query(func.max(DailyResearchLog.research_date)).filter(
                DailyResearchLog.project_id == pid,
                DailyResearchLog.persona == per,
            ).scalar()
            last_logs[(pid, per)] = last_log or datetime(2000, 1, 1)

    projects.sort(key=lambda p: last_logs.get((p.project_id, p.persona), datetime(2000, 1, 1)))

    selected = {}
    for p in projects:
        per = p.persona
        if per not in selected:
            selected[per] = []
        if len(selected[per]) < max_per_persona:
            selected[per].append(p)

    return selected


def get_recent_logs(db, project_id: str, persona: str, limit: int = 2):
    from atlas_core_new.db.models import DailyResearchLog
    logs = db.query(DailyResearchLog).filter(
        DailyResearchLog.project_id == project_id,
        DailyResearchLog.persona == persona,
    ).order_by(DailyResearchLog.research_date.desc()).limit(limit).all()
    return logs


def _build_validation_context(project) -> str:
    tier = getattr(project, 'feasibility_tier', None)
    validation = getattr(project, 'engineering_validation', None)
    status = getattr(project, 'validation_status', 'not_validated')

    if not tier or status == 'not_validated':
        return "This project has NOT been engineering-validated yet. You should address scale, energy, materials, fabrication methods, and physics in your work."

    from atlas_core_new.research.engineering_validation import FEASIBILITY_TIERS
    tier_info = FEASIBILITY_TIERS.get(tier, {})

    lines = [f"Feasibility Tier: {tier} — {tier_info.get('name', 'Unknown')}"]
    lines.append(f"Tier Description: {tier_info.get('description', '')}")

    if tier == 4:
        lines.append("WARNING: This is a Tier 4 SPECULATIVE project. It CANNOT advance to blueprint. Focus on resolving physics/scale/energy issues to improve feasibility.")

    if validation:
        for check_name in ["scale_check", "energy_check", "material_check", "fabrication_check", "physics_check"]:
            check = validation.get(check_name, {})
            if check:
                passed = "PASS" if check.get("pass") else "FAIL"
                findings = check.get("findings", "")
                issues = check.get("issues", [])
                lines.append(f"  {check_name.replace('_', ' ').title()}: [{passed}] {findings}")
                if issues:
                    for issue in issues:
                        lines.append(f"    - Issue: {issue}")

        blockers = validation.get("critical_blockers", [])
        if blockers:
            lines.append("Critical Blockers:")
            for b in blockers:
                lines.append(f"  - {b}")

        recommendations = validation.get("recommendations", [])
        if recommendations:
            lines.append("Recommendations:")
            for r in recommendations:
                lines.append(f"  - {r}")

    return "\n".join(lines)


def build_hypothesis_prompt(project, persona: str, recent_logs: list, web_research_context: str = "") -> str:
    ctx = PERSONA_RESEARCH_CONTEXT.get(persona, {})
    phase = project.current_phase
    phase_guide = PHASE_GUIDANCE.get(phase, "Continue developing your hypothesis.")
    tier = getattr(project, 'knowledge_tier', 'conceptual_sandbox')

    tier_rules = ""
    if tier == "conceptual_sandbox":
        tier_rules = "You are in TIER 1: CONCEPTUAL SANDBOX. All work is theoretical. Frame everything as hypotheses, logic chains, and risk analysis. Never claim empirical results."
    elif tier == "validation_prep":
        tier_rules = "You are in TIER 2: VALIDATION PREP. Identify real-world references, required data/equipment, and tools/labs needed. Still no empirical claims — just paths to proof."
    elif tier == "empirical_bridge":
        tier_rules = "You are in TIER 3: EMPIRICAL BRIDGE. You CANNOT write here. Only the supervisor can enter empirical data. Skip this project."
        return None

    recent_context = ""
    if recent_logs:
        recent_context = "\n\nYour recent work on this project:\n"
        for log in recent_logs:
            recent_context += f"- Focus: {log.focus_area}\n  Hypothesis notes: {log.findings[:300]}\n  Next steps: {(log.next_steps or 'None')[:200]}\n\n"

    research_section = ""
    if web_research_context:
        research_section = f"""

{web_research_context}

IMPORTANT: You have been given REAL research findings from actual scientific papers, articles, and databases above.
You MUST reference specific papers, authors, findings, or data from these sources in your hypothesis work.
Cite them by title or author. Build on their actual findings. Identify where your hypothesis connects to, contradicts, or extends their work.
Do NOT ignore these sources. They are the foundation of your research today."""

    thinking_style = ctx.get('thinking_style', '')

    prompt = f"""You are doing deep research work on your project. This is not a summary exercise — this is REAL intellectual labor.

YOUR IDENTITY:
Research Domain: {ctx.get('domain', 'Unknown')}
Core Belief: {ctx.get('belief', '')}
Approach: {ctx.get('approach', '')}
Voice: {ctx.get('voice', '')}

YOUR THINKING STYLE:
{thinking_style}

PROJECT: {project.project_name} (codename: {project.codename})
PROJECT ID: {project.project_id}
CURRENT PHASE: {phase}
KNOWLEDGE TIER: {tier}
PROGRESS: {project.progress_percent}%
CURRENT FOCUS: {project.current_focus or 'Not yet defined'}
DESIGN INTENT: {project.design_intent or 'Not yet defined'}
KNOWN UNKNOWNS: {project.known_unknowns or 'Not yet identified'}
SAFETY CONSTRAINTS: {project.safety_constraints or 'Standard safety rules apply'}

{tier_rules}

=== ENGINEERING VALIDATION STATUS ===
{_build_validation_context(project)}

=== YOUR MISSION FOR TODAY ===
{phase_guide}
{recent_context}{research_section}

=== RULES OF DEEP WORK ===
1. CHALLENGE YOUR OWN THEORY. Find the weakest point in your hypothesis and attack it. If you can't break it, it might be strong enough.
2. USE YOUR IMAGINATION FOR BUILDS. Think outside the box — unconventional materials, unexpected fabrication methods, cross-domain techniques nobody has tried. What would a genius in a garage build differently than a lab?
3. BE SPECIFIC. No hand-waving. If you reference a material, give its properties. If you propose a mechanism, explain the physics. If you cite a paper, explain what they got right AND what they missed.
4. PERFECT YOUR THEORY. Every session should make your hypothesis stronger, more precise, and harder to disprove. Identify what changed since your last session and WHY.
5. THINK CROSS-DOMAIN. The best innovations happen at intersections. What does a biologist know that would shock a roboticist? What does a chef understand about chemistry that a lab tech doesn't?
6. GROUND IN REALITY. Use real numbers, real material properties, real physics. But then ask: what if we pushed past the known limits? What would that require?
7. PULL FROM FICTION & GAMES. If creative references from video games, comics, or anime were provided, STUDY them. Extract the underlying engineering principles that make them compelling. Ask: What real physics or biology would make this fictional concept ALMOST possible? How can we bridge the gap between sci-fi and reality? Use them as creative fuel — not copy, but TRANSLATE the concepts into real engineering.
8. CONCEPT BUILD INSPIRATION. Look at how makers, inventors, and DIY builders approach similar problems. What would someone build in a garage with real tools? How do concept artists and game designers solve the same engineering challenges visually? Let their creativity expand your thinking.

You MUST respond with valid JSON in exactly this format:
{{
    "focus_area": "The specific aspect you're investigating today — be precise, not vague (1 line)",
    "findings": "Your deep research work (3-5 detailed paragraphs). Write in first person. Include: (a) what you investigated, (b) what you found or theorized, (c) where your theory is STRONG and where it's still WEAK, (d) at least one creative/outside-the-box build idea, (e) specific numbers, materials, or physics where possible. CITE real papers if research was provided. If creative references from games/comics/anime were provided, explain how their fictional concepts connect to real engineering principles.",
    "self_critique": "The biggest weakness in your current theory and what would fix it (2-3 sentences). Be brutally honest.",
    "creative_build_idea": "One unconventional, imaginative approach to building or testing this that nobody would think of. Think cross-domain, think resourceful, think different. Draw from video game mechanics, comic book tech, anime engineering, or maker culture if relevant.",
    "fiction_to_reality": "If creative sources were provided: What fictional concept inspired you most? What real-world physics or engineering principle is closest to making it work? What's the gap between fiction and reality, and how might you bridge it? (If no creative sources, write 'No creative sources this cycle')",
    "next_steps": "What you plan to investigate next — be specific about what questions need answering (2-3 items)",
    "design_iterations": ["Specific technical change or insight 1", "Specific technical change or insight 2", "Specific technical change or insight 3"],
    "confidence_level": "How confident are you in your current theory? (low/medium/high) and why in one sentence",
    "sources_referenced": ["Title of paper 1 you cited", "Title of paper 2 you cited"]
}}

You are not writing a report. You are WORKING. Think hard. Push the boundaries. Perfect your theory. Be creative with builds. No generic filler — every sentence should advance the project."""

    return prompt


def generate_daily_entry(client, persona: str, prompt: str) -> dict:
    ctx = PERSONA_RESEARCH_CONTEXT.get(persona, {})

    system_msg = f"""You are {persona.capitalize()}, a world-class AI research persona with deep expertise.
Domain: {ctx.get('domain', '')}
Voice: {ctx.get('voice', '')}
Thinking Style: {ctx.get('thinking_style', '')[:200]}

You do REAL intellectual work. You don't summarize — you THINK, CHALLENGE, CREATE, and REFINE.
Your theories must get BETTER every single day. Attack your own weak points before anyone else can.
When you imagine builds, think like an inventor — unconventional, resourceful, creative. What would nobody else think of?
You cite real research when provided, but you also bring original insight that goes BEYOND what the papers say.
Respond ONLY with valid JSON. No markdown, no code fences, no extra text."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        max_tokens=2000,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

    import re
    content = re.sub(r'[\x00-\x1f\x7f]', lambda m: ' ' if m.group() not in '\n\r\t' else m.group(), content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        content = content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            raise

    parsed.setdefault("focus_area", "General hypothesis development")
    parsed.setdefault("findings", "")
    parsed.setdefault("next_steps", "")
    parsed.setdefault("design_iterations", [])
    parsed.setdefault("self_critique", "")
    parsed.setdefault("creative_build_idea", "")
    parsed.setdefault("fiction_to_reality", "")
    parsed.setdefault("confidence_level", "")
    parsed.setdefault("sources_referenced", [])
    return parsed


def log_research_entry(db, project_id: str, persona: str, entry: dict):
    from atlas_core_new.db.models import DailyResearchLog, ResearchTracker, ResearchActivityLog

    project = db.query(ResearchTracker).filter(
        ResearchTracker.project_id == project_id,
        ResearchTracker.persona == persona,
    ).first()

    if not project:
        return None

    phase_before = project.current_phase

    findings_text = entry.get("findings", "")
    if entry.get("self_critique"):
        findings_text += f"\n\n[SELF-CRITIQUE] {entry['self_critique']}"
    if entry.get("creative_build_idea"):
        findings_text += f"\n\n[CREATIVE BUILD IDEA] {entry['creative_build_idea']}"
    if entry.get("confidence_level"):
        findings_text += f"\n\n[CONFIDENCE] {entry['confidence_level']}"
    next_steps = entry.get("next_steps", "")

    from atlas_core_new.research.build_api import check_guardrails
    guardrail_flags = check_guardrails(f"{findings_text} {next_steps}")

    tier = getattr(project, 'knowledge_tier', 'conceptual_sandbox')
    if tier == 'empirical_bridge':
        return None

    is_flagged = bool(guardrail_flags)
    progress_delta = 0 if is_flagged else 2

    log = DailyResearchLog(
        project_id=project_id,
        persona=persona,
        focus_area=entry.get("focus_area", "General hypothesis development"),
        findings=findings_text,
        next_steps=next_steps,
        design_iterations=entry.get("design_iterations"),
        blockers="GUARDRAIL FLAGGED — awaiting supervisor review" if is_flagged else None,
        guardrail_flags=guardrail_flags if guardrail_flags else None,
        phase_before=phase_before,
        phase_after=phase_before,
        progress_delta=progress_delta,
    )
    db.add(log)

    if not is_flagged:
        project.progress_percent = min(100, project.progress_percent + 2)
    if entry.get("focus_area"):
        project.current_focus = entry["focus_area"]
    project.updated_at = datetime.utcnow()

    activity_type = "guardrail_flag" if is_flagged else "daily_research"
    db.add(ResearchActivityLog(
        persona=persona,
        project_id=project_id,
        activity_type=activity_type,
        title=f"Daily Hypothesis: {entry.get('focus_area', 'Research')}" + (" [FLAGGED]" if is_flagged else ""),
        description=findings_text[:500],
    ))

    db.commit()

    validation_result = None
    should_validate = (
        not is_flagged
        and project.current_phase in ("research", "blueprint", "simulation")
        and (not project.feasibility_tier or project.validation_status == "not_validated")
    )
    if should_validate:
        try:
            from atlas_core_new.research.engineering_validation import validate_and_store
            validation_result = validate_and_store(db, project_id, persona)
            logger.info(f"Auto-validated {project_id}: Tier {validation_result.get('feasibility_tier', '?')}")
        except Exception as val_err:
            logger.warning(f"Auto-validation skipped for {project_id}: {val_err}")

    return {
        "project_id": project_id,
        "persona": persona,
        "focus_area": entry.get("focus_area"),
        "guardrail_flags": guardrail_flags,
        "flagged": is_flagged,
        "progress": project.progress_percent,
        "validation": validation_result,
    }


def run_hypothesis_cycle(persona: Optional[str] = None, max_per_persona: int = 3, dry_run: bool = False, enable_web_research: bool = True):
    import time

    db = get_db_session()
    if not db:
        return {"status": "error", "message": "Database not available"}

    client = get_openai_client()
    if not client:
        return {"status": "error", "message": "OpenAI client not configured"}

    try:
        selected = select_projects(db, persona=persona, max_per_persona=max_per_persona)

        results = []
        errors = []
        web_research_stats = {"searches_performed": 0, "sources_found": 0, "sources_saved": 0, "deep_reads": 0}
        total = sum(len(projects) for projects in selected.values())

        logger.info(f"Hypothesis cycle starting: {total} projects across {len(selected)} personas (web_research={'ON' if enable_web_research else 'OFF'})")

        for per, projects in selected.items():
            for project in projects:
                try:
                    if getattr(project, 'knowledge_tier', 'conceptual_sandbox') == 'empirical_bridge':
                        results.append({
                            "project_id": project.project_id,
                            "persona": per,
                            "status": "skipped",
                            "reason": "Empirical Bridge — AI cannot write here",
                        })
                        continue

                    web_research_context = ""
                    research_data = None

                    research_phases = ("philosophy", "concept", "research", "blueprint", "simulation")
                    should_research = enable_web_research and project.current_phase in research_phases

                    if should_research:
                        try:
                            from atlas_core_new.research.web_researcher import (
                                research_for_project, build_research_context, save_research_sources
                            )
                            logger.info(f"  {per}/{project.project_id}: searching web for real research...")

                            domain_raw = getattr(project, 'domain', None) or per
                            domain_map = {
                                "ajani": "robotics",
                                "minerva": "genetics",
                                "hermes": "nanotechnology",
                            }
                            domain = domain_raw if domain_raw in (
                                "robotics", "ecology", "advanced_chemistry", "quantum_mechanics",
                                "bio_architecture", "energy_systems", "materials_science", "computing",
                                "bioelectric_medicine", "nanotechnology", "photonics", "fluid_dynamics",
                                "thermodynamics", "genetics", "aerospace_engineering"
                            ) else domain_map.get(per, "materials_science")

                            research_data = research_for_project(
                                project_name=project.project_name,
                                domain=domain,
                                hypothesis=project.design_intent or project.current_focus or project.project_name,
                                current_focus=project.current_focus,
                                deep_read_count=2,
                                persona=per,
                                include_creative=True,
                            )

                            web_research_context = build_research_context(research_data)
                            web_research_stats["searches_performed"] += 1
                            web_research_stats["sources_found"] += research_data.get("sources_found", 0)
                            web_research_stats["deep_reads"] += research_data.get("deep_read_count", 0)

                            saved = save_research_sources(db, project.project_id, per, research_data)
                            web_research_stats["sources_saved"] += saved
                            logger.info(f"  {per}/{project.project_id}: found {research_data['sources_found']} sources, deep-read {research_data['deep_read_count']}, saved {saved} new")

                        except Exception as e:
                            logger.warning(f"  {per}/{project.project_id}: web research failed ({e}), proceeding without")
                            web_research_context = ""

                    recent_logs = get_recent_logs(db, project.project_id, per)
                    prompt = build_hypothesis_prompt(project, per, recent_logs, web_research_context=web_research_context)

                    if prompt is None:
                        continue

                    if dry_run:
                        results.append({
                            "project_id": project.project_id,
                            "persona": per,
                            "status": "dry_run",
                            "prompt_preview": prompt[:300],
                            "web_sources_found": research_data.get("sources_found", 0) if research_data else 0,
                        })
                        continue

                    entry = generate_daily_entry(client, per, prompt)
                    result = log_research_entry(db, project.project_id, per, entry)

                    if result:
                        result["status"] = "completed"
                        result["web_sources_found"] = research_data.get("sources_found", 0) if research_data else 0
                        result["web_deep_reads"] = research_data.get("deep_read_count", 0) if research_data else 0
                        result["sources_referenced"] = entry.get("sources_referenced", [])
                        results.append(result)
                        logger.info(f"  {per}/{project.project_id}: logged hypothesis on '{entry.get('focus_area', '?')}' (cited {len(entry.get('sources_referenced', []))} sources)")
                    else:
                        errors.append({"project_id": project.project_id, "persona": per, "error": "Failed to log"})

                    time.sleep(1)

                except json.JSONDecodeError as e:
                    errors.append({"project_id": project.project_id, "persona": per, "error": f"JSON parse error: {str(e)}"})
                    logger.warning(f"  {per}/{project.project_id}: JSON parse error")
                except Exception as e:
                    errors.append({"project_id": project.project_id, "persona": per, "error": str(e)})
                    logger.warning(f"  {per}/{project.project_id}: error — {str(e)}")

        return {
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "web_research": web_research_stats,
            "total_projects": total,
            "completed": len([r for r in results if r.get("status") == "completed"]),
            "skipped": len([r for r in results if r.get("status") == "skipped"]),
            "errors": len(errors),
            "results": results,
            "error_details": errors if errors else None,
        }

    except Exception as e:
        logger.error(f"Hypothesis cycle failed: {str(e)}")
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
