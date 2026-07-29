using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

/// <summary>
/// Central manager for the Atlas HUD system (Phase 1).
/// Place this MonoBehaviour on the AtlasHUDManager GameObject in the MAIN scene.
/// On Awake it builds the full canvas hierarchy and wires up both Phase-1 environments:
///   • AtlasFaceEnvironment   (default view)
///   • AISelectionHubEnvironment
/// Navigation is driven by ATLASMANAGER.Instance.NavigateTo…().
/// </summary>
public class ATLASMANAGER : MonoBehaviour
{
    public static ATLASMANAGER Instance { get; private set; }

    // ── Internal environment references ──────────────────────────────────────
    private AtlasFaceEnvironment       atlasFaceEnv;
    private AISelectionHubEnvironment  aiHubEnv;
    private EnvironmentTransitionManager transitionMgr;

    private AtlasEnvironmentBase currentEnv;
    private bool isTransitioning;

    // ─────────────────────────────────────────────────────────────────────────
    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;

        Bootstrap();
    }

    // ── Bootstrap ─────────────────────────────────────────────────────────────
    private void Bootstrap()
    {
        EnsureEventSystem();

        // Root Canvas
        Canvas canvas = BuildCanvas();

        // Transition overlay sits behind environments in draw order
        GameObject tmGO  = new GameObject("TransitionManager");
        tmGO.transform.SetParent(canvas.transform, false);
        transitionMgr = tmGO.AddComponent<EnvironmentTransitionManager>();
        transitionMgr.BuildOverlay(canvas.transform);

        // Build both environments
        atlasFaceEnv = AtlasFaceEnvironment.Create(canvas.transform);
        aiHubEnv     = AISelectionHubEnvironment.Create(canvas.transform);

        transitionMgr.Initialize(atlasFaceEnv, aiHubEnv);

        // Start on Atlas Face
        atlasFaceEnv.ShowImmediate();
        aiHubEnv.HideImmediate();
        currentEnv = atlasFaceEnv;
    }

    // ── Public Navigation API ─────────────────────────────────────────────────

    /// <summary>Transition from Atlas Face → AI Selection Hub.</summary>
    public void NavigateToAIHub()
    {
        if (isTransitioning || currentEnv != atlasFaceEnv) return;
        isTransitioning = true;
        transitionMgr.Transition(atlasFaceEnv, aiHubEnv, direction: 1, onComplete: () =>
        {
            currentEnv      = aiHubEnv;
            isTransitioning = false;
        });
    }

    /// <summary>Transition from AI Selection Hub → Atlas Face.</summary>
    public void NavigateToAtlasFace()
    {
        if (isTransitioning || currentEnv != aiHubEnv) return;
        isTransitioning = true;
        transitionMgr.Transition(aiHubEnv, atlasFaceEnv, direction: -1, onComplete: () =>
        {
            currentEnv      = atlasFaceEnv;
            isTransitioning = false;
        });
    }

    // ── Private Helpers ───────────────────────────────────────────────────────

    private static Canvas BuildCanvas()
    {
        var go     = new GameObject("AtlasHUDCanvas");
        var canvas = go.AddComponent<Canvas>();
        canvas.renderMode    = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder  = 10;

        var scaler = go.AddComponent<CanvasScaler>();
        scaler.uiScaleMode         = CanvasScaler.ScaleMode.ScaleWithScreenSize;
        scaler.referenceResolution = new Vector2(1920, 1080);
        scaler.matchWidthOrHeight  = 0.5f;

        go.AddComponent<GraphicRaycaster>();
        return canvas;
    }

    private static void EnsureEventSystem()
    {
        // FindFirstObjectByType requires Unity 6 (6000.x) — this project targets Unity 6000.5.4f1.
        if (FindFirstObjectByType<EventSystem>() != null) return;
        var esGO = new GameObject("EventSystem");
        esGO.AddComponent<EventSystem>();
        esGO.AddComponent<StandaloneInputModule>();
    }
}
