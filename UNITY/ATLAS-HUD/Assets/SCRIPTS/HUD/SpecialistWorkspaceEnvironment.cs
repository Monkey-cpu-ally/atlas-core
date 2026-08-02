using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Phase 1 – Environment 3: Specialist Workspace (stub)
///
/// Entered when the user selects a specialist card in the AI Selection Hub.
/// In Phase 1 this is a functional stub that displays the active specialist's
/// name and specialty alongside placeholder content panels.
///
/// Phase 2 will add: specialty wheel, AI-specific graffiti/heavy-ink artwork,
/// staged subject entrance animations, and the AI workspace studio.
///
/// Usage: call SpecialistWorkspaceEnvironment.Create(canvasTransform) once from ATLASMANAGER.
///        Then call LoadSpecialist(cardData) to populate before navigating here.
/// </summary>
public class SpecialistWorkspaceEnvironment : AtlasEnvironmentBase
{
    // ── Dynamic label references ──────────────────────────────────────────────
    private Text lblSpecialistName;
    private Text lblSpecialty;
    private Image accentStripe;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>Creates the Specialist Workspace environment under the HUD canvas root.</summary>
    public static SpecialistWorkspaceEnvironment Create(Transform canvasRoot)
    {
        var go = new GameObject("SpecialistWorkspaceEnvironment");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        var env = go.AddComponent<SpecialistWorkspaceEnvironment>();
        env.BuildUI();
        return env;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>
    /// Populates the workspace with the specialist that was just selected.
    /// Safe to call before or after the environment becomes visible.
    /// </summary>
    public void LoadSpecialist(AISpecialistCard.CardData data)
    {
        if (lblSpecialistName != null) lblSpecialistName.text = data.Name;
        if (lblSpecialty      != null) lblSpecialty.text      = data.Specialty;
        if (accentStripe      != null)
            accentStripe.color = new Color(data.AccentColor.r,
                                           data.AccentColor.g,
                                           data.AccentColor.b, 0.55f);
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI()
    {
        var root = GetComponent<RectTransform>();
        AtlasUIFactory.CreateBackground("DeepBG", root,
            new Color(0.01f, 0.04f, 0.06f, 1f));

        BuildHeaderBar(root);
        BuildWorkspaceArea(root);
        BuildFooterBar(root);
    }

    private void BuildHeaderBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("HeaderBar", root,
            new Vector2(0f, 0.885f), Vector2.one,
            new Vector2(20, 0), new Vector2(-20, -6));

        // Accent stripe (tinted to active specialist colour by LoadSpecialist)
        var stripeRT = AtlasUIFactory.CreateFullStretch("AccentStripe", bar);
        accentStripe       = stripeRT.gameObject.AddComponent<Image>();
        accentStripe.color = new Color(0f, 0.6f, 1f, 0.15f);

        var content = HolographicPanel.BuildPanelLayers(bar);

        // Back button
        AtlasUIFactory.CreateButton("Btn_Back", content,
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(14, 0), size: new Vector2(180, 34),
            label: "◀   AI HUB",
            fontSize: 12,
            bgColor:   new Color(0f, 0.25f, 0.50f, 0.70f),
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToAIHub());

        // Specialist name (populated by LoadSpecialist)
        lblSpecialistName = AtlasUIFactory.CreateLabel("Lbl_Specialist", content,
            "—",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(420, 0),
            fontSize: 20, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleCenter);

        // Forward button
        AtlasUIFactory.CreateButton("Btn_Archive", content,
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-14, 0), size: new Vector2(200, 34),
            label: "ARCHIVE  ▶",
            fontSize: 12,
            bgColor:   HolographicPanel.ButtonFill,
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToResearchArchive());
    }

    private void BuildWorkspaceArea(RectTransform root)
    {
        var area = AtlasUIFactory.CreateStretchRect("WorkspaceArea", root,
            new Vector2(0.04f, 0.11f), new Vector2(0.96f, 0.87f),
            Vector2.zero, Vector2.zero);

        var content = HolographicPanel.BuildPanelLayers(area);

        AtlasUIFactory.CreateLabel("Lbl_Phase", content,
            "SPECIALIST  WORKSPACE  —  PHASE 2  CONTENT  PENDING",
            anchor: new Vector2(0.5f, 0.7f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(600, 36),
            fontSize: 13, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleCenter);

        lblSpecialty = AtlasUIFactory.CreateLabel("Lbl_Specialty", content,
            "—",
            anchor: new Vector2(0.5f, 0.58f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(500, 28),
            fontSize: 16, color: HolographicPanel.TextPrimary,
            alignment: TextAnchor.MiddleCenter);
    }

    private void BuildFooterBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("FooterBar", root,
            Vector2.zero, new Vector2(1f, 0.082f),
            new Vector2(20, 6), new Vector2(-20, 0));

        var content = HolographicPanel.BuildPanelLayers(bar);

        AtlasUIFactory.CreateLabel("Lbl_EnvTag", content,
            "ENV_03  ::  SPECIALIST_WORKSPACE  ::  DEPTH_2",
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(18, 0), size: new Vector2(560, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleLeft);
    }
}
