using UnityEngine;

/// <summary>
/// Expression states used by AIPortraitPanel to switch the displayed face portrait.
///
/// Combat is only valid for AIs where AIFaceProfile.supportsCombat is true (Ajani).
/// </summary>
public enum PortraitExpression
{
    Neutral  = 0,
    Thinking = 1,
    Speaking = 2,
    Approval = 3,
    Concern  = 4,
    Serious  = 5,
    Combat   = 6,
}

/// <summary>
/// ScriptableObject that holds the per-AI face profile for the portrait panel.
///
/// Each sprite slot is optional — if left null the portrait panel falls back to the
/// procedural face generator in AtlasTextureFactory.BuildPortraitFace(), which
/// produces a visually distinct holographic line-art face for every (AI, expression)
/// combination entirely from code, with no texture imports required.
///
/// Usage:
///   • Create via Assets ▶ Create ▶ Atlas ▶ AI Face Profile.
///   • Four pre-built instances live in Assets/RESOURCES/Faces/.
///   • Load at runtime with Resources.Load&lt;AIFaceProfile&gt;("Faces/Ajani_Face").
/// </summary>
[CreateAssetMenu(fileName = "AIFaceProfile", menuName = "Atlas/AI Face Profile", order = 2)]
public class AIFaceProfile : ScriptableObject
{
    // ── Identity ──────────────────────────────────────────────────────────────

    [Header("Identity")]
    public AIIdentity identity;

    [Tooltip("Enables the Combat expression for this AI. True for Ajani only.")]
    public bool supportsCombat;

    // ── Expression Sprites (null = procedural generation) ─────────────────────

    [Header("Expression Sprites (leave null to use procedural generation)")]
    public Sprite neutralSprite;
    public Sprite thinkingSprite;
    public Sprite speakingSprite;
    public Sprite approvalSprite;
    public Sprite concernSprite;
    public Sprite seriousSprite;
    public Sprite combatSprite;

    // ── Accessors ─────────────────────────────────────────────────────────────

    /// <summary>
    /// Returns the assigned Sprite for <paramref name="expression"/>, or null if none
    /// is assigned (the caller should fall back to procedural generation).
    /// </summary>
    public Sprite GetSprite(PortraitExpression expression)
    {
        switch (expression)
        {
            case PortraitExpression.Neutral:  return neutralSprite;
            case PortraitExpression.Thinking: return thinkingSprite;
            case PortraitExpression.Speaking: return speakingSprite;
            case PortraitExpression.Approval: return approvalSprite;
            case PortraitExpression.Concern:  return concernSprite;
            case PortraitExpression.Serious:  return seriousSprite;
            case PortraitExpression.Combat:   return combatSprite;
            default:                          return neutralSprite;
        }
    }

    /// <summary>
    /// Returns the best-fit PortraitExpression for the given OrbState, respecting
    /// this AI's supportsCombat flag (Combat is returned only when true).
    /// </summary>
    public PortraitExpression ExpressionForOrbState(OrbState state)
    {
        switch (state)
        {
            case OrbState.Thinking: return PortraitExpression.Thinking;
            case OrbState.Speaking: return PortraitExpression.Speaking;
            case OrbState.Active:   return PortraitExpression.Neutral;
            case OrbState.Standby:  return PortraitExpression.Serious;
            default:                return PortraitExpression.Neutral;
        }
    }
}
