using UnityEngine;

/// <summary>
/// Identifies which Atlas AI specialist this data describes.
/// Matches the four entries in the AI Personality Bible (UX_DIVISION/05_AI_PERSONALITY_INTERACTION_BIBLE.md).
/// </summary>
public enum AIIdentity { Ajani = 0, Minerva = 1, Hermes = 2, Council = 3, Atlas = 4 }

/// <summary>
/// ScriptableObject that captures a single AI specialist's visual identity and animation timing.
///
/// Colour values and pulse durations are locked to the tokens defined in:
///   themes/atlas_color_tokens.json
///   themes/atlas_motion_tokens.json
///
/// Usage: Create instances via Assets ▶ Create ▶ Atlas ▶ AI Personality Data.
///        Four pre-built instances live in Assets/RESOURCES/AI/.
/// </summary>
[CreateAssetMenu(fileName = "AIPersonalityData", menuName = "Atlas/AI Personality Data", order = 1)]
public class AIPersonalityData : ScriptableObject
{
    // ── Identity ──────────────────────────────────────────────────────────────

    [Header("Identity")]
    public AIIdentity identity;
    public string displayName;
    [TextArea(2, 4)]
    public string role;

    // ── Colours  (from atlas_color_tokens.json) ───────────────────────────────

    [Header("Colours")]
    [Tooltip("Primary brand colour. Use for bright accents and icon tints.")]
    public Color primaryColor;

    [Tooltip("Soft fill colour. Use for background tints and panel fills.")]
    public Color softColor;

    [Tooltip("Edge / glow colour. Use for border highlights and ring glows.")]
    public Color edgeColor;

    // ── Animation  (from atlas_motion_tokens.json) ────────────────────────────

    [Header("Animation")]
    [Tooltip("Orb pulse cycle length in milliseconds.  Ajani=1800  Minerva=2200  Hermes=1400  Council=2600")]
    public float pulseDurationMs;
}
