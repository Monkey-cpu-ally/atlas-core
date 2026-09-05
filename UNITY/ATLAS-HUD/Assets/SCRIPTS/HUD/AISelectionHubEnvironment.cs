using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Phase 1 – Environment 2: AI Selection Hub
///
/// A grid of six AI specialist cards arranged in two rows of three.
/// Includes:
///   • Full-screen background
///   • Top header bar  (hub title, back-navigation button)
///   • 2×3 specialist card grid built from AISpecialistCard.Create()
///   • Bottom status bar
///
/// Usage: call AISelectionHubEnvironment.Create(canvasTransform) once from ATLASMANAGER.
/// </summary>
public class AISelectionHubEnvironment : AtlasEnvironmentBase
{
    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>Creates the AI Selection Hub environment under the HUD canvas root.</summary>
    public static AISelectionHubEnvironment Create(Transform canvasRoot)
    {
        var go = new GameObject("AISelectionHubEnvironment");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        var env = go.AddComponent<AISelectionHubEnvironment>();
        env.BuildUI();
        return env;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI()
    {
        var root = GetComponent<RectTransform>();

        // Full-screen background — replaced by star-field shader via AtlasBackgroundFX.
        var bgRT  = AtlasUIFactory.CreateFullStretch("DeepBG", root);
        var bgImg = bgRT.gameObject.AddComponent<Image>();
        bgImg.color = new Color(0.01f, 0.03f, 0.09f, 1f);

        BuildHeaderBar(root);
        BuildCardGrid(root);
        BuildFooterBar(root);

        // Slightly cooler tint than AtlasFace to visually distinguish environments.
        AtlasBackgroundFX.Attach(root, new Color(0.85f, 0.90f, 1.00f, 1f));
    }

    // ── Header bar ────────────────────────────────────────────────────────────

    private void BuildHeaderBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("HeaderBar", root,
            new Vector2(0f, 0.885f), Vector2.one,
            new Vector2(20, 0), new Vector2(-20, -6));

        var content = HolographicPanel.BuildPanelLayers(bar);

        // Left: back button
        AtlasUIFactory.CreateButton("Btn_Back", content,
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(14, 0), size: new Vector2(180, 34),
            label: "◀   ATLAS FACE",
            fontSize: 12,
            bgColor:   new Color(0f, 0.25f, 0.50f, 0.70f),
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToAtlasFace());

        // Centre: hub title
        AtlasUIFactory.CreateLabel("Lbl_Title", content,
            "AI  SELECTION  HUB",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(420, 0),
            fontSize: 20, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleCenter);

        // Right: tag
        AtlasUIFactory.CreateLabel("Lbl_Tag", content,
            "SELECT  A  SPECIALIST",
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-16, 0), size: new Vector2(260, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleRight);
    }

    // ── 2×3 Specialist card grid ──────────────────────────────────────────────

    private void BuildCardGrid(RectTransform root)
    {
        var gridArea = AtlasUIFactory.CreateStretchRect("CardGrid", root,
            new Vector2(0.04f, 0.11f), new Vector2(0.96f, 0.87f),
            Vector2.zero, Vector2.zero);

        // Use a GridLayoutGroup to auto-arrange the six cards
        var grid                 = gridArea.gameObject.AddComponent<GridLayoutGroup>();
        grid.cellSize            = new Vector2(260, 160);
        grid.spacing             = new Vector2(28, 28);
        grid.startAxis           = GridLayoutGroup.Axis.Horizontal;
        grid.startCorner         = GridLayoutGroup.Corner.UpperLeft;
        grid.childAlignment      = TextAnchor.MiddleCenter;
        grid.constraint          = GridLayoutGroup.Constraint.FixedColumnCount;
        grid.constraintCount     = 3;

        foreach (var specialist in AISpecialistCard.Specialists)
            AISpecialistCard.Create(gridArea, specialist,
                s => ATLASMANAGER.Instance.NavigateToSpecialistWorkspace(s));
    }

    // ── Footer bar ────────────────────────────────────────────────────────────

    private void BuildFooterBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("FooterBar", root,
            Vector2.zero, new Vector2(1f, 0.082f),
            new Vector2(20, 6), new Vector2(-20, 0));

        var content = HolographicPanel.BuildPanelLayers(bar);

        AtlasUIFactory.CreateLabel("Lbl_EnvTag", content,
            "ENV_02  ::  AI_SELECTION_HUB  ::  DEPTH_1",
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(18, 0), size: new Vector2(520, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleLeft);

        AtlasUIFactory.CreateLabel("Lbl_Hint", content,
            "CLICK A SPECIALIST CARD TO ENTER WORKSPACE",
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-16, 0), size: new Vector2(400, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleRight);
    }
}
