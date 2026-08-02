using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// AI Portrait Panel — holographic identity display in the left column of the
/// Atlas Face environment (x: 0–0.20, y: 0.12–0.90).
///
/// Displays:
///   • Holographic portrait frame with corner accent marks and cross-hair
///   • Ambient glow fill that pulses independently
///   • AI display name and role subtitle
///   • Live status indicator (colour-keyed to OrbState)
///
/// Usage: AIPortraitPanel.Create(environmentRectTransform, optionalPersonalityData)
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class AIPortraitPanel : MonoBehaviour
{
    // ── References ────────────────────────────────────────────────────────────

    private Image     accentStripe;
    private Image     frameGlow;
    private Image     portraitCore;
    private Image     statusDot;
    private Text      lblName;
    private Text      lblRole;
    private Text      lblStateTag;
    private Coroutine frameGlowRoutine;

    private Color _primaryColor = HolographicPanel.BorderCyan;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Builds the portrait panel as a child of <paramref name="envRoot"/>,
    /// anchored to the left column of the environment's rect.
    /// </summary>
    public static AIPortraitPanel Create(Transform envRoot, AIPersonalityData data = null)
    {
        var go = new GameObject("AIPortraitPanel");
        go.transform.SetParent(envRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = new Vector2(0.00f, 0.12f);
        rt.anchorMax = new Vector2(0.20f, 0.90f);
        rt.offsetMin = new Vector2(12, 4);
        rt.offsetMax = new Vector2(-4, -4);

        var panel = go.AddComponent<AIPortraitPanel>();
        panel.BuildUI(rt);

        if (data != null)
            panel.SetAIIdentity(data);

        return panel;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI(RectTransform root)
    {
        var content = HolographicPanel.BuildPanelLayers(root);

        // ── Accent stripe (top 6%) ────────────────────────────────────────────
        var stripeRT = AtlasUIFactory.CreateStretchRect("AccentStripe", content,
            new Vector2(0f, 0.94f), Vector2.one, Vector2.zero, Vector2.zero);
        accentStripe       = stripeRT.gameObject.AddComponent<Image>();
        accentStripe.color = new Color(_primaryColor.r, _primaryColor.g, _primaryColor.b, 0.50f);

        // ── Portrait frame (38–92% of height) ────────────────────────────────
        var frameRT = AtlasUIFactory.CreateStretchRect("PortraitFrame", content,
            new Vector2(0.06f, 0.38f), new Vector2(0.94f, 0.92f),
            Vector2.zero, Vector2.zero);
        var frameBG   = frameRT.gameObject.AddComponent<Image>();
        frameBG.color = new Color(0f, 0.05f, 0.15f, 0.80f);

        // Corner marks
        BuildCornerMark(frameRT, top: true,  left: true);
        BuildCornerMark(frameRT, top: true,  left: false);
        BuildCornerMark(frameRT, top: false, left: true);
        BuildCornerMark(frameRT, top: false, left: false);

        // Glow halo
        var glowRT  = AtlasUIFactory.CreateStretchRect("PortraitGlow", frameRT,
            new Vector2(0.15f, 0.10f), new Vector2(0.85f, 0.90f),
            Vector2.zero, Vector2.zero);
        frameGlow       = glowRT.gameObject.AddComponent<Image>();
        frameGlow.color = new Color(_primaryColor.r, _primaryColor.g, _primaryColor.b, 0.12f);

        // Portrait core — uses procedural placeholder graphic
        var coreRT   = AtlasUIFactory.CreateStretchRect("PortraitCore", frameRT,
            new Vector2(0.12f, 0.08f), new Vector2(0.88f, 0.92f),
            Vector2.zero, Vector2.zero);
        portraitCore = coreRT.gameObject.AddComponent<Image>();
        if (AtlasVisualAssets.PortraitSprite != null)
        {
            portraitCore.sprite = AtlasVisualAssets.PortraitSprite;
            portraitCore.type   = Image.Type.Simple;
            portraitCore.color  = new Color(_primaryColor.r, _primaryColor.g, _primaryColor.b, 0.75f);
        }
        else
        {
            portraitCore.color = new Color(_primaryColor.r, _primaryColor.g, _primaryColor.b, 0.22f);
        }

        BuildCrossHair(frameRT);

        // ── Name label (30–37%) ───────────────────────────────────────────────
        var nameRT = AtlasUIFactory.CreateStretchRect("Lbl_Name", content,
            new Vector2(0f, 0.30f), new Vector2(1f, 0.37f),
            new Vector2(4, 0), new Vector2(-4, 0));
        lblName           = nameRT.gameObject.AddComponent<Text>();
        lblName.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        lblName.text      = "ATLAS";
        lblName.fontSize  = 14;
        lblName.color     = HolographicPanel.TextAccent;
        lblName.alignment = TextAnchor.MiddleCenter;

        // ── Role label (23–30%) ───────────────────────────────────────────────
        var roleRT = AtlasUIFactory.CreateStretchRect("Lbl_Role", content,
            new Vector2(0f, 0.23f), new Vector2(1f, 0.30f),
            new Vector2(4, 0), new Vector2(-4, 0));
        lblRole           = roleRT.gameObject.AddComponent<Text>();
        lblRole.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        lblRole.text      = "Core Intelligence";
        lblRole.fontSize  = 8;
        lblRole.color     = HolographicPanel.TextPrimary;
        lblRole.alignment = TextAnchor.MiddleCenter;

        AtlasUIFactory.CreateHorizontalDivider("Divider", content,
            yAnchor: 0.22f, xPadding: 8f, HolographicPanel.BorderCyan);

        // ── Status dot (14–20%) ───────────────────────────────────────────────
        var dotRT     = AtlasUIFactory.CreateStretchRect("StatusDot", content,
            new Vector2(0.06f, 0.14f), new Vector2(0.20f, 0.20f),
            Vector2.zero, Vector2.zero);
        statusDot       = dotRT.gameObject.AddComponent<Image>();
        statusDot.color = new Color(0f, 1f, 0.3f, 1f);

        // ── State tag (14–20%) ────────────────────────────────────────────────
        var stateRT   = AtlasUIFactory.CreateStretchRect("Lbl_State", content,
            new Vector2(0.24f, 0.14f), new Vector2(1f, 0.20f),
            Vector2.zero, Vector2.zero);
        lblStateTag           = stateRT.gameObject.AddComponent<Text>();
        lblStateTag.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        lblStateTag.text      = "ACTIVE";
        lblStateTag.fontSize  = 8;
        lblStateTag.color     = new Color(0f, 1f, 0.3f, 1f);
        lblStateTag.alignment = TextAnchor.MiddleLeft;

        // ── Footer tag (1–8%) ─────────────────────────────────────────────────
        var tagRT   = AtlasUIFactory.CreateStretchRect("Lbl_Tag", content,
            new Vector2(0f, 0.01f), new Vector2(1f, 0.08f),
            new Vector2(4, 0), new Vector2(-4, 0));
        var tagLbl  = tagRT.gameObject.AddComponent<Text>();
        tagLbl.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        tagLbl.text      = "IDENTITY PANEL";
        tagLbl.fontSize  = 7;
        tagLbl.color     = HolographicPanel.TextMuted;
        tagLbl.alignment = TextAnchor.MiddleCenter;

        frameGlowRoutine = StartCoroutine(FrameGlowRoutine());
    }

    // ── Geometric helpers ─────────────────────────────────────────────────────

    private void BuildCornerMark(RectTransform parent, bool top, bool left)
    {
        float hXMin = left  ? 0f    : 0.82f;
        float hXMax = left  ? 0.18f : 1.00f;
        float hYMin = top   ? 0.95f : 0.00f;
        float hYMax = top   ? 1.00f : 0.05f;

        float vXMin = left  ? 0.00f : 0.95f;
        float vXMax = left  ? 0.05f : 1.00f;
        float vYMin = top   ? 0.82f : 0.00f;
        float vYMax = top   ? 1.00f : 0.18f;

        string tag = (top ? "T" : "B") + (left ? "L" : "R");

        var hRT = AtlasUIFactory.CreateStretchRect("Corner_" + tag + "_H", parent,
            new Vector2(hXMin, hYMin), new Vector2(hXMax, hYMax),
            Vector2.zero, Vector2.zero);
        hRT.gameObject.AddComponent<Image>().color = _primaryColor;

        var vRT = AtlasUIFactory.CreateStretchRect("Corner_" + tag + "_V", parent,
            new Vector2(vXMin, vYMin), new Vector2(vXMax, vYMax),
            Vector2.zero, Vector2.zero);
        vRT.gameObject.AddComponent<Image>().color = _primaryColor;
    }

    private void BuildCrossHair(RectTransform parent)
    {
        Color dim = new Color(_primaryColor.r, _primaryColor.g, _primaryColor.b, 0.16f);

        var h = AtlasUIFactory.CreateStretchRect("CrossH", parent,
            new Vector2(0f, 0.49f), new Vector2(1f, 0.51f),
            new Vector2(8, 0), new Vector2(-8, 0));
        h.gameObject.AddComponent<Image>().color = dim;

        var v = AtlasUIFactory.CreateStretchRect("CrossV", parent,
            new Vector2(0.49f, 0f), new Vector2(0.51f, 1f),
            new Vector2(0, 8), new Vector2(0, -8));
        v.gameObject.AddComponent<Image>().color = dim;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>Applies an AI personality's colours and labels to the panel.</summary>
    public void SetAIIdentity(AIPersonalityData data)
    {
        if (data == null) return;

        _primaryColor = data.primaryColor;

        if (accentStripe  != null) accentStripe.color  = new Color(data.primaryColor.r, data.primaryColor.g, data.primaryColor.b, 0.50f);
        if (portraitCore  != null) portraitCore.color  = new Color(data.primaryColor.r, data.primaryColor.g, data.primaryColor.b, 0.22f);
        if (frameGlow     != null) frameGlow.color     = new Color(data.primaryColor.r, data.primaryColor.g, data.primaryColor.b, 0.12f);
        if (lblName       != null) lblName.text        = data.displayName != null ? data.displayName.ToUpper() : "ATLAS";
        if (lblRole       != null) lblRole.text        = data.role;
    }

    /// <summary>Updates the status indicator to reflect the current orb state.</summary>
    public void SetOrbState(OrbState state)
    {
        Color stateColor;
        string stateText;

        switch (state)
        {
            case OrbState.Active:
                stateColor = new Color(0f, 1f, 0.3f, 1f);
                stateText  = "ACTIVE";
                break;
            case OrbState.Thinking:
                stateColor = new Color(1f, 0.8f, 0f, 1f);
                stateText  = "THINKING";
                break;
            case OrbState.Speaking:
                stateColor = new Color(0f, 1f, 1f, 1f);
                stateText  = "SPEAKING";
                break;
            default:
                stateColor = new Color(0.4f, 0.6f, 0.8f, 1f);
                stateText  = "STANDBY";
                break;
        }

        if (statusDot   != null) statusDot.color   = stateColor;
        if (lblStateTag != null)
        {
            lblStateTag.color = stateColor;
            lblStateTag.text  = stateText;
        }
    }

    // ── Glow animation ────────────────────────────────────────────────────────

    private IEnumerator FrameGlowRoutine()
    {
        float phase = Random.Range(0f, Mathf.PI * 2f);
        while (true)
        {
            phase += Time.deltaTime * 0.9f;
            float alpha = Mathf.Lerp(0.06f, 0.28f, (Mathf.Sin(phase) + 1f) * 0.5f);
            if (frameGlow != null)
            {
                Color c = frameGlow.color;
                c.a = alpha;
                frameGlow.color = c;
            }
            yield return null;
        }
    }
}
