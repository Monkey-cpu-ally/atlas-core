using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Phase 1 – Environment 1: Atlas Face
///
/// The default landing environment. Displays:
///   • Full-screen deep-space background
///   • Top status bar  (title, version, system-status indicator)
///   • Central identity panel (AtlasCoreOrb in orange Atlas identity, name, readout lines)
///   • Bottom navigation bar  (environment label + "Enter AI Hub" button)
///
/// Usage: call AtlasFaceEnvironment.Create(canvasTransform) once from ATLASMANAGER.
/// </summary>
public class AtlasFaceEnvironment : AtlasEnvironmentBase
{
    // ── Animated elements ─────────────────────────────────────────────────────
    private Image          statusDot;
    private AtlasCoreOrb   _coreOrb;
    private AIPortraitPanel _portraitPanel;
    private DialoguePanel  _dialoguePanel;
    private Coroutine      statusPulseRoutine;

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

        // Full-screen deep background — replaced at runtime by AtlasBackgroundFX
        // with the animated star-field DeepSpace shader.
        AtlasUIFactory.CreateBackground("DeepBG", root, HolographicPanel.DeepBackground);

        BuildTopBar(root);
        BuildCenterPanel(root);
        BuildStatusWidgetBar(root);
        BuildBottomBar(root);
        BuildSidePanels(root);

        // Attach animated background effects (star field + grid overlay).
        // Must be called after all environment children are built so the
        // sibling index placement is correct.
        AtlasBackgroundFX.Attach(root, Color.white);
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

        // ── Atlas Core Orb ────────────────────────────────────────────────────
        // The orb is the living centrepiece of the Atlas Face environment.
        // It uses the Atlas orange identity (loaded from Resources/AI/Atlas).
        var orbContainer = AtlasUIFactory.CreateElement(
            "OrbContainer", content,
            anchor: new Vector2(0.5f, 0.70f), pivot: new Vector2(0.5f, 0.5f),
            position: Vector2.zero, size: new Vector2(260, 260));

        _coreOrb = AtlasCoreOrb.Create(orbContainer, 260f);

        // Apply Atlas orange identity
        var atlasData = Resources.Load<AIPersonalityData>("AI/Atlas");
        if (atlasData != null)
            _coreOrb.SetAIIdentity(atlasData);

        _coreOrb.SetState(OrbState.Active);

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

    // ── Status widget bar ─────────────────────────────────────────────────────

    private void BuildStatusWidgetBar(RectTransform root)
    {
        StatusWidgetBar.Create(root);
    }

    // ── Side panels (portrait + dialogue) ────────────────────────────────────

    private void BuildSidePanels(RectTransform root)
    {
        // Load Atlas personality data for the portrait panel
        var atlasData = Resources.Load<AIPersonalityData>("AI/Atlas");
        _portraitPanel = AIPortraitPanel.Create(root, atlasData);
        _dialoguePanel = DialoguePanel.Create(root);
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
