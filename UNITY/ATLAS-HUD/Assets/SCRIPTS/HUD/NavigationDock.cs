using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Navigation Dock — persistent bottom strip showing one button per HUD state.
///
/// Positioned at the very bottom of the canvas (y: 0–0.045) and always visible
/// above the environment content. The active environment's button is highlighted
/// with the accent colour; inactive buttons use the muted fill.
///
/// Usage:
///   var dock = NavigationDock.Create(canvasRoot);
///   dock.SetActiveState(AtlasHUDState.AtlasFace);
/// </summary>
public class NavigationDock : MonoBehaviour
{
    // ── Navigation entries ────────────────────────────────────────────────────

    private static readonly string[] DockLabels = { "ATLAS", "AI HUB", "WORKSPACE", "ARCHIVE", "OPS" };

    // ── Internal state ────────────────────────────────────────────────────────

    private Image[] buttonBGs  = new Image[5];
    private Text[]  buttonTxts = new Text[5];

    private AtlasHUDState _activeState = AtlasHUDState.AtlasFace;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Builds the navigation dock as a persistent child of the HUD canvas root.
    /// </summary>
    public static NavigationDock Create(Transform canvasRoot)
    {
        var go = new GameObject("NavigationDock");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = new Vector2(0f,  0f);
        rt.anchorMax = new Vector2(1f,  0.045f);
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        var dock = go.AddComponent<NavigationDock>();
        dock.BuildDock(rt);
        return dock;
    }

    // ── Construction ──────────────────────────────────────────────────────────

    private void BuildDock(RectTransform root)
    {
        // Background strip
        var bg   = root.gameObject.AddComponent<Image>();
        bg.color = new Color(0.01f, 0.03f, 0.09f, 0.96f);

        // Top border line
        AtlasUIFactory.CreateBorderStrip("TopBorder", root,
            horizontal: true, isTopOrLeft: true, HolographicPanel.BorderCyan);

        int states = System.Enum.GetValues(typeof(AtlasHUDState)).Length;
        float width = 1f / states;

        for (int i = 0; i < states; i++)
        {
            var state = (AtlasHUDState)i;
            int  captured = i;   // closure capture

            float xMin = i * width;
            float xMax = xMin + width;

            // Button cell
            var cellRT = AtlasUIFactory.CreateStretchRect("Nav_" + DockLabels[i], root,
                new Vector2(xMin, 0f), new Vector2(xMax, 1f),
                new Vector2(1, 2), new Vector2(-1, -2));

            var cellBG   = cellRT.gameObject.AddComponent<Image>();
            cellBG.color = Color.clear;
            buttonBGs[i] = cellBG;

            var btn = cellRT.gameObject.AddComponent<Button>();
            btn.targetGraphic = cellBG;

            // Highlight colour on hover
            var colors            = btn.colors;
            colors.normalColor    = Color.clear;
            colors.highlightedColor = new Color(HolographicPanel.BorderCyan.r, HolographicPanel.BorderCyan.g, HolographicPanel.BorderCyan.b, 0.15f);
            colors.pressedColor   = new Color(HolographicPanel.BorderCyan.r, HolographicPanel.BorderCyan.g, HolographicPanel.BorderCyan.b, 0.30f);
            btn.colors = colors;

            btn.onClick.AddListener(() => OnDockButtonClicked(state));

            // Separator line (left edge except first)
            if (i > 0)
            {
                var sepRT = AtlasUIFactory.CreateStretchRect("Sep", root,
                    new Vector2(xMin, 0.1f), new Vector2(xMin, 0.9f),
                    new Vector2(-1, 0), new Vector2(1, 0));
                sepRT.gameObject.AddComponent<Image>().color =
                    new Color(HolographicPanel.BorderCyan.r, HolographicPanel.BorderCyan.g, HolographicPanel.BorderCyan.b, 0.25f);
            }

            // Label text
            var lblRT = AtlasUIFactory.CreateStretchRect("Lbl", cellRT,
                Vector2.zero, Vector2.one,
                Vector2.zero, Vector2.zero);
            var lbl         = lblRT.gameObject.AddComponent<Text>();
            lbl.font        = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            lbl.text        = DockLabels[i];
            lbl.fontSize    = 9;
            lbl.color       = HolographicPanel.TextMuted;
            lbl.alignment   = TextAnchor.MiddleCenter;
            buttonTxts[i]   = lbl;
        }

        // Highlight the default active state
        ApplyActiveHighlight();
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>Updates which button is highlighted as active.</summary>
    public void SetActiveState(AtlasHUDState state)
    {
        _activeState = state;
        ApplyActiveHighlight();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private void ApplyActiveHighlight()
    {
        for (int i = 0; i < buttonBGs.Length; i++)
        {
            bool active = (i == (int)_activeState);

            if (buttonBGs[i] != null)
                buttonBGs[i].color = active
                    ? new Color(HolographicPanel.BorderCyan.r, HolographicPanel.BorderCyan.g, HolographicPanel.BorderCyan.b, 0.18f)
                    : Color.clear;

            if (buttonTxts[i] != null)
                buttonTxts[i].color = active ? HolographicPanel.TextAccent : HolographicPanel.TextMuted;
        }
    }

    private void OnDockButtonClicked(AtlasHUDState state)
    {
        if (ATLASMANAGER.Instance == null) return;

        switch (state)
        {
            case AtlasHUDState.AtlasFace:           ATLASMANAGER.Instance.NavigateToAtlasFace();         break;
            case AtlasHUDState.AISelectionHub:      ATLASMANAGER.Instance.NavigateToAIHub();             break;
            case AtlasHUDState.SpecialistWorkspace: ATLASMANAGER.Instance.NavigateToSpecialistWorkspace(); break;
            case AtlasHUDState.ResearchArchive:     ATLASMANAGER.Instance.NavigateToResearchArchive();   break;
            case AtlasHUDState.CoreOperations:      ATLASMANAGER.Instance.NavigateToCoreOperations();    break;
        }
    }
}
