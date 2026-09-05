using System.Collections;
using UnityEngine;

/// <summary>
/// Base class for every Atlas HUD environment.
///
/// Each concrete environment is a full-screen panel under the HUD canvas.
/// This base class owns:
///   • ShowImmediate / HideImmediate  – instant show/hide
///   • FadeIn / FadeOut               – alpha-only coroutines
///   • SlideIn / SlideOut             – slide + fade coroutines (for transitions)
///
/// Concrete subclasses override OnShown() / OnHidden() to start/stop their
/// own animation coroutines.
/// </summary>
[RequireComponent(typeof(RectTransform))]
public abstract class AtlasEnvironmentBase : MonoBehaviour
{
    protected RectTransform rectTransform;
    protected CanvasGroup   canvasGroup;

    protected virtual void Awake()
    {
        rectTransform = GetComponent<RectTransform>();

        canvasGroup = GetComponent<CanvasGroup>();
        if (canvasGroup == null)
            canvasGroup = gameObject.AddComponent<CanvasGroup>();
    }

    // ── Instant show / hide ───────────────────────────────────────────────────

    public virtual void ShowImmediate()
    {
        gameObject.SetActive(true);
        canvasGroup.alpha          = 1f;
        canvasGroup.interactable   = true;
        canvasGroup.blocksRaycasts = true;
        OnShown();
    }

    public virtual void HideImmediate()
    {
        canvasGroup.alpha          = 0f;
        canvasGroup.interactable   = false;
        canvasGroup.blocksRaycasts = false;
        gameObject.SetActive(false);
        OnHidden();
    }

    // ── Fade coroutines ───────────────────────────────────────────────────────

    public IEnumerator FadeIn(float duration)
    {
        gameObject.SetActive(true);
        canvasGroup.interactable   = false;
        canvasGroup.blocksRaycasts = false;
        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed           += Time.deltaTime;
            canvasGroup.alpha  = Mathf.Clamp01(elapsed / duration);
            yield return null;
        }
        canvasGroup.alpha          = 1f;
        canvasGroup.interactable   = true;
        canvasGroup.blocksRaycasts = true;
        OnShown();
    }

    public IEnumerator FadeOut(float duration)
    {
        canvasGroup.interactable   = false;
        canvasGroup.blocksRaycasts = false;
        float start   = canvasGroup.alpha;
        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed           += Time.deltaTime;
            canvasGroup.alpha  = Mathf.Lerp(start, 0f, elapsed / duration);
            yield return null;
        }
        canvasGroup.alpha = 0f;
        gameObject.SetActive(false);
        OnHidden();
    }

    // ── Slide + fade coroutines ───────────────────────────────────────────────

    /// <param name="slideOffset">Horizontal pixel offset to slide FROM (e.g. +300 = slides in from right).</param>
    public IEnumerator SlideIn(float duration, float slideOffset)
    {
        gameObject.SetActive(true);
        canvasGroup.interactable   = false;
        canvasGroup.blocksRaycasts = false;

        Vector2 resting  = rectTransform.anchoredPosition;
        Vector2 startPos = resting + new Vector2(slideOffset, 0f);
        float elapsed    = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t  = SmoothStep(Mathf.Clamp01(elapsed / duration));
            canvasGroup.alpha              = t;
            rectTransform.anchoredPosition = Vector2.Lerp(startPos, resting, t);
            yield return null;
        }

        canvasGroup.alpha              = 1f;
        rectTransform.anchoredPosition = resting;
        canvasGroup.interactable       = true;
        canvasGroup.blocksRaycasts     = true;
        OnShown();
    }

    /// <param name="slideOffset">Horizontal pixel offset to slide TO (e.g. -300 = slides out to left).</param>
    public IEnumerator SlideOut(float duration, float slideOffset)
    {
        canvasGroup.interactable   = false;
        canvasGroup.blocksRaycasts = false;

        Vector2 resting = rectTransform.anchoredPosition;
        Vector2 endPos  = resting + new Vector2(slideOffset, 0f);
        float elapsed   = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t  = SmoothStep(Mathf.Clamp01(elapsed / duration));
            canvasGroup.alpha              = 1f - t;
            rectTransform.anchoredPosition = Vector2.Lerp(resting, endPos, t);
            yield return null;
        }

        canvasGroup.alpha              = 0f;
        rectTransform.anchoredPosition = resting;   // reset for next entry
        gameObject.SetActive(false);
        OnHidden();
    }

    // ── Hooks for subclasses ──────────────────────────────────────────────────

    protected virtual void OnShown()  { }
    protected virtual void OnHidden() { }

    // ── Math helper ───────────────────────────────────────────────────────────

    private static float SmoothStep(float t) => t * t * (3f - 2f * t);
}
