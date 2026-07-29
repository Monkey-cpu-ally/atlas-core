using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Reusable holographic specialist card used inside the AI Selection Hub.
///
/// Each card shows:
///   • Name, specialty, and status badge
///   • A coloured accent stripe keyed to the specialist's domain
///   • Idle shimmer animation when active
///
/// Usage: AISpecialistCard.Create(parent, data)
/// </summary>
public class AISpecialistCard : MonoBehaviour
{
    // ── Data model ────────────────────────────────────────────────────────────

    public struct CardData
    {
        public string Name;
        public string Specialty;
        public string StatusText;
        public Color  AccentColor;
        public string GlyphChar;
    }

    // ── Preset specialists ─────────────────────────────────────────────────────

    public static readonly CardData[] Specialists =
    {
        new CardData { Name = "ATLAS PRIME",  Specialty = "General Intelligence",  StatusText = "ACTIVE",   AccentColor = new Color(0.00f, 0.80f, 1.00f), GlyphChar = "◈" },
        new CardData { Name = "NEXUS",        Specialty = "Deep Research",          StatusText = "ACTIVE",   AccentColor = new Color(0.60f, 0.20f, 1.00f), GlyphChar = "⬡" },
        new CardData { Name = "CIPHER",       Specialty = "Code & Engineering",     StatusText = "ACTIVE",   AccentColor = new Color(0.10f, 1.00f, 0.50f), GlyphChar = "⟨/⟩" },
        new CardData { Name = "SAGE",         Specialty = "Knowledge Base",         StatusText = "ACTIVE",   AccentColor = new Color(1.00f, 0.75f, 0.00f), GlyphChar = "⊕" },
        new CardData { Name = "ECHO",         Specialty = "Creative AI",            StatusText = "STANDBY",  AccentColor = new Color(1.00f, 0.30f, 0.60f), GlyphChar = "♦" },
        new CardData { Name = "FORGE",        Specialty = "System Engineering",     StatusText = "STANDBY",  AccentColor = new Color(0.90f, 0.50f, 0.00f), GlyphChar = "⚙" },
    };

    // ── Instance fields ────────────────────────────────────────────────────────

    private CardData data;
    private Image    accentBar;
    private Image    glowBorder;
    private float    shimmerPhase;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>Creates a card under <paramref name="parent"/> at its natural size.</summary>
    public static AISpecialistCard Create(Transform parent, CardData cardData)
    {
        var go = new GameObject($"Card_{cardData.Name}");
        go.transform.SetParent(parent, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.sizeDelta = new Vector2(260, 160);

        var card   = go.AddComponent<AISpecialistCard>();
        card.data  = cardData;
        card.BuildUI(rt);
        return card;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI(RectTransform root)
    {
        var content = HolographicPanel.BuildPanelLayers(root);

        // Coloured accent stripe at the top of the card
        var stripeRT = AtlasUIFactory.CreateStretchRect("AccentStripe", content,
            new Vector2(0, 0.88f), new Vector2(1, 1f),
            Vector2.zero, Vector2.zero);
        accentBar       = stripeRT.gameObject.AddComponent<Image>();
        accentBar.color = new Color(data.AccentColor.r, data.AccentColor.g, data.AccentColor.b, 0.55f);

        // Glyph / icon
        AtlasUIFactory.CreateLabel("Glyph", content,
            data.GlyphChar,
            anchor: new Vector2(0.18f, 0.62f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(48, 48),
            fontSize: 26, color: data.AccentColor,
            alignment: TextAnchor.MiddleCenter);

        // Specialist name
        AtlasUIFactory.CreateLabel("Lbl_Name", content,
            data.Name,
            anchor: new Vector2(0.5f, 0.60f), pivot: new Vector2(0.5f, 0.5f),
            position: new Vector2(14, 0), size: new Vector2(210, 28),
            fontSize: 14, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleLeft);

        // Specialty sub-label
        AtlasUIFactory.CreateLabel("Lbl_Specialty", content,
            data.Specialty,
            anchor: new Vector2(0.5f, 0.44f), pivot: new Vector2(0.5f, 0.5f),
            position: new Vector2(14, 0), size: new Vector2(210, 20),
            fontSize: 10, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleLeft);

        // Thin divider
        AtlasUIFactory.CreateHorizontalDivider("Div", content,
            yAnchor: 0.32f, xPadding: 10f, HolographicPanel.BorderCyan);

        // Status badge
        bool online     = data.StatusText == "ACTIVE";
        var  badgeColor = online ? Color.green : new Color(1f, 0.6f, 0f);

        AtlasUIFactory.CreateLabel("Lbl_Status", content,
            $"● {data.StatusText}",
            anchor: new Vector2(0.5f, 0.18f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(200, 20),
            fontSize: 11, color: badgeColor,
            alignment: TextAnchor.MiddleCenter);
    }

    // ── Shimmer animation ─────────────────────────────────────────────────────

    private void Update()
    {
        if (accentBar == null) return;
        shimmerPhase += Time.deltaTime * 1.5f;
        float a = 0.40f + Mathf.Sin(shimmerPhase) * 0.18f;
        Color c = accentBar.color;
        c.a     = a;
        accentBar.color = c;
    }
}
