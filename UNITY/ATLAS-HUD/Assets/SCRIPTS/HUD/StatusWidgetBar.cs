using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Status Widget Bar — narrow horizontal strip showing live system metrics.
///
/// Anchored just above the bottom navigation bar (y: 0.085–0.125) in the
/// Atlas Face environment. Renders four holographic status widgets:
///   • NEURAL CORE  – pulsing activity bar
///   • MEMORY       – filled percentage bar
///   • UPLINK       – signal strength bars
///   • LATENCY      – animated response-time indicator
///
/// Usage: StatusWidgetBar.Create(environmentRectTransform)
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class StatusWidgetBar : MonoBehaviour
{
    // ── Widget count ──────────────────────────────────────────────────────────

    private const int WidgetCount = 4;

    private static readonly string[] WidgetLabels  = { "NEURAL CORE", "MEMORY", "UPLINK", "LATENCY" };
    private static readonly float[]  WidgetValues  = { 0.82f, 0.92f, 0.78f, 0.65f };   // 0–1 initial fills
    private static readonly Color[]  WidgetColors  =
    {
        new Color(0f,    1f,    1f,    1f),   // cyan  – neural
        new Color(0.20f, 0.75f, 1f,    1f),   // blue  – memory
        new Color(0f,    1f,    0.4f,  1f),   // green – uplink
        new Color(1f,    0.80f, 0f,    1f),   // amber – latency
    };

    // ── Internal references ───────────────────────────────────────────────────

    private Image[]     fillBars   = new Image[WidgetCount];
    private Coroutine[] animations = new Coroutine[WidgetCount];

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Builds the status widget bar as a child of <paramref name="envRoot"/>.
    /// </summary>
    public static StatusWidgetBar Create(Transform envRoot)
    {
        var go = new GameObject("StatusWidgetBar");
        go.transform.SetParent(envRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = new Vector2(0f,    0.085f);
        rt.anchorMax = new Vector2(1f,    0.125f);
        rt.offsetMin = new Vector2(20, 3);
        rt.offsetMax = new Vector2(-20, -3);

        var bar = go.AddComponent<StatusWidgetBar>();
        bar.BuildUI(rt);
        return bar;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI(RectTransform root)
    {
        // Subtle background
        var bg   = root.gameObject.AddComponent<Image>();
        bg.color = new Color(0f, 0.04f, 0.12f, 0.70f);

        // Top border
        AtlasUIFactory.CreateBorderStrip("Border_Top", root,
            horizontal: true, isTopOrLeft: true,
            new Color(HolographicPanel.BorderCyan.r, HolographicPanel.BorderCyan.g, HolographicPanel.BorderCyan.b, 0.55f));

        // Four equal-width widget cells
        for (int i = 0; i < WidgetCount; i++)
        {
            float xMin = i       * (1f / WidgetCount);
            float xMax = (i + 1) * (1f / WidgetCount);

            BuildWidget(root, i, xMin, xMax);
        }
    }

    private void BuildWidget(RectTransform root, int index, float xMin, float xMax)
    {
        // Cell container
        var cellRT = AtlasUIFactory.CreateStretchRect("Widget_" + WidgetLabels[index], root,
            new Vector2(xMin, 0f), new Vector2(xMax, 1f),
            new Vector2(2, 2), new Vector2(-2, -2));

        // Vertical separator line (left edge, except first)
        if (index > 0)
        {
            var sep = AtlasUIFactory.CreateStretchRect("Sep", root,
                new Vector2(xMin, 0.1f), new Vector2(xMin, 0.9f),
                new Vector2(-1, 0), new Vector2(1, 0));
            sep.gameObject.AddComponent<Image>().color =
                new Color(HolographicPanel.BorderCyan.r, HolographicPanel.BorderCyan.g, HolographicPanel.BorderCyan.b, 0.25f);
        }

        // Label (left portion of cell)
        var lblRT = AtlasUIFactory.CreateStretchRect("Lbl", cellRT,
            new Vector2(0f, 0f), new Vector2(0.38f, 1f),
            Vector2.zero, Vector2.zero);
        var lbl        = lblRT.gameObject.AddComponent<Text>();
        lbl.font       = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        lbl.text       = WidgetLabels[index];
        lbl.fontSize   = 8;
        lbl.color      = HolographicPanel.TextMuted;
        lbl.alignment  = TextAnchor.MiddleLeft;

        // Bar track background (right portion)
        var trackRT    = AtlasUIFactory.CreateStretchRect("Track", cellRT,
            new Vector2(0.40f, 0.25f), new Vector2(1f, 0.75f),
            Vector2.zero, Vector2.zero);
        var trackBG    = trackRT.gameObject.AddComponent<Image>();
        trackBG.color  = new Color(0f, 0.10f, 0.22f, 0.80f);

        // Fill bar
        var fillRT     = AtlasUIFactory.CreateStretchRect("Fill", trackRT,
            Vector2.zero, new Vector2(WidgetValues[index], 1f),
            Vector2.zero, Vector2.zero);
        var fillImg        = fillRT.gameObject.AddComponent<Image>();
        fillImg.color      = new Color(WidgetColors[index].r, WidgetColors[index].g, WidgetColors[index].b, 0.75f);
        fillBars[index]    = fillImg;

        // Start idle animation
        animations[index] = StartCoroutine(AnimateWidget(index, fillRT));
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>Sets a widget's fill value (0–1) directly.</summary>
    public void SetWidgetValue(int index, float value)
    {
        if (index < 0 || index >= WidgetCount) return;
        if (fillBars[index] == null) return;

        var rt = fillBars[index].GetComponent<RectTransform>();
        rt.anchorMax = new Vector2(Mathf.Clamp01(value), 1f);
    }

    // ── Widget animation ──────────────────────────────────────────────────────

    private IEnumerator AnimateWidget(int index, RectTransform fillRT)
    {
        float baseValue  = WidgetValues[index];
        float phase      = Random.Range(0f, Mathf.PI * 2f);
        float speed      = 0.4f + index * 0.15f;   // slightly different speeds per widget

        while (true)
        {
            phase += Time.deltaTime * speed;
            float noise  = (Mathf.Sin(phase) * 0.05f) + (Mathf.Sin(phase * 2.3f) * 0.02f);
            float value  = Mathf.Clamp01(baseValue + noise);

            if (fillRT != null)
                fillRT.anchorMax = new Vector2(value, 1f);

            yield return null;
        }
    }
}
