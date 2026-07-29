using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Phase 1 – Environment 1: Atlas Face
///
/// The default landing environment. Displays:
///   • Full-screen deep-space background
///   • Top status bar  (title, version, system-status indicator)
///   • Central identity panel (animated hexagonal emblem, name, readout lines)
///   • Bottom navigation bar  (environment label + "Enter AI Hub" button)
///
/// Usage: call AtlasFaceEnvironment.Create(canvasTransform) once from ATLASMANAGER.
/// </summary>
public class AtlasFaceEnvironment : AtlasEnvironmentBase
{
    // ── Animated elements ─────────────────────────────────────────────────────
    private Image  statusDot;
    private Image  emblemRing;
    private float  ringPhase;
    private Coroutine statusPulseRoutine;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>Creates the Atlas Face environment under the HUD canvas root.</summary>
    public static AtlasFaceEnvironment Create(Transform canvasRoot)
    {
        var go = new GameObject("AtlasFaceEnvironment");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        var env = go.AddComponent<AtlasFaceEnvironment>();
        env.BuildUI();
        return env;
    }

    // ── UI Construction ───────────────────────────────────────────────────────

    private void BuildUI()
    {
        var root = GetComponent<RectTransform>();

        // Full-screen deep background
        AtlasUIFactory.CreateBackground("DeepBG", root, HolographicPanel.DeepBackground);

        BuildTopBar(root);
        BuildCenterPanel(root);
        BuildBottomBar(root);
    }

    // ── Top bar ───────────────────────────────────────────────────────────────

    private void BuildTopBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("TopBar", root,
            new Vector2(0f, 0.925f), Vector2.one,
            new Vector2(20, 0), new Vector2(-20, -6));

        var content = HolographicPanel.BuildPanelLayers(bar);

        // Left: brand
        AtlasUIFactory.CreateLabel("Lbl_Brand", content,
            "ATLAS  |  CORE INTERFACE",
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(18, 0), size: new Vector2(420, 0),
            fontSize: 16, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleLeft);

        // Centre: version tag
        AtlasUIFactory.CreateLabel("Lbl_Version", content,
            "v6.0  —  HOLOGRAPHIC HUD",
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(300, 0),
            fontSize: 12, color: HolographicPanel.TextPrimary,
            alignment: TextAnchor.MiddleCenter);

        // Right: status indicator
        statusDot = AtlasUIFactory.CreateElement(
            "StatusDot", content,
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-16, 0), size: new Vector2(12, 12))
            .gameObject.AddComponent<Image>();
        statusDot.color = Color.green;

        AtlasUIFactory.CreateLabel("Lbl_Status", content,
            "ALL SYSTEMS ONLINE",
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-36, 0), size: new Vector2(180, 0),
            fontSize: 11, color: Color.green,
            alignment: TextAnchor.MiddleRight);
    }

    // ── Central identity panel ────────────────────────────────────────────────

    private void BuildCenterPanel(RectTransform root)
    {
        var panel = AtlasUIFactory.CreateStretchRect("IdentityPanel", root,
            new Vector2(0.22f, 0.12f), new Vector2(0.78f, 0.90f),
            Vector2.zero, new Vector2(0, -52));

        var content = HolographicPanel.BuildPanelLayers(panel);

        // ── Emblem ring (animated) ────────────────────────────────────────────
        var ringContainer = AtlasUIFactory.CreateElement(
            "EmblemContainer", content,
            anchor: new Vector2(0.5f, 0.74f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(160, 160));

        // Pulsing outer ring
        var ringRT  = AtlasUIFactory.CreateElement(
            "Ring", ringContainer,
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(150, 150));
        emblemRing  = ringRT.gameObject.AddComponent<Image>();
        emblemRing.color = new Color(0f, 0.80f, 1f, 0.45f);

        // Inner filled circle (emblem background)
        var innerRT = AtlasUIFactory.CreateElement(
            "EmblemBG", ringContainer,
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(118, 118));
        var innerImg = innerRT.gameObject.AddComponent<Image>();
        innerImg.color = new Color(0f, 0.28f, 0.58f, 0.85f);

        // Glyph: hexagonal lattice symbol
        var glyphRT  = AtlasUIFactory.CreateElement(
            "Glyph", ringContainer,
            anchor: new Vector2(0.5f, 0.5f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(110, 110));
        var glyph    = glyphRT.gameObject.AddComponent<Text>();
        glyph.text   = "⬡";
        glyph.fontSize     = 58;
        glyph.color        = HolographicPanel.TextAccent;
        glyph.alignment    = TextAnchor.MiddleCenter;

        // ── Name & subtitle ───────────────────────────────────────────────────
        AtlasUIFactory.CreateLabel("Lbl_Name", content,
            "ATLAS",
            anchor: new Vector2(0.5f, 0.55f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(300, 42),
            fontSize: 32, color: HolographicPanel.TextAccent,
            alignment: TextAnchor.MiddleCenter);

        AtlasUIFactory.CreateLabel("Lbl_Subtitle", content,
            "ADVANCED TACTICAL & LEARNING ASSISTANT SYSTEM",
            anchor: new Vector2(0.5f, 0.49f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(440, 22),
            fontSize: 10, color: HolographicPanel.TextPrimary,
            alignment: TextAnchor.MiddleCenter);

        // ── Divider ───────────────────────────────────────────────────────────
        AtlasUIFactory.CreateHorizontalDivider("Divider", content,
            yAnchor: 0.44f, xPadding: 30f, HolographicPanel.BorderCyan);

        // ── Status readout lines ──────────────────────────────────────────────
        string[] readout =
        {
            "MODE        :  STANDBY",
            "MEMORY      :  98.2%  NOMINAL",
            "NEURAL CORE :  ACTIVE",
            "UPLINK      :  SECURE  [256-BIT]",
        };

        for (int i = 0; i < readout.Length; i++)
        {
            float yAnchor = 0.38f - i * 0.065f;
            AtlasUIFactory.CreateLabel($"Readout_{i}", content,
                readout[i],
                anchor: new Vector2(0.5f, yAnchor), pivot: new Vector2(0.5f, 0.5f),
                position: new Vector2(10, 0), size: new Vector2(360, 22),
                fontSize: 11, color: HolographicPanel.TextPrimary,
                alignment: TextAnchor.MiddleLeft);
        }
    }

    // ── Bottom navigation bar ─────────────────────────────────────────────────

    private void BuildBottomBar(RectTransform root)
    {
        var bar = AtlasUIFactory.CreateStretchRect("BottomBar", root,
            Vector2.zero, new Vector2(1f, 0.085f),
            new Vector2(20, 6), new Vector2(-20, 0));

        var content = HolographicPanel.BuildPanelLayers(bar);

        // Left: environment label
        AtlasUIFactory.CreateLabel("Lbl_EnvTag", content,
            "ENV_01  ::  ATLAS_FACE  ::  DEPTH_0",
            anchor: new Vector2(0f, 0.5f), pivot: new Vector2(0f, 0.5f),
            position: new Vector2(18, 0), size: new Vector2(460, 0),
            fontSize: 11, color: HolographicPanel.TextMuted,
            alignment: TextAnchor.MiddleLeft);

        // Right: navigate to AI Hub
        AtlasUIFactory.CreateButton("Btn_AIHub", content,
            anchor: new Vector2(1f, 0.5f), pivot: new Vector2(1f, 0.5f),
            position: new Vector2(-18, 0), size: new Vector2(244, 34),
            label: "▶   ENTER AI SELECTION HUB",
            fontSize: 12,
            bgColor:   HolographicPanel.ButtonFill,
            textColor: HolographicPanel.TextAccent,
            onClick: () => ATLASMANAGER.Instance.NavigateToAIHub());
    }

    // ── Animations ────────────────────────────────────────────────────────────

    protected override void OnShown()
    {
        if (statusPulseRoutine != null) StopCoroutine(statusPulseRoutine);
        statusPulseRoutine = StartCoroutine(PulseStatusDot());
    }

    protected override void OnHidden()
    {
        if (statusPulseRoutine != null)
        {
            StopCoroutine(statusPulseRoutine);
            statusPulseRoutine = null;
        }
    }

    private void Update()
    {
        if (emblemRing == null) return;

        ringPhase += Time.deltaTime * 0.75f;
        float scale = 0.88f + Mathf.Sin(ringPhase) * 0.12f;
        emblemRing.transform.localScale = new Vector3(scale, scale, 1f);

        Color c = emblemRing.color;
        c.a     = 0.30f + Mathf.Sin(ringPhase * 1.4f) * 0.18f;
        emblemRing.color = c;
    }

    private IEnumerator PulseStatusDot()
    {
        while (true)
        {
            if (statusDot != null)
            {
                Color c = statusDot.color;
                c.a     = Mathf.Lerp(0.35f, 1f, Mathf.PingPong(Time.time * 2f, 1f));
                statusDot.color = c;
            }
            yield return null;
        }
    }
}
