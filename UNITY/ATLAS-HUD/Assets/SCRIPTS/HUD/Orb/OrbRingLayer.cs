using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// One concentric ring layer of the Atlas Core Orb.
///
/// Each ring is a square Image that rotates slowly at a spec-locked pace.
/// Three rings at inner / middle / outer radii create the orbital halo effect.
///
/// Ring geometry is driven by a fraction of the orb container size:
///   inner  = 18%  (atlas_hud_v2.theme.json → rings.inner_radius_pct)
///   middle = 34%
///   outer  = 52%
///
/// Note: Without a circle sprite assigned, the Image renders as a coloured
///       square — this is intentional for Phase 1. Assign a ring-shaped
///       Sprite to ringImage in a future polish phase to achieve circular geometry.
///
/// Usage: OrbRingLayer.Create(parent, containerSize, radiusFraction, ...)
/// </summary>
[RequireComponent(typeof(RectTransform))]
public class OrbRingLayer : MonoBehaviour
{
    // ── Inspector ─────────────────────────────────────────────────────────────

    [Tooltip("Revolution period in seconds (36 s = spec idle pace).")]
    [SerializeField] private float revolutionSeconds = 36f;

    [Tooltip("+1 = clockwise, -1 = counter-clockwise.")]
    [SerializeField] private float rotationDirection = 1f;

    // ── Internal ──────────────────────────────────────────────────────────────

    private Image  ringImage;
    private float  idleAlpha;
    private float  activeAlpha;
    private Coroutine idleRoutine;

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Creates a ring layer centred inside <paramref name="parent"/>.
    /// </summary>
    /// <param name="parent">The orb container RectTransform.</param>
    /// <param name="containerSize">Container square side length in pixels.</param>
    /// <param name="radiusFraction">Ring diameter as a fraction of container size (e.g. 0.52 for outer).</param>
    /// <param name="revolutionSec">Seconds for one full revolution.</param>
    /// <param name="direction">+1 clockwise, -1 counter-clockwise.</param>
    /// <param name="color">Base colour including alpha (alpha becomes the idle alpha).</param>
    public static OrbRingLayer Create(Transform parent, float containerSize,
        float radiusFraction, float revolutionSec, float direction, Color color)
    {
        float diameter = containerSize * radiusFraction;

        var go = new GameObject($"Ring_{radiusFraction:F2}");
        go.transform.SetParent(parent, false);

        var rt          = go.AddComponent<RectTransform>();
        rt.anchorMin    = new Vector2(0.5f, 0.5f);
        rt.anchorMax    = new Vector2(0.5f, 0.5f);
        rt.pivot        = new Vector2(0.5f, 0.5f);
        rt.sizeDelta    = new Vector2(diameter, diameter);
        rt.anchoredPosition = Vector2.zero;

        var img   = go.AddComponent<Image>();
        img.color = color;

        // Apply the procedural ring shader so the Image renders as a torus
        // with a soft glow halo instead of a plain coloured square.
        if (AtlasVisualAssets.OrbRingMat != null)
            img.material = AtlasVisualAssets.OrbRingMat;

        var ring                 = go.AddComponent<OrbRingLayer>();
        ring.ringImage           = img;
        ring.revolutionSeconds   = revolutionSec;
        ring.rotationDirection   = direction;
        ring.idleAlpha           = color.a;
        ring.activeAlpha         = Mathf.Min(color.a * 2.8f, 0.85f);

        ring.StartIdleRotation();
        return ring;
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>Replaces the ring colour (preserves idle/active alpha relationship).</summary>
    public void SetColor(Color newColor)
    {
        idleAlpha    = newColor.a;
        activeAlpha  = Mathf.Min(newColor.a * 2.8f, 0.85f);
        if (ringImage != null)
            ringImage.color = newColor;
    }

    /// <summary>
    /// Transitions between idle (standby) and active visual intensity.
    /// t = 0 → idle alpha; t = 1 → active alpha.
    /// </summary>
    public void SetIntensity(float t)
    {
        if (ringImage == null) return;
        Color c = ringImage.color;
        c.a = Mathf.Lerp(idleAlpha, activeAlpha, t);
        ringImage.color = c;
    }

    /// <summary>Starts or restarts the idle rotation coroutine.</summary>
    public void StartIdleRotation()
    {
        if (idleRoutine != null) StopCoroutine(idleRoutine);
        idleRoutine = StartCoroutine(IdleRotationRoutine());
    }

    /// <summary>Stops the idle rotation coroutine and holds current angle.</summary>
    public void StopIdleRotation()
    {
        if (idleRoutine == null) return;
        StopCoroutine(idleRoutine);
        idleRoutine = null;
    }

    // ── Coroutine ─────────────────────────────────────────────────────────────

    private IEnumerator IdleRotationRoutine()
    {
        // Spec: ring_idle = 36 000 ms (one full revolution). Linear, like an astronomical body.
        float degreesPerSecond = (360f / revolutionSeconds) * rotationDirection;
        while (true)
        {
            transform.Rotate(0f, 0f, degreesPerSecond * Time.deltaTime);
            yield return null;
        }
    }
}
