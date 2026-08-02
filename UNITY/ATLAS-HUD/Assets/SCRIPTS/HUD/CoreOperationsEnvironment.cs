using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Phase 1 – Environment 5: Core Operations (stub)
///
/// The deepest environment in the Atlas HUD. Surfaces server logs,
/// infrastructure diagnostics, backend service panels, and file browser.
///
/// Phase 2 will add: depth-based diagnostic panel stack, service node graph,
/// restrained Bloom and Depth of Field, editable module cards, and log streams.
///
/// Usage: call CoreOperationsEnvironment.Create(canvasTransform) once from ATLASMANAGER.
/// </summary>
public class CoreOperationsEnvironment : AtlasEnvironmentBase
{
    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>Creates the Core Operations environment under the HUD canvas root.</summary>
    public static CoreOperationsEnvironment Create(Transform canvasRoot)
    {
        var go = new GameObject("CoreOperationsEnvironment");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        var env = go.AddComponent<CoreOperationsEnvironment>();
        env.BuildUI();
        return env;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI()
    {
        var root = GetComponent<RectTransform>();
        AtlasUIFactory.CreateBackground("DeepBG", root,
            new Color(0.01f, 0.02f, 0.04f, 1f));

        BuildHeaderBar(root);
        BuildOperationsArea(root);
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
            label: "◀   ARCHIVE",
            fontSize: 12,
            bgColor:   new Color(0f, 0.25f, 0.50f, 0.70f),
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToResearchArchive());

        AtlasUIFactory.CreateLabel("Lbl_Title", content,
            "CORE  OPERATIONS",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(420, 0),
            fontSize: 20, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleCenter);

        AtlasUIFactory.CreateLabel("Lbl_Tag", content,
            "BACKEND  SYSTEMS  ACTIVE",
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-16, 0), size: new Vector2(260, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleRight);
    }

    private void BuildOperationsArea(RectTransform root)
    {
        var area = AtlasUIFactory.CreateStretchRect("OpsArea", root,
            new Vector2(0.04f, 0.11f), new Vector2(0.96f, 0.87f),
            Vector2.zero, Vector2.zero);

        var content = HolographicPanel.BuildPanelLayers(area);

        AtlasUIFactory.CreateLabel("Lbl_Phase", content,
            "CORE  OPERATIONS  —  PHASE 2  CONTENT  PENDING",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(600, 36),
            fontSize: 13, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleCenter);

        AtlasUIFactory.CreateLabel("Lbl_Desc", content,
            "Diagnostic stack  •  Service nodes  •  Backend logs  •  Editable modules",
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
            "ENV_05  ::  CORE_OPERATIONS  ::  DEPTH_4",
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(18, 0), size: new Vector2(520, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleLeft);
    }
}
