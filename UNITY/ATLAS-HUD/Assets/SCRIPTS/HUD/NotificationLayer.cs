using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Notification Layer — persistent full-screen overlay that renders holographic
/// toast notifications in the top-right corner.
///
/// Sits at the top of the canvas sibling hierarchy so notifications always
/// appear above environment content. The layer itself has zero background so
/// it does not interfere with interaction below it.
///
/// Usage:
///   NotificationLayer.Instance.Show("SYSTEM", "Uplink established.", NotifType.Info, 3f);
/// </summary>
public class NotificationLayer : MonoBehaviour
{
    // ── Notification type ─────────────────────────────────────────────────────

    public enum NotifType { Info, Warning, Alert, Success }

    // ── Singleton ─────────────────────────────────────────────────────────────

    public static NotificationLayer Instance { get; private set; }

    // ── Layout constants ──────────────────────────────────────────────────────

    private const int   MaxVisible     = 4;
    private const float ToastWidth     = 280f;
    private const float ToastHeight    = 52f;
    private const float ToastSpacing   = 6f;
    private const float FadeDuration   = 0.25f;

    // ── Toast colours ─────────────────────────────────────────────────────────

    private static readonly Color ColInfo    = new Color(0f,    0.78f, 1f,    1f);
    private static readonly Color ColWarning = new Color(1f,    0.75f, 0f,    1f);
    private static readonly Color ColAlert   = new Color(1f,    0.20f, 0.20f, 1f);
    private static readonly Color ColSuccess = new Color(0.10f, 1f,    0.40f, 1f);

    // ── Internal state ────────────────────────────────────────────────────────

    private RectTransform toastContainer;
    private Queue<GameObject> pool = new Queue<GameObject>();

    // ── Factory ───────────────────────────────────────────────────────────────

    /// <summary>
    /// Creates the notification layer as a sibling of all environments in the
    /// canvas, placed just below the warp-flash overlay.
    /// </summary>
    public static NotificationLayer Create(Transform canvasRoot)
    {
        var go = new GameObject("NotificationLayer");
        go.transform.SetParent(canvasRoot, false);

        var rt       = go.AddComponent<RectTransform>();
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        rt.offsetMin = Vector2.zero;
        rt.offsetMax = Vector2.zero;

        // Transparent canvas group so the layer itself catches no raycasts.
        var cg                   = go.AddComponent<CanvasGroup>();
        cg.blocksRaycasts        = false;
        cg.interactable          = false;
        cg.alpha                 = 1f;

        var layer = go.AddComponent<NotificationLayer>();
        layer.BuildLayer(rt);
        return layer;
    }

    // ── Construction ──────────────────────────────────────────────────────────

    private void BuildLayer(RectTransform root)
    {
        Instance = this;

        // Toast anchor container — top-right corner
        var containerGO  = new GameObject("ToastContainer");
        containerGO.transform.SetParent(root, false);

        toastContainer   = containerGO.AddComponent<RectTransform>();
        toastContainer.anchorMin = new Vector2(1f, 1f);
        toastContainer.anchorMax = new Vector2(1f, 1f);
        toastContainer.pivot     = new Vector2(1f, 1f);
        toastContainer.sizeDelta = new Vector2(ToastWidth + 16f, 0f);
        toastContainer.anchoredPosition = new Vector2(-16f, -16f);

        // Vertical layout so toasts stack downwards automatically
        var layout              = containerGO.AddComponent<VerticalLayoutGroup>();
        layout.childAlignment   = TextAnchor.UpperRight;
        layout.spacing          = ToastSpacing;
        layout.childForceExpandWidth  = true;
        layout.childForceExpandHeight = false;
        layout.reverseArrangement     = false;

        var fitter           = containerGO.AddComponent<ContentSizeFitter>();
        fitter.verticalFit   = ContentSizeFitter.FitMode.PreferredSize;

        // Seed two startup notifications to prove the layer works
        Show("ATLAS HUD", "Holographic shell initialised.",   NotifType.Success, 5f);
        Show("UPLINK",    "Secure channel active  [256-bit].", NotifType.Info,    6f);
    }

    // ── Public API ────────────────────────────────────────────────────────────

    /// <summary>
    /// Displays a toast notification that auto-dismisses after <paramref name="duration"/> seconds.
    /// </summary>
    public void Show(string title, string message, NotifType type, float duration = 4f)
    {
        if (toastContainer == null) return;

        // Limit simultaneous toasts
        int current = toastContainer.childCount;
        if (current >= MaxVisible) return;

        Color accent = TypeColor(type);
        var toast    = BuildToast(title, message, accent);
        toast.transform.SetParent(toastContainer, false);

        StartCoroutine(ToastLifecycle(toast, duration));
    }

    // ── Toast builder ─────────────────────────────────────────────────────────

    private GameObject BuildToast(string title, string message, Color accent)
    {
        var go = new GameObject("Toast");
        var rt = go.AddComponent<RectTransform>();
        rt.sizeDelta = new Vector2(ToastWidth, ToastHeight);

        var le           = go.AddComponent<LayoutElement>();
        le.preferredHeight = ToastHeight;
        le.flexibleWidth   = 1;

        var cg              = go.AddComponent<CanvasGroup>();
        cg.alpha            = 0f;

        // Background
        var bg      = go.AddComponent<Image>();
        bg.color    = new Color(0.02f, 0.06f, 0.16f, 0.92f);

        // Left accent stripe
        var stripeRT = new GameObject("Stripe").AddComponent<RectTransform>();
        stripeRT.SetParent(go.transform, false);
        stripeRT.anchorMin = Vector2.zero;
        stripeRT.anchorMax = new Vector2(0f, 1f);
        stripeRT.offsetMin = Vector2.zero;
        stripeRT.offsetMax = new Vector2(4, 0);
        stripeRT.gameObject.AddComponent<Image>().color = accent;

        // Top border
        var topRT = new GameObject("TopBorder").AddComponent<RectTransform>();
        topRT.SetParent(go.transform, false);
        topRT.anchorMin = new Vector2(0f, 1f);
        topRT.anchorMax = Vector2.one;
        topRT.offsetMin = Vector2.zero;
        topRT.offsetMax = new Vector2(0, 1);
        topRT.gameObject.AddComponent<Image>().color =
            new Color(accent.r, accent.g, accent.b, 0.55f);

        // Title text
        var titleRT = new GameObject("Title").AddComponent<RectTransform>();
        titleRT.SetParent(go.transform, false);
        titleRT.anchorMin = new Vector2(0f, 0.52f);
        titleRT.anchorMax = Vector2.one;
        titleRT.offsetMin = new Vector2(10, 0);
        titleRT.offsetMax = new Vector2(-6, -3);
        var titleTxt       = titleRT.gameObject.AddComponent<Text>();
        titleTxt.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        titleTxt.text      = title;
        titleTxt.fontSize  = 10;
        titleTxt.color     = accent;
        titleTxt.alignment = TextAnchor.MiddleLeft;

        // Message text
        var msgRT = new GameObject("Message").AddComponent<RectTransform>();
        msgRT.SetParent(go.transform, false);
        msgRT.anchorMin = Vector2.zero;
        msgRT.anchorMax = new Vector2(1f, 0.52f);
        msgRT.offsetMin = new Vector2(10, 3);
        msgRT.offsetMax = new Vector2(-6, 0);
        var msgTxt         = msgRT.gameObject.AddComponent<Text>();
        msgTxt.font        = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        msgTxt.text        = message;
        msgTxt.fontSize    = 8;
        msgTxt.color       = HolographicPanel.TextPrimary;
        msgTxt.alignment   = TextAnchor.MiddleLeft;

        return go;
    }

    // ── Toast lifecycle coroutine ─────────────────────────────────────────────

    private IEnumerator ToastLifecycle(GameObject toast, float duration)
    {
        var cg = toast.GetComponent<CanvasGroup>();

        // Fade in
        yield return StartCoroutine(FadeCanvasGroup(cg, 0f, 1f, FadeDuration));

        // Hold
        yield return new WaitForSeconds(duration);

        // Fade out
        yield return StartCoroutine(FadeCanvasGroup(cg, 1f, 0f, FadeDuration));

        Destroy(toast);
    }

    private IEnumerator FadeCanvasGroup(CanvasGroup cg, float from, float to, float dur)
    {
        float elapsed = 0f;
        while (elapsed < dur)
        {
            elapsed   += Time.deltaTime;
            cg.alpha   = Mathf.Lerp(from, to, Mathf.Clamp01(elapsed / dur));
            yield return null;
        }
        cg.alpha = to;
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private static Color TypeColor(NotifType type)
    {
        switch (type)
        {
            case NotifType.Warning: return ColWarning;
            case NotifType.Alert:   return ColAlert;
            case NotifType.Success: return ColSuccess;
            default:                return ColInfo;
        }
    }

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }
}
