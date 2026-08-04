using UnityEngine;

/// <summary>
/// Data-driven transition profile for a specific HUD state pair.
///
/// Create instances via Assets ▶ Create ▶ Atlas ▶ HUD Transition Profile.
/// Assign an array of these to EnvironmentTransitionManager.Initialize() to
/// override the default timing and curve for any From → To pair.
///
/// Suggested starting durations (from the Transition Architecture spec):
///   AtlasFace → AISelectionHub     : 0.65 s
///   AISelectionHub → Workspace     : 0.80 s
///   Workspace → ResearchArchive    : 0.90 s
///   ResearchArchive → CoreOps      : 1.00 s
///   Any back navigation            : 0.45 – 0.70 s
/// </summary>
[CreateAssetMenu(fileName = "HUDTransitionProfile", menuName = "Atlas/HUD Transition Profile", order = 2)]
public class HUDTransitionProfile : ScriptableObject
{
    [Header("State Pair")]
    public AtlasHUDState fromState;
    public AtlasHUDState toState;

    [Header("Timing")]
    [Tooltip("Total transition duration in seconds.")]
    [Min(0.05f)]
    public float duration = 0.35f;

    [Header("Curves")]
    [Tooltip("Easing applied to the shared hero element's position during the transition.")]
    public AnimationCurve heroPositionCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);

    [Tooltip("Easing applied to the shared hero element's scale during the transition.")]
    public AnimationCurve heroScaleCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);

    [Tooltip("Easing applied to the outgoing environment's alpha/slide.")]
    public AnimationCurve outgoingFadeCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);

    [Tooltip("Easing applied to the incoming environment's alpha/slide.")]
    public AnimationCurve incomingFadeCurve = AnimationCurve.EaseInOut(0f, 0f, 1f, 1f);

    [Header("Hero Element (Phase 2+)")]
    [Tooltip("World-space target position for the shared hero element at the transition end.")]
    public Vector3 targetPosition;

    [Tooltip("Target scale for the shared hero element at the transition end.")]
    public Vector3 targetScale = Vector3.one;

    [Header("Flags")]
    [Tooltip("Play the warp-flash cyan overlay during this transition.")]
    public bool useWarpFlash = true;

    [Tooltip("Animate the camera during this transition (reserved for Phase 2+).")]
    public bool moveCamera;

    [Tooltip("Keep the shared hero element visible and continuous across environments.")]
    public bool preserveHeroElement = true;
}
