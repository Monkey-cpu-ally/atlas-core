using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

/// <summary>
/// Central manager for the Atlas HUD system (Phase 1).
/// Place this MonoBehaviour on the AtlasHUDManager GameObject in the MAIN scene.
///
/// On Awake it builds the full canvas hierarchy and wires up all five Phase-1
/// environments:
///   1. AtlasFaceEnvironment            — default view (Atlas orange identity)
///   2. AISelectionHubEnvironment       — specialist card grid
///   3. SpecialistWorkspaceEnvironment  — specialist-specific studio (Phase 1 stub)
///   4. ResearchArchiveEnvironment      — archive card track (Phase 1 stub)
///   5. CoreOperationsEnvironment       — backend diagnostics (Phase 1 stub)
///
/// Navigation is state-machine driven via EnvironmentTransitionManager.RequestStateChange().
/// Direction (forward/back) is derived automatically from enum ordering; all transitions
/// respect the input-lock guard inside the transition manager.
/// </summary>
public class ATLASMANAGER : MonoBehaviour
{
    public static ATLASMANAGER Instance { get; private set; }

    // ── Environment references ────────────────────────────────────────────────
    private AtlasFaceEnvironment            atlasFaceEnv;
    private AISelectionHubEnvironment       aiHubEnv;
    private SpecialistWorkspaceEnvironment  workspaceEnv;
    private ResearchArchiveEnvironment      archiveEnv;
    private CoreOperationsEnvironment       coreOpsEnv;

    private EnvironmentTransitionManager    transitionMgr;
    private AtlasEnvironmentBase            currentEnv;

    // ── Persistent HUD layers ─────────────────────────────────────────────────
    private NavigationDock    navDock;
    private NotificationLayer notifLayer;

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

        // Initialise visual assets (materials + procedural textures) before any
        // environment is built.  All HolographicPanel.BuildPanelLayers() calls,
        // OrbRingLayer.Create() calls, and AtlasUIFactory.CreateButton() calls
        // rely on AtlasVisualAssets being ready.
        AtlasVisualAssets.Initialize();

        Canvas canvas = BuildCanvas();

        // ── Persistent layers (NavigationDock + NotificationLayer) ────────────
        // Built before environments so environments render on top of dock,
        // then transition overlay goes on top of everything.
        navDock    = NavigationDock.Create(canvas.transform);
        notifLayer = NotificationLayer.Create(canvas.transform);

        // Transition overlay rendered on top of all environments
        GameObject tmGO = new GameObject("TransitionManager");
        tmGO.transform.SetParent(canvas.transform, false);
        transitionMgr = tmGO.AddComponent<EnvironmentTransitionManager>();
        transitionMgr.BuildOverlay(canvas.transform);

        // Build all five environments
        atlasFaceEnv = AtlasFaceEnvironment.Create(canvas.transform);
        aiHubEnv     = AISelectionHubEnvironment.Create(canvas.transform);
        workspaceEnv = SpecialistWorkspaceEnvironment.Create(canvas.transform);
        archiveEnv   = ResearchArchiveEnvironment.Create(canvas.transform);
        coreOpsEnv   = CoreOperationsEnvironment.Create(canvas.transform);

        // Register all environments with the transition manager
        var registry = new Dictionary<AtlasHUDState, AtlasEnvironmentBase>
        {
            { AtlasHUDState.AtlasFace,           atlasFaceEnv  },
            { AtlasHUDState.AISelectionHub,      aiHubEnv      },
            { AtlasHUDState.SpecialistWorkspace, workspaceEnv  },
            { AtlasHUDState.ResearchArchive,     archiveEnv    },
            { AtlasHUDState.CoreOperations,      coreOpsEnv    },
        };

        transitionMgr.Initialize(registry);

        // Start on Atlas Face; hide all other environments
        atlasFaceEnv.ShowImmediate();
        aiHubEnv.HideImmediate();
        workspaceEnv.HideImmediate();
        archiveEnv.HideImmediate();
        coreOpsEnv.HideImmediate();
        currentEnv = atlasFaceEnv;

        // Initialise navigation dock highlight
        navDock.SetActiveState(AtlasHUDState.AtlasFace);
    }

    // ── Public Navigation API ─────────────────────────────────────────────────
    //
    // RequestStateChange() derives slide direction from AtlasHUDState enum order
    // (higher value = going deeper; lower = going back), so each method below
    // works correctly for both forward and back navigation.

    /// <summary>Navigate to the Atlas Face environment (deepest back).</summary>
    public void NavigateToAtlasFace()
    {
        transitionMgr.RequestStateChange(AtlasHUDState.AtlasFace, () =>
        {
            currentEnv = atlasFaceEnv;
            navDock?.SetActiveState(AtlasHUDState.AtlasFace);
        });
    }

    /// <summary>Navigate to the AI Selection Hub.</summary>
    public void NavigateToAIHub()
    {
        transitionMgr.RequestStateChange(AtlasHUDState.AISelectionHub, () =>
        {
            currentEnv = aiHubEnv;
            navDock?.SetActiveState(AtlasHUDState.AISelectionHub);
        });
    }

    /// <summary>
    /// Navigate to the Specialist Workspace after selecting a specialist card.
    /// Populates the workspace with the chosen specialist's data before transitioning.
    /// </summary>
    public void NavigateToSpecialistWorkspace(AISpecialistCard.CardData specialist)
    {
        workspaceEnv.LoadSpecialist(specialist);
        transitionMgr.RequestStateChange(AtlasHUDState.SpecialistWorkspace, () =>
        {
            currentEnv = workspaceEnv;
            navDock?.SetActiveState(AtlasHUDState.SpecialistWorkspace);
        });
    }

    /// <summary>
    /// Navigate to the Specialist Workspace without changing the active specialist
    /// (used for back navigation from the Research Archive).
    /// </summary>
    public void NavigateToSpecialistWorkspace()
    {
        transitionMgr.RequestStateChange(AtlasHUDState.SpecialistWorkspace, () =>
        {
            currentEnv = workspaceEnv;
            navDock?.SetActiveState(AtlasHUDState.SpecialistWorkspace);
        });
    }

    /// <summary>Navigate to the Research Archive.</summary>
    public void NavigateToResearchArchive()
    {
        transitionMgr.RequestStateChange(AtlasHUDState.ResearchArchive, () =>
        {
            currentEnv = archiveEnv;
            navDock?.SetActiveState(AtlasHUDState.ResearchArchive);
        });
    }

    /// <summary>Navigate to Core Operations.</summary>
    public void NavigateToCoreOperations()
    {
        transitionMgr.RequestStateChange(AtlasHUDState.CoreOperations, () =>
        {
            currentEnv = coreOpsEnv;
            navDock?.SetActiveState(AtlasHUDState.CoreOperations);
        });
    }

    // ── Private Helpers ───────────────────────────────────────────────────────

    private static Canvas BuildCanvas()
    {
        var go     = new GameObject("AtlasHUDCanvas");
        var canvas = go.AddComponent<Canvas>();
        canvas.renderMode   = RenderMode.ScreenSpaceOverlay;
        canvas.sortingOrder = 10;

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
