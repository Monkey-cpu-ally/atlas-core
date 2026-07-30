using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// The Atlas Core Orb — the living centrepiece of the Atlas Face environment.
///
/// Visual structure (bottom → top in draw order):
///   Ring_Outer   — 52% of container, slow CW drift
///   Ring_Middle  — 34% of container, slightly faster CCW drift
///   Ring_Inner   — 18% of container, slightly slower CW drift
///   CoreGroup    — container for the sphere layers; breathing scale animation
///     CoreGlow   — large ambient halo, very low alpha
///     CoreField  — plasma body, dark blue base tinted by active AI
///     CoreBright — central bright point, full AI primary colour
///
/// Ring geometry fractions are locked to atlas_hud_v2.theme.json:
///   inner_radius_pct = 18, middle_radius_pct = 34, outer_radius_pct = 52
///
/// Breathing constants from atlas_motion_tokens.json:
///   core_breathing period = 6 000 ms, amplitude = 4%
///
/// Ring idle rotation from atlas_motion_tokens.json:
///   ring_idle = 36 000 ms per revolution (linear drift, not spinning)
///
/// Note: Ring Images are squares in Phase 1. Assign a ring-shaped Sprite to
///       each OrbRingLayer.ringImage in a future polish phase for circular geometry.
///
/// Usage:
///   var orb = AtlasCoreOrb.Create(parentTransform, 300f);
///   orb.SetAIIdentity(ajaniData);
///   orb.SetState(OrbState.Active);
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class AtlasCoreOrb : MonoBehaviour
{
    // ── Spec-locked constants ─────────────────────────────────────────────────

    private const float InnerRingFraction  = 0.18f;
    private const float MiddleRingFraction = 0.34f;
    private const float OuterRingFraction  = 0.52f;

    // Core sphere layer sizes as fraction of container.
    private const float CoreGlowFraction   = 0.32f;
    private const float CoreFieldFraction  = 0.20f;
    private const float CoreBrightFraction = 0.09f;

    // atlas_motion_tokens.json: core_breathing 6 000 ms, amplitude 4%.
    private const float BreathPeriodSec   = 6.0f;
    private const float BreathAmplitude   = 0.04f;

    // Ring revolution periods — outer is slowest, inner slightly faster.
    // All are multiples of the spec's 36 s base period.
    private const float OuterRevSec  = 36.0f;
    private const float MiddleRevSec = 28.8f;   // 36 × 0.8
    private const float InnerRevSec  = 43.2f;   // 36 × 1.2

    // ── References ────────────────────────────────────────────────────────────

    private OrbRingLayer       outerRing;
    private OrbRingLayer       middleRing;
    private OrbRingLayer       innerRing;
    private RectTransform      coreGroup;
    private Image              coreGlow;
    private Image              coreField;
    private Image              coreBright;
    private OrbStateController stateController;
    private Coroutine          breathRoutine;

    // Default core colours (no AI selected — neutral cyan).
    private Color currentPrimary = HolographicPanel.BorderCyan;
    private Color currentSoft    = new Color(0f, 0.45f, 1.00f, 0.22f);

    // ── Public accessors ──────────────────────────────────────────────────────

    public OrbStateController StateController => stateController;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Builds the complete orb hierarchy under <paramref name="parent"/> and
    /// returns the AtlasCoreOrb component.
    /// </summary>
    /// <param name="parent">Content RectTransform to attach to.</param>
    /// <param name="containerSize">Square side length of the orb container in pixels.</param>
    public static AtlasCoreOrb Create(Transform parent, float containerSize)
    {
        var go = new GameObject("AtlasCoreOrb");
        go.transform.SetParent(parent, false);

        var rt              = go.AddComponent<RectTransform>();
        rt.anchorMin        = new Vector2(0.5f, 0.5f);
        rt.anchorMax        = new Vector2(0.5f, 0.5f);
        rt.pivot            = new Vector2(0.5f, 0.5f);
        rt.sizeDelta        = new Vector2(containerSize, containerSize);
        rt.anchoredPosition = Vector2.zero;

        var orb              = go.AddComponent<AtlasCoreOrb>();
        orb.stateController  = go.AddComponent<OrbStateController>();
        orb.Build(rt, containerSize);
        orb.stateController.Initialize(orb);
        return orb;
    }

    // ── Construction ──────────────────────────────────────────────────────────

    private void Build(RectTransform root, float size)
    {
        // ── Rings (drawn before core so they appear behind it) ─────────────────
        // Each ring uses a slightly different revolution period and alternates
        // direction to create an organic orbital feel, not mechanical spinning.
        outerRing  = OrbRingLayer.Create(root, size, OuterRingFraction,  OuterRevSec,  direction:  1f,
                         new Color(HolographicPanel.BorderCyan.r,
                                   HolographicPanel.BorderCyan.g,
                                   HolographicPanel.BorderCyan.b, 0.10f));

        middleRing = OrbRingLayer.Create(root, size, MiddleRingFraction, MiddleRevSec, direction: -1f,
                         new Color(HolographicPanel.BorderCyan.r,
                                   HolographicPanel.BorderCyan.g,
                                   HolographicPanel.BorderCyan.b, 0.16f));

        innerRing  = OrbRingLayer.Create(root, size, InnerRingFraction,  InnerRevSec,  direction:  1f,
                         new Color(HolographicPanel.BorderCyan.r,
                                   HolographicPanel.BorderCyan.g,
                                   HolographicPanel.BorderCyan.b, 0.22f));

        // ── CoreGroup — breathing scale animation applied here ─────────────────
        var coreGO     = new GameObject("CoreGroup");
        coreGO.transform.SetParent(root, false);
        coreGroup      = coreGO.AddComponent<RectTransform>();
        coreGroup.anchorMin        = Vector2.zero;
        coreGroup.anchorMax        = Vector2.one;
        coreGroup.offsetMin        = Vector2.zero;
        coreGroup.offsetMax        = Vector2.zero;

        // ── Sphere layers (from large ambient halo down to bright centre point) ─
        float glowSize   = size * CoreGlowFraction;
        float fieldSize  = size * CoreFieldFraction;
        float brightSize = size * CoreBrightFraction;

        // Glow: large, very low alpha — gives the "plasma cloud" impression.
        coreGlow   = BuildCoreLayer("CoreGlow",   coreGroup, glowSize,
                         new Color(0f, 0.45f, 1.00f, 0.22f));

        // Field: the body of the orb — dark blue base, tinted by active AI.
        coreField  = BuildCoreLayer("CoreField",  coreGroup, fieldSize,
                         new Color(0.03f, 0.07f, 0.16f, 0.92f));

        // Bright: the brilliant inner point — full AI primary colour.
        coreBright = BuildCoreLayer("CoreBright", coreGroup, brightSize,
                         HolographicPanel.BorderCyan);

        // ── Start breathing ────────────────────────────────────────────────────
        breathRoutine = StartCoroutine(BreathingRoutine());
    }

    private static Image BuildCoreLayer(string name, RectTransform parent, float size, Color color)
    {
        var rt          = AtlasUIFactory.CreateElement(name, parent,
                              new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
                              Vector2.zero, new Vector2(size, size));
        var img         = rt.gameObject.AddComponent<Image>();
        img.color       = color;
        return img;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>
    /// Shifts the orb's accent colour to the active AI's identity and updates
    /// the pulse timing to match that AI's personality.
    /// </summary>
    /// <param name="data">
    ///   One of the four AIPersonalityData assets in Assets/RESOURCES/AI/.
    ///   Pass null to reset to the neutral Atlas chrome colour.
    /// </param>
    public void SetAIIdentity(AIPersonalityData data)
    {
        if (data == null)
        {
            ResetToNeutral();
            return;
        }

        currentPrimary = data.primaryColor;
        currentSoft    = data.softColor;

        ApplyColors(data.primaryColor, data.softColor, data.edgeColor);
        stateController.SetPulsePeriod(data.pulseDurationMs / 1000f);
    }

    /// <summary>Transitions the orb to a new operational state.</summary>
    public void SetState(OrbState state) => stateController.SetState(state);

    // ── Called by OrbStateController ──────────────────────────────────────────

    /// <summary>
    /// Drives core sphere brightness.  t = 0 (standby dim) → 1 (fully active).
    /// Called every frame by OrbStateController's pulse coroutine.
    /// </summary>
    public void SetCoreIntensity(float t)
    {
        if (coreGlow == null || coreBright == null) return;

        Color g = coreGlow.color;
        g.a = Mathf.Lerp(0.12f, 0.45f, t);
        coreGlow.color = g;

        Color b = coreBright.color;
        b.a = Mathf.Lerp(0.40f, 1.00f, t);
        coreBright.color = b;
    }

    /// <summary>
    /// Drives ring brightness.  t = 0 (idle opacity) → 1 (active opacity).
    /// Called when the orb state changes.
    /// </summary>
    public void SetRingIntensity(float t)
    {
        innerRing?.SetIntensity(t);
        middleRing?.SetIntensity(t);
        outerRing?.SetIntensity(t);
    }

    // ── Internal helpers ──────────────────────────────────────────────────────

    private void ApplyColors(Color primary, Color soft, Color edge)
    {
        // Core layers take on the AI's colours.
        if (coreGlow != null)
            coreGlow.color   = new Color(soft.r,    soft.g,    soft.b,    0.22f);
        if (coreBright != null)
            coreBright.color = new Color(primary.r, primary.g, primary.b, coreBright.color.a);

        // Rings shift to the AI's edge colour (preserving their individual alphas).
        innerRing?.SetColor( new Color(edge.r, edge.g, edge.b, 0.22f));
        middleRing?.SetColor(new Color(edge.r, edge.g, edge.b, 0.16f));
        outerRing?.SetColor( new Color(edge.r, edge.g, edge.b, 0.10f));
    }

    private void ResetToNeutral()
    {
        currentPrimary = HolographicPanel.BorderCyan;
        currentSoft    = new Color(0f, 0.45f, 1.00f, 0.22f);
        Color edge     = HolographicPanel.BorderCyan;
        ApplyColors(HolographicPanel.BorderCyan, currentSoft, edge);
    }

    // ── Breathing coroutine ───────────────────────────────────────────────────

    /// <summary>
    /// Animates the CoreGroup with a gentle ±4% scale pulse (6 s period).
    /// Source: atlas_motion_tokens.json → core_breathing: 6000 ms, amplitude: 4%.
    /// </summary>
    private IEnumerator BreathingRoutine()
    {
        float phase = 0f;
        while (true)
        {
            phase += Time.deltaTime * (Mathf.PI * 2f / BreathPeriodSec);
            float scale = 1f + Mathf.Sin(phase) * BreathAmplitude;
            if (coreGroup != null)
                coreGroup.localScale = new Vector3(scale, scale, 1f);
            yield return null;
        }
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    private void OnDestroy()
    {
        if (breathRoutine != null)
            StopCoroutine(breathRoutine);
    }
}
