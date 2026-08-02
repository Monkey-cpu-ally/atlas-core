using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Phase 1 – Environment 4: Research Archive (stub)
///
/// Accessible from the Specialist Workspace. Presents historical research,
/// Black inventor and scholar records, and project-linked discovery reports
/// along a curved depth track of archive cards.
///
/// Phase 2 will add: world-space card prefabs, spline/Bezier paths,
/// selected-card focus, portrait cards, and subtle idle motion.
///
/// Usage: call ResearchArchiveEnvironment.Create(canvasTransform) once from ATLASMANAGER.
/// </summary>
public class ResearchArchiveEnvironment : AtlasEnvironmentBase
{
    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>Creates the Research Archive environment under the HUD canvas root.</summary>
    public static ResearchArchiveEnvironment Create(Transform canvasRoot)
    {
        var go = new GameObject("ResearchArchiveEnvironment");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        var env = go.AddComponent<ResearchArchiveEnvironment>();
        env.BuildUI();
        return env;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI()
    {
        var root = GetComponent<RectTransform>();
        AtlasUIFactory.CreateBackground("DeepBG", root,
            new Color(0.01f, 0.03f, 0.05f, 1f));

        BuildHeaderBar(root);
        BuildArchiveArea(root);
        BuildFooterBar(root);
    }

    private void BuildHeaderBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("HeaderBar", root,
            new Vector2(0f, 0.885f), Vector2.one,
            new Vector2(20, 0), new Vector2(-20, -6));

        var content = HolographicPanel.BuildPanelLayers(bar);

        AtlasUIFactory.CreateButton("Btn_Back", content,
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(14, 0), size: new Vector2(200, 34),
            label: "◀   WORKSPACE",
            fontSize: 12,
            bgColor:   new Color(0f, 0.25f, 0.50f, 0.70f),
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToSpecialistWorkspace());

        AtlasUIFactory.CreateLabel("Lbl_Title", content,
            "RESEARCH  ARCHIVE",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(420, 0),
            fontSize: 20, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleCenter);

        AtlasUIFactory.CreateButton("Btn_Core", content,
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-14, 0), size: new Vector2(200, 34),
            label: "CORE OPS  ▶",
            fontSize: 12,
            bgColor:   HolographicPanel.ButtonFill,
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToCoreOperations());
    }

    private void BuildArchiveArea(RectTransform root)
    {
        var area = AtlasUIFactory.CreateStretchRect("ArchiveArea", root,
            new Vector2(0.04f, 0.11f), new Vector2(0.96f, 0.87f),
            Vector2.zero, Vector2.zero);

        var content = HolographicPanel.BuildPanelLayers(area);

        AtlasUIFactory.CreateLabel("Lbl_Phase", content,
            "RESEARCH  ARCHIVE  —  PHASE 2  CONTENT  PENDING",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(600, 36),
            fontSize: 13, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleCenter);

        AtlasUIFactory.CreateLabel("Lbl_Desc", content,
            "Curved archive card track  •  Historical Black inventor records  •  Project research",
            anchor: new Vector2(0.5f, 0.42f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(640, 22),
            fontSize: 10, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleCenter);
    }

    private void BuildFooterBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("FooterBar", root,
            Vector2.zero, new Vector2(1f, 0.082f),
            new Vector2(20, 6), new Vector2(-20, 0));

        var content = HolographicPanel.BuildPanelLayers(bar);

        AtlasUIFactory.CreateLabel("Lbl_EnvTag", content,
            "ENV_04  ::  RESEARCH_ARCHIVE  ::  DEPTH_3",
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(18, 0), size: new Vector2(520, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleLeft);
    }
}
