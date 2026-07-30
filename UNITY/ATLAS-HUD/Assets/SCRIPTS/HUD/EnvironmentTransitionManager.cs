using System;
using System.Collections;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Manages cinematic transitions between Atlas HUD environments (Phase 1).
///
/// Transition sequence for A → B:
///   1. Full-screen warp flash (white → transparent) signals "travel"
///   2. Environment A slides out to the left  (0.35 s)
///   3. Environment B slides in from the right (0.35 s)
///
/// For B → A (reverse navigation), directions are mirrored.
///
/// The warp overlay is a full-screen Image that sits on top of all environments.
/// Call Initialize() after constructing both environments so the overlay can
/// be placed at the correct sibling index.
/// </summary>
public class EnvironmentTransitionManager : MonoBehaviour
{
    // ── Settings ──────────────────────────────────────────────────────────────

    private const float SlideDistance = 200f;   // pixels
    private const float SlideDuration = 0.35f;
    private const float FlashDuration = 0.20f;

    // ── Internal references ───────────────────────────────────────────────────

    private AtlasFaceEnvironment      atlasFaceEnv;
    private AISelectionHubEnvironment aiHubEnv;
    private Image                     warpOverlay;
    private bool                      isRunning;

    // ── Warp flash colour ─────────────────────────────────────────────────────
    // Cyan tone that matches HolographicPanel.BorderCyan at partial opacity.
    private static readonly Color WarpColor = new Color(
        HolographicPanel.BorderCyan.r,
        HolographicPanel.BorderCyan.g,
        HolographicPanel.BorderCyan.b,
        0f);   // alpha driven by the flash coroutine

    // ── Setup ─────────────────────────────────────────────────────────────────

    /// <summary>
    /// Creates the warp flash overlay under <paramref name="canvasRoot"/>.
    /// Must be called before Initialize().
    /// </summary>
    public void BuildOverlay(Transform canvasRoot)
    {
        var rt   = AtlasUIFactory.CreateFullStretch("WarpOverlay", canvasRoot);
        warpOverlay       = rt.gameObject.AddComponent<Image>();
        warpOverlay.color = WarpColor;   // starts transparent
        // Overlay sits on top of everything
        rt.SetAsLastSibling();
    }

    /// <summary>
    /// Stores references to both environments so Transition() can drive them.
    /// Call after both environments have been created.
    /// </summary>
    public void Initialize(AtlasFaceEnvironment face, AISelectionHubEnvironment hub)
    {
        atlasFaceEnv = face;
        aiHubEnv     = hub;

        // Ensure overlay remains on top
        if (warpOverlay != null)
            warpOverlay.transform.SetAsLastSibling();
    }

    // ── Public transition API ─────────────────────────────────────────────────

    /// <summary>
    /// Cinematic transition from <paramref name="from"/> → <paramref name="to"/>.
    /// </summary>
    /// <param name="direction">+1 = going deeper (left→right); -1 = going back.</param>
    /// <param name="onComplete">Callback invoked after the transition finishes.</param>
    public void Transition(AtlasEnvironmentBase from, AtlasEnvironmentBase to,
                           int direction, Action onComplete = null)
    {
        if (isRunning) return;
        StartCoroutine(RunTransition(from, to, direction, onComplete));
    }

    // ── Coroutine ─────────────────────────────────────────────────────────────

    private IEnumerator RunTransition(AtlasEnvironmentBase from, AtlasEnvironmentBase to,
                                      int direction, Action onComplete)
    {
        isRunning = true;

        float slideOut = -SlideDistance * direction;   // 'from' exits this direction
        float slideIn  =  SlideDistance * direction;   // 'to' enters from opposite side

        // ── Phase 1: warp flash ───────────────────────────────────────────────
        yield return StartCoroutine(FlashOverlay(FlashDuration));

        // ── Phase 2: slide-out current + slide-in next (overlapping) ─────────
        // Run both coroutines concurrently by launching as separate child routines
        bool outDone = false;
        bool inDone  = false;

        StartCoroutine(RunOut(from, slideOut, () => outDone = true));
        StartCoroutine(RunIn( to,  slideIn,  () => inDone  = true));

        while (!outDone || !inDone)
            yield return null;

        isRunning = false;
        onComplete?.Invoke();
    }

    private IEnumerator RunOut(AtlasEnvironmentBase env, float offset, Action done)
    {
        yield return StartCoroutine(env.SlideOut(SlideDuration, offset));
        done();
    }

    private IEnumerator RunIn(AtlasEnvironmentBase env, float offset, Action done)
    {
        yield return StartCoroutine(env.SlideIn(SlideDuration, offset));
        done();
    }

    // ── Warp flash overlay ────────────────────────────────────────────────────

    private IEnumerator FlashOverlay(float duration)
    {
        if (warpOverlay == null) yield break;

        float half    = duration * 0.5f;
        float elapsed = 0f;

        // Fade in
        while (elapsed < half)
        {
            elapsed += Time.deltaTime;
            float a = Mathf.Clamp01(elapsed / half) * 0.55f;
            warpOverlay.color = new Color(WarpColor.r, WarpColor.g, WarpColor.b, a);
            yield return null;
        }

        // Fade out
        elapsed = 0f;
        while (elapsed < half)
        {
            elapsed += Time.deltaTime;
            float a = (1f - Mathf.Clamp01(elapsed / half)) * 0.55f;
            warpOverlay.color = new Color(WarpColor.r, WarpColor.g, WarpColor.b, a);
            yield return null;
        }

        warpOverlay.color = WarpColor;   // fully transparent (alpha = 0)
    }
}
