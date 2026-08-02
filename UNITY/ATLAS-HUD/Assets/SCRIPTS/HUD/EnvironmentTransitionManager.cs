using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Manages cinematic transitions between Atlas HUD environments.
///
/// Transition sequence for A → B:
///   1. Warp flash (cyan → transparent) signals "travel"
///   2. Environment A slides out (direction-keyed)
///   3. Environment B slides in from the opposite side
///
/// Usage:
///   1. Call BuildOverlay(canvasRoot) to create the warp flash overlay.
///   2. Call Initialize(registry) with a state → environment dictionary.
///   3. Call RequestStateChange(destination) to trigger a guarded transition.
///
/// The legacy Transition(from, to, direction, onComplete) API is preserved
/// for backward compatibility.
/// </summary>
public class EnvironmentTransitionManager : MonoBehaviour
{
    // ── Default timing constants ──────────────────────────────────────────────

    private const float DefaultSlideDistance = 200f;
    private const float DefaultSlideDuration = 0.35f;
    private const float DefaultFlashDuration = 0.20f;

    // ── Internal state ────────────────────────────────────────────────────────

    private Image   warpOverlay;
    private bool    isRunning;

    private AtlasHUDState currentState = AtlasHUDState.AtlasFace;
    private Dictionary<AtlasHUDState, AtlasEnvironmentBase> registry;
    private RectTransform   heroElement;
    private HUDTransitionProfile[] profiles;

    // ── Warp flash colour ─────────────────────────────────────────────────────
    // Cyan tone that matches HolographicPanel.BorderCyan at zero alpha.
    private static readonly Color WarpColor = new Color(
        HolographicPanel.BorderCyan.r,
        HolographicPanel.BorderCyan.g,
        HolographicPanel.BorderCyan.b,
        0f);

    // ── Public read-only properties ───────────────────────────────────────────

    /// <summary>True while a transition coroutine is running. Use to guard input.</summary>
    public bool IsTransitioning => isRunning;

    /// <summary>The HUD state that is currently active (or being transitioned from).</summary>
    public AtlasHUDState CurrentState => currentState;

    // ── Setup ─────────────────────────────────────────────────────────────────

    /// <summary>
    /// Creates the warp flash overlay under <paramref name="canvasRoot"/>.
    /// Must be called before Initialize().
    /// </summary>
    public void BuildOverlay(Transform canvasRoot)
    {
        var rt      = AtlasUIFactory.CreateFullStretch("WarpOverlay", canvasRoot);
        warpOverlay       = rt.gameObject.AddComponent<Image>();
        warpOverlay.color = WarpColor;   // starts fully transparent
        // Overlay rendered on top of all environments
        rt.SetAsLastSibling();
    }

    /// <summary>
    /// Initialises the transition system with a complete environment registry.
    /// Call after all environments have been created.
    /// </summary>
    /// <param name="envRegistry">Maps each AtlasHUDState to its environment.</param>
    /// <param name="hero">
    ///   Optional shared hero element (Atlas Orb). Reserved for Phase 2 hero-motion support.
    /// </param>
    /// <param name="transitionProfiles">
    ///   Optional per-pair timing overrides. Falls back to defaults when null or unmatched.
    /// </param>
    public void Initialize(
        Dictionary<AtlasHUDState, AtlasEnvironmentBase> envRegistry,
        RectTransform hero = null,
        HUDTransitionProfile[] transitionProfiles = null)
    {
        registry  = envRegistry;
        heroElement = hero;
        profiles  = transitionProfiles;
        currentState = AtlasHUDState.AtlasFace;

        if (warpOverlay != null)
            warpOverlay.transform.SetAsLastSibling();
    }

    // ── State-machine API ─────────────────────────────────────────────────────

    /// <summary>
    /// Requests a guarded transition to <paramref name="destination"/>.
    /// Ignored while a transition is already running or if destination equals current state.
    /// </summary>
    public void RequestStateChange(AtlasHUDState destination, Action onComplete = null)
    {
        if (isRunning) return;
        if (registry == null) return;
        if (currentState == destination) return;

        if (!registry.TryGetValue(currentState, out var from)) return;
        if (!registry.TryGetValue(destination, out var to)) return;

        HUDTransitionProfile profile = FindProfile(currentState, destination);
        float duration  = profile != null ? profile.duration : DefaultSlideDuration;
        bool  useFlash  = profile == null  || profile.useWarpFlash;
        int   direction = (int)destination > (int)currentState ? 1 : -1;

        AtlasHUDState nextState = destination;
        StartCoroutine(RunTransition(from, to, direction, duration, useFlash, () =>
        {
            currentState = nextState;
            onComplete?.Invoke();
        }));
    }

    // ── Legacy transition API (backward compatibility) ────────────────────────

    /// <summary>
    /// Direct transition between two environments. Does not update the internal
    /// state machine; prefer RequestStateChange() for new code.
    /// </summary>
    public void Transition(AtlasEnvironmentBase from, AtlasEnvironmentBase to,
                           int direction, Action onComplete = null)
    {
        if (isRunning) return;
        StartCoroutine(RunTransition(from, to, direction,
                                     DefaultSlideDuration, true, onComplete));
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private HUDTransitionProfile FindProfile(AtlasHUDState from, AtlasHUDState to)
    {
        if (profiles == null) return null;
        for (int i = 0; i < profiles.Length; i++)
        {
            var p = profiles[i];
            if (p != null && p.fromState == from && p.toState == to)
                return p;
        }
        return null;
    }

    // ── Coroutines ────────────────────────────────────────────────────────────

    private IEnumerator RunTransition(AtlasEnvironmentBase from, AtlasEnvironmentBase to,
                                       int direction, float duration,
                                       bool useFlash, Action onComplete)
    {
        isRunning = true;

        float slideOut = -DefaultSlideDistance * direction;
        float slideIn  =  DefaultSlideDistance * direction;

        if (useFlash)
            yield return StartCoroutine(FlashOverlay(DefaultFlashDuration));

        bool outDone = false;
        bool inDone  = false;

        StartCoroutine(RunOut(from, slideOut, duration, () => outDone = true));
        StartCoroutine(RunIn( to,  slideIn,  duration, () => inDone  = true));

        while (!outDone || !inDone)
            yield return null;

        isRunning = false;
        onComplete?.Invoke();
    }

    private IEnumerator RunOut(AtlasEnvironmentBase env, float offset, float duration, Action done)
    {
        yield return StartCoroutine(env.SlideOut(duration, offset));
        done();
    }

    private IEnumerator RunIn(AtlasEnvironmentBase env, float offset, float duration, Action done)
    {
        yield return StartCoroutine(env.SlideIn(duration, offset));
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
